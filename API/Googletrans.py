# Это не переводчик гугл. Это "free" переводчик гугл, который не поддерживается (см. GoogleAPI)
from googletrans import Translator

translator = Translator(service_urls=[
    'translate.google.com',
    'translate.google.ru',
])
if __name__ == "__main__":
    translated = translator.translate("контроль повторного входа", dest="en", src="ru")
    print(translated.text)
