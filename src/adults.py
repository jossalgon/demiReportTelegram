import requests

import variables
from src.utils import Utils

utils = Utils()

bot = variables.bot
admin_id = variables.admin_id
group_id = variables.group_id


class Adults:
    def stop_18(self, message):
        variables.porn = False
        bot.reply_to(message, 'Cesen con las pajas')

    def start_18(self, message):
        variables.porn = True
        bot.reply_to(message, 'Delen a las pajas')

    def send_butts(self, message, attempt=0):
        try:
            r = requests.get('http://api.obutts.ru/noise/1')
            data = r.json()[0]
            if not data and attempt <= 3:
                self.send_butts(message, attempt + 1)
            photo = 'http://media.obutts.ru/' + data['preview']
            bot.send_photo(message.chat.id, photo)
        except Exception as exception:
            bot.reply_to(message, 'Algo no fue bien :(')

    def send_boobs(self, message, attempt=0):
        try:
            r = requests.get('http://api.oboobs.ru/noise/1')
            data = r.json()[0]
            if not data and attempt <= 3:
                self.send_boobs(message, attempt + 1)
            photo = 'http://media.oboobs.ru/' + data['preview']
            bot.send_photo(message.chat.id, photo)
        except Exception as exception:
            bot.reply_to(message, 'Algo no fue bien :(')
