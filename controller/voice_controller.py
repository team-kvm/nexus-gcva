import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import sys
import time
import logging
from os import listdir
from os.path import isfile, join
from pynput.keyboard import Key, Controller
from threading import Thread

class VoiceController:
    def __init__(self, chat_bot_instance):
        self.r = sr.Recognizer()
        self.keyboard = Controller()
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.chat_bot_instance = chat_bot_instance

        self.file_exp_status = False
        self.files = []
        self.path = ''
        self.is_awake = True
        self.today = datetime.date.today()

        with sr.Microphone() as source:
            self.r.energy_threshold = 500
            self.r.dynamic_energy_threshold = False

    def reply(self, audio):
        self.chat_bot_instance.addAppMsg(audio)
        print(audio)
        self.engine.say(audio)
        self.engine.runAndWait()

    def wish(self):
        hour = int(datetime.datetime.now().hour)
        if hour < 12:
            self.reply("Good Morning!")
        elif hour < 18:
            self.reply("Good Afternoon!")
        else:
            self.reply("Good Evening!")
        self.reply("I am Nexus, how may I help you sir?")

    def record_audio(self):
        with sr.Microphone() as source:
            self.r.pause_threshold = 0.8
            try:
                audio = self.r.listen(source, phrase_time_limit=5)
                voice_data = self.r.recognize_google(audio)
                print(f"Recognized speech: {voice_data}")
                return voice_data.lower()
            except sr.RequestError:
                self.reply('Sorry, my service is down. Please check your Internet connection.')
            except sr.UnknownValueError:
                print('Could not understand audio')
            return ''

    def respond(self, voice_data):
        voice_data = voice_data.replace('nexus', '').strip()
        print(f"Processing command: {voice_data}")
        self.chat_bot_instance.addUserMsg(voice_data)

        if not self.is_awake:
            if 'wake up' in voice_data:
                self.is_awake = True
                self.wish()
            return

        if 'hello' in voice_data:
            self.wish()

        elif 'what is your name' in voice_data:
            self.reply('My name is NEXUS!')

        elif 'date' in voice_data:
            self.reply(self.today.strftime("%B %d, %Y"))

        elif 'time' in voice_data:
            self.reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

        elif 'search' in voice_data:
            query = voice_data.split('search', 1)[1]
            self.reply(f'Searching for {query}')
            url = 'https://google.com/search?q=' + query
            try:
                webbrowser.open(url)
                self.reply('This is what I found for you, sir')
            except:
                self.reply('Please check your Internet connection, sir')

        elif 'location' in voice_data:
            self.reply('Which place are you looking for, sir?')
            temp_audio = self.record_audio()
            self.chat_bot_instance.addUserMsg(temp_audio)
            self.reply('Locating...')
            url = 'https://google.com/maps/search/' + temp_audio
            try:
                webbrowser.open(url)
                self.reply('This is what I found for you, sir')
            except:
                self.reply('Please check your Internet connection, sir')

        elif 'bye' in voice_data or 'by' in voice_data:
            self.is_awake = False
            self.reply("Goodbye sir! Have a nice day.")

        elif 'exit' in voice_data or 'terminate' in voice_data:
            self.chat_bot_instance.close()
            sys.exit()

        elif 'copy' in voice_data:
            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press('c')
                self.keyboard.release('c')
            self.reply('Copied to clipboard, sir')

        elif 'paste' in voice_data:
            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press('v')
                self.keyboard.release('v')
            self.reply('Pasted from clipboard, sir')

        elif 'list' in voice_data:
            self.list_files()

        elif self.file_exp_status:
            self.handle_file_navigation(voice_data)

        else:
            self.reply('I am not configured to do this, sir')

    def list_files(self):
        self.path = 'C://'
        self.files = listdir(self.path)
        filestr = ""
        for i, f in enumerate(self.files, 1):
            filestr += f"{i}: {f}<br>"
        self.file_exp_status = True
        self.reply('These are the files in your root directory, sir')
        self.chat_bot_instance.addAppMsg(filestr)

    def handle_file_navigation(self, voice_data):
        if 'open' in voice_data:
            try:
                idx = int(voice_data.split(' ')[-1]) - 1
                selected = self.files[idx]
                full_path = os.path.join(self.path, selected)
                if isfile(full_path):
                    os.startfile(full_path)
                    self.file_exp_status = False
                else:
                    self.path = os.path.join(self.path, selected)
                    self.files = listdir(self.path)
                    filestr = ""
                    for i, f in enumerate(self.files, 1):
                        filestr += f"{i}: {f}<br>"
                    self.reply('Opened successfully, sir')
                    self.chat_bot_instance.addAppMsg(filestr)
            except:
                self.reply('You do not have permission to access this folder, sir')

        elif 'back' in voice_data:
            if self.path == 'C://':
                self.reply('Sorry sir, this is the root directory')
            else:
                self.path = os.path.dirname(os.path.dirname(self.path)) + '//'
                self.files = listdir(self.path)
                filestr = ""
                for i, f in enumerate(self.files, 1):
                    filestr += f"{i}: {f}<br>"
                self.reply('Going back, sir')
                self.chat_bot_instance.addAppMsg(filestr)

