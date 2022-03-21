# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './GUI/properties.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets


class Ui_propertiesWidget(object):
    def setupUi(self, propertiesWidget):
        propertiesWidget.setObjectName("propertiesWidget")
        self.propertiesLayout = QtWidgets.QHBoxLayout(propertiesWidget)
        self.propertiesLayout.setObjectName("propertiesLayout")

        self.key_main_lang = QtWidgets.QLabel(propertiesWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.key_main_lang.sizePolicy().hasHeightForWidth())
        self.key_main_lang.setSizePolicy(sizePolicy)
        self.key_main_lang.setWordWrap(True)
        self.key_main_lang.setObjectName("key_main_lang")
        self.key_main_lang.setContentsMargins(0, 0, 1, 0)
        self.propertiesLayout.addWidget(self.key_main_lang)
        self.value_main_lang = QtWidgets.QLabel(propertiesWidget)
        self.value_main_lang.setObjectName("value_main_lang")
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.key_main_lang)
        layout.addWidget(self.value_main_lang)
        # self.propertiesLayout.addWidget(self.value_main_lang)
        self.propertiesLayout.addLayout(layout)
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Plain)
        line.setMidLineWidth(0)
        line.setMaximumHeight(10)
        line.setContentsMargins(0, 0, 0, -1)
        line.setLineWidth(1)
        self.propertiesLayout.addWidget(line)

        self.key_service = QtWidgets.QLabel(propertiesWidget)
        self.key_service.setObjectName("key_service")
        self.key_service.setContentsMargins(0, 0, 1, 0)
        self.propertiesLayout.addWidget(self.key_service)
        self.value_service = QtWidgets.QLabel(propertiesWidget)
        self.value_service.setObjectName("value_service")
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.key_service)
        layout.addWidget(self.value_service)
        self.propertiesLayout.addLayout(layout)
        # self.propertiesLayout.addWidget(self.value_service)
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Plain)
        line.setMidLineWidth(0)
        line.setMaximumHeight(10)
        line.setContentsMargins(0, 0, 0, -1)
        line.setLineWidth(1)
        self.propertiesLayout.addWidget(line)

        self.key_langs = QtWidgets.QLabel(propertiesWidget)
        self.key_langs.setObjectName("key_langs")
        self.key_langs.setContentsMargins(0, 0, 1, 0)
        self.propertiesLayout.addWidget(self.key_langs)
        self.value_langs = QtWidgets.QLabel(propertiesWidget)
        self.value_langs.setObjectName("value_langs")
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.key_langs)
        layout.addWidget(self.value_langs)
        self.propertiesLayout.addLayout(layout)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Plain)
        line.setMidLineWidth(0)
        line.setMaximumHeight(10)
        line.setContentsMargins(0, 0, 0, -1)
        line.setLineWidth(1)
        self.propertiesLayout.addWidget(line)

        self.key_project_files = QtWidgets.QLabel(propertiesWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.key_project_files.sizePolicy().hasHeightForWidth())
        self.key_project_files.setSizePolicy(sizePolicy)
        self.key_project_files.setWordWrap(True)
        self.key_project_files.setObjectName("key_project_files")
        self.key_project_files.setContentsMargins(0, 0, 1, 0)
        self.value_project_files = QtWidgets.QLabel(propertiesWidget)
        self.value_project_files.setObjectName("value_project_files")
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.key_project_files)
        layout.addWidget(self.value_project_files)
        self.propertiesLayout.addLayout(layout)

        self.propertiesLayout.setContentsMargins(4, 2, 4, 2)
        self.propertiesLayout.setSpacing(5)


        self.retranslateUi(propertiesWidget)
        QtCore.QMetaObject.connectSlotsByName(propertiesWidget)

    def retranslateUi(self, propertiesWidget):
        _translate = QtCore.QCoreApplication.translate
        propertiesWidget.setWindowTitle(_translate("propertiesWidget", "Свойства"))
        self.key_service.setText(_translate("propertiesWidget", "Сервис:"))
        self.key_langs.setText(_translate("propertiesWidget", "Языки:"))
        self.key_main_lang.setText(_translate("propertiesWidget", "Основной язык:"))
        self.key_project_files.setText(_translate("propertiesWidget", "Загружено файлов:"))
