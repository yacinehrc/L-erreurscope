#!/usr/bin/env python3
"""
Reconnaissance vocale en français (Vosk, hors-ligne), en mode "appuyer pour parler" :
maintenez le bouton poussoir enfoncé pour parler, relâchez pour valider.
Affichage sur écran LCD I2C (16x2, backpack PCF8574), un mot par ligne.

Matériel : Raspberry Pi, écran LCD I2C, micro USB, bouton poussoir sur GPIO27.
"""

import json
import queue
import re
import threading
import time
import unicodedata

import sounddevice as sd
import vosk
from gpiozero import Button
from RPLCD.i2c import CharLCD
from text_to_num import alpha2digit

# ---------------------------------------------------------------------------
# CONFIGURATION - à adapter si besoin
# ---------------------------------------------------------------------------
MODEL_PATH = "vosk-model-small-fr-0.22"
SAMPLE_RATE = 16000
DEVICE_INDEX = None

I2C_ADDRESS = 0x27   # confirmé via i2cdetect -y 1
LCD_COLS = 16        # 16 pour un écran 16x2, 20 pour un 20x4
LCD_ROWS = 2         # 2 pour un écran 16x2, 4 pour un 20x4

DELAI_ENTRE_MOTS = 0.6  # secondes d'affichage par mot

BOUTON_PIN = 27  # GPIO27, pin physique 13

lcd = CharLCD('PCF8574', I2C_ADDRESS, cols=LCD_COLS, rows=LCD_ROWS)
bouton = Button(BOUTON_PIN, bounce_time=0.05)

en_ecoute = threading.Event()


def convertir_chiffres(texte):
    """Convertit les nombres écrits en toutes lettres en chiffres (ex. 'quatorze' -> '14')."""
    try:
        return alpha2digit(texte, "fr")
    except Exception:
        return texte


MOIS_FR = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
}
MOTIF_MOIS = re.compile(r"\b(" + "|".join(MOIS_FR.keys()) + r")\b", re.IGNORECASE)


def convertir_mois(texte):
    """Remplace les noms de mois en français par leur numéro sur 2 chiffres (ex. 'mai' -> '05')."""
    return MOTIF_MOIS.sub(lambda m: MOIS_FR[m.group(0).lower()], texte)


MOTIF_DATE = re.compile(r"\b(\d{1,2})\s+(\d{2})\s+(\d{4})\b")


def convertir_dates(texte):
    """Relie jour/mois/année par des '/' quand les 3 se suivent (ex. '14 05 2017' -> '14/05/2017')."""
    return MOTIF_DATE.sub(r"\1/\2/\3", texte)


def retirer_accents(texte):
    """Remplace les caractères accentués par leur équivalent sans accent (ex. 'é' -> 'e'),
    car l'écran LCD ne connaît pas ces caractères et affiche un symbole illisible à la place."""
    nfkd = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def afficher_apercu(texte):
    """Affiche un aperçu rapide (résultat partiel en cours), sans délai entre mots."""
    texte = retirer_accents(texte)
    lcd.clear()
    for i in range(LCD_ROWS):
        debut = i * LCD_COLS
        morceau = texte[debut:debut + LCD_COLS]
        if not morceau:
            break
        lcd.cursor_pos = (i, 0)
        lcd.write_string(morceau)


def afficher_mots(texte, delai=DELAI_ENTRE_MOTS):
    """Affiche chaque mot du texte l'un après l'autre, un mot par ligne."""
    texte = retirer_accents(texte)
    mots = texte.split()
    if not mots:
        afficher_apercu("Rien entendu")
        return
    lcd.clear()
    ligne = 0
    dernier_index = len(mots) - 1
    for index, mot in enumerate(mots):
        lcd.cursor_pos = (ligne, 0)
        lcd.write_string(mot[:LCD_COLS])

        if index == dernier_index:
            break  # dernier mot : on le laisse affiché, pas de clear après

        time.sleep(delai)
        ligne += 1
        if ligne >= LCD_ROWS:
            lcd.clear()
            ligne = 0


# ---------------------------------------------------------------------------
# INITIALISATION DE LA RECONNAISSANCE VOCALE
# ---------------------------------------------------------------------------
vosk.SetLogLevel(-1)
modele = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(modele, SAMPLE_RATE)

audio_queue = queue.Queue()


def callback_audio(indata, frames, temps, status):
    if status:
        print(status)
    if en_ecoute.is_set():
        audio_queue.put(bytes(indata))


def main():
    afficher_apercu("Appuyez pour parler")
    print("Prêt. Maintenez le bouton enfoncé pour parler (Ctrl+C pour arrêter).")

    etait_presse = False

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        device=DEVICE_INDEX,
        dtype="int16",
        channels=1,
        callback=callback_audio,
    ):
        while True:
            presse = bouton.is_pressed

            # Vient d'être pressé : démarre une écoute propre
            if presse and not etait_presse:
                recognizer.Reset()
                with audio_queue.mutex:
                    audio_queue.queue.clear()
                afficher_apercu("Parlez...")
                print("Bouton pressé : écoute en cours...")
                en_ecoute.set()

            # Vient d'être relâché : finalise et affiche
            elif not presse and etait_presse:
                en_ecoute.clear()
                afficher_apercu("Analyse...")
                # Vide tout l'audio encore en attente avant de finaliser,
                # pour ne pas perdre la fin de la phrase
                while True:
                    try:
                        data_restante = audio_queue.get_nowait()
                    except queue.Empty:
                        break
                    recognizer.AcceptWaveform(data_restante)

                resultat = json.loads(recognizer.FinalResult())
                texte = resultat.get("text", "").strip()
                print("Bouton relâché.")
                if texte:
                    texte = convertir_chiffres(texte)
                    texte = convertir_mois(texte)
                    texte = convertir_dates(texte)
                    print("Transcrit :", texte)
                    afficher_mots(texte)
                else:
                    afficher_apercu("Rien entendu")

            etait_presse = presse

            if presse:
                try:
                    data = audio_queue.get(timeout=0.05)
                except queue.Empty:
                    data = None
                if data:
                    if not recognizer.AcceptWaveform(data):
                        partiel = json.loads(recognizer.PartialResult())
                        texte_partiel = partiel.get("partial", "").strip()
                        if texte_partiel:
                            texte_partiel = convertir_chiffres(texte_partiel)
                            texte_partiel = convertir_mois(texte_partiel)
                            texte_partiel = convertir_dates(texte_partiel)
                            afficher_apercu(texte_partiel)
            else:
                time.sleep(0.02)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt.")
        lcd.clear()
        lcd.write_string("Arrete")