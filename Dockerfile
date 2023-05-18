FROM python:3.9.5-slim-buster

# Path: /app
WORKDIR /app

RUN apt update

RUN apt-get update && apt-get install -y ffmpeg

RUN apt install build-essentials -y
RUN apt-get install manpages-dev -y
RUN apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev libsndfile1-dev -y

# Path: /app/requirements.txt
COPY requirements.txt requirements.txt

# Path: /app
RUN pip install -r requirements.txt

# Path: /app
COPY . .

RUN python3 -m pip install --upgrade pip

CMD [ "python3", "-u", "main.py" ]