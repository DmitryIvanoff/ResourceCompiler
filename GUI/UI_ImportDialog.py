# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './GUI/ImportDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ImportDialog(object):
    def setupUi(self, ImportDialog):
        ImportDialog.setObjectName("ImportDialog")
        ImportDialog.resize(405, 359)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        ImportDialog.setFont(font)
        ImportDialog.setSizeGripEnabled(False)
        ImportDialog.setModal(True)
        self.formLayout = QtWidgets.QFormLayout(ImportDialog)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.WrapLongRows)
        self.formLayout.setObjectName("formLayout")
        self.Folder_label = QtWidgets.QLabel(ImportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.Folder_label.sizePolicy().hasHeightForWidth())
        self.Folder_label.setSizePolicy(sizePolicy)
        self.Folder_label.setWordWrap(True)
        self.Folder_label.setObjectName("Folder_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.Folder_label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.FromEdit = QtWidgets.QLineEdit(ImportDialog)
        self.FromEdit.setInputMask("")
        self.FromEdit.setObjectName("FromEdit")
        self.horizontalLayout.addWidget(self.FromEdit)
        self.SelectButton = QtWidgets.QPushButton(ImportDialog)
        self.SelectButton.setObjectName("SelectButton")
        self.horizontalLayout.addWidget(self.SelectButton)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.MainLang_label = QtWidgets.QLabel(ImportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MainLang_label.sizePolicy().hasHeightForWidth())
        self.MainLang_label.setSizePolicy(sizePolicy)
        self.MainLang_label.setScaledContents(False)
        self.MainLang_label.setWordWrap(True)
        self.MainLang_label.setObjectName("MainLang_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.MainLang_label)
        self.MainLangComboBox = QtWidgets.QComboBox(ImportDialog)
        self.MainLangComboBox.setObjectName("MainLangComboBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.MainLangComboBox)
        self.Langs_label = QtWidgets.QLabel(ImportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.Langs_label.sizePolicy().hasHeightForWidth())
        self.Langs_label.setSizePolicy(sizePolicy)
        self.Langs_label.setWordWrap(True)
        self.Langs_label.setObjectName("Langs_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.Langs_label)
        self.langsWidget = QtWidgets.QListWidget(ImportDialog)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(9)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.langsWidget.setFont(font)
        self.langsWidget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.langsWidget.setObjectName("langsWidget")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.langsWidget)
        self.AutoTrans_label = QtWidgets.QLabel(ImportDialog)
        self.AutoTrans_label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.AutoTrans_label.setWordWrap(True)
        self.AutoTrans_label.setObjectName("AutoTrans_label")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.AutoTrans_label)
        self.AutoTransComboBox = QtWidgets.QComboBox(ImportDialog)
        self.AutoTransComboBox.setObjectName("AutoTransComboBox")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.AutoTransComboBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(ImportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(ImportDialog)
        self.buttonBox.accepted.connect(ImportDialog.accept)
        self.buttonBox.rejected.connect(ImportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportDialog)

    def retranslateUi(self, ImportDialog):
        _translate = QtCore.QCoreApplication.translate
        ImportDialog.setWindowTitle(_translate("ImportDialog", "???????????? ????????????"))
        self.Folder_label.setText(_translate("ImportDialog", "????????????:"))
        self.FromEdit.setPlaceholderText(_translate("ImportDialog", "./test/ResClMain"))
        self.SelectButton.setText(_translate("ImportDialog", "??????????????..."))
        self.MainLang_label.setText(_translate("ImportDialog", "???????????????? ????????:"))
        self.Langs_label.setText(_translate("ImportDialog", "??????????:"))
        self.AutoTrans_label.setText(_translate("ImportDialog", "????????????:"))
