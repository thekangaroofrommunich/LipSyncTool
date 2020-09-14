import io
import os
import wave

#def sample_recognize is made by Google and changed to LST's needs:
#https://cloud.google.com/speech-to-text/docs/sync-recognize?hl=de

from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import io

def sample_recognize(local_file_path):
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
        local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    client = speech_v1.SpeechClient()

    enable_word_time_offsets = True

    # The language of the supplied audio
    language_code = "en-US"

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 44100

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "enable_word_time_offsets": enable_word_time_offsets,
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    response = client.recognize(config, audio)
    print("Credit by Google used")
    try:
        result = response.results[0]
        return result.alternatives[0]#.transcript
    except (IndexError):
        return ""
    #for result in response.results:
        # First alternative is the most probable result
        #alternative = result.alternatives[0]
        #print(u"Transcript: {}".format(alternative.transcript))

def get_transcript(local_file_path):
    audio = wave.open(local_file_path, "rb")
    frames = audio.getnframes()
    framerate=audio.getframerate()
    duration = frames / float(framerate)
    audio.close()
    if(duration > 59):
        try:
            return input("Your audio is too long for automatic"
                        " recognition. Please enter your transcript: ")
        except (AttributeError):
            return ""
    try:
        return sample_recognize(local_file_path).transcript
    except (AttributeError):
        return ""

def sample_recognize_and_end_last_word(local_file_path):
    audio = wave.open(local_file_path, "rb")
    frames = audio.getnframes()
    framerate=audio.getframerate()
    duration = frames / float(framerate)
    audio.close()
    if(duration > 59):
        try:
            return input("Your audio is too long for automatic"
                        " recognition. Please enter your transcript: ")
        except (AttributeError):
            return ""
    text_with_stamps = sample_recognize(local_file_path)
    text = ""
    try:
        text = text_with_stamps.transcript #can be empty, then an exception is thrown
        
        #in the last "words", get the timestamp, which is at position length-6 and length-5
        seconds = text_with_stamps[len(text_with_stamps)-6].split(": ")[1]
        nanoseconds = text_with_stamps[len(text_with_stamps)-5].split(": ")[1]
        seconds = (int(seconds)*1000) + ((int(nanoseconds)/1000000))
    except (AttributeError, IndexError, TypeError, ValueError):
        if(duration > 2):
            seconds = duration -1
        else:
            seconds = 0
    return(text, seconds)