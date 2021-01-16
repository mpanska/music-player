import speech_recognition as sr
#from player import create_gui
from threading import Thread
from playerClass import run_gui, PlayerClass
from multiprocessing import Process

def print_hi():
    r = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print('say smth')
            audio = r.listen(source)

            try:
                print('u said ' + r.recognize_google(audio))
                if r.recognize_google(audio) == "hello":
                    print('correct')
                else:
                    print('no')
            except Exception as e:
                print("Err: " + str(e))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    player = PlayerClass
    Thread(target=run_gui()).start()
