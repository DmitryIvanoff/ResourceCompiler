from pathlib import Path
import argparse
import re
import locale
import os
import logging.handlers
from stat import S_IWRITE
import xml.etree.ElementTree as ET
logger = logging.getLogger("count")
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
logger.addHandler(ch)

pattern_inikv = re.compile(r"(?m)^(?P<key>[\w0-9]+)=(?P<value>.+)$")
pattern_word = re.compile(r"\b[\w]+\b")


def make_backup(file, suffix=".bckp"):
    """

    :param file:
    :param suffix
    :return:
    """
    backup_path = str(file.resolve()) + suffix  # делаем backup
    backup = Path(backup_path)
    if not os.path.exists(backup_path):
        logger.info("  creating back up %s ...", backup_path)
        file.rename(backup)  # теперь содержимое file находится по пути backup
        file.touch()  # теперь file можно менять и писать туда
    else:
        backup.chmod(S_IWRITE)
        os.remove(backup)
        file.rename(backup)  # теперь содержимое file находится по пути backup
    return backup


def file_in_encoding(file, encoding="utf8"):
    logger.info("try to open file %s in encoding %s", str(file.resolve()), encoding)
    with file.open(mode="r", encoding=encoding) as fbckp:
        try:
            s = fbckp.read()
        except UnicodeDecodeError as e:
            logger.exception(e)
            return None
    logger.info("file %s successfully opened")
    return s


def parse_ini(s):
    count_words = 0
    count_chars = 0
    for m in pattern_inikv.finditer(s):
        v = m.group("value")
        for m_int in pattern_word.finditer(v):
            count_chars += len(m_int.group(0))
            count_words += 1
    return count_words, count_chars


def parse_xml(s):
    count_words = 0
    count_chars = 0
    for m_int in pattern_word.finditer(s):
        count_chars += len(m_int.group(0))
        count_words += 1
    return count_words, count_chars


def count_ini(aDir, recur=False, pattern="*"):
    aDir = Path(aDir)
    if not aDir.exists():
        logger.error("%s is not exist", aDir)
    if recur:
        pattern = "**/" + pattern
    words = 0
    chars = 0
    # ini files
    for path in aDir.glob(pattern):
        if recur:
            if re.search(r"[\\/]{1}Apacs30_old", str(path)):  # фильтр файлов
                continue
            if not re.search(r"[\\/]{1}Res", str(path)):  # фильтр файлов
                continue
            if not (path.name.replace(path.suffix, "").endswith("Rus")):  # or path.name.replace(path.suffix, "").endswith("Enu")):
                continue
        if path.suffix == ".ini":  # ini
            # bckp = make_backup(path)
            logger.info("try to open file %s", str(path.resolve()))
            with path.open(mode="rb") as fb:
                b = fb.read()
                s = ""
                for encoding in locale.getpreferredencoding(), "utf-8-sig", "utf-16":
                    try:
                        s = b.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                if not s:
                    logger.info("can't decode file")
                    return 4
            logger.info("file %s successfully opened")
            w, c = parse_ini(s)
            words += w
            chars += c

    return words, chars


def count_xml(aDir, recur=False, pattern="*"):
    aDir = Path(aDir)
    if not aDir.exists():
        logger.error("%s is not exist", aDir)
    if recur:
        pattern = "**/" + pattern
    words = 0
    chars = 0
    for path in aDir.glob(pattern):
        if recur:
            if re.search(r"[\\/]{1}Apacs_old", str(path)):  # фильтр файлов
                continue
            if not re.search(r"[\\/]{1}Help[\\/]{1}", str(path)):  # фильтр файлов
                continue
            # if not re.search(r"[\\/]{1}Help(Enu)?", str(path)):  # фильтр файлов
            #   continue
        if path.suffix == ".xml":  # xml
            try:
                tree = ET.parse(path)
            except BaseException:
                logger.info("cant parse %s", str(path))
                continue
            root = tree.getroot()
            for elem in root.findall(".//"):
                if elem.text:
                    w, c = parse_xml(elem.text)
                    words += w
                    chars += c

    return words, chars


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="toutf8.py", description="Утилита для перевода res ini files -> UTF8")
    parser.add_argument("dir", help="Директория, в которой ищем все файлы ")
    parser.add_argument("-r", "--recursive", required=False, help="если нужно рекурсивно", action="store_true", default=False)
    parser.add_argument("-l", "--loglevel", default="INFO", help="log level (default: %(default)s)")
    args = parser.parse_args()
    logging.basicConfig(format="[%(levelname)s]:  %(message)s", level=args.loglevel, filename="toutf8.log",
                        filemode="w")
    print(args)
    if args.recursive:
        words1, chars1 = count_ini(args.dir, args.recursive)
        print("INI: words: ", str(words1), "chars: ", str(chars1))
        words2, chars2 = count_xml(args.dir, args.recursive)
        print("XML: words: ", str(words2), "chars: ", str(chars2))
    else:
        words1, chars1 = count_ini(args.dir)
        print("INI: words: ", str(words1), "chars: ", str(chars1))
        words2, chars2 = count_xml(args.dir)
        print("XML: words: ", str(words2), "chars: ", str(chars2))
    print("ALL words: ", str(words1 + words2), "chars:", str(chars1 + chars2))
