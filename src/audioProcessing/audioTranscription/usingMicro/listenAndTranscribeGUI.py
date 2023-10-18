import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import speech_recognition as sr
import numpy as np
from collections import deque


class SpeechRecognizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Recognizer App")
        self.root.geometry("800x600")

        # Initialize speech recognizer and microphone index
        self.recognizer = sr.Recognizer()
        self.microphone_index = None

        # Circular buffer for audio spectrum display
        self.buffer_size = 2000  # 20 seconds at 100 Hz (adjust according to your requirements)
        self.audio_spectrum_buffer = deque(maxlen=self.buffer_size)

        # GUI elements
        self.setup_gui()

    def setup_gui(self):
        # Microphone selection dropdown
        self.microphone_label = ttk.Label(self.root, text="Select Microphone:")
        self.microphone_label.pack(pady=10)
        self.microphone_var = tk.StringVar()
        self.microphone_dropdown = ttk.Combobox(self.root, textvariable=self.microphone_var, state="readonly")
        self.microphone_dropdown.pack()
        self.update_microphone_list()

        # Audio spectrum plot
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(0, self.buffer_size)  # Display 20 seconds of audio
        self.ax.set_ylim(-100, 100)
        self.line, = self.ax.plot([], [])
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Transcribed text box
        self.transcribed_text = tk.Text(self.root, height=10, width=80)
        self.transcribed_text.pack(pady=10)

        # Buttons
        self.start_stop_button = ttk.Button(self.root, text="Start Listening", command=self.toggle_listen)
        self.start_stop_button.pack(side="left", padx=10)
        self.clear_button = ttk.Button(self.root, text="Clear", command=self.clear_transcriptions)
        self.clear_button.pack(side="left", padx=10)
        self.quit_button = ttk.Button(self.root, text="Quit", command=self.quit_app)
        self.quit_button.pack(side="right", padx=10)

    def update_microphone_list(self):
        self.microphone_info = sr.Microphone.list_microphone_names()
        self.microphone_var.set("")  # Clear any previous selection
        self.microphone_dropdown['values'] = [
            f"{index}: {name}" for index, name in enumerate(self.microphone_info)
        ]

    def toggle_listen(self):
        if self.start_stop_button["text"] == "Start Listening":
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        try:
            selected_index = int(self.microphone_var.get().split(":")[0])
            self.microphone_index = selected_index
            self.audio_stream = sr.Microphone(device_index=selected_index)
            self.start_stop_button.config(text="Stop Listening")
            self.listen()
        except ValueError:
            print("Invalid microphone selection. Please select a valid microphone.")

    def stop_listening(self):
        self.start_stop_button.config(text="Start Listening")
        if hasattr(self, 'audio_stream'):
            try:
                self.audio_stream.stop_stream()
            except:
                None
            self.audio_stream = None


    def listen(self):
        self.line, = self.ax.plot([], [])
        self.ax.set_xlim(0, 2000)
        self.ax.set_ylim(-100, 100)
        self.root.after(0, self.animate)
        self.root.mainloop()

    def animate(self):
        if self.audio_stream is None:
            return

        with self.audio_stream as source:
            try:
                audio_data = self.recognizer.listen(source, timeout=0.1)
                self.transcribe_and_display(audio_data)
            except sr.WaitTimeoutError:
                pass

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.root.after(100, self.animate)

    def transcribe_and_display(self, audio_data):
        try:
            transcript = self.recognizer.recognize_google(audio_data)
            self.transcribed_text.insert(tk.END, transcript + "\n")
            # Update the audio spectrum
            audio_spectrum = np.random.randint(-100, 100, 1000)  # Replace with actual audio spectrum data
            self.update_spectrum(audio_spectrum)
        except sr.UnknownValueError:
            pass

    def update_spectrum(self, audio_spectrum):
        self.audio_spectrum_buffer.extend(audio_spectrum)
        start_idx = max(0, len(self.audio_spectrum_buffer) - self.buffer_size)
        end_idx = len(self.audio_spectrum_buffer)
        self.line.set_xdata(np.arange(end_idx - start_idx))
        self.line.set_ydata(list(self.audio_spectrum_buffer)[start_idx:end_idx])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.canvas.flush_events()

    def clear_transcriptions(self):
        self.transcribed_text.delete("1.0", tk.END)

    def quit_app(self):
        try:
            self.stop_listening()
        except:
            None
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechRecognizerApp(root)
    root.mainloop()
