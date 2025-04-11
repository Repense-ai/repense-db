import mysql.connector
import os
from typing import Optional, Dict, Any
from urllib.parse import parse_qs
from repensedb.connections.base import DatabaseConnection


class MySQLConnection(DatabaseConnection):
    def __init__(self, url: Optional[str] = None, **kwargs):
        super().__init__(url, **kwargs)

    def _load_secrets(self) -> Dict[str, Any]:
        """Load MySQL connection parameters from AWS Secrets Manager"""
        secrets = self.secrets_manager.get_secret()
        self.config.update({
            "host": secrets.get("host", "localhost"),
            "port": int(secrets.get("port", 3306)),
            "user": secrets.get("username"),
            "password": secrets.get("password"),
            "database": secrets.get("dbname")
        })
        return self.config

    def _load_env_vars(self):
        """Load MySQL connection parameters from environment variables"""
        self.config.update({
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", 3306)),
            "user": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
            "database": os.getenv("MYSQL_DATABASE")
        })
        # Remove None values
        self.config = {k: v for k, v in self.config.items() if v is not None}

    def _parse_url_params(self):
        """Parse MySQL connection parameters from URL"""
        self.config.update({
            "host": self.parsed_url.hostname or "localhost",
            "port": self.parsed_url.port or 3306,
            "user": self.parsed_url.username,
            "password": self.parsed_url.password,
            "database": self.parsed_url.path.lstrip("/"),
        })

        if self.parsed_url.query:
            query_params = parse_qs(self.parsed_url.query)
            for key, value in query_params.items():
                self.config[key] = value[0]

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            return self.connection
        except mysql.connector.Error as err:
            raise ConnectionError(f"Failed to connect to MySQL: {err}")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def is_connected(self) -> bool:
        return self.connection and self.connection.is_connected()
