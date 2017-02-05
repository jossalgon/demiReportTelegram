# -*- encoding: utf-8 -*-

import random

import variables

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
    audio = open('data/music/%s.ogg' % str(sel), 'rb')
    bot.send_audio(chat_id, audio)


def send_shh(bot, update):
    chat_id = update.message.chat.id
    audio = open('data/shh.ogg', 'rb')
    bot.send_audio(chat_id, audio)


def send_alerta(bot, update):
    chat_id = update.message.chat.id
    audio = open('data/alerta.ogg', 'rb')
    bot.send_audio(chat_id, audio)


def send_tq(bot, update):
    chat_id = update.message.chat.id
    audio = open('data/tq.ogg', 'rb')
    bot.send_audio(chat_id, audio)


def send_disculpa(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id, 'Disculpa por equivocarme, pero no soy perfecto, soy humano y cometo errores; '
                              'lo siento, pero la vida no viene con instrucciones.')
