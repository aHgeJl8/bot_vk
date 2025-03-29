import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import random
import re
import time
from collections import defaultdict

def clean_text(text):
    """Очистка текста сообщения"""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text.lower()

def load_qa_database(file_path='qa.json'):
    """Загрузка базы вопросов-ответов"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            # Создаем индекс для поиска по всем словам
            data['word_index'] = defaultdict(list)
            for phrase in data['questions']:
                words = phrase.split()
                for word in words:
                    data['word_index'][word].append(phrase)
            
            return data
    except FileNotFoundError:
        return {'questions': {}, 'unknown_responses': ["Не понимаю вас"], 'word_index': defaultdict(list)}
    except json.JSONDecodeError:
        print("Ошибка: Неверный формат JSON файла.")
        return {'questions': {}, 'unknown_responses': ["Ошибка в базе данных"], 'word_index': defaultdict(list)}

def find_partial_matches(text, qa_db):
    """Находит все фразы, где хотя бы одно слово совпадает"""
    cleaned_text = clean_text(text)
    words = cleaned_text.split()
    
    if not words:
        return []
    
    # Находим все фразы, содержащие хотя бы одно слово из запроса
    matches = []
    for word in words:
        if word in qa_db['word_index']:
            matches.extend(qa_db['word_index'][word])
    
    # Удаляем дубликаты
    return list(set(matches))

def get_answer(text, qa_db):
    """Получение ответа со случайным выбором при частичном совпадении"""
    cleaned_text = clean_text(text)
    
    # 1. Проверяем точное совпадение
    if cleaned_text in qa_db['questions']:
        answer = qa_db['questions'][cleaned_text]
        return random.choice(answer) if isinstance(answer, list) else answer
    
    # 2. Ищем частичные совпадения
    partial_matches = find_partial_matches(text, qa_db)
    
    if not partial_matches:
        return random.choice(qa_db['unknown_responses'])
    
    # 3. Выбираем случайную подходящую фразу
    random_phrase = random.choice(partial_matches)
    answer = qa_db['questions'][random_phrase]
    return random.choice(answer) if isinstance(answer, list) else answer

def generate_random_id():
    """Генерация random_id"""
    return int(time.time() * 1000)

def vk_bot(token, group_id):
    """Основная функция бота"""
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_id)
    vk = vk_session.get_api()
    
    qa_db = load_qa_database()
    print("Бот запущен и готов к работе...")
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            msg = event.object.message
            user_id = msg['from_id']
            text = msg['text']
            
            answer = get_answer(text, qa_db)
            random_id = generate_random_id()
            
            vk.messages.send(
                user_id=user_id,
                message=answer,
                random_id=random_id
            )

if __name__ == "__main__":
    GROUP_ID = '229899982'
    TOKEN = 'vk1.a.B8syLSdGNoenTEg5MydclnHmi2K3p8-7vIOSbu577vMSYa5ltpxF67Zddm7eHOm4RLOGDmuygUTkiNb3KZVImwbpRVMkFron1Bstx67gea_lDlFLd0W_H1V44rm439rX4JRHU1M_cj9UKkr4H9AVPqPGGo64toOscDn0j7ud7LhHKirgXvUUP2ZC_61Ka8DiWT7HtoxctNG-yHw9mxwHzg'
    vk_bot(TOKEN, GROUP_ID)