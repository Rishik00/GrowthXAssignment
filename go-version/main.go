package main

import (
	"context"
	"fmt"
	"log"
	"strconv"

	// "mime/quotedprintable"
	"net/http"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type User struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type Admin struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

func HelloEndPoint(c *gin.Context) {
	fmt.Println("Hello world route! Maybe migrtion is going well")
	message := c.Param("message")
	c.JSON(http.StatusOK, gin.H{"Message": message}) // Use gin.H for JSON response
}

func getDocumentsEndpoint(client *mongo.Client) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Extract documentId from URL parameter (string by default)
		documentId := c.Param("id")
		fmt.Println("Received documentId:", documentId)

		// Convert documentId from string to int32
		id, err := strconv.Atoi(documentId) // Convert to int
		if err != nil {
			// Return a 400 Bad Request if the conversion fails
			c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
				"error": "Invalid ID format",
			})
			return
		}
		filter := bson.D{{Key: "assignment_id", Value: int32(id)}} // Convert to int32

		// Fetch the document from the database
		document, err := getOneDocument(client, filter)
		if err != nil {
			// Log error and return 500 Internal Server Error
			fmt.Println("Error fetching document:", err)
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
				"error":   "Failed to fetch document",
				"details": err.Error(),
			})
			return
		}

		// Return the fetched document
		c.JSON(http.StatusOK, gin.H{
			"document": document,
		})
	}
}

func getAllDocumentsEndpoint (client *mongo.Client) gin.HandlerFunc {
	return func(c *gin.Context) {
		documents, err := getAllDocuments(client)
		fmt.Println("All Documents endpoint")
		if err != nil {
			fmt.Println("Error fetching document:", err)
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
				"error":   "Failed to fetch document",
				"details": err.Error(),
			})
			return
		}
		fmt.Println("Results: ", documents)

		c.JSON(http.StatusOK, gin.H{
			"documents": documents,
		})
	}
}

func AddDocEndpoint(client *mongo.Client) gin.HandlerFunc {

    return func(c *gin.Context) {
        // Parse the JSON request body into a UserAssignments struct
        var document UserAssignments
        if err := c.ShouldBindJSON(&document); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{
                "error":   "Invalid request payload",
                "details": err.Error(),
            })
            return
        }

        // Call AddOneDocument to add the new document to the database
        message, err := AddOneDocument(document, client)
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{
                "error":   "Failed to add document",
                "details": err.Error(),
            })
            return
        }

        // Send a successful response
        c.JSON(http.StatusOK, gin.H{
            "message": message,
        })
    }
}

func DeleteEndpoint(client *mongo.Client) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the document ID from the URL parameter
		documentIdStr := c.Param("id")
		fmt.Println("Deleting for document ID: " + documentIdStr)

		// Convert the string ID to an integer
		documentId, err := strconv.Atoi(documentIdStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error":   "Invalid document ID format",
				"details": err.Error(),
			})
			return
		}

		// Call the DeleteOneDocument function
		message, err := DeleteOneDocument(documentId, client)
		if err != nil {
			if err.Error() == "no document found" { // Check for specific "not found" error
				c.JSON(http.StatusNotFound, gin.H{
					"error":   "Document not found",
					"details": err.Error(),
				})
				return
			}

			// Return other errors as internal server errors
			c.JSON(http.StatusInternalServerError, gin.H{
				"error":   "Failed to delete document",
				"details": err.Error(),
			})
			return
		}

		// Send a successful response
		c.JSON(http.StatusOK, gin.H{
			"message": message,
		})
	}
}


func AuthUser(c *gin.Context) {
	var input User

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"Error": err.Error(),
		})
		return 
	}

	c.JSON(http.StatusOK, gin.H{"message": "Username and password validated for user"})
}

func AuthAdmin(c *gin.Context) {
	var input Admin

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"Error": err.Error(),
		})
		return 
	}

	c.JSON(http.StatusOK, gin.H{"message": "Username and password validated for admin"})
}

func main() {
	client, err := ConnectToDB()
	router := gin.Default()

	if err != nil {
		log.Fatalf("Error initializing MongoDB: %v", err)
	}
	defer func() {
		if err := client.Disconnect(context.TODO()); err != nil {
			log.Fatalf("Error disconnecting MongoDB: %v", err)
		}
	}()

	router.POST("/message/:message", HelloEndPoint)
	user := router.Group("/user")
	{
		user.POST("/login/", AuthUser) // Havent tested
		user.GET("/documents/", getAllDocumentsEndpoint(client))
		user.GET("/documents/:id", getDocumentsEndpoint(client))
		user.POST("/documents/", AddDocEndpoint(client))
	}

	admin := router.Group("/admin")
	{
		admin.POST("/login/", AuthAdmin) // Havent tested
		admin.GET("/documents/", getAllDocumentsEndpoint(client))
		admin.GET("/documents/:id", getDocumentsEndpoint(client))
		admin.POST("/documents/", AddDocEndpoint(client))
		admin.DELETE("/documents/:id", DeleteEndpoint(client))
		
	}
	
	// Start the server
	if err := router.Run(); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}


