import threading
import time
import tkinter as tk
from tkinter import ttk
from queue import Queue

class ProcessorThread:
    def __init__(self, manager, name):
        self.manager = manager
        self.name = name
        self._stop_event = threading.Event()

        self.iterationNbr = 0


    def start(self):
        while not self.manager.shutdown_event.is_set() and not self._stop_event.is_set():
            print(f"Processing on thread '{self.name}'...")
            time.sleep(5)
            self.manager.update_status(f"Processing completed on thread '{self.name}'.")
            self.manager.update_running_threads()
            message = f"{self.name} - Processing task {self.iterationNbr}"
            self.manager.push_messages(message)
            self.iterationNbr += 1

    def stop(self):
        print(f"Notifying GUI :Stopping on thread '{self.name}'...")
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class GUIUpdater:
    def __init__(self, manager, name):
        self.manager = manager
        self.name = name
        self._stop_event = threading.Event()

    def start(self):
        while not self.manager.shutdown_event.is_set() and not self._stop_event.is_set():
            print(f"Updating GUI for thread '{self.name}'...")
            time.sleep(2)
            # Send a message to the GUI
            message = f"{self.name} - Processing complete"
            self.manager.push_messages(message)

            # self.manager.update_running_threads()


    def stop(self):
        print(f"Updating GUI : Stopping on thread '{self.name}'...")
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def set_context_menu(self, context_menu):
        self.context_menu = context_menu

    def on_right_click(self, event):
        self.context_menu.post(event.x_root, event.y_root)

class ThreadManager:
    def __init__(self):
        self.status = "Idle"
        self.shutdown_event = threading.Event()
        self.processor_threads = []
        self.gui_threads = []
        self.threadNextIdx =0
        self.registerManagerThread = None

        self.refresh_paused = False

        self.root = tk.Tk()
        self.message_queue = Queue()



    def start(self):
        # Start the tkinter main loop in the main thread
        self.gui_thread = threading.Thread(target=self.create_gui)
        self.gui_thread.start()

        self.root.mainloop()

    def push_messages(self, message):
        self.message_queue.put(message)
    def display_messages(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self.threads_listbox.insert(tk.END, message)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Stop Thread", command=self.stop_selected_thread)

    def on_listbox_right_click(self, event):
        self.create_context_menu()
        self.context_menu.post(event.x_root, event.y_root)

    def update_status(self, status):
        self.status = status

    def on_listbox_enter(self, event):
        self.refresh_paused = True

    def on_listbox_leave(self, event):
        self.refresh_paused = False

    def update_running_threads(self):
        if not self.refresh_paused:
            self.threads_listbox.delete(0, tk.END)
            for name, instance , thread in self.processor_threads + self.gui_threads:
                self.threads_listbox.insert(tk.END, f"{name}: {str(_)[:30]}...")
                instance.display_messages()

    def getNextThreadIndex(self):
        self.threadNextIdx += 1
        return  self.threadNextIdx

    def start_processor_threads(self, num_threads=1):
        for i in range(num_threads):
            idx = self.getNextThreadIndex()
            thread_name = f"ProcessorThread-{idx}"
            instance = GUIUpdater(self, thread_name)
            processor_thread = threading.Thread(target=instance.start)
            self.processor_threads.append((thread_name, instance, processor_thread))
            processor_thread.start()
        self.update_running_threads()

    def start_gui_threads(self, num_threads=1):
        for i in range(num_threads):
            idx = self.getNextThreadIndex()
            thread_name = f"GUIThread-{idx}"
            instance = GUIUpdater(self, thread_name)
            gui_thread = threading.Thread(target=instance.start)
            self.gui_threads.append((thread_name, instance, gui_thread))
            gui_thread.start()
        self.update_running_threads()

    def stop_threads(self):
        self.shutdown_event.set()
        for name, instance, thread in self.processor_threads + self.gui_threads:
            thread.join()

    def stop_all_threads(self):
        self.stop_threads()

    def stop_selected_thread(self):
        selected_item = self.threads_listbox.curselection()
        if selected_item:
            thread_index = int(selected_item[0])  # Extract the selected index
            print(thread_index)
            thread_name, _ = self.threads_listbox.get(thread_index).split(": ")
            for idx, (processor_thread_name, processor_thread, thread) in enumerate(self.processor_threads):
                if processor_thread_name == thread_name:
                    processor_thread.stop()
                    self.processor_threads.pop(idx)
                    break
            for idx, (gui_thread_name, gui_thread, thread) in enumerate(self.gui_threads):
                if gui_thread_name == thread_name:
                    gui_thread.stop()
                    self.gui_threads.pop(idx)
                    break
            self.update_running_threads()
    def launch_job(self):
        job_name = self.job_function_entry.get()
        if job_name:
            print(f"Launching job: {job_name}")

    def create_gui(self):

        self.root.title("Thread Manager")
        self.root.geometry("400x600")

        self.start_threads_button = tk.Button(self.root, text="Start Threads", command=self.start_processor_threads)
        self.start_threads_button.pack(pady=10)

        self.stop_all_threads_button = tk.Button(self.root, text="Stop All Threads", command=self.stop_all_threads)
        self.stop_all_threads_button.pack(pady=10)


        self.stop_selected_thread_button = tk.Button(self.root, text="Stop Selected Thread", command=self.stop_selected_thread)
        self.stop_selected_thread_button.pack(pady=10)

        self.job_function_label = tk.Label(self.root, text="Job Function:")
        self.job_function_label.pack(pady=5)

        # global job_function_entry
        self.job_function_entry = tk.Entry(self.root, width=30)
        self.job_function_entry.pack(pady=5)

        self.launch_job_button = tk.Button(self.root, text="Launch Job", command=self.launch_job)
        self.launch_job_button.pack(pady=10)

        self.threads_frame = ttk.LabelFrame(self.root, text="Threads")
        self.threads_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # global threads_listbox
        self.threads_listbox = tk.Listbox(self.threads_frame, selectmode=tk.SINGLE, width=40)
        self.threads_listbox.pack(pady=10)

       # Create a listbox to display the threads
       #  self.threads_listbox = tk.Listbox(self.root)
       #  self.threads_listbox.pack(expand=True, fill='both')

        # Set up a context menu for the listbox
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Stop Thread", command=self.stop_selected_thread)

        # Bind right-click event to show the context menu
        self.threads_listbox.bind("<Button-3>", self.on_listbox_right_click)

    def registerManagerThread(self, tManThread):
        self.registerManagerThread=tManThread

if __name__ == "__main__":
    manager = ThreadManager()
    manager.start()
    tManThread = threading.Thread(target=manager.update_running_threads())
    tManThread.daemon = True
    manager.registerManagerThread(tManThread)

    # manager.start()
    tManThread.join()
    print("Thread Manager is completed.")
