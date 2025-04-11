"""
Redis Client Configuration

Create a redis client from configuration.
"""

import logging
import json

from typing import Any, Optional, List

import numpy as np

from repensedb.connections.redis import RedisConnection

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, connection: RedisConnection, namespace: str):
        """
        Initialize Redis manager

        Args:
            connection: RedisConnection instance
            namespace: Namespace prefix for keys
        """
        if not isinstance(connection, RedisConnection):
            raise TypeError("Connection must be a RedisConnection instance")

        if not connection.is_connected():
            connection.connect()

        self.conn = connection
        self.namespace = namespace

    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.namespace}:{key}"

    def set_value(self, key: str, value: Any, expire: Optional[int] = None):
        """
        Set a key-value pair with optional expiration

        Args:
            key: Key name
            value: Value to store (will be JSON serialized if not string)
            expire: Optional expiration time in seconds
        """
        try:
            full_key = self._make_key(key)
            if not isinstance(value, str):
                value = json.dumps(value)
            self.conn.redis.set(full_key, value, ex=expire)
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            raise

    def get_value(self, key: str, deserialize: bool = True) -> Any:
        """
        Get value for a key

        Args:
            key: Key name
            deserialize: Whether to JSON deserialize the value

        Returns:
            Stored value or None if key doesn't exist
        """
        try:
            full_key = self._make_key(key)
            value = self.conn.redis.get(full_key)
            if value and deserialize:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            raise

    def delete_key(self, key: str):
        """Delete a key"""
        try:
            full_key = self._make_key(key)
            self.conn.redis.delete(full_key)
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            raise

    def list_keys(self, pattern: str = "*") -> List[str]:
        """
        List keys matching pattern

        Args:
            pattern: Redis key pattern (default: all keys in namespace)

        Returns:
            List of matching keys
        """
        try:
            full_pattern = self._make_key(pattern)
            keys = self.conn.redis.keys(full_pattern)
            return [k.decode().replace(f"{self.namespace}:", "") for k in keys]
        except Exception as e:
            logger.error(f"Error listing keys with pattern {pattern}: {e}")
            raise

    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter

        Args:
            key: Counter key
            amount: Amount to increment by

        Returns:
            New counter value
        """
        try:
            full_key = self._make_key(key)
            return self.conn.redis.incr(full_key, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {key}: {e}")
            raise

    def expire_key(self, key: str, seconds: int):
        """Set expiration time on key"""
        try:
            full_key = self._make_key(key)
            self.conn.redis.expire(full_key, seconds)
        except Exception as e:
            logger.error(f"Error setting expiration for key {key}: {e}")
            raise

    def clear_namespace(self):
        """Delete all keys in namespace"""
        try:
            keys = self.conn.redis.keys(self._make_key("*"))
            if keys:
                self.conn.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error clearing namespace {self.namespace}: {e}")
            raise

    @staticmethod
    def convert_types(number: Any):
        if isinstance(number, (np.int64, np.float64)):
            return number.item()
