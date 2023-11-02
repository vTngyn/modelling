import re
from typing import List

class SpeechSpeaker:
    max_id = 0
    def __init__(self, first_name, last_name):
        SpeechSpeaker.max_id += 1
        self.id = SpeechSpeaker.max_id - 1
        self.first_name = None
        self.last_name = None

    def to_string(self):
        try:
            s = f"[{(self.id or '')}#{(self.last_name or '')}, {(self.first_name or '')}]"
            return s
        except Exception as e:
            print(e)
        return None

class TranscriptSegmentData:
    def __init__(self, audio_file: str):
        self.start_timestamp = None
        self.end_timestamp = None
        self.text: str = None
        self.audio_file: str = audio_file
        self.speakers: List = []

    def initialize_from_transcription_line(self, transcription_line):
        self.start_timestamp, self.end_timestamp, self.text = TranscriptSegmentData.parse_transcription_line(transcription_line)


    def initialize_with_splitted_elements(self, start_timestamp, end_timestamp, text: str):
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.text = text

    def to_string(self):
        try:
            s = f"Segment:\n start at: {(self.start_timestamp or ''):6.2f}\n End at: {(self.end_timestamp or ''):6.2f}\n text: {(self.text or '')}\n"
            return s
        except Exception as e:
            print(e)
            print(self.text)
            print(self.start_timestamp)
            print(self.end_timestamp)
        return None

    def pretty_transcription_line(self):
        try:
            sp = ''
            for p in self.speakers:
                sp += p.to_string()
            display_str = f"[{self.start_timestamp or '':8.2f}] - [{self.end_timestamp or '':8.2f}]:{self.text or ''} [{sp}]"
            return display_str
        except Exception as e:
            print(e)
            print(self.text)
            print(self.start_timestamp)
            print(self.end_timestamp)
        return None

    def add_speaker(self, speaker: SpeechSpeaker):
        if speaker:
            self.speakers.append(speaker)

    def add_speakers(self, speakers: List[SpeechSpeaker]):
        if speakers and len(speakers)>0:
            for speaker in speakers:
                self.add_speaker(speaker)

    @staticmethod
    def parse_transcription_line( transcription_file_line):
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
