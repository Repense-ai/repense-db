import logging
from typing import Any, List, Optional
from repensedb.connections.mysql import MySQLConnection
from repensedb.utils.logs import LOGGING_CONFIG

logging.basicConfig(**LOGGING_CONFIG)


class MySQLManager:
    def __init__(self, connection: MySQLConnection, namespace: str, table_name: str):
        """
        Initialize MySQL manager

        Args:
            connection: MySQLConnection instance
            namespace: Database name
            table_name: Table name
        """
        if not isinstance(connection, MySQLConnection):
            raise TypeError("Connection must be a MySQLConnection instance")

        if not connection.is_connected():
            connection.connect()

        self.conn = connection
        self.namespace = namespace
        self.table_name = table_name
        self.table = f"{self.namespace}.{self.table_name}"

    def create_namespace(self):
        """Create database if it doesn't exist"""
        query = f"CREATE DATABASE IF NOT EXISTS {self.namespace}"
        self.conn.execute_query(query)

    def create_table(self, schema: str):
        """Create table if it doesn't exist"""
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({schema})"
        self.conn.execute_query(query)

    def insert_record(self, log_dict: dict[str, Any]):
        """Insert a single record"""
        fields = ", ".join(log_dict.keys())
        placeholders = ", ".join(["%s"] * len(log_dict))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})"
        values = tuple(log_dict.values())
        self.conn.execute_query(query, values)

    def select_records(self, condition: Optional[str] = None) -> List[dict]:
        """Select records with optional condition"""
        query = f"SELECT * FROM {self.table}"
        if condition:
            query += f" WHERE {condition}"
        results = self.conn.execute_query(query)
        return [
            dict(zip([col[0] for col in self.conn.cursor.description], row))
            for row in results
        ]

    def update_records(self, condition: str, log_dict: dict[str, Any]):
        """Update records matching condition"""
        query = f"UPDATE {self.table} SET {', '.join([f'{key} = %s' for key in log_dict.keys()])} WHERE {condition}"
        values = tuple(log_dict.values())
        self.conn.execute_query(query, values)

    def delete_records(self, condition: str):
        """Delete records matching condition"""
        query = f"DELETE FROM {self.table} WHERE {condition}"
        self.conn.execute_query(query)

    def list_tables(self) -> List[str]:
        """List all tables in the namespace"""
        query = f"SHOW TABLES FROM {self.namespace}"
        tables = self.conn.execute_query(query)
        return [table[0] for table in tables]

    def delete_table(self):
        """Drop the table"""
        query = f"DROP TABLE IF EXISTS {self.table}"
        self.conn.execute_query(query)

    def delete_namespace(self):
        """Drop the database"""
        query = f"DROP DATABASE IF EXISTS {self.namespace}"
        self.conn.execute_query(query)
