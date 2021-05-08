import asyncio
import json
import os
import threading
from time import sleep

import colorama
import requests
import websockets
from requests.exceptions import *

TOKEN = ''
colorama.init()
run_receiving = True
with open('config.json', 'r', encoding='UTF-8') as f:
    config = json.load(f)
URL = config['url']


def login():
    global TOKEN
    os.system('cls')
    print('Login')
    username = input('Enter your login: ')
    os.system('cls')
    print('Login')
    password = input('Enter your password: ')
    data = requests.post(f'{URL}/login', json={'username': username,
                                               'password': password}).json()
    if data['result']:
        TOKEN = data['token']
        return True
    else:
        os.system('cls')
        print('Login')
        print(f'ERROR: {data["msg"]}')
        sleep(5)
        return False


def reg():
    global TOKEN
    os.system('cls')
    print('Registration')
    username = input('Enter your login: ')
    os.system('cls')
    print('Registration')
    password = input('Enter your password: ')
    data = requests.post(f'{URL}/registration', json={'username': username,
                                                      'password': password}).json()
    if data['result']:
        TOKEN = data['token']
        return True
    else:
        os.system('cls')
        print('Registration')
        print(f'ERROR: {data["msg"]}')
        sleep(5)
        return False


def start_chat():
    global TOKEN
    membername = input(
        'enter username, which you want start messaging(!back for return to list of chats): ')
    res = requests.post(f'{URL}/chats/start/{TOKEN}/', json={'membername': membername}).json()
    print(res)
    if res['result'] or membername == '!back':
        return True
    else:
        print(res['msg'])
        return False


async def get_messages(chat_id):
    global TOKEN
    # os.system('cls')
    uri = f"ws://localhost:8000/chats/{TOKEN}/{chat_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            data = [f'{colorama.Fore.GREEN + i[0]}:\n' \
                    f'{colorama.Fore.BLUE + i[2]}\n' \
                    f'{colorama.Fore.WHITE + i[1]}\n' \
                    for i in json.loads(data)['messages']]
            print('\n'.join(data))


def get_chats():
    global TOKEN
    while True:
        data = requests.get(f'{URL}/chats/{TOKEN}').json()
        if data['result']:
            while True:
                os.system('cls')
                print('New chat(1)\n'
                      'Enter to chat(2)\n'
                      'Back(3)\n'
                      'Reload list(4)')
                messages = data['chats']
                print('№    name')
                for i in range(len(messages)):
                    print(f'{i + 1}    {messages[i]["membername"]}')
                choice = input('> ')
                if choice == '1':
                    while True:
                        res = start_chat()
                        if res:
                            break
                    break
                elif choice == '2':
                    while True:
                        try:
                            print('enter chat num')
                            choice = int(input())
                            if choice in range(1, len(messages) + 1):
                                chat_id = messages[choice - 1]['chat_id']
                                send_message(int(chat_id))
                                break
                            else:
                                print('chat not found')
                        except ValueError:
                            print('enter please number')

                elif choice == '3':
                    return True
                elif choice == '4':
                    break

        else:
            print(data['msg'])
            return False


def event_loop(args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(get_messages(args))
    loop.close()


def send_message(chat_id):
    global run_receiving
    thread2 = threading.Thread(target=event_loop, args=(int(chat_id),))
    thread2.start()
    while True:
        choice = input()
        if choice == '!back':
            thread2 = None
            return
        requests.post(f'{URL}/chats/{TOKEN}/{chat_id}', json={'text': choice})
        print(f'{colorama.Fore.GREEN + "logs"}: {colorama.Fore.WHITE + "sended"}\n')


def main():
    global TOKEN
    while True:
        while True:
            os.system('cls')
            print(
                '''Login(1)
Registration(2)'''
            )
            choice = input('> ')
            if choice == '1':
                res = login()
            elif choice == '2':
                res = reg()
            else:
                continue
            if res:
                break
        while True:
            os.system('cls')
            print(
                '''Chats(1)
Exit(2)'''
            )
            choice = input('> ')
            if choice == '1':
                get_chats()
            elif choice == '2':
                TOKEN = ''
                break


try:
    main()
except ConnectionError:
    print('Не удается подключиться к серверу')
