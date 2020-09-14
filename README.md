This software can be executed by adding it to a workspace, where Gentle is installed. 

Gentle can be downloaded from here: https://github.com/lowerquality/gentle

Gentle needs a proper installation of Kaldi.

Therefore I reccommend the following procedure:

1) Clone everything (Gentle into this folder and Kaldi into gentle/ext)

You should then have the working directory as follows:

|audio_input.py

|generate_film_images

|gentle_align.py

|image_stream.py

|JSon_As_Table.py

|phones.txt

|program.py

|program_from_docker.py

|README.md

|table_phonetics.json

|transcript_by_google.py

-gentle

  |\gentle_stuff
  
  |DOCKERFILE
  
  |install.sh
  
  -ext
  
    |\stuff
    
      -kaldi
      
        |src, |INSTALL, |README.md, |\more kaldi stuff

2) Install the nvidia cuda toolkit by executing
sudo apt install nvidia-cuda-toolkit

3) Install the reqirements for LST, check the Dockerfile for exact prerequisits

4) Install Kaldi (from the instructions of their INSTALL file)

5) Do everything from install.sh by gentle, but do NOT execute the line where Kaldi is installed

6) You should be done, restart your computer.