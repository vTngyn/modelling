import re
def extract_parameters_for_number_of_speakers_from_filename(base_file_name: str) -> dict:
    # default parameters:
    specifyNrSpeakers = False
    isExactNbrSPeakerKnown = False
    numberOfSpeakers = 2
    min_speakers = 2
    max_speakers = 6
    # , specifyNrSpeakers = True, isExactNbrSPeakerKnown = False, numberOfSpeakers = 2, min_speakers = 2, max_speakers = 6
    # Define regex patterns to match the desired patterns
    pattern_interval = r'_([0-9]{1,})[pP]-([0-9]{1,})[pP]_'  # Pattern for interval: {lower}-{upper}p
    pattern_single = r'_([0-9]{1,})[pP]_'  # Pattern for single number
    pattern_interval = r'_([0-9]{1,})[pP]-([0-9]{1,})[pP]_'  # Pattern for interval: {lower}-{upper}p
    pattern_single = r'_([0-9]{1,})[pP]_'  # Pattern for single number
    pattern_interval = r'_(\d+)[pP]-(\d+)[pP]_'  # Pattern for interval: {lower}-{upper}p
    pattern_single = r'_(\d+)[pP]_'  # Pattern for single number

    # Use findall to extract all matching substrings for interval
    matches_interval = re.findall(pattern_interval, base_file_name)
    if matches_interval and len(matches_interval) > 0:
        try:
            min_speakers, max_speakers = int(matches_interval[0][0]), int(matches_interval[0][1])
            specifyNrSpeakers = True
        except Exception as e:
            print(e)
    else:
        # If no interval numbers found, try to extract single numbers
        matches_single = re.findall(pattern_single, base_file_name)
        if matches_single and len(matches_single) > 0:
            try:
                numberOfSpeakers = int(matches_single[0])
                specifyNrSpeakers = True
                isExactNbrSPeakerKnown = True
            except Exception as e:
                print(e)
    result = {'specifyNrSpeakers': specifyNrSpeakers, 'isExactNbrSPeakerKnown': isExactNbrSPeakerKnown,
              'numberOfSpeakers': numberOfSpeakers, 'min_speakers': min_speakers, 'max_speakers': max_speakers}
    # SpeakerDiarization.debug("extracted speaker parameters:")
    print(result)
    return result

extract_parameters_for_number_of_speakers_from_filename("djksfhksj_45p_ferfe.txt")
extract_parameters_for_number_of_speakers_from_filename("djksfhksj_8p-124P_ferfe.txt")
