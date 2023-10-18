import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import re
from threading import Thread
from play_segment_GUI import AudioSegmentPlayerGUI
from common_classes import SegmentData
import time
"""
from tkinter import messagebox
import sounddevice as sd  # Import sounddevice for audio device management
from vtnLibs.AudioUtils import AudioUtils as AudioU
import pprint
"""


class ViewTranscriptionApp:
    def __init__(self, default_folder=None, header_lines_number=4):
        self.audio_file_path = None
        self.header_lines_number=header_lines_number

        self.root = tk.Tk()
        self.root.title("Audio Player App")
        self.text_area = None
        self.selected_file_content = None
        self.selected_line_idx = None
        self.selected_transcription_line_content = None
        self.selected_segment_info = None
        self.directory_path = default_folder
        self.prev_line = None  # Track previously clicked line

        # Colors
        self.line_hover_bg = "grey"
        self.line_hover_fg = "blue"
        self.line_selected_bg = "lightblue"
        self.line_selected_fg = "red"
        self.line_default_bg = "black"
        self.line_default_fg = "white"

        # Create GUI elements
        self.create_widgets()

        self.audio_player_gui_list = []

        self.root.mainloop()

    def create_widgets(self):
        # Drop-down list to display text files
        self.file_dropdown = ttk.Combobox(self.root, width=40, state='readonly')
        self.file_dropdown.pack(pady=10)
        self.file_dropdown.bind('<<ComboboxSelected>>', self.load_text_file)

        self.audio_file_label = tk.Label(self.root, text=self.audio_file_path or '')
        self.audio_file_label.pack(padx=20, pady=10)

        # Button to select a directory
        self.select_directory_button = tk.Button(self.root, text="Select Directory", command=self.select_directory)
        self.select_directory_button.pack(pady=10)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_app)
        self.quit_button.pack(pady=10)

        # If a default folder is provided, populate the dropdown
        if self.directory_path:
            self.populate_file_dropdown()

        # Play button
        self.play_audio_button = tk.Button(self.root, text="Play segment", command=self.show_audio_player_gui)
        self.play_audio_button.pack(pady=10)


    def select_directory(self):
        # Prompt user to select a directory
        self.directory_path = filedialog.askdirectory(title="Select directory", initialdir=self.directory_path)

        if self.directory_path:
            self.populate_file_dropdown()

    def populate_file_dropdown(self):
        self.file_dropdown['values'] = None
        # Populate the drop-down list with text files in the selected directory
        if os.path.exists(self.directory_path):
            text_files = [f for f in os.listdir(self.directory_path) if f.endswith('.txt')]
            self.file_dropdown['values'] = tuple(os.path.join(self.directory_path, file) for file in text_files)
        else:
            self.directory_path=None
            self.select_directory()

    def load_text_file(self, event):
        selected_file = self.file_dropdown.get()
        if selected_file:
            # Read and display the content of the selected text file
            with open(selected_file, 'r') as file:
                self.selected_file_content = file.read()

            self.display_text_content()
            self.notify_audio_file_found()

    def display_text_content(self):
        audio_file_not_found = True
        if self.text_area:
            self.text_area.destroy()

        # Text area to display content of the selected text file
        self.text_area = tk.Text(self.root, wrap="word", height=20, width=80)
        self.text_area.pack(padx=10, pady=10)

        if self.selected_file_content:
            # Split the content into lines and insert each line as a separate item
            lines = self.selected_file_content.split('\n')
            for i, line in enumerate(lines):
                if (i >= self.header_lines_number):
                    self.insert_line(i, line)
                else:
                    if audio_file_not_found:
                        if (self.extract_audio_file_info(line)):
                            audio_file_not_found = False

    def insert_line(self, line_num, line):
        tag_name = f"line{line_num}"
        self.text_area.insert(tk.END, line + '\n', (tag_name,))

        # Configure the tag to set colors and bind events
        self.text_area.tag_configure(tag_name, foreground=self.line_default_fg)
        self.text_area.tag_bind(tag_name, "<Enter>", lambda event, tag=tag_name: self.on_line_enter(tag))
        self.text_area.tag_bind(tag_name, "<Leave>", lambda event, tag=tag_name: self.on_line_leave(tag))
        self.text_area.tag_bind(tag_name, "<Button-1>", lambda event, tag=tag_name: self.on_line_click(tag))
        self.text_area.tag_bind(tag_name, "<Double-1>", lambda event, tag=tag_name: self.on_line_double_click(tag))

    def on_line_enter(self, tag):
        # print("on_line_enter")
        # self.text_area.tag_configure(tag, background=self.line_hover_bg, foreground=self.line_hover_fg)
        self.__set_hover_colors__(tag)

    def on_line_leave(self, tag):
        # print("on_line_leave")
        # self.text_area.tag_configure(tag, background=self.text_area.cget("bg"), foreground=self.line_default_fg)
        self.__set_normal_colors__(tag)
        self.set_selected_line()

    def __set_tag_colors__(self, tag, bg_color, fg_color):
        self.text_area.tag_configure(tag, background=bg_color, foreground=fg_color)

    def __set_hover_colors__(self, tag):
        self.__set_tag_colors__(tag, self.line_hover_bg, self.line_hover_fg)

    def __set_normal_colors__(self, tag):
        self.__set_tag_colors__(tag, self.line_default_bg, self.line_default_fg)

    def __set_selected_colors__(self, tag):
        self.__set_tag_colors__(tag, self.line_selected_bg, self.line_selected_fg)

    def on_line_click(self, tag):
        print("on_line_click")
        # Unhighlight the previous line if any
        if self.prev_line:
            # self.text_area.tag_configure(self.prev_line, background=self.text_area.cget("bg"),foreground=self.line_default_fg)
            self.__set_normal_colors__(self.prev_line)

        # Highlight the selected line
        # self.text_area.tag_configure(tag, background=self.line_selected_bg, foreground=self.line_selected_fg)
        self.__set_selected_colors__(tag)
        self.prev_line = tag
        self.selected_line_idx, self.selected_transcription_line_content = self.parse_selected_line(tag)

    def on_line_double_click(self, tag):
        print("on_line_double_click")
        self.on_line_click(tag)

        start_timestamp, end_timestamp, transcription_text = self.parse_transcription_line(self.selected_transcription_line_content)
        self.selected_segment_info = SegmentData(audio_file=self.audio_file_path, start_timestamp=start_timestamp, end_timestamp=end_timestamp, text=transcription_text)
        # trans_text = self.selected_segment_info.to_string1()
        d=self.selected_segment_info
        trans_text = s = f"Segment:\n start at: {d.start_timestamp or '':.2f}\n End at: {d.end_timestamp or '':.2f}\n text: {d.text or ''}\n"

        # self.show_selected_line_popup_window(self.selected_line_idx, self.selected_transcription_line_content)
        self.show_selected_line_popup_window(self.selected_line_idx, trans_text)

        self.show_audio_player_gui()


    def run_audio_gui(self):
        print("run_audio_gui")
        # new_audio_GUI_root = tk.Tk()
        audio_GUI_root = tk.Toplevel(self.root)
        audio_player_gui = AudioSegmentPlayerGUI(audio_GUI_root, self.selected_segment_info, self.gui_closed_callback)
        # audio_player_gui.update_audio_gui()
        return audio_GUI_root, audio_player_gui

    def show_audio_player_gui(self):
        print("run_audio_gui")
        if (self.selected_segment_info):
            # Create an instance of the AudioPlayerGUI class and pass the segment data
            audio_GUI_root, audio_player_gui=self.run_audio_gui()
            #audio_player_gui =None
            #Tkinker is not multithread safe
            #gui_thread = self.start_audio_gui_thread(audio_player_gui)
            gui_thread = None
            self.audio_player_gui_list.append((audio_player_gui, gui_thread))
            #new_audio_GUI_root.mainloop()
        else:
            print("self.selected_segment_info is empty !!")


    def start_audio_gui_thread(self, audio_player_gui):
        print("start_audio_gui_thread")
        # Create a separate thread to run the GUI
        # gui_thread = Thread(target=audio_player_gui.run)
        gui_thread = Thread(target=self.run_audio_gui)
        # gui_thread.daemon = True
        gui_thread.start()
        self.audio_player_gui_list.append((audio_player_gui, gui_thread))

    def gui_closed_callback(self, **kwargs):
        print("gui_closed_callback parameters:")
        print(kwargs)
        print("\n\n")
        print("GUI closed or thread finished")

    def __show_popup_window__(self, title, display_text, close_callback_function=None):
        self.popup_window = tk.Toplevel(self.root)
        self.popup_window.wm_title(title)
        label = tk.Label(self.popup_window, text=display_text)
        label.pack(padx=20, pady=20)
        if close_callback_function:
            self.popup_window.protocol("WM_DELETE_WINDOW", close_callback_function)

    def parse_selected_line(self, tag):
        line_num = int(tag.replace("line", ""))
        transcription_line_content = self.selected_file_content.split('\n')[line_num]
        return line_num, transcription_line_content

    def show_selected_line_popup_window(self, line_idx, transcription_line_content):

        self.__show_popup_window__(f"Selected transcription text [{line_idx}", transcription_line_content, self.on_popup_close)
        # messagebox.showinfo("Line Content", line_content)
        # self.popup_window = tk.Toplevel(self.root)
        # self.popup_window.wm_title("Line Content")
        # label = tk.Label(self.popup_window, text=transcription_line_content)
        # label.pack(padx=20, pady=20)
        # self.popup_window.protocol("WM_DELETE_WINDOW", self.on_popup_close)

    def notify_audio_file_found(self):
        self.audio_file_label.config(text=self.audio_file_path or "")
        # if self.audio_file_path:
        #     self.__show_popup_window__("Extracted audio file path", self.audio_file_path, self.on_popup_close)
        # else:
        #     self.__show_popup_window__("Extracted audio file path", "audio file info NOT FOUND!!", self.on_popup_close)

    def on_popup_close(self):
        # print("on_popup_close")
        self.popup_window.destroy()
        self.reset_highlight()

    def set_selected_line(self):
        # print("set_selected_line")
        if self.prev_line:
            self.__set_selected_colors__(self.prev_line)

    def reset_highlight(self):
        # print("reset_highlight")
        # if self.prev_line:
        #     self.text_area.tag_configure(self.prev_line, background=self.text_area.cget("bg"), foreground=self.line_default_fg)
        #     self.prev_line = None
        self.set_selected_line()

    def update_gui(self):
        print(f"update_audio_gui : {time.ctime()}")
        # Update the first GUI periodically
        self.root.after(1000, self.update_gui)


    def quit_app(self):
        self.root.quit()

    def parse_transcription_line(self, transcription_file_line):
        timestamp_regex = r"[\d]{1,}\.[\d]{2}"
        pattern = r"\[("+timestamp_regex+")s -> ("+timestamp_regex+")s\] (.+)"
        match = re.match(pattern, transcription_file_line)

        if match:
            start_timestamp = float(match.group(1))
            end_timestamp = float(match.group(2))
            long_string = match.group(3)
            return start_timestamp, end_timestamp, long_string
        else:
            return None, None, None

    def extract_audio_file_info(self, audio_file_info_line):
        # Extract the audio file information
        audio_file_pattern = r"NFO:\s* - audio file\s*=\s*(['\"])(.+?)\1"
        audio_file_match = re.search(audio_file_pattern, audio_file_info_line)

        self.audio_file_path = None
        if audio_file_match:
            self.audio_file_path = audio_file_match.group(2)
            return True
        return False


class SegmentData:
    def __init__(self, start_timestamp, end_timestamp, audio_file, text=None):
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.audio_file = audio_file
        self.text = text



