from __future__ import annotations

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

from contact_model import ContactModel


class LogAndRegMenu(Frame):

    def __init__(
        self: LogAndRegMenu, screen: Screen, model: ContactModel
    ) -> None:
        super().__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            can_scroll=False,
            title="Чат"
        )
        self._model = model
        self._reg_button = Button('Регистрация', self._registration)
        self._log_button = Button('Вход', self._login)
        self._quit_button = Button('Закрыть', self._quit)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Label('Пожалуйста, войдите или зарегистрируйтесь', align='^',
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
                self._screen, "Вы уверенны?",
                ["Да", "Нет"], has_shadow=True,
                on_close=self._quit_on_yes
            )
        )

    @staticmethod
    def _quit_on_yes(selected: int) -> typing.NoReturn:
        if selected == 0:
            raise StopApplication("User pressed quit")


class Login(Frame):

    def __init__(
        self: Login, screen: Screen, model: ContactModel
    ) -> None:
        super().__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            can_scroll=False,
            title="Вход"
        )

        self._model = model

        layout = Layout([100], fill_frame=False)
        self.add_layout(layout)

        layout.add_widget(Text('Имя пользователя:', 'username'))
        layout.add_widget(Text('Пароль:', 'password'))

        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        self._login_button = Button('Вход', self._login)
        self._back_button = Button('Назад', self._back)
        layout2.add_widget(self._login_button, 0)
        layout2.add_widget(self._back_button, 1)

        self.fix()

    def _login(self: Login) -> None:
        self.save()
        if not self.data['username'] or not self.data['password']:
            self._keyerror_handler()
        res = self._model.login(self.data['username'], self.data['password'])
        if res['result']:
            raise NextScene
        else:
            self._user_not_found_handler(res['msg'])
    
    def _keyerror_handler(self: Login) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, "Пожалуйста, заполните все поля!",
                ["Ок", "Назад"], has_shadow=True,
                on_close=self._keyerror_handler_on_yes
            )
        )

    def _user_not_found_handler(self: Login, msg: str) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, msg,
                ["Ok", "Назад"], has_shadow=True,
                on_close=self._keyerror_handler_on_yes
            )
        )

    @staticmethod
    def _keyerror_handler_on_yes(selected) -> None:
        if selected == 0:
            raise NextScene("Login")
        raise NextScene("LogAndReg")

    def _back(self: Login) -> None:
        raise NextScene('LogAndReg')


class Register(Frame):

    def __init__(
        self: Login, screen: Screen, model: ContactModel
    ) -> None:
        super().__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            can_scroll=False,
            title="Регистрация"
        )

        self._model = model

        layout = Layout([100], fill_frame=False)
        self.add_layout(layout)

        layout.add_widget(Text('Имя пользователя:', 'username'))
        layout.add_widget(Text('Пароль:', 'password'))

        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        self._login_button = Button('Регистрация', self._registration)
        self._back_button = Button('Назад', self._back)
        layout2.add_widget(self._login_button, 0)
        layout2.add_widget(self._back_button, 1)

        self.fix()

    def _registration(self: Login) -> None:
        self.save()
        if not self.data['username'] or not self.data['password']:
            self._keyerror_handler()
        res = self._model.register(self.data['username'], self.data['password'])
        print(res)
    
    def _keyerror_handler(self: Login) -> None:
        self._scene.add_effect(
            PopUpDialog(
                self._screen, "Пожалуйста, заполните все поля!",
                ["Ок", "Назад"], has_shadow=True,
                on_close=self._keyerror_handler_on_yes
            )
        )

    @staticmethod
    def _keyerror_handler_on_yes(selected) -> None:
        if selected == 0:
            raise NextScene("Registration")
        raise NextScene("LogAndReg")

    def _back(self: Login) -> None:
        raise NextScene('LogAndReg')


class ListView(Frame):
    def __init__(self, screen, model):
        super(ListView, self).__init__(screen,
                                       screen.height * 2 // 3,
                                       screen.width * 2 // 3,
                                       on_load=self._reload_list,
                                       hover_focus=True,
                                       can_scroll=False,
                                       title="Contact List")
        # Save off the model that accesses the contacts database.
        self._model = model

        # Create the form for displaying the list of contacts.
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            model.get_summary(),
            name="contacts",
            add_scroll_bar=True,
            on_change=self._on_pick,
            on_select=self._edit)
        self._edit_button = Button("Edit", self._edit)
        self._delete_button = Button("Delete", self._delete)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        layout.add_widget(Divider())
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Add", self._add), 0)
        layout2.add_widget(self._edit_button, 1)
        layout2.add_widget(self._delete_button, 2)
        layout2.add_widget(Button("Quit", self._quit), 3)
        self.fix()
        self._on_pick()

    def _on_pick(self):
        self._edit_button.disabled = self._list_view.value is None
        self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self, new_value=None):
        self._list_view.options = self._model.get_summary()
        self._list_view.value = new_value

    def _add(self):
        self._model.current_id = None
        raise NextScene("Edit Contact")

    def _edit(self):
        self.save()
        self._model.current_id = self.data["contacts"]
        raise NextScene("Edit Contact")

    def _delete(self):
        self.save()
        self._model.delete_contact(self.data["contacts"])
        self._reload_list()

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


class ContactView(Frame):
    def __init__(self, screen, model):
        super(ContactView, self).__init__(screen,
                                          screen.height * 2 // 3,
                                          screen.width * 2 // 3,
                                          hover_focus=True,
                                          can_scroll=False,
                                          title="Contact Details",
                                          reduce_cpu=True)
        # Save off the model that accesses the contacts database.
        self._model = model

        # Create the form for displaying the list of contacts.
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Name:", "name"))
        layout.add_widget(Text("Address:", "address"))
        layout.add_widget(Text("Phone number:", "phone"))
        layout.add_widget(Text("Email address:", "email"))
        layout.add_widget(TextBox(
            Widget.FILL_FRAME, "Notes:", "notes", as_string=True, line_wrap=True))
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()

    def reset(self):
        # Do standard reset to clear out form, then populate with new data.
        super(ContactView, self).reset()
        self.data = self._model.get_current_contact()

    def _ok(self):
        self.save()
        self._model.update_current_contact(self.data)
        raise NextScene("Main")

    @staticmethod
    def _cancel():
        raise NextScene("Main")
