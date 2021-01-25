from tkinter import *
import pygame
import os
from PIL import Image, ImageTk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, simpledialog
from mutagen.mp3 import MP3
import speech_recognition as sr
import json
from threading import Thread
import time
import random

from globals import FILES_DIRECTORY, JSON_DIRECTORY, CONFIG_DIRECTORY
global my_gui


# TODO: 1) what button was pressed on statusbar
#       2) IndexError: tuple index out of range on forward when nothin selected


class PlayerClass:
    global audio_length

    def __init__(self, master):
        self.stopped = False
        self.if_paused = False
        self.muted = False
        self.if_random = False

        self.songs_dict = {}
        self.cat_dict = {}

        self.master = master
        master.title("Noizemaker")
        master.iconbitmap(f'{FILES_DIRECTORY}note.ico')

        self.main_frame = Frame(master)
        self.main_frame.pack(pady=20)

        self.lisbox_frame = Frame(self.main_frame)
        self.lisbox_frame.grid(row=0, column=0)

        # create scrollbar for listbox
        self.scrollbar = Scrollbar(self.lisbox_frame, orient=VERTICAL)
        # create playlist box
        self.song_listbox = Listbox(self.lisbox_frame, fg='black', width=60, yscrollcommand=self.scrollbar.set)

        self.scrollbar.config(command=self.song_listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.song_listbox.pack(side=LEFT, fill=BOTH, expand=1)

        # Defining and resizing buton images
        self.play_img = Image.open(FILES_DIRECTORY + "play.png")
        self.resized = self.play_img.resize((50, 50), Image.ANTIALIAS)
        self.play_img = ImageTk.PhotoImage(self.resized)
        self.pause_img = Image.open(FILES_DIRECTORY + 'pause.png')
        self.resized = self.pause_img.resize((50, 50), Image.ANTIALIAS)
        self.pause_img = ImageTk.PhotoImage(self.resized)
        self.previous_img = Image.open(FILES_DIRECTORY + "previous.png")
        self.resized = self.previous_img.resize((50, 50), Image.ANTIALIAS)
        self.previous_img = ImageTk.PhotoImage(self.resized)
        self.next_img = Image.open(FILES_DIRECTORY + "next.png")
        self.resized = self.next_img.resize((50, 50), Image.ANTIALIAS)
        self.next_img = ImageTk.PhotoImage(self.resized)
        self.stop_img = Image.open(FILES_DIRECTORY + 'stop.png')
        self.resized = self.stop_img.resize((50, 50), Image.ANTIALIAS)
        self.stop_img = ImageTk.PhotoImage(self.resized)
        self.shuffle_img = Image.open(FILES_DIRECTORY + 'shuffle.png')
        self.resized = self.shuffle_img.resize((50, 50), Image.ANTIALIAS)
        self.shuffle_img = ImageTk.PhotoImage(self.resized)

        # creating buttons frame and control buttons
        self.buttons_frame = Frame(self.main_frame)
        self.buttons_frame.grid(row=1, column=0, pady=10)  # just right under playlist

        self.play_btn = Button(self.buttons_frame, image=self.play_img, borderwidth=0, command=self.play)
        self.pause_btn = Button(self.buttons_frame, image=self.pause_img, borderwidth=0,
                                command=lambda: self.pause(self.if_paused))
        self.previous_btn = Button(self.buttons_frame, image=self.previous_img, borderwidth=0, command=self.previous)
        self.next_btn = Button(self.buttons_frame, image=self.next_img, borderwidth=0, command=self.next)
        self.stop_btn = Button(self.buttons_frame, image=self.stop_img, borderwidth=0, command=self.stop)
        self.shuffle_btn = Button(self.buttons_frame, image=self.shuffle_img, borderwidth=0, command=self.randomize)

        self.previous_btn.grid(row=0, column=0, padx=10)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.play_btn.grid(row=0, column=2, padx=10)
        self.stop_btn.grid(row=0, column=3, padx=10)
        self.next_btn.grid(row=0, column=4, padx=10)
        self.shuffle_btn.grid(row=0, column=5, padx=10)

        # creating menu bar
        self.menubar = Menu(master)
        # file menu list
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open file", command=self.open_file)
        self.filemenu.add_command(label="Save as playlist", command=self.save_dict)
        self.filemenu.add_command(label="Open playlist", command=self.choose_playlist)
        self.filemenu.add_command(label="Search for file in playlists", command=self.search_in_app)
        self.filemenu.add_command(label="Find song in file system", command=self.open_all)

        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=master.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # edit menu list
        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Remove selected song", command=self.remove_song)
        self.editmenu.add_command(label="Clear playlist", command=self.clear_playlist)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

        # help menu list
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Help", command=self.show_help)
        self.helpmenu.add_command(label="About", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        master.config(menu=self.menubar)

        # create song time position slider
        self.song_slider = ttk.Scale(self.main_frame, from_=0, to=100, orient=HORIZONTAL, value=0,
                                     command=self.progress_song, length=360)
        self.song_slider.grid(row=2, column=0, pady=10)

        # create volume frame
        self.volume_frame = LabelFrame(self.main_frame, text="Volume")
        self.volume_frame.grid(row=0, column=1, padx=20)

        # create volume slider
        self.volume_slider = ttk.Scale(self.volume_frame, from_=1, to=0, orient=VERTICAL, value=0.5, length=125,
                                       command=self.change_volume)
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
        self.voice_btn = Button(self.voice_frame, text="Use voice",
                                command=lambda: Thread(target=self.voice_commands).start())
        self.voice_btn.grid(row=2, column=1, padx=10)

        # adding a status bar
        # anchor=E -> east, we put the text to the right side
        self.statusbar = Label(master, text='', bd=1, relief=GROOVE, anchor=E)
        self.statusbar.pack(fill=X, side=BOTTOM, ipady=2)

    # adding a toplevel window for choosing a playlist
    def choose_playlist(self):
        """
        Function choose_playlist opens a toplevel window with the list of saved playlists and different controls
        """
        # fill categories dict with data
        file_path = CONFIG_DIRECTORY + 'categories.json'
        with open(file_path) as infile:
            self.cat_dict = json.load(infile)

        # creating toplevel frame for playlists
        self.playlist_toplvl = Toplevel()
        self.playlist_toplvl.title("Open playlist")
        self.playlist_toplvl.geometry("400x300")
        self.playlist_toplvl.iconbitmap(f'{FILES_DIRECTORY}note.ico')

        # main toplevel frame:
        toplvl_frame = Frame(self.playlist_toplvl)
        toplvl_frame.pack(pady=10)

        listbox_frame = Frame(toplvl_frame)
        listbox_frame.grid(row=0, column=0)

        pllst_scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)

        # adding a list with playlists
        self.list_of_playlists = Listbox(listbox_frame, fg='black', width=30, height=7, yscrollcommand=pllst_scrollbar.set)
        self.list_of_playlists.pack(pady=10, side=LEFT, fill=BOTH, expand=1)
        # configure scrollbar
        pllst_scrollbar.config(command=self.list_of_playlists.yview())
        pllst_scrollbar.pack(side=RIGHT, fill=Y)

        # load all existing playlists to listbox
        def get_all_playlists():
            """
            Function get_all_playlists() is used to load all of the files saved in playlists directory
            """
            arr_of_playlists = []
            for root, dirs, files in os.walk(JSON_DIRECTORY):
                for fl in files:
                    arr_of_playlists.append(fl)
            return arr_of_playlists
        arr_of_playlists = get_all_playlists()  # arr_of_playlists has paths of all playlists

        # adding controls and defining controls flame
        controls_frame = Frame(toplvl_frame)
        controls_frame.grid(row=1, column=0)
        open_pllst_btn = Button(controls_frame, text="Open playlist", bg="#cbffc4",
                                command=lambda: self.read_json(self.list_of_playlists.get(ACTIVE)))
        open_pllst_btn.grid(row=0, column=0, padx=10)
        delete_pllst_btn = Button(controls_frame, text="Delete playlist", bg='#f29696', command=self.remove_playlist)
        delete_pllst_btn.grid(row=0, column=1, padx=10)

        # inserting all playlists into listbox
        for file in arr_of_playlists:
            # formatting every file to get only it's name
            filemane = file.split('\\')[-1].split('.')[0]
            self.list_of_playlists.insert(END, filemane)

        right_frame = Frame(toplvl_frame)
        right_frame.grid(row=0, column=1)
        # creating dropdown list
        # variable = StringVar(self.playlist_toplvl)
        variable = StringVar(right_frame)
        OPTIONS = self.cat_dict.keys()
        try:
            variable.set(list(self.cat_dict.keys())[0])  # default value
        except IndexError:
             pass  # do nothothing if category dict is empty


        # creating dropdown option menu
        w = OptionMenu(right_frame, variable, *OPTIONS)
        w.grid(row=4, column=0, padx=10)

        def print_filtered_playlists():
            # get current option
            filter = variable.get()
            print(filter)
            result = []
            for category in self.cat_dict:
                # for every key of categoty dict find the selected category
                if category == filter:
                    # if key is as filter: get names of playlists
                    categorized = self.cat_dict.get(category)
                    for root, dirs, files in os.walk(JSON_DIRECTORY):
                        for elem in categorized:
                            if elem in files:
                                result.append(os.path.join(root, elem))
            arr_of_playlists = result
            self.list_of_playlists.delete(0, END)

            for file in arr_of_playlists:
                filename = file.split('/')[-1].split('.')[0]
                self.list_of_playlists.insert(END, filename)


        def add_to_category():
            """
            Function add_to_category is used to add selected playlist to selected category created by user.
            :return:
            """
            counter = 0
            if self.list_of_playlists.get(ANCHOR) == "" or self.list_of_playlists.get(ACTIVE) is None:
                messagebox.showinfo("Error", "No playlist selcted")
                return

            answer = messagebox.askyesno("Add to category", "Add this playlist to category %s?" % variable.get())
            if answer:
                print("answer")
                for file in arr_of_playlists:
                    # iterate through all playlists:
                    filename = file.split('\\')[-1].split('.')[0]
                    # if file name is chosen:
                    if filename == self.list_of_playlists.get(ACTIVE):
                        # add to category dict:
                        for el in self.cat_dict.get(variable.get()):
                            if el == file:
                                counter +=1
                                messagebox.showinfo("Error!",
                                                    f"Playslist {filename} is already in category {variable.get()}.")

                        if counter == 0:
                            print("else")
                            self.cat_dict[variable.get()].append(file)
                            self.rewrite_cat_file()
                            messagebox.showinfo("Succesfully added!", f"Playslist {filename} added to category {variable.get()}.")
                            return
                    else:
                        pass
            else:
                pass

        def remove_filter():
            self.list_of_playlists.delete(0, END)
            arr_of_playlists = get_all_playlists()
            for file in arr_of_playlists:
                # formatting every file to get only it's name
                filemane = file.split('\\')[-1].split('.')[0]
                self.list_of_playlists.insert(END, filemane)

        add_to_cat_btn = Button(right_frame, text="Add playlist to category", command=add_to_category)
        add_to_cat_btn.grid(row=0, column=0, padx=10)

        filter_btn = Button(right_frame, text="Filter", command=print_filtered_playlists)
        filter_btn.grid(row=2, column=0, padx=10, pady=10)
        filter_btn = Button(right_frame, text="Remove filter", command=remove_filter)
        filter_btn.grid(row=3, column=0, padx=10, pady=10)
        self.btn = Button(right_frame, text="Create new category", command=self.create_category)
        self.btn.grid(row=1, column=0, padx=10, pady=10)

    def save_dict(self):
        """
        Function save_dict() is used to save currently opened songs stored in a dictionary to a json file.
        Json files are used as playlists and store audio file name as key and path as a value.
        """
        if self.song_listbox.get(END) == "":
            messagebox.showinfo("Error", "There are no songs to create the playlist from")
            return
        file = simpledialog.askstring("Input", "Name of the playlist")
        if file == "" or file is None:
            messagebox.showinfo("Alert!", f'No playlist name was given')
            return
        else:
            messagebox.showinfo("Success", f'New playlist {file} was created')

        filename = f'{file}.json'
        file_path = JSON_DIRECTORY + filename
        with open(file_path, 'w') as file:
            json.dump(self.songs_dict, file, indent=2)

    def read_json(self, filename):
        """
        Function read_json is needed to read data from json file which contains a playlist.
        :param filename: the name of file that we want to read.
        """
        if filename is None or filename == "":
            messagebox.showinfo("Error", "No playlist selected")
            return

        file_path = JSON_DIRECTORY + f'{filename}.json' # bobux

        with open(file_path) as infile:
            # loading json content into into song dict
            self.songs_dict = json.load(infile)
        print("read json song dict: %s" % self.songs_dict)

        # clear listbox before opening new playlist
        self.song_listbox.delete(0, END)

        for song in self.songs_dict:
            song_name = song.split('/')[-1].split('.')[0]
            # Insert into listbox
            self.song_listbox.insert(END, song_name)
        # close toplevel after playlist was opened
        self.playlist_toplvl.destroy()

    def change_volume(self, x):
        pygame.mixer.music.set_volume(self.volume_slider.get())

    def show_about(self):
        messagebox.showinfo("About",
                            "Noizemaker is an mp3 player aplication, that allows You to play music and create playlists."
                            "\n Created on 2021. \n Creator: Marhatyta Panska")

    def show_help(self):
        messagebox.showinfo("Help", "Voice commands: \n - Play: play selected song\n - Stop: stop\n"
                                    " - Pause: pause current song\n - Next: play next song\n"
                                    " - Back: go back to previous song\n - About: open 'About' information\n"
                                    " - Help: open help information with all voice commands\n "
                                    " - Mute: turn off the volume\n - Unmute: turn the volume on\n"
                                    " - Open: open filedialog to open mp3 files\n - Clear: clears current playlist\n"
                                    " - Remove: removes selected song\n - Save: saves currently opened songs to playlist\n "
                                    " - Shuffle: turns the shuffle mode on or off\n"
                                    "Break: turn off the voice commands mode")

    def progress_song(self, x):
        # loading song from playlist
        song = self.song_listbox.get(ACTIVE)
        song = self.songs_dict.get(song)
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

    def randomize(self):
        """
        Function randomize() is used to turn of the shuffle mode, or turn it off.
        """
        print('shuffle')
        if self.if_random:
            # turn the shuffle mode off
            self.if_random = False
        else:
            # turn it on
            self.if_random = True

    def open_file(self):
        """
        Function open_file() is used to load songs into application. Can be called with "Open file" menu option
        """
        songs = filedialog.askopenfilenames(title='Open songs', filetypes=(("mp3 Files", "*.mp3"),))
        # loop by song list and replace directory info and mp3
        for song in songs:
            song_name = song.split('/')[-1].split('.')[0]
            # insert into listbox
            if song_name in self.songs_dict:
                messagebox.showinfo("Error", "This song is already opedend")
                return
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
        self.song_slider.config(value=0)
        # stop playing
        pygame.mixer.music.stop()
        self.song_listbox.selection_clear(ACTIVE)
        self.statusbar.config(text='stopped')
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

        next_song = self.song_listbox.curselection()
        if self.if_random:
            next_song = self.song_listbox.index(0) + random.randrange(0, len(self.songs_dict))
        else:
            next_song = next_song[0] + 1
        song = self.song_listbox.get(next_song)

        # song = f'{song}.mp3'
        song = self.songs_dict.get(song)
        try:
            pygame.mixer.music.load(song)
        except pygame.error:
            messagebox.showinfo("Alert!", "This is the end of playlist")
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
        try:
            pygame.mixer.music.load(song)
        except pygame.error:
            messagebox.showinfo("Alert!", "This is the end of playlist")

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
        """
        Function voice_commands() is used to recognize voice, convert it into a string and call different
        functions based on that string. Can be called with "Voice command" button.
        """
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
                    elif recognizer.recognize_google(audio) == "back":
                        self.voice_label.config(text='Back')
                        self.previous()
                    elif recognizer.recognize_google(audio) == "help":
                        self.voice_label.config(text='Help')
                        self.show_help()
                    elif recognizer.recognize_google(audio) == "about":
                        self.voice_label.config(text='About')
                        self.show_about()
                    elif recognizer.recognize_google(audio) == "mute":
                        # need to check if the audio is already muted or not
                        if self.muted == True:
                            # if it is, do nothing
                            self.voice_label.config(text='Already muted')
                        else:
                            # if not - mute audio
                            self.voice_label.config(text='Mute')
                            self.mute()
                    elif recognizer.recognize_google(audio) == "unmute":
                        # need to check if the audio is muted or not
                        if self.muted == False:
                            # if it's not - do nothing
                            self.voice_label.config(text='The volume is already on')
                        else:
                            # if it is - unmute it
                            self.voice_label.config(text='Unmute')
                            self.mute()
                    elif recognizer.recognize_google(audio) == "open":
                        self.voice_label.config(text='Open file')
                        self.open_file()
                    elif recognizer.recognize_google(audio) == "shuffle":
                        self.voice_label.config(text='Shuffle')
                        self.randomize()
                    elif recognizer.recognize_google(audio) == "clear":
                        self.voice_label.config(text='Clear playlist')
                        self.clear_playlist()
                    elif recognizer.recognize_google(audio) == "remove":
                        self.voice_label.config(text='Remove selected song')
                        self.remove_song()  # save_dict
                    elif recognizer.recognize_google(audio) == "save":
                        self.voice_label.config(text='Save as playlist')
                        self.save_dict()
                    elif recognizer.recognize_google(audio) == "break":
                        # get out of the loop
                        self.voice_label.config(text='Break, quitting voice commands mode.')
                        # print('Break')
                        time.sleep(3)
                        self.voice_label.config(text='Waiting for your commands...(voice mode off)')
                        return
                    else:
                        self.voice_label.config(text="Unknown command: " + recognizer.recognize_google(audio))
                except Exception as e:
                    print("Error: " + str(e))

    # def get_files(self, root):
    #     files = []
    #     def scan_dir(dir):
    #         for f in os.listdir(dir):
    #             try:
    #                 f = os.path.join(dir, f)
    #                 if os.path.isdir(f):
    #                     scan_dir(f)
    #                 elif os.path.splitext(f)[1] == ".mp3":
    #                     files.append(f)
    #             except PermissionError:
    #                 pass
    #     scan_dir(root)
    #     # print(files)
    #     return files

    def open_all(self):
        """
        Function open_all is used to search through all possible directories and search for
        audio files that start with given string.
        """
        filename = simpledialog.askstring("Search all system", "Search: (It will take some time)")
        # self.statusbar.config(text='Please, wait, it might teake some time...')
        # check if there is any input:
        if filename == "" or filename is None:
            messagebox.showinfo("Alert!", 'No search parameter given!')
            return

        result = []
        drives_list = lambda: (chr(i) + ":\\" for i in range(ord("A"), ord("Z") + 1))

        for drv in drives_list():
            # iterate through all possible drives:
            print(drv)
            for root, dirs, files in os.walk(drv):
                for file in files:
                    # self.statusbar.config(text=f'current drive: {drv}')

                    if file.startswith(filename):
                        # if there's any file that starts with given string:
                        result.append(os.path.join(root, file))
                        # self.statusbar.config(text=f'Path: {os.path.join(root, file)}')
                        song_name = file.split('/')[-1].split('.')[0]

                        if song_name in self.songs_dict:
                            # ignore if the song is alredy on the list
                            continue
                        self.songs_dict[song_name] = os.path.join(root, file)
                        self.song_listbox.insert(END, song_name)
        if not result:
            messagebox.showinfo("Error", "No matches for '%s' found." % filename)

    def remove_playlist(self):
        """
        Function remove_playlist is used to remove the chosen playlist from playlists folder
        """
        playlist_name = self.list_of_playlists.get(ACTIVE)

        if self.list_of_playlists.get(ACTIVE) == "" or self.list_of_playlists.get(ACTIVE) is None:
            messagebox.showinfo("Error", "There's nothing to remove")
            return
        answer = messagebox.askyesno("Remove", "Do you really want to remove this playlist?")
        if answer:
            if os.path.exists(f"{JSON_DIRECTORY}{playlist_name}.json"):
                os.remove(f"{JSON_DIRECTORY}{playlist_name}.json")
                self.list_of_playlists.delete(ANCHOR)
            else:
                messagebox.showinfo("Error", "The file does not exist")
                print("The file does not exist")
        else:
            pass

    # def search_in_app(self):
    #     """
    #     Function search_in_app is used to find all saved playlists and find a song
    #     with a given filename
    #     """
    #     song_to_find = simpledialog.askstring("Find mp3 file saved in application", "Name of the file:")
    #     if song_to_find == "" or song_to_find is None:
    #         messagebox.showinfo("Alert!", 'No file name was given')
    #         return
    #     # search jsons directory for all playlists, save them on list
    #     json_files = [pos_json for pos_json in os.listdir(JSON_DIRECTORY) if pos_json.endswith('.json')]
    #
    #     for filename in json_files:
    #         # iterate through all files in directory
    #         file_path = JSON_DIRECTORY + f'{filename}'
    #         with open(file_path) as infile:
    #             # loading json content into into temp dict
    #             temp_dict = json.load(infile)
    #             if song_to_find in temp_dict:
    #                 # if there is a song somewhere:
    #                 print("in playlist: %s" % filename)
    #                 song_path = temp_dict.get(song_to_find)
    #                 self.songs_dict[song_to_find] = song_path
    #                 self.song_listbox.insert(END, song_to_find)
    #                 return
    #     # if no matches found, show error messagee
    #     messagebox.showinfo("Error", "There is no such file in application.")



    def search_in_app(self):
        """
        Function search_in_app is used to find all saved playlists and find a song
        with a given filename
        """
        song_to_find = simpledialog.askstring("Find mp3 file saved in application", "Name of the file:")
        if song_to_find == "" or song_to_find is None:
            messagebox.showinfo("Alert!", 'No file name was given')
            return
        # search jsons directory for all playlists, save them on list
        json_files = [pos_json for pos_json in os.listdir(JSON_DIRECTORY) if pos_json.endswith('.json')]

        temp_dict = {}
        for filename in json_files:
            # iterate through all files in directory
            file_path = JSON_DIRECTORY + f'{filename}'
            with open(file_path) as infile:
                # loading json content into into temp dict
                temp_dict.update(json.load(infile))

        self.songs_dict = dict(filter(lambda item: song_to_find in item[0], temp_dict.items()))
        if self.songs_dict == {}:
            messagebox.showinfo("Error", "There's nothing like '%s' in application." % song_to_find)
            return

        print(f"search{self.songs_dict}")

        for song in self.songs_dict:
            if self.song_listbox.get(END) == song:
                continue
            self.song_listbox.insert(END, song)


    def create_category(self):
        category = simpledialog.askstring("Create category", "Name of the playlist category:")
        if category == "" or category is None:
            messagebox.showinfo("Alert!", "No category name given.")
            return
        self.cat_dict[category] = []
        print(self.cat_dict)
        self.rewrite_cat_file()

    def rewrite_cat_file(self):
        file_path = CONFIG_DIRECTORY + 'categories.json'
        with open(file_path, 'w') as file:
            json.dump(self.cat_dict, file, indent=2)


def run_gui():
    pygame.mixer.init()
    root = Tk()
    root.geometry("600x500")

    global my_gui
    my_gui = PlayerClass(root)
    root.mainloop()
