# -*- encoding: utf-8 -*-

import configparser
import io
import logging
import os
import re
import time
import datetime
import pkgutil
import pushover
import pymysql

from reportTelegram import reportBot, utils, reports
from reportTelegram import variables as report_variables
from telegram import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, InlineQueryHandler, \
    ChosenInlineResultHandler, ConversationHandler, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from telegram.ext.filters import MergedFilter, InvertedFilter

from demiReportTelegram import adults, general, mentions, poles, variables, songs
from demiReportTelegram import utils as demi_utils


admin_id = variables.admin_id
group_id = variables.group_id
photo_ok = True

config = configparser.ConfigParser()
config.read('config.ini')

TG_TOKEN = config['Telegram']['token']
PORT = int(os.environ.get('PORT', '8443'))

DB_HOST = variables.DB_HOST
DB_USER = variables.DB_USER
DB_PASS = variables.DB_PASS
DB_NAME = variables.DB_NAME
EXTERNAL_HOST = variables.EXTERNAL_HOST

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

wanted_words = list()


def start(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text='F*CK U', reply_to_message_id=message.message_id)


def welcome_to_member(bot, update, job_queue):
    message = update.message
    try:
        user_id = message.new_chat_members[0].id
        sti = io.BufferedReader(io.BytesIO(pkgutil.get_data('demiReportTelegram', 'data/stickers/nancy_ok.webp')))
        msg_sticker = bot.send_sticker(message.chat_id, sti)
        sti.close()
        if message.chat_id == group_id and not utils.is_from_group(user_id):
            variables.add_new_member(user_id)
            bot.send_message(variables.admin_id, user_id)
        job_queue.run_once(demi_utils.remove_message, 30, context=(message.chat_id, msg_sticker.message_id))
    except:
        logger.error('Fatal error in welcome_to_member', exc_info=True)


# ADMIN POWER
def power_on(bot, update):
    chat_member = bot.get_chat_member(group_id, admin_id)
    if chat_member.status == 'kicked':
        bot.unban_chat_member(group_id, admin_id)
        bot.send_message(admin_id, 'Desbaneado')
    else:
        bot.promote_chat_member(group_id, admin_id, can_restrict_members=True, can_change_info=True)
        bot.send_message(group_id, 'Selu activó sus poderes')


def power_off(bot, update):
    bot.promote_chat_member(group_id, admin_id, can_restrict_members=False)
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
    message = update.effective_message
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


def viva_españa(bot, update):
    message = update.message
    if message.chat_id != group_id:
        return False
    bot.send_message(message.chat_id, 'CLARO QUE SI JODER', reply_to_message_id=message.message_id)


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


def ranking_gasta_puntos(bot, update):
    message = update.message
    res = poles.get_ranking_gasta_puntos()
    bot.send_message(message.chat_id, res, parse_mode='Markdown')


def filter_pole_reward(msg):
    return Filters.private(msg) and Filters.photo(msg) \
           and variables.poles \
           and int(msg.from_user.id) == variables.poles[0] \
           and datetime.datetime.today().weekday() == 5 \
           and photo_ok


def filter_group_name_reward(msg):
    return Filters.private(msg) and Filters.text(msg) and not Filters.command(msg) \
           and variables.poles \
           and (int(msg.from_user.id) == variables.poles[1] or int(msg.from_user.id) == variables.poles[2]) \
           and datetime.datetime.today().weekday() == 5


def filter_wanted_words(msg):
    return wanted_words and Filters.text(msg) and not Filters.forwarded(msg) and not Filters.command(msg) and \
           bool(re.search('\\b' + '\\b|\\b'.join(wanted_words) + '\\b', msg.text, re.IGNORECASE))


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


@run_async
def notify(bot, update, args):
    text = ' '.join(args)
    text = text.replace('\\n', '\n')
    if text:
        for user_id in demi_utils.get_user_ids():
            try:
                bot.send_message(user_id, text, parse_mode='Markdown')
            except:
                pass


def gett(bot, update, job_queue):
    message = update.message
    res = [datetime.datetime.fromtimestamp(job[0]).strftime('%d/%m/%Y %H:%M:%S') + " -> " + str(job[1].name)
           for job in job_queue.queue.queue]
    bot.sendMessage(chat_id=message.chat_id, text='\n'.join(res), reply_to_message_id=message.message_id)


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


def cancelDuelo(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text='Cagao, que eres un cagao...',
                    reply_to_message_id=message.message_id,
                    reply_markup=ReplyKeyboardRemove(selective=True))
    return ConversationHandler.END


def cancelApuesta(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text='Tantos puntos y tan pocos cojones...',
                    reply_to_message_id=message.message_id,
                    reply_markup=ReplyKeyboardRemove(selective=True))
    return ConversationHandler.END


def clean_keyboard(bot, update):
    message = update.message
    msg = bot.sendMessage(chat_id=message.chat_id, text='Limpiando teclado...',
                          reply_to_message_id=message.message_id,
                          reply_markup=ReplyKeyboardRemove(selective=True))
    bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
    bot.delete_message(chat_id=message.chat_id, message_id=msg.message_id)


def done(bot, update):
    message = update.message
    bot.sendMessage(chat_id=message.chat_id, text='ALRIGHT',
                    reply_to_message_id=message.message_id,
                    reply_markup=ReplyKeyboardRemove(selective=True))
    return ConversationHandler.END


def pin(bot, update):
    message = update.message.reply_to_message
    if message is not None:
        bot.pinChatMessage(chat_id=group_id, message_id=message.message_id, disable_notification=True)


def safe_report(bot, update, job_queue):
    message = update.message
    user_id = message.from_user.id
    command = message.text.split('@')[0].split(' ')[0]
    name = command.replace('/', '').capitalize()
    reported = utils.get_user_id(name)
    if reported == user_id:
        bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
    else:
        reports.send_report(bot, user_id, reported, job_queue)


def safe_love(bot, update, job_queue):
    message = update.message
    user_id = message.from_user.id
    command = message.text.split('@')[0].split(' ')[0]
    name = command.replace('/love', '').capitalize()
    loved = utils.get_user_id(name)
    if loved == user_id:
        bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
    else:
        reports.send_love(bot, user_id, loved, job_queue)


def send_wanted_word(bot, update):
    message = update.message
    user_id = message.from_user.id
    words = list()
    for wanted_word in wanted_words:
        word = re.search('\\b'+wanted_word+'\\b', message.text, re.IGNORECASE)
        if word:
            words.append(word.group(0))
    targets = list()

    for word in words:
        targets.extend(demi_utils.get_users_from_word(word))

    for target_id in set(targets):
        if int(target_id) == int(admin_id) and target_id != user_id:
            pushover.Client(variables.pushover_client) \
                .send_message(update.message.text, title=utils.get_name(user_id), priority=-1)

        elif target_id != user_id:
            bot.forward_message(target_id, message.chat.id, message.message_id)


def pre_add_wanted_word(bot, update):
    message = update.message
    user_id = message.from_user.id

    if message.chat_id != user_id:
        bot.send_message(message.chat_id, 'Este comando no puede ser usado en un grupo, abre mp.',
                         reply_to_message_id=message.message_id)
        return ConversationHandler.END

    bot.send_message(user_id, 'Ok, envía una mensaje por palabra o frase exacta que quieres que te notifique.'
                                      '\n\nPara acabar pulsa /done', reply_to_message_id=message.message_id)
    return 0


def add_wanted_word(bot, update):
    message = update.message
    user_id = message.from_user.id
    word = message.text

    if demi_utils.is_wanted_word(word, user_id):
        message.reply_text('Esa palabra ya existe')
        return

    elif len(word) > 100:
        message.reply_text('No me escribas el quijote tampoco cabron')
        return

    elif len(demi_utils.get_wanted_words(user_id)) >= 20:
        message.reply_text('Uff ya tienes muchas, quitame alguna antes anda')
        return ConversationHandler.END

    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO WantedWords(word, userId) VALUES(%s, %s)",
                        (str(word), str(user_id)))
        wanted_words.append(message.text)
        message.reply_text('Palabra "%s" añadida' % message.text)

    except Exception:
        logger.error('Fatal error in add_wanted_word', exc_info=True)
    finally:
        if con:
            con.commit()
            con.close()


def manage_wanted_word(bot, update, edit_message=False):
    message = update.effective_message
    user_id = update.effective_user.id
    chat_id = message.chat_id
    words = demi_utils.get_wanted_words(user_id)
    text = "👀 *Wanted Words*\n\n"

    keyboard = list()
    for word_id in list(words):
        word = words[word_id]
        keyboard.append([InlineKeyboardButton(word, callback_data='DELWORD_%i' % word_id)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if message.chat_id != user_id and not edit_message:
        bot.send_message(chat_id, 'TIENES MP', reply_to_message_id=message.message_id)

    if edit_message:
        if len(words) == 0:
            bot.edit_message_text(chat_id=user_id,
                                  text=text + 'No tienes ninguna palabra de aviso todavía. Para añadir alguna usa /addword',
                                  message_id=message.message_id, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            bot.edit_message_reply_markup(reply_markup=reply_markup, chat_id=chat_id,
                                          message_id=message.message_id)
    else:
        if len(words) == 0:
            text += 'No tienes ninguna palabra de aviso todavía. Para añadir alguna usa /addword'
        else:
            text += 'Estas son las palabras (pulsa sobre cualquiera para eliminarla):'

        bot.send_message(user_id, text, reply_markup=reply_markup, parse_mode='Markdown')


def log_error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def filter_is_from_group(msg):
    return utils.is_from_group(msg.from_user.id)


def not_forwarded(msg):
    return not bool(msg.forward_date)


def login_account(bot, job):
    demi_utils.login_account()


def pole_timer(job_queue):
    x = datetime.datetime.today()
    y = x.replace(day=x.day, hour=23, minute=59, second=55, microsecond=0)
    y2 = x.replace(day=x.day, hour=1, minute=00, second=00, microsecond=0) + datetime.timedelta(days=1)
    delta_t = y - x
    delta_t2 = y2 - x
    secs = delta_t.seconds + 1
    secs2 = delta_t2.seconds + 1
    job_queue.run_daily(callback=demi_utils.pole_counter, time=secs)
    job_queue.run_daily(callback=poles.run_daily_perros, time=secs-20)
    job_queue.run_daily(callback=poles.daily_reward, time=secs+60)
    job_queue.run_daily(callback=variables.clean_poles, time=secs2)
    job_queue.run_repeating(callback=login_account, interval=datetime.timedelta(days=30), first=5)


class CommandHandlerFlood(CommandHandler):
    def handle_update(self, update, dispatcher):
        user_id = update.message.from_user.id
        if user_id == 296066710 and update.message.chat.type != 'private' \
                and demi_utils.flooder(dispatcher.user_data[user_id], dispatcher.job_queue, 2):
            dispatcher.bot.restrict_chat_member(group_id, user_id, can_send_messages=False,
                                                until_date=time.time() + 60)

        return super(CommandHandlerFlood, self).handle_update(update, dispatcher)


def callback_query_handler(bot, update, user_data, job_queue, chat_data):
    query_data = update.callback_query.data
    message = update.effective_message
    if query_data.startswith('PIPAS_UPDATE'):
        if demi_utils.get_who_pipas().strip() == message.text_markdown:
            bot.answer_callback_query(update.callback_query.id, 'Sin cambios')
        else:
            mentions.who_pipas(bot, update, message_id=message.message_id, chat_id=update.effective_chat.id)
            bot.answer_callback_query(update.callback_query.id, 'Actualizado correctamente')
    elif query_data.startswith('MENTION'):
        mentions.post_mention_control(bot, update, user_data, job_queue)
    elif query_data.startswith('STATS_UPDATE'):
        reports.callback_query_handler(bot, update, user_data, job_queue, chat_data)
    elif query_data.startswith('MINECRAFT_UPDATE'):
        if demi_utils.get_who_minecraft().strip() == message.text_markdown:
            bot.answer_callback_query(update.callback_query.id, 'Sin cambios')
        else:
            demi_utils.send_who_minecraft(bot, update, message_id=message.message_id,
                                          chat_id=update.effective_chat.id)
            bot.answer_callback_query(update.callback_query.id, 'Actualizado correctamente')
    elif query_data.startswith('DELWORD'):
        try:
            word_id = int(query_data.split('DELWORD_')[1])
            wanted_words.remove(demi_utils.get_word(word_id))
            demi_utils.remove_wanted_word(word_id)
            bot.answer_callback_query(update.callback_query.id, 'Palabra eliminada')
        except:
            bot.answer_callback_query(update.callback_query.id, 'Esta palabra no existe')

        manage_wanted_word(bot, update, edit_message=True)

    else:
        mentions.pipas_selected(bot, update, user_data, job_queue)


def main():
    #utils.create_database()
    #demi_utils.create_database()

    updater = Updater(token=TG_TOKEN, workers=32)
    dp = updater.dispatcher
    report_variables.user_data_dict = dp.user_data
    pushover.init(variables.pushover_token)

    wanted_words.extend(demi_utils.get_all_words())

    pole_timer(updater.job_queue)

    dp.add_handler(CommandHandlerFlood('start', start))
    dp.add_handler(CommandHandlerFlood('stats', reports.send_stats, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('expulsados', reportBot.top_kicks, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('who', reportBot.who, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('reports', reportBot.set_reports, filter_is_from_group, pass_args=True))
    dp.add_handler(CommandHandler('bantime', reportBot.set_ban_time, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(CommandHandler('mutetime', set_mute_time, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_to_member, pass_job_queue=True))
    dp.add_handler(CommandHandler('sipower', power_on, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('nopower', power_off, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('troll', set_troll, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION) & not_forwarded, mention_handler))
    dp.add_handler(RegexHandler(r'(?i)[\s\S]*hipertextual.com|[\s\S]*twitter\.com\/Hipertextual|[\s\S]*hiper.click',
                                hipermierda, edited_updates=True))
    dp.add_handler(RegexHandler(r'(?i)(?=.*viva)(?=.*españa)(?=.*franco)?', viva_españa))
    dp.add_handler(RegexHandler(r'(?i).*y no [\w ]+ a[l]? selu\?.*', send_selu_sticker))
    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_handler(ChosenInlineResultHandler(inline_result, pass_user_data=True, pass_job_queue=True))
    dp.add_handler(RegexHandler(r'(?i)po+le+.*', pole_handler))
    dp.add_handler(RegexHandler(r'(?i)su+bpo+le+.*', subpole_handler))
    dp.add_handler(RegexHandler(r'(?i)tercer comentario+.*', tercercomentario_handler))
    dp.add_handler(CommandHandlerFlood('ranking', ranking, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('gastados', ranking_gasta_puntos, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('nuke', poles.send_nuke, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('perros', poles.send_perros, filter_is_from_group))
    dp.add_handler(MessageHandler(filter_pole_reward, poles.change_group_photo_bot))
    dp.add_handler(MessageHandler(filter_group_name_reward, poles.change_group_name_bot))
    dp.add_handler(CommandHandler('no18', stop_18, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('si18', start_18, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('pin', pin, Filters.user(user_id=admin_id)))
    dp.add_handler(
        CommandHandlerFlood('butts', adults.send_butts, lambda msg: variables.porn and filter_is_from_group))
    dp.add_handler(
        CommandHandlerFlood('boobs', adults.send_boobs, lambda msg: variables.porn and filter_is_from_group))
    dp.add_handler(CommandHandler('addpole', add_pole, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(
        CommandHandler('addsubpole', add_subpole, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(CommandHandler('cleanpoles', clean_poles, Filters.user(user_id=admin_id)))
    dp.add_handler(CommandHandler('talk', talk, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(CommandHandler('notify', notify, Filters.user(user_id=admin_id), pass_args=True))
    dp.add_handler(CommandHandlerFlood('purge', general.purger, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('demigrante', general.send_demigrante, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('shh', general.send_shh, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('ninoninini', general.send_ninoninini, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('alerta', general.send_alerta, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('tq', general.send_tq, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('callate', general.send_callate, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('disculpa', general.send_disculpa, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('locura', general.send_locura, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('mecagoenlamadrequemepario', general.send_gritopokemon, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('hijodecuatrocientossetenta',
                                       general.send_futbol_audio, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('queeeeeeeeeeeeeeeeeeeeeeeeeeeeee', general.send_queeee_audio,
                                       filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('meperd0nas', general.send_meperdonas_audio, filter_is_from_group))
    dp.add_handler(CommandHandler('gett', gett, Filters.user(user_id=admin_id), pass_job_queue=True))
    dp.add_handler(CallbackQueryHandler(callback_query_handler, pass_user_data=True, pass_job_queue=True,
                                        pass_chat_data=True))
    dp.add_handler(CommandHandlerFlood('pipas', mentions.who_pipas, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('repipas', mentions.recover_pipas, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('mention', mentions.mention_control, filter_is_from_group))
    dp.add_handler(CommandHandlerFlood('minecraft', demi_utils.send_who_minecraft, filter_is_from_group))
    dp.add_handler(CommandHandler('words', manage_wanted_word))

    # Lovedomingo
    # dp.add_handler(CommandHandlerFlood('lovedomingo', safe_love,
    #                                    MergedFilter(Filters.chat(chat_id=group_id),
    #                                                 and_filter=filter_is_from_group),
    #                                    pass_job_queue=True))
    for name in utils.get_names():
        dp.add_handler(CommandHandlerFlood(name.lower(), safe_report,
                                           MergedFilter(Filters.chat(chat_id=group_id), and_filter=filter_is_from_group),
                                           pass_job_queue=True))
        # dp.add_handler(CommandHandlerFlood('love' + name.lower(), safe_love,
        #                                    MergedFilter(Filters.chat(chat_id=group_id),
        #                                                 and_filter=filter_is_from_group),
        #                                    pass_job_queue=True))

    headshot_handler = ConversationHandler(
        entry_points=[CommandHandlerFlood('headshot', poles.pre_headshot, filter_is_from_group)],
        states={
            0: [RegexHandler('^(%s)$' % '|'.join(utils.get_names()), poles.headshot, pass_job_queue=True)],
        },

        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('mute', cancel), CommandHandler('addword', cancel)]
    )
    dp.add_handler(headshot_handler)

    duelo_handler = ConversationHandler(
        entry_points=[CommandHandlerFlood('dudududuelo', poles.pre_duelo, filter_is_from_group)],
        states={
            0: [RegexHandler('^(%s)$' % '|'.join(utils.get_names()), poles.duelo, pass_job_queue=True)],
        },

        fallbacks=[CommandHandler('cancel', cancelDuelo), CommandHandler('mute', cancel), CommandHandler('addword', cancel)]
    )
    dp.add_handler(duelo_handler)

    apuesta_handler = ConversationHandler(
        entry_points=[CommandHandlerFlood('apuesta', poles.pre_apuesta, filter_is_from_group)],
        states={
            0: [RegexHandler('^[0-9]*$', poles.apuesta, pass_job_queue=True)],
        },

        fallbacks=[CommandHandler('cancel', cancelApuesta), CommandHandler('mute', cancel), CommandHandler('addword', cancel)]
    )
    dp.add_handler(apuesta_handler)

    mute_handler = ConversationHandler(
        entry_points=[CommandHandlerFlood('mute', poles.pre_mute, filter_is_from_group)],
        states={
            0: [RegexHandler('^(%s)$' % '|'.join(utils.get_names()), poles.mute)],
        },

        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('headshot', cancel),
                   CommandHandler('addword', cancel), CommandHandler('duelo', cancel)]
    )
    dp.add_handler(mute_handler)

    wanted_word_handler = ConversationHandler(
        entry_points=[CommandHandlerFlood('addword', pre_add_wanted_word, filter_is_from_group)],
        states={
            0: [MessageHandler(MergedFilter(Filters.text, and_filter=InvertedFilter(Filters.command)), add_wanted_word)],
        },

        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('done', done),
                   CommandHandler('headshot', cancel), CommandHandler('mute', cancel), CommandHandler('duelo', cancelDuelo),
                   CommandHandler('apuesta', cancelApuesta)]
    )
    dp.add_handler(wanted_word_handler)
    dp.add_handler(MessageHandler(filter_wanted_words, send_wanted_word))

    dp.add_handler(CommandHandler('cancel', clean_keyboard, MergedFilter(Filters.user(user_id=62394824),
                                                                         or_filter=Filters.user(user_id=57233245))))

    dp.add_error_handler(log_error)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TG_TOKEN)
    updater.bot.set_webhook(EXTERNAL_HOST + TG_TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
