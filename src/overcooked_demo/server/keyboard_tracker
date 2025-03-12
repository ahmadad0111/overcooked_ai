import socket
import psycopg2
import keyboard
from datetime import datetime
from threading import Thread
import json

class KeyboardTracker:
    def __init__(self, config_file="db.json", server_host="0.0.0.0", server_port=5002):
        # Load database credentials from JSON file
        with open(config_file, "r") as file:
            self.config = json.load(file)

        self.server_host = server_host
        self.server_port = server_port
        self.current_hash_key = None
        self.running = False

        # Establish database connection
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    # Connect to DB and insert keyboard event
    def insert_keyboard_event(self, key, event_type):
        if not self.current_hash_key:
            return
        try:
            self.cursor.execute(
                """
                INSERT INTO keyboard_events (hash_key, timestamp, key, event_type)
                VALUES (%s, %s, %s, %s)
                """,
                (self.current_hash_key, datetime.now(), key, event_type),
            )
            self.conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")

    # Keyboard listener callback
    def on_key(self, event):
        if self.running:
            self.insert_keyboard_event(event.name, event.event_type)

    def start_listener(self):
        keyboard.hook(self.on_key)
        keyboard.wait()

    # Socket listener for receiving commands
    def socket_listener(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.server_host, self.server_port))
        server.listen(1)
        print(f"Keyboard Tracker listening on {self.server_host}:{self.server_port}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Connection from {addr}")
                while True:
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        break

                    if data.startswith("START"):
                        self.current_hash_key = data.split()[1]
                        self.running = True
                        try:
                            self.cursor.execute("INSERT INTO session (hash_key) VALUES (%s) ON CONFLICT DO NOTHING", (self.current_hash_key,))
                            self.conn.commit()
                        except Exception as e:
                            print(f"DB Error: {e}")
                        print(f"Recording started with key: {self.current_hash_key}")

                    elif data == "STOP":
                        self.running = False
                        self.current_hash_key = None
                        print("Recording stopped.")

    # Start both the socket listener and keyboard listener
    def start_tracking(self):
        # Start socket listener in a separate thread
        Thread(target=self.socket_listener, daemon=True).start()
        # Start keyboard listener
        self.start_listener()

