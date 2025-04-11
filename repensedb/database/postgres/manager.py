import logging
from typing import Any, List, Optional, Dict
from repensedb.connections.postgres import PostgreSQLConnection

logger = logging.getLogger(__name__)


class PostgreSQLManager:
    def __init__(self, connection: PostgreSQLConnection, schema: str, table_name: str):
        """
        Initialize PostgreSQL manager

        Args:
            connection: PostgreSQLConnection instance
            schema: Schema name
            table_name: Table name
        """
        if not isinstance(connection, PostgreSQLConnection):
            raise TypeError("Connection must be a PostgreSQLConnection instance")

        if not connection.is_connected():
            connection.connect()

        self.conn = connection
        self.schema = schema
        self.table_name = table_name
        self.table = f"{self.schema}.{self.table_name}"

    def create_schema(self):
        """Create schema if it doesn't exist"""
        query = f"CREATE SCHEMA IF NOT EXISTS {self.schema}"
        self.conn.execute_query(query)

    def create_table(self, columns: str):
        """
        Create table if it doesn't exist

        Args:
            columns: Column definitions SQL string
        """
        self.create_schema()
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({columns})"
        self.conn.execute_query(query)

    def insert_record(
        self, data: Dict[str, Any], returning: str = None
    ) -> Optional[Any]:
        """
        Insert a single record

        Args:
            data: Dictionary of column names and values
            returning: Optional column to return

        Returns:
            Returned value if specified
        """
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"

            if returning:
                query += f" RETURNING {returning}"

            result = self.conn.execute_query(query, tuple(data.values()))
            return result[0][0] if returning else None
        except Exception as e:
            logger.error(f"Error inserting into {self.table}: {e}")
            raise

    def select_records(
        self,
        columns: str = "*",
        condition: str = None,
        params: tuple = None,
        order_by: str = None,
        limit: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Select records with optional conditions

        Args:
            columns: Columns to select
            condition: WHERE clause
            params: Query parameters
            order_by: ORDER BY clause
            limit: LIMIT clause

        Returns:
            List of records as dictionaries
        """
        try:
            query = f"SELECT {columns} FROM {self.table}"
            if condition:
                query += f" WHERE {condition}"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"

            results = self.conn.execute_query(query, params)
            return [
                dict(zip([col[0] for col in self.conn.cursor.description], row))
                for row in results
            ]
        except Exception as e:
            logger.error(f"Error selecting from {self.table}: {e}")
            raise

    def update_records(
        self, data: Dict[str, Any], condition: str, params: tuple = None
    ) -> int:
        """
        Update records matching condition

        Args:
            data: Dictionary of columns and values to update
            condition: WHERE clause
            params: Query parameters

        Returns:
            Number of records updated
        """
        try:
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            query = f"UPDATE {self.table} SET {set_clause} WHERE {condition}"

            all_params = tuple(data.values()) + (params or ())
            result = self.conn.execute_query(query, all_params)
            return result.rowcount
        except Exception as e:
            logger.error(f"Error updating {self.table}: {e}")
            raise

    def delete_records(self, condition: str, params: tuple = None) -> int:
        """
        Delete records matching condition

        Args:
            condition: WHERE clause
            params: Query parameters

        Returns:
            Number of records deleted
        """
        try:
            query = f"DELETE FROM {self.table} WHERE {condition}"
            result = self.conn.execute_query(query, params)
            return result.rowcount
        except Exception as e:
            logger.error(f"Error deleting from {self.table}: {e}")
            raise

    def list_tables(self) -> List[str]:
        """List all tables in the schema"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
        """
        results = self.conn.execute_query(query, (self.schema,))
        return [row[0] for row in results]

    def delete_table(self):
        """Drop the table"""
        query = f"DROP TABLE IF EXISTS {self.table}"
        self.conn.execute_query(query)

    def delete_schema(self):
        """Drop the schema and all its contents"""
        query = f"DROP SCHEMA IF EXISTS {self.schema} CASCADE"
        self.conn.execute_query(query)
