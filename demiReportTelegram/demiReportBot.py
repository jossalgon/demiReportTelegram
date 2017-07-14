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
from telegram import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, InlineQueryHandler, \
    ChosenInlineResultHandler, ConversationHandler, CallbackQueryHandler

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


def welcome_to_member(bot, update):
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
    except:
        logger.error('Fatal error in welcome_to_member', exc_info=True)


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
def inline_query(bot, update):
    songs.inline_query(bot, update)


def inline_result(bot, update, user_data, job_queue):
    from_id = update.chosen_inline_result.from_user.id
    if utils.is_from_group(from_id) and not demi_utils.flooder(user_data, job_queue):
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
    return msg.chat.type == 'private' and bool(msg.photo) \
           and variables.poles \
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
    text = text.replace('\\n', '\n')
    if text:
        bot.send_message(group_id, text, parse_mode='Markdown')


def gett(bot, update, job_queue):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text=str(job_queue.queue.queue), reply_to_message_id=message.message_id)


def cancel(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text='Eres tonto hasta para esto...',
                    reply_to_message_id=message.message_id,
                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def log_error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def filter_is_from_group(msg):
    return utils.is_from_group(msg.from_user.id)


def not_forwarded(msg):
    return not bool(msg.forward_date)


def main():
    utils_teamspeak.create_database()
    utils.create_database()
    demi_utils.create_database()

    updater = Updater(token=TG_TOKEN, workers=32)
    dp = updater.dispatcher

    demi_utils.pole_timer(updater.job_queue)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('stats', reportBot.stats, filter_is_from_group))
    dp.add_handler(CommandHandler('expulsados', reportBot.top_kicks, filter_is_from_group))
    dp.add_handler(CommandHandler('who', reportBot.who, filter_is_from_group))
    dp.add_handler(CommandHandler('reports', reportBot.set_reports, filter_is_from_group, pass_args=True))
    dp.add_handler(CommandHandler('bantime', reportBot.set_ban_time, lambda msg: msg.from_user.id == admin_id,
                                  pass_args=True))
    dp.add_handler(MessageHandler(Filters.status_update, welcome_to_member))
    dp.add_handler(CommandHandler('sipower', power_on, lambda msg: msg.from_user.id == admin_id))
    dp.add_handler(CommandHandler('nopower', power_off, lambda msg: msg.from_user.id == admin_id))
    dp.add_handler(CommandHandler('ts', teamspeak.ts_stats, filter_is_from_group))
    dp.add_handler(CommandHandler('troll', set_troll, lambda msg: msg.from_user.id == admin_id, pass_args=True))
    dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION) & not_forwarded, mention_handler))
    dp.add_handler(RegexHandler(r'(?i).*hipertextual.com|.*twitter\.com\/Hipertextual', hipermierda))
    dp.add_handler(RegexHandler(r'(?i)(?=.*es)(?=.*raulito)(?=.*oro)?', raulito_oro))
    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_handler(ChosenInlineResultHandler(inline_result, pass_user_data=True, pass_job_queue=True))
    dp.add_handler(RegexHandler(r'(?i)po+le+.*', pole_handler))
    dp.add_handler(RegexHandler(r'(?i)su+bpo+le+.*', subpole_handler))
    dp.add_handler(RegexHandler(r'(?i)tercer comentario+.*', tercercomentario_handler))
    dp.add_handler(CommandHandler('ranking', ranking, filter_is_from_group))
    dp.add_handler(CommandHandler('nuke', poles.send_nuke, filter_is_from_group))
    dp.add_handler(CommandHandler('perros', poles.send_perros, filter_is_from_group))
    dp.add_handler(MessageHandler(filter_pole_reward, poles.change_group_photo_bot))
    dp.add_handler(MessageHandler(filter_group_name_reward, poles.change_group_name_bot))
    dp.add_handler(CommandHandler('no18', stop_18, lambda msg: msg.from_user.id == admin_id))
    dp.add_handler(CommandHandler('si18', start_18, lambda msg: msg.from_user.id == admin_id))
    dp.add_handler(
        CommandHandler('butts', adults.send_butts, lambda msg: variables.porn and filter_is_from_group))
    dp.add_handler(
        CommandHandler('boobs', adults.send_boobs, lambda msg: variables.porn and filter_is_from_group))
    dp.add_handler(CommandHandler('addpole', add_pole, lambda msg: msg.from_user.id == admin_id, pass_args=True))
    dp.add_handler(
        CommandHandler('addsubpole', add_subpole, lambda msg: msg.from_user.id == admin_id, pass_args=True))
    dp.add_handler(CommandHandler('cleanpoles', clean_poles, lambda msg: msg.from_user.id == admin_id))
    dp.add_handler(CommandHandler('talk', talk, lambda msg: msg.from_user.id == admin_id, pass_args=True))
    dp.add_handler(CommandHandler('purge', general.purger, filter_is_from_group))
    dp.add_handler(CommandHandler('demigrante', general.send_demigrante, filter_is_from_group))
    dp.add_handler(CommandHandler('shh', general.send_shh, filter_is_from_group))
    dp.add_handler(CommandHandler('alerta', general.send_alerta, filter_is_from_group))
    dp.add_handler(CommandHandler('tq', general.send_tq, filter_is_from_group))
    dp.add_handler(CommandHandler('disculpa', general.send_disculpa, filter_is_from_group))
    dp.add_handler(CommandHandler('locura', general.send_locura, filter_is_from_group))
    dp.add_handler(CommandHandler('mecagoenlamadrequemepario', general.send_gritopokemon, filter_is_from_group))
    dp.add_handler(CommandHandler('gett', gett, pass_job_queue=True))
    dp.add_handler(CallbackQueryHandler(mentions.callback_query_handler, pass_user_data=True, pass_job_queue=True))
    dp.add_handler(CommandHandler('pipas', mentions.who_pipas, filter_is_from_group))
    dp.add_handler(CommandHandler('repipas', mentions.recover_pipas, filter_is_from_group))
    dp.add_handler(CommandHandler('mention', mentions.mention_control, filter_is_from_group))

    for name in utils.get_names():
        dp.add_handler(CommandHandler(name.lower(), reportBot.report, lambda msg: msg.chat_id == group_id))

    headshot_handler = ConversationHandler(
        entry_points=[CommandHandler('headshot', poles.pre_headshot, filter_is_from_group)],
        states={
            0: [RegexHandler('^(%s)$' % '|'.join(utils.get_names()), poles.headshot)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(headshot_handler)

    dp.add_error_handler(log_error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
