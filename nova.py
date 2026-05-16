import pyttsx3
import speech_recognition as sr
import sys

r = sr.Recognizer()
mic = sr.Microphone()

with mic:
    r.adjust_for_ambient_noise(mic, duration=2)

def Hablar(x):
    engine = pyttsx3.init()
    engine.say(x)
    engine.runAndWait()

def reconocerVoz():
    with mic:
        audio = r.listen(mic)

    try:
        return r.recognize_google(audio, language="es-ES")
    
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        Hablar("No tienes internet, necesita tener una conexión a internet para usar el asistente")
        sys.exit(-1)

