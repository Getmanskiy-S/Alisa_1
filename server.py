import json
import logging
from flask import Flask, request, jsonify
from geo import get_geo_info, get_distance

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

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
    handle_dialog(response, request.json)
    logging.info(f'Response:  {response!r}')
    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Знакомимся с пользователем
        res['response']['text'] = 'Привет! Как тебя зовут?'
        sessionStorage[user_id] = {'first_name': None}  # Инициализируем хранилище для пользователя
        return

    if sessionStorage[user_id]['first_name'] is None:
        # Получаем имя пользователя
        first_name = get_first_name(req)
        if first_name:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = f'Приятно познакомиться, {first_name}! Я могу показать город или сказать расстояние между городами!'
            return
        else:
            res['response']['text'] = 'Не расслышала! Повтори, пожалуйста, как тебя зовут?'
            return

    # Далее навык должен во всех сообщениях обращаться к пользователю по имени
    first_name = sessionStorage[user_id]['first_name']

    # Получаем города из запроса
    cities = get_cities(req)
    if not cities:
        res['response']['text'] = f'{first_name}, ты не написал название ни одного города!'
    elif len(cities) == 1:
        country = get_geo_info(cities[0], 'country')
        if country:
            res['response']['text'] = f'{first_name}, этот город в стране - {country}'
        else:
            res['response']['text'] = f'{first_name}, не удалось определить страну для города {cities[0]}.'
    elif len(cities) == 2:
        coord1 = get_geo_info(cities[0], 'coordinates')
        coord2 = get_geo_info(cities[1], 'coordinates')
        if coord1 and coord2:
            distance = get_distance(coord1, coord2)
            res['response']['text'] = f'{first_name}, расстояние между этими городами: {str(round(distance))} км.'
        else:
            res['response']['text'] = f'{first_name}, не удалось определить координаты для городов.'
    else:
        res['response']['text'] = f'{first_name}, слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            if entity['value'].get('first_name'):
                return entity['value']['first_name']

    return None


if __name__ == '__main__':
    app.run()
