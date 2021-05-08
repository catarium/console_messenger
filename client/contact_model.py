import sys
import threading
import requests
import asyncio

from excc import MessengerError
from websockets import connect


class ContactModel(object):
    
    def __init__(self, url) -> None:
        self.token = ''
        self.url = url
        self.messages = []
        self.loop = asyncio.get_event_loop()

    async def _get_messages(self, chat_id: int) -> None:
        uri = f"ws://localhost:8000/chats/{self.token}/{chat_id}"
        async with connect(uri) as websocket:
            while True:
                data = await websocket.recv()
                self.messages += data['messages']

    def start_websocket(self, chat_id: int) -> None:
        # self.thread = threading.Thread(target=self._get_messages, args=(chat_id,))
        self.loop.create_task(self._get_messages(chat_id))
        self.loop.run_forever()

    def close_websocket(self) -> None:
        self.loop.close()

    def get_messages(self) -> list:
        res = self.messages
        self.messages = []
        return res

    def login(self, username: str, password: str) -> dict:
        res = requests.post(
            f'{self.url}/login', 
            json={'username': username, 'password': password}
        ).json()
        try:
            self.token = res['token']
        except KeyError:
            pass
        return res

    def register(self, username: str, password: str) -> None:
        res = requests.post(
            f'{self.url}/registration',
            json={'username': username, 'password': password}
        ).json()

        try:
            if res['result']:
                self.token = res['token']
        except KeyError:
            raise MessengerError(res['msg'])

    def send_message(self, chat_id: int, text: str) -> dict:
        return requests.post(f'{self.url}/chats/{self.token}/{chat_id}', json={'text': text})

    def get_chats(self) -> dict:
        return requests.get(f'{self.url}/chats/{self.token}').json()

    def start_chat(self, membername: str) -> None:
        requests.post(
            f'{self.url}/chats/{self.token}', 
            json={'membername': membername}
        ).json()
