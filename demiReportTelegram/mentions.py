# -*- encoding: utf-8 -*-
from telegram import Chat
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
import logging
import re

import pymysql
from reportTelegram import utils

from demiReportTelegram import utils as demi_utils
from demiReportTelegram import variables

admin_id = variables.admin_id
group_id = variables.group_id

DB_HOST = variables.DB_HOST
DB_USER = variables.DB_USER
DB_PASS = variables.DB_PASS
DB_NAME = variables.DB_NAME

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def set_troll(target):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:

            trolls = demi_utils.get_trolls()
            if not utils.is_from_group(target):
                return 'User_id incorrecto'
            elif target in trolls:
                username = utils.get_name(target)
                cur.execute('DELETE FROM Trolls WHERE UserId = %s', (str(target),))
                return '❤️ %s eliminado de la lista de trolls' % username
            else:
                username = utils.get_name(target)
                cur.execute('INSERT INTO Trolls VALUES(%s)', (str(target),))
                return '💔 %s añadido a la lista de trolls' % username
    except Exception:
        logger.error('Fatal error in set_troll', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def mention_handler(bot, message):
    usernames = demi_utils.get_usernames(bot)
    mentions = re.findall(r'@\w+', message.text)
    user_ids = demi_utils.get_user_ids()
    silent_todos = demi_utils.get_not_mention('TODOS')
    silent_menciones = demi_utils.get_not_mention('MENCIONES')
    silent_pipas = demi_utils.get_not_mention('PIPAS')

    if message.from_user.id in demi_utils.get_trolls():
        return False

    for mention in mentions:
        mention = mention.lower()
        if mention in usernames:
            if usernames[mention] not in silent_menciones:
                bot.forward_message(usernames[mention], group_id, message.message_id)
    if bool(re.match(r'(?i).*@todos.*', message.text)):
        for user_id in user_ids:
            if user_id not in silent_todos:
                bot.forward_message(user_id, group_id, message.message_id)
    if bool(re.match(r'(?i).*@pipas.*', message.text)):
        event_id = str(message.message_id)
        text = re.subn(r'(?i) ?@pipas ?', '', message.text)[0].capitalize()
        demi_utils.create_event(event_id=event_id, message_id=message.message_id, text=text)

        keyboard = [[InlineKeyboardButton("Sí", callback_data='0_%s' % event_id),
                     InlineKeyboardButton("No", callback_data='1_%s' % event_id)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        for user_id in user_ids:
            if user_id not in silent_pipas:
                msg = bot.forward_message(user_id, group_id, message.message_id, reply_markup=reply_markup)
                bot.send_message(user_id, '¿Sales?‎', reply_markup=reply_markup, reply_to_message_id=msg.message_id)


def callback_query_handler(bot, update, user_data, job_queue):
    query_data = update.callback_query.data
    if query_data.startswith('MENTION'):
        post_mention_control(bot, update, user_data, job_queue)
    else:
        pipas_selected(bot, update, user_data, job_queue)


def pipas_selected(bot, update, user_data, job_queue):
    query = update.callback_query
    query_data = query.data.split('_')
    query_selected = int(query_data[0])
    event_id = str(query_data[1])
    user_id = query.from_user.id

    if demi_utils.get_vote(event_id, user_id) == query_selected:
        bot.answer_callback_query(query.id, 'Ya has votado esa opción')
        return False
    elif demi_utils.flooder(user_data, job_queue):
        bot.answer_callback_query(query.id, 'Has realizado demasiados votos')
        return False

    if int(event_id) not in demi_utils.get_events():
        bot.edit_message_text(text="Quedada terminada",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return False

    if query_selected == 0:
        selected = 'Sí'
    else:
        selected = 'No'

    bot.edit_message_text(text="Has elegido: %s" % selected,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    keyboard = [[InlineKeyboardButton("Sí", callback_data='0_%s' % event_id),
                 InlineKeyboardButton("No", callback_data='1_%s' % event_id)]]
    keyboard[0][query_selected].text = '[%s]' % selected

    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_reply_markup(reply_markup=reply_markup, chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
    if query_selected == 0:
        bot.send_message(group_id, '¡%s sale!' % utils.get_name(user_id),
                         reply_to_message_id=demi_utils.get_event_message_id(event_id))
    elif query_selected == 1 and demi_utils.get_vote(event_id, user_id) == 0:
        bot.send_message(group_id, '¡%s hace achu achu!' % utils.get_name(user_id),
                         reply_to_message_id=demi_utils.get_event_message_id(event_id))

    demi_utils.add_participant_event(event_id, user_id, query_selected)
    bot.answer_callback_query(query.id, 'Votado correctamente')


def who_pipas(bot, update):
    message = update.message
    res = demi_utils.get_who_pipas()
    bot.send_message(message.chat.id, res, parse_mode='Markdown')


def recover_pipas(bot, update):
    message = update.message
    user_id = message.from_user.id

    if message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        message.reply_text('Tienes MP')

    for event_id in demi_utils.get_events():
        keyboard = [[InlineKeyboardButton("Sí", callback_data='0_%s' % event_id),
                     InlineKeyboardButton("No", callback_data='1_%s' % event_id)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = bot.forward_message(user_id, group_id, event_id, reply_markup=reply_markup)
        bot.send_message(user_id, '¿Sales?‎', reply_markup=reply_markup, reply_to_message_id=msg.message_id)


def mention_control(bot, update, message_edited_id=None):
    message = update.message
    user_id = message.from_user.id if message_edited_id is None else update.callback_query.from_user.id

    is_silent_todos = demi_utils.is_silent_user(user_id, 'TODOS')
    is_silent_pipas = demi_utils.is_silent_user(user_id, 'PIPAS')
    is_silent_menciones = demi_utils.is_silent_user(user_id, 'MENCIONES')

    text_button1 = '❌@Todos desactivado' if is_silent_todos else '✔@Todos activado'
    text_button2 = '❌@Pipas desactivado' if is_silent_pipas else '✔️@Pipas activado'
    text_button3 = '❌Menciones desactivadas' if is_silent_menciones else '✔Menciones activadas'

    keyboard = [[InlineKeyboardButton(text_button1, callback_data='MENTION_TODOS_%i' % int(not is_silent_todos)),
                 InlineKeyboardButton(text_button2, callback_data='MENTION_PIPAS_%i' % int(not is_silent_pipas))],
                [InlineKeyboardButton(text_button3, callback_data='MENTION_MENCIONES_%i' % int(not is_silent_menciones))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if message_edited_id:
        bot.edit_message_reply_markup(reply_markup=reply_markup, chat_id=user_id, message_id=message_edited_id)
    else:
        if message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            message.reply_text('Tienes MP')

        bot.send_message(user_id, '📢 Menciones\n\n¿Qué avisos quieres?‎', reply_markup=reply_markup)


def post_mention_control(bot, update, user_data, job_queue):
    query = update.callback_query
    query_data = query.data.split('_')
    mention_type = str(query_data[1])
    silent = bool(int(query_data[2]))

    demi_utils.mention_control(query.from_user.id, mention_type, silent)
    text = mention_type.lower().capitalize()
    text += ' desactivado' if silent else ' activado'
    bot.answer_callback_query(query.id, text)
    mention_control(bot, update, message_edited_id=query.message.message_id)
