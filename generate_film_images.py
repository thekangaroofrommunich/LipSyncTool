import JSon_As_Table
import wave
import os
import json
import logging
import time

#return the Length of the audio in 100th of a second
def get_length_of_audio(audio_adress):
    locked = True #it might happen, that the audio cannot be openned -> try again
    while(locked):
        try:
            audio = wave.open(audio_adress, "rb")
            locked = False
        except Exception:
            locked = True
            time.sleep(0.01)
    frames = audio.getnframes()
    framerate=audio.getframerate()
    duration = frames / float(framerate)
    return duration
    
# Generates the image_table, having the entry (time in 1/100 s, phone)
# for each timestamp
def generate_image_table(phone_table):
    act_time = 0 #current timestamp, therefore the to be taken one-hundreth-second
    image_table = []
    for word in phone_table: #for every word, add for every time phonemes into table
        if word != None:
            for index in range(len(word)-1):
                phone = word[index+1]
                if(act_time != phone[1]):
                    number_of_empty_frames = (((phone[1])*100) - act_time)
                    for n in range(int(number_of_empty_frames)):
                        image_table += [(act_time, "nothing")]
                        act_time += 1
                for n in range(int(phone[2]*100)):#add phones
                    image_table += [(act_time, phone[0])]
                    act_time += 1
    return image_table

#This function is called to return a frametable, that has the length of
#(duration of the corresponding audio * Frames per Second)
#You could say the lenght of the frame table "equals" the length of the audio
def pad_with_nones(adress_wav, frame_table):
    duration = get_length_of_audio(adress_wav)
    duration = int(duration * 100)
    to_pad = duration - len(frame_table)
    if to_pad > 0:
        position = len(frame_table)
        for index in range(to_pad):
            frame_table = frame_table + [(position, "nothing")]
            position += 1
    return frame_table

# Gets the adress of the alignment and creates the frame table for frame
# duration of 100th of a second
def write_frame_table(adress):
    table_target_file = open("GeneratedFrameTable.txt", "w")
    result_table = generate_image_table(JSon_As_Table.create_table(adress))
    table_target_file.write(str(result_table))
    table_target_file.close()
    return result_table

# gets the requested frames per seconds and the adress of the folder,
# where the alignment with the name "align.json" is saved to.
# Returns the frame table
def write_frame_table_nfps(n, adress):# n frames per second; adress of the folder
    adress_wav = adress + "/a.wav"
    adress_JSON = "Generated_Alignment/align.json"
    try:
        result_table_100fps = generate_image_table(JSon_As_Table.create_table(adress_JSON))
    except Exception:
        return []

    # fill with "nothing" in the end
    result_table_100fps = pad_with_nones(adress_wav, result_table_100fps)

    #100 FPS were given, but n requested -> get every n/100th frame (rounded off)
    result_table_nfps = []
    x = 100 / n
    current_frame = 0
    for index in range(int((len(result_table_100fps))/x)):
        result_table_nfps += [[current_frame, (result_table_100fps[int(x*index)][1])]]
        current_frame += 1

    #delete the alignment, as it is no longer needed, and can be written again
    try:
        os.remove("Generated_Alignment/align.json")
    except Exception:
        logging.info("Alignment could NOT be deleted.")

    #remove 0.5 secs "nothing" after the last syllable with neutral (f), after that close mouth
    max_replace = int(n/2)
    act_mouth = result_table_nfps[0][1]
    replaced = 0
    for index in range(len(result_table_nfps)):
        if((act_mouth != "nothing")
            and(act_mouth not in "m_b,m_E,m_I,m_S")
            and (result_table_nfps[index][1] == "nothing")
            and (replaced < max_replace)):
            #frame = result_table_nfps[index]
            result_table_nfps[index][1] = "neutral"
            replaced += 1
        else:
            replaced = 0
        act_mouth = result_table_nfps[index][1]

    #with the following lines, the frameable could be saved to the hard drive (if needed)
    #table_target_file = open("GeneratedFrameTable.txt", "w")
    #table_target_file.write(str(result_table_nfps))
    #table_target_file.close()

    logging.info("Frame table completed.")
    return result_table_nfps

#returns the frametable, created by the fuction above.
#Additionally returns the full text, spoken and recognized in this run
def get_frame_table_nfps_and_text(fps, path_of_folder):
    adress_JSON = "Generated_Alignment/align.json"

    #read spoken words from alignment
    text = []
    try:
        with open(adress_JSON, "r") as f:
            json_file = json.load(f)
        try:
            words = json_file["words"]#read all "words" from the file and add it to table
        except:
            a=5#return []
        #print(words)
        for index in range(len(words)):#add the timestamps of the recognized words
            try:
                word = words[index]
                word_time = word["start"]
                word_text = word["alignedWord"]
                text.append((word_time, word_text))
            except:
                pass #nothing should be done
    except: #in case of an error, the table is returned as far as processed
        pass

    #create table
    table = write_frame_table_nfps(fps, path_of_folder)

    return table, text