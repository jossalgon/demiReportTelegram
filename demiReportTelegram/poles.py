# -*- encoding: utf-8 -*-
import pkgutil
import threading

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from telegram.ext.dispatcher import run_async
from telegram.error import TimedOut
import datetime
import logging
import os
import sys
import random
import time
import io

from reportTelegram import reports
from reportTelegram import utils
from reportTelegram import variables as report_variables

from demiReportTelegram import utils as demi_utils
from demiReportTelegram import variables

admin_id = variables.admin_id
group_id = variables.group_id
PERROS = variables.perros
NUKE = variables.nuke
HEADSHOT = variables.HEADSHOT
DUELO = variables.DUELO
MUTE = variables.MUTE

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def pole_handler(user_id):
    poles = variables.poles
    is_saturday = (datetime.datetime.today().weekday() == 5)
    con = demi_utils.create_connection()
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
    con = demi_utils.create_connection()
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
    con = demi_utils.create_connection()
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
    con = demi_utils.create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT UserId, Points FROM Ranking GROUP BY UserId, Points ORDER BY Points DESC')
            rows = cur.fetchall()
            top = '🏆 Ranking:\n*1º - %s (%d ptos)*\n' % (utils.get_name(rows[0][0]), rows[0][1])
            for row, pos in zip(rows[1:], range(2, len(rows)+1)):
                top += '%dº - %s (%d ptos)\n' % (pos, utils.get_name(row[0]), row[1])
            top += '\n🔫 Duelo por %d ptos.\n🤐 Mute por %d ptos.\n🎯 Headshot por %d ptos.\n🐺 Perros por %d ptos.\n☢ Nuke por %d ptos.' % \
                   (DUELO, MUTE, HEADSHOT, PERROS, NUKE)
            return top
    except Exception:
        logger.error('Fatal error in get_ranking', exc_info=True)
    finally:
        if con:
            con.close()


def get_ranking_gasta_puntos():
    con = demi_utils.create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT UserId, Veces FROM Usos GROUP BY UserId, Veces ORDER BY Veces DESC')
            rows = cur.fetchall()
            if rows[0][1] == 0:
                top = '💸 Ranking puntos gastados:\n*1º - %s (%d ptos)*\n' % (utils.get_name(rows[0][0]), rows[0][1])
            else:
                top = '💸 Ranking puntos gastados:\n*1º - %s (-%d ptos)*\n' % (utils.get_name(rows[0][0]), rows[0][1])
            for row, pos in zip(rows[1:], range(2, len(rows)+1)):
                if row[1] == 0:
                    top += '%dº - %s (%d ptos)\n' % (pos, utils.get_name(row[0]), row[1])
                else:
                    top += '%dº - %s (-%d ptos)\n' % (pos, utils.get_name(row[0]), row[1])
            return top
    except Exception:
        logger.error('Fatal error in get_ranking_gasta_puntos', exc_info=True)
    finally:
        if con:
            con.close()


@run_async
def send_nuke(bot, update):
    message = update.message
    user_id = message.from_user.id
    con = demi_utils.create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
            user_points = cur.fetchone()[0]
            if user_points >= NUKE:
                cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s', (str(NUKE), str(user_id)))
                cur.execute('UPDATE Usos SET Veces = Veces + %s WHERE UserId = %s', (str(NUKE), str(user_id)))
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
                                 'No tienes puntos suficientes, te faltan %d ptos.' % (NUKE - user_points),
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
    con = demi_utils.create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
            user_points = cur.fetchone()[0]
            if user_points >= PERROS:
                cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s',
                            (str(PERROS), str(user_id)))
                cur.execute('UPDATE Usos SET Veces = Veces + %s WHERE UserId = %s', (str(PERROS), str(user_id)))
                cuenta_perros(bot, user_id, message)
            else:
                bot.send_message(message.chat_id,
                                 'No tienes puntos suficientes, te faltan %d ptos.' % (PERROS - user_points),
                                 reply_to_message_id=message.message_id)
    except Exception:
        logger.error('Fatal error in send_perros', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


@run_async
def cuenta_perros(bot, user_id=None, message=None):
    bot.send_document(group_id, 'http://imgur.com/buULxjj.gif')
    if message:
        bot.send_message(message.chat_id, 'ORDEN RECIBIDA lanzando perros',
                         reply_to_message_id=message.message_id)
    msg = bot.send_message(group_id, 'Perros fachas EN *5 SEG.*', parse_mode='Markdown')
    time.sleep(1)
    for i in range(4, -1, -1):
        text = 'Perros fachas EN *%d SEG.*' % i
        try:
            bot.edit_message_text(text, chat_id=group_id, message_id=msg.message_id, parse_mode='Markdown')
            time.sleep(1)
        except TimedOut:
            pass
    perros(bot, user_id)


@run_async
def perros(bot, user_id=None):
    targets = list()
    user_ids = [user_id for user_id in demi_utils.get_user_ids() if bot.get_chat_member(group_id, user_id).status != 'kicked']
    if user_id:
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
    if check_points(bot, update, HEADSHOT):
        bot.send_message(message.chat_id, '🎯 HEADSHOT A ...\n\nO /cancel para cancelar el tiro',
                         reply_to_message_id=message.message_id,
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, selective=True))
        return 0
    else:
        return ConversationHandler.END


@run_async
def pre_duelo(bot, update):
    message = update.message
    names = utils.get_names()
    reply_keyboard = [names[i:i + 3] for i in range(0, len(names), 3)]
    if check_points(bot, update, DUELO):
        bot.send_message(message.chat_id, '🎯 Retar a un duelo A ...\n\nO /cancel para cancelar el tiro',
                         reply_to_message_id=message.message_id,
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, selective=True))
        return 0
    else:
        return ConversationHandler.END


@run_async
def pre_apuesta(bot, update):
    if check_apuestas_actuales(bot, update):
        message = update.message
        numbers = variables.APUESTAS
        reply_keyboard = [numbers[i:i + 4] for i in range(0, len(numbers), 4)]
        bot.send_message(message.chat_id, 'Apuesta una cantidad de puntos y ¡gana! o /cancel si no tienes huevos',
                         reply_to_message_id=message.message_id,
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, selective=True))
        return 0
    else:
        return ConversationHandler.END

def check_points(bot, update, points):
    message = update.message
    user_id = message.from_user.id
    con = demi_utils.create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
            user_points = cur.fetchone()[0]
            if user_points < points:
                bot.send_message(message.chat_id,
                                 'No tienes puntos suficientes, te faltan %d ptos.' % (points - user_points),
                                 reply_to_message_id=message.message_id,
                                 reply_markup=ReplyKeyboardRemove(selective=True))
                return False
            else:
                return True
    except Exception:
        logger.error('Fatal error in check_points', exc_info=True)
        return False
    finally:
        if con:
            con.close()


@run_async
def apuesta(bot, update, job_queue):
    import random
    message = update.message
    user_id = message.from_user.id
    puntos_apostados = update.message.text
    con = demi_utils.create_connection()
    if (puntos_apostados == '0'):
        bot.send_message(message.chat_id,
         'Te crees muy gracioso, ¿no?',
         reply_to_message_id=message.message_id,
         reply_markup=ReplyKeyboardRemove(selective=True))
        return ConversationHandler.END        
    if (puntos_apostados not in variables.APUESTAS):
        bot.send_message(message.chat_id,
         'Elige una opción de las disponibles.',
         reply_to_message_id=message.message_id,
         reply_markup=ReplyKeyboardRemove(selective=True))
        return ConversationHandler.END
    if not check_points(bot, update, int(puntos_apostados)):
        return ConversationHandler.END
    try:
        with con.cursor() as cur:
            cur.execute('UPDATE Economy SET ApuestasDia = ApuestasDia - 1 WHERE UserId = %s',
                         str(user_id))

        bot.send_document(message.chat_id, 'https://media.giphy.com/media/GWS8bXKxphfEI/giphy.gif', reply_to_message_id=message.message_id,
                              reply_markup=ReplyKeyboardRemove(selective=True))
        try:
            time.sleep(3)
        except TimedOut:
            pass

        lucky = random.randint(0, 99)
        if lucky < 50:
            with con.cursor() as cur:
                cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s',
                            (str(int(puntos_apostados)), str(user_id)))
                cur.execute('UPDATE Usos SET Veces = Veces + %s WHERE UserId = %s', (str(int(puntos_apostados)), str(user_id)))
            bot.send_message(message.chat_id, '¡PIERDES ' + str(int(puntos_apostados)) + ' puntos! Puntos actuales: ' + puntos_actuales(user_id, con))
            bot.send_document(message.chat_id, 'https://media.giphy.com/media/3o6UB5RrlQuMfZp82Y/giphy.gif')
        if 50 <= lucky < 99:
            with con.cursor() as cur:
                cur.execute('UPDATE Ranking SET Points = Points + %s WHERE UserId = %s',
                            (str(int(puntos_apostados)), str(user_id)))
            bot.send_message(message.chat_id, '¡GANAS ' + str(int(puntos_apostados)) + ' puntos! Puntos actuales: ' + puntos_actuales(user_id, con))
            bot.send_document(message.chat_id, 'https://media.giphy.com/media/pPzjpxJXa0pna/giphy.gif')
        elif lucky == 99:
            with con.cursor() as cur:
                cur.execute('UPDATE Ranking SET Points = Points + %s WHERE UserId = %s',
                            (str(int(puntos_apostados)*13), str(user_id)))
            bot.send_message(message.chat_id, 'GG EZ +' + str(int(puntos_apostados)*13) + ' puntos! Puntos actuales: ' + puntos_actuales(user_id, con))
            bot.send_document(message.chat_id, 'https://media.giphy.com/media/hv4TC2Ide8rDoXy0iK/giphy.gif')
    except Exception:
        logger.error('Fatal error in apuesta', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()
    return ConversationHandler.END


def puntos_actuales(user_id, con):
    with con.cursor() as cur:
        cur.execute('SELECT Points FROM Ranking WHERE UserId = %s',
                    (str(user_id)))
    return str(cur.fetchone()[0])

def check_apuestas_actuales(bot, update):
    message = update.message
    user_id = message.from_user.id
    con = demi_utils.create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT ApuestasDia FROM Economy WHERE UserId = %s', (str(user_id)));
        apuestas_actuales = str(cur.fetchone()[0]);

        if(apuestas_actuales == '0'):
            bot.send_message(message.chat_id,
             'No te quedan apuestas hoy.',
             reply_to_message_id=message.message_id,
             reply_markup=ReplyKeyboardRemove(selective=True))       
            return False;
        else:
            return True;
    except Exception:
        logger.error('Fatal error in check_points', exc_info=True)
        return False
    finally:
        if con:
            con.close()

@run_async
def duelo(bot, update, job_queue):
    import random
    message = update.message
    user_id = message.from_user.id
    name = update.message.text
    con = demi_utils.create_connection()
    random = random.randint(0, 1)
    if not check_points(bot, update, DUELO):
        return ConversationHandler.END
    try:
        bot.send_document(group_id, 'https://i.imgur.com/eK86rUd.gif')
        msg = bot.send_message(group_id, 'Es hora del DU DU DU DUELO!', parse_mode='Markdown')
        for i in range(3, 0, -1):
            time.sleep(1)

        if random == 0:
            reported = user_id
            bot.send_message(variables.group_id, name + ' tenía una carta trampa y pierdes')
            name = utils.get_name(reported)
            resource = 'data/gifs/duelo/bewd.mp4'
        else:
            reported = utils.get_user_id(name)
            bot.send_message(variables.group_id, 'Sacas a Exodia y ganas automáticamente')
            resource = 'data/gifs/duelo/exodia.mp4'

        gif_path = os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource)
        if os.path.isfile(gif_path):
            gif1, gif2 = open(gif_path, 'rb'), open(gif_path, 'rb')
        else:
            gif1 = gif2 = 'data/gifs/duelo/exodia.mp4'

        with con.cursor() as cur:
            cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s',
                        (str(DUELO), str(user_id)))
            cur.execute('UPDATE Usos SET Veces = Veces + %s WHERE UserId = %s', (str(DUELO), str(user_id)))
        if message.chat.type == 'private':
            bot.send_document(user_id, gif2, reply_to_message_id=message.message_id,
                              reply_markup=ReplyKeyboardRemove(selective=True))
            bot.send_document(group_id, gif1)
        else:
            bot.send_document(group_id, gif1, reply_to_message_id=message.message_id,
                              reply_markup=ReplyKeyboardRemove(selective=True))
        if not isinstance(gif1, str):
            gif1.close()
            gif2.close()
        thr1 = threading.Thread(target=reports.counter, args=(bot, name, reported, job_queue))
        thr1.start()
    except Exception:
        logger.error('Fatal error in duelo', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()
        return ConversationHandler.END


@run_async
def headshot(bot, update, job_queue):
    message = update.message
    user_id = message.from_user.id
    name = update.message.text
    reported = utils.get_user_id(name)
    con = demi_utils.create_connection()

    if not check_points(bot, update, HEADSHOT):
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
            cur.execute('UPDATE Usos SET Veces = Veces + %s WHERE UserId = %s', (str(HEADSHOT), str(user_id)))
        if message.chat.type == 'private':
            bot.send_document(user_id, gif2, reply_to_message_id=message.message_id,
                              reply_markup=ReplyKeyboardRemove(selective=True))
            bot.send_document(group_id, gif1)
        else:
            bot.send_document(group_id, gif1, reply_to_message_id=message.message_id,
                              reply_markup=ReplyKeyboardRemove(selective=True))
        if not isinstance(gif1, str):
            gif1.close()
            gif2.close()
        thr1 = threading.Thread(target=reports.counter, args=(bot, name, reported, job_queue))
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
    con = demi_utils.create_connection()
    for user_id in user_ids:
        chat_member = bot.get_chat_member(group_id, user_id)
        user_data = report_variables.user_data_dict[user_id]
        try:
            user_data['ban_time'] = reports.variables.ban_time
            if chat_member.status == 'kicked':
                if 'ban_time' in user_data and user_data['ban_time'] > 0 and chat_member.until_date is not None:
                    user_data['ban_time'] = chat_member.until_date.timestamp()-time.time()+reports.variables.ban_time

            sti = io.BufferedReader(io.BytesIO(pkgutil.get_data('reportTelegram', 'data/stickers/%s.webp' % reports.variables.sticker)))
            bot.send_sticker(user_id, sti)
            sti.close()
            m, s = divmod(user_data['ban_time'], 60)
            text = 'Expulsado durante %02d:%02d minutos\n\n⚠️Esto no es un **** contador⚠' % (m, s)
            bot.send_message(user_id, text)
            bot.kick_chat_member(group_id, user_id, until_date=time.time()+user_data['ban_time'])
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


@run_async
def pre_mute(bot, update):
    message = update.message
    names = utils.get_names()
    reply_keyboard = [names[i:i + 3] for i in range(0, len(names), 3)]
    if check_points(bot, update, MUTE):
        bot.send_message(message.chat_id, '🎯 MUTE A ...\n\nO /cancel para cancelar el muteo',
                         reply_to_message_id=message.message_id,
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, selective=True))
        return 0
    else:
        return ConversationHandler.END


@run_async
def mute(bot, update):
    message = update.message
    user_id = message.from_user.id
    name = update.message.text
    reported = utils.get_user_id(name)
    con = demi_utils.create_connection()

    if not check_points(bot, update, MUTE):
        return ConversationHandler.END
    try:
        with con.cursor() as cur:
            cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s',
                        (str(MUTE), str(user_id)))
            cur.execute('UPDATE Usos SET Veces = Veces + %s WHERE UserId = %s', (str(MUTE), str(user_id)))
        text = 'Mira %s que te calles la puta boca 🤐\nCon amor @%s' % (name, message.from_user.username)
        bot.send_message(group_id, text, reply_markup=ReplyKeyboardRemove(selective=True))
        if message.chat.type == 'private':
            text = 'Has silenciado a %s 🤐' % name
            bot.send_message(user_id, text, reply_to_message_id=message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))

        thr1 = threading.Thread(target=couter_mute, args=(bot, reported))
        thr1.start()
    except Exception:
        logger.error('Fatal error in mute', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()
        return ConversationHandler.END


def couter_mute(bot, reported):
    try:
        user_data = report_variables.user_data_dict[reported]

        while bot.get_chat_member(group_id, reported).status == 'kicked' and 'ban_time' in user_data:
            time.sleep(user_data['ban_time'] + 1)

        if 'mute_time' in user_data and user_data['mute_time'] > 0:
            user_data['mute_time'] += variables.MUTE_TIME
            bot.restrict_chat_member(group_id, reported, can_send_messages=False,
                                     until_date=time.time()+variables.MUTE_TIME)
            m, s = divmod(variables.MUTE_TIME, 60)
            text = 'Mute actualizado: +%02d:%02d' % (m, s)
            bot.send_message(reported, text)
            return True

        user_data['mute_time'] = variables.MUTE_TIME
        m, s = divmod(user_data['mute_time'], 60)
        text = '🤐 Muteado durante: %02d:%02d' % (m, s)
        msg = bot.send_message(reported, text)

        bot.restrict_chat_member(group_id, reported, can_send_messages=False,
                                 until_date=time.time() + variables.MUTE_TIME)

        while user_data['mute_time'] > 0:
            time.sleep(1)
            user_data['mute_time'] -= 1
            m, s = divmod(user_data['mute_time'], 60)
            text = '🤐 Muteado durante: %02d:%02d' % (m, s)
            bot.edit_message_text(text, chat_id=reported, message_id=msg.message_id)
        bot.send_message(reported, 'Ya puedes volver a hablar 😁')
    except Exception:
        logger.error('Fatal error in mute', exc_info=True)


def change_group_photo_bot(bot, update):
    message = update.message
    try:
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, '🌀Procesando...')
        photo_file = bot.getFile(message.photo[-1].file_id)
        photo_file.download('photo.jpg')
        with open('photo.jpg', 'rb') as photo_downloaded:
            bot.set_chat_photo(chat_id=group_id, photo=photo_downloaded)
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

    con = demi_utils.create_connection()
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
            bot.set_chat_title(chat_id=group_id, title=group_name)
            bot.edit_message_text('✅ Nombre cambiado', chat_id=chat_id, message_id=msg.message_id)
    except Exception:
        logger.error('Fatal error in change_group_name_bot', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def run_daily_perros(bot, job):
    if random.random() < 0.15:
        cuenta_perros(bot)


def daily_reward(bot, job):
    bot.send_message(group_id, 'RECOMPENSA DIARIA AÑADIDA', parse_mode='Markdown')
    con = demi_utils.create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('UPDATE Ranking SET Points = Points + 1')
            cur.execute('UPDATE Economy SET ApuestasDia = 3')
    except Exception:
        logger.error('Fatal error in daily_rewards', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()
    bot.send_message(group_id, get_ranking(), parse_mode='Markdown')
