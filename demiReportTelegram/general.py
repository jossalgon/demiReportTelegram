# -*- encoding: utf-8 -*-
import os
import random

import sys

from demiReportTelegram import variables

admin_id = variables.admin_id
group_id = variables.group_id


def purger(bot, update):
    message = update.message
    if len(variables.new_members) == 0:
        bot.send_message(message.chat_id, 'Nada que purgar', reply_to_message_id=message.message_id)
    for new_user in variables.new_members:
        bot.kick_chat_member(group_id, new_user)
        variables.new_members.remove(new_user)


def send_demigrante(bot, update):
    message = update.message
    chat_id = message.chat.id
    sel = random.randint(1, 22)
    resource = 'data/music/%s.ogg' % str(sel), 'rb'
    audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource), 'rb')
    bot.send_audio(chat_id, audio)
    audio.close()


def send_shh(bot, update):
    message = update.message
    chat_id = message.chat.id
    resource = 'data/voices/shh.ogg'
    audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource), 'rb')
    bot.send_audio(chat_id, audio)
    audio.close()


def send_alerta(bot, update):
    message = update.message
    chat_id = message.chat.id
    resource = 'data/voices/alerta.ogg'
    audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource), 'rb')
    bot.send_audio(chat_id, audio)
    audio.close()


def send_tq(bot, update):
    message = update.message
    chat_id = message.chat.id
    resource = 'data/voices/tq.ogg'
    audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource), 'rb')
    bot.send_audio(chat_id, audio)
    audio.close()


def send_disculpa(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id, 'Disculpa por equivocarme, pero no soy perfecto, soy humano y cometo errores; '
                              'lo siento, pero la vida no viene con instrucciones.')


def send_locura(bot, update):
    message = update.message
    chat_id = message.chat.id
    resource = 'data/voices/locura.ogg'
    audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource), 'rb')
    bot.send_document(chat_id, 'http://imgur.com/fk6eHuB.gif')
    bot.send_audio(chat_id, audio)
    audio.close()

def send_gritopokemon(bot, update):
    message = update.message
    chat_id = message.chat.id
    resource = 'data/voices/gritopokemon.ogg'
    audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource), 'rb')
    bot.send_audio(chat_id, audio)
    audio.close()

