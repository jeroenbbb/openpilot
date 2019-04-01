# this program is a simple Telegram connection
# it has to read actively if messages are sent to the bot because a hook is not possible

# You will find it at t.me/ScoozyBot.
# For a description of the Bot API, see this page: https://core.telegram.org/bots/api
# https://khashtamov.com/en/how-to-create-a-telegram-bot-using-python/


import sys
import json
import requests
import time
import urllib
import config


if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")
    
from common.params import Params

params = Params()
token = params.get("TelegramToken").decode().strip()
URL = "https://api.telegram.org/bot{}/".format(token)
print (token)

def get_url(url):
    
    content = "{\"result\": [], \"ok\": false}"
    try:
        # this line hangs after 500 request so use timeout and try/except
        response = requests.get(url, timeout=0.5)
        content = response.content.decode("utf8")
    except:
        pass
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_me():
    url = URL + "getme"
    js = get_json_from_url(url)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def handle_answer(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chatId = update["message"]["chat"]["id"]
        answer = generate_answer(text, chatId)
        send_message(answer, chatId)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


#def send_message(text, chat_id):
#    text = urllib.parse.quote_plus(text)
#    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
#    get_url(url)
    
def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)    


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def generate_answer(text, chat):
    global last_message
    
    answer = "Sorry, begrijp ik niet"
    text = text.lower()
    
    if text == "/start":
        answer = "Welkom bij de ScoozyBot. Met deze bot kun je je Scoozy monitoren en opdrachten geven."

    # user requests message content by typing message=xxxxx
    if text.find("message=") == 0:

        type = text[8:]
        print ("requesting ************************************ " + type)

        if last_message is not None:
            # send back the last message of the requested type
            if type in last_message:
                asnwer = last_message[type]
            
    if text.find("waar") > -1:
        answer = "Ik ben nu in de Platananlaan"
    
    return answer
    
def main():
    count = 0
    last_update_id = None
    print (get_me())
    while True:
        updates = get_updates(last_update_id)
        print (updates)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_answer(updates)
        time.sleep(2)
        print ("Sleep" + str(count))
        count = count + 1


if __name__ == '__main__':
    main()
