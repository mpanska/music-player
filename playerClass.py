from tkinter import Tk, Label, Button
from tkinter import *
import pygame
import time
import os
from PIL import Image, ImageTk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, simpledialog
from mutagen.mp3 import MP3
import speech_recognition as sr
import json
from threading import Thread
import time

import glob

from globals import FILES_DIRECTORY, JSON_DIRECTORY

global my_gui

# TODO: 1) fix next button so when at the end there's no error
#       2) what button was pressed on statusbar
#       3) IndexError: tuple index out of range on forward when nothin selected
#       4) fix play function




class PlayerClass:
    global audio_length

    def __init__(self, master):
        self.stopped = False
        self.if_paused = False
        self.muted = False
        self.if_random = False

        self.songs_dict = {}

        self.master = master
        master.title("Noizemaker")

        self.main_frame = Frame(master)
        self.main_frame.pack(pady=20)


        self.lisbox_frame = Frame(self.main_frame)
        self.lisbox_frame.grid(row=0, column=0)

        #create scrollbar for listbox
        self.scrollbar = Scrollbar(self.lisbox_frame, orient=VERTICAL)
        # create playlist box
        self.song_listbox = Listbox(self.lisbox_frame, fg='black', width=60, yscrollcommand=self.scrollbar.set)

        self.scrollbar.config(command=self.song_listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

       # self.song_listbox.grid(row=0, column=0)
        self.song_listbox.pack(side=LEFT, fill=BOTH, expand=1)


        # Defining and resizing buton images
        self.play_img = Image.open(FILES_DIRECTORY + "play.png")
        self.resized = self.play_img.resize((50, 50), Image.ANTIALIAS)
        self.play_img = ImageTk.PhotoImage(self.resized)
        self.pause_img = Image.open(FILES_DIRECTORY + 'pause.png')
        self.resized = self.pause_img.resize((50, 50), Image.ANTIALIAS)
        self. pause_img = ImageTk.PhotoImage(self.resized)
        self.previous_img = Image.open(FILES_DIRECTORY + "previous.png")
        self.resized = self.previous_img.resize((50, 50), Image.ANTIALIAS)
        self.previous_img = ImageTk.PhotoImage(self.resized)
        self.next_img = Image.open(FILES_DIRECTORY + "next.png")
        self.resized = self.next_img.resize((50, 50), Image.ANTIALIAS)
        self.next_img = ImageTk.PhotoImage(self.resized)
        self.stop_img = Image.open(FILES_DIRECTORY + 'stop.png')
        self.resized = self.stop_img.resize((50, 50), Image.ANTIALIAS)
        self.stop_img = ImageTk.PhotoImage(self.resized)

        # creating buttons frame and control buttons
        self.buttons_frame = Frame(self.main_frame)
        self.buttons_frame.grid(row=1, column=0, pady=10)  # just right under playlist

        self.play_btn = Button(self.buttons_frame, image=self.play_img, borderwidth=0, command=self.play)
        self.pause_btn = Button(self.buttons_frame, image=self.pause_img, borderwidth=0, command=lambda: self.pause(self.if_paused))
        self.previous_btn = Button(self.buttons_frame, image=self.previous_img, borderwidth=0, command=self.previous)
        self.next_btn = Button(self.buttons_frame, image=self.next_img, borderwidth=0, command=self.next)
        self.stop_btn = Button(self.buttons_frame, image=self.stop_img, borderwidth=0, command=self.stop)

        self.previous_btn.grid(row=0, column=0, padx=10)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.play_btn.grid(row=0, column=2, padx=10)
        self.stop_btn.grid(row=0, column=3, padx=10)
        self.next_btn.grid(row=0, column=4, padx=10)


        # creating menu bar
        self.menubar = Menu(master)
        # file menu list
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open file", command=self.open_file)
        self.filemenu.add_command(label="Remove selected song", command=self.remove_song)
        self.filemenu.add_command(label="Clear playlist", command=self.clear_playlist)
        self.filemenu.add_command(label="Save as playlist", command=self.save_dict)
        self.filemenu.add_command(label="Open playlist", command=self.choose_playlist)
        self.filemenu.add_command(label="Open all mp3 files", command=lambda: self.open_all(self.get_files("D:\\")))

        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=master.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        # help menu list
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Help", command=self.show_help)
        self.helpmenu.add_command(label="About", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        master.config(menu=self.menubar)

        # create song time position slider
        self.song_slider = ttk.Scale(self.main_frame, from_=0, to=100, orient=HORIZONTAL, value=0, command=self.progress_song,
                                     length=360)
        self.song_slider.grid(row=2, column=0, pady=10)

        # create volume frame
        self.volume_frame = LabelFrame(self.main_frame, text="Volume")
        self.volume_frame.grid(row=0, column=1, padx=20)

        # create volume slider
        self.volume_slider = ttk.Scale(self.volume_frame, from_=1, to=0, orient=VERTICAL, value=1, length=125, command=self.change_volume)
        self.volume_slider.grid(row=0, column=0, pady=10)

        # Defining and resizing volume buton images
        self.mute_img = Image.open(FILES_DIRECTORY + "mute.png")
        self.resized = self.mute_img.resize((50, 50), Image.ANTIALIAS)
        self.mute_img = ImageTk.PhotoImage(self.resized)
        self.mute_btn = Button(self.volume_frame, image=self.mute_img, borderwidth=0, command=self.mute)
        self.mute_btn.grid(row=1, column=0, pady=10, padx=10)

        # Defining and resizing buton images
        self.volume_img = Image.open(FILES_DIRECTORY + "volume.png")
        self.resized = self.volume_img.resize((50, 50), Image.ANTIALIAS)
        self.volume_img = ImageTk.PhotoImage(self.resized)

        self.voice_frame = Frame(master)
        self.voice_frame.pack(pady=10)

        # create voice recognition status box
        self.voice_label = Label(self.voice_frame, fg='black', width=50, bg='white')
        self.voice_label.config(text='Waiting for your commands...')
        self.voice_label.grid(row=2, column=0)

        # voice button
        self.voice_btn = Button(self.voice_frame, text="Use voice", command=lambda: Thread(target=self.voice_commands).start())
        self.voice_btn.grid(row=2, column=1, padx=10)


        # adding a status bar
        # anchor=E -> east, we put the text to the right side
        self.statusbar = Label(master, text='', bd=1, relief=GROOVE, anchor=E)
        self.statusbar.pack(fill=X, side=BOTTOM, ipady=2)

    # adding a toplevel window for choosing a playlist
    def choose_playlist(self):
        self.playlist_toplvl = Toplevel()
        self.playlist_toplvl.title("Open playlist")
        self.playlist_toplvl.geometry("400x300")

        # adding a list with playlists
        self.list_of_playlists = Listbox(self.playlist_toplvl, fg='black', width=50)
        self.list_of_playlists.pack(pady=10)
        arr_of_playlists = glob.glob(f"{JSON_DIRECTORY}*.json")

        # adding controls
        self.open_pllst_btn = Button(self.playlist_toplvl, text="open playlist", command=lambda: self.read_json(self.list_of_playlists.get(ACTIVE)))
        self.open_pllst_btn.pack(pady=10)

        for file in arr_of_playlists:
            # formatting every file to get only it's name
            filemane = file.split('\\')[-1].split('.')[0]
            self.list_of_playlists.insert(END, filemane)


    def save_dict(self):
        if self.song_listbox.get(END) == "":
            messagebox.showinfo("Error", "There are no songs to create the playlist from")
            return
        file = simpledialog.askstring("Input", "Name of the playlist")
        if file == "" or file is None:
            messagebox.showinfo("Alert!", f'No playlist name was given')
            return
        else:
            messagebox.showinfo("Success", f'New playlist {file} was created')
            # print("Filename: ", file)

        filename = f'{file}.json'
        file_path = JSON_DIRECTORY + filename
        with open(file_path, 'w') as file:
            json.dump(self.songs_dict, file, indent=2)


    def read_json(self, filename):

        if filename is None or filename == "":
            messagebox.showinfo("Error", "No playlist selected")
            return

        file_path = JSON_DIRECTORY + f'{filename}.json'

        with open(file_path) as infile:
            # loading json content into into song dict
            self.songs_dict = json.load(infile)
        print("read json song dict: %s" % self.songs_dict)

        for song in self.songs_dict:
            song_name = song.split('/')[-1].split('.')[0]
            # Insert into listbox
            self.song_listbox.insert(END, song_name)
        # close toplevel after playlist was opened
        self.playlist_toplvl.destroy()


    def change_volume(self, x):
        pygame.mixer.music.set_volume(self.volume_slider.get())


    def show_about(self):
        messagebox.showinfo("About", "This is about")

    def show_help(self):
        messagebox.showinfo("Help", "This is help")

    def progress_song(self, x):
        # loading song from playlist
        song = self.song_listbox.get(ACTIVE)
        song = self.songs_dict.get(song)
        # song = f'{song}.mp3'
        # lading it to a mixer
        pygame.mixer.music.load(song)
        # play it
        pygame.mixer.music.play(loops=0, start=int(self.song_slider.get()))

    def mute(self):
        """
        Function mute() is used to mute and unmute volume
        """
        if self.muted:
            # we need to unmute the music
            pygame.mixer.music.set_volume(self.volume_slider.get())
            self.mute_btn.configure(image=self.volume_img)
            self.muted = False
        else:
            # mute music
            pygame.mixer.music.set_volume(0)
            self.mute_btn.configure(image=self.mute_img)
            self.muted = True


    def open_file(self):
        """
        Function open_file() is used to load songs into application. Can be called with "Open file" menu option
        """
        songs = filedialog.askopenfilenames(title='Open songs', filetypes=(("mp3 Files", "*.mp3"),))
        # Loop by song list and replace directory info and mp3
        for song in songs:
            song_name = song.split('/')[-1].split('.')[0]
            # Insert into listbox
            self.songs_dict[song_name] = song
            print(self.songs_dict)
            self.song_listbox.insert(END, song_name)

    def play(self):
        """
        Function play() is used to play a song, which is an active position of the songs listbox.
        Can be called with 'play' button
        """
        # set to false so song can by played
        self.stop()
        self.stopped = False
        self.if_paused = False
        # loading the song
        song = self.song_listbox.get(ACTIVE)
        song = self.songs_dict.get(song)
        print("play method: (song) %s" % song)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)
        # called to get time and update time slider to current song play time
        self.get_song_time()

    def stop(self):
        """
        Function stop() is used to stop the song which is currently playing.
        Can be called with 'stop' button
        """
        # reset slider when stopped
        # self.statusbar.config(text='stopped')
        self.song_slider.config(value=0)
        # stop playing
        pygame.mixer.music.stop()
        self.song_listbox.selection_clear(ACTIVE)
        # self.statusbar.config(text='')
        # set status
        self.stopped = True

    def pause(self, paused):
        """
        Function pause(paused) is used to pause the song which is currently playing.
        Can be called with 'pause' button
        :param paused: sets the state of global variable if_paused to current state (paused of not)
        """
        self.if_paused = paused
        if self.if_paused:
            pygame.mixer.music.unpause()
            self.if_paused = False
        else:
            pygame.mixer.music.pause()
            self.statusbar.config(text="paused")
            self.if_paused = True

    def next(self):
        """
        Function next() is used to go to the next song in songs listbox playlist.
        Can be called with 'next' button
        """
        self.statusbar.config(text='')
        self.song_slider.config(value=0)
        # get current song's index (needs fix)
        try:
            next_song = self.song_listbox.curselection()
            next_song = next_song[0] + 1
            song = self.song_listbox.get(next_song)
        except IndexError:
            pass

        # song = f'{song}.mp3'
        song = self.songs_dict.get(song)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)

        self.song_listbox.selection_clear(0, END)
        self.song_listbox.activate(next_song)
        self.song_listbox.selection_set(next_song, last=None)

    def previous(self):
        """
        Function previous() is used to go to the previous song in songs listbox playlist.
        Can be called with 'previous' button
        """
        self.statusbar.config(text='')
        self.song_slider.config(value=0)
        # get current song's index
        next_song = self.song_listbox.curselection()
        next_song = next_song[0] - 1
        song = self.song_listbox.get(next_song)

        song = self.songs_dict.get(song)
        # song = f'{song}.mp3'
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)

        self.song_listbox.selection_clear(0, END)
        self.song_listbox.activate(next_song)
        self.song_listbox.selection_set(next_song, last=None)

    def remove_song(self):
        """
        Function remove_song() is used to remove the song from songs listbox playlist.
        Can be called via menu option File -> Remove selected song
        """
        if self.song_listbox.get(ANCHOR) == "" or self.song_listbox.get(ACTIVE) == None:
            messagebox.showinfo("Error", "There's nothing to remove")
            return
        answer = messagebox.askyesno("Remove", "Do you really want to remove this song?")
        if answer:
            self.stop()
            # delete selected song
            self.song_listbox.delete(ANCHOR)
            pygame.mixer.music.stop()
        else:
            pass


    def clear_playlist(self):
        """
        Function clear_playlist() is used to remove all the songs from listbox playlist.
        Can be called via menu option File -> Clear playlist.
        """
        if self.song_listbox.get(END) == "":
            messagebox.showinfo("Clear error", "There's nothing to remove")
            return
        answer = messagebox.askyesno("Clear", "Do you really want to clear the playlist?")
        if answer:
            self.stop()
            self.song_listbox.delete(0, END)
            pygame.mixer.music.stop()
        else:
            pass

    def get_song_time(self):
        if self.stopped:
            return
        if self.if_paused:
            return

        curr_time = pygame.mixer.music.get_pos() / 1000
        formated_time = time.strftime('%M:%S', time.gmtime(curr_time))
        # get current song
        song = self.song_listbox.get(ACTIVE)
        # song = f'{song}.mp3'
        song = self.songs_dict.get(song)
        m_song = MP3(song)

        global audio_length
        audio_length = m_song.info.length  # in seconds
        formated_length = time.strftime('%M:%S', time.gmtime(audio_length))
        # pygame bug, needed to sync time of slider and curr time (1 sec)
        curr_time += 1

        if int(self.song_slider.get()) == int(audio_length):
            # song is over
            self.statusbar.config(text=f'{formated_length} / {formated_length}')
        elif self.if_paused:
            pass
        elif int(self.song_slider.get()) == int(curr_time):
            # not moved
            slider_position = int(audio_length)
            self.song_slider.config(to=slider_position, value=int(curr_time))
        else:
            # moved
            slider_position = int(audio_length)
            self.song_slider.config(to=slider_position, value=int(self.song_slider.get()))
            formated_time = time.strftime('%M:%S', time.gmtime(int(self.song_slider.get())))
            self.statusbar.config(text=f'{formated_time} / {formated_length}')
            moved_time = int(self.song_slider.get()) + 1
            self.song_slider.config(value=moved_time)
        self.statusbar.after(1000, self.get_song_time)


    def voice_commands(self):
        #self.voice_label.config(text='Waiting for your commands...')
        recognizer = sr.Recognizer()
        while True:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                self.voice_label.config(text='Say something')
                # print('say smth')
                audio = recognizer.listen(source)
                try:
                    # self.voice_label.config(text='You said: ' + recognizer.recognize_google(audio))
                    print('u said ' + recognizer.recognize_google(audio))
                    if recognizer.recognize_google(audio) == "play":
                        # print('Play')
                        self.voice_label.config(text='Play')
                        self.play()
                    elif recognizer.recognize_google(audio) == "stop":
                        self.voice_label.config(text='Stop')
                        # print('Stop')
                        self.stop()
                    elif recognizer.recognize_google(audio) == "pause":
                        self.voice_label.config(text='Pause')
                        # print('Pause')
                        self.pause()
                    elif recognizer.recognize_google(audio) == "next":
                        self.voice_label.config(text='Next')
                        # print('Next')
                        self.next()
                    elif (recognizer.recognize_google(audio) == "back") or \
                        (recognizer.recognize_google(audio) == "previous"):
                        self.voice_label.config(text='Back')
                        # print('Back')
                        self.previous()
                    # get out of the loop
                    elif recognizer.recognize_google(audio) == "break":
                        self.voice_label.config(text='Break, quitting voice commands mode.')
                        # print('Break')
                        time.sleep(3)
                        self.voice_label.config(text='Waiting for your commands...(voice mode off)')
                        return
                    else:
                        self.voice_label.config(text="Unknown command: " + recognizer.recognize_google(audio))
                except Exception as e:
                    print("Error: " + str(e))


    def get_files(self, root):
        files = []
        def scan_dir(dir):
            for f in os.listdir(dir):
                try:
                    f = os.path.join(dir, f)
                    if os.path.isdir(f):
                        scan_dir(f)
                    elif os.path.splitext(f)[1] == ".mp3":
                        files.append(f)
                except PermissionError:
                    pass
        scan_dir(root)
        print(files)
        return files

    def open_all(self, path_list):
        for path in path_list:
            # formatting every file to get only it's name
            filemane = path.split('\\')[-1].split('.')[0]
            #print(filemane)
            self.songs_dict[filemane] = path
            self.song_listbox.insert(END, filemane)
        print(self.songs_dict)


# def search_C_and_D():
#     file_D = get_files('D:\\')
#     file_C = get_files('C:\\')
#     file_D.extend(file_C)
#     return file_D



def run_gui():
    # file = search_all_system()
    # file = get_files("D:\\")

    pygame.mixer.init()
    root = Tk()
    root.geometry("600x500")

    global my_gui
    my_gui = PlayerClass(root)
    root.mainloop()










