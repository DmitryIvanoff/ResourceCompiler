# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './GUI/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(962, 634)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(9)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.browser = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.browser.sizePolicy().hasHeightForWidth())
        self.browser.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.browser.setFont(font)
        self.browser.setStyleSheet("font: Consolas")
        self.browser.setElideMode(QtCore.Qt.ElideLeft)
        self.browser.setDocumentMode(True)
        self.browser.setTabsClosable(True)
        self.browser.setObjectName("browser")
        self.horizontalLayout_2.addWidget(self.browser)
        self.treeLayout = QtWidgets.QHBoxLayout()
        self.treeLayout.setSpacing(1)
        self.treeLayout.setObjectName("treeLayout")
        self.treeButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeButton.sizePolicy().hasHeightForWidth())
        self.treeButton.setSizePolicy(sizePolicy)
        self.treeButton.setMaximumSize(QtCore.QSize(8, 16777215))
        self.treeButton.setStyleSheet("")
        self.treeButton.setObjectName("treeButton")
        self.treeLayout.addWidget(self.treeButton)
        self.horizontalLayout_2.addWidget(self.treeButton)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.projectName = QtWidgets.QComboBox(self.centralwidget)
        self.projectName.setObjectName("projectName")
        self.verticalLayout.addWidget(self.projectName)
        self.projectView = QtWidgets.QTreeView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.projectView.sizePolicy().hasHeightForWidth())
        self.projectView.setSizePolicy(sizePolicy)
        self.projectView.setObjectName("projectView")
        self.verticalLayout.addWidget(self.projectView)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 962, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        self.menuFile.setFont(font)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        self.menuHelp.setFont(font)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusbar.sizePolicy().hasHeightForWidth())
        self.statusbar.setSizePolicy(sizePolicy)
        self.statusbar.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(8)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.statusbar.setFont(font)
        self.statusbar.setSizeGripEnabled(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionUpdate = QtWidgets.QAction(MainWindow)
        self.actionUpdate.setObjectName("actionUpdate")
        self.actionExport = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.actionExport.setFont(font)
        self.actionExport.setObjectName("actionExport")
        self.actionImport = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.actionImport.setFont(font)
        self.actionImport.setObjectName("actionImport")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.actionHelp.setFont(font)
        self.actionHelp.setObjectName("actionHelp")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.actionAbout.setFont(font)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        self.actionSettings.setFont(font)
        self.actionSettings.setObjectName("actionSettings")
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "???????????????????? ????????????????"))
        self.menuFile.setTitle(_translate("MainWindow", "????????"))
        self.menuHelp.setTitle(_translate("MainWindow", "????????????"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionOpen.setText(_translate("MainWindow", "??????????????..."))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionUpdate.setText(_translate("MainWindow", "Update..."))
        self.actionUpdate.setShortcut(_translate("MainWindow", "Ctrl+U"))
        self.actionExport.setText(_translate("MainWindow", "??????????????????"))
        self.actionExport.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionImport.setText(_translate("MainWindow", "??????????????..."))
        self.actionImport.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "??????????????????"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionHelp.setText(_translate("MainWindow", "Help"))
        self.actionHelp.setShortcut(_translate("MainWindow", "F1"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionSettings.setText(_translate("MainWindow", "??????????????????..."))
