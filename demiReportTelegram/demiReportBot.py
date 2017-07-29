# -*- encoding: utf-8 -*-

import configparser
import io
import logging
import time
from datetime import datetime
import pkgutil

from reportTelegram import reportBot, utils
from reportTelegram import variables as report_variables
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
        user_id = message.new_chat_members[0].id
        sti = io.BufferedReader(io.BytesIO(pkgutil.get_data('demiReportTelegram', 'data/stickers/nancy_ok.webp')))
        bot.send_sticker(message.chat_id, sti)
        sti.close()
        if message.chat_id == group_id and not utils.is_from_group(user_id):
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


def send_selu_sticker(bot, update):
    message = update.message
    if message.chat_id != group_id:
        return False
    try:
        sti = io.BufferedReader(io.BytesIO(pkgutil.get_data('demiReportTelegram', 'data/stickers/selu.webp')))
        bot.send_sticker(message.chat_id, sti)
        sti.close()
    except:
        logger.error('Fatal error in send_selu_sticker', exc_info=True)


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
    return Filters.private(msg) and Filters.photo(msg) \
           and variables.poles \
           and int(msg.from_user.id) == variables.poles[0] \
           and datetime.today().weekday() == 5 \
           and photo_ok


def filter_group_name_reward(msg):
    return Filters.private(msg) and Filters.text(msg) and not Filters.command(msg) \
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


def bot_ia(bot, update):
    message = update.message
    res = demi_utils.get_bot_ia(message.text)
    bot.send_message(message.chat_id, res, reply_to_message_id=message.message_id, parse_mode='Markdown')


def gett(bot, update, job_queue):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text=str(job_queue.queue.queue), reply_to_message_id=message.message_id)


def set_mute_time(bot, update, args):
    message = update.message
    seconds = args[0]
    if seconds.isdigit():
        variables.MUTE_TIME = int(seconds)
        m, s = divmod(variables.MUTE_TIME, 60)
        mute_time_text = '%01d:%02d' % (m, s)
        res = 'MUTE TIME A {0} MINUTOS'.format(mute_time_text)
        chat_id = group_id
    else:
        res = 'Send me a number like "/mutetime 5"'
        chat_id = message.chat_id
    bot.send_message(chat_id, res)


def cancel(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text='Eres tonto hasta para esto...',
                    reply_to_message_id=message.message_id,
                    reply_markup=ReplyKeyboardRemove(selective=True))
    return ConversationHandler.END


def pin(bot, update):
    message = update.message.reply_to_message
    if message is not None:
        bot.pinChatMessage(chat_id=group_id, message_id=message.message_id, disable_notification=True)


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
    report_variables.user_data_dict = dp.user_data

    demi_utils.pole_timer(updater.job_queue)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('stats', reportBot.stats, filter_is_from_group))
    dp.add_handler(CommandHandler('expulsados', reportBot.top_kicks, filter_is_from_group))
    dp.add_handler(CommandHandler('who', reportBot.who, filter_is_from_group))
    dp.add_handler(CommandHandler('reports', reportBot.set_reports, filter_is_from_group, pass_args=True))
    dp.add_handler(CommandHandler('bantime', reportBot.set_ban_time, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(CommandHandler('mutetime', set_mute_time, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_to_member))
    dp.add_handler(CommandHandler('sipower', power_on, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('nopower', power_off, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('ts', utils_teamspeak.ts_view, filter_is_from_group))
    dp.add_handler(CommandHandler('whots', teamspeak.ts_stats, filter_is_from_group))
    dp.add_handler(CommandHandler('troll', set_troll, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION) & not_forwarded, mention_handler))
    dp.add_handler(RegexHandler(r'(?i).*hipertextual.com|.*twitter\.com\/Hipertextual', hipermierda))
    dp.add_handler(RegexHandler(r'(?i)(?=.*es)(?=.*raulito)(?=.*oro)?', raulito_oro))
    dp.add_handler(RegexHandler(r'(?i).*y no [\w ]+ a[l]? selu\?.*', send_selu_sticker))
    dp.add_handler(RegexHandler(r'(?i).*bot.*', bot_ia))
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
    dp.add_handler(CommandHandler('no18', stop_18, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('si18', start_18, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('pin', pin, Filters.user(user_id=admin_id)))
    dp.add_handler(
        CommandHandler('butts', adults.send_butts, lambda msg: variables.porn and filter_is_from_group))
    dp.add_handler(
        CommandHandler('boobs', adults.send_boobs, lambda msg: variables.porn and filter_is_from_group))
    dp.add_handler(CommandHandler('addpole', add_pole, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(
        CommandHandler('addsubpole', add_subpole, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(CommandHandler('cleanpoles', clean_poles, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('talk', talk, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(CommandHandler('purge', general.purger, filter_is_from_group))
    dp.add_handler(CommandHandler('demigrante', general.send_demigrante, filter_is_from_group))
    dp.add_handler(CommandHandler('shh', general.send_shh, filter_is_from_group))
    dp.add_handler(CommandHandler('ninoninini', general.send_ninoninini, filter_is_from_group))
    dp.add_handler(CommandHandler('alerta', general.send_alerta, filter_is_from_group))
    dp.add_handler(CommandHandler('tq', general.send_tq, filter_is_from_group))
    dp.add_handler(CommandHandler('disculpa', general.send_disculpa, filter_is_from_group))
    dp.add_handler(CommandHandler('locura', general.send_locura, filter_is_from_group))
    dp.add_handler(CommandHandler('mecagoenlamadrequemepario', general.send_gritopokemon, filter_is_from_group))
    dp.add_handler(CommandHandler('gett', gett, Filters.user(user_id=admin_id), pass_job_queue=True))
    dp.add_handler(CallbackQueryHandler(mentions.callback_query_handler, pass_user_data=True, pass_job_queue=True))
    dp.add_handler(CommandHandler('pipas', mentions.who_pipas, filter_is_from_group))
    dp.add_handler(CommandHandler('repipas', mentions.recover_pipas, filter_is_from_group))
    dp.add_handler(CommandHandler('mention', mentions.mention_control, filter_is_from_group))

    for name in utils.get_names():
        dp.add_handler(CommandHandler(name.lower(), reportBot.report, Filters.chat(chat_id=group_id)))

    headshot_handler = ConversationHandler(
        entry_points=[CommandHandler('headshot', poles.pre_headshot, filter_is_from_group)],
        states={
            0: [RegexHandler('^(%s)$' % '|'.join(utils.get_names()), poles.headshot)],
        },

        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('mute', cancel)]
    )
    dp.add_handler(headshot_handler)

    mute_handler = ConversationHandler(
        entry_points=[CommandHandler('mute', poles.pre_mute, filter_is_from_group)],
        states={
            0: [RegexHandler('^(%s)$' % '|'.join(utils.get_names()), poles.mute)],
        },

        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('headshot', cancel)]
    )
    dp.add_handler(mute_handler)

    dp.add_error_handler(log_error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
