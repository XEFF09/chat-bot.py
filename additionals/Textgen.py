from dotenv import load_dotenv
import requests
import json
import os
import openai

load_dotenv()
googleai_key = os.getenv('GOOGLEAI_KEY')

openai_key = os.getenv('OPENAI_KEY')
openai.api_key = openai_key

def textGen(messages: list) -> str:

        # -- OpenAI API --
        
        # url = "https://api.openai.com/v1/chat/completions"
        # payload = json.dumps({
        #         "model": "gpt-3.5-turbo",
        #         "messages": messages,
        #         "max_tokens": 50
        # })
        # headers = {
        #         'Content-Type': 'application/json',
        #         'Authorization': f'Bearer {openai_key}'
        # }
        # response = requests.request("POST", url, headers=headers, data=payload)
        # data = json.loads(response.text).get('choices')[0].get('message').get('content')
        # messages.append({"role": "assistant", "content": f"{data}"})
        # return data

        # -- Google AI API --

        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={googleai_key}'
        body = {"contents":[{"parts":[{"text":f"{messages}"}]}]}
        response = requests.post(url, json=body)
        data = json.loads(response.text).get('candidates')[0].get('content').get('parts')[0].get('text')
        messages.append({"role": "assistant", "content": f"{data}"})
        return data
