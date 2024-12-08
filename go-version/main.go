package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"

	"go.mongodb.org/mongo-driver/mongo"
)

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

// getAllDocumentsEndpoint handles the /alldocuments endpoint
func getAllDocumentsEndpoint(client *mongo.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("Received request at the /alldocuments endpoint")
		documents, err := getAllDocuments(client)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		io.WriteString(w, documents)
	}
}

func main() {
	client, err := ConnectToDB()
	if err != nil {
		log.Fatalf("Error initializing MongoDB: %v", err)
	}
	defer func() {
		if err := client.Disconnect(context.TODO()); err != nil {
			log.Fatalf("Error disconnecting MongoDB: %v", err)
		}
	}()

	// Registering routes
	http.HandleFunc("/", getHelloEndpoint)
	http.Handle("/user/document", getDocumentEndpoint(client))
	http.Handle("/user/alldocuments", getAllDocumentsEndpoint(client))

	fmt.Println("Starting server on port 3333...")
	err = http.ListenAndServe(":3333", nil)
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
