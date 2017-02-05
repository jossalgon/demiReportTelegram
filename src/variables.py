import configparser

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

num_reports = 5
ban_time = 300
nuke = 30
perros = 20
porn = True
berserker = False
jorge_despierto = True
poles = []
new_members = []


def add_new_member(new_member):
    global new_members
    new_members.append(new_member)


def add_member_to_poles(new_member, pos):
    global poles
    if not len(poles) > pos:
        poles.append(new_member)


def clean_poles():
    global poles
    poles = []
