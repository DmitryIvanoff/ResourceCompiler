from pathlib import Path
# ---------------------------------
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFileDialog
# ---------------------------------
from GUI.UI_ImportDialog import Ui_ImportDialog  # Это наш конвертированный файл дизайна
# ---------------------------------
from ApcWorkObj import ApcCompiler
from ApcLogger import getLogger


class Item(QtWidgets.QListWidgetItem):
    def __init__(self, key, value, parent=None):
        super().__init__(value, parent, type=QtWidgets.QListWidgetItem.UserType)
        self._key = key
        self._value = value


class ImportDialog(QtWidgets.QDialog, Ui_ImportDialog):
    """
    #TODO: refactor
    """
    logger = getLogger("ImportDialog")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.langs = dict()
        self.source = None
        self.FromEdit.setPlaceholderText("C:/Apacs30/Modules/ApcClientExtensions/ApcClExtResourceManager/ResClMain")
        self.MainLangComboBox.currentIndexChanged.connect(self._update_main_lang)
        self.SelectButton.pressed.connect(self.on_open_triggered)
        self.main_lang = None
        self.main_langs = dict()
        self.service = None
        self.services = dict()
        self.openDialog = QFileDialog(self)
        self.openDialog.setFileMode(QFileDialog.Directory)
        self.openDialog.setOptions(QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        self.openDialog.setWindowTitle(self.tr("Открыть проект"))

    def set_compiler(self, compiler):
        self.FromEdit.setText(str(compiler.XML_editor.file))

        # setting main_lang
        self.main_langs.clear()
        self.main_lang = None
        self.MainLangComboBox.clear()
        index = -1
        main_lang_index = -1
        for l in compiler.langs:
            index += 1
            self.MainLangComboBox.addItem(compiler.languages[l].lower())
            self.main_langs.update({index: (l, compiler.languages[l].lower())})
            if l == compiler.main_lang:
                self.MainLangComboBox.setCurrentIndex(index)
                self.main_lang = l
                main_lang_index = index
        self.MainLangComboBox.setCurrentIndex(main_lang_index)

        # setting langs
        self.langs = dict()
        self.langsWidget.clear()
        for l in compiler.languages:
            item = Item(l, compiler.languages[l].lower())
            if l in compiler.json_langs:
                item.setCheckState(QtCore.Qt.Checked)
                self.langs.update({l: item})
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
                if l in self.langs:
                    self.langs.pop(l)
            self.langsWidget.addItem(item)
            if self.main_lang == l:
                item.setHidden(True)

        # service set
        self.services.clear()
        self.service = None
        self.AutoTransComboBox.clear()
        index = 0
        self.AutoTransComboBox.addItem("Не выбран")
        self.services.update({index: ("Не выбран", None)})
        serv_index = 0
        for serv in compiler.services:
            if compiler.services[serv]:
                index += 1
                self.AutoTransComboBox.addItem(serv)
                self.services.update({index: (serv, compiler.services[serv])})
                if serv == compiler.service:
                    self.service = serv
                    serv_index = index
        self.AutoTransComboBox.setCurrentIndex(serv_index)

    def accept(self) -> None:
        self._update_fields()
        if not self.langs:
            QtWidgets.QMessageBox.warning(self, self.tr("Внимание!"), "Выберите языки", QtWidgets.QMessageBox.Close)
            return
        return super().accept()

    def setup(self, From, langs: list = None, main_lang=None, service=None):
        try:
            self.FromEdit.setText(str(From))

            self.main_langs.clear()
            self.main_lang = None
            self.MainLangComboBox.clear()
            index = -1
            main_lang_index = -1
            for l in ApcCompiler.languages:
                index += 1
                self.MainLangComboBox.addItem(self.tr(ApcCompiler.languages[l].lower()))
                self.main_langs.update({index: (l, self.tr(ApcCompiler.languages[l].lower()))})
                if l == main_lang:
                    self.MainLangComboBox.setCurrentIndex(index)
                    self.main_lang = l
                    main_lang_index = index
                self.MainLangComboBox.setCurrentIndex(main_lang_index)

            if not langs:
                langs = []
            self.langs = dict()
            self.langsWidget.clear()
            for l in ApcCompiler.languages:
                item = Item(l, ApcCompiler.languages[l].lower())
                if l in langs:
                    item.setCheckState(QtCore.Qt.Checked)
                    self.langs.update({l: item})
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                    if l in self.langs:
                        self.langs.pop(l)
                self.langsWidget.addItem(item)
                if self.main_lang == l:
                    item.setHidden(True)

            self.services.clear()
            self.service = None
            self.AutoTransComboBox.clear()
            index = 0
            self.AutoTransComboBox.addItem("Не выбран")
            self.services.update({index: ("Не выбран", None)})
            serv_index = 0
            for serv in ApcCompiler.services:
                if ApcCompiler.services[serv]:
                    index += 1
                    self.AutoTransComboBox.addItem(serv)
                    self.services.update({index: (serv, ApcCompiler.services[serv])})
                    if serv == service:
                        self.service = serv
                        serv_index = index
            self.AutoTransComboBox.setCurrentIndex(serv_index)
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))

    @pyqtSlot(int, name="_update_service")
    def _update_service(self, index: int):
        if index == -1:
            self.service = None
            return
        if self.services:
            service = self.services[index]
            self.service = service[0]
            if self.service == "Не выбран" or not self.service:
                self.service = None

    @pyqtSlot(int, name="_update_main_lang")
    def _update_main_lang(self, index: int):
        try:
            self.logger.debug("main_lang changed")
            if index == -1:
                self.main_lang = None
                return
            if self.main_langs:
                main_lang = self.main_langs[index]
                self.main_lang = main_lang[0]
                self.logger.debug(self.langsWidget.count())
                for r in range(self.langsWidget.count()):
                    item = self.langsWidget.item(r)
                    if item._key == self.main_lang:
                        item.setHidden(True)
                    else:
                        item.setHidden(False)
                self.logger.debug("Langs: " + str(self.langs))
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))

    @pyqtSlot(name="_update_fields")
    def _update_fields(self):
        try:
            self._update_service(self.AutoTransComboBox.currentIndex())
            self._update_main_lang(self.MainLangComboBox.currentIndex())
            self._update_from()
            self._update_langs()

        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))

    @pyqtSlot(name="_update_from")
    def _update_from(self):
        try:
            self.source = Path(self.FromEdit.text().strip(" \n"))
            self.logger.debug("From: " + str(self.source))
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))

    @pyqtSlot(name="_update_langs")
    def _update_langs(self):
        try:
            for r in range(self.langsWidget.count()):
                item = self.langsWidget.item(r)
                if item.checkState() == QtCore.Qt.Checked:
                    self.langs.update({item._key: item._value})
                else:
                    if item._key in self.langs:
                        self.langs.pop(item._key)
            self.logger.debug("Langs: " + str(self.langs))
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))

    @pyqtSlot(name='on_open_triggered')
    def on_open_triggered(self):
        try:
            self.logger.debug("Working directory: %s", str(self.source))
            # self.openDialog.setDirectory(self.source)
            # nResult = self.openDialog.exec()
            # if nResult:
            curdir = QFileDialog.getExistingDirectory(
                self,
                self.tr("Open resources directory"),
                str(self.source),
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            if curdir:
                self.source = Path(curdir)
                self.FromEdit.setText(str(curdir))
            self.logger.info("Working directory: %s", str(self.source))

        except Exception as e:
            self.logger.exception(e)
