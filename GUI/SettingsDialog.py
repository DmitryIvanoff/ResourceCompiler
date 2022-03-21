# ---------------------------------
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal
# ---------------------------------
from GUI.UI_SettingsDialog import Ui_SettingsDialog  # Это наш конвертированный файл дизайна
from GUI.UI_TokenWidget import Ui_Form  # Это наш конвертированный файл дизайна
# ---------------------------------
from ApcWorkObj import ApcCompiler
from ApcLogger import getLogger


class Item(QtWidgets.QListWidgetItem):
    def __init__(self, key, value, parent=None):
        super().__init__(value, parent, type=QtWidgets.QListWidgetItem.UserType)
        self._key = key
        self._value = value


class Settings(QtCore.QObject):
    logger = getLogger("Settings")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QtCore.QSettings("AAMSystems", "ApcResTranslator", self)

    @pyqtSlot(name="resetMain")
    def resetMain(self):
        self.settings.beginGroup("Main_settings")
        self.settings.remove("")
        self.settings.endGroup()

    @pyqtSlot(name="resetTokens")
    def resetTokens(self):
        self.settings.beginGroup("Tokens")
        self.settings.remove("")
        self.settings.endGroup()

    @pyqtSlot(name="resetAll")
    def resetAll(self):
        self.settings.clear()

    def get_settings(self) -> dict:
        # todo: кешируются ли настройки? (чтобы не бегать в реестр)
        _settings = dict()
        self.settings.beginGroup("Main_settings")
        _settings["main_lang"] = self.settings.value("main_language", ApcCompiler.default_lang, type=str)
        _settings["langs"] = self.settings.value("languages", list(ApcCompiler.languages.keys()), type=list)
        _settings["service"] = self.settings.value("service", "", type=str)
        self.settings.endGroup()
        self.settings.beginGroup("Tokens")
        tokens = {
            serv: self.settings.value(serv, "", str) for serv in ApcCompiler.services
            if ApcCompiler.services[serv] and (ApcCompiler.services[serv].get_token() is not None)
        }
        for serv in tokens:
            try:
                ApcCompiler.services[serv].set_token(tokens[serv])
            except FileNotFoundError as e:
                self.logger.exception(e)
                if isinstance(self.parent, QtWidgets.QWidget):
                    QtWidgets.QMessageBox.warning(self.parent, self.tr("Ошибка"), f'Не получилось загрузить token: {e.filename}', QtWidgets.QMessageBox.Ok)
        self.settings.endGroup()
        _settings["tokens"] = tokens
        self.logger.debug(_settings)
        return _settings

    def set_settings(self, settings: dict):
        self.settings.beginGroup("Main_settings")
        self.settings.setValue("main_language", settings["main_lang"])
        self.settings.setValue("languages", settings["langs"])
        self.settings.setValue("service", settings["service"])
        self.settings.endGroup()
        self.settings.beginGroup("Tokens")
        tokens = settings["tokens"]
        for serv in tokens:
            if ApcCompiler.services[serv]:
                try:
                    token = ApcCompiler.services[serv].get_token()
                    if token is not None:
                        ApcCompiler.services[serv].set_token(tokens[serv])
                        self.settings.setValue(serv, tokens[serv])
                except Exception as e:
                    self.logger.error(
                        f"Не получилось установить api-ключ!"
                        f"{str(ApcCompiler.services[serv])}: {tokens[serv]}"
                    )
                    raise
        self.settings.endGroup()
        self.logger.debug("Set main_lang: %s", settings["main_lang"])
        self.logger.debug("Set langs: %s", settings["langs"])
        self.logger.debug("Set service: %s", settings["service"])


class TokenWidget(QtWidgets.QWidget, Ui_Form):
    logger = getLogger("TokenWidget")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.KeyLabel.setFont(font)
        self.KeyLabel.setWordWrap(True)
        self.KeyField.setPlaceholderText("Введите ваш API-ключ")
        self.KeyField.setWhatsThis("API-ключ. Для каждого сервиса API-ключ задается по-разному"
                                   "При установке ключа посмотрите инструкцию.")
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(9)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.KeyField.setFont(font)

    def setToken(self, token: str):
        self.KeyField.setPlainText(token)

    def getToken(self):
        return self.KeyField.toPlainText()

    def reset(self):
        self.KeyField.clear()


class SettingsDialog(QtWidgets.QDialog, Ui_SettingsDialog):
    """"""
    logger = getLogger("SettingsDialog")
    resetMain = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.langs = dict()
        self.MainLangsComboBox.currentIndexChanged.connect(self._update_main_lang)
        self.ServicesComboBox.currentIndexChanged.connect(self._update_service)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Reset).clicked.connect(self.reset)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.accept)
        self.gridLayout.removeWidget(self.buttonBox)
        self.TokenWidget = TokenWidget(self)
        self.gridLayout.addWidget(self.TokenWidget, 3, 0, 1, 2)
        self.TokenWidget.setHidden(True)
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.main_lang = None
        self.main_langs = dict()
        self.service = None
        self.services = dict()  # everything in ServicesComboBox
        self.setWhatsThis(
            "Окошко настроек."
        )
        self.tokens = dict()

    def set_settings(self, settings: dict):
        main_lang = settings["main_lang"]
        #  main_lang setup
        self.main_langs.clear()
        self.main_lang = None
        self.MainLangsComboBox.clear()
        index = -1
        main_lang_index = -1
        for l in ApcCompiler.languages:
            index += 1
            self.MainLangsComboBox.addItem(ApcCompiler.languages[l].lower())
            self.main_langs.update({index: (l, ApcCompiler.languages[l].lower())})
            if l == main_lang:
                self.MainLangsComboBox.setCurrentIndex(index)
                self.main_lang = l
                main_lang_index = index
        self.MainLangsComboBox.setCurrentIndex(main_lang_index)

        # langs setup
        langs = settings["langs"]
        self.langs = dict()
        self.langsWidget.clear()
        for l in ApcCompiler.languages:
            # if l==self.main_lang:
            #   continue
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

        # service setup
        service = settings["service"]
        self.services.clear()
        self.service = None
        self.ServicesComboBox.clear()
        index = 0
        self.ServicesComboBox.addItem("Не выбран")
        self.services.update({index: ("Не выбран", None)})
        serv_index = 0
        for serv in ApcCompiler.services:
            if ApcCompiler.services[serv]:
                index += 1
                self.ServicesComboBox.addItem(serv)
                self.services.update({index: (serv, ApcCompiler.services[serv])})
                if serv == service:
                    self.service = serv
                    serv_index = index
        self.ServicesComboBox.setCurrentIndex(serv_index)

        # token setup
        self.tokens = settings["tokens"]
        if self.service:
            token = ApcCompiler.services[self.service].get_token()
            if token is not None:
                self.logger.debug("Token: " + str(token))
                self.TokenWidget.setToken(token)
                self.tokens.update({self.service: token})
            else:
                self.TokenWidget.reset()
                self.TokenWidget.setVisible(False)
        else:
            self.TokenWidget.reset()
            self.TokenWidget.setVisible(False)

    def accept(self) -> None:
        nResult = self._update_fields()
        if nResult:
            return
        else:
            return super().accept()

    def reset(self):
        """reset."""
        try:
            # langs reset
            self.langs = dict()
            self.langsWidget.clear()
            for l in ApcCompiler.languages:
                item = Item(l, ApcCompiler.languages[l].lower())
                item.setCheckState(QtCore.Qt.Unchecked)
                self.langsWidget.addItem(item)
                if self.main_lang == l:
                    item.setHidden(True)
            # main_lang reset
            self.main_langs.clear()
            self.main_lang = None
            self.MainLangsComboBox.clear()

            index = -1
            for l in ApcCompiler.languages:
                index += 1
                self.MainLangsComboBox.addItem(self.tr(ApcCompiler.languages[l].lower()))
                self.main_langs.update({index: (l, self.tr(ApcCompiler.languages[l].lower()))})
            self.MainLangsComboBox.setCurrentIndex(-1)
            # service reset
            self.services.clear()
            self.service = None
            self.ServicesComboBox.clear()

            index = 0
            self.ServicesComboBox.addItem("Не выбран")
            self.services.update({index: ("Не выбран", None)})
            serv_index = 0
            for serv in ApcCompiler.services:
                if ApcCompiler.services[serv]:
                    index += 1
                    self.ServicesComboBox.addItem(serv)
                    self.services.update({index: (serv, ApcCompiler.services[serv])})
            self.ServicesComboBox.setCurrentIndex(serv_index)
            # tokenwidget reset
            self.tokens = dict()
            self.TokenWidget.reset()
            self.TokenWidget.setVisible(False)
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))

    @pyqtSlot(int, name="_update_service")
    def _update_service(self, index: int):
        try:
            if index == -1:
                self.service = None
                return 0
            if self.services:
                service = self.services[index]
                self.service = service[0]
                if self.service == "Не выбран" or not self.service:
                    self.service = None
                    self.logger.debug(f"Service:{self.service}")
                    self.TokenWidget.reset()
                    self.TokenWidget.setVisible(False)
                    return 0
                token = ApcCompiler.services[self.service].get_token()
                if token is not None:
                    self.logger.debug(f"Token:{token}")
                    self.TokenWidget.setToken(token)
                    self.TokenWidget.setVisible(True)
                else:
                    self.logger.debug(f"reset")
                    self.TokenWidget.reset()
                    self.TokenWidget.setVisible(False)
                return 0

        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))
            return -1
        return 0

    @pyqtSlot(int, name="_update_main_lang")
    def _update_main_lang(self, index: int):
        try:
            if index == -1:
                self.main_lang = None
                return 0
            if self.main_langs:
                main_lang = self.main_langs[index]
                self.main_lang = main_lang[0]
                for r in range(self.langsWidget.count()):
                    item = self.langsWidget.item(r)
                    if item._key == self.main_lang:
                        item.setHidden(True)
                        item.setCheckState(QtCore.Qt.Checked)
                    else:
                        item.setHidden(False)
                self.logger.debug("Langs: " + str(self.langs))
                return 0
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))
            return -1

    @pyqtSlot(name="_update_fields")
    def _update_fields(self):
        try:
            nResult = self._update_langs()
            if nResult:
                return -1
            nResult = self._update_token(self.TokenWidget.getToken())
            if nResult:
                return -1
            return 0
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))
            return -1

    @pyqtSlot(str, name="_update_token")
    def _update_token(self, value):
        try:
            if self.service:
                token = ApcCompiler.services[self.service].get_token()
                if token is not None:
                    self.logger.info("Token: " + str(ApcCompiler.services[self.service].get_token()))
                    self.logger.info("Service: %s", self.service)
                    if not value:
                        QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Нужно ввести ключ!"))
                        return -1
                    self.tokens.update({self.service: value})

        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.warning(self, self.tr("Ошибка"), str(e))
            return -1
        return 0

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
        return 0
