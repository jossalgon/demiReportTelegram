import variables
from src.utils import Utils

utils = Utils()

bot = variables.bot


class Welcome:
    def send_welcome(self, message):
        bot.reply_to(message, 'F*CK U')

    def send_welcome_to_new_member(self, message):
        user_id = message.new_chat_member.id
        sti = open('data/stickers/nancy_ok.webp', 'rb')
        bot.send_sticker(variables.group_id, sti)
        sti.close()
        if not utils.is_from_group(user_id):
            variables.add_new_member(user_id)
            bot.send_message(variables.admin_id, user_id)

    def send_bye_to_member(self, message):
        user_id = message.left_chat_member.id
        sti = open('data/stickers/nancy.webp', 'rb')
        sti2 = open('data/stickers/nancy.webp', 'rb')
        bot.send_sticker(variables.group_id, sti)
        bot.send_sticker(user_id, sti2)
        sti.close()
        sti2.close()

