"""
Database Configuration and Management
MongoDB connection and utilities for WorkWave Coast
"""
import os
import logging
from typing import Optional, Dict, Any
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.database import Database
from config.constants import DATABASE_INDEXES, COLLECTIONS

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self, uri: str):
        """Initialize database configuration
        
        Args:
            uri: MongoDB connection URI
        """
        self.uri = uri
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._collections: Dict[str, Collection] = {}
        
    @property
    def client(self) -> MongoClient:
        """Get MongoDB client, creating connection if needed"""
        if self._client is None:
            try:
                self._client = MongoClient(
                    self.uri,
                    serverSelectionTimeoutMS=30000,  # 30 seconds
                    socketTimeoutMS=20000,           # 20 seconds
                    connectTimeoutMS=20000,          # 20 seconds
                    maxPoolSize=10,
                    retryWrites=True
                )
                # Test connection
                self._client.admin.command('ping')
                logger.info("MongoDB connection established successfully")
            except errors.ServerSelectionTimeoutError as e:
                logger.error(f"MongoDB connection timeout: {e}")
                raise
            except Exception as e:
                logger.error(f"MongoDB connection error: {e}")
                raise
                
        return self._client
    
    @property
    def db(self) -> Database:
        """Get database instance"""
        if self._db is None:
            self._db = self.client['workwave']
        return self._db
    
    @property
    def candidates(self) -> Collection:
        """Get candidates collection"""
        if 'candidates' not in self._collections:
            self._collections['candidates'] = self.db[COLLECTIONS['candidates']]
        return self._collections['candidates']
    
    @property
    def admin_logs(self) -> Collection:
        """Get admin logs collection"""
        if 'admin_logs' not in self._collections:
            self._collections['admin_logs'] = self.db[COLLECTIONS['admin_logs']]
        return self._collections['admin_logs']
    
    @property 
    def email_logs(self) -> Collection:
        """Get email logs collection"""
        if 'email_logs' not in self._collections:
            self._collections['email_logs'] = self.db[COLLECTIONS['email_logs']]
        return self._collections['email_logs']
    
    def create_indexes(self) -> bool:
        """Create database indexes as defined in constants
        
        Returns:
            bool: True if all indexes created successfully
        """
        try:
            logger.info("Creating database indexes...")
            
            for index_config in DATABASE_INDEXES:
                collection_name = index_config['collection']
                index_spec = index_config['index']
                options = index_config.get('options', {})
                
                collection = self.db[collection_name]
                
                try:
                    # Create index
                    result = collection.create_index(index_spec, **options)
                    logger.info(f"Created index '{result}' on {collection_name}")
                    
                except errors.OperationFailure as e:
                    if "already exists" in str(e):
                        logger.info(f"Index already exists on {collection_name}: {index_spec}")
                    else:
                        logger.warning(f"Failed to create index on {collection_name}: {e}")
                        
            logger.info("Database index creation completed")
            return True
            
        except Exception as e:
            logger.error(f"MongoDB connection error during index creation: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test database connection
        
        Returns:
            bool: True if connection is successful
        """
        try:
            self.client.admin.command('ping')
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information
        
        Returns:
            dict: Connection information
        """
        try:
            server_info = self.client.server_info()
            db_stats = self.db.command("dbstats")
            
            return {
                'connected': True,
                'server_version': server_info.get('version'),
                'database_name': self.db.name,
                'collections': self.db.list_collection_names(),
                'database_size': db_stats.get('dataSize', 0),
                'collections_count': len(db_stats.get('collections', 0))
            }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def close_connection(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._collections.clear()
            logger.info("Database connection closed")


class DatabaseManager:
    """Singleton database manager"""
    
    _instance: Optional['DatabaseManager'] = None
    _db_config: Optional[DatabaseConfig] = None
    
    def __new__(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, uri: str) -> DatabaseConfig:
        """Initialize database configuration
        
        Args:
            uri: MongoDB connection URI
            
        Returns:
            DatabaseConfig: Initialized database configuration
        """
        if self._db_config is None:
            self._db_config = DatabaseConfig(uri)
            # Test connection and create indexes
            if self._db_config.test_connection():
                self._db_config.create_indexes()
            
        return self._db_config
    
    @property
    def db_config(self) -> Optional[DatabaseConfig]:
        """Get current database configuration"""
        return self._db_config
    
    def get_collection(self, name: str) -> Optional[Collection]:
        """Get collection by name
        
        Args:
            name: Collection name
            
        Returns:
            Collection: MongoDB collection or None
        """
        if self._db_config is None:
            logger.error("Database not initialized")
            return None
            
        if name == 'candidates':
            return self._db_config.candidates
        elif name == 'admin_logs':
            return self._db_config.admin_logs
        elif name == 'email_logs':
            return self._db_config.email_logs
        else:
            return self._db_config.db[name]


# Global database manager instance
db_manager = DatabaseManager()


def get_database_config(uri: str) -> DatabaseConfig:
    """Get or create database configuration
    
    Args:
        uri: MongoDB connection URI
        
    Returns:
        DatabaseConfig: Database configuration instance
    """
    return db_manager.initialize(uri)


def get_collection(name: str) -> Optional[Collection]:
    """Get collection by name using global manager
    
    Args:
        name: Collection name
        
    Returns:
        Collection: MongoDB collection or None
    """
    return db_manager.get_collection(name)