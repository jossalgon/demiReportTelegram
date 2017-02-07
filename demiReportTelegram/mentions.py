# -*- encoding: utf-8 -*-

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
    not_mention = demi_utils.get_not_mention()
    for mention in mentions:
        mention = mention.lower()
        if mention in usernames:
            if usernames[mention] not in not_mention:
                bot.forward_message(usernames[mention], group_id, message.message_id)
    if bool(re.match(r'(?i).*@todos.*', message.text)):
        for user_id in user_ids:
            if user_id not in not_mention:
                bot.forward_message(user_id, group_id, message.message_id)


def mention_toggle(user_id):
    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            not_mention = demi_utils.get_not_mention()
            if user_id not in not_mention:
                cur.execute('INSERT INTO SilentMention VALUES(%s)', (str(user_id),))
                return '❎ Menciones desactivadas'
            else:
                cur.execute('DELETE FROM SilentMention WHERE UserId = %s', (str(user_id),))
                return '✅ Menciones activadas'
    except Exception:
        logger.error('Fatal error in mention_toggle', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()
