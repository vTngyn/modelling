import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from icecream import ic
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC


class Extra(tk.Toplevel):
    lastest_window_id = 0
    def __init__(self):
        super().__init__()
        print('extra window')
        self.lastest_window_id += 1
        self.window_id = self.lastest_window_id
        self.title(f'extra window #{self.window_id}')
        self.geometry('300x400')
        ttk.Label(self, text='A label').pack()
        ttk.Button(self, text='A button').pack()
        ttk.Label(self, text='another label').pack(expand=True)


# https://docs.python.org/3/library/tkinter.messagebox.html
def ask_yes_no():
    answer = messagebox.askquestion('Title', 'Body')
    print(answer)
    messagebox.showerror('Info title', 'Here is some information')


def create_window():
    global extra_window
    extra_window = Extra()


# extra_window = tk.Toplevel()
# extra_window.title('extra window')
# extra_window.geometry('300x400')
# ttk.Label(extra_window, text = 'A label').pack()
# ttk.Button(extra_window, text = 'A button').pack()
# ttk.Label(extra_window, text = 'another label').pack(expand = True)

def close_window():
    extra_window.destroy()


def initialize_gui(presenter):
    # window
    window_manager = tk.Tk()
    window_manager.geometry('600x400')
    window_manager.title('Multiple windows')

    button1 = ttk.Button(window_manager, text='open main window', command=presenter.create_window)
    button1.pack(expand=True)

    button2 = ttk.Button(window_manager, text='close main window', command=presenter.close_window)
    button2.pack(expand=True)

    button3 = ttk.Button(window_manager, text='create yes no window', command=presenter.ask_yes_no)
    button3.pack(expand=True)

    return window_manager

class PresenterMainAppGUI(LEC):
    def __init__(self, view, model):
        self.view=view
        self.model=model
    def run(self):
        self.view.run(self)
def run_gui():
    window_manager = initialize_gui()
    # run
    window_manager.mainloop()


if __name__ == '__init__':
    run_gui()