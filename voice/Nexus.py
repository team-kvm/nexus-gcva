import eel
import os
from queue import Queue

class ChatBot:
    started = False
    userinputQueue = Queue()

    def isUserInput(self):
        return not ChatBot.userinputQueue.empty()

    def popUserInput(self):
        return ChatBot.userinputQueue.get()

    def close_callback(route, websockets):
        if not websockets:
            print('WebSocket disconnected, closing application...')
        exit()

    @eel.expose
    def getUserInput(self, msg):
        ChatBot.userinputQueue.put(msg)
        print(f"Received input from GUI: {msg}")  # Debugging line

    def close(self):
        ChatBot.started = False
        print("Chatbot is shutting down.")

    def addUserMsg(self, msg):
        eel.addUserMsg(msg)

    def addAppMsg(self, msg):
        eel.addAppMsg(msg)

    def start(self):
        path = os.path.dirname(os.path.abspath(__file__))
        eel.init(path + r'\web', allowed_extensions=['.js', '.html'])
        try:
            eel.start('index.html', mode='edge',
                      host='localhost',
                      port=27005,
                      block=False,
                      size=(350, 480),
                      position=(10, 100),
                      disable_cache=True,
                      close_callback=ChatBot.close_callback)
            ChatBot.started = True
            while ChatBot.started:
                try:
                    eel.sleep(10.0)
                except:
                    break
        except Exception as e:
            print(f"Error starting eel: {e}")

