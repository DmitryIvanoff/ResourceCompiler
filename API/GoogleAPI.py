# api
import os
from pathlib import Path

"""Translates text into the target language.

Target must be an ISO 639-1 language code.
See https://g.co/cloud/translate/v2/translate-reference#supported_languages
"""
import google.cloud.translate_v2 as translate_v2

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath("./GoogleAPI_cred.json")

translate_client = None


def set_credentials(file: str):
    """https://cloud.google.com/docs/authentication/getting-started.

    :param file:
    :return:
    """
    if not file:
        return
    global translate_client
    file = file.strip("\n\"\' ")
    file = Path(file).resolve().absolute()
    translate_client = translate_v2.Client.from_service_account_json(str(file))


def get_credentials():
    return os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")


# todo: перейти с Cloud Translate Basic -> Advanced
# 1. batch requests
# 2. glossaries


def translate(text, source, target, format_="text", model=None):
    if not translate_client:
        return ""
    result = translate_client.translate(
        text,
        target_language=target,
        source_language=source,
        format_=format_, model=model)
    return result.get("translatedText", "")


def get_supported_langs():
    """Lists all available languages and localizes them to the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    if not translate_client:
        return ""
    return translate_client.get_languages(target_language="ru")


# set_credentials(str(Path(__file__).parent.joinpath("GoogleAPI_cred.json")))


if __name__ == "__main__":
    from pprint import pprint

    set_credentials("./GoogleAPI_cred.json")
    pprint(get_credentials())
    pprint(get_supported_langs())
    text1 = " Связи с ним не было. Поиск оборудования Apollo осуществляется в два этапа.\
   Первый — широковещательный запрос, с помощью которого осуществляется поиск модулей Lantronix,\
второй этап — поиск дочерних панелей по протоколу TCP. Если на дочерних панелях используется шифрование данных,\
то в утилите поиска эти панели отображаться не будет."
    translated_text1 = translate(text1, "ru", "en")
    print(text1, translated_text1)

    text2 = "Связи с ним не было. Утилита предназначена для поиска оборудования и программного обеспечения (далее ПО), \
запущенного на компьютерах, в локальной сети предприятия.\
Утилита предоставляет информацию о настройках и текущей конфигурации оборудования/ПО,\
а также позволяет применять ряд внешних команд к найденному оборудованию."
    translated_text2 = translate(text1, "ru", "uk")
    print(text2, translated_text2)
