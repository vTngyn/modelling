import threading
import time
import tkinter as tk
from tkinter import ttk

class ProcessorThread:
    def __init__(self, manager, name):
        self.manager = manager
        self.name = name

    def start(self):
        while not self.manager.shutdown_event.is_set():
            print(f"Processing on thread '{self.name}'...")
            time.sleep(2)
            self.manager.update_status(f"Processing completed on thread '{self.name}'.")
            self.manager.update_running_threads()

class GUIUpdater:
    def __init__(self, manager, name):
        self.manager = manager
        self.name = name

    def start(self):
        while not self.manager.shutdown_event.is_set():
            print(f"Updating GUI for thread '{self.name}'...")
            time.sleep(1)
            self.manager.update_running_threads()

class ThreadManager:
    def __init__(self, root):
        self.status = "Idle"
        self.shutdown_event = threading.Event()
        self.processor_threads = []
        self.gui_threads = []
        self.root = root

    def update_status(self, status):
        self.status = status

    def update_running_threads(self):
        threads_listbox.delete(0, tk.END)
        for name, _ in self.processor_threads + self.gui_threads:
            threads_listbox.insert(tk.END, f"{name}: {str(_)[:30]}...")

    def start_processor_threads(self, num_threads=1):
        for i in range(num_threads):
            thread_name = f"ProcessorThread-{i}"
            processor_thread = threading.Thread(target=ProcessorThread(self, thread_name).start)
            self.processor_threads.append((thread_name, processor_thread))
            processor_thread.start()
        self.update_running_threads()

    def start_gui_threads(self, num_threads=1):
        for i in range(num_threads):
            thread_name = f"GUIThread-{i}"
            gui_thread = threading.Thread(target=GUIUpdater(self, thread_name).start)
            self.gui_threads.append((thread_name, gui_thread))
            gui_thread.start()
        self.update_running_threads()

    def stop_threads(self):
        self.shutdown_event.set()
        for _, thread in self.processor_threads + self.gui_threads:
            thread.join()

    def stop_all_threads(self):
        self.stop_threads()

    def stop_selected_thread(self):
        selected_item = threads_listbox.curselection()
        if selected_item:
            thread_index = selected_item[0]
            thread_name, thread = threads_listbox.get(thread_index).split(": ")
            for name, t in self.processor_threads + self.gui_threads:
                if name == thread_name:
                    t.join()
                    break
            self.update_running_threads()

    def launch_job(self):
        job_name = job_function_entry.get()
        if job_name:
            print(f"Launching job: {job_name}")

    def create_gui(self):
        start_threads_button = tk.Button(self.root, text="Start Threads", command=self.start_processor_threads)
        start_threads_button.pack(pady=10)

        stop_all_threads_button = tk.Button(self.root, text="Stop All Threads", command=self.stop_all_threads)
        stop_all_threads_button.pack(pady=10)

        stop_selected_thread_button = tk.Button(self.root, text="Stop Selected Thread", command=self.stop_selected_thread)
        stop_selected_thread_button.pack(pady=10)

        job_function_label = tk.Label(self.root, text="Job Function:")
        job_function_label.pack(pady=5)

        global job_function_entry
        job_function_entry = tk.Entry(self.root, width=30)
        job_function_entry.pack(pady=5)

        launch_job_button = tk.Button(self.root, text="Launch Job", command=self.launch_job)
        launch_job_button.pack(pady=10)

        threads_frame = ttk.LabelFrame(self.root, text="Threads")
        threads_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        global threads_listbox
        threads_listbox = tk.Listbox(threads_frame, selectmode=tk.SINGLE, width=40)
        threads_listbox.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Thread Manager")

    manager = ThreadManager(root)

    gui_thread = threading.Thread(target=manager.create_gui)
    gui_thread.start()

    manager.start()

    # Uncomment this line to start the manager's GUI in the main thread
    # manager.create_gui()
