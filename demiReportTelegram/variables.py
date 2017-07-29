import configparser
from collections import deque
import pymysql


config = configparser.ConfigParser()
config.read('config.ini')

api_token = config['Telegram']['token']

link = config['Telegram']['link']
group_id = int(config['Telegram']['group_id'])
admin_id = int(config['Telegram']['admin_id'])

DB_HOST = config['Database']['DB_HOST']
DB_USER = config['Database']['DB_USER']
DB_PASS = config['Database']['DB_PASS']
DB_NAME = config['Database']['DB_NAME']

CLEVERBOT_KEY = config['Token']['CLEVERBOT_KEY']

nuke = 30
perros = 20
HEADSHOT = 7
MUTE = 5
MUTE_TIME = 600
porn = True
poles = []
new_members = []

msg_queue = deque([], 15)


def add_new_member(new_member):
    global new_members
    new_members.append(new_member)


def add_member_to_poles(new_member, pos):
    global poles
    if not len(poles) > pos:
        poles.append(new_member)


def clean_poles(bot, job):
    global poles
    poles = []

    con = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM PipasVotes")
            cur.execute("DELETE FROM Pipas")
    except Exception as exception:
        print(exception)
    finally:
        if con:
            con.commit()
            con.close()
