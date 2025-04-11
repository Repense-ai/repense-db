# import pytest
# from unittest.mock import Mock
# import os

# from repensedb.connections.mysql import MySQLConnection
# from repensedb.database.mysql.manager import MySQLManager


# @pytest.fixture(scope="module")
# def mysql_connection():
#     conn = MySQLConnection(
#         host=os.getenv("MYSQL_HOST", "localhost"),
#         user=os.getenv("MYSQL_USER", "root"),
#         password=os.getenv("MYSQL_PASSWORD", ""),
#         port=int(os.getenv("MYSQL_PORT", 3306))
#     )
#     conn.connect()
#     yield conn
#     conn.disconnect()


# @pytest.fixture(scope="module")
# def mysql_manager(mysql_connection):
#     manager = MySQLManager(
#         connection=mysql_connection,
#         namespace="test_db",
#         table="test_table"
#     )
    
#     # Ensure clean state
#     try:
#         manager.delete_namespace()
#     except:
#         pass
    
#     yield manager
    
#     # Cleanup after all tests
#     try:
#         manager.delete_namespace()
#     except:
#         pass


# @pytest.fixture
# def mock_manager():
#     mock_conn = Mock()
#     manager = MySQLManager(mock_conn, "test_db", "test_table")
#     return manager


# def test_mysql_manager_initialization():
#     conn = MySQLConnection(
#         host="localhost",
#         user="root",
#         password="",
#         port=3306
#     )
#     manager = MySQLManager(conn, "test_db", "test_table")
#     assert isinstance(manager, MySQLManager)
#     assert manager.namespace == "test_db"
#     assert manager.table == "test_table"


# def test_mysql_manager_create_namespace(mysql_manager):
#     mysql_manager.create_namespace()
#     namespaces = mysql_manager.list_namespaces()
#     assert "test_db" in namespaces


# def test_mysql_manager_create_table(mysql_manager):
#     mysql_manager.create_namespace()
#     schema = """
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(255) NOT NULL,
#         email VARCHAR(255) UNIQUE,
#         age INT,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     """
#     mysql_manager.create_table(schema=schema)
#     tables = mysql_manager.list_tables()
#     assert "test_table" in tables


# def test_mysql_manager_insert_and_select_single_record(mysql_manager):
#     test_data = {
#         "name": "John Doe",
#         "email": "john@example.com",
#         "age": 30
#     }
    
#     # Insert single record
#     inserted_id = mysql_manager.insert_record(test_data)
#     assert isinstance(inserted_id, int)
    
#     # Select and verify
#     records = mysql_manager.select_records(where="id = %s", params=(inserted_id,))
#     assert len(records) == 1
#     assert records[0]["name"] == "John Doe"
#     assert records[0]["email"] == "john@example.com"
#     assert records[0]["age"] == 30


# def test_mysql_manager_insert_and_select_multiple_records(mysql_manager):
#     test_data = [
#         {"name": "Alice", "email": "alice@example.com", "age": 25},
#         {"name": "Bob", "email": "bob@example.com", "age": 35},
#         {"name": "Charlie", "email": "charlie@example.com", "age": 40}
#     ]
    
#     # Insert multiple records
#     inserted_ids = mysql_manager.insert_records(test_data)
#     assert len(inserted_ids) == 3
    
#     # Select and verify
#     records = mysql_manager.select_records(where="age > %s", params=(30,))
#     assert len(records) == 2  # Bob and Charlie


# def test_mysql_manager_update_records(mysql_manager):
#     # Insert test record
#     test_data = {"name": "Test User", "email": "test@example.com", "age": 25}
#     inserted_id = mysql_manager.insert_record(test_data)
    
#     # Update record
#     update_data = {"age": 26}
#     updated = mysql_manager.update_records(
#         data=update_data,
#         where="id = %s",
#         params=(inserted_id,)
#     )
#     assert updated > 0
    
#     # Verify update
#     record = mysql_manager.select_records(where="id = %s", params=(inserted_id,))[0]
#     assert record["age"] == 26


# def test_mysql_manager_delete_records(mysql_manager):
#     # Insert test record
#     test_data = {"name": "Delete Test", "email": "delete@example.com", "age": 30}
#     inserted_id = mysql_manager.insert_record(test_data)
    
#     # Delete record
#     deleted = mysql_manager.delete_records(where="id = %s", params=(inserted_id,))
#     assert deleted > 0
    
#     # Verify deletion
#     records = mysql_manager.select_records(where="id = %s", params=(inserted_id,))
#     assert len(records) == 0


# def test_mysql_manager_count_records(mysql_manager):
#     # Clear existing records
#     mysql_manager.delete_records()
    
#     # Insert test records
#     test_data = [
#         {"name": "User1", "email": "user1@example.com", "age": 25},
#         {"name": "User2", "email": "user2@example.com", "age": 30},
#         {"name": "User3", "email": "user3@example.com", "age": 35}
#     ]
#     mysql_manager.insert_records(test_data)
    
#     # Count all records
#     total_count = mysql_manager.count_records()
#     assert total_count == 3
    
#     # Count with condition
#     filtered_count = mysql_manager.count_records(where="age > %s", params=(30,))
#     assert filtered_count == 1


# def test_mysql_manager_truncate_table(mysql_manager):
#     # Insert some records
#     test_data = [
#         {"name": "User1", "email": "user1@example.com", "age": 25},
#         {"name": "User2", "email": "user2@example.com", "age": 30}
#     ]
#     mysql_manager.insert_records(test_data)
    
#     # Truncate table
#     mysql_manager.truncate_table()
    
#     # Verify table is empty
#     count = mysql_manager.count_records()
#     assert count == 0


# @pytest.mark.parametrize("invalid_data", [
#     {},  # Empty dict
#     {"invalid_column": "value"},  # Non-existent column
#     None,  # None value
# ])
# def test_mysql_manager_insert_invalid_data(mysql_manager, invalid_data):
#     with pytest.raises(Exception):
#         mysql_manager.insert_record(invalid_data)


# def test_mysql_manager_transaction_commit(mysql_manager):
#     mysql_manager.begin_transaction()
#     try:
#         mysql_manager.insert_record({"name": "Transaction Test", "email": "trans@example.com", "age": 30})
#         mysql_manager.commit_transaction()
        
#         # Verify record was committed
#         records = mysql_manager.select_records(where="email = %s", params=("trans@example.com",))
#         assert len(records) == 1
#     except:
#         mysql_manager.rollback_transaction()
#         raise


# def test_mysql_manager_transaction_rollback(mysql_manager):
#     mysql_manager.begin_transaction()
#     try:
#         mysql_manager.insert_record({"name": "Rollback Test", "email": "rollback@example.com", "age": 30})
#         raise Exception("Forced rollback")
#     except:
#         mysql_manager.rollback_transaction()
    
#     # Verify record was not committed
#     records = mysql_manager.select_records(where="email = %s", params=("rollback@example.com",))
#     assert len(records) == 0


# def test_mysql_manager_cleanup(mysql_manager):
#     # Test table deletion
#     mysql_manager.delete_table()
#     tables = mysql_manager.list_tables()
#     assert "test_table" not in tables
    
#     # Test namespace deletion
#     mysql_manager.delete_namespace()
#     namespaces = mysql_manager.list_namespaces()
#     assert "test_db" not in namespaces
