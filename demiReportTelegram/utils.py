import datetime
import os
import time

import logging
import pymysql

from demiReportTelegram import variables

ADMIN_ID = variables.admin_id
GROUP_ID = variables.group_id

DB_HOST = variables.DB_HOST
DB_USER = variables.DB_USER
DB_PASS = variables.DB_PASS
DB_NAME = variables.DB_NAME

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def get_user_ids():
    user_ids = []
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute('SELECT UserId FROM Users')
            rows = cur.fetchall()
            for row in rows:
                user_ids.append(row[0])
    except Exception:
        logger.error('Fatal error in is_from_group', exc_info=True)
    finally:
        if con:
            con.close()
        return user_ids


def get_usernames(bot):
    usernames = {}
    for user_id in get_user_ids():
        username = bot.get_chat_member(GROUP_ID, user_id).user.username
        usernames['@%s' % username.lower()] = user_id
    return usernames


def get_trolls():
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
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


def get_not_mention():
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    not_mentions = []
    try:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM SilentMention")
            rows = cur.fetchall()
            for row in rows:
                not_mentions.append(row[0])
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.close()
        return not_mentions


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
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
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
                  `UserId` int(11) NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `Trolls` ( \
                  `UserId` int(11) NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                CREATE TABLE IF NOT EXISTS `GroupNames` ( \
                  `groupName` text NOT NULL, \
                  `position` int(11) NOT NULL \
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \
                ")
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.commit()
            con.close()


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


def pole_timer(job_queue):
    x = datetime.datetime.today()
    y = x.replace(day=x.day, hour=23, minute=59, second=55, microsecond=0)
    y2 = x.replace(day=x.day, hour=1, minute=00, second=00, microsecond=0) + datetime.timedelta(days=1)
    delta_t = y - x
    delta_t2 = y2 - x
    secs = delta_t.seconds + 1
    secs2 = delta_t2.seconds + 1
    job_queue.run_daily(callback=pole_counter, time=secs)
    job_queue.run_daily(callback=variables.clean_poles, time=secs2)
