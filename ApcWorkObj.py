"""
ResourceCompiler
Алгоритм работы:
Папка с ресурсами (ResClMain например),
Там есть xml файл (например, ApcRegResources.xml) вида:
#######
<?xml version="1.0" encoding="WINDOWS-1251" standalone="no" ?>
<Registry Version="1">

  <Key ID="RESOURCES\ApcMapiError">
    <Key ID="RUS">
      <KeyValue Name="FileTxt" vType="String" vValue="\Rus\ApcResourcesRus.ini"/>
    </Key>
    <Key ID="ENU">
      <KeyValue Name="FileTxt" vType="String" vValue="\Enu\ApcResourcesEnu.ini"/>
    </Key>
  </Key>

</Registry>
#######
1. Initialization. Задать(через консоль или в GUI) языки, для которых нужен перевод и основной язык,
 с которого будем переводить(для API сервиса)
2. Validation. (проверка совпадения ресурсов *.ini с тем,что есть в <ProjectName>Resources.json)
(из всех *.ini файлов вытащить данные в JSON (<ProjectName>Resources.json),
добавить указанные языки (новые ini файлы аналоги *Rus.ini))
3. Compilation. JSON компилировать обратно в ресурсы , при этом где нет перевода, добавлять перевод сервиса (помечать такие переводы),
который выберем, а где уже был с заменой, кроме основного языка (русского)
4*. Словарь названий языков:
 {
  "RUS": "Русский",
  "ENU": "Английский",
  "kk": "Казахский",
  "uk": "Украинский",
  "az": "Азербайджанский"
 }
"""
from pathlib import Path
import copy
import sys
import re
import threading
from pprint import pformat
from functools import lru_cache
from traceback import format_exc
# ------- наши модули ----------
from ApcEditor import JSONEditor, IniEditor  # ,XMLEditor
from Tree import BPTree
from TranslateService import YandexTranslator, GoogleTranslate_v2  # пока не используем
from ApcLogger import getLogger
from ApcResEditor import ResXMLEditor
from typing import Iterable
from os import PathLike

# временная папка, в которую распаковываются файлы при запуске exe
# когда собрано в 'one-file' (см build.py) mode
# https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
bundle_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))


class ApcCompiler:
    languages = {
        "RUS": "Русский",
        "ENU": "Английский",
        "KAZ": "Казахский",
        "UKR": "Украинский",
        "AZE": "Азербайджанский",
        "ESP": "Испанский",
        "RON": "Румынский"
    }

    services = {
        "Yandex": YandexTranslator(),  # , пока не используем
        "Google": GoogleTranslate_v2()
    }

    default_lang = "RUS"
    abbrs_editor = None
    abbreviations = []  # abbrs_editor.sections["abbreviations"]

    logger = getLogger("ApcCompiler", loglevel="INFO")

    apc_res_format = re.compile(r"(?x)"
                                r"(?:"
                                r"  (?P<word>%[\w]{2,}%)|"
                                r"  (?P<sym>%[sdn])|"
                                r"  (?P<digit>%[\d]%)"
                                r")")

    @staticmethod
    def set_log_level(loglevel):
        ApcCompiler.logger = getLogger("ApcCompiler", loglevel=loglevel)
        IniEditor.logger = getLogger("IniEditor", loglevel=loglevel)
        ResXMLEditor.logger = getLogger("ResXMLEditor", loglevel=loglevel)
        JSONEditor.logger = getLogger("JSONEditor", loglevel=loglevel)

    @staticmethod
    def set_abbreviations(abbrs: Iterable = None, filename: PathLike = None):
        if abbrs:
            ApcCompiler.abbreviations = abbrs
        elif filename and Path(filename).exists():
            ApcCompiler.abbrs_editor = JSONEditor(Path(filename))
            ApcCompiler.abbrs_editor.open()
            ApcCompiler.abbreviations = ApcCompiler.abbrs_editor.sections["abbreviations"]
        else:
            ApcCompiler.abbrs_editor = JSONEditor(bundle_dir.joinpath("abbreviations.json"))
            ApcCompiler.abbrs_editor.open()
            ApcCompiler.abbreviations = ApcCompiler.abbrs_editor.sections["abbreviations"]
        # ApcCompiler.logger.debug(f"abbreviations:\n{pformat(ApcCompiler.abbreviations)}")

    def __init__(self, xml_file=None, json_file=None, wd=None, auto_tr_ch: str = '$',
                 service: str = None):
        """# todo: support many xml files

        :type xml_file: path-like object
        :type json_file: path-like object
        :type wd: path-like object
        :type service: str
        """
        self.logger.debug(f"constructing ApcWorkObj {str(xml_file)}")
        self.mutex = threading.Lock()  # make reading/writing operation of resources safe
        if not wd:
            wd = Path(".")
        if not xml_file:
            lRes = self.findXML(wd)
            self.logger.debug("Found xmls:%s", str(lRes))
            for xml_f, js_f in lRes:  # берем первый
                xml_file = Path(xml_f)
                if not json_file:
                    json_file = js_f
                break
        else:
            xml_file = Path(xml_file)
        if not xml_file:
            raise ValueError(f"Can't find XML file in {str(wd.resolve())}")
        if not json_file:
            json_file = Path(xml_file.name.split(".")[0] + ".json")
        else:
            json_file = Path(json_file)
        if xml_file.is_absolute():
            self.XML_editor = ResXMLEditor(xml_file)
        else:
            self.XML_editor = ResXMLEditor(wd.joinpath(xml_file))
        if json_file.is_absolute():
            self.JSON_editor = JSONEditor(json_file)
        else:
            self.JSON_editor = JSONEditor(wd.joinpath(json_file))
        self.JSON_editor.open()
        self.XML_editor.open()  # todo: cache (pickle) resources representation
        self.XML_editor.parse_sections()
        self.wd = wd
        self.metainfo = self.JSON_editor.sections.get("METAINFO")
        if not self.metainfo:
            self.JSON_editor.sections["METAINFO"] = dict()
            self.metainfo = self.JSON_editor.sections["METAINFO"]
        self.auto_tr_ch = self.metainfo.get("Char", auto_tr_ch)
        self.service = self.metainfo.get("Service", service)
        self.json_langs = set(self.metainfo.get("JSONLangs", set()))
        self.main_lang = self.metainfo.get("MainLang", self.default_lang)
        self.langs = set(self.metainfo.get("ResLangs", set()))  # языки, которые есть в ресурсах
        if not self.langs:
            if not self.XML_editor.sections.get("RESOURCES"):
                raise ValueError(f"Can't find 'RESOURCES' tag in {str(self.XML_editor.file)}")
            for obj in self.XML_editor.sections["RESOURCES"]:
                dObj = self.XML_editor.sections["RESOURCES"][obj]
                for lang in dObj:
                    self.langs.add(lang)
        self.metainfo.update({
            "MainLang": self.main_lang,
            "ResLangs": list(self.langs),
            "SupportedLangs": self.languages,
            "Char": self.auto_tr_ch,
            "Service": self.service,
            "JSONLangs": list(self.json_langs)
        })
        self.logger.debug("saving metainfo")
        self.JSON_editor.save()

    def update_json(self, langs, main_lang: str = default_lang, auto_tr_ch: str = "$",
                    service: str = None, progress_callback=None):
        """Загружаем все из xml(со всеми ini) в dict Переструктурируем dict грузим
        в json.

        :param main_lang:
        :param langs:
        :param auto_tr_ch:
        :param service:
        :return:
        """
        try:
            self.logger.info("update_json")
            self.mutex.acquire()  # lock cause reading resources
            if service:
                if service in self.services:  # if set, check for availability
                    self.service = service
                else:
                    raise ValueError(f"{service} is not supported!")
            else:
                self.service = service
            self.metainfo.update({
                "Service": service
            })
            if main_lang not in self.langs:
                raise ValueError(f"Main lang: {main_lang} is not in our resources")
            self.auto_tr_ch = auto_tr_ch
            self.main_lang = main_lang
            self.metainfo.update({
                "MainLang": main_lang,
                "Char": self.auto_tr_ch,
            })
            self.logger.info("Thread: %s", threading.current_thread().name)
            self.logger.info("Compiling %s", str(self.JSON_editor.file))
            self.logger.info("Service: %s", str(self.service))
            # representation to JSON
            XML_repr = copy.deepcopy(self.XML_editor.sections)
            self.logger.debug("XML: %s", str(XML_repr))
            # Intersection of langs and ResLangs to json_repr
            progress = 0
            JSON_repr = self._convert_to_JSON_repr(set(langs) | {main_lang}, XML_repr, progress, progress_callback)
            # self.logger.debug("Representation for JSON after converting: %s", str(JSON_repr))
            self.logger.info("JSON langs after convert: %s", str(self.json_langs))
            # new langs to resources and JSON (langs - ResLangs)
            self._add_new_langs(JSON_repr, set(langs), progress, progress_callback)
            self.logger.info("JSON langs after add new: %s", str(self.json_langs))
            # self.logger.debug("New representation for JSON: %s", str(JSON_repr))
            self.JSON_editor.sections["RESOURCES"] = JSON_repr["RESOURCES"]
            self.metainfo.update({
                "JSONLangs": list(self.json_langs),
            })
            self.JSON_editor.save(encoding="utf-8")
            if progress_callback:
                progress_callback.emit(round(100.0))
        finally:
            self.mutex.release()

    def _add_new_langs(self, JSON_repr: dict, langs, progress, callback=None) -> None:
        new_langs = set(langs) - self.langs
        len_langs = float(len(new_langs))
        for l in (new_langs):  # new languages which are not in res langs
            # rebuild abbrs dict
            abbrs = {list(abbr[self.main_lang].keys())[0]: list(abbr[l].keys())[0] for abbr in self.abbreviations if
                     "" not in abbr[l].keys()}
            self.logger.info("Add new language: %s", l)
            # insert new
            self.json_langs.add(l)
            len_resources = float(len(JSON_repr["RESOURCES"]))
            for obj in JSON_repr["RESOURCES"]:
                dObj = JSON_repr["RESOURCES"][obj]
                len_sections = float(len(dObj))
                for section in dObj:
                    dOptions = dObj[section]
                    len_options = float(len(dOptions))
                    for option in dOptions:
                        if self.main_lang != l:
                            translation = dOptions[option].get(l, "")
                            if self.service:  # service translation
                                translation = self.translate(dOptions[option][self.main_lang], l, abbrs)
                                if translation:
                                    translation = self.auto_tr_ch + translation
                            dOptions[option].update({l: translation})
                        if callback:
                            # 2 - число шагов (_convert, _add)
                            progress += 1.0 / (len_resources * len_langs * len_options * len_sections * 2.0)
                            callback.emit(round(100.0 * progress))
                        self.logger.debug("progress: %s", str(progress))
        self.logger.info("Add new langs to JSON")
        self.metainfo.update({
            "JSONLangs": list(self.json_langs),
        })
        self.JSON_editor.save(encoding="utf8")

    def _convert_to_JSON_repr(self, langs, representation, step=1, callback=None) -> dict:
        self.logger.debug("Converting from tree XML-Ini to JSON tree")
        self.json_langs = set(langs) & set(self.langs)
        progress = float(step) / 2.0
        len_resources = float(len(representation["RESOURCES"]))
        for obj in representation["RESOURCES"]:
            obj_tree = BPTree()
            dObj = representation["RESOURCES"][obj]
            editor = self._search_ini_file(self.main_lang, obj, representation["RESOURCES"])
            editor.open()
            dSections_main_lang = editor.sections
            len_langs = float(len(self.json_langs))
            for lang in self.json_langs:
                # rebuild abbrs dict
                abbrs = {list(abbr[self.main_lang].keys())[0]: list(abbr[lang].keys())[0] for abbr in self.abbreviations if
                         "" not in abbr[lang].keys()}
                editor = self._search_ini_file(lang, obj, representation["RESOURCES"])
                if editor.file.name.endswith("_BinOther.ini") or editor.file.name.endswith("_PanelBin.ini"):
                    dObj[lang] = editor.sections
                    # representation["RESOURCES"][obj] = obj_tree.to_dict()
                    continue
                editor.open()
                dObj[lang] = editor.sections
                dSections = dObj[lang]
                # futures=[]
                len_sections = float(len(dSections_main_lang))
                for s in dSections_main_lang:
                    len_options = float(len(dSections_main_lang[s]))
                    dOptions = dSections.get(s)
                    if not dOptions:  # copy options from dSections_main_lang
                        dOptions = copy.deepcopy(dSections_main_lang[s])
                        for op in dOptions:
                            translation = ""
                            if self.service:  # service translation
                                translation = self.translate(dSections_main_lang[s][op], lang, abbrs)
                                if translation:
                                    translation = self.auto_tr_ch + translation
                            dOptions[op] = {lang: translation}
                            progress += 1.0 / (len_resources * len_langs * len_options * len_sections * 2.0)
                            if callback:
                                callback.emit(round(100.0 * progress))
                            self.logger.debug("progress: %s", str(progress))
                        self.logger.debug("%s", str({s: dOptions}))
                        dSections.update({s: dOptions})
                    else:
                        for op in dSections_main_lang[s]:
                            if not dOptions.get(op):
                                self.logger.debug("%s", op)
                                translation = ""
                                if self.service:  # service translation
                                    translation = self.translate(dSections_main_lang[s][op], lang, abbrs)
                                    if translation:
                                        translation = self.auto_tr_ch + translation
                                dOptions[op] = {lang: translation}
                            else:
                                dOptions[op] = {lang: dOptions[op]}
                            progress += 1.0 / (len_resources * len_langs * len_sections * len_options * 2.0)
                            if callback:
                                callback.emit(round(100.0 * progress))
                            self.logger.debug("progress: %s", str(progress))
                    for op in set(dOptions) - set(dSections_main_lang[s]):
                        dOptions.pop(op)
                for s in set(dSections) - set(dSections_main_lang):
                    dSections.pop(s)
                BPTree.left_join(obj_tree, BPTree.from_dict(dObj[lang]))
            # self.logger.debug("Resources tree: %s", obj_tree)
            representation["RESOURCES"][obj] = obj_tree.to_dict()
        self.logger.info("Resources langs: %s", str(self.langs))
        return representation

    @staticmethod
    def replace_abbrs(text: str, abbrs) -> (str, dict):
        """replacing abbreviations with (__{<index>}__)

        @return: replaced string = "<repl1> ...", groups = {"repl1":"abbr1", ...}
        """
        replaces_abbrs = [(re.search(r'(?i)\b' + re.escape(abbr) + r'(ы|и|е|а|я|у|ю|ом|ов|ам|ах|ами|ой|ей|ёй|ая|ые|ый|ья)?\b', text), abbr) for abbr in abbrs]
        replaces_abbrs.append((re.search(r'__redirect\([\w ,]+\)', text), None))
        if not any(replaces_abbrs):  # filter
            return text, {}
        s = text
        groups = dict()
        index = 0

        for m, abbr in replaces_abbrs:
            if not m:
                continue
            _repl = f"(__{str(index)}__)"
            if abbr:
                s, count = re.subn(r'(?i)\b' + re.escape(abbr) + r'(ы|и|е|а|я|у|ю|ом|ов|ам|ах|ами|ой|ей|ёй|ая|ые|ый|ья)?\b', "{" + _repl + "}", s)
            else:
                s, count = re.subn(re.escape(m.group()), "{" + _repl + "}", s)
            if count:
                ApcCompiler.logger.debug(f"replaced string: {s}")
                groups[_repl] = abbrs[abbr] if abbr else m.group()
                index += 1
        return s, groups

    @staticmethod
    def replace_format(text: str) -> (str, list):
        """replacing our format symbols with {}

        @return: replaced string = "{} ...", groups = [<sym1>,...]
        """
        if not re.search(ApcCompiler.apc_res_format, text):  # filter
            return text, {}
        s = ""
        groups = []#{}
        startpos = 0
       # index = 0
        for m in re.finditer(ApcCompiler.apc_res_format, text):
            s += text[startpos:m.start()]
            #_repl = f"(_{str(index)}_)"
            s += '{}'#"{"+_repl+"}"
            startpos = m.end()
            #index += 1
            #groups[_repl] = m.group()
            groups.append(m.group())
        s += text[startpos:]
        return s, groups

    @staticmethod
    def check_symbols_displacement(text: str, translation: str) -> str:
        """check our special format symbols displacement respect to other words
        (check spaces around)

        @param text: original text
        @param translation: translated text (probably, with wrong spaces between words)
        @return: correct traslation string
        """
        if not text or not translation:
            return translation
        spec_sym_pattern = re.compile(r"[{}<>$%/()\\|*+&—\-»«_°:]")
        s = ""
        startpos = 0
        editions = 0
        ApcCompiler.logger.debug([zip(re.finditer(spec_sym_pattern, text), re.finditer(spec_sym_pattern, translation))])
        for m, tr_m in zip(re.finditer(spec_sym_pattern, text), re.finditer(spec_sym_pattern, translation)):
            len_tr = len(translation)
            len_text = len(text)
            if m.group() != tr_m.group():  # нашли несоответствие симоволов - выходим
                ApcCompiler.logger.warning(f"Symbols do not match! {m.group()},{tr_m.group()}")
                break
            if m.start() > 0 and tr_m.start() > 0:
                if text[m.start() - 1] != ' ' and translation[tr_m.start() - 1] == ' ':  # убираем ' ' в начале
                    s += translation[startpos:tr_m.start() - 1]
                    s += tr_m.group()
                    startpos = tr_m.end()
                    editions += 1
                elif text[m.start() - 1] == ' ' and translation[tr_m.start() - 1] != ' ':  # добавляем ' ' в начале
                    s += translation[startpos:tr_m.start()]
                    s += ' '
                    s += tr_m.group()
                    startpos = tr_m.end()
                    editions += 1
                ApcCompiler.logger.debug(s) if s else None
                if m.end() < len_text and tr_m.end() < len_tr:
                    #для случаев, когда в русском варианте есть после, например, скобок запятая, а на втором языке - нет
                    if text[m.end()] != ' ' and text[m.end()] != ',' and translation[tr_m.end()] == ' ':  # убираем ' ' в конце
                        if re.match(spec_sym_pattern, text[m.end()]):  # кейс который из начала уберет
                            continue
                        s += translation[startpos:tr_m.end()]
                        startpos = tr_m.end() + 1
                        editions += 1

                    elif text[m.end()] == ' ' and translation[tr_m.end()] != ' ':  # добавляем ' ' в конец
                        if re.match(spec_sym_pattern, translation[tr_m.end()]):  # кейс который из начала добавит
                            continue
                        s += translation[startpos:tr_m.end()]
                        s += ' '
                        startpos = tr_m.end()
                        editions += 1
                elif m.end() == len_text and tr_m.end() < len_tr:
                    if not translation[tr_m.end():].strip():  # были пробелы
                        translation = translation[:tr_m.end()]
                        editions += 1
                elif m.end() < len_text and tr_m.end() == len_tr:
                    if not text[m.end():].strip():  # были пробелы
                        s += translation[startpos:tr_m.end()]
                        s += text[m.end():]
                        startpos = tr_m.end()
                        editions += 1
                ApcCompiler.logger.debug(s) if s else None
            elif m.start() == 0 and tr_m.start() > 0:
                if not translation[:tr_m.start()].strip():  # были пробелы
                    startpos = tr_m.start()
                    editions += 1
            elif m.start() > 0 and tr_m.start() == 0:
                if not text[:m.start()].strip():  # были пробелы
                    s += text[:m.start()]
                    editions += 1
            ApcCompiler.logger.debug(s) if s else None
        if editions:
            s += translation[startpos:]
            translation = s
        return translation

    def translate(self, text: str, lang: str, abbrs=None, service: str = None) -> str:
        if not self.service:
            if service:
                self.service = service
            else:
                return ""
        try:
            raw_text = text
            # define abbreviations
            if abbrs is None:
                abbrs = {list(abbr[self.main_lang].keys())[0]: list(abbr[lang].keys())[0] for abbr in self.abbreviations if
                         "" not in abbr[lang].keys()}

            # replace some special symbols
            if lang == "UKR":
                brackets_exprs = []
                for m in re.finditer(r"<(\b[\w\s]+\b)>", text):
                    brackets_exprs.append(m.group(1))
                if brackets_exprs:
                    text = re.sub(r"<(\b[\w\s]+\b)>", r"<%>", text)
                ApcCompiler.logger.debug(f"after '<value>' replacement:\n'{text}'")

            # replace abbreviations
            text, abbrs_repls = self.replace_abbrs(text, abbrs)
            self.logger.debug(f"after abbreviations replacement:\n'{text}'")

            # replace our formattings strings
            text, format_repls = self.replace_format(text)
            self.logger.debug(f"after format replacement:\n'{text}'")

            # translate
            translation = self.services[self.service].translate(text, lang,
                                                                self.main_lang)
            if not translation:
                self.logger.error("Can't translate %s", str(text))
            elif text:
                # repair formatting
                self.logger.debug("translation: " + pformat(translation))
                # first of all check relative displacement of special symbols after translation
                translation = self.check_symbols_displacement(text, translation)
                self.logger.debug("after symbols displacement: " + pformat(translation))
                self.logger.debug("abbreviations replacements: " + pformat(abbrs_repls))
                self.logger.debug("formatting replacements: " + pformat(format_repls))
                translation = translation.format(*format_repls, **abbrs_repls)
                self.logger.debug("after abbr and format replacement: " + pformat(translation))
                if lang == "UKR":  # replace some special symbols (return back)
                    for expr in brackets_exprs:
                        m = re.search(r"<[%]>", translation)
                        if m:
                            new_expr = self.translate(expr, lang, abbrs, service)
                            new_transl = translation[:m.start() + 1]
                            new_transl += new_expr
                            new_transl += translation[m.end() - 1:]
                            translation = new_transl
                # проверка на большие буквы
                if text[0].upper() == text[0] and translation[0].lower() == translation[0]:
                    translation = translation[0].upper() + translation[1:]
                translation = re.sub(r"°[\s]+C", r"°C", translation)
        except Exception:
            self.logger.debug(format_exc())
            self.logger.debug("Try to just translate without speculations with our format")
            # translate
            translation = self.services[self.service].translate(raw_text, lang,
                                                                self.main_lang)
            if not translation:
                self.logger.error("Can't translate %s", str(text))

        return translation

    def compile(self, progress_callback=None):
        """compile resources with pack2Res2.bat."""
        import os
        import subprocess as sb
        oldDir = os.getcwd()
        try:
            self.mutex.acquire()  # lock
            os.chdir(self.wd)
            cp = sb.run("pack2Res2.bat", capture_output=True, check=True)
            b = cp.stdout
            self.logger.info(f"Compiled with result: {cp.returncode}. Output: {b.decode('utf-8-sig', 'surrogateescape')}")
        except sb.CalledProcessError as e:
            raise
        finally:
            os.chdir(oldDir)
            self.mutex.release()

    def save(self, progress_callback=None):
        """
            Загружаем все из json, переструктурируем и грузим в xml-ini
        :return: None
        """
        try:
            self.mutex.acquire()  # lock cause resources saving
            self.logger.info("Saving %s", str(self.JSON_editor.file))
            json_repr = self.JSON_editor.sections["RESOURCES"]
            xml_repr = self.XML_editor.sections["RESOURCES"]
            if self.abbrs_editor:
                self.abbrs_editor.open()
                self.abbreviations = self.abbrs_editor.sections["abbreviations"]
            _sections = dict()
            progress = 0.0
            len_langs = float(len(self.json_langs))
            len_repr = float(len(json_repr))
            for l in self.json_langs - {self.main_lang}:  # сохраняем все, кроме основного языка
                abbrs = {list(abbr[self.main_lang].keys())[0]: list(abbr[l].keys())[0] for abbr in self.abbreviations if
                         "" not in abbr[l].keys()}
                for obj in json_repr:
                    dObj = json_repr[obj]
                    editor = self._search_ini_file(l, obj, xml_repr)
                    # new XMl sections
                    _lang_section = {l: str(Path("/")) + str(editor.file.relative_to(self.wd))}
                    _sections.setdefault(obj, _lang_section).update(_lang_section)
                    if editor.file.name.endswith("_BinOther.ini") or editor.file.name.endswith("_PanelBin.ini"):
                        if self.XML_editor.add_sections(_sections):
                            self.logger.debug("new XML: %s", str(self.XML_editor.sections))
                            self.XML_editor.save()
                        self.langs.add(l)
                        continue

                    dSections = dict()
                    len_sections = float(len(dObj))
                    for section in dObj:
                        dOptions = dObj[section]
                        dSections[section] = dict()
                        len_options = float(len(dOptions))
                        for option in dOptions:
                            translation = dOptions[option][l]
                            if not translation:
                                marked_translation = ''  # помечаем автоперевод только в JSONe
                                if self.service:  # service translation
                                    translation = self.translate(dOptions[option][self.main_lang], l, abbrs)
                                    marked_translation = self.auto_tr_ch + translation if translation else translation
                                dOptions[option].update({l: marked_translation})
                            elif str(translation).startswith(self.auto_tr_ch):
                                translation = translation[len(self.auto_tr_ch):]
                            dSections[section].update({option: translation})
                            if progress_callback:
                                progress += 1.0 / (len_langs * len_options * len_repr * len_sections)
                                progress_callback.emit(round(100.0 * progress))  # todo: исправить: добавить какую-то обретку
                            self.logger.debug("progress: %s", str(progress))

                    # add new ini sections and remove old sections/options
                    editor.open()
                    removed_sections = []
                    for s in editor.sections:
                        removed_sections.append(s) if s not in dSections else None
                    editor.remove_sections(removed_sections)
                    self.logger.debug(f"removed sections:\n{pformat(removed_sections)}")
                    removed_options = dict()
                    editor.remove_sections([s for s in editor.sections if not dSections.get(s)])
                    for s in editor.sections:
                        for op in editor.sections[s]:
                            if op not in dSections[s]:
                                removed_options[s] = {op: editor.sections[s][op]}
                    editor.remove_options(removed_options)
                    self.logger.debug(f"removed opts:\n{pformat(removed_options)}")
                    editor.update_sections(dSections)
                    editor.save(encoding="utf-8")
                self.langs.add(l)
            if self.XML_editor.add_sections(_sections):
                self.logger.debug("new XML: %s", str(self.XML_editor.sections))
                self.XML_editor.save()
            self.metainfo.update({
                "ResLangs": list(self.langs),
                "Service": self.service
            })
            self.JSON_editor.save(encoding="utf8")
        finally:
            self.mutex.release()

    def _search_ini_file(self, l: str, obj: str, xml_repr: dict) -> IniEditor:
        """ищем ini файл, который указан в xml."""

        if l in self.langs:
            rel_path = Path("." + xml_repr[obj][l]
                            if xml_repr[obj][l].startswith("\\") else xml_repr[obj][l])
            cd = self.wd
            ini_file = cd.joinpath(rel_path).resolve()
            while not ini_file.exists() and str(cd) != cd.anchor:
                cd = cd.parent
                ini_file = cd.joinpath(rel_path).resolve()
                self.logger.debug(f"ini  file: {ini_file}")
            self.logger.debug(f"ini  file: {ini_file}")
            editor = IniEditor(ini_file)
        elif xml_repr[obj][self.main_lang].endswith("_BinOther.ini") or xml_repr[obj][self.main_lang].endswith(
                "_PanelBin.ini"):
            rel_path = Path("." + xml_repr[obj][self.main_lang]
                            if xml_repr[obj][self.main_lang].startswith("\\") else xml_repr[obj][self.main_lang])
            cd = self.wd
            ini_file = cd.joinpath(rel_path).resolve()
            while not ini_file.exists() and str(cd) != cd.anchor:
                cd = cd.parent
                ini_file = cd.joinpath(rel_path).resolve()
            self.logger.debug(f"ini  file: {ini_file}")
            editor = IniEditor(ini_file)
        else:
            rel_path = Path("." + xml_repr[obj][self.main_lang]
                            if xml_repr[obj][self.main_lang].startswith("\\") else xml_repr[obj][self.main_lang])
            cd = self.wd
            ini_file = cd.joinpath(rel_path).resolve()
            while not ini_file.exists() and str(cd) != cd.anchor:
                cd = cd.parent
                ini_file = cd.joinpath(rel_path).resolve()
            self.logger.warning(f"ini file: {ini_file}")
            if ini_file.parent.name.upper() != self.main_lang:
                editor = IniEditor(ini_file.parent.joinpath(obj + l))
            else:
                editor = IniEditor(ini_file.parent.parent.joinpath(Path(l).joinpath(obj + l)))
        return editor

    @lru_cache(maxsize=128)
    def findXML(self, wd):
        self.logger.debug(f"searching res xmls in {str(wd)}..")
        resDir = Path(wd)
        result = []
        for xml_file in resDir.glob("*.xml"):
            json_file = None
            for j in resDir.glob("*.json"):
                json_file = j.name
                if json_file.split(".")[0] != xml_file.name.split(".")[0]:
                    continue
                result.append((xml_file.name, json_file))
                break
            if not json_file:
                try:
                    result.append((xml_file.name, None))
                except ValueError as e:
                    self.logger.exception(e)
                    continue
            self.logger.debug("XML: {}; JSON: {}".format(str(xml_file), str(json_file)))
        return result

    @staticmethod
    def get_langs():
        return ApcCompiler.languages


if __name__ == "__main__":
    import time

    t1 = time.time()
    wd = Path("./test/ResClMain")
    xml_file = "ApcRegResources.xml"
    json_file = "Resources.json"
    compiler = ApcCompiler(Path(xml_file), Path(json_file), wd)
    langs = ApcCompiler.get_langs()
    compiler.update_json({"RUS", "ENU"})
    compiler.save()
    t2 = time.time()
    print(t2 - t1)
