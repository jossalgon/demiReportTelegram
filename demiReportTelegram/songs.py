# -*- encoding: utf-8 -*-
import io
import os
import pkgutil

import sys
from telegram import InlineQueryResultArticle, InputTextMessageContent

from reportTelegram import utils

from demiReportTelegram import variables


admin_id = variables.admin_id
group_id = variables.group_id


def inline_query(bot, update):
    results = list()

    results.append(InlineQueryResultArticle('1', 'Alien - Nunca me Faltes',
                                            InputTextMessageContent('Alien - Nunca me Faltes'),
                                            thumb_url='http://i.imgur.com/663CMAj.png'))
    results.append(InlineQueryResultArticle('2', 'El merengue del PP',
                                            InputTextMessageContent('El merengue del PP'),
                                            thumb_url='http://i.imgur.com/brP3eGU.png'))
    results.append(InlineQueryResultArticle('3', 'Seinfeld MLG remix (Skrillfeld)',
                                            InputTextMessageContent('Seinfeld MLG remix (Skrillfeld)'),
                                            thumb_url='https://imgur.com/XfgkG2v.png'))
    results.append(InlineQueryResultArticle('4', 'Niña, no te modernices (Payo Juan)',
                                            InputTextMessageContent('Niña, no te modernices (Payo Juan)'),
                                            thumb_url='https://imgur.com/x89UIt6.png'))
    results.append(InlineQueryResultArticle('5', 'Torres Gemelas (Delfín Quishpe)',
                                            InputTextMessageContent('Torres Gemelas (Delfín Quishpe)'),
                                            thumb_url='https://imgur.com/7ssC7xU.png'))
    results.append(InlineQueryResultArticle('6', 'Titanic en flauta',
                                            InputTextMessageContent('Titanic en flauta'),
                                            thumb_url='https://imgur.com/YAlttL7.png'))
    results.append(InlineQueryResultArticle('7', 'Danza Hebrea - Hava Nagila Medley',
                                            InputTextMessageContent('Danza Hebrea - Hava Nagila Medley'),
                                            thumb_url='https://i.imgur.com/zvDpBLk.png'))
    results.append(InlineQueryResultArticle('8', 'Niño predicador',
                                            InputTextMessageContent('Niño predicador'),
                                            thumb_url='https://imgur.com/c7UiQat.png'))
    results.append(InlineQueryResultArticle('9', 'HEYYEYAAEYAAAEYAEYAA',
                                            InputTextMessageContent('HEYYEYAAEYAAAEYAEYAA'),
                                            thumb_url='https://imgur.com/OUoza0S.png'))
    results.append(InlineQueryResultArticle('10', 'Vitas - 7th Element',
                                            InputTextMessageContent('Vitas - 7th Element'),
                                            thumb_url='https://imgur.com/H66YT9u.png'))
    results.append(InlineQueryResultArticle('11', 'GhostBusters Theme Song',
                                            InputTextMessageContent('GhostBusters Theme Song'),
                                            thumb_url='https://imgur.com/Ep75AU6.png'))
    results.append(InlineQueryResultArticle('12', 'Jimmy Mi Carcachita',
                                            InputTextMessageContent('Jimmy Mi Carcachita'),
                                            thumb_url='http://imgur.com/sGZ4BVA.png'))
    results.append(InlineQueryResultArticle('13', 'Never Gonna Give You Up (Rick Astley)',
                                            InputTextMessageContent(
                                                'Never Gonna Give You Up (Rick Astley)'),
                                            thumb_url='http://imgur.com/sTwVRvO.png'))
    results.append(InlineQueryResultArticle('14', 'Ai se eu te pego (version Salvador Raya)',
                                            InputTextMessageContent(
                                                'Ai se eu te pego (version Salvador Raya)'),
                                            thumb_url='http://imgur.com/i3sJkB1.png'))
    results.append(InlineQueryResultArticle('15', 'Minorias (South Park)',
                                            InputTextMessageContent('Minorias (South Park)'),
                                            thumb_url='http://imgur.com/EIw6pob.png'))
    results.append(InlineQueryResultArticle('16', 'Epic sax guy',
                                            InputTextMessageContent('Epic sax guy'),
                                            thumb_url='http://imgur.com/W5YgViI.png'))
    results.append(InlineQueryResultArticle('17', 'Shut The Fuck Up (Filthy Frank)',
                                            InputTextMessageContent('Shut The Fuck Up (Filthy Frank)'),
                                            thumb_url='http://imgur.com/cWx2Mc1.png'))
    results.append(InlineQueryResultArticle('18', 'Darude - Sandstorm',
                                            InputTextMessageContent('Darude - Sandstorm'),
                                            thumb_url='http://imgur.com/T6Ysv4Q.png'))
    results.append(InlineQueryResultArticle('19',
                                            'El sonido de silencio de serguio denis en español/the sound of silence',
                                            InputTextMessageContent(
                                                'el sonido de silencio de serguio denis en español/the sound of silence'),
                                            thumb_url='http://imgur.com/aT35PYZ.png'))
    results.append(InlineQueryResultArticle('20', 'Running in The 90s (Initial D)',
                                            InputTextMessageContent('Running in The 90s (Initial D)'),
                                            thumb_url='http://imgur.com/jzy3w40.png'))
    results.append(InlineQueryResultArticle('21', 'Salvame La Vida - Mago Rey y Gackty Chan',
                                            InputTextMessageContent(
                                                'Salvame La Vida - Mago Rey y Gackty Chan'),
                                            thumb_url='http://imgur.com/lfjz7JK.png'))
    results.append(InlineQueryResultArticle('22', 'Darude - Sandstorm (RENGE FLUTE REMIX)',
                                            InputTextMessageContent(
                                                'Darude - Sandstorm (RENGE FLUTE REMIX)'),
                                            thumb_url='http://imgur.com/8vXAcr8.png'))

    update.inline_query.answer(results)


def inline_result(bot, update):
    result = update.chosen_inline_result
    res = int(result.result_id)
    sel = res
    resource = 'data/music/%s.ogg' % str(sel)
    audio = open(os.path.join(os.path.dirname(sys.modules['demiReportTelegram'].__file__), resource), 'rb')
    if sel == 17:
        bot.send_document(group_id, 'http://i.imgur.com/vABnMpR.gif')
    comentario = 'Sent by %s' % utils.get_name(result.from_user.id)
    bot.send_audio(group_id, audio, caption=comentario)
    audio.close()
