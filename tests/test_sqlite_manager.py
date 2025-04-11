import pytest
import os
from repensedb.connections.sqlite import SQLiteConnection
from repensedb.database.sqlite.manager import SQLiteManager


@pytest.fixture(scope="module")
def sqlite_manager():
    # Use in-memory database for testing
    conn = SQLiteConnection(url="sqlite://:memory:")
    manager = SQLiteManager(conn, "test_table")
    yield manager
    manager.delete_table()
    conn.disconnect()


@pytest.fixture(scope="module")
def file_sqlite_manager():
    # Use file-based database for testing
    test_db = "test_database.db"
    conn = SQLiteConnection(url=f"sqlite:///{test_db}")
    manager = SQLiteManager(conn, "test_table")
    yield manager
    manager.delete_table()
    conn.disconnect()
    # Clean up test database file
    if os.path.exists(test_db):
        os.remove(test_db)


def test_create_table(sqlite_manager):
    columns = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    """
    sqlite_manager.create_table(columns)
    assert "test_table" in sqlite_manager.list_tables()


def test_insert_and_select(sqlite_manager):
    # Insert test data
    test_data = {"name": "Test Record"}
    sqlite_manager.insert_record(test_data)

    # Select and verify
    results = sqlite_manager.select(
        columns="name", where="name = ?", params=("Test Record",)
    )
    assert results and results[0]["name"] == "Test Record"


def test_bulk_insert(sqlite_manager):
    test_data = [{"name": f"Record {i}"} for i in range(3)]
    sqlite_manager.bulk_insert(test_data)

    results = sqlite_manager.select()
    assert len(results) == 4


def test_update(sqlite_manager):
    sqlite_manager.update(
        set_values="name = ?", where="name = ?", params=("Updated Record", "Record 0")
    )

    results = sqlite_manager.select(where="name = ?", params=("Updated Record",))
    assert results and results[0]["name"] == "Updated Record"


def test_delete(sqlite_manager):
    sqlite_manager.delete(where="name = ?", params=("Updated Record",))
    results = sqlite_manager.select(where="name = ?", params=("Updated Record",))
    assert len(results) == 0


def test_create_index(sqlite_manager):
    sqlite_manager.create_index("idx_name", "name", unique=True)
    table_info = sqlite_manager.get_table_info()
    assert any(col["name"] == "name" for col in table_info)


def test_file_based_database(file_sqlite_manager):
    columns = "id INTEGER PRIMARY KEY, name TEXT"
    file_sqlite_manager.create_table(columns)

    test_data = {"name": "File DB Test"}
    file_sqlite_manager.insert_record(test_data)

    results = file_sqlite_manager.select()
    assert len(results) == 1
    assert results[0]["name"] == "File DB Test"
