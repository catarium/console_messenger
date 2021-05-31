from __future__ import annotations

import os
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


class ChatsListView(Frame):

    def __init__(
        self: ChatsListView, screen: Screen, model: MessageModel
    ) -> None:
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
            on_load=self._reload_chats_list
        )

        self._model = model

        self._build_chat_button = Button(
            self._('Создать чат'), self._build_chat
        )
        self._enter_chat_button = Button(
            self._("Войти в чат"), self._enter_chat
        )
        self._reload_chats_button = Button(
            self._("Обновить список чатов"), self._reload_chats_list
        )
        self._back_button = Button(
            self._("Выйти"), self._back
        )

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        self._chats_list = ListBox(
            Widget.FILL_FRAME,
            options=[],
            name="chats",
            on_select=self._enter_chat
        )

        layout.add_widget(
            Label(self._('Список чатов'), align='^')
        )
        layout.add_widget(
            self._chats_list
        )

        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(self._build_chat_button, 0)
        layout2.add_widget(self._enter_chat_button, 1)
        layout2.add_widget(self._reload_chats_button, 2)
        layout2.add_widget(self._back_button, 3)
        self.fix()

    def _reload_chats_list(self: ChatsListView) -> None:
        with open("client/config.json", "r") as file:
            data = json.loads(file.read())
            self._model = MessageModel(data['url'])
            chats = self._model.get_chats()

            if chats['result']:
                # chats = [tuple(chat) for chat in chats['chats']]
                self._chats_list.options = chats['chats']
            elif not chats['result']:
                self._chats_list.options = []

    def _build_chat(self: ChatsListView) -> None:
        raise NextScene('StartChat')

    def _enter_chat(self: ChatsListView) -> None:
        self.save()   
        os.environ["TUI_CHAT_ID"] = self.data['chats']
        raise NextScene("Chat")

    def _reload_chats(self: ChatsListView) -> None:
        raise NextScene('ChatsList')

    def _back(self: ChatsListView) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, self._(f"Вы уверенны?"),
                [self._("Да"), self._("Нет")], has_shadow=True,
                on_close=self._quit_on_yes
            )
        )

    @staticmethod
    def _quit_on_yes(selected: int) -> None:
        if selected == 0:
            raise NextScene("StartMenu")
