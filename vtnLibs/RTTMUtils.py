from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC

class RTTMUtils(LEC):
    @staticmethod
    def extract_segment_from_file(rttm_file):
        # Read the RTTM file and extract timing and transcriptions
        transcriptions = []
        with open(rttm_file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            parts = line.strip().split()
            start_time = float(parts[3])
            duration = float(parts[4])
            speaker = parts[7]
            transcriptions.append(SegmentationModel(start_time, start_time + duration, speaker))
        return transcriptions

    # @staticmethod
    # def extractInfoFromRTTMFile():

    def extract_speakers_segments(self):
        # Create a dictionary to store segments for each speaker
        speaker_segments = {speaker: [] for speaker in self.speaker_icons.keys()}

        for i, (_, _, speaker) in enumerate(self.segment_timings):
            if not self.selected_speakers or speaker in self.selected_speakers:
                speaker_segments[speaker].append(f'Segment {i + 1}: {self.segment_timings[i]} seconds')

        return speaker_segments


class SegmentationModel():
    def __init__(self, start_time,  duration, speaker):
        self.start_time=start_time
        self.speaker=speaker
        self.duration=duration
        self.end_time = self.start_time + self.duration
        self.transcription
        self.lang
