import requests
import traceback
from urllib.parse import *
from typing import Iterable, List

# https://cloud.yandex.ru/docs/translate/api-ref/authentication
key = ""  # your service account API-key for 'Translate' from Yandex.Cloud
api_url = urlparse("https://translate.api.cloud.yandex.net/translate/v2/translate")


def get_langs():
    try:
        r = requests.post(
            urljoin(api_url.geturl(), "languages"),
            headers={"Authorization": f'Api-Key {key}'})
        result = r.json()
        if r.status_code != 200:
            print(result)
            return ""
        return r
    except BaseException:
        print(traceback.format_exc())
        return ""


def translate(
        texts: Iterable[str],
        target: str,
        format: str = "PLAIN_TEXT",
        source: str = None,
        glossary: list = None) -> List[str]:
    """https://cloud.yandex.ru/docs/translate/api-ref/Translation/translate.

    :param texts: list of texts
    :param target:
    :param source:
    :param format:
    :param glossary: list of pairs (tuples(sourceText,translatedText))
    :return: list of translated texts
    """
    # create params dict
    params = dict()
    try:
        if texts:
            params["texts"] = list(texts)
        if target:
            params["targetLanguageCode"] = target
        if source:
            params["sourceLanguageCode"] = source
        if format == "HTML":
            params["format"] = "HTML"
        if glossary:
            params["glossaryConfig"] = dict()
            params["glossaryConfig"]["glossaryData"] = dict()
            glossaryData = params["glossaryConfig"]["glossaryData"]
            glossaryData['glossaryPairs'] = [
                {"sourceText": k, "translatedText": v} for (k, v) in glossary
            ]
        r = requests.post(
            urljoin(api_url.geturl(), "translate"),
            json=params,
            headers={"Authorization": f'Api-Key {key}'})
        result = r.json()
        if r.status_code != 200:
            print(result)
            return [""]
        else:
            return [t["text"] for t in result["translations"]]
    except BaseException:
        print(traceback.format_exc())
        return [""]


if __name__ == "__main__":
    langs = get_langs().json()["languages"]

    print(langs)
    text1 = "Поиск оборудования Apollo осуществляется в два этапа.\
   Первый — широковещательный запрос, с помощью которого осуществляется поиск модулей Lantronix,\
второй этап — поиск дочерних панелей по протоколу TCP. Если на дочерних панелях используется шифрование данных,\
то в утилите поиска эти панели отображаться не будет."
    translated_text1 = translate([text1], "en", "ru")[0]
    print(text1, translated_text1)

    text2 = "Утилита предназначена для поиска оборудования и программного обеспечения (далее ПО), \
запущенного на компьютерах, в локальной сети предприятия.\
Утилита предоставляет информацию о настройках и текущей конфигурации оборудования/ПО,\
а также позволяет применять ряд внешних команд к найденному оборудованию."
    translated_text2 = translate([text2], "uk", "ru")[0]
    print(text2, translated_text2)
