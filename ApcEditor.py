import locale
import os
import sys
from pathlib import Path
from stat import S_IWRITE, S_IREAD
from io import StringIO
import chardet

# for ini
from configparser import ConfigParser, ExtendedInterpolation

try:
    import configobj
except BaseException:
    pass

# for xml
import xml.dom
from xml.dom.minidom import parse, parseString

try:
    import lxml.etree as etree
except BaseException:
    pass

# for json
try:
    import ujson as ujson
except BaseException:
    import json as ujson

# our modules
from ApcLogger import getLogger


# ------------------------------------------------------------------------------

class Editor:
    """read full file content in string which is not so good in case big
    files."""
    encodings = [
        "utf-8",
        locale.getpreferredencoding(),
        "utf-8-sig",
        "cp1251",
        "cp1252",
        "utf16",
        "latin",
    ]
    logger = getLogger("Editor")

    def __init__(self, file, *args, **kwargs):
        self.file = Path(file)
        self.text = None
        self.encoding = None
        self._edited = False

    def __str__(self):
        return f"Filename:" \
               f"{str(self.file)}\n" \
               f"Encoding:" \
               f"{self.encoding}\n" \
               f"Содержимое:" \
               f"{self.text}\n"

    def open(self, *args, **kwargs):
        self.logger.info("opening %s", str(self.file))
        if not Path(self.file).exists():
            self.text = ""
            self.encoding = kwargs.get("encoding")
            return
        self.file.chmod(S_IWRITE | S_IREAD)
        if not self._open_in_encoding(encoding=kwargs.get("encoding")):
            self.logger.error(f"Can't open {str(self.file)}")
            raise RuntimeError(f"Can't open {str(self.file)}")

    def _open_in_encoding(self, encoding: str = None) -> bool:
        """try to detect encoding if it is not given with module 'chardet' Unless
        latest set try to it determine manually."""
        opened = False
        with self.file.open("rb") as fb:
            b = fb.read()
            self.logger.debug(b)
            self.encoding = encoding
            if self.encoding:  # if encoding set
                self.text = b.decode(encoding=self.encoding)
                opened = True
            elif "chardet" in sys.modules:  # detect encoding
                detected = chardet.detect(b)
                self.logger.debug(detected)
                self.encoding = detected["encoding"]
                self.text = b.decode(encoding=self.encoding)
                opened = True
            else:  # if 'chardet' not installed then detect encoding manually
                for encoding in self.encodings:
                    try:
                        self.text = b.decode(encoding=encoding)
                    except UnicodeDecodeError as e:
                        continue
                    self.encoding = encoding
                    opened = True
                    break
        return opened

    def edit(self, text: str):
        self.text = text
        self._edited = True

    def save(self, *args, **kwargs):
        self.logger.info("saving %s", str(self.file))
        if self.file.exists():
            self.file.chmod(S_IWRITE)
        else:
            if not self.file.parent.exists():
                os.makedirs(self.file.parent)
        with self.file.open(mode="w", encoding=kwargs.get("encoding", self.encoding)) as f:
            f.write(self.text)
        self._edited = False


# ------------------------------------------------------------------------------

class IniEditor(Editor):
    encodings = [
        "utf-8-sig",
        locale.getpreferredencoding(),
        "cp1251",
        "cp1252",
        "utf16",
        "latin",
    ]
    logger = getLogger("IniEditor")

    def __init__(self, file):
        file = Path(file)
        if not file.suffix or file.suffix != ".ini":
            file = file.parent.joinpath(file.name.split(".")[0] + ".ini")
        super().__init__(file)
        if "configobj" not in sys.modules:
            self.ini_file = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
            self.ini_file.optionxform = lambda option: str(option)
        else:
            self.ini_file = None
        self.sections = dict()

    def open(self, *args, **kwargs):
        self.logger.debug("open %s", str(self.file))
        if not Path(self.file).exists():
            self.text = ""
            self.encoding = locale.getpreferredencoding()
            return
        if not self._open_in_encoding(encoding=kwargs.get("encoding")):
            self.logger.error(f"Can't open {str(self.file)}")
            raise RuntimeError(f"Can't open {str(self.file)}")
        if "configobj" in sys.modules:
            # with self.file.open(mode="w", encoding=self.encoding, newline="\n") as configfile:
            #  configfile.write(re.sub(";", "#", s))
            self.ini_file = configobj.ConfigObj(
                StringIO(self.text.replace(";", "#")),
                raise_errors=True,
                file_error=True,
                list_values=False)
            self.logger.debug(self.ini_file)
            self.sections = self.ini_file.dict()
        else:
            self.ini_file.read_string(self.text)
            sections = self.ini_file
            self.sections = {k: {o: sections[k][o] for o in sections[k]} for k in sections}
            self.sections.pop("DEFAULT")

    def __str__(self):
        return f"{super().__str__()}" \
               f"Sections:" \
               f"{str(self.sections)}"

    def set(self, section: str, option: str, value):
        if "configobj" not in sys.modules:
            if self.ini_file.get(section, option) != value:
                self.ini_file.set(section, option, value)
                self.sections.setdefault(section, dict())[option] = value
                self._edited = True
        else:
            raise NotImplementedError

    def get(self, section: str, option: str):
        if "configobj" not in sys.modules:
            return self.ini_file.get(section, option)
        else:
            raise NotImplementedError

    def edit(self, d: dict):
        if "configobj" not in sys.modules:
            self.ini_file.read_dict(d)
        else:
            self.ini_file.clear()
            self.ini_file.update(d)
        self._edited = True

    def update_sections(self, sections):
        """
        :param sections: {section:{option:value}}
        :return:
        """
        _edited = False
        if "configobj" not in sys.modules:
            for section in sections:
                if section in self.ini_file:
                    for option in sections[section]:
                        _val = sections[section][option]
                        if option not in self.sections[section]:
                            self.ini_file.set(section, option, _val)
                            self.sections[section][option] = _val
                            _edited = True
                        elif self.ini_file.get(section, option) != _val:
                            self.ini_file.set(section, option, _val)
                            self.sections[section][option] = _val
                            _edited = True
                else:
                    self.ini_file.add_section(section)
                    self.sections[section] = dict()
                    for option in sections[section]:
                        _val = sections[section][option]
                        self.ini_file.set(section, option, _val)
                        self.sections[section][option] = _val
                        _edited = True
        else:
            for section in sections:
                if not self.ini_file.get(section):
                    self.ini_file[section] = {}
                    self.sections[section] = dict()
                    _edited = True
                for option in sections[section]:
                    _val = sections[section][option]
                    if self.ini_file[section].get(option) != _val:
                        self.ini_file[section][option] = _val
                        self.sections[section][option] = _val
                        _edited = True
                self.ini_file.comments[section] = ["\n"]
        self._edited = _edited if _edited else self._edited
        return _edited

    def remove_sections(self, sections):
        """
        :param sections: []
        :return:
        """
        if "configobj" not in sys.modules:
            if not sections:
                self._edited = False
                return
            for section in sections:
                self.ini_file.remove_section(section)
                self.sections.pop(section)
        else:
            if not sections:
                self._edited = False
                return
            for section in sections:
                self.ini_file.pop(section)
                self.sections.pop(section)
        self._edited = True

    def remove_options(self, sections):
        """
        :param sections: {"section1": ["option1",..],..}
        :return:
        """
        _edited = False
        if "configobj" not in sys.modules:
            for section in sections:
                for option in sections[section]:
                    existed = self.ini_file.remove_option(section, option)
                    if existed:
                        _edited = True
                    self.sections[section].pop(option)
        else:
            for section in sections:
                if not self.ini_file.get(section):
                    continue
                for option in sections[section]:
                    if option in self.ini_file[section]:
                        self.ini_file[section].pop(option)
                        self.sections[section].pop(option)
                        _edited = True
        self._edited = _edited if _edited else self._edited

    def save(self, *args, **kwargs):
        """
        :return: None
        """
        self.logger.debug("saving %s", str(self.file))

        if self.file.exists():
            if not self._edited:
                self.logger.debug("%s wasn't edited!", str(self.file))
                return
            self.file.chmod(S_IWRITE)
        else:
            if not self.file.parent.exists():
                os.makedirs(self.file.parent)
        # write self.sections to self.file
        if "configobj" not in sys.modules:
            with self.file.open(mode="w", encoding=kwargs.get("encoding", self.encoding)) as configfile:
                configfile.write(f";DONT REMOVE THIS COMMENT - this line is a workaround for "
                                 f"GetPrivateProfileStringA() and UTF-8-BOM encoding\n")
                self.ini_file.write(configfile, space_around_delimiters=False)
        else:
            self.ini_file.filename = None  # чтобы метод write вернул список байт-строк
            with self.file.open(mode="wb") as configfile:
                outstr = "\n".join(self.ini_file.write())
                self.logger.debug(outstr.replace("#", ";"))
                outstr = outstr.replace("#", ";").replace(" = ", "=")
                if not outstr.startswith(";DONT REMOVE THIS COMMENT"):
                    outstr = (f";DONT REMOVE THIS COMMENT - this line is a workaround for "
                              f"GetPrivateProfileStringA() and UTF-8-BOM encoding\n{outstr}")
                configfile.write(outstr.encode(kwargs.get("encoding", "utf-8")))
        self._edited = False

# ------------------------------------------------------------------------------


class XMLEditor(Editor):
    """
    todo: define that class as abstract
    суть - читаем в xml
    меняем Inifiles_map
    пишем Inifiles_map в файл
    """
    domimp = xml.dom.minidom.getDOMImplementation()

    logger = getLogger("XMLEditor")

    def __init__(self, file):
        self.logger.debug(f"constructing XMLEditor({str(file)})")
        file = Path(file)
        if not file.suffix or file.suffix != ".xml":
            file = file.parent.joinpath(file.name.split(".")[0] + ".xml")
        super().__init__(file)

        self.document = self.domimp.createDocument("", "Registry", "")
        self.sections = None
        self.root = None

    def edit(self, text: str):
        if not self.document:
            return
        self.document.documentElement.appendChild(parseString(text).documentElement)

    def __str__(self):
        return f"{super().__str__()}" \
               f"Sections:" \
               f"{str(self.sections)}\n"

    def open(self) -> dict:
        """

        :return: {KeyID: {rus:{},enu:{},...}}
        """
        self.logger.info("opening %s", str(self.file))
        if not Path(self.file).exists():
            self.text = ""
            self.encoding = locale.getpreferredencoding()
            return dict()
        try:
            doc = parse(str(self.file))
        except Exception as e:
            self.logger.exception(e)
            return dict()
        self.document = doc
        self.encoding = doc.encoding
        self.root = self.document.documentElement
        self.text = self.document.toxml(self.encoding)

    def parse_sections(self):
        raise NotImplementedError

    def add_sections(self, sections):
        """
        Пример:
        {'TApcClExtReporter': {'RUS': '\\Rus\\ApcClExtReporterRus.ini', 'ENU': '\\Enu\\ApcClExtReporterEnu.ini'}}
        :param sections:  {section:{option:value}}
        :return:
        """
        raise NotImplementedError

    def save(self):
        """

        :return:
        """
        self.logger.debug("saving %s", str(self.file))
        if self.file.exists():
            self.file.chmod(S_IWRITE)
        else:
            if not self.file.parent.exists():
                os.makedirs(self.file.parent)
        with self.file.open(mode="w", encoding=self.encoding) as f:
            self.document.writexml(f, encoding=self.encoding, addindent="  ", newl="\n")


# ------------------------------------------------------------------------------
class lXMLEditor(Editor):
    """# todo: define that class as abstract using lxml lib"""
    logger = getLogger("lXMLEditor")

    def __init__(self, file):
        file = Path(file)
        super().__init__(file)

        self.document = None
        self.sections = None
        self.root = None

    def edit(self, text: str):
        if not self.document:
            return

    def __str__(self):
        return f"{super().__str__()}" \
               f"Sections:" \
               f"{str(self.sections)}\n"

    def parse_sections(self):
        raise NotImplementedError

    def add_sections(self, sections: dict):
        """
        Пример:
        {'TApcClExtReporter': {'RUS': '\\Rus\\ApcClExtReporterRus.ini', 'ENU': '\\Enu\\ApcClExtReporterEnu.ini'}}
        :param sections:  {section:{option:value}}
        :return:
        """
        raise NotImplementedError

    def open(self):
        """

        :return: {KeyID: {rus:{},enu:{},...}}
        """
        super().open()
        self.document = etree.parse(str(self.file))  # etree.XML(str(self.text).encode(encoding="utf-8"))
        self.root = self.document.getroot()
        self.encoding = self.document.docinfo.encoding

    def save(self):
        """

        :return:
        """
        self.text = etree.tostring(
            self.document, encoding=self.encoding, xml_declaration=True, method='xml',
            pretty_print=True, standalone=self.document.docinfo.standalone).decode(self.encoding)
        super(lXMLEditor, self).save()
        # self.document.write(str(self.file), encoding=self.encoding, xml_declaration=True, method='xml',
        #                     pretty_print=True, standalone=self.document.docinfo.standalone)


# ---------------------------------------------------------------------

class JSONEditor(Editor):
    """"""
    encodings = [
        "utf-8-sig",
        "utf-8",
    ]
    logger = getLogger("JSONEditor")

    def __init__(self, file):
        self.logger.debug(f"constructing JSONEditor({str(file)})")
        file = Path(file)
        if not file.suffix or file.suffix != ".json":
            file = file.parent.joinpath(file.name.split(".")[0] + ".json")
        super().__init__(file)
        self.sections = None

    def open(self):
        """
        :return: {KeyID: {rus:{},enu:{},...}}
        """
        super().open()
        if not self.encoding:
            self.encoding = "utf-8"
        if self.text:
            self.sections = ujson.loads(self.text)
        else:
            self.sections = dict()

    def edit(self, text):
        self.text = text
        self.sections = ujson.loads(self.text)

    def __str__(self):
        return f"{super().__str__()}" \
               f"Sections:" \
               f"{str(self.sections)}\n"

    def update_sections(self, sections):
        """

        :param sections: {RESOURCES: {section:{option:{rus:'sdfsd',enu:'sdfsd'}}}}
        :return:
        """
        self.logger.debug(f"updating sections in {str(self.file)}")
        if not self.sections:
            self.sections = dict()
            self.sections.update(sections)
        else:
            self.sections.update(sections)

    def update_options(self, section, options):
        """

        :param section:
        :param options: {option:{rus:'sdfsd',enu:'sdfsd'}}
        :return:
        """
        self.logger.debug(f"updating options in {str(self.file)}")
        if self.sections:
            self.sections.setdefault("RESOURCES", dict())
        else:
            self.sections = {"RESOURCES": {section: dict()}}
        for option in options:
            self.sections["RESOURCES"][section][option] = options[option]

    def save(self, *args, **kwargs):
        """

        :return:
        """
        self.logger.debug("saving %s", str(self.file))
        if self.sections:
            if kwargs.get("encoding"):
                self.encoding = kwargs.get("encoding")
            if self.file.exists():
                self.file.chmod(S_IWRITE)
            else:
                if not self.file.parent.exists():
                    os.makedirs(self.file.parent)
            with self.file.open(mode="w", encoding=self.encoding) as f:
                if ujson.__name__ == "ujson":
                    ujson.dump(self.sections, f, indent=2, ensure_ascii=False, escape_forward_slashes=False)
                else:
                    ujson.dump(self.sections, f, indent=2, ensure_ascii=False)


class MetainfoEditor(JSONEditor):
    def __init__(self, file="MetaInfo"):
        file = Path(file)
        super(JSONEditor, self).__init__(file)
        self.sections = dict()

    def update_options(self, section, options):
        pass

    def update_sections(self, sections: dict):
        self.sections.update(sections)


if __name__ == "__main__":
    editor = JSONEditor("lol.json")
    editor.open()
    print(editor.sections)
    editor.save()
