# -*- encoding: utf-8 -*-

import variables

bot = variables.bot
admin_id = variables.admin_id
group_id = variables.group_id


class Key_words:
    def jorge_despierto_handler(self):
        variables.jorge_despierto = True

    def jorge_buenosdias_handler(self, message):
        variables.jorge_despierto = True
        bot.reply_to(message, 'Buenos dias bella durmiente')

    def hipermierda_handler(self, message):
        user_id = message.from_user.id
        bot.reply_to(message, 'Que le jodan a Gabriela y que le jodan a Ford PUTOS ANORMALES FOLLAIOS')
        bot.kick_chat_member(group_id, user_id)
        bot.unban_chat_member(group_id, user_id)
        bot.send_message(user_id, 'Jiji entra anda: %s' % variables.link)

    def raulito_oro(self, message):
        bot.reply_to(message, 'No, todavía no')
