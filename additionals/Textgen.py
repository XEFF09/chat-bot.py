from dotenv import load_dotenv
import requests
import json
import os
import openai

import google.generativeai as genai

import PIL.Image

load_dotenv()
googleai_key = os.getenv('GOOGLEAI_KEY')
genai.configure(api_key=googleai_key)

# openai_key = os.getenv('OPENAI_KEY')
# openai.api_key = openai_key

def imageGen(img_path):
        img = PIL.Image.open(f'{img_path}')
        return img

def textGen(chat, text:str, img_path=None) -> str:
        # -- Google AI API (doc) --

        img = None
        if img_path is not None:
                model = genai.GenerativeModel('gemini-pro-vision')
                img = imageGen(img_path)
                response = model.generate_content([f"{text}", img], stream=True)
        else:
                response = chat.send_message([f"{text}"], stream=True)

        
        response.resolve()
        return (response.text)

        # -- OpenAI API --
        
        # url = "https://api.openai.com/v1/chat/completions"
        # payload = json.dumps({
        #         "model": "gpt-3.5-turbo",
        #         "text": text,
        #         "max_tokens": 50
        # })
        # headers = {
        #         'Content-Type': 'application/json',
        #         'Authorization': f'Bearer {openai_key}'
        # }
        # response = requests.request("POST", url, headers=headers, data=payload)
        # data = json.loads(response.text).get('choices')[0].get('message').get('content')
        # text.append({"role": "assistant", "content": f"{data}"})
        # return data

        # -- Google AI API --

        # url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={googleai_key}'
        # body = {"contents":[{"parts":[{"text":f"{text}"}]}]}
        # response = requests.post(url, json=body)
        # data = json.loads(response.text).get('candidates')[0].get('content').get('parts')[0].get('text')
        # text.append({"role": "assistant", "content": f"{data}"})
        # return data
