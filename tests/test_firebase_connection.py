import pytest
import json
import os

from firebase_admin import delete_app, get_app
from repensedb.connections.firebase import FirebaseConnection


@pytest.fixture
def sample_credentials_dict():
    path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    with open(path, "r") as f:
        creds = json.load(f)
    return creds


@pytest.fixture
def credentials_file():
    path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    return path


@pytest.fixture(autouse=True)
def cleanup_firebase():
    yield
    try:
        delete_app(get_app())
    except ValueError:
        pass


def test_init_with_credentials_dict(sample_credentials_dict):
    conn = FirebaseConnection(credentials_dict=sample_credentials_dict)
    assert conn.config["credentials_dict"] == sample_credentials_dict
    assert conn.app is None


def test_init_with_credentials_path(credentials_file):
    conn = FirebaseConnection(credentials_path=credentials_file)
    assert conn.config["credentials_path"] == credentials_file
    assert conn.app is None


def test_init_without_credentials():
    with pytest.raises(ValueError) as exc_info:
        FirebaseConnection()
    assert "Either credentials_dict or credentials_path must be provided" in str(
        exc_info.value
    )


def test_connect_with_credentials_dict(sample_credentials_dict):
    conn = FirebaseConnection(credentials_dict=sample_credentials_dict)
    try:
        conn.connect()
        assert conn.app is not None
        assert conn.is_connected() is True
    except ValueError as e:
        raise Exception(f"Skipping test due to invalid credentials: {e}")


def test_connect_with_credentials_path(credentials_file):
    conn = FirebaseConnection(credentials_path=credentials_file)
    try:
        conn.connect()
        assert conn.app is not None
        assert conn.is_connected() is True
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")


def test_disconnect(sample_credentials_dict):
    conn = FirebaseConnection(credentials_dict=sample_credentials_dict)
    try:
        conn.connect()
        assert conn.is_connected() is True

        conn.disconnect()
        assert conn.app is None
        assert conn._db is None
        assert conn._auth is None
        assert conn.is_connected() is False
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")


def test_multiple_connections(sample_credentials_dict):
    conn1 = FirebaseConnection(credentials_dict=sample_credentials_dict)
    conn2 = FirebaseConnection(credentials_dict=sample_credentials_dict)

    try:
        conn1.connect()
        conn2.connect()

        assert conn1.app == conn2.app
        assert conn1.is_connected() is True
        assert conn2.is_connected() is True
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")


def test_db_property(sample_credentials_dict):
    conn = FirebaseConnection(credentials_dict=sample_credentials_dict)
    try:
        db = conn.db
        assert db is not None
        assert conn.is_connected() is True
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")


def test_auth_property(sample_credentials_dict):
    conn = FirebaseConnection(credentials_dict=sample_credentials_dict)
    try:
        auth_instance = conn.auth
        assert auth_instance is not None
        assert conn.is_connected() is True
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")


def test_collection_reference(sample_credentials_dict):
    conn = FirebaseConnection(credentials_dict=sample_credentials_dict)
    try:
        collection_ref = conn.collection("test_collection")
        assert collection_ref is not None
        assert collection_ref.id == "test_collection"
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")


def test_document_reference(sample_credentials_dict):
    conn = FirebaseConnection(credentials_dict=sample_credentials_dict)
    try:
        doc_ref = conn.document("test_collection/test_doc")
        assert doc_ref is not None
        assert doc_ref.id == "test_doc"
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")
