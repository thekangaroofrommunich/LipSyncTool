FROM nvidia/cuda:10.2-base

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && \
	apt-get -y upgrade
RUN	apt-get install -y alsa-base alsa-utils \
		libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 \
		ffmpeg \
		python3.7 python3-dev python3-pip \
    	git \
		libxrender-dev \
		#python-pyaudio 
		python3-pyaudio &&\
	apt install -y libsm6 libxext6 && \
	pip3 install pyaudio && \
	#dpkg –add-architecture i386 && \
	apt-get update && apt-get upgrade && \
	apt-get install -y lib32gcc1 lib32stdc++6
	#libcurl4-gnutls-dev:i386

#camera input
#RUN git clone https://github.com/umlaeute/v4l2loopback.git
#RUN cd v4l2loopback & make & make install & depmod -a
#RUN apt install -y aptitude & aptitude install v4l2loopback-dkms

#gentle prerequisites

RUN DEBIAN_FRONTEND=noninteractive && \
	apt-get update && \
	apt-get install -y \
		gcc g++ gfortran \
		libc++-dev \
		libstdc++-6-dev \
		zlib1g-dev \
		automake autoconf libtool \
		git subversion \
		libatlas3-base \
		nvidia-cuda-dev \
		ffmpeg \
		python3 python3-dev python3-pip \
		python python-dev \
		python-pip \
		wget unzip && \
	apt-get clean

#install gentle
RUN git clone https://github.com/lowerquality/gentle.git && \
	cd gentle/ext && git clone https://github.com/kaldi-asr/kaldi.git && \
	mkdir openfst && cd openfst && \
		apt install -y curl && \
		curl -O http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.6.6.tar.gz && \
		apt install -y graphviz && \
		tar -xzf openfst-1.6.6.tar.gz && \
		cd openfst-1.6.6 && \
		./configure --enable-far=true && \
		make -j4 && \
		make install
#		pip3 install openfst
RUN cd gentle/ext/kaldi/tools && \
	apt-get install -y gcc-5 g++-5 gcc-6 g++-6\
		make \
		automake \
		autoconf \
		unzip \
		sox \
		gfortran \
		libtool \
		subversion && \
	make && \
	extras/install_openblas.sh && \
	cd .. && cd src && \
	./configure --shared --mathlib=OPENBLAS && \
	make depend -j 4 && make -j 4

RUN pip3 install requests==2.22.0 \
		scipy==1.4.1 \
		numpy==1.18.5 \
		opencv-python==4.2.0.34 \
		scikit-image==0.17.2 \
		ffmpeg-python==0.2.0 \
		Twisted==20.3.0 \
		google-api-core==1.20.0 \
		google-auth==1.17.1 \
		google-cloud-core==1.3.0 \
		google-cloud-speech==1.3.2 \
		google-cloud-storage==1.29.0 \
		google-resumable-media==0.5.1 \
		googleapis-common-protos==1.52.0 \
		grpcio==1.29.0 \
		PyAudio==0.2.11 \
		pydub==0.24.1

RUN cd /gentle && python3 setup.py develop
RUN cd /gentle && ./install_models.sh

VOLUME /gentle/webdata

ADD program.py audio_input.py generate_film_images.py gentle_align.py \
	image_stream.py JSon_As_Table.py table_phonetics.json \
	transcript_by_google.py program_from_docker.py ./
ADD m3 gentle/ext/m3
ADD Faces Faces
ADD assets assets

EXPOSE 8000
CMD ["python3", "./program_from_docker.py"]