import requests
import os, time, json
from dotenv import load_dotenv
from galaxy_battery_status import check_battery_status

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

def same_msg(message_id):
    try:
        with open('data/last_message_id','r') as f:
            last_message_id = int(f.readline())
    except:
        f = open('data/last_message_id','x')
        f.close()
        last_message_id = -1
    if message_id == last_message_id:
        return False
    else:
        with open('data/last_message_id','w') as f:
            f.write(str(message_id))
    return True

def poll_telegram():
    api = os.environ.get('api')
    chat_id = os.environ.get('chat_id')
    apiURL = f'https://api.telegram.org/bot{api}/getUpdates'
    try:
        response = requests.get(apiURL, json={'offset':-1})
        message_data = response.json().get('result')[0].get('message')
        last_message = message_data.get('text')
        if same_msg(message_data.get('message_id')):
            if last_message.lower()=='battery':
                send_to_telegram(check_battery_status())
    except Exception as e:
        print(e)
