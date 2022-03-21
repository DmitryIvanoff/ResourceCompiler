"""Здесь класс, который парсит xml c ресурсами например
"Apacs30/Modules/ApcSysExtensions/ApcZKTecoExt/ResClMain/ApcRegResources.xml" и
сохраняет в виде дерева dictов: 'self.sections["RESOURCES"][Obj][lang]'."""
import sys
import re
from copy import deepcopy

try:
  # Убирать нельзя! Какой-то линтер убрал это вхождение и потом всё развалилось с запросом мол не могу найти 'XMLEditor'
  import lxml.etree as etree

  from ApcEditor import lXMLEditor
except BaseException:
  from xml.dom import Node
  from ApcEditor import XMLEditor

from ApcLogger import getLogger

if 'lxml.etree' in sys.modules:
    class ResXMLEditor(lXMLEditor):
        """
        lxml
        todo: refactoring (rewrite to ApcRegistry)
        """
        logger = getLogger("ResXMLEditor")
        logger.warning("Using lxml!")

        def __init__(self, file):
            super().__init__(file)
            self.resourcesNode = None
            self.objects = None

        def parse_sections(self):
            self.sections = dict()
            self.objects = dict()
            for child in self.root.iter("Key"):
                self.logger.debug(child.get("ID"))
                if child.get("ID"):
                    ID = child.get("ID")
                    P_ID = child.getparent().get("ID") if child.getparent() is not None else None
                    self.logger.debug(ID)
                    m = re.match(r"(?i)^RESOURCES([\\]([\w]+))?$", ID)
                    if m:
                        if not self.sections.get("RESOURCES"):
                            self.sections["RESOURCES"] = dict()
                            self.resourcesNode = child
                        if m.group(2):
                            Obj = m.group(2)
                            self.sections["RESOURCES"][Obj] = dict()
                            self.objects[Obj] = child
                    elif P_ID and P_ID.endswith("RESOURCES"):
                        self.sections["RESOURCES"][ID] = dict()
                        Obj = ID
                        self.objects[Obj] = child
                    elif self.sections.get("RESOURCES") and Obj:
                        KeyValues = child.xpath("./KeyValue[@Name='FileTxt']")
                        if KeyValues:
                            self.logger.debug(KeyValues)
                            self.sections["RESOURCES"][Obj][ID] = KeyValues[0].get("vValue")
                        else:
                            KeyValues = child.xpath("./KeyValue[@Name='FileBinOther']")
                            if KeyValues:
                                self.logger.debug(KeyValues)
                                self.sections["RESOURCES"][Obj][ID] = KeyValues[0].get("vValue")

            return self.sections

        def add_sections(self, sections):
            """
            Пример:
            {'TApcClExtReporter': {'RUS': '\\Rus\\ApcClExtReporterRus.ini', 'ENU': '\\Enu\\ApcClExtReporterEnu.ini'}}
            :param sections:  {section:{option:value}}
            :return:
            """
            self.logger.debug(f"add sections in {str(self.file)})")
            if self.root is None:
                self.open()

            if self.resourcesNode is None:
                self.logger.error("Can't find Resources")
                return
            edited = False
            for obj in sections:
                if obj in self.sections["RESOURCES"]:
                    for lang in sections[obj]:
                        _val = sections[obj][lang]
                        # если нет языка такого, добавляем новый клонированием других
                        if lang not in self.sections["RESOURCES"][obj]:
                            Elem = None
                            for node in self.objects[obj]:  # RUS ENU и тп
                                if Elem is None:  # клонируем первый попавшийся
                                    Elem = deepcopy(node)
                                    break
                            if Elem is not None:
                                Elem.set("ID", lang)
                                KeyValues = Elem.xpath("./KeyValue[@Name='FileTxt']")
                                for KeyValue in KeyValues:
                                    if KeyValue.get("vValue") != _val:
                                        KeyValue.set("vValue", _val)
                                if not KeyValues:
                                    KeyValues = Elem.xpath("./KeyValue[@Name='FileBinOther']")
                                    self.logger.debug(f'{Elem} {KeyValues}')
                                    for KeyValue in KeyValues:
                                        if KeyValue.get("vValue") != _val:
                                            KeyValue.set("vValue", _val)
                                self.sections["RESOURCES"][obj][lang] = _val
                                self.objects[obj].append(Elem)
                                edited = True
                        # если есть, то заменяем старый на новый (меняем аргументы)
                        else:
                            Elem = None
                            for node in self.objects[obj]:  # RUS ENU и тп
                                if node.get("ID") == lang:
                                    Elem = node
                                    break
                            if Elem is not None:
                                KeyValues = Elem.xpath("./KeyValue[@Name='FileTxt']")
                                for KeyValue in KeyValues:
                                    if KeyValue.get("vValue") != _val:
                                        KeyValue.set("vValue", _val)
                                        edited = True
                                if not KeyValues:
                                    KeyValues = Elem.xpath("./KeyValue[@Name='FileBinOther']")
                                    self.logger.debug(f'{Elem} {KeyValues}')
                                    for KeyValue in KeyValues:
                                        if KeyValue.get("vValue") != _val:
                                            KeyValue.set("vValue", _val)
                                            edited = True
                                self.sections["RESOURCES"][obj][lang] = _val
                else:
                    # если такого объекта нет
                    continue
            return edited
else:
    class ResXMLEditor(XMLEditor):
        """xml DOM."""
        logger = getLogger("ResXMLEditor")

        def __init__(self, file):
            super().__init__(file)
            self.objects = None
            self.resourcesNode = None

        def parse_sections(self) -> dict:
            """
            :return: {KeyID: {rus:{},enu:{},...}}
            """
            self.logger.debug(f"parsing {str(self.file)}")
            # ---- parse sections --------
            self.sections = dict()
            self.objects = dict()
            for node in self.root.childNodes:
                if node.nodeType == Node.TEXT_NODE:
                    self.root.removeChild(node)
            Keys = self.root.getElementsByTagName("Key")
            for Key in Keys:
                ID = Key.getAttribute("ID")
                self.logger.debug(f"ID: {ID}")
                # self.logger.debug(f"key {Key.name}, ID: {ID}")
                m = re.search(r"RESOURCES[\\]?([\w]+)?", ID)
                if m:
                    self.sections["RESOURCES"] = dict()
                    self.resourcesNode = Key
                    if m.group(1):
                        self.sections["RESOURCES"][m.group(1)] = {}
                        Obj = m.group(1)
                        self.objects[Obj] = Key
                else:
                    if Key.parentNode.getAttribute("ID").endswith("RESOURCES"):
                        self.sections["RESOURCES"][ID] = {}
                        Obj = ID
                        self.objects[Obj] = Key
                KeyValues = Key.getElementsByTagName("KeyValue")
                for KeyValue in KeyValues:
                    if KeyValue.parentNode == Key:  # Key - RUS,ENU и тп
                        Name = KeyValue.getAttribute("Name")
                        if Name == "FileTxt":
                            vValue = KeyValue.getAttribute("vValue")
                            self.sections["RESOURCES"][Obj][ID] = vValue
                        elif Name == "FileBinOther":
                            vValue = KeyValue.getAttribute("vValue")
                            self.sections["RESOURCES"][Obj][ID] = vValue

            self.logger.debug(f"found res node:\n{self.resourcesNode}")
            self.logger.debug(f"objects:\n{self.objects}")
            self.logger.debug(f"parsed {str(self.file)}")
            return self.sections

        def add_sections(self, sections):
            """
            Пример:
            {'TApcClExtReporter': {'RUS': '\\Rus\\ApcClExtReporterRus.ini', 'ENU': '\\Enu\\ApcClExtReporterEnu.ini'}}
            :param sections:  {section:{option:value}}
            :return:
            """
            self.logger.debug(f"add sections in {str(self.file)})")
            if not self.root:
                self.open()

            if not self.resourcesNode:
                self.logger.error("Can't find Resources")
                return
            for obj in sections:
                if obj in self.sections["RESOURCES"]:
                    for lang in sections[obj]:
                        # если нет языка такого, добавляем новый клонированием других
                        if lang not in self.sections["RESOURCES"][obj]:
                            Elem = None
                            for node in self.objects[obj].childNodes:  # RUS ENU и тп
                                if node.nodeType == Node.ELEMENT_NODE:
                                    if not Elem:  # клонируем первый попавшийся
                                        Elem = node.cloneNode(True)
                                        break
                            if Elem:
                                Elem.setAttribute("ID", lang)
                                KeyValues = Elem.getElementsByTagName("KeyValue")
                                for KeyValue in KeyValues:
                                    Name = KeyValue.getAttribute("Name")
                                    if Name == "FileTxt":
                                        KeyValue.setAttribute("vValue", sections[obj][lang])
                                    elif Name == "FileBinOther":
                                        KeyValue.setAttribute("vValue", sections[obj][lang])
                                self.sections["RESOURCES"][obj][lang] = sections[obj][lang]
                                self.objects[obj].appendChild(Elem)

                        # если есть, то заменяем старый на новый (меняем аргументы)
                        else:
                            Elem = None
                            for node in self.objects[obj].childNodes:  # RUS ENU и тп
                                if node.nodeType == Node.ELEMENT_NODE:
                                    if node.getAttribute("ID") == lang:
                                        Elem = node
                                        break
                            if Elem:
                                KeyValues = Elem.getElementsByTagName("KeyValue")
                                for KeyValue in KeyValues:
                                    Name = KeyValue.getAttribute("Name")
                                    if Name == "FileTxt":
                                        KeyValue.setAttribute("vValue", sections[obj][lang])
                                    elif Name == "FileBinOther":
                                        KeyValue.setAttribute("vValue", sections[obj][lang])
                                self.sections["RESOURCES"][obj][lang] = sections[obj][lang]
                else:
                    # если такого объекта нет
                    continue
