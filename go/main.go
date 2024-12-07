package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/joho/godotenv" // Load environment variables from .env file
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Load environment variables from the .env file
func init() {
	if err := godotenv.Load(); err != nil {
		log.Println("Warning: No .env file found.")
	}
}

// ConnectToDB initializes the MongoDB client and returns a connected client
func ConnectToDB() (*mongo.Client, error) {
	// Retrieve MongoDB URI from environment variables
	uri := os.Getenv("MONGO_URI")
	if uri == "" {
		return nil, fmt.Errorf("Set the mongo_uri environment variable")
	}

	// Connect to MongoDB
	client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(uri))
	if err != nil {
		return nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}

	// Verify the connection
	if err = client.Ping(context.TODO(), nil); err != nil {
		client.Disconnect(context.TODO())
		return nil, fmt.Errorf("failed to ping MongoDB: %w", err)
	}

	return client, nil
}

// getOneDocument fetches a single document from the specified collection
func getOneDocument(client *mongo.Client) (string, error) {
	coll := client.Database("User").Collection("UserAssignments")
	var result bson.M

	err := coll.FindOne(context.TODO(), bson.D{{"user", "user1"}}).Decode(&result)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return "", fmt.Errorf("no document found")
		}
		return "", fmt.Errorf("error fetching document: %w", err)
	}

	jsonData, err := json.MarshalIndent(result, "", "   ")
	if err != nil {
		return "", fmt.Errorf("error marshalling document to JSON: %w", err)
	}

	return string(jsonData), nil
}

// getHelloEndpoint handles the root endpoint
func getHelloEndpoint(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Received request at root endpoint")
	io.WriteString(w, "Hello, HTTP!")
}

// getDocumentEndpoint handles the /document endpoint
func getDocumentEndpoint(client *mongo.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("Received request at /document endpoint")
		document, err := getOneDocument(client)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		io.WriteString(w, document)
	}
}

func main() {
	// Connect to MongoDB
	client, err := ConnectToDB()
	if err != nil {
		log.Fatalf("Error initializing MongoDB: %v", err)
	}
	defer func() {
		if err := client.Disconnect(context.TODO()); err != nil {
			log.Fatalf("Error disconnecting MongoDB: %v", err)
		}
	}()

	// Setup HTTP routes
	http.HandleFunc("/", getHelloEndpoint)
	http.HandleFunc("/document", getDocumentEndpoint(client))

	// Start HTTP server at http://localhost:3333/
	fmt.Println("Starting server on port 3333...")
	err = http.ListenAndServe(":3333", nil)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
