#!/usr/bin/env python3
import json
import queue
import re
import subprocess
import threading
import time
import unicodedata
from pathlib import Path

import sounddevice as sd
import vosk
from gpiozero import Button
from RPLCD.i2c import CharLCD
from text_to_num import alpha2digit

MODEL_PATH = "vosk-model-small-fr-0.22"
DEVICE_INDEX = 1
SAMPLE_RATE = int(sd.query_devices(DEVICE_INDEX, "input")["default_samplerate"])

I2C_ADDRESS = 0x27
LCD_COLS = 16
LCD_ROWS = 2
DELAI_ENTRE_MOTS = 0.6

BOUTON_PIN = 27

DOSSIER_AUDIOS = Path("/home/pi/erreurscope/audios")
NB_VOCAUX = 10
SORTIE_AUDIO = "plughw:CARD=Headphones,DEV=0"

MOIS_FR = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
}
MOTIF_MOIS = re.compile(r"\b(" + "|".join(MOIS_FR) + r")\b", re.IGNORECASE)
MOTIF_DATE = re.compile(r"\b(\d{1,2})\s+(\d{2})\s+(\d{4})\b")
MOTIF_DATE_COMPLETE = re.compile(r"\b\d{1,2}/\d{2}/\d{4}\b")
MOTIF_MOT = re.compile(r"[^\W\d_]{2,}")

lcd = CharLCD("PCF8574", I2C_ADDRESS, cols=LCD_COLS, rows=LCD_ROWS)
bouton = Button(BOUTON_PIN, bounce_time=0.05)

vosk.SetLogLevel(-1)
recognizer = vosk.KaldiRecognizer(vosk.Model(MODEL_PATH), SAMPLE_RATE)

audio_queue = queue.Queue()
en_ecoute = threading.Event()
lecteur = None
numero = 1


def normaliser(texte):
    try:
        texte = alpha2digit(texte, "fr")
    except Exception:
        pass
    texte = MOTIF_MOIS.sub(lambda m: MOIS_FR[m.group(0).lower()], texte)
    return MOTIF_DATE.sub(r"\1/\2/\3", texte)


def contient_nom_et_date(texte):
    return bool(MOTIF_DATE_COMPLETE.search(texte) and MOTIF_MOT.search(texte))


def sans_accents(texte):
    nfkd = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def afficher(texte):
    texte = sans_accents(texte)
    lcd.clear()
    for ligne in range(LCD_ROWS):
        morceau = texte[ligne * LCD_COLS:(ligne + 1) * LCD_COLS]
        if not morceau:
            break
        lcd.cursor_pos = (ligne, 0)
        lcd.write_string(morceau)


def afficher_mots(texte):
    mots = sans_accents(texte).split()
    lcd.clear()
    for index, mot in enumerate(mots):
        ligne = index % LCD_ROWS
        if index and ligne == 0:
            lcd.clear()
        lcd.cursor_pos = (ligne, 0)
        lcd.write_string(mot[:LCD_COLS])
        if index < len(mots) - 1:
            time.sleep(DELAI_ENTRE_MOTS)


def arreter_audio():
    if lecteur and lecteur.poll() is None:
        lecteur.terminate()


def jouer_vocal_suivant():
    global lecteur, numero
    chemin = DOSSIER_AUDIOS / f"vocal {numero}.mp3"
    numero = numero % NB_VOCAUX + 1
    if chemin.exists():
        arreter_audio()
        lecteur = subprocess.Popen(["mpg123", "-q", "-o", "alsa", "-a", SORTIE_AUDIO, str(chemin)])


def callback_audio(indata, frames, temps, status):
    if en_ecoute.is_set():
        audio_queue.put(bytes(indata))


def main():
    afficher("Appuyez pour parler")
    etait_presse = False
    dernier_partiel = ""

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=4000,
        latency="high",
        device=DEVICE_INDEX,
        dtype="int16",
        channels=1,
        callback=callback_audio,
    ):
        while True:
            presse = bouton.is_pressed

            if presse and not etait_presse:
                arreter_audio()
                recognizer.Reset()
                dernier_partiel = ""
                with audio_queue.mutex:
                    audio_queue.queue.clear()
                afficher("Parlez...")
                en_ecoute.set()

            elif etait_presse and not presse:
                en_ecoute.clear()
                afficher("Analyse...")
                while not audio_queue.empty():
                    recognizer.AcceptWaveform(audio_queue.get_nowait())
                texte = normaliser(json.loads(recognizer.FinalResult()).get("text", "").strip())
                if texte:
                    print("Transcrit :", texte)
                    afficher_mots(texte)
                    if contient_nom_et_date(texte):
                        jouer_vocal_suivant()
                else:
                    afficher("Rien entendu")

            etait_presse = presse

            if not presse:
                time.sleep(0.02)
                continue

            try:
                data = audio_queue.get(timeout=0.05)
            except queue.Empty:
                continue

            if recognizer.AcceptWaveform(data):
                continue

            partiel = normaliser(json.loads(recognizer.PartialResult()).get("partial", "").strip())
            if partiel and partiel != dernier_partiel:
                afficher(partiel)
                dernier_partiel = partiel


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        arreter_audio()
        lcd.clear()