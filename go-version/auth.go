package main

import (
	"fmt"
	"time"
	"github.com/golang-jwt/jwt/v5"
)

var SecretKey = []byte("secret-key")

func createToken(username string) (string, error) {
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, 
        jwt.MapClaims{ 
        "username": username, 
        "exp": time.Now().Add(time.Hour * 24).Unix(), 
        })

    tokenString, err := token.SignedString(SecretKey)
    if err != nil {
    return "", err
    }

 return tokenString, nil
}

func verifyToken(tokenString string) error {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		return SecretKey, nil
	})
	if err != nil {
		fmt.Println("Somethings off...")
		return nil
	}

	return nil
}

