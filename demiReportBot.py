# -*- encoding: utf-8 -*-

import datetime
import time
from collections import deque

import variables
from src.admin import Admin
from src.adults import Adults
from src.general import General
from src.key_words import Key_words
from src.mentions import Mentions
from src.poles import Poles
from src.songs import Songs
from src.utils import Utils
from src.welcome import Welcome
from reportTelegram.src.reports import Reports
from teamSpeakTelegram.src.utils import Utils as Ts_utils

welcome = Welcome()
admin = Admin()
adults = Adults()
general = General()
key_words = Key_words()
mentions = Mentions()
poles = Poles()
reports = Reports()
songs = Songs()
utils = Utils()
ts_utils = Ts_utils()

bot = variables.bot
admin_id = variables.admin_id
group_id = variables.group_id
photo_ok = True

# BOT

msg_queue = deque([], 15)


def is_flooder(user_id):
    return msg_queue.count(user_id) >= msg_queue.maxlen/3


def listener(messages):
    global msg_queue
    for message in messages:
        msg_text = message.text
        from_id = message.from_user.id
        if msg_text is None:
            break
        elif not is_flooder(from_id) and message.text.startswith('/'):
            msg_queue.append(from_id)

bot.set_update_listener(listener)

while True:
    try:
        @bot.message_handler(commands=['help', 'start'])
        def send_welcome(message):
            welcome.send_welcome(message)

        # REPORTS

        @bot.message_handler(
            commands=['selu', 'amador', 'raul', 'ale1', 'alf', 'punky', 'domingo', 'fernando', 'dolito', 'jorge',
                      'carlos', 'raulito'],
            func=lambda msg: utils.is_from_group(msg.from_user.id) and msg.chat.id == group_id)
        def send_report(message):
            user_id = message.from_user.id
            command = message.text.split('@')[0]
            name = command.replace('/', '').capitalize()
            reported = utils.get_user_id(name)
            reports.send_report(user_id, reported)

        @bot.message_handler(commands=['stats'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def get_stats(message):
            reports.get_stats(message)

        @bot.message_handler(commands=['expulsados'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def expulsados_handler(message):
            reports.expulsados_handler(message)

        @bot.message_handler(commands=['who'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def who(message):
            reports.who(message)

        @bot.message_handler(content_types=['new_chat_member'])
        def send_welcome_to_new_member(message):
            welcome.send_welcome_to_new_member(message)

        @bot.message_handler(content_types=['left_chat_member'])
        def send_bye_to_member(message):
            welcome.send_bye_to_member(message)

        # ADMIN POWER
        @bot.message_handler(commands=['sipower'], func=lambda msg: msg.from_user.id == admin_id)
        def power_on(message):
            utils.set_power(2)
            bot.send_message(group_id, 'Selu activó sus poderes')
        
        @bot.message_handler(commands=['nopower'], func=lambda msg: msg.from_user.id == admin_id)
        def power_on(message):
            utils.set_power(0)
            bot.send_message(group_id, 'Selu desactivó sus poderes')

        # TS
        @bot.message_handler(commands=['ts'], func=lambda msg: ts_utils.is_allow(msg.from_user.id))
        def ts_stats(message):
            bot.reply_to(message, ts_utils.ts_stats())

        # MENTIONS
        @bot.message_handler(commands=['troll'], func=lambda msg: msg.chat.id == admin_id)
        def set_troll(message):
            mentions.set_troll(message)


        @bot.message_handler(func=lambda msg: msg.chat.id == group_id and msg.entities is not None and msg.entities[
                                                                                                           0].type == 'mention' and msg.from_user.id not in utils.get_trolls())
        def mention_handler(message):
            mentions.mention_handler(message)


        @bot.message_handler(commands=['mention'])
        def mention_toggle(message):
            mentions.mention_toggle(message)

        # KEY WORDS
        @bot.message_handler(commands=['getjorge'])
        def jorge_buenosdias_handler(message):
            bot.reply_to(message, variables.jorge_despierto)


        @bot.message_handler(content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker', 'photo'],
                             func=lambda msg: msg.from_user.id == 8787392 and msg.chat.id == group_id and 7 < int(
                                 time.strftime('%H')) < 14 and not variables.jorge_despierto)
        def jorge_despierto_handler(message):
            key_words.jorge_despierto_handler()


        @bot.message_handler(content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker', 'photo'],
                             func=lambda msg: msg.from_user.id == 8787392 and msg.chat.id == group_id and 14 <= int(
                                 time.strftime('%H')) < 21 and not variables.jorge_despierto)
        def jorge_buenosdias_handler(message):
            key_words.jorge_buenosdias_handler(message)


        @bot.message_handler(regexp='hipertextual.com|twitter.com\/Hipertextual',
                             func=lambda msg: msg.chat.id == group_id)
        def hipermierda_handler(message):
            key_words.hipermierda_handler(message)


        @bot.message_handler(regexp='[Rr]aulito( ya)* oro\?')
        def raulito_oro(message):
            key_words.raulito_oro(message)


        # SONGS
        @bot.inline_handler(func=lambda msg: not is_flooder(msg.from_user.id))
        def query_text(inline_query):
            songs.query_text(inline_query)


        @bot.chosen_inline_handler(
            func=lambda chosen_inline_result: utils.is_from_group(chosen_inline_result.from_user.id))
        def send_chosen(chosen_inline_result):
            global msg_queue
            from_id = chosen_inline_result.from_user.id
            if not is_flooder(from_id):
                msg_queue.append(from_id)
                songs.send_chosen(chosen_inline_result)

        # POLES
        @bot.message_handler(regexp='^([Pp][Oo]+[Ll][Ee]+)',
                             func=lambda msg: msg.chat.id == group_id and time.strftime('%H') == '00')
        def pole_handler(message):
            poles.pole_handler(message)


        @bot.message_handler(regexp='^([Ss][Uu]+[Bb][Pp][Oo]+[Ll][Ee]+)',
                             func=lambda msg: msg.chat.id == group_id and time.strftime('%H') == '00')
        def subpole_handler(message):
            poles.subpole_handler(message)


        @bot.message_handler(regexp='^([Tt]ercer [Cc]omentario)',
                             func=lambda msg: msg.chat.id == group_id and time.strftime('%H') == '00')
        def tercercomentario_handler(message):
            poles.tercercomentario_handler(message)


        @bot.message_handler(commands=['ranking'])
        def ranking_handler(message):
            poles.ranking_handler(message)


        @bot.message_handler(commands=['nuke'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def send_nuke(message):
            poles.send_nuke(message)


        @bot.message_handler(commands=['perros'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def send_perros(message):
            poles.send_perros(message)


        @bot.message_handler(content_types=['photo'],
                             func=lambda msg: msg.chat.type == 'private' and variables.poles
                                              and msg.from_user.id == variables.poles[0]
                                              and datetime.datetime.today().weekday() == 5
                                              and photo_ok)
        def pole_reward(message):
            poles.change_group_photo_bot(message)


        @bot.message_handler(func=lambda msg: msg.chat.type == 'private' and msg.text[0] != '/'
                                              and variables.poles
                                              and (msg.from_user.id == variables.poles[1]
                                                   or msg.from_user.id == variables.poles[2])
                                              and datetime.datetime.today().weekday() == 5)
        def group_name_reward(message):
            poles.change_group_name_bot(message)

        # +18
        @bot.message_handler(commands=['no18'], func=lambda msg: msg.from_user.id == admin_id)
        def stop_18(message):
            adults.stop_18(message)


        @bot.message_handler(commands=['si18'], func=lambda msg: msg.from_user.id == admin_id)
        def start_18(message):
            adults.start_18(message)


        @bot.message_handler(commands=['butts'],
                             func=lambda msg: (utils.is_from_group(msg.from_user.id) or msg.from_user.id == 302903437) and variables.porn)
        def send_butts(message, attempt=0):
            adults.send_butts(message, attempt)


        @bot.message_handler(commands=['boobs'],
                             func=lambda msg: (utils.is_from_group(msg.from_user.id) or msg.from_user.id == 302903437) and variables.porn)
        def send_boobs(message, attempt=0):
            adults.send_boobs(message, attempt)

        # ADMIN UTILS
        @bot.message_handler(commands=['addpole'], func=lambda msg: msg.from_user.id == admin_id)
        def add_pole(message):
            text = message.text[9::]
            variables.poles = [int(text), 0, 0]
            bot.reply_to(message, str(variables.poles))


        @bot.message_handler(commands=['addsubpole'], func=lambda msg: msg.from_user.id == admin_id)
        def add_subpole(message):
            text = message.text[12::]
            variables.poles = [0, int(text), 0]
            bot.reply_to(message, str(variables.poles))


        @bot.message_handler(commands=['cleanpoleS'], func=lambda msg: msg.from_user.id == admin_id)
        def clean_poles(message):
            variables.poles = []
            bot.reply_to(message, str(variables.poles))


        @bot.message_handler(commands=['photo'], func=lambda msg: msg.from_user.id == admin_id)
        def change_photo(message):
            global photo_ok
            if photo_ok:
                photo_ok = False
            else:
                photo_ok = True
            bot.reply_to(message, photo_ok)


        @bot.message_handler(commands=['setjorge'], func=lambda msg: msg.from_user.id == admin_id)
        def set_jorge_by_bot(message):
            if variables.jorge_despierto:
                variables.jorge_despierto = False
            else:
                variables.jorge_despierto = True


        @bot.message_handler(commands=['time'], func=lambda msg: msg.from_user.id == admin_id)
        def set_ban_time_by_bot(message):
            admin.set_ban_time_by_bot(message)


        @bot.message_handler(commands=['reportes'], func=lambda msg: msg.from_user.id == admin_id)
        def set_reportes(message):
            admin.set_num_reports_by_bot(message)


        @bot.message_handler(commands=['berserker'], func=lambda msg: msg.from_user.id == admin_id)
        def berserker_on(message):
            admin.berserker_on(message)


        @bot.message_handler(commands=['gett'], func=lambda msg: msg.from_user.id == admin_id)
        def get_t(message):
            bot.send_message(admin_id, '%s\n%s' % (utils.t, utils.t2))


        # OTHER COMMANDS
        @bot.message_handler(commands=['purge'], func=lambda msg: msg.chat.id == group_id)
        def purger(message):
            general.purger(message)


        @bot.message_handler(commands=['talk'], func=lambda msg: msg.chat.id == admin_id)
        def talk(message):
            general.talk(message)


        @bot.message_handler(commands=['demigrante'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def send_demigrante(message):
            general.send_demigrante(message)


        @bot.message_handler(commands=['shh'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def send_shh(message):
            general.send_shh(message)


        @bot.message_handler(commands=['alerta'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def send_alerta(message):
            general.send_alerta(message)


        @bot.message_handler(commands=['tq'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def send_tq(message):
            general.send_tq(message)


        @bot.message_handler(commands=['disculpa'], func=lambda msg: utils.is_from_group(msg.from_user.id))
        def send_disculpa(message):
            general.send_disculpa(message)


        def main():
            try:
                ts_utils.create_database()
                utils.create_database()
                for u in utils.get_userIds():
                    bot.unban_chat_member(group_id, u)
                if not utils.temporizado:
                    utils.run_timer()
            except Exception as exception:
                bot.send_message(admin_id, 'Error: %s' % exception)


        if __name__ == '__main__':
            main()

        bot.polling(none_stop=True)

    except Exception as e:
        print('Error: %s\nReiniciando en 10seg' % str(e))
        time.sleep(10)
