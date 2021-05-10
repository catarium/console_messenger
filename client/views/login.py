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


class LoginView(Frame):

    def __init__(
        self: Login, screen: Screen, model: MessageModel
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
        layout.add_widget(Text(self._('Пароль:'), 'password'))

        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        self._login_button = Button(self._('Вход'), self._login)
        self._back_button = Button(self._('Назад'), self._back)
        layout2.add_widget(self._login_button, 0)
        layout2.add_widget(self._back_button, 1)

        self.fix()

    def _login(self: Login) -> None:
        self.save()
        if not self.data['username'] or not self.data['password']:
            self._keyerror_handler()
        res = self._model.login(self.data['username'], self.data['password'])
        if self.data['username'] and self.data['password']:
            if res['result']:
                raise NextScene("ChatsList")
            self._user_not_found_handler(res['msg'])
    
    def _keyerror_handler(self: Login) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, self._("Пожалуйста, заполните все поля!"),
                [self._("Ок"), self._("Назад")], has_shadow=True,
                on_close=self._errors_handler_on_yes
            )
        )

    def _user_not_found_handler(self: Login, msg: str) -> None:
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

    def _back(self: Login) -> None:
        raise NextScene('StartMenu')
