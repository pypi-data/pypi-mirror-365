"""
Evaluation API Routes

Provides comprehensive evaluation capabilities for AI models including
benchmark testing, performance analysis, and comparison metrics.
"""

from fastapi import APIRouter, Query, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import logging
from datetime import datetime, timedelta
import asyncpg
import asyncio
import json
import os
import uuid
from enum import Enum

try:
    from ..middleware.auth import require_read_access, require_write_access
except ImportError:
    # For development/testing when auth is not required
    def require_read_access():
        return {"user_id": "test_user"}
    
    def require_write_access():
        return {"user_id": "test_user"}

logger = logging.getLogger(__name__)

router = APIRouter()

# Database connection configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres?options=-c%20search_path%3Ddev")

# Enums
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EvaluationPriority(int, Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10

# Request Models
class EvaluationRequest(BaseModel):
    name: str = Field(..., description="评估任务名称", min_length=1, max_length=255)
    models: List[str] = Field(..., description="待评估模型列表", min_items=1)
    benchmark: str = Field(..., description="基准测试名称")
    dataset: Optional[str] = Field(None, description="数据集名称")
    config: Optional[Dict[str, Any]] = Field(None, description="评估配置参数")
    priority: EvaluationPriority = Field(EvaluationPriority.MEDIUM, description="任务优先级")
    timeout_minutes: Optional[int] = Field(60, description="超时时间(分钟)", ge=5, le=1440)

class BatchEvaluationRequest(BaseModel):
    name_prefix: str = Field(..., description="批量任务名称前缀")
    models: List[str] = Field(..., description="待评估模型列表", min_items=1)
    benchmarks: List[str] = Field(..., description="基准测试列表", min_items=1)
    config: Optional[Dict[str, Any]] = Field(None, description="通用评估配置")
    priority: EvaluationPriority = Field(EvaluationPriority.MEDIUM, description="任务优先级")

# Response Models
class EvaluationResponse(BaseModel):
    success: bool
    task_id: str
    status: TaskStatus
    message: Optional[str] = None
    estimated_time_minutes: Optional[int] = None

class EvaluationStatusResponse(BaseModel):
    task_id: str
    name: str
    status: TaskStatus
    models: List[str]
    benchmark: str
    progress: float = Field(0.0, description="完成进度 (0.0-1.0)")
    current_model: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None

class ModelResult(BaseModel):
    model_name: str
    metrics: Dict[str, float]
    raw_results: Optional[List[Any]] = None
    execution_time_seconds: float
    status: str

class EvaluationResult(BaseModel):
    task_id: str
    name: str
    status: TaskStatus
    models: List[ModelResult]
    benchmark: str
    dataset: Optional[str] = None
    summary: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_execution_time_seconds: Optional[float] = None

class BenchmarkInfo(BaseModel):
    name: str
    description: str
    category: str
    metrics: List[str]
    config_schema: Optional[Dict[str, Any]] = None

# Database connection helper
async def get_db_connection():
    """Get database connection"""
    try:
        return await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Task Management Functions
async def create_task_record(task_id: str, request: EvaluationRequest) -> None:
    """Create evaluation task record in database"""
    conn = await get_db_connection()
    try:
        await conn.execute("""
            INSERT INTO evaluations (id, name, status, models, benchmark, dataset, config, priority, timeout_minutes, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, task_id, request.name, TaskStatus.PENDING.value, request.models, 
            request.benchmark, request.dataset, json.dumps(request.config) if request.config else None,
            request.priority, request.timeout_minutes, datetime.utcnow())
    finally:
        await conn.close()

async def update_task_status(task_id: str, status: TaskStatus, 
                           progress: Optional[float] = None,
                           current_model: Optional[str] = None,
                           error_message: Optional[str] = None) -> None:
    """Update evaluation task status"""
    conn = await get_db_connection()
    try:
        updates = ["status = $2"]
        params = [task_id, status.value]
        param_count = 2
        
        if progress is not None:
            param_count += 1
            updates.append(f"progress = ${param_count}")
            params.append(progress)
            
        if current_model is not None:
            param_count += 1
            updates.append(f"current_model = ${param_count}")
            params.append(current_model)
            
        if error_message is not None:
            param_count += 1
            updates.append(f"error_message = ${param_count}")
            params.append(error_message)
            
        if status == TaskStatus.RUNNING:
            param_count += 1
            updates.append(f"started_at = ${param_count}")
            params.append(datetime.utcnow())
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            param_count += 1
            updates.append(f"completed_at = ${param_count}")
            params.append(datetime.utcnow())
        
        query = f"UPDATE evaluations SET {', '.join(updates)} WHERE id = $1"
        await conn.execute(query, *params)
    finally:
        await conn.close()

async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get evaluation task status"""
    conn = await get_db_connection()
    try:
        result = await conn.fetchrow("""
            SELECT * FROM evaluations WHERE id = $1
        """, task_id)
        
        if not result:
            return None
            
        return {
            'task_id': str(result['id']),
            'name': result['name'],
            'status': result['status'],
            'models': result['models'],
            'benchmark': result['benchmark'],
            'dataset': result['dataset'],
            'progress': result.get('progress', 0.0),
            'current_model': result.get('current_model'),
            'created_at': result['created_at'],
            'started_at': result.get('started_at'),
            'completed_at': result.get('completed_at'),
            'estimated_completion': result.get('estimated_completion'),
            'error_message': result.get('error_message')
        }
    finally:
        await conn.close()

def generate_task_id() -> str:
    """Generate unique task ID"""
    return str(uuid.uuid4())

# Background task functions
async def run_evaluation_task(task_id: str, request: EvaluationRequest):
    """Run evaluation task in background"""
    try:
        logger.info(f"Starting evaluation task {task_id}: {request.name}")
        await update_task_status(task_id, TaskStatus.RUNNING)
        
        # For now, create a mock evaluation for testing
        import random
        
        total_models = len(request.models)
        results = []
        
        for i, model in enumerate(request.models):
            logger.info(f"Evaluating model {model} ({i+1}/{total_models})")
            await update_task_status(task_id, TaskStatus.RUNNING, 
                                   progress=i/total_models, current_model=model)
            
            # Simulate evaluation time
            await asyncio.sleep(2)
            
            # Mock evaluation results
            model_result = {
                'model_name': model,
                'metrics': {
                    'accuracy': round(random.uniform(0.6, 0.95), 4),
                    'f1_score': round(random.uniform(0.55, 0.92), 4),
                    'overall_score': round(random.uniform(0.6, 0.9), 4)
                },
                'raw_results': [f"sample_prediction_{j}" for j in range(5)],  # Mock predictions
                'execution_time_seconds': round(random.uniform(1.5, 4.0), 2)
            }
            results.append(model_result)
            
            # Update progress
            await update_task_status(task_id, TaskStatus.RUNNING, 
                                   progress=(i+1)/total_models, current_model=model)
        
        # Save final results
        await save_evaluation_results(task_id, results)
        await update_task_status(task_id, TaskStatus.COMPLETED, progress=1.0)
        
        logger.info(f"Completed evaluation task {task_id}")
        
    except Exception as e:
        logger.error(f"Evaluation task {task_id} failed: {e}")
        await update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))

async def save_evaluation_results(task_id: str, results: List[Dict[str, Any]]):
    """Save evaluation results to database"""
    conn = await get_db_connection()
    try:
        for result in results:
            await conn.execute("""
                INSERT INTO evaluation_results (evaluation_id, model_name, metrics, raw_results, execution_time_seconds, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, task_id, result['model_name'], json.dumps(result['metrics']),
                json.dumps(result.get('raw_results')), result['execution_time_seconds'], datetime.utcnow())
    finally:
        await conn.close()

# API Endpoints

@router.post("/", response_model=EvaluationResponse)
async def create_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks
):
    """Create new evaluation task"""
    try:
        task_id = generate_task_id()
        
        # Create task record
        await create_task_record(task_id, request)
        
        # Start background evaluation
        background_tasks.add_task(run_evaluation_task, task_id, request)
        
        return EvaluationResponse(
            success=True,
            task_id=task_id,
            status=TaskStatus.PENDING,
            estimated_time_minutes=request.timeout_minutes
        )
        
    except Exception as e:
        logger.error(f"Failed to create evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create evaluation: {str(e)}")

@router.post("/batch", response_model=List[EvaluationResponse])
async def create_batch_evaluation(
    request: BatchEvaluationRequest,
    background_tasks: BackgroundTasks,
    user: Dict = Depends(require_write_access)
):
    """Create batch evaluation tasks"""
    try:
        responses = []
        
        for i, benchmark in enumerate(request.benchmarks):
            task_id = generate_task_id()
            eval_request = EvaluationRequest(
                name=f"{request.name_prefix}_{benchmark}_{i+1}",
                models=request.models,
                benchmark=benchmark,
                config=request.config,
                priority=request.priority
            )
            
            await create_task_record(task_id, eval_request)
            background_tasks.add_task(run_evaluation_task, task_id, eval_request)
            
            responses.append(EvaluationResponse(
                success=True,
                task_id=task_id,
                status=TaskStatus.PENDING
            ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Failed to create batch evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create batch evaluation: {str(e)}")

@router.get("/", response_model=List[EvaluationStatusResponse])
async def list_evaluations(
    status: Optional[TaskStatus] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0)
):
    """List evaluation tasks"""
    try:
        conn = await get_db_connection()
        try:
            query = "SELECT * FROM evaluations"
            params = []
            
            if status:
                query += " WHERE status = $1"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
            params.extend([limit, offset])
            
            results = await conn.fetch(query, *params)
            
            return [
                EvaluationStatusResponse(
                    task_id=str(row['id']),
                    name=row['name'],
                    status=TaskStatus(row['status']),
                    models=row['models'],
                    benchmark=row['benchmark'],
                    progress=row.get('progress', 0.0),
                    current_model=row.get('current_model'),
                    created_at=row['created_at'],
                    started_at=row.get('started_at'),
                    completed_at=row.get('completed_at'),
                    estimated_completion=row.get('estimated_completion'),
                    error_message=row.get('error_message')
                )
                for row in results
            ]
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Failed to list evaluations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list evaluations: {str(e)}")

@router.get("/{task_id}/status", response_model=EvaluationStatusResponse)
async def get_evaluation_status(
    task_id: str
):
    """Get evaluation task status"""
    try:
        status = await get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return EvaluationStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evaluation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation status: {str(e)}")

@router.get("/{task_id}/results", response_model=EvaluationResult)
async def get_evaluation_results(
    task_id: str
):
    """Get evaluation results"""
    try:
        # Get task info
        status = await get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get results
        conn = await get_db_connection()
        try:
            results = await conn.fetch("""
                SELECT * FROM evaluation_results WHERE evaluation_id = $1 ORDER BY created_at
            """, task_id)
            
            model_results = [
                ModelResult(
                    model_name=row['model_name'],
                    metrics=json.loads(row['metrics']),
                    raw_results=json.loads(row['raw_results']) if row['raw_results'] else None,
                    execution_time_seconds=float(row['execution_time_seconds']),
                    status="completed"
                )
                for row in results
            ]
            
            # Calculate summary
            summary = {}
            if model_results:
                all_metrics = [r.metrics for r in model_results]
                if all_metrics:
                    metric_names = set()
                    for metrics in all_metrics:
                        metric_names.update(metrics.keys())
                    
                    for metric in metric_names:
                        values = [m.get(metric, 0) for m in all_metrics if metric in m]
                        if values:
                            summary[f"avg_{metric}"] = sum(values) / len(values)
                            summary[f"max_{metric}"] = max(values)
                            summary[f"min_{metric}"] = min(values)
            
            return EvaluationResult(
                task_id=task_id,
                name=status['name'],
                status=TaskStatus(status['status']),
                models=model_results,
                benchmark=status['benchmark'],
                dataset=status.get('dataset'),
                summary=summary,
                created_at=status['created_at'],
                started_at=status.get('started_at'),
                completed_at=status.get('completed_at')
            )
        finally:
            await conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evaluation results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation results: {str(e)}")

@router.post("/{task_id}/cancel")
async def cancel_evaluation(
    task_id: str
):
    """Cancel evaluation task"""
    try:
        status = await get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        current_status = TaskStatus(status['status'])
        if current_status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel task with status: {current_status}")
        
        await update_task_status(task_id, TaskStatus.CANCELLED)
        
        return {"success": True, "message": "Task cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel evaluation: {str(e)}")

@router.get("/{task_id}/stream")
async def stream_evaluation_progress(
    task_id: str
):
    """Stream evaluation progress in real-time"""
    
    async def generate():
        """Generate SSE stream for evaluation progress"""
        last_status = None
        
        while True:
            try:
                current_status = await get_task_status(task_id)
                if not current_status:
                    yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                    break
                
                # Only send update if status changed
                if current_status != last_status:
                    yield f"data: {json.dumps(current_status)}\n\n"
                    last_status = current_status
                
                # Stop streaming if task is complete
                status_enum = TaskStatus(current_status['status'])
                if status_enum in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    break
                
                await asyncio.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in stream: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
    
    return StreamingResponse(generate(), media_type="text/plain")

@router.get("/benchmarks", response_model=List[BenchmarkInfo])
async def list_benchmarks(
    category: Optional[str] = None
):
    """List available benchmarks"""
    try:
        # Get benchmarks from database
        conn = await get_db_connection()
        try:
            results = await conn.fetch("SELECT * FROM dev.benchmarks ORDER BY category, name")
            benchmarks = [
                BenchmarkInfo(
                    name=row['name'],
                    description=row['description'],
                    category=row['category'],
                    metrics=row['metrics'] if isinstance(row['metrics'], list) else json.loads(row['metrics']) if row['metrics'] else [],
                    config_schema=row['config_schema'] if isinstance(row['config_schema'], dict) else json.loads(row['config_schema']) if row['config_schema'] else None
                )
                for row in results
            ]
        finally:
            await conn.close()
        
        if category:
            benchmarks = [b for b in benchmarks if b.category == category]
        
        return benchmarks
        
    except Exception as e:
        logger.error(f"Failed to list benchmarks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list benchmarks: {str(e)}")

@router.get("/models")
async def list_evaluatable_models():
    """List models available for evaluation"""
    try:
        # This would integrate with your model registry
        # For now, return common models
        return {
            "success": True,
            "models": [
                {"name": "gpt-4", "provider": "openai", "type": "llm"},
                {"name": "gpt-3.5-turbo", "provider": "openai", "type": "llm"},
                {"name": "claude-3-opus", "provider": "anthropic", "type": "llm"},
                {"name": "claude-3-sonnet", "provider": "anthropic", "type": "llm"},
                {"name": "llama-2-70b", "provider": "meta", "type": "llm"},
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")