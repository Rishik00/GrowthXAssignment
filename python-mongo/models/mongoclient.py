from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from typing import Optional, List, Union

class UserAssignment(BaseModel):
    assignment_id: Optional[int] = None  # Default to None
    name: str
    user: str
    description: str
    admin: str

class MyMongoClient:
    def __init__(self, atlas_uri: str, dbname: str, cname: str):
        """Initialize MongoDB client and collection."""
        self.mongodb_client = MongoClient(atlas_uri)
        self.database = self.mongodb_client[dbname]
        self.collection = self.database[cname]

        # Ensure assignment_id index
        self.collection.create_index("assignment_id", unique=True)

    def ping(self):
        """Ping the MongoDB server to confirm connection."""
        self.mongodb_client.admin.command("ping")
        print("Pinged the MongoDB server.")

    def insert_one_document(self, data: UserAssignment) -> Optional[int]:
        """Insert a new document into the collection with a sequential ID."""
        try:
            last_assignment = list(self.collection.find().sort("assignment_id", -1).limit(1))
            new_assignment_id = 1 if not last_assignment else last_assignment[0]["assignment_id"] + 1

            validated_data = data.model_dump()
            validated_data["assignment_id"] = new_assignment_id

            self.collection.insert_one(validated_data)
            print(f"Inserted document with assignment_id: {new_assignment_id}")
            return new_assignment_id
        except Exception as e:
            print(f"Error inserting document: {e}")
            return None

    def get_all_documents(self, limit: int = 5) -> List[UserAssignment]:
        """Retrieve documents from the collection."""
        assignments = self.collection.find().limit(limit)
        return [UserAssignment(**assignment) for assignment in assignments]

    def get_document_by_field(self, field: str, value: str) -> Optional[UserAssignment]:
        """Retrieve a document by a specific field."""
        assignment = self.collection.find_one({field: value})
        print(assignment)
        if assignment:
            return UserAssignment(**assignment)
        return None

    def delete_one_document(self, assignment_id: int) -> bool:
        """Delete a document by its assignment_id."""
        try:
            result = self.collection.delete_one({"assignment_id": assignment_id})
            if result.deleted_count > 0:
                print(f"Deleted assignment with ID: {assignment_id}")
                return True
            else:
                print(f"No assignment found to delete with ID: {assignment_id}")
                return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def close(self):
        """Close the MongoDB client connection."""
        self.mongodb_client.close()
