package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"

	// "github.com/bytedance/sonic/option"
	"github.com/joho/godotenv" // Load environment variables from .env file
	// "github.com/mailru/easyjson/opt/optional"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type UserAssignments struct {
	AssignmentID int    `bson:"assignment_id" json:"assignment_id"`
	Name         string `bson:"name" json:"name"`
	User         string `bson:"user" json:"user"`
	Description  string `bson:"description" json:"description"`
	Admin        string `bson:"admin" json:"admin"`
}

// Load environment variables from the .env file
func init() {
	if err := godotenv.Load(); err != nil {
		log.Println("Warning: No .env file found.")
	}
}

// ConnectToDB initializes the MongoDB client and returns a connected client
func ConnectToDB() (*mongo.Client, error) {
	uri := os.Getenv("MONGO_URI")
	fmt.Println("Connected to the mongo cluster")
	if uri == "" {
		return nil, fmt.Errorf("set the mongo_uri environment variable")
	}

	client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(uri))
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}

	if err = client.Ping(context.TODO(), nil); err != nil {
		client.Disconnect(context.TODO())
		return nil, fmt.Errorf("failed to ping MongoDB: %w", err)
	}

	return client, nil
}

// getOneDocument fetches a single document from the specified collection
func getOneDocument(client *mongo.Client, filter bson.D) (string, error) {
	coll := client.Database("User").Collection("UserAssignments")
	var result bson.M

	fmt.Println("Here in the enddpoint fn")
	err := coll.FindOne(context.TODO(), filter).Decode(&result)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return "", fmt.Errorf("no document found")
		}
		return "", fmt.Errorf("error fetching document: %w", err)
	}
	fmt.Println("Result: ", result)
	jsonData, err := json.MarshalIndent(result, "", "   ")
	if err != nil {
		return "", fmt.Errorf("error marshalling document to JSON: %w", err)
	}

	return string(jsonData), nil
}


func getAllDocuments(client *mongo.Client) (string, error) {
	coll := client.Database("User").Collection("UserAssignments")
	filter := bson.D{{Key: "user", Value: "user1"}} // Filter for user1 documents

	cursor, err := coll.Find(context.TODO(), filter)
	fmt.Printf("Cursor: %+v\n", cursor)

	if err != nil {
		return "", fmt.Errorf("error finding documents: %w", err)
	}
	defer cursor.Close(context.TODO())

	var results []UserAssignments
	if err = cursor.All(context.TODO(), &results); err != nil {
		return "", fmt.Errorf("error decoding documents: %w", err)
	}

	jsonData, err := json.MarshalIndent(results, "", "   ")
	if err != nil {
		return "", fmt.Errorf("error marshalling documents to JSON: %w", err)
	}

	return string(jsonData), nil
}

func getLatestAssignmentID(client *mongo.Client) (int, error) {
    coll := client.Database("User").Collection("UserAssignments")

    // Sort by 'AssignmentID' in descending order and limit the result to 1
    var result UserAssignments
    err := coll.FindOne(
        context.TODO(),
        bson.D{}, // No filter, get all documents
        options.FindOne().SetSort(bson.D{{Key: "assignment_id", Value: -1}}),
    ).Decode(&result)
    
    if err != nil {
        if err == mongo.ErrNoDocuments {
            return 0, fmt.Errorf("no documents found")
        }
        return 0, fmt.Errorf("error fetching latest document: %w", err)
    }

    return result.AssignmentID, nil
}

func AddOneDocument(document UserAssignments, client *mongo.Client) (string, error) {
    fmt.Println("Inserting one document")
    coll := client.Database("User").Collection("UserAssignments")

    // Get the latest AssignmentID
    latestID, err := getLatestAssignmentID(client)
    if err != nil {
        return "", fmt.Errorf("error getting latest assignment ID: %w", err)
    }

    // Set the next AssignmentID
    document.AssignmentID = latestID + 1

    result, err := coll.InsertOne(context.TODO(), document)
    if err != nil {
        return "", fmt.Errorf("error inserting document: %w", err)
    }

    fmt.Printf("Inserted document with ID: %v\n", result.InsertedID)
    return "Success", nil
}

func DeleteOneDocument(documentId int, client *mongo.Client) (string, error) {
	fmt.Println("Deleting one document")
	coll := client.Database("User").Collection("UserAssignments")

	result, err := coll.DeleteOne(context.TODO(), bson.D{{Key: "assignment_id", Value: documentId}})
	if err != nil {
		return "", fmt.Errorf("Error deleting document: %w", err)
	}

	fmt.Println("Deleted document %w", result)
	return "Success", nil
}


// func mongo_hello() {
//     fmt.Println("In mongoclient.go, executing")
//     client, err := ConnectToDB()
//     if err != nil {
//         log.Fatalf("Error connecting to DB: %v", err)
//     }
//     defer func() {
//         if err := client.Disconnect(context.TODO()); err != nil {
//             log.Fatalf("Error disconnecting DB: %v", err)
//         }
//     }()

//     // Fetch all documents
//     allDocs, err := getAllDocuments(client)
//     if err != nil {
//         log.Fatalf("Error fetching all documents: %v", err)
//     }
//     fmt.Println("All Documents:", allDocs)

//     // Fetch one document
//     oneDoc, err := getOneDocument(client)
//     if err != nil {
//         log.Fatalf("Error fetching one document: %v", err)
//     }
//     fmt.Println("One Document:", oneDoc)

//     // Insert a new document
//     document := UserAssignments{
//         AssignmentID: 3, // Ensure this ID is unique
//         Name:         "Urgent Assignment",
//         User:         "user1",
//         Description:  "Complete ASAP",
//         Admin:        "admin2",
//     }
//     res, err := AddOneDocument(document, client)
//     if err != nil {
//         log.Fatalf("Error inserting document: %v", err)
//     }
//     fmt.Println("Insert Result:", res)

//     // Fetch all documents again
//     updatedDocs, err := getAllDocuments(client)
//     if err != nil {
//         log.Fatalf("Error fetching updated documents: %v", err)
//     }
//     fmt.Println("Updated Documents:", updatedDocs)
// }
