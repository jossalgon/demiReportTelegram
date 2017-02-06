import requests
import logging

from demiReportTelegram import variables

admin_id = variables.admin_id
group_id = variables.group_id

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def send_butts(bot, update, attempt=0):
    message = update.message
    try:
        r = requests.get('http://api.obutts.ru/noise/1')
        data = r.json()[0]
        if not data and attempt <= 3:
            send_butts(bot, update, attempt + 1)
        photo = 'http://media.obutts.ru/' + data['preview']
        bot.send_photo(message.chat.id, photo)
    except Exception:
        logger.error('Fatal error in send_butts', exc_info=True)


def send_boobs(bot, update, attempt=0):
    message = update.message
    try:
        r = requests.get('http://api.oboobs.ru/noise/1')
        data = r.json()[0]
        if not data and attempt <= 3:
            send_boobs(bot, update, attempt + 1)
        photo = 'http://media.oboobs.ru/' + data['preview']
        bot.send_photo(message.chat.id, photo)
    except Exception:
        logger.error('Fatal error in send_boobs', exc_info=True)
