from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from vtnLibs.AudioFileUtils import AudioFileUtils as AudFU
from typing import List
from vtnLibs.common_utils.FileFolderOperationsUtils import FileFOlderOpsUtils as ffU
from ..common_classes import AbstractSegmentData, SpeechSpeaker
import os, re
class SpeakerDiarizationPyAnnoteModule(LEC):
    def __init__(self, diarization_file_path, audio_file_path=None):
        self.diarization_file_path: str=diarization_file_path
        self.audio_file_path: str=audio_file_path
        self.last_diariz_file_line_index_ptr: int=0
        self.file_content: List[PyAnnoteDiarizSegmentData] = []
        self.speaker_list: List[SpeechSpeaker]= []

    def __load_diar_file_content__(self) -> List[str]:
        lines=[]
        if self.diarization_file_path and ffU.is_existing_file(self.diarization_file_path):
            last_diarization_idx_line = 0
            with open(self.diarization_file_path, mode= os.O_RDONLY , ) as file:
                lines = file.readlines()
        return lines

    def __add_speakers_to_unique_list__(self, speakers: List[SpeechSpeaker]):
        if speakers and len(speakers)>0:
            for ss in speakers:
                if ss not in self.speaker_list:
                    self.speaker_list.append(ss)

    def get_segmentdata_from_diariz_line(self, audio_file_path, diariz_line) -> tuple[PyAnnoteDiarizSegmentData, int]:
        segData = PyAnnoteDiarizSegmentData(audio_file_path)
        segData.initialize_from_raw_text_line(diariz_line)
        new_diarization_idx_line=None
        previous_segmentdata = None

        speakers,  new_diarization_idx_line = self.find_speakers_in_diarizationRTTM(segData=segData, last_diarization_idx_line=last_diarization_idx_line)

        segData.add_speakers(speakers=speakers)

        return segData, new_diarization_idx_line

    def __load_speaker_list_from_file__(self):
        lines=self.__load_diar_file_content__()
        if lines and len(lines) > 0:
            lines = lines.split('\n')
            for i, line in enumerate(lines):
                if (i >= self.header_lines_number):
                    if line and len(line) > 0:
                        # segData, last_diarization_idx_line = (self.audio_file_path)
                        self.selected_segment_info, last_diarization_idx_line = self.get_segmentdata_from_diariz_line(
                            audio_file_path=self.audio_file_path,
                            diariz_line=line, find_speakers_in_diariz_file=False,
                            last_diarization_idx_line=last_diarization_idx_line)

                        print(self.selected_segment_info.to_string())
                        self.insert_textarea_line(i,
                                                  self.selected_segment_info.pretty_transcription_line())
                else:
                    if audio_file_not_found:
                        if (self.extract_audio_file_info(line)):
                            audio_file_not_found = False
                            self.__get__diarization_file_path_from_audio_file_path__()

    def __get_audio_file_size_length__(self):
        audio_length = AudFU.get_audio_length_ffmpeg(self.audio_file_path)
        filesize = ffU.get_file_size(self.audio_file_path)

    def __extract_info_from_diar_file_line__(self):

    def get_all_speakers(self)-> List[str]:

    def find_speakers_in_diarizationRTTM(self, segData: TranscriptSegmentData,
                                         last_diarization_idx_line=None) -> int:

        if not self.diariz_file_lines:
            # Read content from the second file
            with open(self.diarization_file_path, 'r') as diariz_file:
                diariz_file_lines = diariz_file.readlines()

        # Create an output file to store the results
        # output_file = open('output.txt', 'w')
        start_idx = 0
        if last_diarization_idx_line and last_diarization_idx_line < len(self.diariz_file_lines):
            x_lines_before_last_idx = last_diarization_idx_line - 3
            if (x_lines_before_last_idx > 0):
                start_idx = x_lines_before_last_idx
            else:
                start_idx = last_diarization_idx_line

        # Extract timestamps and corresponding "SPEAKER_{XX}" strings from diariz file
        timestamps_and_speakers = []
        speakers = []
        i = start_idx
        for line in self.diariz_file_lines[start_idx:]:
            found_match = False
            match = re.search(
                r'SPEAKER\swaveform\s1\s([0-9]{1,}\.[0-9]{1,})\s([0-9]{1,}\.[0-9]{1,})\s<NA>\s<NA>\s(SPEAKER_)(\d+)\s',
                line)
            if match:
                diariz_start_time, param2, speaker, speaker_idx = match.groups()
                timestamps_and_speakers.append((float(diariz_start_time), float(param2), speaker, speaker_idx))
                if segData.end_timestamp >= diariz_start_time:
                    # Check if start_time2 falls within the range of the current line in file1
                    if segData.start_timestamp <= diariz_start_time:
                        #     output_file.write(f"Line in file1: [{diariz_start_time}s -> {param2}s] {speaker}\n")
                        #     output_file.write(f"Matching line in file2: {line2}\n")
                        #     output_file.write('\n')  # Add a separator between matches
                        speakers.append(SpeechSpeaker(first_name=speaker_idx, last_name=speaker))
                        self.debug(
                            f"speaker found:[{diariz_start_time}s in {segData.start_timestamp}s -> {segData.end_timestamp}\n")

                        found_match = True
                    else:
                        if found_match:
                            break  # Move to the next line in file1
            i += 1

        last_processed_line_index = i
        return speakers, last_processed_line_index

        # Close the output file
        # output_file.close()

        # Close the input files
        # diariz_file.close()


class PyAnnoteDiarizSegmentData(AbstractSegmentData):

    timestamp_regex = r"[\d]{1,}\.[\d]{3}"
    na_regex = r"<NA>>"
    timestamp_pattern = r"(" + timestamp_regex + ") -> (" + timestamp_regex + ") (.+)"
    pattern = r'SPEAKER\swaveform\s1\s([0-9]{1,})\.' + timestamp_pattern + '\s' + na_regex + '\s' + na_regex + '\s(SPEAKER_)(\d+)\s' + na_regex + '\s' + na_regex + '',

    def __init__(self, audio_file: str):
        super.__init__(audio_file)
        self.wave_form = None

    def __parse_raw_text_line__(self, raw_text_line):
        self.parse_raw_text_line(raw_text_line=raw_text_line)
    def parse_raw_text_line(self, raw_text_line):

        match = re.match(self.pattern, raw_text_line)

        if match:
            wave_form = float(match.group(1))
            start_timestamp = float(match.group(2))
            end_timestamp = float(match.group(3))
            long_string = match.group(4)
            return wave_form, start_timestamp, end_timestamp, long_string
        else:
            return None, None, None
