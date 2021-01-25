from threading import Thread
from playerClass import run_gui, PlayerClass

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    player = PlayerClass
    player.search_in_app
    Thread(target=run_gui()).start()


