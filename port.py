#!/usr/bin/python3

# Importation des modules n�cessaires
from scapy.all import *  # Pour la manipulation des paquets r�seau
import socket  # Pour la connexion aux ports et la r�cup�ration des informations des services
import requests  # Pour effectuer des requ�tes HTTP
from tabulate import tabulate  # Pour l'affichage des r�sultats sous forme de tableau

# Fonction pour scanner les ports ouverts sur une adresse IP cible
def port_scan(target_ip, ports):
    open_ports = []  # Liste pour stocker les ports ouverts
    closed_ports = []  # Liste pour stocker les ports ferm�s

    # Boucle � travers chaque port dans la plage sp�cifi�e
    for port in ports:
        # Envoi d'un paquet TCP SYN pour v�rifier si le port est ouvert
        response = sr1(IP(dst=target_ip)/TCP(dport=port, flags="S"), timeout=1, verbose=0)
        if response is not None:  # Si une r�ponse est re�ue
            if response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:  # Si le drapeau SYN-ACK est re�u
                open_ports.append(port)  # Ajout du port � la liste des ports ouverts
                # Envoi d'un paquet TCP RESET pour terminer la connexion
                send(IP(dst=target_ip)/TCP(dport=response.sport, flags="R"), verbose=0)
            else:
                closed_ports.append(port)  # Ajout du port � la liste des ports ferm�s

    return open_ports, closed_ports  # Retourne les listes des ports ouverts et ferm�s

# Fonction pour obtenir la version du service s'ex�cutant sur un port sp�cifique
def get_service_version(target_ip, port):
    try:
        # Cr�ation d'une connexion socket vers l'IP cible et le port sp�cifi�
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((target_ip, port))
        # Envoi d'une requ�te sp�cifique au service pour obtenir la version
        if port == 80:  # Si le port est 80 (HTTP)
            s.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")  # Requ�te HTTP GET
            response = s.recv(1024)  # R�ception de la r�ponse
            return response.decode().splitlines()[0]  # Retourne la premi�re ligne de la r�ponse
        else:
            return s.recv(1024).decode()  # Retourne la r�ponse brute
        s.close()  # Fermeture de la connexion socket
    except Exception as e:
        return f"Unable to determine service version: {e}"  # En cas d'erreur, retourne un message d'erreur

# Fonction pour obtenir la version d'Apache s'ex�cutant sur un serveur web
def get_apache_version(target_ip):
    try:
        response = requests.get(f"http://{target_ip}")  # Requ�te HTTP GET � l'adresse cible
        if response.status_code == 200:  # Si la requ�te r�ussit
            server_header = response.headers.get("Server")  # R�cup�ration de l'en-t�te Server
            if server_header:
                return server_header  # Retourne la version d'Apache
            else:
                return "Unable to determine Apache version"  # Si l'en-t�te Server n'est pas trouv�
        else:
            return "Failed to connect to the server"  # Si la connexion �choue
    except Exception as e:
        return f"An error occurred: {e}"  # En cas d'erreur, retourne un message d'erreur

# Point d'entr�e du script
if __name__ == "__main__":
    target_ip = input("Saisir l'adresse IP cible : ")  # Demande � l'utilisateur d'entrer l'adresse IP cible
    port_range = input("Entrez la plage de ports (ex: 1-100): ")  # Demande � l'utilisateur d'entrer la plage de ports
    start_port, end_port = map(int, port_range.split("-"))  # Analyse la plage de ports
    ports = range(start_port, end_port + 1)  # G�n�re une liste de ports dans la plage sp�cifi�e
    open_ports, closed_ports = port_scan(target_ip, ports)  # Appel de la fonction port_scan pour scanner les ports ouverts

    table_data = []  # Liste pour stocker les donn�es du tableau
    for port in open_ports:  # Parcours des ports ouverts
        service_version = ""  # Variable pour stocker la version du service
        if port == 80:  # Si le port est 80 (HTTP)
            service_version = get_apache_version(target_ip)  # Appel de la fonction pour obtenir la version d'Apache
        else:
            service_version = get_service_version(target_ip, port)  # Appel de la fonction pour obtenir la version du service
        table_data.append([port, service_version])  # Ajout du port et de sa version � la liste des donn�es du tableau
    
    # Affichage des r�sultats sous forme de tableau
    print(tabulate(table_data, headers=["Port", "Service Version"], tablefmt="fancy_grid"))
