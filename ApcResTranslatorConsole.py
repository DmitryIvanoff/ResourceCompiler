import time
import argparse
from pathlib import Path
from ApcWorkObj import ApcCompiler


def main(**kwargs):
    t1 = time.time()
    print(kwargs)
    if kwargs.get("dirs"):
        lDirs = kwargs["dirs"]
    else:
        lDirs = [Path(".")]  # cwd
    for d in lDirs:
        wd = Path(d)
        for p in wd.glob("*.xml"):
            xml_file = p
            json_file = wd.joinpath(p.name.split(".")[0] + ".json")
            compiler = ApcCompiler(xml_file.relative_to(wd), json_file.relative_to(wd), wd)
            langs = kwargs.get("langs")
            main_lang = kwargs.get("primal")
            mark = kwargs.get("mark", "$")
            service = kwargs.get("service")
            if not langs:
                compiler.save()
            else:
                compiler.update_json(langs, main_lang, mark, service=service)

    t2 = time.time()
    print("Время выполнения:", t2 - t1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Утилита для добавления переводов ресурсов."
        "Пример: python ApcResTranslatorConsole.py -l ENU -p RUS ./'",
        epilog="""

        Простой сценарий:
        Допустим у нас ресурсы переведены на русский ("RUS").
        1. Добавляем новый язык например Азербайджанский (AZ):
        Пример: "python ApcResTranslatorConsole.py -l AZ -p RUS ./test/Dir1 ./Dir2".
        D JSONe добавятся поля AZ с автопереводом, помеченным '*' (параметр -m);
        язык, с которого переводит сервис, можно указать в параметре -p (по умолчанию Русский),
        а также сам сервис в параметре -s;
        2. Изменяем поля и/или заполняем пустые поля переводом (качественным:)). Можно оставить поля пустыми,
        тогда сервис для перевода переведет их с языка, который вы укажете (параметр -p);
        Выполняем сохранение своих изменений (пустые поля заполнятся машинным переводом:
        "python ApcResTranslatorConsole.py -p RUS ./test/Dir1 ./Dir2 ").
        """)

    parser.add_argument("-l", "--langs",
                        nargs="+",
                        help="Языки, которые будут добавлены/обновлены и появятся в JSONе "
                             "(поддерживаемые языки: %(choices)s)",
                        choices=ApcCompiler.get_langs(),
                        metavar="LANGS"
                        )
    # parser.add_argument("-a", "--apply",
    #                     action="store_true",
    #                     required=False,
    #                     help="Флаг для применения изменений (default: %(default)s)",
    #                     default=False,
    #                     )
    parser.add_argument("-p", "--primal",
                        help="Язык, с которого будет переводить сервис (default: %(default)s)",
                        metavar="Main lang",
                        default="RUS",
                        )
    parser.add_argument("-s", "--service", required=False,
                        help="Cервис-переводчик (default: %(default)s)",
                        default="Yandex",
                        metavar="SERVICE")
    parser.add_argument("dirs", nargs="+",
                        help="Директории, в которых лежит xml файл и папки с ресурсами 'RUS', 'ENU' и тд")
    parser.add_argument("-m", "--mark", required=False, default="$",
                        help="Специальный символ для пометки машинного перевода (default: %(default)s)")

    parser.add_argument("--loglevel", required=False, default="INFO",
                        help="Уровень логирования (default: %(default)s)")

    args = parser.parse_args()
    main(**args.__dict__)
