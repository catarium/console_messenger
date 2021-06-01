from __future__ import annotations

import os
import json
import typing
import contextlib
import threading
import asyncio
import time
import random

from math import floor

from asciimatics.exceptions import NextScene, StopApplication
from asciimatics.widgets import (
    Layout, Text, TextBox, Widget, Button, 
    ListBox, Divider, Frame, Label, VerticalDivider, 
    PopUpDialog
)
from asciimatics.screen import Screen

from ..models import MessageModel
from ..localization import Localizate


class ChatView(Frame):

    def __init__(
        self: ChatView, screen: Screen, model: MessageModel
    ) -> None:
        self.stop = True

        with open("client/config.json", "r") as file:
            data = json.loads(file.read())
            self._: Localizate = Localizate(data['lang'])

        super().__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            can_scroll=True,
            title=self._("Чат"),
        )

        self._model = model

        self._send_message_button = Button(
            self._('Отправить сообщение'), self._send_message
        )
        self._back_button = Button(
            self._("Выйти"), self._back
        )

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        self._messages_list = ListBox(
            Widget.FILL_FRAME,
            options=[],
            name="messages",
            # add_scroll_bar=True

        )
        self._input_form = Text(
            label="Сообщение:",
            name="message"
        )

        layout.add_widget(
            Label(self._('Сообщения'), align='^')
        )
        layout.add_widget(
            self._messages_list
        )
        layout.add_widget(
            self._input_form
        )

        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(self._send_message_button, 0)
        layout2.add_widget(self._back_button, 1)
        self.fix()

        self.model_connected = False

    def _send_message(self: ChatView) -> None:
        self.save()
        print('sended')
        self._model.send_message(
            int(os.environ['TUI_CHAT_ID']),
            self.data['message']
        )


    def _update(self, frame_no) -> None:
        try:
            super()._update(frame_no)
            if not self.model_connected:
                with open("client/config.json", "r") as file:
                    self.model_connected = True
                    data = json.loads(file.read())
                    self._model.start_websocket(int(os.environ['TUI_CHAT_ID']))
            messages = self._model.get_messages()
            messages = [(f'{messages[i][2]} {messages[i][0]}: {messages[i][1]}', str(i)) for i in range(len(messages))]
            if messages != self._messages_list.options and messages:
                print(messages != self._messages_list.options)
                if self._messages_list.value is None or \
                        self._messages_list.options[-1][1] == self._messages_list.value:
                    self._messages_list.options = messages
                    self._messages_list.value = self._messages_list.options[-1][1]
                else:
                    self._messages_list.options = messages
        except KeyboardInterrupt:
            self._back()
            raise KeyboardInterrupt

    def _back(self: ChatView) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, self._(f"Вы уверенны?"),
                [self._("Да"), self._("Нет")], has_shadow=True,
                on_close=self._quit_on_yes
            )
        )

    def _quit_on_yes(self: ChatView, selected: int) -> None:
        if selected == 0:
            self.model_connected = False
            self._model.close_websocket()
            raise NextScene("ChatsList")
