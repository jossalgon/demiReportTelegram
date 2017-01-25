# -*- encoding: utf-8 -*-

from telebot import types

import variables
from src.utils import Utils

utils = Utils()

bot = variables.bot
admin_id = variables.admin_id
group_id = variables.group_id


class Songs:
    def query_text(self, inline_query):
        try:
            r = types.InlineQueryResultArticle('1', 'Alien - Nunca me Faltes',
                                               types.InputTextMessageContent('Alien - Nunca me Faltes'),
                                               thumb_url='http://i.imgur.com/663CMAj.png')
            r2 = types.InlineQueryResultArticle('2', 'El merengue del PP',
                                                types.InputTextMessageContent('El merengue del PP'),
                                                thumb_url='http://i.imgur.com/brP3eGU.png')
            r3 = types.InlineQueryResultArticle('3', 'Seinfeld MLG remix (Skrillfeld)',
                                                types.InputTextMessageContent('Seinfeld MLG remix (Skrillfeld)'),
                                                thumb_url='https://imgur.com/XfgkG2v.png')
            r4 = types.InlineQueryResultArticle('4', 'Niña, no te modernices (Payo Juan)',
                                                types.InputTextMessageContent('Niña, no te modernices (Payo Juan)'),
                                                thumb_url='https://imgur.com/x89UIt6.png')
            r5 = types.InlineQueryResultArticle('5', 'Torres Gemelas (Delfín Quishpe)',
                                                types.InputTextMessageContent('Torres Gemelas (Delfín Quishpe)'),
                                                thumb_url='https://imgur.com/7ssC7xU.png')
            r6 = types.InlineQueryResultArticle('6', 'Titanic en flauta',
                                                types.InputTextMessageContent('Titanic en flauta'),
                                                thumb_url='https://imgur.com/YAlttL7.png')
            r7 = types.InlineQueryResultArticle('7', 'Danza Hebrea - Hava Nagila Medley',
                                                types.InputTextMessageContent('Danza Hebrea - Hava Nagila Medley'),
                                                thumb_url='https://i.imgur.com/zvDpBLk.png')
            r8 = types.InlineQueryResultArticle('8', 'Niño predicador',
                                                types.InputTextMessageContent('Niño predicador'),
                                                thumb_url='https://imgur.com/c7UiQat.png')
            r9 = types.InlineQueryResultArticle('9', 'HEYYEYAAEYAAAEYAEYAA',
                                                types.InputTextMessageContent('HEYYEYAAEYAAAEYAEYAA'),
                                                thumb_url='https://imgur.com/OUoza0S.png')
            r10 = types.InlineQueryResultArticle('10', 'Vitas - 7th Element',
                                                 types.InputTextMessageContent('Vitas - 7th Element'),
                                                 thumb_url='https://imgur.com/H66YT9u.png')
            r11 = types.InlineQueryResultArticle('11', 'GhostBusters Theme Song',
                                                 types.InputTextMessageContent('GhostBusters Theme Song'),
                                                 thumb_url='https://imgur.com/Ep75AU6.png')
            r12 = types.InlineQueryResultArticle('12', 'Jimmy Mi Carcachita',
                                                 types.InputTextMessageContent('Jimmy Mi Carcachita'),
                                                 thumb_url='http://imgur.com/sGZ4BVA.png')
            r13 = types.InlineQueryResultArticle('13', 'Never Gonna Give You Up (Rick Astley)',
                                                 types.InputTextMessageContent(
                                                     'Never Gonna Give You Up (Rick Astley)'),
                                                 thumb_url='http://imgur.com/sTwVRvO.png')
            r14 = types.InlineQueryResultArticle('14', 'Ai se eu te pego (version Salvador Raya)',
                                                 types.InputTextMessageContent(
                                                     'Ai se eu te pego (version Salvador Raya)'),
                                                 thumb_url='http://imgur.com/i3sJkB1.png')
            r15 = types.InlineQueryResultArticle('15', 'Minorias (South Park)',
                                                 types.InputTextMessageContent('Minorias (South Park)'),
                                                 thumb_url='http://imgur.com/EIw6pob.png')
            r16 = types.InlineQueryResultArticle('16', 'Epic sax guy',
                                                 types.InputTextMessageContent('Epic sax guy'),
                                                 thumb_url='http://imgur.com/W5YgViI.png')
            r17 = types.InlineQueryResultArticle('17', 'Shut The Fuck Up (Filthy Frank)',
                                                 types.InputTextMessageContent('Shut The Fuck Up (Filthy Frank)'),
                                                 thumb_url='http://imgur.com/cWx2Mc1.png')
            r18 = types.InlineQueryResultArticle('18', 'Darude - Sandstorm',
                                                 types.InputTextMessageContent('Darude - Sandstorm'),
                                                 thumb_url='http://imgur.com/T6Ysv4Q.png')
            r19 = types.InlineQueryResultArticle('19',
                                                 'El sonido de silencio de serguio denis en español/the sound of silence',
                                                 types.InputTextMessageContent(
                                                     'el sonido de silencio de serguio denis en español/the sound of silence'),
                                                 thumb_url='http://imgur.com/aT35PYZ.png')
            r20 = types.InlineQueryResultArticle('20', 'Running in The 90s (Initial D)',
                                                 types.InputTextMessageContent('Running in The 90s (Initial D)'),
                                                 thumb_url='http://imgur.com/jzy3w40.png')
            r21 = types.InlineQueryResultArticle('21', 'Salvame La Vida - Mago Rey y Gackty Chan',
                                                 types.InputTextMessageContent(
                                                     'Salvame La Vida - Mago Rey y Gackty Chan'),
                                                 thumb_url='http://imgur.com/lfjz7JK.png')
            r22 = types.InlineQueryResultArticle('22', 'Darude - Sandstorm (RENGE FLUTE REMIX)',
                                                 types.InputTextMessageContent(
                                                     'Darude - Sandstorm (RENGE FLUTE REMIX)'),
                                                 thumb_url='http://imgur.com/8vXAcr8.png')

            bot.answer_inline_query(inline_query.id,
                                    [r, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18,
                                     r19, r20, r21, r22])
        except Exception as exception:
            bot.send_message(admin_id, exception)

    def send_chosen(self, chosen_inline_result):
        res = int(chosen_inline_result.result_id)
        sel = res
        audio = open('data/music/%s.ogg' % str(sel), 'rb')
        if sel == 17:
            bot.send_document(group_id, 'http://i.imgur.com/vABnMpR.gif')
        msg = bot.send_audio(group_id, audio)
        comentario = 'Sent by %s' % utils.get_name(chosen_inline_result.from_user.id)
        bot.edit_message_caption(comentario, group_id, msg.message_id)
