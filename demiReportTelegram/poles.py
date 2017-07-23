# -*- encoding: utf-8 -*-
import pkgutil
import threading

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from telegram.ext.dispatcher import run_async
import datetime
import logging
import os
import sys
import random
import time
import io

import pymysql
from reportTelegram import reports
from reportTelegram import utils

from demiReportTelegram import utils as demi_utils
from demiReportTelegram import variables

admin_id = variables.admin_id
group_id = variables.group_id
perros = variables.perros
nuke = variables.nuke
HEADSHOT = variables.HEADSHOT

DB_HOST = variables.DB_HOST
DB_USER = variables.DB_USER
DB_PASS = variables.DB_PASS
DB_NAME = variables.DB_NAME

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def pole_handler(user_id):
    poles = variables.poles
    is_saturday = (datetime.datetime.today().weekday() == 5)
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            if user_id in poles:
                cur.execute('UPDATE Ranking SET Points = Points - 3 WHERE UserId = %s', (str(user_id),))
                return 'No eres el centro del mundo sabes? (-3 ptos)'
            elif len(poles) == 0:
                text = 'Pole conseguida! (+3 ptos)'
                variables.add_member_to_poles(user_id, 0)
                cur.execute('UPDATE Ranking SET Points = Points + 3 WHERE UserId = %s', (str(user_id),))
                if is_saturday:
                    text = '\n\nVete con tu foto a chuparla a jugar al LoL\n' \
                           + '💝(Enviame la foto por privado)'
                return text
            else:
                cur.execute('UPDATE Ranking SET Points = Points - 1 WHERE UserId = %s', (str(user_id),))
                return 'FAIL!!! (-1 ptos)'
    except Exception:
        logger.error('Fatal error in pole_handler', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def subpole_handler(user_id):
    poles = variables.poles
    is_saturday = (datetime.datetime.today().weekday() == 5)
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            if user_id in poles:
                cur.execute('UPDATE Ranking SET Points = Points - 3 WHERE UserId = %s', (str(user_id),))
                return 'No eres el centro del mundo sabes?  (-3 ptos)'
            elif len(poles) == 1:
                text = 'Más vale subpole en mano que cien en tu ano! (+2 ptos)'
                variables.add_member_to_poles(user_id, 1)
                cur.execute('UPDATE Ranking SET Points = Points + 2 WHERE UserId = %s', (str(user_id),))
                if is_saturday:
                    text = text + '\n\nVete con tu nombre a chuparla a jugar al LoL\n' \
                           + '💝(Escríbeme un nombre para el grupo por privado)'
                return text
            else:
                cur.execute('UPDATE Ranking SET Points = Points - 1 WHERE UserId = %s', (str(user_id),))
                return 'FAIL!!! (-1 ptos)'
    except Exception:
        logger.error('Fatal error in subpole_handler', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def tercercomentario_handler(user_id):
    poles = variables.poles
    is_saturday = (datetime.datetime.today().weekday() == 5)
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            if user_id in poles:
                cur.execute('UPDATE Ranking SET Points = Points - 3 WHERE UserId = %s', (str(user_id),))
                return 'No eres el centro del mundo sabes? (-3 ptos)'
            elif len(poles) == 2:
                text = 'Larga vida al tercer comentario! (+1 ptos)'
                variables.add_member_to_poles(user_id, 2)
                cur.execute('UPDATE Ranking SET Points = Points + 1 WHERE UserId = %s', (str(user_id),))
                if is_saturday:
                    text = text + '\n\nVete con tu nombre a chuparla a jugar al LoL\n' \
                           + '💝(Escríbeme un nombre para el grupo por privado)'
                return text
            else:
                cur.execute('UPDATE Ranking SET Points = Points - 1 WHERE UserId = %s', (str(user_id),))
                return 'FAIL!!! (-1 ptos)'
    except Exception:
        logger.error('Fatal error in tercercomentario_handler', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def get_ranking():
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute('SELECT UserId, Points FROM Ranking GROUP BY UserId, Points ORDER BY Points DESC')
            rows = cur.fetchall()
            top = '🏆 Ranking:\n*1º - %s (%d ptos)*\n' % (utils.get_name(rows[0][0]), rows[0][1])
            for row, pos in zip(rows[1:], range(2, len(rows)+1)):
                top += '%dº - %s (%d ptos)\n' % (pos, utils.get_name(row[0]), row[1])
            top += '\n🎯 Headshot por %d ptos.\n🐺 Perros por %d ptos.\n☢ Nuke por %d ptos.' % (HEADSHOT, perros, nuke)
            return top
    except Exception:
        logger.error('Fatal error in get_ranking', exc_info=True)
    finally:
        if con:
            con.close()


@run_async
def send_nuke(bot, update):
    message = update.message
    user_id = message.from_user.id
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
            user_points = cur.fetchone()[0]
            if user_points >= nuke:
                cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s', (str(nuke), str(user_id)))
                bot.send_document(group_id, 'http://imgur.com/vZDxkFk.gif')
                audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), 'data/voices/nuke.ogg'),
                             'rb')
                bot.send_audio(group_id, audio)
                bot.send_message(message.chat_id, 'ORDEN RECIBIDA nuke EN 15 SEG.',
                                 reply_to_message_id=message.message_id)
                time.sleep(5)
                bot.send_message(group_id, 'nuke EN 10 SEG.')
                time.sleep(5)
                for i in range(5, 0, -1):
                    bot.send_message(group_id, 'nuke EN %d SEG.' % i)
                    time.sleep(1)
                user_ids = demi_utils.get_user_ids()
                cuenta_all(bot, user_ids)
            else:
                bot.send_message(message.chat_id,
                                 'No tienes puntos suficientes, te faltan %d ptos.' % (nuke - user_points),
                                 reply_to_message_id=message.message_id)
    except Exception:
        logger.error('Fatal error in send_nuke', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()

@run_async
def send_perros(bot, update):
    message = update.message
    user_id = message.from_user.id
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
            user_points = cur.fetchone()[0]
            if user_points >= perros:
                cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s',
                            (str(perros), str(user_id)))
                bot.send_document(group_id, 'http://imgur.com/buULxjj.gif')
                bot.send_message(message.chat_id, 'ORDEN RECIBIDA lanzando perros',
                                 reply_to_message_id=message.message_id)
                msg = bot.send_message(group_id, 'perros EN *5 SEG.*', parse_mode='Markdown')
                for i in range(4, -1, -1):
                    time.sleep(1)
                    text = 'perros EN *%d SEG.*' % i
                    bot.edit_message_text(text, chat_id=group_id, message_id=msg.message_id, parse_mode='Markdown')
                cuenta_perros(bot, user_id)
            else:
                bot.send_message(message.chat_id,
                                 'No tienes puntos suficientes, te faltan %d ptos.' % (perros - user_points),
                                 reply_to_message_id=message.message_id)
    except Exception:
        logger.error('Fatal error in send_perros', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def cuenta_perros(bot, user_id):
    targets = list()
    user_ids = demi_utils.get_user_ids()
    user_ids.remove(user_id)
    if len(user_ids) >= 5:
        samples = random.sample(range(len(user_ids)), 5)
        for t in samples:
            targets.append(user_ids[t])
        cuenta_all(bot, targets)
    else:
        cuenta_all(bot, user_ids)


@run_async
def pre_headshot(bot, update):
    message = update.message
    names = utils.get_names()
    reply_keyboard = [names[i:i + 3] for i in range(0, len(names), 3)]
    if check_headshot(bot, update):
        bot.send_message(message.chat_id, '🎯 HEADSHOT A ...\n\nO /cancel para cancelar el tiro',
                         reply_to_message_id=message.message_id,
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, selective=True))
        return 0
    else:
        return ConversationHandler.END


def check_headshot(bot, update):
    message = update.message
    user_id = message.from_user.id
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
            user_points = cur.fetchone()[0]
            if user_points < HEADSHOT:
                bot.send_message(message.chat_id,
                                 'No tienes puntos suficientes, te faltan %d ptos.' % (HEADSHOT - user_points),
                                 reply_to_message_id=message.message_id,
                                 reply_markup=ReplyKeyboardRemove(selective=True))
                return False
            else:
                return True
    except Exception:
        logger.error('Fatal error in check_headshot', exc_info=True)
        return False
    finally:
        if con:
            con.close()


@run_async
def headshot(bot, update):
    message = update.message
    user_id = message.from_user.id
    name = update.message.text
    reported = utils.get_user_id(name)
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)

    if not check_headshot(bot, update):
        return ConversationHandler.END
    try:
        resource = 'data/gifs/headshots/%s.mp4' % str(reported)
        gif_path = os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource)
        if os.path.isfile(gif_path):
            gif1, gif2 = open(gif_path, 'rb'), open(gif_path, 'rb')
        else:
            gif1 = gif2 = 'https://media.giphy.com/media/3N2ML3tw4c4uc/giphy.gif'

        with con.cursor() as cur:
            cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s',
                        (str(HEADSHOT), str(user_id)))

        bot.send_document(group_id, gif1, reply_markup=ReplyKeyboardRemove(selective=True))
        if message.chat.type == 'private':
            bot.send_document(user_id, gif2, reply_markup=ReplyKeyboardRemove(selective=True))
        if not isinstance(gif1, str):
            gif1.close()
            gif2.close()
        thr1 = threading.Thread(target=reports.counter, args=(bot, name, reported))
        thr1.start()
    except Exception:
        logger.error('Fatal error in headshot', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()
        return ConversationHandler.END


@run_async
def cuenta_all(bot, user_ids):

    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    for user_id in user_ids:
        try:
            ban_time = reports.variables.ban_time
            sti = io.BufferedReader(io.BytesIO(pkgutil.get_data('reportTelegram', 'data/stickers/%s.webp' % reports.variables.sticker)))
            bot.send_sticker(user_id, sti)
            sti.close()
            m, s = divmod(ban_time, 60)
            text = 'Expulsado durante %02d:%02d minutos\n\n⚠️Esto no es un **** contador⚠' % (m, s)
            bot.send_message(user_id, text)
            bot.kick_chat_member(group_id, user_id)
        except:
            logger.error('Fatal error in cuenta_all kicks', exc_info=True)
    time.sleep(reports.variables.ban_time)
    for user_id in user_ids:
        try:
            bot.unban_chat_member(group_id, user_id)
            with con.cursor() as cur:
                cur.execute('DELETE FROM Reports WHERE Reported = %s', (str(user_id),))
                cur.execute('UPDATE Flamers SET Kicks = Kicks + 1 WHERE UserId = %s', (str(user_id),))
            button = InlineKeyboardButton('Invitación', url=variables.link)
            markup = InlineKeyboardMarkup([[button]])
            bot.send_message(user_id, 'Ya puedes entrar %s, usa esta invitación:' % utils.get_name(user_id), reply_markup=markup)
        except:
            logger.error('Fatal error in cuenta_all unban', exc_info=True)
    if con:
        con.commit()
        con.close()


def change_group_photo_bot(bot, update):
    message = update.message
    try:
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, '🌀Procesando...')
        photo_file = bot.getFile(message.photo[-1].file_id)
        photo_file.download('photo.jpg')
        demi_utils.change_group_photo()
        bot.edit_message_text('✅ Foto cambiada', chat_id=chat_id, message_id=msg.message_id)
    except Exception:
        logger.error('Fatal error in change_group_photo_bot', exc_info=True)


def change_group_name_bot(bot, update):
    message = update.message
    group_name = ''
    poles = variables.poles
    user_id = message.from_user.id
    position = poles.index(user_id) + 1
    name = message.text
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, '🌀Procesando...')

    if len(name) > 30:
        bot.send_message(chat_id, 'Aviso ese nombre es mu largo acho', reply_to_message_id=message.message_id)
        name = name[:30]

    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute('UPDATE GroupNames SET groupName = %s  WHERE position = %s', (str(name), str(position)))
            cur.execute('SELECT groupName FROM GroupNames')
            rows = cur.fetchall()
            for i, row in enumerate(rows):
                if i <= 1:
                    group_name += '%s - ' % row[0]
                else:
                    group_name += row[0]
            demi_utils.change_group_name(group_name)
            bot.edit_message_text('✅ Nombre cambiado', chat_id=chat_id, message_id=msg.message_id)
    except Exception:
        logger.error('Fatal error in change_group_name_bot', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()
