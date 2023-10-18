import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
import speech_recognition as sr

class SpeechRecognizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Recognizer App")
        self.root.geometry("800x600")

        self.debug_text = None
        self.debug_label = None
        self.device_label = None
        self.device_var = None
        self.device_dropdown = None
        self.transcription_label = None
        self.transcription_text = None
        self.start_stop_button = None
        self.replay_button = None
        self.clear_button = None
        self.quit_button = None
        self.indicator_light = None

        self.setup_debug_gui()

        self.recognizer = sr.Recognizer()
        self.audio_stream = None
        self.audio_devices = self.get_working_audio_devices()
        self.selected_audio_device = None
        self.last_audio_data = None

        self.setup_gui()


    def setup_gui(self):
        self.device_label = ttk.Label(self.root, text="Select Audio Device:")
        self.device_label.pack(pady=10)
        self.device_var = tk.StringVar()
        self.device_dropdown = ttk.Combobox(self.root, textvariable=self.device_var, state="readonly")
        self.device_dropdown['values'] = [f"{dev['name']}" for dev in self.audio_devices]
        self.device_dropdown.pack()
        self.device_dropdown.bind("<<ComboboxSelected>>", self.on_device_selected)

        self.transcription_label = ttk.Label(self.root, text="Transcription:")
        self.transcription_label.pack(pady=10)
        self.transcription_text = tk.Text(self.root, height=5, width=60, state="disabled")
        self.transcription_text.pack()

        self.start_stop_button = ttk.Button(self.root, text="Start Listening", command=self.toggle_listen)
        self.start_stop_button.pack(side="left", padx=10)
        self.replay_button = ttk.Button(self.root, text="Replay Last Audio", command=self.replay_last_audio)
        self.replay_button.pack(side="left", padx=10)
        self.clear_button = ttk.Button(self.root, text="Clear", command=self.clear_transcriptions)
        self.clear_button.pack(side="left", padx=10)
        self.quit_button = ttk.Button(self.root, text="Quit", command=self.quit_app)
        self.quit_button.pack(side="right", padx=10)

        self.indicator_light = tk.Canvas(self.root, width=20, height=20, bg="grey")
        self.indicator_light.pack(side="right", padx=10)

    def setup_debug_gui(self):
        self.debug_label = ttk.Label(self.root, text="Debug:")
        self.debug_label.pack(pady=10)
        self.debug_text = tk.Text(self.root, height=5, width=60, state="disabled")
        self.debug_text.pack()

    def get_working_audio_devices(self):
        working_devices = []
        for dev in sd.query_devices():
            try:
                sd.check_input_settings(device=dev["name"])
                working_devices.append(dev)
            except sd.PortAudioError as e:
                self.log_to_debug(f"Error checking device '{dev['name']}': {str(e)}")
            except Exception as e:
                self.log_to_debug(f"An unexpected error occurred: {str(e)}")
        return working_devices

    def on_device_selected(self, event):
        selected_device_name = self.device_var.get()
        for dev in self.audio_devices:
            if dev["name"] == selected_device_name:
                self.selected_audio_device = dev
                break

    def toggle_listen(self):
        try:
            if self.audio_stream is None:
                self.start_listening()
            else:
                self.stop_listening()
        except Exception as e:
            self.log_to_debug(f"Error toggling listening: {str(e)}")

    def start_listening(self):
        try:
            selected_index = self.device_dropdown.current()
            self.microphone_index = selected_index
            self.audio_stream = sd.InputStream(device=selected_index, callback=self.audio_callback)
            self.audio_stream.start()
            self.start_stop_button.config(text="Stop Listening")
            self.indicator_light.config(bg="green")
        except Exception as e:
            self.log_to_debug(f"Error starting listening: {str(e)}")

    def stop_listening(self):
        try:
            self.start_stop_button.config(text="Start Listening")
            self.indicator_light.config(bg="grey")
            if self.audio_stream is not None:
                self.audio_stream.stop()
        except Exception as e:
            self.log_to_debug(f"Error stopping listening: {str(e)}")

    def audio_callback(self, indata, frames, time, status):
        try:
            if status:
                self.log_to_debug(f"Error in audio callback: {status}")
            if any(indata):
                self.last_audio_data = indata.copy()  # Store the last audio data
                self.transcribe_and_display(indata)
        except Exception as e:
            self.log_to_debug(f"Error processing audio callback: {str(e)}")

    def transcribe_and_display(self, audio_data):
        try:
            transcript = self.recognizer.recognize_google(audio_data)
            self.transcription_text.configure(state="normal")
            self.transcription_text.insert(tk.END, transcript + "\n")
            self.transcription_text.configure(state="disabled")
        except sr.UnknownValueError:
            pass
        except Exception as e:
            self.log_to_debug(f"Error transcribing and displaying: {str(e)}")

    def replay_last_audio(self):
        try:
            if self.last_audio_data is not None:
                sd.play(self.last_audio_data[:, 0], samplerate=self.audio_stream.samplerate)
        except Exception as e:
            self.log_to_debug(f"Error replaying last audio: {str(e)}")

    def log_to_debug(self, message):
        self.debug_text.configure(state="normal")
        self.debug_text.insert(tk.END, message + "\n")
        self.debug_text.configure(state="disabled")

    def clear_transcriptions(self):
        try:
            self.transcription_text.configure(state="normal")
            self.transcription_text.delete("1.0", tk.END)
            self.transcription_text.configure(state="disabled")
        except Exception as e:
            self.log_to_debug(f"Error clearing transcriptions: {str(e)}")

    def quit_app(self):
        try:
            self.root.quit()
        except Exception as e:
            self.log_to_debug(f"Error quitting application: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechRecognizerApp(root)
    root.mainloop()
