from gtts import gTTS
import os

def voicegen(text, save_foldername, language='en', output_file='output.mp3'):

    if ('```') in text or ('``') in text:
        return open(f'{save_foldername}/{output_file}', 'w').close()

    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(f'{save_foldername}/{output_file}')