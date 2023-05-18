FROM python:3.9.5-slim-buster

# Path: /app
WORKDIR /app

# Path: /app/requirements.txt
COPY requirements.txt requirements.txt

# Path: /app
RUN pip install -r requirements.txt

# Path: /app
COPY . .

RUN apt-get update && apt-get install -y ffmpeg

CMD [ "python3", "-u", "main.py" ]