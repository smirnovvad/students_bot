# coding=utf-8
import sys
import asyncio
import telepot
from telepot import glance
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space, include_callback_query_chat_id)
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from client import ApiClient
from settings import API_URL, TELEGRAM_TOKEN

class ApiClientStarter(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ApiClientStarter, self).__init__(*args, **kwargs)

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = glance(msg)
        print(msg, content_type, chat_type, chat_id)

        # delay = float(msg['text'])

        # 3. Schedule event
        #      The second argument is the event spec: a 2-tuple of (flavor, dict).
        # Put any custom data in the dict. Retrieve them in the event-handling function.

        if content_type == 'text':

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Войти', callback_data='main',)],
            ])
            await self.sender.sendMessage('Авторизуйтесь', reply_markup=keyboard)

        # self.close()


TOKEN = TELEGRAM_TOKEN
print(TOKEN)

# telepot.api.set_proxy('https://45.32.195.95:8118', )


bot = telepot.aio.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
        per_chat_id(), create_open, ApiClient, timeout=10000),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
