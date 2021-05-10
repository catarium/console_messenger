import sys
import json

from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.effects import Julia
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from client.models import MessageModel
from client.views import (
    StartMenuView, LoginView, RegistrationView, ChatsListView, 
    ChatView
)


with open('client/config.json') as f:
    config = json.load(f)


def demo(screen, scene):
    scenes = [
        Scene([Julia(screen), StartMenuView(screen)], -1, name="StartMenu"),
        Scene([Julia(screen), LoginView(screen, contacts)], -1, name="Login"),
        Scene([Julia(screen), RegistrationView(screen, contacts)], -1, name="Registration"),
        Scene([Julia(screen), ChatsListView(screen, contacts)], -1, name="ChatsList"),
        Scene([Julia(screen), ChatView(screen, contacts)], -1, name="Chat"),
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


contacts = MessageModel(config['url'])
last_scene = None

while True:

    try:
        Screen.wrapper(demo, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
