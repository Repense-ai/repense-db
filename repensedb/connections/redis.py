import redis
from typing import Optional
from repensedb.connections.base import DatabaseConnection


class RedisConnection(DatabaseConnection):
    def __init__(self, url: Optional[str] = None, **kwargs):
        super().__init__(url, **kwargs)

    def _parse_url_params(self):
        """Parse Redis connection parameters from URL"""
        self.config.update(
            {
                "host": self.parsed_url.hostname or "localhost",
                "port": self.parsed_url.port or 6379,
                "db": int(self.parsed_url.path.lstrip("/") or 0),
            }
        )

        if self.parsed_url.password:
            self.config["password"] = self.parsed_url.password

    def connect(self):
        try:
            self.connection = redis.Redis(**self.config)
            # Test connection
            self.connection.ping()
            return self.connection
        except redis.ConnectionError as err:
            raise ConnectionError(f"Failed to connect to Redis: {err}")

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def is_connected(self) -> bool:
        try:
            return self.connection and self.connection.ping()
        except (redis.ConnectionError, AttributeError):
            return False
