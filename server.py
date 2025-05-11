import json
import logging
from flask import Flask, request, jsonify
from googletrans import Translator

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

translator = Translator()


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
    text = req['request']['command'].lower()  # Получаем текст запроса пользователя

    if 'переведи слово:' in text or 'переведите слово:' in text:
        try:
            word_to_translate = text.split(':')[-1].strip()  # Извлекаем слово для перевода
            translation = translator.translate(word_to_translate, dest='en')  # Переводим на английский

            res['response']['text'] = translation.text  # Возвращаем перевод
        except Exception as e:
            res['response']['text'] = f"Произошла ошибка при переводе: {e}"  # Обрабатываем ошибки
    else:
        res['response']['text'] = "Я понимаю только запросы на перевод слова.  Например: 'Переведи слово: стакан'"


if __name__ == '__main__':
    app.run()
