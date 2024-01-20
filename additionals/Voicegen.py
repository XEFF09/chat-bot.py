from gtts import gTTS
import os

def voicegen(text, save_foldername, language='en', output_file='output.mp3'):
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(f'{save_foldername}/{output_file}')