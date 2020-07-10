import datetime
import os
import re
import time
import logging
import pymysql
import socket
from mcstatus import MinecraftServer
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async

from reportTelegram import utils as report_utils
from demiReportTelegram import variables

ADMIN_ID = variables.admin_id
GROUP_ID = variables.group_id

DB_HOST = variables.DB_HOST
DB_USER = variables.DB_USER
DB_PASS = variables.DB_PASS
DB_NAME = variables.DB_NAME

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def create_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)


def get_user_ids(is_pipas=False):
    user_ids = []
    con = create_connection()
    try:
        with con.cursor() as cur:
            if is_pipas:
                cur.execute('SELECT UserId FROM PipasUsers')
            else:
                cur.execute('SELECT UserId FROM Users')
            rows = cur.fetchall()
            for row in rows:
                user_ids.append(row[0])
    except Exception:
        logger.error('Fatal error in get_user_ids', exc_info=True)
    finally:
        if con:
            con.close()
        return user_ids


def is_from_pipas_group(user_id):
    result = False
    con = create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT EXISTS(SELECT 1 FROM PipasUsers WHERE UserId = %s)', (str(user_id),))
            result = bool(cur.fetchone()[0])
    except Exception:
        logger.error('Fatal error in is_from_group', exc_info=True)
    finally:
        if con:
            con.close()
        return result


def get_user_name(id):
    user_name = []
    con = create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Name FROM PipasUsers Where UserId=%s' % id)
            rows = cur.fetchall()
            for row in rows:
                user_name.append(row[0])
    except Exception:
        logger.error('Fatal error in is_from_group', exc_info=True)
    finally:
        if con:
            con.close()
        return user_name


def get_usernames(bot):
    usernames = {}
    for user_id in get_user_ids():
        username = bot.get_chat_member(GROUP_ID, user_id).user.username
        usernames['@%s' % username.lower()] = user_id
    return usernames


def get_trolls():
    con = create_connection()
    trolls = []
    try:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM Trolls")
            rows = cur.fetchall()
            for row in rows:
                trolls.append(row[0])
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return trolls


def get_not_mention(mention_type):
    con = create_connection()
    not_mentions = []
    try:
        with con.cursor() as cur:
            cur.execute("SELECT userId FROM SilentMention WHERE mentionType=%s", (str(mention_type),))
            rows = cur.fetchall()
            for row in rows:
                not_mentions.append(row[0])
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return not_mentions


def get_events():
    con = create_connection()
    events = []
    try:
        with con.cursor() as cur:
            cur.execute("SELECT eventId FROM Pipas")
            rows = cur.fetchall()
            for row in rows:
                events.append(row[0])
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return events


def get_event_text(event_id):
    con = create_connection()
    res = ''
    try:
        with con.cursor() as cur:
            cur.execute("SELECT text FROM Pipas WHERE eventId=%s", (str(event_id),))
            res = cur.fetchone()[0]
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return res


def get_event_message_id(event_id):
    con = create_connection()
    res = ''
    try:
        with con.cursor() as cur:
            cur.execute("SELECT messageId FROM Pipas WHERE eventId=%s", (str(event_id),))
            res = cur.fetchone()[0]
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return res


def get_vote(event_id, user_id):
    con = create_connection()
    res = ''
    try:
        with con.cursor() as cur:
            cur.execute("SELECT selected FROM PipasVotes WHERE eventId=%s and userId=%s", (str(event_id), str(user_id)))
            query_fetch = cur.fetchone()
            res = query_fetch[0] if query_fetch is not None else res
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return res


def get_name(user_id):
    username = 'Anon'
    con = create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT Name FROM PipasUsers WHERE UserId = %s', (str(user_id),))
            if cur.rowcount:
                username = cur.fetchone()[0]
    except Exception:
        logger.error('Fatal error in get_name', exc_info=True)
    finally:
        if con:
            con.close()
        return username


def get_participants_event(event_id):
    con = create_connection()
    user_ids = [[], [], []]
    try:
        with con.cursor() as cur:
            cur.execute("SELECT userId, selected  FROM PipasVotes WHERE eventId = %s", (str(event_id),))
            rows = cur.fetchall()
            for row in rows:
                if row[1] == 0:
                    user_ids[0].append(get_name(row[0]))
                if row[1] == 1:
                    user_ids[1].append(get_name(row[0]))
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return user_ids


def is_long_event(event_id):
    con = create_connection()
    res = ''
    try:
        with con.cursor() as cur:
            cur.execute('SELECT EXISTS(SELECT 1 FROM Pipas WHERE eventId=%s AND pipasDate IS NOT NULL)', (str(event_id),))
            res = bool(cur.fetchone()[0])
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return res


def create_event(event_id, message_id, text):
    con = create_connection()
    pipas_date_search = re.search(r'\d{1,2}/\d{1,2}/\d{4}', text)

    try:
        if pipas_date_search:
            pipas_date_text = pipas_date_search.group(0)
            pipas_date = datetime.datetime.strptime(pipas_date_text, '%d/%m/%Y').date()

            search_start, search_end = pipas_date_search.span()
            text = text[:search_start] + '*' + pipas_date_text + '*' + text[search_end:]

            if pipas_date < datetime.date.today():
                return False
            else:
                pipas_date = str(pipas_date)
        else:
            pipas_date = None
    except ValueError:
        return False

    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO Pipas VALUES(%s, %s, %s, %s)",
                        (str(event_id), str(message_id), str(text), pipas_date))
        return True
    except Exception:
        logger.error('Fatal error in create_event', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def add_participant_event(event_id, user_id, selected):
    con = create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('INSERT INTO PipasVotes(eventId, userId, selected) VALUES(%s, %s, %s) '
                        'ON DUPLICATE KEY UPDATE selected = VALUES(selected)',
                        (str(event_id), str(user_id), str(selected)))
    except Exception:
        logger.error('Fatal error in pipas_selected', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def get_who_pipas():
    res = '🌳 Quedadas'
    events = get_events()
    if len(events) == 0:
        res += '\n\n😢 De momento no hay ningún plan' \
               '\n\nRecuerda que puedes crear uno poniendo @pipas seguido del plan y si es necesaria una fecha. ' \
               'La fecha debe ser futura con el formato "dd/mm/yyyy".' \
               '\nEjemplo: "@pipas parque a las 11" o "@pipas cine el 01/10/2017"'

    else:
        for event in events:
            option_1 = get_participants_event(event)[0]
            option_2 = get_participants_event(event)[1]
            event_name = get_event_text(event)

            res += '\n\n%s' % (event_name if event_name != '' else 'Parque pipas')
            res += '\n✔️ Sí (%i): %s' % (len(option_1), ', '.join(option_1))
            res += '\n❌ No (%i): %s' % (len(option_2), ', '.join(option_2))

    return res


def mention_control(user_id, mention_type, silent):
    con = create_connection()
    try:
        with con.cursor() as cur:
            if silent:
                cur.execute('INSERT INTO SilentMention VALUES(%s, %s)', (str(user_id), str(mention_type)))
                return '❎ Menciones desactivadas'
            else:
                cur.execute('DELETE FROM SilentMention WHERE userId=%s and mentionType=%s',
                            (str(user_id), str(mention_type)))
                return '✅ Menciones activadas'
    except Exception:
        logger.error('Fatal error in mention_toggle', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def get_wanted_words(user_id):
    words = {}
    con = create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('SELECT wordId, word FROM WantedWords WHERE userId=%s', (str(user_id),))
            rows = cur.fetchall()
            for row in rows:
                words[row[0]] = row[1]
    except Exception:
        logger.error('Fatal error in get_wanted_words', exc_info=True)
    finally:
        if con:
            con.close()
        return words


def remove_wanted_word(word_id):
    con = create_connection()
    try:
        with con.cursor() as cur:
            cur.execute('DELETE FROM WantedWords WHERE wordId=%s', (str(word_id),))
            return True
    except Exception:
        logger.error('Fatal error in remove_wanted_word', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def is_wanted_word(word, user_id):
    con = create_connection()
    res = False
    try:
        with con.cursor() as cur:
            cur.execute("SELECT wordId FROM WantedWords WHERE word=%s and userId=%s",
                        (str(word), str(user_id)))
            query_fetch = cur.fetchone()
            res = query_fetch is not None
    except Exception:
        logger.error('Fatal error in is_wanted_word', exc_info=True)
    finally:
        if con:
            con.close()
        return res


def get_word(word_id):
    con = create_connection()
    res = ''
    try:
        with con.cursor() as cur:
            cur.execute("SELECT word FROM WantedWords WHERE wordId=%s", (str(word_id),))
            res = cur.fetchone()[0]
    except Exception:
        logger.error('Fatal error in get_word', exc_info=True)
    finally:
        if con:
            con.close()
        return res


def get_users_from_word(word):
    con = create_connection()
    user_ids = list()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT userId FROM WantedWords WHERE word=%s", (str(word),))
            rows = cur.fetchall()
            for row in rows:
                user_ids.append(row[0])
    except Exception:
        logger.error('Fatal error in get_word', exc_info=True)
    finally:
        if con:
            con.close()
        return user_ids


def get_all_words():
    con = create_connection()
    words = list()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT word FROM WantedWords")
            rows = cur.fetchall()
            for row in rows:
                words.append(row[0])
    except Exception as exception:
        logger.error('Fatal error in get_all_words', exc_info=True)
    finally:
        if con:
            con.close()
        return words


def is_silent_user(user_id, mention_type):
    con = create_connection()
    res = False
    try:
        with con.cursor() as cur:
            cur.execute("SELECT userId FROM SilentMention WHERE userId=%s and mentionType=%s",
                        (str(user_id), str(mention_type)))
            query_fetch = cur.fetchone()
            res = query_fetch is not None
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return res


def login_account():
    os.system("./../tg/bin/telegram-cli -W -e 'status_online'")
    os.system("./../tg/bin/telegram-cli -W -e 'status_offline'")


def change_group_photo():
    os.system("./../tg/bin/telegram-cli -W -e 'channel_set_photo channel#1060426760 photo.jpg'")
    os.system("./../tg/bin/telegram-cli -W -e 'status_offline'")


def set_power(power):
    os.system("./../tg/bin/telegram-cli -W -e 'channel_set_admin channel#1060426760 Selu %i'" % power)
    os.system("./../tg/bin/telegram-cli -W -e 'status_offline'")


def change_group_name(name):
    os.system("./../tg/bin/telegram-cli -W -e 'rename_channel channel#1060426760 %s'" % name)
    os.system("./../tg/bin/telegram-cli -W -e 'status_offline'")


def create_database():
    con = create_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS `Usos` ( \
                  `UserId` int(11) NOT NULL, \
                  `Veces` int(11) NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `Ranking` ( \
                  `UserId` int(11) NOT NULL, \
                  `Points` int(11) NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `SilentMention` ( \
                  `userId` int(11) NOT NULL, \
                  `mentionType` TEXT NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `Trolls` ( \
                  `UserId` int(11) NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `GroupNames` ( \
                  `groupName` text NOT NULL, \
                  `position` int(11) NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `WantedWords` ( \
                  `wordId` int NOT NULL AUTO_INCREMENT, \
                  `word` text NOT NULL, \
                  `userId` int(11) NOT NULL, \
                   PRIMARY KEY (wordId) \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `Pipas` ( \
                  `eventId` BIGINT(30) NOT NULL, \
                  `messageId` BIGINT(30) NOT NULL, \
                  `text` TEXT NOT NULL, \
                  `pipasDate` DATE, \
                  PRIMARY KEY (eventId) \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `PipasVotes` ( \
                  `eventId` BIGINT(30) NOT NULL, \
                  `userId` int(11) NOT NULL, \
                  `selected` int(11) NOT NULL, \
                  UNIQUE KEY (eventId, userId), \
                  FOREIGN KEY (eventId) REFERENCES Pipas(eventId) \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `PipasUsers` ( \
                  `UserId` int(11) NOT NULL, \
                  `Name` text NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                ")
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.commit()
            con.close()


@run_async
def pole_counter(bot, job):
    text = time.strftime('%H:%M:*%S*')
    msg = bot.send_message(GROUP_ID, text, parse_mode='Markdown')
    time.sleep(0.5)
    for i in range(10):
        if text != time.strftime('%H:%M:*%S*') and (
                        time.strftime('%S') == '00' or int(time.strftime('%S')) >= 55):
            text = time.strftime('%H:%M:*%S*')
            bot.edit_message_text(text, chat_id=GROUP_ID, message_id=msg.message_id, parse_mode='Markdown')
        time.sleep(0.5)


def flooder(user_data, job_queue, num_messages=5):
    if 'flood' in user_data and user_data['flood'] < num_messages:
        user_data['flood'] += 1
        run_flood_timer(user_data, job_queue)
    elif 'flood' not in user_data:
        user_data['flood'] = 0
    return user_data['flood'] == num_messages


def clear_flooder(bot, job):
    user_data = job.context
    user_data['flood'] = 0


def run_flood_timer(user_data, job_queue):
    if 'flood_job' in user_data:
        job = user_data['flood_job']
        job.schedule_removal()
        del user_data['flood_job']
    user_data['flood_job'] = job_queue.run_once(clear_flooder, 10, context=user_data)


def get_who_minecraft():
    server = MinecraftServer.lookup(variables.minecraft_ip)
    text = ""
    try:
        server.ping()
        query = server.query()
        if query.players.online > 0:
            text = "⛏ *{0}* \[{1}/{2}]:\n   ▫️ {3}".format(query.map, query.players.online, query.players.max,
                                                    "\n   ▫️ ".join(query.players.names))
        else:
            text = "⛏ No hay nadie en este momento"
    except (socket.timeout, ConnectionRefusedError, AttributeError):
        text = "🚫 Servidor no disponible"
    finally:
        return text


def send_who_minecraft(bot, update, message_id=None, chat_id=None):
    message = update.effective_message

    res = get_who_minecraft()

    keyboard = [[InlineKeyboardButton("Actualizar", callback_data='MINECRAFT_UPDATE')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if message_id and chat_id:
        bot.edit_message_text(text=res, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup,
                              parse_mode='Markdown', reply_to_message_id=message.message_id)
    else:
        bot.send_message(message.chat.id, res, parse_mode='Markdown', reply_markup=reply_markup,
                         reply_to_message_id=message.message_id)


def remove_message(bot, job):
    chat_id, message_id = job.context
    bot.delete_message(chat_id=chat_id, message_id=message_id)
