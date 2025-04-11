import logging
import sqlite3
from typing import Any, List, Dict, Optional
from repensedb.connections.sqlite import SQLiteConnection

logger = logging.getLogger(__name__)


class SQLiteManager:
    def __init__(self, connection: SQLiteConnection, table_name: str):
        """
        Initialize SQLite manager

        Args:
            connection: SQLiteConnection instance
            table_name: Table name
        """
        if not isinstance(connection, SQLiteConnection):
            raise TypeError("Connection must be a SQLiteConnection instance")

        if not connection.is_connected():
            connection.connect()

        self.conn = connection
        self.table_name = table_name

    def create_table(self, columns: str):
        """
        Create table if it doesn't exist

        Args:
            columns: Column definitions SQL string
        """
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                {columns}
            )"""
            self.conn.execute_query(query)
        except sqlite3.Error as e:
            logger.error(f"Error creating table {self.table_name}: {e}")
            raise

    def insert_record(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a single record into the table

        Args:
            data: Dictionary of column names and values

        Returns:
            Row ID of inserted record
        """
        try:
            fields = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
            self.conn.execute_query(query, tuple(data.values()))
            return self.conn.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error inserting into {self.table_name}: {e}")
            raise

    def bulk_insert(self, records: List[Dict[str, Any]]) -> List[int]:
        """
        Insert multiple records into the table

        Args:
            records: List of dictionaries containing column names and values

        Returns:
            List of inserted row IDs
        """
        if not records:
            return []

        try:
            row_ids = []
            fields = ", ".join(records[0].keys())
            placeholders = ", ".join(["?"] * len(records[0]))
            query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

            values = [tuple(record.values()) for record in records]
            for (
                value
            ) in values:  # SQLite doesn't support multiple value sets in one query
                self.conn.execute_query(query, value)
                row_ids.append(self.conn.cursor.lastrowid)
            return row_ids
        except sqlite3.Error as e:
            logger.error(f"Error bulk inserting into {self.table_name}: {e}")
            raise

    def select(
        self,
        columns: str = "*",
        where: Optional[str] = None,
        params: Optional[tuple] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[sqlite3.Row]:
        """
        Select records from the table

        Args:
            columns: Columns to select
            where: WHERE clause
            params: Query parameters
            order_by: ORDER BY clause
            limit: LIMIT clause

        Returns:
            List of records as Row objects
        """
        try:
            query = f"SELECT {columns} FROM {self.table_name}"
            if where:
                query += f" WHERE {where}"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"
            return self.conn.execute_query(query, params)
        except sqlite3.Error as e:
            logger.error(f"Error selecting from {self.table_name}: {e}")
            raise

    def update(
        self, set_values: str, where: str, params: Optional[tuple] = None
    ) -> int:
        """
        Update records in the table

        Args:
            set_values: SET clause
            where: WHERE clause
            params: Query parameters

        Returns:
            Number of rows affected
        """
        try:
            query = f"UPDATE {self.table_name} SET {set_values} WHERE {where}"
            self.conn.execute_query(query, params)
            return self.conn.cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error updating {self.table_name}: {e}")
            raise

    def delete(self, where: str, params: Optional[tuple] = None) -> int:
        """
        Delete records from the table

        Args:
            where: WHERE clause
            params: Query parameters

        Returns:
            Number of rows affected
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE {where}"
            self.conn.execute_query(query, params)
            return self.conn.cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error deleting from {self.table_name}: {e}")
            raise

    def list_tables(self) -> List[str]:
        """
        List all tables in the database

        Returns:
            List of table names
        """
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            results = self.conn.execute_query(query)
            return [row[0] for row in results]
        except sqlite3.Error as e:
            logger.error(f"Error listing tables: {e}")
            raise

    def delete_table(self):
        """Drop the table"""
        try:
            query = f"DROP TABLE IF EXISTS {self.table_name}"
            self.conn.execute_query(query)
        except sqlite3.Error as e:
            logger.error(f"Error dropping table {self.table_name}: {e}")
            raise

    def vacuum(self):
        """Optimize the database file size"""
        try:
            self.conn.execute_query("VACUUM")
        except sqlite3.Error as e:
            logger.error(f"Error vacuuming database: {e}")
            raise

    def get_table_info(self) -> List[Dict[str, Any]]:
        """
        Get table schema information

        Returns:
            List of column information dictionaries
        """
        try:
            query = f"PRAGMA table_info({self.table_name})"
            return self.conn.execute_query(query)
        except sqlite3.Error as e:
            logger.error(f"Error getting table info for {self.table_name}: {e}")
            raise

    def create_index(self, index_name: str, columns: str, unique: bool = False):
        """
        Create an index on specified columns

        Args:
            index_name: Name of the index
            columns: Columns to index
            unique: Whether the index should be unique
        """
        try:
            unique_str = "UNIQUE" if unique else ""
            query = f"CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {self.table_name} ({columns})"
            self.conn.execute_query(query)
        except sqlite3.Error as e:
            logger.error(f"Error creating index {index_name} on {self.table_name}: {e}")
            raise

    def begin_transaction(self):
        """Begin a transaction"""
        try:
            self.conn.execute_query("BEGIN TRANSACTION")
        except sqlite3.Error as e:
            logger.error(f"Error beginning transaction: {e}")
            raise

    def commit_transaction(self):
        """Commit the current transaction"""
        try:
            self.conn.execute_query("COMMIT")
        except sqlite3.Error as e:
            logger.error(f"Error committing transaction: {e}")
            raise

    def rollback_transaction(self):
        """Rollback the current transaction"""
        try:
            self.conn.execute_query("ROLLBACK")
        except sqlite3.Error as e:
            logger.error(f"Error rolling back transaction: {e}")
            raise
