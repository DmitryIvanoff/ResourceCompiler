
# ---------------------------------
from PyQt5 import QtWidgets, QtCore
from GUI.UI_HelpWindow import Ui_Help
from ApcLogger import getLogger


class HelpWindow(QtWidgets.QWidget, Ui_Help):
    logger = getLogger("HelpWindow")

    def __init__(self, document: QtCore.QUrl, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.textBrowser.setSource(document)
        self.textBrowser.setOpenExternalLinks(True)
        # self.textBrowser.setSource(QtCore.QUrl("https://docs.python.org/"))
        # self.setSizePolicy(self.textBrowser.sizePolicty())
