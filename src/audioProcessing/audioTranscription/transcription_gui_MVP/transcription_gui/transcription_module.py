import re

from src.audioProcessing.audioTranscription.transcription_gui_MVP.common_classes import AbstractSegmentData


class TranscriptSegmentData(AbstractSegmentData):
    timestamp_regex = r"[\d]{1,}\.[\d]{2}"
    pattern = r"\[(" + timestamp_regex + ")s -> (" + timestamp_regex + ")s\] (.+)"

    def __init__(self, audio_file: str):
        super.__init__(audio_file)

    def __parse_raw_text_line__(self, raw_text_line):
        match = re.match(self.pattern, raw_text_line)

        if match:
            start_timestamp = float(match.group(1))
            end_timestamp = float(match.group(2))
            long_string = match.group(3)
            return start_timestamp, end_timestamp, long_string
        else:
            return None, None, None
