import telegram
import datetime
import os
import threading
import time

import pymysql

import variables

ADMIN_ID = variables.admin_id
GROUP_ID = variables.group_id

DB_HOST = variables.DB_HOST
DB_USER = variables.DB_USER
DB_PASS = variables.DB_PASS
DB_NAME = variables.DB_NAME


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
    os.system("./../tg/bin/telegram-cli -W -e 'channel_set_photo channel#1060426760 data/photo.jpg'")
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


class Timer:
    def __init__(self):
        self.bot = telegram.Bot(variables.api_token)
        self.temporizado = False
        self.t = None
        self.t2 = None

    def pole_reseter(self):
        self.temporizado = False
        variables.clean_poles()
        if self.t is not None:
            self.t.cancel()
            self.t2.cancel()
        self.run_timer()

    def pole_counter(self):
        text = time.strftime('%H:%M:*%S*')
        msg = self.bot.send_message(GROUP_ID, text, parse_mode='Markdown')
        time.sleep(0.5)
        for i in range(10):
            if text != time.strftime('%H:%M:*%S*') and (
                            time.strftime('%S') == '00' or int(time.strftime('%S')) >= 55):
                text = time.strftime('%H:%M:*%S*')
                self.bot.edit_message_text(text, chat_id=GROUP_ID, message_id=msg.message_id, parse_mode='Markdown')
            time.sleep(0.5)

    def run_timer(self):
        self.temporizado = True
        x = datetime.datetime.today()
        y = x.replace(day=x.day, hour=23, minute=59, second=55, microsecond=0)
        y2 = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        delta_t = y - x
        delta_t2 = y2 - x
        secs = delta_t.seconds + 1
        secs2 = delta_t2.seconds + 1
        self.t = threading.Timer(secs, self.pole_counter)
        self.t2 = threading.Timer(secs2, self.pole_reseter)
        self.t.start()
        self.t2.start()

