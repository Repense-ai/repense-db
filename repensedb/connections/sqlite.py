import sqlite3
from typing import Optional, Any, Dict
from pathlib import Path
from urllib.parse import parse_qs
from repensedb.connections.base import DatabaseConnection


class SQLiteConnection(DatabaseConnection):
    def __init__(self, url: Optional[str] = None, **kwargs):
        super().__init__(url, **kwargs)
        self.cursor = None

    def _load_secrets(self) -> Dict[str, Any]:
        """
        SQLite doesn't typically need secrets, but we implement the abstract method
        to return the connection parameters
        """
        return {"url": self.url} if self.url else {}
    
    def _load_env_vars(self) -> Dict[str, Any]:
        """
        SQLite doesn't typically need secrets, but we implement the abstract method
        to return the connection parameters
        """
        return {"url": self.url} if self.url else {}    

    def _parse_url_params(self):
        """Parse SQLite connection parameters from URL"""
        if self.parsed_url.path:
            # Remove leading slash for absolute paths
            path = self.parsed_url.path.lstrip("/")
            self.config["database"] = path
        else:
            self.config["database"] = (
                ":memory:"  # Use in-memory database if no path specified
            )

        # Parse additional parameters from query string
        if self.parsed_url.query:
            query_params = parse_qs(self.parsed_url.query)
            for key, value in query_params.items():
                if key == "mode":
                    self.config[key] = value[0]
                elif key == "isolation_level":
                    self.config[key] = value[0]
                elif key == "timeout":
                    self.config[key] = float(value[0])

    def connect(self):
        try:
            # Ensure directory exists for file-based databases
            if self.config["database"] != ":memory:":
                db_path = Path(self.config["database"])
                db_path.parent.mkdir(parents=True, exist_ok=True)

            self.connection = sqlite3.connect(**self.config)
            self.connection.row_factory = (
                sqlite3.Row
            )  # Enable dictionary-like row access
            self.cursor = self.connection.cursor()
            return self.connection
        except sqlite3.Error as err:
            raise ConnectionError(f"Failed to connect to SQLite: {err}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def is_connected(self) -> bool:
        return self.connection is not None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query and return results"""
        if not self.is_connected():
            self.connect()

        try:
            self.cursor.execute(query, params or ())

            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                return self.cursor.fetchall()
            self.connection.commit()
        except sqlite3.Error as err:
            self.connection.rollback()
            raise err
