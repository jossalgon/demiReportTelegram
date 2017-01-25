# -*- encoding: utf-8 -*-

import re
import sqlite3 as lite

import variables
from src.utils import Utils

utils = Utils()

bot = variables.bot
admin_id = variables.admin_id
group_id = variables.group_id
db_dir = variables.db_dir


class Mentions:
    def set_troll(self, message):
        con = lite.connect(db_dir)
        try:
            cur = con.cursor()
            target = int(message.text[7::])
            username = utils.get_name(target)
            trolls = utils.get_trolls()
            if target in trolls:
                cur.execute('DELETE FROM Trolls WHERE UserId = ?', (target,))
                bot.send_message(group_id, '❤️ %s eliminado de la lista de trolls' % username)
            else:
                cur.execute('INSERT INTO Trolls VALUES(?)', (target,))
                bot.send_message(group_id, '💔 %s añadido a la lista de trolls' % username)
        except Exception as exception:
            bot.send_message(admin_id, exception)
        finally:
            if con:
                con.commit()
                con.close()

    def mention_handler(self, message):
        usernames = utils.get_usernames()
        mentions = re.findall(r'\@\w+', message.text)
        user_ids = utils.get_userIds()
        not_mention = utils.get_not_mention()
        for mention in mentions:
            if mention in usernames:
                bot.forward_message(usernames[mention], group_id, message.message_id)
            elif mention == '@todos':
                for user_id in user_ids:
                    if user_id not in not_mention:
                        bot.forward_message(user_id, group_id, message.message_id)

    def mention_toggle(self, message):
        user_id = message.from_user.id
        con = lite.connect(db_dir)
        try:
            cur = con.cursor()
            not_mention = utils.get_not_mention()
            if user_id not in not_mention:
                cur.execute('INSERT INTO SilentMention VALUES(?)', (user_id,))
                bot.reply_to(message, '❎ Menciones desactivadas')
            else:
                cur.execute('DELETE FROM SilentMention WHERE UserId = ?', (user_id,))
                bot.reply_to(message, '✅ Menciones activadas')
        except Exception as exception:
            print(exception)
        finally:
            if con:
                con.commit()
                con.close()

    def send_not_mention(self, message):
        not_mentions_list = utils.get_not_mention()
        not_mentions_text = 'Usuarios con menciones silenciadas:'
        for user in not_mentions_list:
            not_mentions_text += '\n%s' % user
        bot.reply_to(message, not_mentions_text)

    def send_trolls(self, message):
        trolls_list = utils.get_trolls()
        trolls_text = 'Trolls:'
        for user in trolls_list:
            trolls_text += '\n%s' % user
        bot.reply_to(message, trolls_text)


