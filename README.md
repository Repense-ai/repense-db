# RepenseDB 🚀

[![PyPI version](https://badge.fury.io/py/repensedb.svg)](https://badge.fury.io/py/repensedb)
[![Python Versions](https://img.shields.io/pypi/pyversions/repensedb.svg)](https://pypi.org/project/repensedb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful and flexible database manipulation library that provides a unified interface for multiple database systems.

## 🌟 Features

- 🔌 Unified connection interface for multiple databases
- 🔄 Support for MySQL, SQLite, Redis, Firebase, and PostgreSQL
- 🛠 Factory pattern for easy connection creation
- 🔐 Secure credential management
- 🐳 Docker-friendly configuration
- 📦 Easy integration with existing projects

## 🚀 Quick Start

### Installation

```bash
pip install repensedb
```

or with Poetry:

```bash
poetry add repensedb
```

### Basic Usage

```python
from repensedb.connections.factory import ConnectionFactory

# SQLite connection (in-memory)
sqlite_url = "sqlite://:memory:"
sqlite_conn = ConnectionFactory.create(sqlite_url)
sqlite_conn.connect()

# SQLite connection (file-based)
sqlite_file_url = "sqlite:///path/to/database.db"
sqlite_file_conn = ConnectionFactory.create(sqlite_file_url)
sqlite_file_conn.connect()

# MySQL connection
mysql_url = "mysql://user:password@localhost:3306/mydatabase"
mysql_conn = ConnectionFactory.create(mysql_url)
mysql_conn.connect()

# Redis connection
redis_url = "redis://localhost:6379/0"
redis_conn = ConnectionFactory.create(redis_url)
redis_conn.connect()
```

### SQLite Example

```python
from repensedb.connections.sqlite import SQLiteConnection
from repensedb.database.sqlite.manager import SQLiteManager

# Initialize connection and manager
conn = SQLiteConnection(url="sqlite:///myapp.db")
manager = SQLiteManager(conn, "users")

# Create table
columns = """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
"""
manager.create_table(columns)

# Insert data
user = {"name": "John Doe", "email": "john@example.com"}
user_id = manager.insert_record(user)

# Query data
results = manager.select(where="email = ?", params=("john@example.com",))
```

### Firebase Integration

```python
from repensedb.connections.firebase import FirebaseConnection
from repensedb.database.firebase.manager import FirebaseManager

# Initialize with credentials
firebase_conn = FirebaseConnection(credentials_path="path/to/service-account.json")
fb_manager = FirebaseManager(firebase_conn)

# Perform operations
user_data = {"name": "John Doe", "email": "john@example.com"}
doc_id = fb_manager.insert_document("users", data=user_data)
```

## 🔧 Supported Databases

- SQLite (file-based and in-memory)
- MySQL
- Redis
- Firebase
- PostgreSQL

## 📚 Documentation

For detailed documentation and examples, visit our [documentation page](#).

## 🧪 Testing

We use pytest for testing. To run the test suite:

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest
```

## 🛠 Development

### Prerequisites

- Python 3.10+
- Poetry
- Docker (optional, for local database testing)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/repensedb.git
cd repensedb

# Install dependencies
poetry install

# Setup pre-commit hooks
pre-commit install
```

### Code Quality

We maintain high code quality standards using:

- Black for code formatting
- Flake8 for linting
- Pre-commit hooks for consistency

To run code quality checks:

```bash
make lint
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with ❤️ by [Repense.ai](https://repense.ai)
- Maintained by Samuel Alessandro Baptista

---

<p align="center">Made with ❤️ by Repense.ai</p>
