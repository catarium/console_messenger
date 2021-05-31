from __future__ import annotations

import json
import contextlib

from asciimatics.exceptions import NextScene
from asciimatics.widgets import (
    Layout, Text, TextBox, Widget, Button,
    ListBox, Divider, Frame, Label, VerticalDivider,
    PopUpDialog
)
from asciimatics.screen import Screen

from ..models import MessageModel
from ..localization import Localizate


class StartChatView(Frame):

    def __init__(
            self: StartChatView, screen: Screen, model: MessageModel
    ) -> None:
        with open("client/config.json", "r") as file:
            data = json.loads(file.read())
            self._: Localizate = Localizate(data['lang'])

        super().__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            can_scroll=False,
            title=self._("Вход")
        )

        self._model = model

        layout = Layout([100], fill_frame=False)
        self.add_layout(layout)

        layout.add_widget(Text(self._('Имя пользователя:'), 'username'))

        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        self._start_chat_button = Button(self._('Начать чат'), self._start_chat)
        self._back_button = Button(self._('Назад'), self._back)
        layout2.add_widget(self._start_chat_button, 0)
        layout2.add_widget(self._back_button, 1)

        self.fix()

    def _start_chat(self: StartChatView) -> None:
        self.save()
        if not self.data['username']:
            self._keyerror_handler()
        print(self.data['username'])
        res = self._model.start_chat(self.data['username'])
        if res['result']:
            raise NextScene("ChatsList")
        self._user_not_found_handler(res['msg'])

    def _keyerror_handler(self: StartChatView) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, self._("Пожалуйста, заполните все поля!"),
                [self._("Ок"), self._("Назад")], has_shadow=True,
                on_close=self._errors_handler_on_yes
            )
        )

    def _user_not_found_handler(self: StartChatView, msg: str) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, msg,
                [self._("Ok"), self._("Назад")], has_shadow=True,
                on_close=self._errors_handler_on_yes
            )
        )

    @staticmethod
    def _errors_handler_on_yes(selected) -> None:
        if selected == 0:
            raise NextScene("Login")
        raise NextScene("StartMenu")

    def _back(self: _back) -> None:
        raise NextScene("ChatsList")
