from fastapi import FastAPI, WebSocket
from server.db_models import Users, Chats, Messages
from server.db_models import metadata
from server import DATABASE_URL
import ormar
import random
from server.models import User, Member, Message
from werkzeug.security import generate_password_hash, check_password_hash
import asyncio
from datetime import datetime as dt
import sqlalchemy


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()

users = {}

generate_token = lambda: ''.join(random.choices('qwertyuiopasdfghkjlzxcvbnm1234568790', k=16))


@app.post('/registration/')
async def reg(user: User):
    try:
        data = await Users.objects.get(username=user.username)
    except ormar.exceptions.NoMatch:
        if user.username != '!back':
            await Users.objects.create(username=user.username,
                                       password=generate_password_hash(user.password))
            id_ = await Users.objects.get(username=user.username)
            id_ = id_.id
            token = generate_token()
            users[token] = id_
            return {'result': True, 'token': token}
        else:
            return {'result': False, 'msg': 'недопустимое имя пользователя'}
    return {'result': False, 'msg': 'имя пользователя занято'}


@app.post('/login/')
async def login(user: User):
    try:
        data = await Users.objects.get(username=user.username)
    except ormar.exceptions.NoMatch:
        return {'result': False, 'msg': 'пользователь не найден'}
    if check_password_hash(data.password, user.password):
        token = generate_token()
        users[token] = data.id
        return {'result': True, 'token': token}
    else:
        return {'result': False, 'msg': 'неверный пароль'}


@app.get('/chats/{token}')
async def get_chats_list(token):
    try:
        user_id = users[token]
    except KeyError:
        return {'result': False, 'msg': 'неверный токен'}
    data = await Chats.objects.all(member_id1=user_id)
    data = [(i.id, Users.objects.get(id=i.member_id2)) for i in data]
    data2 = await Chats.objects.all(member_id2=user_id)
    data += [(i.id, Users.objects.get(id=i.member_id1)) for i in data2]
    data = [{'chat_id': i[0], 'membername': i[1]} for i in data]
    return {'result': True, 'chats': data}


@app.post('/chats/start/{token}/')
async def start_chat(token, member: Member):
    try:
        user_id = users[token]
    except KeyError:
        return {'result': False, 'msg': 'неверный токен'}
    try:
        data = await Users.objects.get(username=member.membername)
    except ormar.exceptions.NoMatch:
        return {'result': False, 'msg': 'пользователь не найден'}
    member_id = data.id
    if member_id == user_id:
        return {'result': False, 'msg': 'нельзя писать самому себе'}
    try:
        data = await Chats.objects.get(member_id1=user_id, member_id2=member_id)
        data2 = await Chats.objects.get(member_id2=user_id, member_id1=member_id)
    except ormar.exceptions.NoMatch:
        id_ = await Chats.objects.get(member_id1=user_id, member_id2=member_id).id
        return {'result': True, 'chat_id': id_}
    return {'result': False, 'msg': 'чат уже создан'}


@app.post('/chats/{token}/{chat_id}')
async def send_message(token, chat_id, message: Message):
    try:
        user_id = users[token]
    except IndexError:
        return {'result': False, 'msg': 'неверный токен'}
    chat = await Chats.objects.get(id=chat_id)
    try:
        if user_id == chat.member_id1 or user_id == chat.member_id2:
            date = dt.now()
            date = date.strftime('%Y-%m-%d %H:%M')
            await Messages.objects.create(user_id=users, chat_id=chat_id, message_text=message.text,
                                          date=date)
            return {'result': True}
    except TypeError:
        return {'result': False, 'msg': 'чат не найден'}
    return {'result': False, 'msg': 'чат не найден'}


@app.websocket('/chats/{token}/{chat_id}')
async def get_messages(token, chat_id, ws: WebSocket):
    await ws.accept()
    try:
        user_id = users[token]
    except IndexError:
        return {'result': False, 'msg': 'incorrect token'}
    try:
        chat = await Chats.objects.get(id=chat_id)
    except ormar.exceptions.NoMatch:
        return {'result': False, 'msg': 'чат не найден'}
    if user_id != chat.member_id1 and user_id != chat.member_id2:
        return {'result': False, 'msg': 'чат не найден'}
    last_message_id = 0
    while True:
        try:
            data = await Messages.objects.all(chat_id=chat_id, id__gt=last_message_id)
        except ormar.exceptions.NoMatch:
            data = []
        messages = [{'username': i.username, 'text': i.message_text, 'date': i.date} for i in data]
        try:
            last_message_id = data[-1][0]
        except IndexError:
            pass
        if messages:
            print('sending')
            await ws.send_json({'result': True, 'messages': messages})
        await asyncio.sleep(5)
