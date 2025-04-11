from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import os
from repensedb.aws.secrets_manager import SecretsManager


class DatabaseConnection(ABC):
    def __init__(
        self,
        url: Optional[str] = None,
        secrets_name: Optional[str] = None,
        secrets_region: Optional[str] = "us-east-2",
        **kwargs
    ):
        self.connection = None
        self.config: Dict[str, Any] = {}

        self.secrets_manager = None

        if secrets_name:
            self.secrets_manager = SecretsManager(secrets_name, secrets_region)
            self._load_secrets()
        elif url:
            self.url = url
            self.parsed_url = urlparse(url)
            self._parse_url_params()
        else:
            self._load_env_vars()

        # Override URL/secrets/env params with explicit kwargs
        self.config.update(kwargs)

        if not self.config:
            raise ValueError(
                "Connection parameters must be provided via URL, secrets, environment variables, or direct parameters"
            )

    @abstractmethod
    def _parse_url_params(self):
        """Parse connection parameters from URL"""
        pass

    @abstractmethod
    def _load_secrets(self):
        """Load connection parameters from Secrets Manager"""
        pass

    @abstractmethod
    def _load_env_vars(self):
        """Load connection parameters from environment variables"""
        pass

    @abstractmethod
    def connect(self):
        """Establish connection to the database"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the database connection"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active"""
        pass
