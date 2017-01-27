# DemiReportTelegram
DemiReportTelegram started by the idea of a telegram report bot and ended with a mix of random funny tools.

## Submodules
Submodule | Description
--------- | -----------
[reportTelegram](https://github.com/jossalgon/reportTelegram) | ReportTelegram is a telegram bot that helps you to keep the group clean by a report system with kicks and ban times.
[teamSpeakTelegram](https://github.com/jossalgon/teamSpeakTelegram) | TeamSpeakTelegram is a telegram bot that tells you who is connected to the teamspeak server to know when your friends are online.

## Installation
1. Create a config.ini file with:

  ```
  [Telegram]
  token_id = YOUR_TELEGRAM_BOT_TOKEN
  link = YOUR_GROUP_LINK
  group_id =  YOUR_GROUP_ID
  admin_id = THE_ADMIN_ID
  
  [TS]
  ts_host = YOUR_TS_HOST
  ts_user = serveradmin (OR YOUR TS USERNAME AS ADMIN)
  ts_pass = YOUR_TS_PASSWORD
  
  [Database]
  DB_HOST = YOUR_DB_HOST
  DB_USER = YOUR_DB_USER
  DB_PASS = YOUR_DB_PASS
  DB_NAME = YOUR_DB_NAME
  ```

2. Change the "send_report" (demiReportBot.py) commands handler to usernames of your group.
    ```
    @bot.message_handler(
            commands=['Mark', 'Charlie', 'Alex'],
            func=lambda msg: ...)
        def send_report(message):
           ...
    ```

3. Install requirements
  ```
  sudo pip install -r requirements.txt
  ```

4. Run the bot
  ```
  python3 demiReportBot.py &
  ```

## Commands
Command | Uses
------- | -----
/start | Reply with a welcome message
/stats | Reply with report stats
/expulsados | Show a kicked top
/who | Reply with the users that you reported
/reportes n | Set max reports to n (where n is a number)
/time n | Set kick time to n (where n is the number of seconds)
/user1 | Report user1
/user2 | Report user2
/user3 | Report user3
/...   | Report ...
/ts | Reply with the teamspeak connected users
/disculpa | Send an apology message
/tq | Send Dolito's audio
/shh | Send "QUE TE CALLES YAAA!!!" audio
/alerta | Send "Oh oh! ALERTA POR SUBNORMAL!" audio
/ranking | Show the _poles_ ranking
/demigrante | Send a random song
/nuke | Kick random users with a _nuke_
/perros | Kick random users with _perros_
/mention | Toggle mention notifications
/butts | Send a butt image
/boobs | Send a boobs image
/purge | Ban not allowed users
