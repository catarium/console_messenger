from fastapi import FastAPI, WebSocket
from create_tables import create_tables
import sqlite3
import random
from models import User, Member, Message
from werkzeug.security import generate_password_hash, check_password_hash
import asyncio
from datetime import datetime as dt


con = sqlite3.connect('db.sqlite')
create_tables(con)
cur = con.cursor()

app = FastAPI()

users = {}


generate_token = lambda: ''.join(random.choices('qwertyuiopasdfghkjlzxcvbnm1234568790', k=16))


@app.post('/registration/')
async def reg(user: User):
    cur.execute('SELECT id FROM users id WHERE username = ?', (
        user.username,))
    data = cur.fetchone()
    if not data:
        if user.username != '!back':
            cur.execute('INSERT INTO users (username, password) VALUES(?, ?)', (
                user.username, generate_password_hash(user.password)))
            cur.execute('SELECT id FROM users WHERE username=?', (user.username,))
            token = generate_token()
            users[token] = cur.fetchone()[0]
            con.commit()
            return {'result': True, 'token': token}
        else:
            return {'result': False, 'msg': 'недопустимое имя пользователя'}
    return {'result': False, 'msg': 'имя пользователя занято'}


@app.post('/login/')
async def login(user: User):
    cur.execute('SELECT id, password FROM users id WHERE username = ?', (
        user.username,))
    data = cur.fetchone()
    try:
        if check_password_hash(data[1], user.password):
            token = generate_token()
            users[token] = data[0]
            return {'result': True, 'token': token}
        else:
            return {'result': False, 'msg': 'неверный пароль'}
    except TypeError:
        return {'result': False, 'msg': 'пользователь не найден'}


@app.get('/chats/{token}')
async def get_chats_list(token):
    try:
        user_id = users[token]
    except KeyError:
        return {'result': False, 'msg': 'неверный токен'}
    cur.execute('''SElECT id, CASE WHEN member_id1=? THEN (SELECT username FROM users WHERE id=member_id2)
                                   WHEN member_id2=? THEN (SELECT username FROM users WHERE id=member_id1)
                   END FROM chats''', (user_id, user_id))
    data = cur.fetchall()
    data = [{'chat_id': i[0], 'membername': i[1]} for i in data if i[1]]
    return {'result': True, 'chats': data}


@app.post('/chats/start/{token}/')
async def start_chat(token, member: Member):
    try:
        user_id = users[token]
    except KeyError:
        return {'result': False, 'msg': 'неверный токен'}
    cur.execute('SELECT id FROM users WHERE username=?', (member.membername,))
    data = cur.fetchone()
    try:
        member_id = data[0]
    except TypeError:
        return {'result': False, 'msg': 'пользователь не найден'}
    if member_id == user_id:
        return {'result': False, 'msg': 'нельзя писать самому себе'}
    cur.execute('''SElECT id, CASE WHEN member_id1=? AND member_id2=? THEN member_id2 
                                   WHEN member_id1=? AND member_id2=? THEN member_id2 
                       END FROM chats''', (user_id, member_id, member_id, user_id))
    res = cur.fetchone()
    if res[1]:
        return {'result': False, 'msg': 'чат уже создан'}
    cur.execute('INSERT INTO chats (member_id1, member_id2) VALUES(?, ?)', (user_id, member_id))
    con.commit()
    cur.execute('SELECT id FROM chats WHERE member_id1=? AND member_id2=?', (user_id, member_id))
    return {'result': True, 'chat_id': cur.fetchone()[0]}


@app.post('/chats/{token}/{chat_id}')
async def send_message(token, chat_id, message: Message):
    try:
        user_id = users[token]
    except IndexError:
        return {'result': False, 'msg': 'неверный токен'}
    cur.execute('SELECT * FROM chats WHERE id=?', (chat_id,))
    try:
        if user_id in cur.fetchone():
            date = dt.now()
            date = date.strftime('%Y-%m-%d %H:%M')
            cur.execute('INSERT INTO messages (user_id, chat_id, message_text, date) VALUES(?, ?, ?, ?)',
                        (user_id, chat_id, message.text, date))
            con.commit()
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
    cur.execute('SELECT * FROM chats WHERE id=?', (chat_id,))
    try:
        if user_id not in cur.fetchone():
            return {'result': False, 'msg': 'чат не найден'}
    except TypeError:
        return {'result': False, 'msg': 'чат не найден'}
    last_message_id = 0
    while True:
        cur.execute('SELECT id, (SELECT username FROM users WHERE id=user_id), '
                    'message_text, date FROM messages WHERE chat_id=? AND id > ?', (chat_id, last_message_id))
        data = cur.fetchall()
        messages = [{'username': i[1], 'text': i[2], 'date': i[3]} for i in data]
        try:
            last_message_id = data[-1][0]
        except IndexError:
            pass
        if messages:
            print('sending')
            await ws.send_json({'result': True, 'messages': messages})
        await asyncio.sleep(5)
