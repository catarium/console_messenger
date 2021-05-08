import sys
import json

from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.effects import Julia
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from contact_model import ContactModel
from widgets import ListView, ContactView, LogAndRegMenu, Login, Register


with open('config.json') as f:
    config = json.load(f)


def demo(screen, scene):
    scenes = [
        Scene([Julia(screen), LogAndRegMenu(screen, contacts)], -1, name="LogAndReg"),
        Scene([Julia(screen), Login(screen, contacts)], -1, name="Login"),
        Scene([Julia(screen), Register(screen, contacts)], -1, name="Registration")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


contacts = ContactModel(config['url'])
last_scene = None

while True:

    try:
        Screen.wrapper(demo, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
