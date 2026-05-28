import json
import speech_recognition as sr
import pyttsx3 as tts
from ollama import chat

engine = tts.init()
r = sr.Recognizer()
microfone = sr.Microphone(device_index=7)

mode = 1
palavra_ativacao = "ativar"
ativo = False

class config():
    def loadConfigFile():
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def saveConfigFile(configFile):
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(configFile, f, indent=4, ensure_ascii=false)
        
configData = config.loadConfigFile()

def say(text):
    print("IA:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    with microfone as source:
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="pt-BR").lower()
        print("Reconhecido:", text)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print("Erro:", e)
        return ""

def ai(text):
    return chat(
        model="gemma3:4b",
        messages=[
            {"role": "system", "content": config()["personality"]},
            {"role": "user", "content": text}
        ],
    )

def aualizarMemoria(response):
    newMemory = chat(
        model="gemma3:4b",
        messages=[
            {"role": "memory", "content": "quais informações devem ser guardadas da resposta a seguir? " + response}
        ]
    )
    configData["memory"] = configData["memory"] + ", " + newMemory.message.content
    config.saveConfigFile(configData)



with microfone as source:
    r.adjust_for_ambient_noise(source, duration=1)

print("Assistente iniciado.")

while True:
    if mode == 0:
        if not ativo:
            print("Aguardando palavra de ativação...")
            text = listen()

            if "desativar trava" in text:
                mode = 1
                print("trava desativada")
                say("trava desativada")

            if palavra_ativacao in text:
                ativo = True
                print("Ativado!")
                say("Estou ouvindo.")
                
        else:
            print("Aguardando comando...")
            text = listen()

            if "desativar trava" in text:
                mode = 1
                print("trava desativada")
                say("trava desativada")
                continue

            if not text:
                continue

            if "desligar" in text:
                ativo = False
                print("Desativado!")
                say("Desativando.")
                continue

            print("Mandando para a IA:", text)

            response = ai(text).message.content
            say(response)
            
    elif mode == 1:
        text = listen()
        if "ativar trava" in text:
            mode = 0

        if text.startswith("jarvis"):
            print(text)

            print("Mandando para a IA:", text)
            response = ai(text).message.content
            say(response)