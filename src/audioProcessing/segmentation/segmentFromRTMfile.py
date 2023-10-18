import tkinter as tk
from PIL import Image, ImageTk
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from vtnLibs.RTTMUtils import RTTMUtils as RTTMU
from vtnLibs.AudioUtils import AudioUtils as AudioU
from vtnLibs.image.ImageUtils import ImageUtils as ImgU

class AudioSegmentPlayerGUI(LEC):
    def __init__(self, master, audio_file, rttm_file_path):
        self.master = master
        master.title("Audio Segment Player")

        # Replace with the actual path to your audio file
        self.audio_file_path = 'path/to/your/audio.file'  # Replace with your audio file path

        # Example segment timings (in seconds)
        self.segment_timings = [(0, 5, 'A'), (10, 15, 'B'), (20, 25, 'A')]  # Replace with your segment timings

        # Load speaker icons
        self.speaker_icons = {speaker: tk.PhotoImage(file=f'speaker_{speaker}.png') for speaker in ['A', 'B']}
        self.speaker_labels = ['A', 'B']  # Replace with the actual speaker labels

        self.create_widgets()
        self.update_listbox()

        self.audio_file=audio_file
        self.rttm_file_path=rttm_file_path
        self.speakers = []
        self.speakersIcons = []
        self.transcriptions = self.extract_transcription()

        self.spearkerMan = SpearkerManager()
    def generate_label_images(self):
        label_images = {}
        labels = self.speakers
        labelExtraHeight = 30
        resizeFactor = 1
        iconHeight = 45
        iconWidth = 30

        for speakerLabel in labels:
            # Load the image file corresponding to the label
            img = Image.open(f'{speakerLabel}_image.png')  # Replace with the actual image file path

            # Resize the image to a specific width (adjust as needed)
            width, height = img.size
            # ratio, new_width, new_height = self.getMinResizeScale(width, height, iconWidth, iconHeight)   # Adjust this value based on your requirement
            ratio, new_width, new_height = ImgU.getMinResizeScale(width, height, new_width, new_height)   # Adjust this value based on your requirement
            # new_height = int(height + labelExtraHeight)
            # new_height = int((new_width / width) * height)
            img = img.resize((new_width, new_height))

            # # Create a transparent image with a label
            # transparent_label_img = Image.new('RGBA', (new_width, new_height+labelExtraHeight), (255, 255, 255, 0))
            # transparent_label_draw = ImageDraw.Draw(transparent_label_img)
            # transparent_label_draw.text((new_width, labelExtraHeight), f'Speaker {label}', fill=(255, 255, 255, 255))
            transparent_label_img = ImgU.createTransparentImg(speakerLabel, labelExtraHeight, new_width, new_height, fill=(255, 255, 255, 255), color=(255, 255, 255, 0))

            # Combine the original image with the label
            combined_img = Image.alpha_composite(Image.alpha_composite(Image.new('RGBA', transparent_label_img.size), img.convert('RGBA')), transparent_label_img)

            label_images[speakerLabel] = ImageTk.PhotoImage(combined_img)

        return label_images
    def extract_speakers_segments(self):
        # Create a dictionary to store segments for each speaker
        speaker_segments = {speaker: [] for speaker in self.speaker_icons.keys()}

        for i, (_, _, speaker) in enumerate(self.segment_timings):
            if not self.selected_speakers or speaker in self.selected_speakers:
                speaker_segments[speaker].append(f'Segment {i+1}: {self.segment_timings[i]} seconds')

        return speaker_segments


    def create_widgets(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        # Checkbox for all speakers
        self.all_speakers_checkbox = tk.Checkbutton(self.master, text="All Speakers", command=self.filter_segments)
        self.all_speakers_checkbox.pack(pady=5)

        # Checkboxes for individual speakers
        self.speaker_var = [tk.IntVar() for _ in range(len(self.speaker_labels))]
        self.speaker_checkboxes = []
        for i, speaker in enumerate(self.speaker_labels):
            self.speaker_checkboxes.append(
                tk.Checkbutton(self.master, text=f"Speaker {speaker}", variable=self.speaker_var[i],
                               command=self.filter_segments))
            self.speaker_checkboxes[i].pack(anchor=tk.W, padx=10)

        self.listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, padx=10)

        self.play_button = tk.Button(self.frame, text="Play Segment", command=self.play_segment)
        self.play_button.pack(side=tk.RIGHT, padx=10)

    def play_audio_segment(self, start_time, end_time):
        audio_segment = AudioU.extract_audio_segment(audio_file, start_time, end_time)
        AudioU.play_audio_segment(audio_segment)


    def addSpeakerToList(self, speaker, name, label, status, img):
        speakerElement = {"name":name, "label":label, "status":status, "img":img}
        self.speakers.append(speakerElement)

    def extract_transcription(self):
        transcriptions = RTTMU.extract_segment_from_file(rttm_file=self.rttm_file_path)
        return transcriptions


    # Transcribe each speaker's segments
    def playAllAudioSegment(self):
        for start_time, end_time, speaker in self.transcriptions:
            # Extract audio segment corresponding to the identified timings

            # Print the transcription and corresponding audio segment
            print(f'Transcription for Speaker {speaker}:')
            # print(f'Audio Segment: {audio_segment}')
            print('\n')
            self.play_audio_segment(start_time, end_time)

    # def play_audio_segment(self, start_time, end_time):
    #     """
    #     Play an audio segment using pydub's playback functionality.
    #     """
    #     # Load the original audio file
    #     audio = AudioSegment.from_file(audio_file)
    #
    #     # Extract the specified segment
    #     segment = audio[start_time * 1000:end_time * 1000]
    #
    #     # Play the audio segment
    #     play(segment)

    # def extract_transcription(self,rttm_file):
    #     # Read the RTTM file and extract timing and transcriptions
    #     transcriptions = []
    #     with open(rttm_file, 'r') as file:
    #         lines = file.readlines()
    #
    #     for line in lines:
    #         parts = line.strip().split()
    #         start_time = float(parts[3])
    #         duration = float(parts[4])
    #         speaker = parts[7]
    #         transcriptions.append((start_time, start_time + duration, speaker))
    #
    #     return transcriptions

    # Replace with the path to your RTTM file
    rttm_file_path = '../../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.run2.NbrSpeakerGiven.rttm'
    audio_file = "../../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.wav"

    def play_segment(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            start_time, end_time, _ = self.segment_timings[selected_index[0]]
            self.play_audio_segment(start_time, end_time)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, (start, end, speaker) in enumerate(self.segment_timings):
            if not self.selected_speakers or speaker in self.selected_speakers:
                self.listbox.insert(tk.END, f'Segment {i + 1} ({speaker}): {start} to {end} seconds')

        self.display_images()

    def filter_segments(self):
        self.selected_speakers = []
        for i in range(len(self.speaker_checkboxes)):
            if self.speaker_var[i].get() == 1:
                self.selected_speakers.append(self.speaker_labels[i])
        self.update_listbox()

    def display_images(self):
        # Clear previous images
        for widget in self.image_label_frame.winfo_children():
            widget.destroy()

        # Display images for each segment
        for speaker in self.speaker_icons.keys():
            label = tk.Label(self.image_label_frame, image=self.speaker_icons[speaker])
            label.pack(pady=5)

SPEAKER_STATUS_IDENTIFIED=1
SPEAKER_STATUS_NEW=0

class SpearkerManager(LEC):
    def __init__(self):
        self.speakers = []

    def addNewSPeaker(self,  id, name, rttmLabel, status=SPEAKER_STATUS_NEW):
        speaker = SpearkerModel( id, name, rttmLabel, status)
        self.speakers.append({"label":rttmLabel, "modle":speaker})

class SpearkerModel():
    def __init__(self, id, name, rttmLabel, status):
        self.id=id
        self.name=name
        self.rttmLabel=rttmLabel
        self.status=status
        self.imgFile=None
        self.voiceSignatureFile=None
        self.metadataFilename=None
        self.icon=None


if __name__ == "__main__":
    # Replace with the path to your RTTM file
    rttm_file_path = '../../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.run2.NbrSpeakerGiven.rttm'
    audio_file = "../../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.wav"

    root = tk.Tk()
    app = AudioSegmentPlayerGUI(root, audio_file, rttm_file_path)
    root.mainloop()
