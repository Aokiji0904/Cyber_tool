#!/usr/bin/env python
#coding: utf-8

import socket
import sys

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Création d'un socket TCP/IP
port = 50000 # Définition du port d'écoute du serveur

clientsocket.bind(('', port)) # Liaison du socket à l'adresse locale et au port spécifié
clientsocket.listen(5) # Mise en écoute du socket avec une file d'attente de 5 connexions maximum
print('Le serveur est démarré et écoute sur le port' + str(port)) # Affichage d'un message indiquant que le serveur est en écoute

while 1: # Boucle infinie pour accepter les connexions entrantes
    (serveursocket, address) = clientsocket.accept() # Acceptation d'une nouvelle connexion
    print("nouvelle connexion à partir de  :" + str(address)) # Affichage de l'adresse de la nouvelle connexion
    print("envoie de commandes : ") # Affichage d'un message pour indiquer que les commandes peuvent être envoyées
    while 1: # Boucle infinie pour envoyer et recevoir des commandes
        r = str(sys.stdin.readline()) # Lecture d'une commande entrée par l'utilisateur
        serveursocket.send(r.encode()) # Envoi de la commande au serveur
        r = serveursocket.recv(9999) # Réception de la réponse du serveur
        client_answer = str(r.decode("utf-8", errors = "ignore")) # Décodage de la réponse en chaîne de caractères
        print(str(client_answer) + "\n") # Affichage de la réponse reçue