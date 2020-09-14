#records audio

import pyaudio
import wave
import scipy.io.wavfile
import numpy
import os
import time
from threading import Thread
import logging

def init(): #not used, copy this to create custom audio input
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 150 #if this value is smaller, an error in PyAudio causes less trouble
    CPS = int(RATE / CHUNK) #Chunks per second
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)
    SAMPLE_WIDTH = p.get_sample_size(FORMAT)
    audio = []

#counts down, how many seconds are still recrded
def timer(secs):
    while secs>0:
        logging.info(str(secs) + " seconds left.")
        time.sleep(1)
        secs -= 1
    logging.info("recording finished.")

#main is used to generate n sconds of audio and save it as 
#a.wav in the given folder
def main(seconds, folder_name):
    thread_timer = Thread(target=timer, args=(seconds,))
    thread_timer.start()
    print("here")
    CHANNELS = 1
    RATE = 44100
    CHUNK = 150 #if this value is smaller, an error in PyAudio causes less trouble
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)

    logging.info("recording...")
    num_dots = int(seconds * RATE)
    data = stream.read(num_dots)
    audio_numpy = numpy.frombuffer(data, dtype=numpy.int16)
    filename = folder_name + "/a.wav"
    scipy.io.wavfile.write(filename, RATE, audio_numpy)
    logging.info("audio written to " + filename)
    return audio_numpy


#records continuously audio and saves pieces of 5 seconds into the desired folder
#2 Tgreads are executed for this purpose
def gen_audio_live(seconds, folder_name):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 150 #if this value is smaller, an error in PyAudio causes less trouble
    CPS = int(RATE / CHUNK) #Chunks per second
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)
    SAMPLE_WIDTH = p.get_sample_size(FORMAT)
    audio = []

    def record_audio():#records audio chunks
        while(True):
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio.append(data) #this is fast enough to not get a missing chunk in the recording
    def get_file(seconds, folder_name): #checks if n seconds are recorded, and saves file
        cycle = 0
        while(True):
            if(len(audio) < ((cycle+1)*(seconds*CPS))):
                time.sleep(0.01) #check back in 0.01 seconds
                continue
            temp_name = folder_name + "/tempaudio.wav"
            filename = folder_name + "/raw" + str(cycle).zfill(4) + ".wav"
            aud_file = wave.open(temp_name, "wb")
            aud_file.setnchannels(CHANNELS)
            aud_file.setframerate(RATE)
            aud_file.setsampwidth(SAMPLE_WIDTH)
            begin = cycle * CPS * seconds
            end = begin + (CPS * seconds) #as last item is not picked, this works correctly
            to_write = audio[begin:end]
            aud_file.writeframes(b''.join(to_write))
            time.sleep(0.01) #if this sleep is not performed, the audio is not written completely before renaming it
            os.rename(temp_name, filename)
            logging.info("Another 5 seconds recorded. Audio written to " + filename)
            cycle += 1
    
    #start recording and saving
    thread_record = Thread(target=record_audio, args=())
    thread_record.start()
    time.sleep(abs(seconds - 1))#let it almost record the chunk first
    thread_save = Thread(target=get_file, args=(seconds, folder_name,))
    thread_save.start()