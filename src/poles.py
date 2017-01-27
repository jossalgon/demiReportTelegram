# -*- encoding: utf-8 -*-

import datetime
import random
import pymysql
import threading
import time

from src.reports import Reports

import variables
from src.utils import Utils

utils = Utils()
reports = Reports()

bot = variables.bot
admin_id = variables.admin_id
group_id = variables.group_id
perros = variables.perros
nuke = variables.nuke

DB_HOST = variables.DB_HOST
DB_USER = variables.DB_USER
DB_PASS = variables.DB_PASS
DB_NAME = variables.DB_NAME


class Poles:
    def pole_handler(self, message):
        user_id = message.from_user.id
        poles = variables.poles
        is_saturday = (datetime.datetime.today().weekday() == 5)
        con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        try:
            with con.cursor() as cur:
                if user_id in poles:
                    cur.execute('UPDATE Ranking SET Points = Points - 3 WHERE UserId = %s', (str(user_id),))
                    bot.reply_to(message, 'No eres el centro del mundo sabes? (-3 ptos)')
                elif len(poles) == 0:
                    text = 'Pole conseguida! (+3 ptos)'
                    if user_id == 62394824:
                        text = '"que estaba hablando con mari tomto" (+3 ptos)'
                        bot.send_photo(group_id, 'http://s11.postimg.org/9joar1voz/campero.jpg')
                    variables.add_member_to_poles(user_id, 0)
                    cur.execute('UPDATE Ranking SET Points = Points + 3 WHERE UserId = %s', (str(user_id),))
                    if is_saturday:
                        text = '\n\nVete con tu foto a chuparla a jugar al LoL\n' \
                               + '💝(Enviame la foto por privado)'
                    bot.reply_to(message, text)
                else:
                    cur.execute('UPDATE Ranking SET Points = Points - 1 WHERE UserId = %s', (str(user_id),))
                    bot.reply_to(message, 'FAIL!!! (-1 ptos)')
        except Exception as exception:
            print(exception)
        finally:
            if con:
                con.commit()
                con.close()

    def subpole_handler(self, message):
        user_id = message.from_user.id
        poles = variables.poles
        is_saturday = (datetime.datetime.today().weekday() == 5)
        con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        try:
            with con.cursor() as cur:
                if user_id in poles:
                    cur.execute('UPDATE Ranking SET Points = Points - 3 WHERE UserId = %s', (str(user_id),))
                    bot.reply_to(message, 'No eres el centro del mundo sabes?  (-3 ptos)')
                elif len(poles) == 1:
                    text = 'Más vale subpole en mano que cien en tu ano! (+2 ptos)'
                    variables.add_member_to_poles(user_id, 1)
                    cur.execute('UPDATE Ranking SET Points = Points + 2 WHERE UserId = %s', (str(user_id),))
                    if is_saturday:
                        text = text + '\n\nVete con tu nombre a chuparla a jugar al LoL\n' \
                               + '💝(Escríbeme un nombre para el grupo por privado)'
                    bot.reply_to(message, text)
                else:
                    cur.execute('UPDATE Ranking SET Points = Points - 1 WHERE UserId = %s', (str(user_id),))
                    bot.reply_to(message, 'FAIL!!! (-1 ptos)')
        except Exception as exception:
            print(exception)
        finally:
            if con:
                con.commit()
                con.close()

    def tercercomentario_handler(self, message):
        user_id = message.from_user.id
        poles = variables.poles
        is_saturday = (datetime.datetime.today().weekday() == 5)
        con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        try:
            with con.cursor() as cur:
                if user_id in poles:
                    cur.execute('UPDATE Ranking SET Points = Points - 3 WHERE UserId = %s', (str(user_id),))
                    bot.reply_to(message, 'No eres el centro del mundo sabes? (-3 ptos)')
                elif len(poles) == 2:
                    text = 'Larga vida al tercer comentario! (+1 ptos)'
                    variables.add_member_to_poles(user_id, 2)
                    cur.execute('UPDATE Ranking SET Points = Points + 1 WHERE UserId = %s', (str(user_id),))
                    if is_saturday:
                        text = text + '\n\nVete con tu nombre a chuparla a jugar al LoL\n' \
                               + '💝(Escríbeme un nombre para el grupo por privado)'
                    bot.reply_to(message, text)
                else:
                    cur.execute('UPDATE Ranking SET Points = Points - 1 WHERE UserId = %s', (str(user_id),))
                    bot.reply_to(message, 'FAIL!!! (-1 ptos)')
        except Exception as exception:
            print(exception)
        finally:
            if con:
                con.commit()
                con.close()

    def ranking_handler(self, message):
        chat_id = message.chat.id
        con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        try:
            with con.cursor() as cur:
                cur.execute('SELECT UserId, Points FROM Ranking GROUP BY UserId ORDER BY Points DESC LIMIT 10')
                rows = cur.fetchall()
                top = '🏆 Ranking:\n*1º - %s (%d ptos)*\n' % (utils.get_name(rows[0][0]), rows[0][1])
                for row, pos in zip(rows[1:], range(2, 11)):
                    top += '%dº - %s (%d ptos)\n' % (pos, utils.get_name(row[0]), row[1])
                top += '\n🐺 Perros por %d ptos.\n☢ Nuke por %d ptos.' % (perros, nuke)
                bot.send_message(chat_id, top, parse_mode='Markdown')
        except Exception as exception:
            print(exception)
        finally:
            if con:
                con.close()

    def send_nuke(self, message):
        user_id = message.from_user.id
        con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        try:
            with con.cursor() as cur:
                cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
                user_points = cur.fetchone()[0]
                if user_points >= nuke:
                    cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s', (str(nuke), str(user_id)))
                    bot.send_document(group_id, 'http://imgur.com/vZDxkFk.gif')
                    audio = open('data/nuke.ogg', 'rb')
                    bot.send_audio(group_id, audio)
                    bot.reply_to(message, 'ORDEN RECIBIDA nuke EN 15 SEG.')
                    time.sleep(5)
                    bot.send_message(group_id, 'nuke EN 10 SEG.')
                    time.sleep(5)
                    for i in range(5, 0, -1):
                        bot.send_message(group_id, 'nuke EN %d SEG.' % i)
                        time.sleep(1)
                    self.cuenta_all()
                else:
                    bot.reply_to(message, 'No tienes puntos suficientes, te faltan %d ptos.' % (nuke - user_points))
        except Exception as exception:
            bot.send_message(admin_id, exception)
        finally:
            if con:
                con.commit()
                con.close()

    def send_perros(self, message):
        user_id = message.from_user.id
        con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        try:
            with con.cursor() as cur:
                cur.execute('SELECT Points FROM Ranking WHERE UserId = %s', (str(user_id),))
                user_points = cur.fetchone()[0]
                if user_points >= perros:
                    cur.execute('UPDATE Ranking SET Points = Points - %s WHERE UserId = %s', (str(perros), str(user_id)))
                    bot.send_document(group_id, 'http://imgur.com/buULxjj.gif')
                    msg = bot.send_message(group_id, 'perros EN *5 SEG.*', parse_mode='Markdown')
                    for i in range(4, -1, -1):
                        time.sleep(1)
                        text = 'perros EN *%d SEG.*' % i
                        bot.edit_message_text(text, chat_id=group_id, message_id=msg.message_id, parse_mode='Markdown')
                    self.cuenta_perros(user_id)
                else:
                    bot.reply_to(message, 'No tienes puntos suficientes, te faltan %d ptos.' % (perros - user_points))
        except Exception as exception:
            bot.send_message(admin_id, exception)
        finally:
            if con:
                con.commit()
                con.close()

    def cuenta_perros(self, user_id):
        targets = []
        users = utils.get_userIds()
        users.remove(user_id)
        target = random.sample(range(len(users)), 5)
        for t in target:
            targets.append(users[t])
        for user_id in targets:
            thr1 = threading.Thread(target=reports.cuenta, args=(utils.get_name(user_id), user_id))
            thr1.start()

    def cuenta_all(self):
        user_ids = utils.get_userIds()
        for user_id in user_ids:
            thr1 = threading.Thread(target=reports.cuenta, args=(utils.get_name(user_id), user_id))
            thr1.start()

    def change_group_photo_bot(self, message):
        try:
            chat_id = message.chat.id
            msg = bot.send_message(chat_id, '🌀Procesando...')
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('data/photo.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)
            utils.change_group_photo()
            bot.edit_message_text('✅ Foto cambiada', chat_id=chat_id, message_id=msg.message_id)
        except Exception as e:
            bot.send_message(admin_id, e)

    def change_group_name_bot(self, message):
        group_name = ''
        poles = variables.poles
        user_id = message.from_user.id
        position = poles.index(user_id) + 1
        name = message.text
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, '🌀Procesando...')

        if len(name) > 30:
            bot.reply_to(message, 'Aviso ese nombre es mu largo acho')
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
                utils.change_group_name(group_name)
                bot.edit_message_text('✅ Nombre cambiado', chat_id=chat_id, message_id=msg.message_id)
        except Exception as e:
            bot.send_message(admin_id, e)
        finally:
            if con:
                con.commit()
                con.close()
