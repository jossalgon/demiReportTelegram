# -*- encoding: utf-8 -*-

import random

import variables

bot = variables.bot
admin_id = variables.admin_id
group_id = variables.group_id


class General:
    def purger(self, message):
        if len(variables.new_members) == 0:
            bot.reply_to(message, 'Nada que purgar')
        for new_user in variables.new_members:
            bot.kick_chat_member(group_id, new_user)
            variables.new_members.remove(new_user)

    def talk(self, message):
        text = message.text[6::]
        bot.send_message(group_id, text)

    def send_demigrante(self, message):
        try:
            chat_id = message.chat.id
            sel = random.randint(1, 22)
            audio = open('data/music/%s.ogg' % str(sel), 'rb')
            bot.send_audio(chat_id, audio)
        except Exception as exception:
            bot.send_message(admin_id, exception)

    def send_shh(self, message):
        chat_id = message.chat.id
        audio = open('data/shh.ogg', 'rb')
        bot.send_audio(chat_id, audio)

    def send_alerta(self, message):
        chat_id = message.chat.id
        audio = open('data/alerta.ogg', 'rb')
        bot.send_audio(chat_id, audio)

    def send_tq(self, message):
        chat_id = message.chat.id
        audio = open('data/tq.ogg', 'rb')
        bot.send_audio(chat_id, audio)

    def send_disculpa(self, message):
        bot.send_message(message.chat.id,
                         'Disculpa por equivocarme, pero no soy perfecto, soy humano y cometo errores; lo siento, pero la vida no viene con instrucciones.')
