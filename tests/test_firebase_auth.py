import pytest
import os
from unittest.mock import Mock

from repensedb.database.firebase.auth import FirebaseAuth
from repensedb.connections.firebase import FirebaseConnection


@pytest.fixture(scope="module")
def auth():
    path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    conn = FirebaseConnection(credentials_path=path)
    firebase_auth = FirebaseAuth(conn)
    yield firebase_auth


@pytest.fixture
def mock_auth():
    mock_conn = Mock()
    firebase_auth = FirebaseAuth(mock_conn)
    return firebase_auth


def test_validate_password_minimum_length(auth):
    error_string = "Password should be at least 6 characters"
    result = auth.validate_password(error_string)
    assert result["6 characters"] is True


def test_validate_password_invalid_length(auth):
    error_string = "Password should be at least 8 characters"
    result = auth.validate_password(error_string)
    assert result["6 characters"] is False


def test_sign_in_success(auth):
    try:
        info = auth.sign_in(
            email=os.getenv("FIREBASE_USER_EMAIL"), 
            password=os.getenv("FIREBASE_USER_PASSWORD")
        )
        assert info["localId"] == os.getenv("FIREBASE_USER_ID")
        assert "idToken" in info
    except ValueError as e:
        pytest.skip(f"Skipping test due to invalid credentials: {e}")