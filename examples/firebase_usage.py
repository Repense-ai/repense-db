from repensedb.connections.firebase import FirebaseConnection
from repensedb.database.firebase.manager import FirebaseManager

# Using credentials dictionary
credentials_dict = {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-key-id",
    "private_key": "your-private-key",
    # ... other credential fields ...
}

# Initialize connection
firebase_conn = FirebaseConnection(credentials_dict=credentials_dict)

# Or using credentials file
firebase_conn = FirebaseConnection(credentials_path="path/to/service-account.json")

# Or using secrets manager
firebase_conn = FirebaseConnection(
    secrets_name="firebase-credentials", secrets_region="us-east-1"
)

# Create manager
fb_manager = FirebaseManager(firebase_conn)

# Use the manager
user_data = {"name": "John Doe", "email": "john@example.com"}
doc_id = fb_manager.insert_document("users", data=user_data)

# Query documents
results = fb_manager.query_documents(
    "users", filters=[("email", "==", "john@example.com")], limit=1
)

# Clean up
firebase_conn.disconnect()
