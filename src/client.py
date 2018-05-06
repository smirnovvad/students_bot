import asyncio
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telepot import glance, origin_identifier
import telepot
from apiclient import tglogin_api, get_groups, get_detail, update


class ApiClient(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ApiClient, self).__init__(*args, **kwargs)
        self._user = None
        self._access_token = ''
        self._groups = dict()
        self._students = dict()
        self._query_before = ''
        self._is_student = False
        self._msg = dict()

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = glance(msg)
        print(msg, content_type, chat_type, chat_id)

        if content_type == 'contact':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Список групп', callback_data='get_groups')],
                [InlineKeyboardButton(text='Мой профиль', callback_data='get_self_profile')],
            ])
            if msg['from']['id'] == msg['contact']['user_id']:
                self._user['phone'] = msg['contact']['phone_number']
                result, status_code = update(self._access_token, self._user['_links']['self'], self._user)

                await self.sender.sendMessage(f'Вы вошли как {self._user["first_name"]} {self._user["last_name"]}', reply_markup=keyboard)
            else:
                await self.sender.sendMessage(f'Надо поделиться своим контаком', reply_markup=keyboard)

        if content_type == 'text':

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Войти', callback_data='main',)],
            ])
            self._msg = await self.sender.sendMessage('Авторизуйтесь', reply_markup=keyboard)

    # AUTH BY ID
    async def _login(self, id):

        # print(msg['from']['id'])
        result, status_code = tglogin_api(id)
        if status_code == 200:
            print(result)
            self._user = result
            self._access_token = result['access_token']
            if 'traing' in self._user:
                # print('student')
                self._is_student = True
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Войти', callback_data='main',)],
            ])
            await self.editor.editMessageText(result['message'], reply_markup=keyboard)

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')
        # print(msg['message'])

        self.editor = telepot.aio.helper.Editor(self.bot, origin_identifier(msg))

        print(query_data)

        if self._access_token == '':
            await self._login(from_id)

        # LOGIN
        if query_data == 'main':
            if self._query_before == query_data and self._user is not None:
                return

            if self._access_token != '':
                print(self._user)
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Список групп', callback_data='get_groups')],
                    [InlineKeyboardButton(text='Мой профиль', callback_data='get_self_profile')],
                ])
                await self.editor.editMessageText(f'Вы вошли как {self._user["first_name"]} {self._user["last_name"]}', reply_markup=keyboard)

        if self._query_before != query_data:
            self._query_before = query_data
        else:
            return
        # GET GROUPS
        if query_data == 'get_groups':
            self._query_before = query_data
            # print(self._access_token)
            result, status_code = get_groups(self._access_token)
            if status_code == 422:
                self._login(from_id)
                self._groups, status_code = get_groups(self._access_token)
            else:
                self._groups = result
            # print(self._groups)
            keyboard = InlineKeyboardMarkup(inline_keyboard=list(map(lambda c: [InlineKeyboardButton(text=str(c['name_group']), callback_data=str('group_detail_' + c['name_group']))], list(self._groups))) + [[InlineKeyboardButton(text='← Назад', callback_data='main')]])
            await self.editor.editMessageText(f'Список групп:', reply_markup=keyboard)
            self._query_before = query_data

        # GET STUDENTS
        if 'group_detail' in query_data:
            link = next((item for item in self._groups if item["name_group"] == query_data[13:]))['_links']
            result, status_code = get_detail(self._access_token, link["students"])
            if status_code == 422:
                self._login(from_id)
                self._students, status_code = get_detail(self._access_token, link["students"])
            else:
                self._students = result['students']

            keyboard = InlineKeyboardMarkup(inline_keyboard=list(map(lambda c: [InlineKeyboardButton(text=str(f'{c["last_name"]} {c["first_name"][0]}. {c["middle_name"][0]}.'), callback_data='student_detail_' + str(c['id']))], list(self._students))) + [[InlineKeyboardButton(text='← Назад', callback_data='get_groups')]])
            await self.editor.editMessageText(f'Список студентов в группе:', reply_markup=keyboard)
            # self._query_before = query_data

        # STUDENT DETAIL
        if 'student_detail_' in query_data:
            student = next((item for item in self._students if item["id"] == int(query_data[15:])))
        # self._students = get_detail(self._access_token, link["students"])['students']
            result = f'*Ф.И.О.* - {student["last_name"]} {student["first_name"]} {student["middle_name"]}\n*Обучение* - {student["traing"]}\n*Email* - {student["email"]}\n*Номер телефона* - {student["phone"]}\n[Telegram](tg://user?id={student["telegram_id"]})'
            if student['phone'] is not None:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Отправить контакт', callback_data=f'get_contact_{student["id"]}'), ],
                    [InlineKeyboardButton(text='← Назад', callback_data='get_groups')],
                ])
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='← Назад', callback_data='get_groups')],
                ])

            await self.editor.editMessageText(f'{result}', reply_markup=keyboard, parse_mode='Markdown')

        # STUDENT DETAIL
        if 'get_self_profile' in query_data:
            if self._is_student:
                print(self._user)
                result = f'*Ф.И.О.* - {self._user["last_name"]} {self._user["first_name"]} {self._user["middle_name"]}\n*Обучение* - {self._user["traing"]}\n*Email* - {self._user["email"]}\n*Номер телефона* - {self._user["phone"]}\n[Telegram](tg://user?id={self._user["telegram_id"]})'
            if self._user['phone'] is not None:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='← Назад', callback_data='main')],
                ])
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Добавить номер', callback_data='get_self_number'), ],
                    [InlineKeyboardButton(text='← Назад', callback_data='main')],
                ])
            await self.editor.editMessageText(f'{result}', reply_markup=keyboard, parse_mode='Markdown')

        if 'get_self_number' in query_data:

            markup = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Отправить номер', request_contact=True)],
            ], one_time_keyboard=True)
            await self.sender.sendMessage(text='Поделитесь своим контактом', reply_markup=markup)

        if 'get_contact' in query_data:
            student = next((item for item in self._students if item["id"] == int(query_data[12:])))

            markup = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Отправить номер', request_contact=True)],
            ], one_time_keyboard=True)
            await self.sender.sendContact(phone_number=student['phone'], first_name=student['first_name'], last_name=student['last_name'])

    async def on__idle(self, event):
        await asyncio.sleep(5)
        await self.editor.deleteMessage()
        self.close()
