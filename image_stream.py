import os, time, sys, subprocess
import numpy as np
import matplotlib.pylab as plt
from PIL import Image
import json
import generate_film_images as gen
import subprocess as sp 
from random import *
import cv2
from skimage.io import imsave
import logging

#this function is called, if video should be saved as file.
#The video will be saved to "Movies/Movie_from_LST.mp4"
def call_ffmpeg(fps):
    input = r"Fotos_generated/image%05d.png"
    output = r"Movies/Movie_from_LST.mp4"
    path_of_audio = "InputFiles/a0000.wav"

    cmd = f'ffmpeg -framerate {fps} -i "{input}" -i {path_of_audio} "{output}" -y'
    subprocess.check_output(cmd, shell=True)

#This function is always called to create and render frames
def pipe_frames(use_case, fps, path_of_folder):#use case E{live, from_aud, from_mic}
    cmd_out = ""
    fps_string = str(fps)

    if(use_case == "live"):
        #configure stream with ffmpeg
        cmd_stream = ['ffmpeg', 
        '-f', 'image2pipe', 
        '-thread_queue_size', '2',
        '-re',
        '-i', '-', # Input comes from pipe
        '-framerate', fps_string, # Framerate
        '-preset', 'veryfast',
        '-f' , 'mpegts',
        'udp://127.0.0.1:1234']
        
        #Initialize Pipe
        pipe = sp.Popen(cmd_stream, stdin=sp.PIPE)

        logging.info("Video stream will be callable under udp://@127.0.0.1:1234")

    #phone to image table specifies, for which phoneme which viseme is related
    phone_to_image_table = ""
    with open("table_phonetics.json", "r") as f:
        phone_to_image_table = json.load(f)

    #openallimages
    def readmouth(path):
        img = plt.imread(path)
        img = img * 255
        img_2 = np.zeros((720,1280,4))
        img_2 [410:610, 540:740] = img
        img = img_2
        img_nz = img[:,:,3] > 0
        img = np.array(img, dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img, img_nz
    background = plt.imread("Faces/background.png")
    background = background * 255
    background = background.astype(np.uint8)
    background_2 = np.zeros((720,1280, 4))
    background_2[0:720, 0:1280]= background
    background = background_2
    background = np.array(background, dtype=np.uint8)
    background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
    face = plt.imread("Faces/face.png")
    face = face * 255
    face_2 = np.zeros((720,1280, 4))
    face_2[60:660, 340:940]= face
    face = face_2
    face_nz = face[:,:,3] > 0
    face = np.array(face, dtype=np.uint8)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    eyes = plt.imread("Faces/eyes.png")
    eyes = eyes * 255
    eyes_2 = np.zeros((720,1280, 4))
    eyes_2[220:420, 440:840]= eyes
    eyes = eyes_2
    eyes_nz = eyes[:,:,3] > 0
    eyes = np.array(eyes, dtype=np.uint8)
    eyes = cv2.cvtColor(eyes, cv2.COLOR_BGR2RGB)
    pupils = plt.imread("Faces/pupils.png")
    pupils = pupils * 255
    pupils_orig = pupils
    pupils_2 = np.zeros((720,1280, 4))
    pupils_2[220:420, 440:840]= pupils
    pupils = pupils_2
    pupils_nz = pupils[:,:,3] > 0
    pupils = np.array(pupils, dtype=np.uint8)
    pupils = cv2.cvtColor(pupils, cv2.COLOR_BGR2RGB)
    blink = plt.imread("Faces/blink.png")
    blink = blink * 255
    blink_2 = np.zeros((720,1280, 4))
    blink_2[220:420, 440:840]= blink
    blink = blink_2
    blink_nz = blink[:,:,3] > 0
    blink = np.array(blink, dtype=np.uint8)
    blink = cv2.cvtColor(blink, cv2.COLOR_BGR2RGB)
    closed_mouth, closed_mouth_nz = readmouth("Faces/closed_mouth.png")
    closed2f, closed2f_nz = readmouth("Faces/closed2f.png")
    closed2i, closed2i_nz = readmouth("Faces/closed2i.png")
    closed2m, closed2m_nz = readmouth("Faces/closed2m.png")
    closed2o, closed2o_nz = readmouth("Faces/closed2o.png")
    f2i, f2i_nz = readmouth("Faces/f2i.png")
    fff, fff_nz = readmouth("Faces/fff.png")
    iii, iii_nz = readmouth("Faces/iii.png")
    m2f, m2f_nz = readmouth("Faces/m2f.png")
    m2i, m2i_nz = readmouth("Faces/m2i.png")
    mmm, mmm_nz = readmouth("Faces/mmm.png")
    o2f, o2f_nz = readmouth("Faces/o2f.png")
    o2i,o2i_nz = readmouth("Faces/o2i.png")
    o2m, o2m_nz = readmouth("Faces/o2m.png")
    ooo, ooo_nz = readmouth("Faces/ooo.png")
    open2closed, open2closed_nz = readmouth("Faces/open2closed.png")
    open2f, open2f_nz = readmouth("Faces/open2f.png")
    open2i, open2i_nz = readmouth("Faces/open2i.png")
    open2m, open2m_nz = readmouth("Faces/open2m.png")
    open2o, open2o_nz = readmouth("Faces/open2o.png")
    open_mouth, open_mouth_nz = readmouth("Faces/open_mouth.png")


    def render_frames(cycle, case):
        #generate frame table
        frame_table, text = gen.get_frame_table_nfps_and_text(fps, path_of_folder)
        display_text = ""
        if(frame_table == []):
            time.sleep(0.01)#in case of live, it will then be called again
            return
           
        #rename audio file and paste it in logic
        try:
            path_old = path_of_folder + "/a.wav"
            path_new = path_of_folder + "/a" + str(cycle).zfill(4) + ".wav"
            os.rename(path_old, path_new)
        except FileNotFoundError:
            logging.info("File does not exist, check hat happened!")
        
        next_blink = randint(fps, (fps * 3)) # after a few frames there should be blinking
                                             # one blink every 1 to 3 seconds
        act_frame_num = 0 # Enumeration of frames
        if(not(case ==" live" )):
            logging.info("start rendering. This can take while.")
            
        #create frames, overlay background, face, eyes, pupils, and mouth
        for frame in frame_table:
            img = np.zeros((720,1280, 3))
            img[0:720, 0:1280] = background
            img [face_nz] = face[face_nz]
            if(next_blink <= 0):
                img[blink_nz] = blink[blink_nz]
                if(next_blink == 0 and fps>30):#at high framerates we need 2 frames blinking
                    next_blink = -1
                else:
                    next_blink = randint(fps, (fps * 3))
            else:
                next_blink = next_blink - 1
                img[eyes_nz] = eyes[eyes_nz]
                #it was considered, letting the avatar move its pupils, however
                #this does not work and causes a breakdown of the program.
                #Comment in the next lines, if you find the mistake that was made.
                """if(next_pupil_move == 0):
                    pup_x = randint(0,90)
                    pup_y = randint(0,40)
                    pupils = np.zeros((720,1280, 4))
                    pupils[(220+pup_x):(420+pup_x), (440+pup_y):(840+pup_y)] = pupils_orig
                    pupils_nz = pupils[:,:,3] > 0
                    pupils = np.array(pupils, dtype=np.uint8)
                    pupils = cv2.cvtColor(pupils, cv2.COLOR_BGR2RGB)
                    next_pupil_move = randint(1, fps*5)
                else:
                    next_pupil_move = next_pupil_move -1"""
                img[pupils_nz] = pupils[pupils_nz]

            #In the following the correct mouth shape is looked up
            #using table_phonetics.json
            vocal = frame[1]
            try:
                mouth_act = phone_to_image_table[vocal]
            except KeyError:
                mouth_act = "closed_mouth"
            
            try: 
                mouth_next_look = frame_table[act_frame_num + 1][1]
                mouth_next = phone_to_image_table[mouth_next_look]
            except (IndexError, KeyError):
                mouth_next = "closed_mouth"
            
            #closed_mouth
            if(mouth_act == "closed_mouth"):
                if(mouth_next == "closed_mouth"):
                    img[closed_mouth_nz] = closed_mouth[closed_mouth_nz]
                elif(mouth_next == "fff"):
                    img[closed2f_nz] = closed2f[closed2f_nz]
                elif(mouth_next == "ooo"):
                    img[closed2o_nz] = closed2o[closed2o_nz]
                elif(mouth_next == "mmm"):
                    img[closed2m_nz] = closed2m[closed2m_nz]
                elif(mouth_next == "iii"):
                    img[closed2i_nz] = closed2i[closed2i_nz]
                elif(mouth_next == "open_mouth"):
                    img[closed2f_nz] = closed2f[closed2f_nz]
                else:
                    img[closed_mouth_nz] = closed_mouth[closed_mouth_nz]
            #open_mouth
            elif(mouth_act == "open_mouth"):
                if(mouth_next == "closed_mouth"):
                    img[open2closed_nz] = open2closed[open2closed_nz]
                elif(mouth_next == "fff"):
                    img[open2f_nz] = open2f[open2f_nz]
                elif(mouth_next == "ooo"):
                    img[open2o_nz] = open2o[open2o_nz]
                elif(mouth_next == "mmm"):
                    img[open2m_nz] = open2m[open2m_nz]
                elif(mouth_next == "iii"):
                    img[open2i_nz] = open2i[open2i_nz]
                elif(mouth_next == "open_mouth"):
                    img[open2f_nz] = open2f[open2f_nz]
                else:
                    img[open_mouth_nz] = open_mouth[open_mouth_nz]
            #fff
            elif(mouth_act == "fff"):
                if(mouth_next == "closed_mouth"):
                    img[closed2f_nz] = closed2f[closed2f_nz]
                elif(mouth_next == "fff"):
                    img[fff_nz] = fff[fff_nz]
                elif(mouth_next == "ooo"):
                    img[o2f_nz] = o2f[o2f_nz]
                elif(mouth_next == "mmm"):
                    img[m2f_nz] = m2f[m2f_nz]
                elif(mouth_next == "iii"):
                    img[f2i_nz] = f2i[f2i_nz]
                elif(mouth_next == "open_mouth"):
                    img[open2f_nz] = open2f[open2f_nz]
                else:
                    img[fff_nz] = fff[fff_nz]
            #ooo
            elif(mouth_act == "ooo"):
                if(mouth_next == "closed_mouth"):
                    img[closed2o_nz] = closed2o[closed2o_nz]
                elif(mouth_next == "fff"):
                    img[o2f_nz] = o2f[o2f_nz]
                elif(mouth_next == "ooo"):
                    img[ooo_nz] = ooo[ooo_nz]
                elif(mouth_next == "mmm"):
                    img[o2m_nz] = o2m[o2m_nz]
                elif(mouth_next == "iii"):
                    img[o2i_nz] = o2i[o2i_nz]
                elif(mouth_next == "open_mouth"):
                    img[open2o_nz] = open2o[open2o_nz]
                else:
                    img[ooo_nz] = ooo[ooo_nz]
            #mmm
            elif(mouth_act == "mmm"):
                if(mouth_next == "closed_mouth"):
                    img[closed2m_nz] = closed2m[closed2m_nz]
                elif(mouth_next == "fff"):
                    img[m2f_nz] = m2f[m2f_nz]
                elif(mouth_next == "ooo"):
                    img[o2m_nz] = o2m[o2m_nz]
                elif(mouth_next == "mmm"):
                    img[mmm_nz] = mmm[mmm_nz]
                elif(mouth_next == "iii"):
                    img[m2i_nz] = m2i[m2i_nz]
                elif(mouth_next == "open_mouth"):
                    img[open2m_nz] = open2m[open2m_nz]
                else:
                    img[mmm_nz] = mmm[mmm_nz]
            #iii
            elif(mouth_act == "iii"):
                if(mouth_next == "closed_mouth"):
                    img[closed2i_nz] = closed2i[closed2i_nz]
                elif(mouth_next == "fff"):
                    img[f2i_nz] = f2i[f2i_nz]
                elif(mouth_next == "ooo"):
                    img[o2i_nz] = o2i[o2i_nz]
                elif(mouth_next == "mmm"):
                    img[m2i_nz] = m2i[m2i_nz]
                elif(mouth_next == "iii"):
                    img[iii_nz] = iii[iii_nz]
                elif(mouth_next == "open_mouth"):
                    img[open2i_nz] = open2i[open2i_nz]
                else:
                    img[iii_nz] = iii[iii_nz]
            
            #calculate the text that is to be displayed
            try:
                act_time = act_frame_num / fps
                if(act_time > text[0][0]):
                    word_new = text[0][1]
                    text.pop(0) #remove word from list
                    if(len(display_text) + len(word_new) > 65):#only 65 characters can be displayed
                        display_text = word_new
                    else:
                        display_text += " " + word_new
            except:
                pass
            font = cv2.FONT_HERSHEY_SIMPLEX
            textsize = cv2.getTextSize(display_text, font, 1, 2)[0]
            textX = int((img.shape[1] - textsize[0]) / 2)
            cv2.putText(img, display_text, (textX, 80), font, 1, (255, 255, 255), 2)

            #save image
            name = "Fotos_generated/image"
            index = frame[0]
            if(index<10):
                index = "0000" + str(index)
            elif(index<100):
                index = "000" + str(index)
            elif(index<1000):
                index = "00" + str(index)
            elif(index<10000):
                index = "0" + str(index)
            else:
                index = str(index)
            name += index
            name += ".png"
            cv2.imwrite(name, img)
            act_frame_num += 1
            
            #img.save(pipe.stdin, 'PNG')
            if(case == "live"):
                img = Image.open(name)
                img.save(pipe.stdin, 'PNG')
        logging.info(str(act_frame_num) + " frames rendered for the current recording")
    
    #In the live case, render_frames is called more often and uses alwasy the current audio
    if(use_case == "live"):
        cycle = 0
        while(True):
            render_frames(cycle, "live")
    else:
        render_frames(0, "not_live")
        call_ffmpeg(fps)
        logging.info("Done. Sometimes ffmpeg needs some time to finish, depending on your PC ressources.")