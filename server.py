import json
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}

@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return jsonify(response)

def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'animal_to_buy': 'слона', # Начинаем с предложения купить слона
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {sessionStorage[user_id]["animal_to_buy"]}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю'
    ]:
        # Пользователь согласился, предлагаем купить следующего животного
        if sessionStorage[user_id]["animal_to_buy"] == 'слона':
            sessionStorage[user_id]["animal_to_buy"] = 'кролика'  # Теперь предлагаем кролика
            res['response']['text'] = 'Отлично! Слона можно найти на Яндекс.Маркете! А теперь купи кролика!'
            res['response']['buttons'] = get_suggests(user_id)  # Обновляем подсказки
            return
        elif sessionStorage[user_id]["animal_to_buy"] == 'кролика':
            res['response']['text'] = 'Замечательно! Кролика можно найти на Яндекс.Маркете! Приходи ещё!'
            res['response']['end_session'] = True #заканчиваем сессию.
            return

    # Если нет, то убеждаем его купить животное!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {sessionStorage[user_id]['animal_to_buy']}!"
    res['response']['buttons'] = get_suggests(user_id)

def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=" + session['animal_to_buy'],
            "hide": True
        })

    return suggests

if __name__ == '__main__':
    app.run()