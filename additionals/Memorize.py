import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_pass = os.getenv('MONGO_PASSWORD')

def memorize(messages: list, save_foldername: str, suffix: int, char: str, guild_id: str):
    os.makedirs(save_foldername, exist_ok=True)
    base_filename = 'conversation'
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.json')
    
    with open(filename, 'w') as file:
        json.dump(messages, file, indent=4, ensure_ascii=False)

    try:
        client = MongoClient()
        client = MongoClient(f"mongodb+srv://admin:{mongo_pass}@cluster0.en0sd6t.mongodb.net/")
        conver_db = client[f'conver_db']    

        post = None
        with open(filename, "r", encoding='utf-8') as file:
            post = json.load(file)

        char_db = conver_db[f'{char}']
        char_db.insert_many(post)

    except Exception as e:
        print(e)
        return