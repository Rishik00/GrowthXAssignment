from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from bson import ObjectId
from typing import Optional, List

from pydantic import BaseModel
from typing import Optional

class UserAssignment(BaseModel):
    assignment_id: Optional[int]  # Optional, will be assigned dynamically
    name: str
    description: str

class MongoAssignment(UserAssignment):
    # MongoAssignment will be used to serialize the data from MongoDB
    pass

class MyMongoClient:
    
    def __init__(self, atlas_uri: str, dbname: str, cname: str):
        # Initialize MongoDB client and collection
        self.mongodb_client = MongoClient(atlas_uri)
        self.database = self.mongodb_client[dbname]
        self.collection = self.database[cname]
    
    def ping(self):
        """Ping the MongoDB server to confirm connection."""
        self.mongodb_client.admin.command('ping')
        print("Pinged the MongoDB server.")

    def insert_one_document(self, data: UserAssignment):
        """Insert a new document into the collection with a sequential ID."""
        # Get the current maximum assignment_id from the collection and increment it
        last_assignment = self.collection.find().sort("assignment_id", -1).limit(1)  # Sort by assignment_id in descending order
        last_assignment = list(last_assignment)
        new_assignment_id = 1 if not last_assignment else last_assignment[0]["assignment_id"] + 1  # Start at 1 if no documents
        
        # Add the assignment_id to the data
        validated_data = data.model_dump()  # Serialize using model_dump()
        validated_data["assignment_id"] = new_assignment_id  # Set the assignment_id
        
        # Insert the document into the collection
        post_id = self.collection.insert_one(validated_data).inserted_id
        print(f"Inserted document with ID: {new_assignment_id}")
        return new_assignment_id

    def get_all_documents(self, limit: int = 5):
        """Retrieve documents from the collection."""
        assignments = self.collection.find().limit(limit)
        assignments_list = [
            MongoAssignment(
                assignment_id=assignment["assignment_id"], 
                name=assignment["name"], 
                description=assignment["description"]
            )
            for assignment in assignments
        ]
        print(f"Found {len(assignments_list)} documents.")
        return assignments_list

    def get_document_by_id(self, assignment_id: int):
        """Retrieve a specific document by its assignment_id."""
        assignment = self.collection.find_one({"assignment_id": assignment_id})
        if assignment:
            return MongoAssignment(
                assignment_id=assignment["assignment_id"], 
                name=assignment["name"], 
                description=assignment["description"]
            )
        return None

    def delete_one_document(self, assignment_id: int):
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


