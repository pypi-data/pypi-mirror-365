"""
Centralized Supabase Client for ISA Model Core

Provides a singleton Supabase client instance that:
- Gets configuration from ConfigManager
- Handles environment-based schema selection
- Provides a single point of database access for all services
"""

import logging
from typing import Optional
from supabase import create_client, Client

from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Singleton Supabase client with environment-aware configuration"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_client()
            SupabaseClient._initialized = True
    
    def _initialize_client(self):
        """Initialize the Supabase client with configuration from ConfigManager"""
        try:
            # Get configuration from ConfigManager
            config_manager = ConfigManager()
            global_config = config_manager.get_global_config()
            
            # Get database configuration
            self.url = global_config.database.supabase_url
            self.key = global_config.database.supabase_key
            self.schema = global_config.database.supabase_schema or "public"
            self.environment = global_config.environment.value
            
            if not self.url or not self.key:
                raise ValueError("Supabase URL and key must be configured")
            
            # Create the client
            self._client = create_client(self.url, self.key)
            
            logger.info(f"Supabase client initialized for {self.environment} environment (schema: {self.schema})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        if not self._client:
            raise RuntimeError("Supabase client not initialized")
        return self._client
    
    def table(self, table_name: str):
        """Get a table with the correct schema"""
        if not self._client:
            raise RuntimeError("Supabase client not initialized")
        
        # Use the configured schema for the environment
        if self.schema and self.schema != "public":
            return self._client.schema(self.schema).table(table_name)
        else:
            return self._client.table(table_name)
    
    def rpc(self, function_name: str, params: Optional[dict] = None):
        """Call an RPC function with the correct schema"""
        if not self._client:
            raise RuntimeError("Supabase client not initialized")
        
        # RPC functions typically use the public schema
        # But we can extend this if needed for schema-specific functions
        return self._client.rpc(function_name, params)
    
    def get_schema(self) -> str:
        """Get the current schema being used"""
        return self.schema
    
    def get_environment(self) -> str:
        """Get the current environment"""
        return self.environment
    
    def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            # Try a simple query to test connection
            result = self.table('models').select('*').limit(1).execute()
            logger.debug("Database connection test successful")
            return True
        except Exception as e:
            logger.warning(f"Database connection test failed: {e}")
            return False

# Global singleton instance
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get the global Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

def get_supabase_table(table_name: str):
    """Convenience function to get a table with correct schema"""
    client = get_supabase_client()
    return client.table(table_name)

def get_supabase_rpc(function_name: str, params: Optional[dict] = None):
    """Convenience function to call RPC functions"""
    client = get_supabase_client()
    return client.rpc(function_name, params)