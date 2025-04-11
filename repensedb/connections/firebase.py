from typing import Optional, Dict, Any

from firebase_admin import (
    credentials,
    initialize_app,
    delete_app,
    get_app,
    firestore,
    auth,
)


class FirebaseConnection:
    """Generic Firebase connection handler that can be used with any Firebase project"""

    def __init__(
        self,
        credentials_dict: Optional[Dict[str, Any]] = None,
        credentials_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Firebase connection with credentials.

        Args:
            credentials_dict: Service account credentials dictionary
            credentials_path: Path to service account JSON file
            **kwargs: Additional Firebase configuration parameters
        """
        if not (credentials_dict or credentials_path):
            raise ValueError(
                "Either credentials_dict or credentials_path must be provided"
            )

        self.config = {}
        if credentials_dict:
            self.config["credentials_dict"] = credentials_dict
        elif credentials_path:
            self.config["credentials_path"] = credentials_path

        # Add any additional configuration parameters
        self.config.update(kwargs)

        self.app = None
        self._db = None
        self._auth = None

    def _load_secrets(self) -> Dict[str, Any]:
        """Load Firebase connection parameters from AWS Secrets Manager"""
        pass

    def _load_env_vars(self) -> Dict[str, Any]:
        """Load Firebase connection parameters from environment variables"""
        pass

    def _get_credentials(self) -> credentials.Certificate:
        """Get Firebase credentials from the provided source"""
        if "credentials_dict" in self.config:
            return credentials.Certificate(self.config["credentials_dict"])
        elif "credentials_path" in self.config:
            return credentials.Certificate(self.config["credentials_path"])
        else:
            raise ValueError(
                "Firebase credentials must be provided either via credentials_dict or credentials_path"
            )

    def connect(self):
        """Initialize Firebase app"""
        try:
            self.app = get_app()
        except ValueError:
            cred = self._get_credentials()

            # Extract optional initialization options
            options = {
                k: v
                for k, v in self.config.items()
                if k not in ["credentials_dict", "credentials_path"]
            }

            self.app = initialize_app(credential=cred, options=options)
        return self.app

    def disconnect(self):
        """Delete Firebase app instance"""
        if self.app:
            delete_app(self.app)
            self.app = None
            self._db = None
            self._auth = None

    def is_connected(self) -> bool:
        """Check if Firebase app is initialized"""
        try:
            get_app()
            return True
        except ValueError:
            return False

    @property
    def db(self) -> firestore.Client:
        """Get Firestore client"""
        if not self.is_connected():
            self.connect()
        if not self._db:
            self._db = firestore.client(self.app)
        return self._db

    @property
    def auth(self) -> auth:
        """Get Firebase Auth instance"""
        if not self.is_connected():
            self.connect()
        if not self._auth:
            self._auth = auth
        return self._auth

    def collection(self, name: str) -> firestore.CollectionReference:
        """Get a Firestore collection reference"""
        return self.db.collection(name)

    def document(self, path: str) -> firestore.DocumentReference:
        """Get a Firestore document reference"""
        return self.db.document(path)
