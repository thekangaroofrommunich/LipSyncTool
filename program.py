# starts the program flows
import os
import gentle_align
import wave
import transcript_by_google
import image_stream
import shutil
import audio_input
import time
from threading import Thread
from pathlib import Path
import subprocess
from pydub import AudioSegment
import logging
import math

#let the user insert what he wants to do, 
#is repeated until valid input is given
def get_use_case():
    while(True):
        logging.info("You can either generate a video by typing in the audio location "\
        "(e.g. \"C:Documents/project/a.wav\"), create a video file from the "\
        "microphone by tpying the duration in seconds (e.g. \"15\"), or type "\
        "\"live\") for live streaming to the output @ udp port 127.0.0.1:1234.")
        time.sleep(0.01)#otherwise, logging info shows up too late, and this line is written above :(
        use_case = input("Type your use case: ")
        if(use_case == "live"): #Usecase Live
            return use_case
        elif("." in use_case): #Indicator for usecase video from file
            path = Path(use_case)
            if(path.is_file):
                return use_case
        else: #try last use case (video from live recording)
            try:
                int(use_case)
                return use_case
            except ValueError:
                logging.info("We could not identify what you want LST to do. Please specify again.")
    return -1

#checks if the google key exists, if not requests an input of a ONE-LINE-key
def get_google_key():
    if(os.path.isfile("google/google_key_lipsynctool.json")):
        return True
    else:
        key_input = input("Input your Google key here (make sure to replace linebreaks by the $ symbol): ")
        key = open("google/google_key_lipsynctool.json", "w")
        line = ""
        #transform it back into eky with line breaks
        for letter in key_input:
            if(letter == "$"):
                key.write(line)
                key.write("\n")
                line = ""
            else:
                line += letter
        if(line == "}"):
            key.write(line)
            key.close()
            return True
    return False

# makes sure all folders exist, that are used
def make_folders():
    newpath = "Fotos_generated"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = "Movies"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = "Generated_Alignment"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = "InputFiles"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = "cache"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    newpath = "google"
    if not os.path.exists(newpath):
        os.makedirs(newpath)

#cleans up, everything that was used, or could be needed clean in the future
def clean_folders():
    trash = False
    try:
        os.remove("GeneratedFrameTable.txt")
    except (PermissionError, OSError):
        trash = True
    try:
        shutil.rmtree("Fotos_generated")
    except (PermissionError, OSError):
        trash = True
    try:
        shutil.rmtree("InputFiles")
    except (PermissionError, OSError):
        trash = True
    try:
        shutil.rmtree("cache")
    except (PermissionError, OSError):
        trash = True
    try:
        shutil.rmtree("Generated_Alignment")
    except (PermissionError, OSError):
        trash = True  
    if(not trash):
        logging.info("All created temporary files, that are not in use, deleted.")        

#records n seconds of audio, transcripts it, generates alignment and writes everything onto file system
def get_audio_and_alignment_for_nsecs(seconds, fps, abs_uri):
    wave = audio_input.main(seconds, abs_uri)
    abs_uri_audio = abs_uri + "/a.wav"
    write_transcript_for_file(abs_uri_audio)
    gentle_align.start_aligning(abs_uri + "/a.wav", "Generated_Alignment/transcript.txt", "Generated_Alignment/align.json")

#audio files longer than 1 minute can unfortunately not be
# handeled by Google. Therefore they are split into pieces and then
# detected in parts
def write_transcript_for_file(file_path):
    logging.info("Getting transcript...")
    audio = wave.open(file_path, "rb")
    frames = audio.getnframes()
    framerate_audio = audio.getframerate()
    duration = frames / float(framerate_audio)
    number_runs = math.ceil(duration / 59)
    audio.close()
    audio = open(file_path, "rb")
    j = range(number_runs)
    transcript = open("Generated_Alignment/transcript.txt", "a")
    text = ""
    for i in j: #for every piece that is 59 seconds long
        aud_file = AudioSegment.from_wav(audio)
        new_audio = AudioSegment.empty()
        new_audio = aud_file[(i*59000):((i+1)*59000)]
        filename = "cache/partitialaudio.wav"
        new_audio.export(filename)
        file_for_google = "cache/forgoogle.wav" #prepare file that google accepts it
        cmd = f'ffmpeg -y -i {filename} -ac 1 -ar 44100 {file_for_google}' 
        subprocess.check_output(cmd, shell=True)
        time.sleep(1)#give FFmpeg time to finish
        uri = os.getcwd()
        uri = uri + "/cache/forgoogle.wav"
        text += transcript_by_google.get_transcript(uri) + " "#add to the previous text
    logging.info("Your file says: " + text)
    transcript.write(str(text))#save text
    transcript.close()
#records unlimited pieces of n seconds of audio and writes them to the file system (calls function in audio_input.py)
def record_live_audio_pieces(seconds, abs_uri):
    audio_input.gen_audio_live(seconds, abs_uri)

#converts input file into usable wav and generates transcript; saves both to file system
def prep_audio_transcript_for_file(file_from, file_to):
    #convert Input File into usable wav file
    try:
        cmd = f'ffmpeg -y -i {file_from} -ac 1 -ar 44100 {file_to}' 
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        logging.info("Your file was not a proper file containing audio. Please"\
            " view the FFmpeg documentation for supported audio files!")
        logging.info("LST will be started again, please consider restarting"\
            " the program manually after more than 3 restarts.")
        main()
        raise SystemExit

    write_transcript_for_file(file_to)

#takes audio when its read, collects data from transcript to add audios (s. Example in function)
def prep_audio_and_alignment_for_live(seconds, fps, abs_uri):
    """ Function explanation:
        It will take the end of the last word within the "seconds" time (time for one loop),
        and cut after this. For all upcoming take the rest of the last audio, and add it to the
        audio from the current loop (same procedure).
        Example:
        secs:   0      1      2      3      4      5      6      7      8      9      10     11  ...
        words:  Hello,       I      am         pleased  to explain     it      to  you.          ...
        audio:  |_____________________|__________________________________________|______________ ...
        files:         a0000.wav                        a0001.wav                   a0002.wav    ...
    """
    def_dur = seconds * 1000 #definitive maximum duration of one piece of input audio in ms
    cycle = 0
    last_audio = None
    last_end = 0
    while(True):
        abs_uri_audio = abs_uri + "/raw" + str(cycle).zfill(4) + ".wav"
        if(not os.path.isfile(abs_uri_audio)):
            time.sleep(0.01)
            continue
        #file may exist, but is not finished
        try:
            audio = wave.open(abs_uri_audio, "rb")
            frames = audio.getnframes()
            framerate=audio.getframerate()
            duration = frames / float(framerate)
            if(duration<seconds):
                audio.close()
                continue
            audio.close()
        except:
            continue
        
        #add (prepend) unused part from last cycle if it exists
        if ((cycle == 0) or (last_audio == None) or (last_end >= def_dur)):
            old_audio = AudioSegment.empty()
        else:
            old_audio = open(last_audio, "rb")
            old_audio = AudioSegment.from_wav(old_audio)
            old_audio = old_audio[-(def_dur-last_end):]
        act_audio = open(abs_uri_audio, "rb")
        act_audio = AudioSegment.from_wav(act_audio)
        act_audio = old_audio + act_audio

        #necessary FFmpeg conversion
        temp_name = abs_uri + "/for_ffmpeg.wav"
        act_audio.export(temp_name)
        #temp_name_2 = folder_name + "/tempaudio_converted.wav"
        cmd = f'ffmpeg -y -i {temp_name} -ac 1 -ar 44100 {abs_uri_audio}' 
        subprocess.check_output(cmd, shell=True)
        time.sleep(0.1)
        #os.rename(temp_name_2, filename)
        try:
            os.remove(temp_name)
        except:
            logging.info("possible Error. Could not remove temporary file!")
        transcript = open("Generated_Alignment/transcript.txt", "w")

        text, end_last_word = transcript_by_google.sample_recognize_and_end_last_word(abs_uri_audio)
        transcript.write(str(text))
        transcript.close()

        abs_end = int(end_last_word + (def_dur-last_end)) #total length of audio in ms

        #cut audio at the end of last word
        complete_audio = act_audio[:abs_end]

        #save file as cache file, render it as needed, and as
        # current file for the frame table and for rendering
        filename = abs_uri + "/aforffmpeg.wav"
        a_destination = abs_uri + "/a.wav"
        complete_audio.export(filename)
        cmd = f'ffmpeg -y -i {filename} -ac 1 -ar 44100 {a_destination}' 
        subprocess.check_output(cmd, shell=True)
        time.sleep(0.1)
        filename_abs = abs_uri + "/a" + str(cycle).zfill(4) + ".wav"
        try:
            shutil.copyfile(a_destination, filename_abs)
        except FileNotFoundError:
            try_again = True
            while (try_again):
                try:
                    shutil.copyfile(a_destination, filename_abs)
                    try_again = False
                except FileNotFoundError:
                    try_again = True

        #generate alignment and save in GeneratedAlignment/align.json
        gentle_align.start_aligning("InputFiles/a.wav", "Generated_Alignment/transcript.txt", "Generated_Alignment/align.json")
        
        #update Values for next loop iteration
        cycle += 1
        last_audio = abs_uri_audio
        last_end = end_last_word

def main():
    log_level = "INFO" 
    logging.getLogger().setLevel(log_level)
    logging.info("starting program")

    clean_folders()
    make_folders()

    uri = os.getcwd() 
    abs_uri = uri + "/InputFiles"

    #set Google key
    if(not get_google_key()):
        logging.info("There was an error setting the Google key. Please make sure it is correctly written "
              "under google/google_key_lipsynctool.json.")
    uri_google = abs_uri.rpartition("/")[0]
    uri_google += "/google/google_key_lipsynctool.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = uri_google

    #get the user to type what he wants LST to do
    use_case = get_use_case()

    #specify framerate or use default 10 FPS.
    try:
        framerate=int(input("Default Framerate: 10. Type in a new framerate [1, 100] "\
                            "or use the default framerate by entering a non-int-value: "))
        logging.info("Desired framerate is " + str(framerate) + " FPS.")
        if(framerate < 1 or framerate > 100):#alignment only generates hundreth of a second
            framerate = 10
            logging.info("No values outside [1, 100] are allowed. Framerate unchanged @ 10FPS.")
    except(ValueError):
        framerate = 10
        logging.info("Framerate unchanged @ 10FPS.")

    #1 First Case: Live
    if(use_case == "live"):# 1) for "live", "live" is set to True
        #start threads audio_grabbing, transcripting and aligning, and producing images
        seconds = 5 # duration of each recording interval

        thread_record = Thread(target=record_live_audio_pieces, args=(seconds, abs_uri,))
        thread_record.start()

        thread_align = Thread(target=prep_audio_and_alignment_for_live, args=(seconds, framerate, abs_uri,))
        thread_align.start()

        thread_stream = Thread(target=image_stream.pipe_frames, args=("live", framerate, abs_uri,))
        thread_stream.start()
    
    #2 Audio is already recorded, generate Alignment and Video
    elif("." in use_case):# 2) for file path, abs_uri is set to the string before the last "/"
        #File is made sure to be in wav format later, and it will be written to InputFiles/a.wav
        abs_uri_audio = abs_uri + "/a.wav"
        prep_audio_transcript_for_file(use_case, abs_uri_audio)
        #generate alignment and save in GeneratedAlignment/align.json
        gentle_align.start_aligning(abs_uri + "/a.wav", "Generated_Alignment/transcript.txt", "Generated_Alignment/align.json")

        #generate video
        image_stream.pipe_frames("from_aud",framerate, abs_uri)

    #3 Record n seconds audio and generate movie
    else: # 3) last usecase: holds seconds, so string is converted into the seconds
        seconds = int(use_case)
        #record audio once with function
        get_audio_and_alignment_for_nsecs(seconds, framerate, abs_uri)

        #generate video
        image_stream.pipe_frames("from_mic",framerate, abs_uri)
    
    clean_folders()

if __name__ == '__main__':
    main()