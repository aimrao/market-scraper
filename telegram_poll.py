from telegram_bot import *
from scrape import *

def poll_telegram():
    api = os.environ.get('api')
    chat_id = os.environ.get('chat_id')
    apiURL = f'https://api.telegram.org/bot{api}/getUpdates'
    try:
        response = requests.get(apiURL, json={'offset':-1})
        message_data = response.json().get('result')[0].get('message')
        last_message = message_data.get('text')
        if same_msg(message_data.get('message_id')):
            if last_message.lower()=='scrape':
                scrape(scrape_interval=5, scrape_duration=1, timezone=india)
    except Exception as e:
        print(e)
