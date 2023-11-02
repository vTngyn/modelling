from typing import List, Tuple
from vtnLibs.common_utils.CodingUtils import StringUtils as strU
from abc import ABC, abstractmethod

class SpeechSpeaker:
    max_id = 0
    false_equality_if_homonym = False
    def __init__(self, first_name: str, last_name: str):
        SpeechSpeaker.max_id += 1
        self.id = SpeechSpeaker.max_id - 1
        self.first_name = first_name
        self.last_name = last_name
        self.speaker_key = self.__get_key_field__(first_name, last_name)

    def __get_key_field__(self, firstname: str, lastname: str):
        first_name = firstname
        if not firstname:
            first_name = ""
        last_name = lastname
        if not lastname:
            last_name = ""
        self.speaker_key = strU.substitute_characters_regex(first_name.strip().lower()) + ', ' + strU.substitute_characters_regex(last_name.strip().lower()).upper()

    def to_string(self):
        try:
            s = f"[{(self.id or '')}#{(self.last_name or '')}, {(self.first_name or '')}]"
            return s
        except Exception as e:
            print(e)
        return None

    def speaker_eq_by_id(self, id):
        if self.id == id:
            return True
        return False

    def speaker_eq_by_names(self, firstname:str, lastname:str):
        speaker_key = self.__get_key_field__(firstname, lastname)
        if self.speaker_key == speaker_key:
            return True
        return False

    def __eq__(self, other: 'SpeechSpeaker') -> bool:
        if not other:
            return False
        if self.speaker_eq_by_id(other.id):
            return True
        if self.false_equality_if_homonym:
            return False
        if self.speaker_eq_by_names(other.first_name, other.last_name):
            return True
        return False
class AbstractSegmentData(ABC):
    def __init__(self, audio_file: str):
        self.start_timestamp = None
        self.end_timestamp = None
        self.text: str = None
        self.audio_file: str = audio_file
        self.speakers: List[SpeechSpeaker] = []
    @abstractmethod
    def __parse_raw_text_line__(self, raw_text_line) -> Tuple[float, float, str]:
        pass


    def initialize_with_splitted_elements(self, start_timestamp, end_timestamp, text: str):
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.text = text

    def is_covering_same_interval(self, other_segment: 'AbstractSegmentData'):
        if self.start_timestamp == other_segment.start_timestamp:
            if self.end_timestamp == other_segment.end_timestamp:
                return True
        return False

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

    def initialize_from_raw_text_line(self, raw_text_line):
        self.start_timestamp, self.end_timestamp, self.text = self.__parse_raw_text_line__(raw_text_line)

