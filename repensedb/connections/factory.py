from typing import Type, Optional
from repensedb.connections.base import DatabaseConnection
from repensedb.connections.mysql import MySQLConnection
from repensedb.connections.redis import RedisConnection
from repensedb.connections.postgres import PostgreSQLConnection
from repensedb.connections.sqlite import SQLiteConnection


class ConnectionFactory:
    _registry = {
        "mysql": MySQLConnection,
        "redis": RedisConnection,
        "postgresql": PostgreSQLConnection,
        "postgres": PostgreSQLConnection,
        "sqlite": SQLiteConnection,
    }

    @classmethod
    def register(cls, scheme: str, connection_class: Type[DatabaseConnection]):
        """Register a new connection type"""
        cls._registry[scheme] = connection_class

    @classmethod
    def create(
        cls, url: Optional[str] = None, connection_type: Optional[str] = None, **kwargs
    ) -> DatabaseConnection:
        """Create a database connection based on URL scheme or explicit connection type"""
        if url:
            scheme = url.split("://")[0]
        elif connection_type:
            scheme = connection_type
        else:
            raise ValueError("Either URL or connection_type must be provided")

        if scheme not in cls._registry:
            raise ValueError(f"Unsupported database type: {scheme}")

        connection_class = cls._registry[scheme]
        return connection_class(url=url, **kwargs)
