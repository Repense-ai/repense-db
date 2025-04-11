import psycopg2
import os
from typing import Optional, Dict, Any
from urllib.parse import parse_qs
from repensedb.connections.base import DatabaseConnection


class PostgreSQLConnection(DatabaseConnection):
    def __init__(self, url: Optional[str] = None, **kwargs):
        super().__init__(url, **kwargs)

    def _load_secrets(self) -> Dict[str, Any]:
        """Load PostgreSQL connection parameters from AWS Secrets Manager"""
        secrets = self.secrets_manager.get_secret()
        self.config.update({
            "host": secrets.get("host", "localhost"),
            "port": int(secrets.get("port", 5432)),
            "user": secrets.get("username"),
            "password": secrets.get("password"),
            "dbname": secrets.get("dbname")
        })
        return self.config

    def _load_env_vars(self):
        """Load PostgreSQL connection parameters from environment variables"""
        self.config.update({
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "dbname": os.getenv("POSTGRES_DB")
        })
        # Remove None values
        self.config = {k: v for k, v in self.config.items() if v is not None}

    def _parse_url_params(self):
        """Parse PostgreSQL connection parameters from URL"""
        self.config.update({
            "host": self.parsed_url.hostname or "localhost",
            "port": self.parsed_url.port or 5432,
            "user": self.parsed_url.username,
            "password": self.parsed_url.password,
            "dbname": self.parsed_url.path.lstrip("/")
        })

        if self.parsed_url.query:
            query_params = parse_qs(self.parsed_url.query)
            for key, value in query_params.items():
                self.config[key] = value[0]

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.config)
            return self.connection
        except psycopg2.Error as err:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {err}")

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def is_connected(self) -> bool:
        return self.connection and not self.connection.closed

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query and return results"""
        if not self.is_connected():
            self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith(("SELECT", "SHOW", "EXPLAIN")):
                return cursor.fetchall()
            self.connection.commit()
        except psycopg2.Error as err:
            self.connection.rollback()
            raise err
        finally:
            cursor.close()
