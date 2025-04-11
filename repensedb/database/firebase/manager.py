import logging
from typing import Optional, Dict, Any, List
from repensedb.connections.firebase import FirebaseConnection

logger = logging.getLogger(__name__)


class FirebaseManager:
    """Generic Firebase database manager"""

    def __init__(self, connection: FirebaseConnection):
        """
        Initialize Firebase manager with a database connection

        Args:
            connection: A FirebaseConnection instance
        """
        if not isinstance(connection, FirebaseConnection):
            raise TypeError("Connection must be a FirebaseConnection instance")

        if not connection.is_connected():
            connection.connect()

        self.conn = connection
        self.db = connection.db

    def insert_document(
        self,
        collection: str,
        document_id: Optional[str] = None,
        data: Dict[str, Any] = None,
    ) -> str:
        """
        Insert a document into a collection

        Args:
            collection: Collection name
            document_id: Optional document ID
            data: Document data

        Returns:
            Document ID
        """
        try:
            col_ref = self.db.collection(collection)
            if document_id:
                doc_ref = col_ref.document(document_id)
                doc_ref.set(data)
                return document_id
            else:
                doc_ref = col_ref.add(data)[1]
                return doc_ref.id
        except Exception as e:
            logger.error(f"Error inserting document into {collection}: {e}")
            raise

    def get_document(
        self, collection: str, document_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        try:
            doc = self.db.collection(collection).document(document_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            raise

    def query_documents(
        self, collection: str, filters: List[tuple] = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents with filters

        Args:
            collection: Collection name
            filters: List of (field, operator, value) tuples
            limit: Maximum number of documents to return

        Returns:
            List of document data
        """
        try:
            query = self.db.collection(collection)

            if filters:
                for field, op, value in filters:
                    query = query.where(
                        field_path=field, 
                        op_string=op, 
                        value=value
                    )

            if limit:
                query = query.limit(limit)

            return [doc.to_dict() for doc in query.stream()]
        except Exception as e:
            logger.error(f"Error querying collection {collection}: {e}")
            raise

    def update_document(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any],
        merge: bool = True,
    ) -> None:
        """Update a document"""
        try:
            self.db.collection(collection).document(document_id).set(data, merge=merge)
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            raise

    def delete_document(self, collection: str, document_id: str) -> None:
        """Delete a document"""
        try:
            self.db.collection(collection).document(document_id).delete()
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
