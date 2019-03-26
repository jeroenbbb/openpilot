# this program is a simple Telegram connection
# it has to read actively if messages are sent to the bot because a hook is not possible

# You will find it at t.me/ScoozyBot.
# For a description of the Bot API, see this page: https://core.telegram.org/bots/api
# https://khashtamov.com/en/how-to-create-a-telegram-bot-using-python/


import sys
import telepot
from time import sleep


if __name__ == "__main__":
    sys.path.append("/home/pi/openpilot")
    
from common.params import Params

params = Params()
token = params.get("TelegramToken").decode()

TelegramBot = telepot.Bot(token)
print (TelegramBot.getMe())
