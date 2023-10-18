import threading
import time

class AudioProcessor:
    def __init__(self, manager):
        self.manager = manager

    def start(self):
        while not self.manager.shutdown_event.is_set():
            print("Audio processing...")
            time.sleep(2)
            self.manager.update_status("Audio processing completed.")

class GUIUpdater:
    def __init__(self, manager):
        self.manager = manager

    def start(self):
        while not self.manager.shutdown_event.is_set():
            print("Updating GUI...")
            time.sleep(1)
            print("GUI: Status -", self.manager.status)

class ThreadManager:
    def __init__(self):
        self.status = "Idle"
        self.shutdown_event = threading.Event()
        self.audio_threads = []
        self.gui_threads = []

    def update_status(self, status):
        self.status = status

    def start_threads(self, num_audio_threads=1, num_gui_threads=1):
        for i in range(num_audio_threads):
            audio_thread = threading.Thread(target=AudioProcessor(self).start)
            self.audio_threads.append(audio_thread)
            audio_thread.start()

        for i in range(num_gui_threads):
            gui_thread = threading.Thread(target=GUIUpdater(self).start)
            self.gui_threads.append(gui_thread)
            gui_thread.start()

    def stop_threads(self):
        self.shutdown_event.set()
        for audio_thread in self.audio_threads:
            audio_thread.join()

        for gui_thread in self.gui_threads:
            gui_thread.join()

if __name__ == "__main__":
    manager = ThreadManager()
    manager.start_threads(num_audio_threads=2, num_gui_threads=1)

    try:
        time.sleep(10)  # Simulate main program execution
    except KeyboardInterrupt:
        pass

    manager.stop_threads()
