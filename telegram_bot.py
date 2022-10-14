import requests
import os
from dotenv import load_dotenv

load_dotenv()   # initializing env vars from .env file
    
def send_to_telegram(message):
    ''' Send message to a user/group using user/group's chat id and api token of your bot '''
    if message == None:
        return
    api = os.environ.get('api')
    chat_id = os.environ.get('chat_id')
    apiURL = f'https://api.telegram.org/bot{api}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chat_id, 'text': message})
        print("Sending to telegram: {}".format(response.status_code))
    except Exception as e:
        print(e)
