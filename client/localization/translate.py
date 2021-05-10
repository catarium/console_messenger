from __future__ import annotations

from googletrans import Translator


class Localizate:

    tanslator: Translator = Translator()

    def __init__(self: Localizate, language: str = "ru") -> None:
        self.language: str = language

    def __call__(self: Localizate, text: str) -> str:
        if self.language != "ru":
            return self.tanslator.translate(
                text, dest=self.language
            ).text
        return text
