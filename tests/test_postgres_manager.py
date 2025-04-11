# import pytest
# from repensedb.connections.postgres import PostgreSQLConnection
# from repensedb.database.postgres.manager import PostgreSQLManager


# @pytest.fixture(scope="module")
# def postgres_manager():
#     conn = PostgreSQLConnection(
#         host="localhost",
#         port=5432,
#         user="test_user",
#         password="test_password",
#         dbname="test_db",
#     )
#     manager = PostgreSQLManager(conn, "test_schema", "test_table")
#     yield manager
#     # Cleanup
#     conn.execute_query("DROP SCHEMA IF EXISTS test_schema CASCADE")
#     conn.disconnect()


# def test_create_schema(postgres_manager):
#     postgres_manager.create_schema()
#     # Query to check if schema exists
#     result = postgres_manager.conn.execute_query(
#         "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
#         ("test_schema",),
#     )
#     assert result and result[0][0] == "test_schema"


# def test_create_table(postgres_manager):
#     columns = """
#         id SERIAL PRIMARY KEY,
#         name VARCHAR(255) NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     """
#     postgres_manager.create_table(columns)
#     assert "test_table" in postgres_manager.list_tables()


# def test_insert_and_select(postgres_manager):
#     # Insert test data
#     test_data = {"name": "Test Record"}
#     postgres_manager.insert_record(test_data)

#     # Select and verify
#     results = postgres_manager.select(
#         columns="name", where="name = %s", params=("Test Record",)
#     )
#     assert results and results[0][0] == "Test Record"
