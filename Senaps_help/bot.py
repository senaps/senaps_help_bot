#!/usr/bin/env python3
"""
A example script to automatically send messages based on certain triggers.

The script makes uses of environment variables to determine the API ID,
hash, phone and such to be used. You may want to add these to your .bashrc
file, including TG_API_ID, TG_API_HASH, TG_PHONE and optionally TG_SESSION.

This script assumes that you have certain files on the working directory,
such as "xfiles.m4a" or "anytime.png" for some of the automated replies.
"""
from config import configs
from getpass import getpass
from collections import defaultdict
from datetime import datetime, timedelta
from os import environ
from messages import REACTS
import re


from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import UpdateNewChannelMessage, UpdateShortMessage, MessageService
from telethon.tl.functions.messages import EditMessageRequest

"""Uncomment this for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug('dbg')
logging.info('info')
"""

# A list of dates of reactions we've sent, so we can keep track of floods
recent_reacts = defaultdict(list)


def update_handler(update):
    global recent_reacts
    try:
        msg = update.message
    except AttributeError:
        # print(update, 'did not have update.message')
        return
    if isinstance(msg, MessageService):
        print(msg, 'was service msg')
        return

    # React to messages in supergroups and PMs
    if isinstance(update, UpdateNewChannelMessage):
        if msg.message.startswith('!'):
            message = re.split('\W+', msg.message)[1]
            myfunction(message=message, msg_type='group', msg=msg)
    if isinstance(update, UpdateShortMessage):
        print('pm message' + msg.message)
        myfunction(message=message, msg_type='user', msg=msg)


def myfunction(message, msg_type, msg):
    for trigger, response in REACTS.items():
        if trigger in message:
            # TODO: we should handle reply to the quoted user
            print('ready to send out the answer!')
            if msg_type == 'group':
                client.send_message(msg.to_id, response, reply_to=msg.id)
            elif msg_type == 'user':
                client.send_message(update.user_id,
                                    response,
                                    reply_to=update.id)

if __name__ == '__main__':
    session_name = configs['session_name']
    user_phone = configs['phone_number']
    app_id = configs['app_id']
    hash_id = configs['hash_id']
    # TODO: this should be converted to configparser object.
    client = TelegramClient(
        session_name, app_id, hash_id,
        proxy=None, update_workers=4
        )
    try:
        print('INFO: Connecting to Telegram Servers...', end='', flush=True)
        client.connect()
        print('Done!')
        if not client.is_user_authorized():
            print('INFO: Unauthorized user')
            client.send_code_request(user_phone)
            code_ok = False
            while not code_ok:
                code = input('Enter the auth code: ')
                try:
                    code_ok = client.sign_in(user_phone, code)
                except SessionPasswordNeededError:
                    password = getpass('Two step verification enabled. '
                                       'Please enter your password: ')
                    code_ok = client.sign_in(password=password)
        print('INFO: Client initialized successfully!')
        client.add_update_handler(update_handler)
        input('Press Enter to stop this!\n')
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
