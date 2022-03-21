# ---------------------------------
from PyQt5 import QtGui, QtWidgets
# ---------------------------------
from GUI.UI_properties import Ui_propertiesWidget  # Это наш конвертированный файл дизайна
# ---------------------------------
from ApcLogger import getLogger


class PropertiesWidget(QtWidgets.QWidget, Ui_propertiesWidget):
    """
    #TODO: refactor
    """
    logger = getLogger("PropertiesWidget")

    def __init__(self, compiler=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFont(QtGui.QFont("Segoe UI", 8))
        self.setStyleSheet("""
    QLabel:hover {
    background: palette(dark);
    }
    """)
        if compiler:
            self.set_compiler(compiler)

    def set_compiler(self, compiler):
        self.value_langs.setText(",".join([self.tr(compiler.languages[l].lower()) for l in compiler.json_langs]))
        self.value_service.setText(str(compiler.service).lower())
        self.value_main_lang.setText(self.tr(compiler.languages[compiler.main_lang].lower()))
