import json
import os

def memorize(messages: list, save_foldername: str, suffix: int):
    os.makedirs(save_foldername, exist_ok=True)
    base_filename = 'conversation'
    filename = os.path.join(save_foldername, f'{base_filename}_{suffix}.txt')
    with open(filename, 'w', encoding = 'utf-8') as file:
        json.dump(messages, file, indent=4, ensure_ascii=False)