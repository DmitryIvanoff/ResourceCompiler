from API import YandexAPI, GoogleAPI  # пока не используем
from ApcLogger import getLogger
from functools import lru_cache
from typing import Iterable, List
import abc


class Exc_wrap:
    def __init__(self, logger):
        self._logger = logger

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self._logger.exception(e)
                raise

        return wrapper


class Translator:
    # Наши названия языков - названия языков в сервисе
    languages = {
        "RUS": "ru",
        "ENU": "en",
        "KAZ": "kk",
        "UKR": "uk",
        "AZE": "az",
        "ESP": "es",
        "RON": 'ro'
    }
    logger = getLogger(name="Translator")

    def __init__(self, name):
        self._name = name

    @abc.abstractmethod
    def get_token(self):
        raise NotImplementedError

    @abc.abstractmethod
    def set_token(self, token: str):
        raise NotImplementedError

    def __str__(self):
        return self._name

    @abc.abstractmethod
    def translate(self, text: str, dest: str, src: str = "RUS"):
        raise NotImplementedError


class YandexTranslator(Translator):

    def __init__(self, key=None):
        super().__init__("Yandex")
        if key:
            YandexAPI.key = key

    def get_token(self):
        return YandexAPI.key

    def set_token(self, token: str):
        YandexAPI.key = token

    @lru_cache(maxsize=512)  # кешируем
    @Exc_wrap(Translator.logger)
    def translate(self, text: str, dest, src=None) -> str:
        self.logger.debug(f"translating")
        if src:
            return YandexAPI.translate(
                [text],
                self.languages[dest],
                self.languages[src]
            )[0]
        else:
            return YandexAPI.translate(
                [text],
                self.languages[dest])[0]

    def translate_batch(self, texts: Iterable[str], dest: str, src: str = None) -> List[str]:
        if src:
            return YandexAPI.translate(
                texts,
                self.languages[dest],
                self.languages[src]
            )
        else:
            return YandexAPI.translate(
                texts,
                self.languages[dest])


class GoogleTranslate_v2(Translator):
    def __init__(self):
        super().__init__("GoogleTranslate_v2")

    def set_token(self, token: str):
        GoogleAPI.set_credentials(token)

    def get_token(self):
        return GoogleAPI.get_credentials()

    @lru_cache(maxsize=512)  # кешируем
    @Exc_wrap(Translator.logger)
    def translate(self, text, dest, src="RUS"):
        if text:
            return GoogleAPI.translate(text, self.languages[src], self.languages[dest])
        else:
            return ""
