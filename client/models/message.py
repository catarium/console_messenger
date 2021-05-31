import sys
import json
from ..threads import StoppableThread
import requests

from websocket import create_connection

messages = []


class MessageModel(object):

    stop: bool = True
    
    def __init__(self, url) -> None:
        with open("client/config.json", "r") as file:
            data = json.loads(file.read())
            self.token = data['token']
        self.url = url
        self.messages = []

    def _get_messages(self, chat_id: int) -> None:
        global messages
        uri = f"ws://localhost:8000/chats/{self.token}/{chat_id}"
        self.ws = create_connection(uri)
        while not MessageModel.stop:
            data = self.ws.recv()
            data = json.loads(data)
            data['messages'] = [tuple(message.values()) for message in data['messages']]
            messages += data['messages']
        return

    def start_websocket(self, chat_id: int) -> None:
        MessageModel.stop = False
        self.thread = StoppableThread(target=self._get_messages, args=(chat_id,))
        self.thread.start()
        
    def close_websocket(self) -> None:
        global messages
        messages = []
        MessageModel.stop = True
        self.ws.close()

    def get_messages(self) -> list:
        global messages
        return messages

    def login(self, username: str, password: str) -> dict:
        res = requests.post(
            f'{self.url}/login', 
            json={'username': username, 'password': password}
        ).json()
        try:
            with open("client/config.json", "r") as file:
                data = json.loads(file.read())
                data['token'] = res['token']
            
            with open("client/config.json", "w") as file:
                file.write(json.dumps(data, indent=4))
            self.token = res['token']
        except KeyError:
            pass
        return res

    def register(self, username: str, password: str) -> None:
        res: dict = requests.post(
            f'{self.url}/registration',
            json={'username': username, 'password': password}
        ).json()

        try:
            if res['result']:
                self.token: str = res['token']

            with open("client/config.json", "r") as file:
                data = json.loads(file.read())
                data['token'] = res['token']
            
            with open("client/config.json", "w") as file:
                file.write(json.dumps(data, indent=4))

        except KeyError:
            pass
            # raise MessengerError(res['msg'])

        return res

    def send_message(self, chat_id: int, text: str) -> dict:
        res = requests.post(f'{self.url}/chats/{self.token}/{chat_id}', json={'text': text})
        return res

    def get_chats(self) -> dict:
        return requests.get(f'{self.url}/chats/{self.token}').json()

    def start_chat(self, membername: str) -> None:
        res = requests.post(f'{self.url}/chats/start/{self.token}/', json={'membername': membername}).json()
        return res
