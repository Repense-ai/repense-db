import pytest
import os
import json

from unittest.mock import Mock
from google.api_core.exceptions import InvalidArgument


from repensedb.database.firebase.manager import FirebaseManager
from repensedb.connections.firebase import FirebaseConnection


@pytest.fixture(scope="module")
def firebase_connection():
    conn = FirebaseConnection(credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH"))
    yield conn


@pytest.fixture(scope="module")
def manager(firebase_connection):
    firebase_manager = FirebaseManager(firebase_connection)
    yield firebase_manager


@pytest.fixture
def mock_manager():
    mock_conn = Mock()
    mock_conn.is_connected.return_value = True
    manager = FirebaseManager(mock_conn)
    return manager


def test_manager_initialization(firebase_connection):
    manager = FirebaseManager(firebase_connection)
    assert isinstance(manager, FirebaseManager)
    assert manager.conn == firebase_connection
    assert manager.db is not None


def test_get_document(manager):

    doc = manager.get_document(
        collection="users",
        document_id="test_user_id"
    )

    assert doc is None


def test_get_nonexistent_document(manager):
    doc = manager.get_document(
        collection="users",
        document_id="nonexistent_id"
    )
    assert doc is None


def test_insert_document(manager):
    test_data = {
        "name": "Test User",
        "email": "test@example.com"
    }

    doc_id = manager.insert_document(
        collection="test_collection",
        data=test_data
    )
    assert doc_id is not None
    manager.delete_document("test_collection", doc_id)


def test_update_document(manager):
    # First insert a test document
    initial_data = {"status": "initial"}

    doc_id = manager.insert_document("test_collection", json.dumps(initial_data))
    
    # Update the document
    update_data = {"status": "updated"}
    
    manager.update_document(
        collection="test_collection",
        document_id=doc_id,
        data=update_data
    )

    # Verify update
    updated_doc = manager.get_document("test_collection", doc_id)
    assert updated_doc["status"] == "updated"

    # Cleanup
    manager.delete_document("test_collection", doc_id)


def test_delete_document(manager):
    # First insert a test document
    test_data = {"test": "data"}

    doc_id = manager.insert_document("test_collection", json.dumps(test_data))
    
    # Delete the document
    manager.delete_document("test_collection", doc_id)

    # Verify deletion
    deleted_doc = manager.get_document("test_collection", doc_id)
    assert deleted_doc is None


def test_query_documents(manager):
    # Insert test documents
    test_data = [
        {"type": "test", "value": 1},
        {"type": "test", "value": 2},
        {"type": "test", "value": 3}
    ]
    doc_ids = []
    for data in test_data:
        doc_id = manager.insert_document("test_collection", json.dumps(data))
        doc_ids.append(doc_id)

    # Query documents
    results = manager.query_documents(
        collection="test_collection",
        filters=[("type", "==", "test")],
        limit=2
    )
    
    assert results is not None

    # Cleanup
    for doc_id in doc_ids:
        manager.delete_document("test_collection", doc_id)
