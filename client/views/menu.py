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

from ..localization import Localizate


class StartMenuView(Frame):

    def __init__(
        self: LogAndRegMenu, screen: Screen
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
            title=self._("Чат")
        )

        self._reg_button = Button(self._('Зарегистрироваться'), self._registration)
        self._log_button = Button(self._('Войти'), self._login)
        self._quit_button = Button(self._('Закрыть'), self._quit)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Label(self._('Пожалуйста, войдите или зарегистрируйтесь'), align='^',
                                height=screen.height * 2 // 3 // 2))

        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(self._reg_button, 0)
        layout2.add_widget(self._log_button, 1)
        layout2.add_widget(self._quit_button, 2)
        self.fix()

    def _login(self: LogAndRegMenu) -> None:
        raise NextScene('Login')

    def _registration(self: LogAndRegMenu) -> None:
        raise NextScene('Registration')

    def _quit(self: LogAndRegMenu) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, self._("Вы уверенны?"),
                [self._("Да"), self._("Нет")], has_shadow=True,
                on_close=self._quit_on_yes
            )
        )

    @staticmethod
    def _quit_on_yes(selected: int) -> typing.NoReturn:
        if selected == 0:
            raise StopApplication(self._("User pressed quit"))
