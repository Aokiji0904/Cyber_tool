#!/usr/bin/python3

# Importation des modules nécessaires
from scapy.all import *  # Pour la manipulation des paquets réseau
import socket  # Pour la connexion aux ports et la récupération des informations des services
import requests  # Pour effectuer des requêtes HTTP
from tabulate import tabulate  # Pour l'affichage des résultats sous forme de tableau

# Fonction pour scanner les ports ouverts sur une adresse IP cible
def port_scan(target_ip, ports):
    open_ports = []  # Liste pour stocker les ports ouverts
    closed_ports = []  # Liste pour stocker les ports fermés

    # Boucle à travers chaque port dans la plage spécifiée
    for port in ports:
        # Envoi d'un paquet TCP SYN pour vérifier si le port est ouvert
        response = sr1(IP(dst=target_ip)/TCP(dport=port, flags="S"), timeout=1, verbose=0)
        if response is not None:  # Si une réponse est reçue
            if response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:  # Si le drapeau SYN-ACK est reçu
                open_ports.append(port)  # Ajout du port à la liste des ports ouverts
                # Envoi d'un paquet TCP RESET pour terminer la connexion
                send(IP(dst=target_ip)/TCP(dport=response.sport, flags="R"), verbose=0)
            else:
                closed_ports.append(port)  # Ajout du port à la liste des ports fermés

    return open_ports, closed_ports  # Retourne les listes des ports ouverts et fermés

# Fonction pour obtenir la version du service s'exécutant sur un port spécifique
def get_service_version(target_ip, port):
    try:
        # Création d'une connexion socket vers l'IP cible et le port spécifié
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((target_ip, port))
        # Envoi d'une requête spécifique au service pour obtenir la version
        if port == 80:  # Si le port est 80 (HTTP)
            s.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")  # Requête HTTP GET
            response = s.recv(1024)  # Réception de la réponse
            return response.decode().splitlines()[0]  # Retourne la première ligne de la réponse
        else:
            return s.recv(1024).decode()  # Retourne la réponse brute
        s.close()  # Fermeture de la connexion socket
    except Exception as e:
        return f"Unable to determine service version: {e}"  # En cas d'erreur, retourne un message d'erreur

# Fonction pour obtenir la version d'Apache s'exécutant sur un serveur web
def get_apache_version(target_ip):
    try:
        response = requests.get(f"http://{target_ip}")  # Requête HTTP GET à l'adresse cible
        if response.status_code == 200:  # Si la requête réussit
            server_header = response.headers.get("Server")  # Récupération de l'en-tête Server
            if server_header:
                return server_header  # Retourne la version d'Apache
            else:
                return "Unable to determine Apache version"  # Si l'en-tête Server n'est pas trouvé
        else:
            return "Failed to connect to the server"  # Si la connexion échoue
    except Exception as e:
        return f"An error occurred: {e}"  # En cas d'erreur, retourne un message d'erreur

# Point d'entrée du script
if __name__ == "__main__":
    target_ip = input("Saisir l'adresse IP cible : ")  # Demande à l'utilisateur d'entrer l'adresse IP cible
    port_range = input("Entrez la plage de ports (ex: 1-100): ")  # Demande à l'utilisateur d'entrer la plage de ports
    start_port, end_port = map(int, port_range.split("-"))  # Analyse la plage de ports
    ports = range(start_port, end_port + 1)  # Génère une liste de ports dans la plage spécifiée
    open_ports, closed_ports = port_scan(target_ip, ports)  # Appel de la fonction port_scan pour scanner les ports ouverts

    table_data = []  # Liste pour stocker les données du tableau
    for port in open_ports:  # Parcours des ports ouverts
        service_version = ""  # Variable pour stocker la version du service
        if port == 80:  # Si le port est 80 (HTTP)
            service_version = get_apache_version(target_ip)  # Appel de la fonction pour obtenir la version d'Apache
        else:
            service_version = get_service_version(target_ip, port)  # Appel de la fonction pour obtenir la version du service
        table_data.append([port, service_version])  # Ajout du port et de sa version à la liste des données du tableau
    
    # Affichage des résultats sous forme de tableau
    print(tabulate(table_data, headers=["Port", "Service Version"], tablefmt="fancy_grid"))
