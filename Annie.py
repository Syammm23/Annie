import speech_recognition as sr
import pyttsx3
import os
import datetime
import webbrowser
import pyautogui
import ollama # For smart answers
import cv2 # For camera vision
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

# --- Annie's Voice Setup ---
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 1 for Female voice
engine.setProperty('rate', 170)

def speak(audio):
    print(f"Annie: {audio}")
    engine.say(audio)
    engine.runAndWait()

# --- Annie's Ears ---
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        app_gui.update_status("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        app_gui.update_status("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        app_gui.update_status(f"You: {query}")
    except Exception:
        app_gui.update_status("Sorry, I didn't get that.")
        return "None"
    return query.lower()

# --- Annie's Brain (Ollama Integration) ---
def get_ollama_response(user_input, user_name="Shyam"): # Changed to Shyam
    response = ollama.chat(model='llama3', messages=[
        {'role': 'system', 'content': f'You are Annie, a friendly AI companion. You are my best friend. Talk casually, use humor, and keep your replies short and fun. Always call me {user_name}.'},
        {'role': 'user', 'content': user_input},
    ])
    return response['message']['content']

# --- Annie's Eyes (Camera) ---
class CameraFeed:
    def __init__(self):
        self.vid = cv2.VideoCapture(0) # 0 for default webcam
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        if not self.vid.isOpened():
            speak("Error: Could not open webcam.")
            return

    def get_frame(self):
        ret, frame = self.vid.read()
        if ret:
            return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# --- Annie's GUI (Graphical User Interface) ---
class AnnieGUI:
    def __init__(self, master):
        self.master = master
        master.title("Annie AI")
        master.geometry("800x600")
        master.resizable(False, False)
        master.configure(bg="#2c3e50") # Dark blue background

        # --- Camera Frame ---
        self.camera_frame = tk.Frame(master, bg="black", width=320, height=240)
        self.camera_frame.pack(pady=10)
        self.camera_label = tk.Label(self.camera_frame, bg="black")
        self.camera_label.pack()

        # --- Status Label ---
        self.status_label = tk.Label(master, text="Click to activate Annie!", font=("Arial", 14), fg="white", bg="#2c3e50")
        self.status_label.pack(pady=5)

        # --- Annie's Circle (Clickable) ---
        self.canvas_size = 200
        self.canvas = tk.Canvas(master, width=self.canvas_size, height=self.canvas_size, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.annie_circle = self.canvas.create_oval(10, 10, self.canvas_size-10, self.canvas_size-10, outline="#e74c3c", width=4, fill="#c0392b") # Red circle
        self.canvas.create_text(self.canvas_size/2, self.canvas_size/2, text="ANNIE", font=("Arial", 24, "bold"), fill="white")
        self.canvas.bind("<Button-1>", self.activate_annie) # Click event

        # --- Conversation Log ---
        self.log_frame = tk.Frame(master, bg="#34495e")
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.log_text = tk.Text(self.log_frame, bg="#34495e", fg="white", font=("Arial", 12), wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.camera = CameraFeed()
        self.update_camera_feed()
        self.is_active = False
        self.audio_wave_level = 0
        self.animate_audio_wave()

    def update_status(self, message):
        self.status_label.config(text=message)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_camera_feed(self):
        ret, frame = self.camera.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_label.config(image=self.photo)
        self.master.after(10, self.update_camera_feed) # Update every 10ms

    def animate_audio_wave(self):
        self.canvas.delete("wave") # Clear previous waves
        if self.is_active:
            # Simple audio wave visualization (can be improved with actual audio input)
            wave_width = self.audio_wave_level * 0.8
            self.canvas.create_oval(
                self.canvas_size/2 - wave_width, self.canvas_size/2 - wave_width,
                self.canvas_size/2 + wave_width, self.canvas_size/2 + wave_width,
                outline="#f1c40f", width=3, tags="wave"
            )
            self.audio_wave_level = (self.audio_wave_level + 5) % (self.canvas_size/2 - 15) # Animate
        
        self.master.after(50, self.animate_audio_wave) # Update wave every 50ms

    def activate_annie(self, event=None):
        if not self.is_active:
            self.is_active = True
            self.update_status("Annie is active!")
            speak("Hello Shyam! How can I assist you today?") # Greet Shyam
            threading.Thread(target=self.annie_main_loop, daemon=True).start()
            self.canvas.itemconfig(self.annie_circle, fill="#2ecc71", outline="#27ae60") # Green when active
        else:
            self.is_active = False
            self.update_status("Annie is going to sleep.")
            speak("Okay, Shyam. Call me when you need me.")
            self.canvas.itemconfig(self.annie_circle, fill="#c0392b", outline="#e74c3c") # Red when inactive

    def annie_main_loop(self):
        while self.is_active:
            query = takeCommand()
            if query == "None":
                continue

            # Command execution logic (Similar to previous, but integrated with GUI)
            if 'open notepad' in query:
                speak("Opening Notepad for you, Shyam.")
                os.system("notepad.exe")
            elif 'open chrome' in query:
                speak("Opening Google Chrome for you, Shyam.")
                os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe") 
            elif 'the time' in query:
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                speak(f"Shyam, the time is {strTime}")
            elif 'open youtube' in query:
                speak("Opening YouTube, enjoy your videos Shyam!")
                webbrowser.open("youtube.com")
            elif 'how are you' in query:
                speak(get_ollama_response(query, "Shyam")) # Use Ollama for friendly chat
            elif 'tell me about' in query:
                topic = query.replace("tell me about", "").strip()
                # Here you could integrate a Wikipedia API or Ollama for facts
                speak(f"Looking up information about {topic}, Shyam.")
                speak(get_ollama_response(f"Tell me a short fact about {topic}", "Shyam")) # Use Ollama for facts
            elif 'exit' in query or 'bye' in query or 'go to sleep' in query:
                self.activate_annie() # Deactivate Annie
                break
            else:
                speak(get_ollama_response(query, "Shyam")) # Default to Ollama for any other query

# --- Main Application Start ---
if __name__ == "__main__":
    root = tk.Tk()
    app_gui = AnnieGUI(root)
    root.mainloop()