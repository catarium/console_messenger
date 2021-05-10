from __future__ import annotations

import json
import typing
import contextlib

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


class RegistrationView(Frame):

    def __init__(
        self: RegistrationView, screen: Screen, model: MessageModel
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
            title=self._("Регистрация")
        )

        self._model = model

        layout = Layout([100], fill_frame=False)
        self.add_layout(layout)

        layout.add_widget(Text(self._('Имя пользователя:'), 'username'))
        layout.add_widget(Text(self._('Пароль:'), 'password'))

        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        self._login_button = Button(self._('Регистрация'), self._registration)
        self._back_button = Button(self._('Назад'), self._back)
        layout2.add_widget(self._login_button, 0)
        layout2.add_widget(self._back_button, 1)

        self.fix()

    def _registration(self: RegistrationView) -> None:
        self.save()
        if not self.data['username'] or not self.data['password']:
            self._keyerror_handler()
        res = self._model.register(self.data['username'], self.data['password'])
        if self.data['username'] and self.data['password']:
            if res['result']:
                raise NextScene("ChatsList")
            self._registration_error_handler(res['msg'])
    
    def _keyerror_handler(self: RegistrationView) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, self._("Пожалуйста, заполните все поля!"),
                [self._("Ок"), self._("Назад")], has_shadow=True,
                on_close=self._errors_handler_on_yes
            )
        )

    def _registration_error_handler(self: RegistrationView, msg: str) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, msg,
                [self._("Ok"), self._("Назад")], has_shadow=True,
                on_close=self._errors_handler_on_yes
            )
        )

    @staticmethod
    def _errors_handler_on_yes(selected: int) -> None:
        if selected == 0:
            raise NextScene("Registration")
        raise NextScene("StartMenu")

    def _back(self: Login) -> None:
        raise NextScene('StartMenu')
