# -*- encoding: utf-8 -*-

import datetime
import logging
import os
import sys
import random
import threading
import time

import pymysql
from reportTelegram import reports
from reportTelegram import utils

from demiReportTelegram import utils as demi_utils
from demiReportTelegram import variables

admin_id = variables.admin_id
group_id = variables.group_id
perros = variables.perros
nuke = variables.nuke

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
            cur.execute('SELECT UserId, Points FROM Ranking GROUP BY UserId, Points ORDER BY Points DESC LIMIT 10')
            rows = cur.fetchall()
            top = '🏆 Ranking:\n*1º - %s (%d ptos)*\n' % (utils.get_name(rows[0][0]), rows[0][1])
            for row, pos in zip(rows[1:], range(2, 11)):
                top += '%dº - %s (%d ptos)\n' % (pos, utils.get_name(row[0]), row[1])
            top += '\n🐺 Perros por %d ptos.\n☢ Nuke por %d ptos.' % (perros, nuke)
            return top
    except Exception:
        logger.error('Fatal error in get_ranking', exc_info=True)
    finally:
        if con:
            con.close()


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
                audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), 'data/nuke.ogg'),
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
                cuenta_all(bot)
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
    targets = []
    users = demi_utils.get_user_ids()
    users.remove(user_id)
    if len(users) >= 5:
        target = random.sample(range(len(users)), 5)
        for t in target[:5]:
            targets.append(users[t])
    else:
        targets = users
    for user_id in targets:
        thr1 = threading.Thread(target=reports.counter, args=(bot, utils.get_name(user_id), user_id))
        thr1.start()


def cuenta_all(bot):
    user_ids = demi_utils.get_user_ids()
    for user_id in user_ids:
        thr1 = threading.Thread(target=reports.counter, args=(bot, utils.get_name(user_id), user_id))
        thr1.start()


def change_group_photo_bot(bot, update):
    message = update.message
    try:
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, '🌀Procesando...')
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('photo.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
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
