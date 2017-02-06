# -*- encoding: utf-8 -*-

import configparser
import io
import logging
import time
from datetime import datetime
import pkgutil

from reportTelegram import reportBot, utils
from teamSpeakTelegram import teamspeak
from teamSpeakTelegram import utils as utils_teamspeak
from telegram import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, InlineQueryHandler, \
    ChosenInlineResultHandler, CommandFilterHandler

from demiReportTelegram import adults, general, mentions, poles, variables, songs
from demiReportTelegram import utils as demi_utils

admin_id = variables.admin_id
group_id = variables.group_id
photo_ok = True

config = configparser.ConfigParser()
config.read('config.ini')

TG_TOKEN = config['Telegram']['token']


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text='F*CK U', reply_to_message_id=message.message_id)


def welcome_or_bye_to_member(bot, update):
    message = update.message
    try:
        if message.new_chat_member:
            user_id = message.new_chat_member.id
            sti = io.BufferedReader(io.BytesIO(pkgutil.get_data('demiReportTelegram', 'data/stickers/nancy_ok.webp')))
            bot.send_sticker(variables.group_id, sti)
            sti.close()
            if not utils.is_from_group(user_id):
                variables.add_new_member(user_id)
                bot.send_message(variables.admin_id, user_id)
        elif message.left_chat_member:
            user_id = message.left_chat_member.id
            sti = io.BufferedReader(io.BytesIO(pkgutil.get_data('demiReportTelegram', 'data/stickers/nancy.webp')))
            sti2 = io.BufferedReader(io.BytesIO(pkgutil.get_data('demiReportTelegram', 'data/stickers/nancy.webp')))
            bot.send_sticker(variables.group_id, sti)
            bot.send_sticker(user_id, sti2)
            sti.close()
            sti2.close()
    except:
        logger.error('Fatal error in welcome_or_bye_to_member', exc_info=True)


# ADMIN POWER
def power_on(bot, update):
    demi_utils.set_power(2)
    bot.send_message(group_id, 'Selu activó sus poderes')


def power_off(bot, update):
    demi_utils.set_power(0)
    bot.send_message(group_id, 'Selu desactivó sus poderes')


# MENTIONS
def set_troll(bot, update, args):
    message = update.message
    target = args[0]
    if target.isdigit():
        res = mentions.set_troll(int(target))
        chat_id = group_id
    else:
        res = 'Send me a number like "/troll 8548545"'
        chat_id = message.chat_id
    bot.send_message(chat_id, res)


def mention_handler(bot, update):
    message = update.message
    if message.chat_id == group_id and message.from_user.id not in demi_utils.get_trolls():
        mentions.mention_handler(bot, message)


def mention_toggle(bot, update):
    message = update.message
    res = mentions.mention_toggle(message.from_user.id)
    bot.send_message(message.chat_id, res, reply_to_message_id=message.message_id)


def hipermierda(bot, update):
    message = update.message
    user_id = message.from_user.id
    if message.chat_id != group_id:
        return False
    text = 'Que le jodan a Gabriela y que le jodan a Ford PUTOS ANORMALES FOLLAIOS'
    bot.send_message(group_id, text, reply_to_message_id=message.message_id)
    bot.kick_chat_member(group_id, user_id)
    bot.unban_chat_member(group_id, user_id)
    button = InlineKeyboardButton('Invitación', url=variables.link)
    markup = InlineKeyboardMarkup([[button]])
    bot.send_message(user_id, 'Jiji entra anda:', reply_markup=markup)


def raulito_oro(bot, update):
    message = update.message
    if message.chat_id != group_id:
        return False
    bot.send_message(message.chat_id, 'No, todavía no', reply_to_message_id=message.message_id)


# SONGS
def flooder(user_data, job_queue):
    if 'flood' in user_data and user_data['flood'] > 0:
        user_data['flood'] -= 1
        if user_data['flood'] == 0:
            job_queue.run_once(clear_flooder, 300, context=user_data)
    elif 'flood' not in user_data:
        user_data['flood'] = 5
    return user_data['flood'] == 0


def clear_flooder(bot, job):
    user_data = job.context
    user_data['flood'] = 5


def inline_query(bot, update):
    songs.inline_query(bot, update)


def inline_result(bot, update, user_data, job_queue):
    from_id = update.chosen_inline_result.from_user.id
    if utils.is_from_group(from_id) and not flooder(user_data, job_queue):
        songs.inline_result(bot, update)


def pole_handler(bot, update):
    message = update.message
    if message.chat_id == group_id and time.strftime('%H') == '00':
        res = poles.pole_handler(message.from_user.id)
        bot.send_message(message.chat_id, res, reply_to_message_id=message.message_id)


def subpole_handler(bot, update):
    message = update.message
    if message.chat_id == group_id and time.strftime('%H') == '00':
        res = poles.subpole_handler(message.from_user.id)
        bot.send_message(message.chat_id, res, reply_to_message_id=message.message_id)


def tercercomentario_handler(bot, update):
    message = update.message
    if message.chat_id == group_id and time.strftime('%H') == '00':
        res = poles.tercercomentario_handler(message.from_user.id)
        bot.send_message(message.chat_id, res, reply_to_message_id=message.message_id)


def ranking(bot, update):
    message = update.message
    res = poles.get_ranking()
    bot.send_message(message.chat_id, res, parse_mode='Markdown')


def filter_pole_reward(msg):
    return msg.chat.type == 'private' and variables.poles \
           and int(msg.from_user.id) == variables.poles[0] \
           and datetime.today().weekday() == 5 \
           and photo_ok


def filter_group_name_reward(msg):
    return msg.chat.type == 'private' and msg.text[0] != '/' \
           and variables.poles \
           and (int(msg.from_user.id) == variables.poles[1] or int(msg.from_user.id) == variables.poles[2]) \
           and datetime.today().weekday() == 5


# +18
def stop_18(bot, update):
    message = update.message
    variables.porn = False
    bot.send_message(message.chat_id, 'Cesen con las pajas', reply_to_message_id=message.message_id)


def start_18(bot, update):
    message = update.message
    variables.porn = True
    bot.send_message(message.chat_id, 'Delen a las pajas', reply_to_message_id=message.message_id)


# ADMIN UTILS
def add_pole(bot, update, args):
    message = update.message
    target = args[0]
    if target.isdigit():
        variables.poles = [int(target), 0, 0]
        res = str(variables.poles)
    else:
        res = 'Send me a number like "/addpole 8548545"'
    bot.send_message(message.chat_id, res, reply_to_message_id=message.message_id)


def add_subpole(bot, update, args):
    message = update.message
    target = args[0]
    if target.isdigit():
        variables.poles = [0, int(target), 0]
        res = str(variables.poles)
    else:
        res = 'Send me a number like "/addpole 8548545"'
    bot.send_message(message.chat_id, res, reply_to_message_id=message.message_id)


def clean_poles(bot, update):
    message = update.message
    variables.poles = []
    bot.send_message(message.chat_id, str(variables.poles), reply_to_message_id=message.message_id)


# OTHER COMMANDS
def talk(bot, update, args):
    text = ' '.join(args)
    if text:
        bot.send_message(group_id, text)


def gett(bot, update, job_queue):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text=str(job_queue.queue.queue), reply_to_message_id=message.message_id)


def log_error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def filter_is_from_group(msg):
    return utils.is_from_group(msg.from_user.id)


def main():
    utils_teamspeak.create_database()
    utils.create_database()
    demi_utils.create_database()

    updater = Updater(token=TG_TOKEN)
    dp = updater.dispatcher

    demi_utils.pole_timer(updater.job_queue)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandFilterHandler('stats', filter_is_from_group, reportBot.stats))
    dp.add_handler(CommandFilterHandler('expulsados', filter_is_from_group, reportBot.top_kicks))
    dp.add_handler(CommandFilterHandler('who', filter_is_from_group, reportBot.who))
    dp.add_handler(CommandFilterHandler('reports', filter_is_from_group, reportBot.set_reports, pass_args=True))
    dp.add_handler(CommandFilterHandler('bantime', lambda msg: msg.from_user.id == admin_id,
                                        reportBot.set_ban_time, pass_args=True))
    dp.add_handler(MessageHandler(Filters.status_update, welcome_or_bye_to_member))
    dp.add_handler(CommandFilterHandler('sipower', lambda msg: msg.from_user.id == admin_id, power_on))
    dp.add_handler(CommandFilterHandler('nopower', lambda msg: msg.from_user.id == admin_id, power_off))
    dp.add_handler(CommandFilterHandler('ts', filter_is_from_group, teamspeak.ts_stats))
    dp.add_handler(CommandFilterHandler('troll', lambda msg: msg.from_user.id == admin_id, set_troll, pass_args=True))
    dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION), mention_handler))
    dp.add_handler(CommandFilterHandler('mention', filter_is_from_group, mention_toggle))
    dp.add_handler(RegexHandler(r'(?i).*hipertextual.com|.*twitter\.com\/Hipertextual', hipermierda))
    dp.add_handler(RegexHandler(r'(?i)(?=.*es)(?=.*raulito)(?=.*oro)?', raulito_oro))
    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_handler(ChosenInlineResultHandler(inline_result, pass_user_data=True, pass_job_queue=True))
    dp.add_handler(RegexHandler(r'(?i)po+le+.*', pole_handler))
    dp.add_handler(RegexHandler(r'(?i)su+bpo+le+.*', subpole_handler))
    dp.add_handler(RegexHandler(r'(?i)tercer comentario+.*', tercercomentario_handler))
    dp.add_handler(CommandFilterHandler('ranking', filter_is_from_group, ranking))
    dp.add_handler(CommandFilterHandler('nuke', filter_is_from_group, poles.send_nuke))
    dp.add_handler(CommandFilterHandler('perros', filter_is_from_group, poles.send_perros))
    dp.add_handler(MessageHandler(filter_pole_reward, poles.change_group_photo_bot))
    dp.add_handler(MessageHandler(filter_group_name_reward, poles.change_group_name_bot))
    dp.add_handler(CommandFilterHandler('no18', lambda msg: msg.from_user.id == admin_id, stop_18))
    dp.add_handler(CommandFilterHandler('si18', lambda msg: msg.from_user.id == admin_id, start_18))
    dp.add_handler(
        CommandFilterHandler('butts', lambda msg: variables.porn and filter_is_from_group, adults.send_butts))
    dp.add_handler(
        CommandFilterHandler('boobs', lambda msg: variables.porn and filter_is_from_group, adults.send_butts))
    dp.add_handler(CommandFilterHandler('addpole', lambda msg: msg.from_user.id == admin_id, add_pole, pass_args=True))
    dp.add_handler(
        CommandFilterHandler('addsubpole', lambda msg: msg.from_user.id == admin_id, add_subpole, pass_args=True))
    dp.add_handler(CommandFilterHandler('cleanpoles', lambda msg: msg.from_user.id == admin_id, clean_poles))
    dp.add_handler(CommandFilterHandler('talk', lambda msg: msg.from_user.id == admin_id, talk, pass_args=True))
    dp.add_handler(CommandFilterHandler('purge', filter_is_from_group, general.purger))
    dp.add_handler(CommandFilterHandler('demigrante', filter_is_from_group, general.send_demigrante))
    dp.add_handler(CommandFilterHandler('shh', filter_is_from_group, general.send_shh))
    dp.add_handler(CommandFilterHandler('alerta', filter_is_from_group, general.send_alerta))
    dp.add_handler(CommandFilterHandler('tq', filter_is_from_group, general.send_tq))
    dp.add_handler(CommandFilterHandler('disculpa', filter_is_from_group, general.send_disculpa))
    dp.add_handler(CommandHandler("gett", gett, pass_job_queue=True))

    for name in utils.get_names():
        dp.add_handler(CommandFilterHandler(name.lower(), lambda msg: msg.chat_id == group_id, reportBot.report))

    dp.add_error_handler(log_error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
