class SegmentData:
    def __init__(self, audio_file: str, start_timestamp, end_timestamp, text: str):
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.text = text
        self.audio_file = audio_file

    def to_string1(self):
        s = f"Segment:\n start at: {self.start_timestamp or '':.2f}\n End at: {self.end_timestamp or '':.2f}\n text: {self.text or ''}\n"
        return s
