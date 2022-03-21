import sys
import os
from pathlib import Path
import traceback

workObjPath = Path(__file__).parent.joinpath("../").resolve()
sys.path.append(str(workObjPath))
# ---------------------------------
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtWidgets, QtCore, QtGui
# ---------------------------------
from GUI.UI_MainWindow import Ui_MainWindow  # Это наш конвертированный файл дизайна
from GUI.ImportDialog import ImportDialog
from GUI.SettingsDialog import SettingsDialog, Settings
from GUI.PropertiesWidget import PropertiesWidget
from GUI.tab import EditTab, BrowseTab, TranslateCommand, ClearCommand, PasteCommand
from GUI.Runnable import Worker
from GUI.HelpWindow import HelpWindow
# ---------------------------------
# import logging
from ApcWorkObj import ApcCompiler
from ApcLogger import getLogger
from ApcEditor import Editor

# временная папка, в которую распаковываются файлы при запуске exe
# когда собрано в 'one-file' (см build.py) mode
# https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
bundle_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
ApcCompiler.set_abbreviations(filename=Path("./abbreviations.json").resolve())


# todo: 1. перевести translate на advanced mode, добавить batch, glossary


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    logger = getLogger("MainWindow")
    ApcCompiler.set_log_level("INFO")

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.logger.debug("constructing MainWindow")
        try:
            self.toolBar.addAction(self.actionImport)
            self.toolBar.addAction(self.actionOpen)
            self.toolBar.addAction(self.actionExport)
            self.toolBar.setWindowTitle(self.tr("Инструменты"))
            self.menuFile.insertAction(self.actionExport, self.actionOpen)
            font = QtGui.QFont()
            font.setFamily("Verdana")
            self.actionOpen.setFont(font)
            self.actionOpen.setShortcut(self.tr("Ctrl+J"))
            self.actionOpen.setText(self.tr("Открыть из JSON"))
            self.actionOpen.triggered.connect(self.on_open_triggered)
            self.actionOpen.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/import.ico").resolve())
                    )
                )
            )
            self.treeButton.pressed.connect(self.on_tree_button_pressed)
            self.actionExport.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/cmdSave.ico").resolve())
                    )
                )
            )
            self.actionImport.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/folder.png").resolve())
                    )
                )
            )
            self.actionSettings.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/Settings.ico").resolve())
                    )
                )
            )
            self.actionCompile = QtWidgets.QAction(self)
            self.actionCompile.setText(self.tr("Пересобрать ресурсы"))
            self.actionCompile.setObjectName("actionCompile")
            self.actionCompile.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/Go.ico").resolve())
                    )
                )
            )
            self.toolBar.addAction(self.actionSettings)
            self.toolBar.addAction(self.actionCompile)
            self.toolBar.addSeparator()
            self.actionHelp.triggered.connect(self.on_help_triggered)
            self.actionAbout.triggered.connect(self.on_about_triggered)
            self.actionSettings.triggered.connect(self.on_settings_triggered)
            self.actionCompile.triggered.connect(self.on_compile_triggered)
            self.actionImport.triggered.connect(self.on_import_triggered)
            self.actionExport.triggered.connect(self.on_export_triggered)
            # undo redo
            self.undoAction = QtWidgets.QAction(self)
            self.undoAction.setText(self.tr("Отмена"))
            self.undoAction.setShortcut(QtGui.QKeySequence.Undo)
            self.undoAction.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/undo.png").resolve())
                    )
                )
            )
            self.undoAction.triggered.connect(self.on_undo_triggered)
            self.redoAction = QtWidgets.QAction(self)
            self.redoAction.setText(self.tr("Повтор"))
            self.redoAction.setShortcut(QtGui.QKeySequence.Redo)
            self.redoAction.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/redo.png").resolve())
                    )
                )
            )
            self.redoAction.triggered.connect(self.on_redo_triggered)
            # actions for tab
            self.actionClear = QtWidgets.QAction(self.tr("Очистить"), self)
            self.actionClear.setShortcut(QtGui.QKeySequence.Delete)
            self.actionClear.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/eraser_2.png").resolve())
                    )
                )
            )
            self.actionClear.triggered.connect(self.on_clear_triggered)
            self.actionCopy = QtWidgets.QAction(self.tr("Копировать"), self)
            self.actionCopy.setShortcut(QtGui.QKeySequence.Copy)
            self.actionCopy.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/copy.png").resolve())
                    )
                )
            )
            self.actionCopy.triggered.connect(self.on_copy_triggered)
            self.toolBar.addAction(self.actionCopy)
            self.actionPaste = QtWidgets.QAction(self.tr("Вставить"), self)
            self.actionPaste.setShortcut(QtGui.QKeySequence.Paste)
            self.actionPaste.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/paste.png").resolve())
                    )
                )
            )
            self.actionPaste.triggered.connect(self.on_paste_triggered)
            self.toolBar.addAction(self.actionPaste)
            # translate action
            self.actionTranslate = QtWidgets.QAction(self.tr("Перевести"), self)
            self.actionTranslate.setShortcut("Ctrl+T")
            self.actionTranslate.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/education.png").resolve())
                    )
                )
            )
            self.actionTranslate.triggered.connect(self.on_translate_triggered)

            # search action
            self.searchBar = QtWidgets.QToolBar(self.tr("Поиск"), self)
            # searchWidget = QtWidgets.QDockWidget(flags=QtCore.Qt.Widget)
            # searchWidget.setContentsMargins(0,0,0,0)
            # #searchWidget.setLayout(searchWidgetLayout)
            # self.addDockWidget(QtCore.Qt.TopDockWidgetArea, searchWidget)
            searchWidgetLayout = QtWidgets.QHBoxLayout()
            self.searchField = QtWidgets.QLineEdit()
            widget = QtWidgets.QWidget()
            widget.setLayout(searchWidgetLayout)
            # self.searchBar.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            searchWidgetLayout.setContentsMargins(0, 0, 10, 0)
            searchWidgetLayout.addStretch(200)
            searchWidgetLayout.addWidget(self.searchField, 100)
            # searchWidget.setWidget(widget)
            self.searchField.setPlaceholderText(self.tr("Поиск"))
            self.searchField.setBaseSize(40, 10)
            # self.searchField.textEdited.connect(self.searchTextInEditor)

            self.searchBar.addWidget(widget)
            # self.searchBar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)
            self.searchBar.setFloatable(True)
            # self.searchBar(searchWidget)
            self.searchBar.hide()
            self.addToolBar(QtCore.Qt.TopToolBarArea, self.searchBar)
            self.searchAction = QtWidgets.QAction(self.tr("Поиск"), self)
            self.searchAction.setShortcut("Ctrl+F")
            self.searchAction.setIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/keyword.png").resolve())
                    )
                )
            )
            self.searchField.textEdited.connect(self.searchTextInEditor)
            # self.searchField.returnPressed.connect(self.searchTextInEditor)
            self.searchAction.triggered.connect(self.on_search_triggered)

            self.toolBar.addAction(self.actionClear)
            self.toolBar.addSeparator()
            self.toolBar.addAction(self.undoAction)
            self.toolBar.addAction(self.redoAction)
            self.toolBar.addSeparator()
            self.toolBar.addAction(self.actionTranslate)

            self.menuEdit = QtWidgets.QMenu(self.menubar)
            font = QtGui.QFont()
            font.setFamily("Verdana")
            font.setPointSize(8)
            self.menuEdit.setFont(font)
            self.menuEdit.setObjectName("menuEdit")
            self.menuEdit.setTitle(self.tr("Правка"))
            self.menubar.insertAction(self.menuHelp.menuAction(), self.menuEdit.menuAction())
            # icons
            self.menuEdit.addAction(self.undoAction)
            self.menuEdit.addAction(self.redoAction)
            self.menuEdit.addAction(self.actionCopy)
            self.menuEdit.addAction(self.actionPaste)
            self.menuEdit.addAction(self.actionClear)
            self.menuEdit.addSeparator()
            self.menuEdit.addAction(self.actionTranslate)
            self.menuEdit.addSeparator()
            self.menuEdit.addAction(self.searchAction)
            self.ErrorDialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, self.tr("Ошибка!"), "",
                                                     QtWidgets.QMessageBox.Ok, self)
            # self.ErrorDialog.setIconPixmap(QtGui.QPixmap("../Resources/Error.ico"))
            self.setWindowIcon(
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/education.png").resolve())
                    )
                )
            )
            self.documents = []
            self.projects = []
            self.wd = Path(".")
            self.actionExport.setEnabled(False)
            self.actionClear.setEnabled(False)
            self.actionTranslate.setEnabled(False)
            self.actionCopy.setEnabled(False)
            self.actionPaste.setEnabled(False)
            self.undoAction.setEnabled(False)
            self.redoAction.setEnabled(False)
            self.searchAction.setEnabled(False)

            self.FileSystem = QFileSystemModel(self)
            # self.FileSystem.setFilter() todo: подумать!
            # self.FileSystem.setNameFilters(["*.json"])
            root = self.FileSystem.setRootPath(str(self.wd))
            self.projectView.setModel(self.FileSystem)
            self.projectView.setWindowFlag(QtCore.Qt.WindowTitleHint)
            self.projectView.setRootIndex(root)
            self.projectView.setItemDelegate(
                FileBrowserDelegate(self.logger, self, self.browser, self.documents, self.projectView))
            self.projectView.doubleClicked.connect(self.on_doubleclicked)
            font = self.projectView.font()
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            self.projectView.setFont(font)
            self.projectView.setHidden(True)

            self.projectName.setHidden(True)
            self.projectName.currentIndexChanged.connect(self.on_currentProjectChanged)

            self.browser.tabCloseRequested.connect(self.on_tab_close)
            self.browser.currentChanged.connect(self.on_currentTabChanged)
            self.importDialog = ImportDialog(parent=self)
            self.importDialog.setWindowIcon(self.actionImport.icon())

            self.propertiesWidget = PropertiesWidget(parent=self.statusbar)
            self.statusbar.addPermanentWidget(self.propertiesWidget)
            # self.statusbar.setStyleSheet("border: 1px solid red")
            self.propertiesWidget.hide()
            self.settings = Settings(self)
            self.settingsDialog = SettingsDialog(parent=self)
            self.settingsDialog.setWindowIcon(self.actionSettings.icon())
            self.settingsDialog.resetMain.connect(self.settings.resetMain)
            try:
                self.logger.info(self.settings.get_settings())
                self.settingsDialog.set_settings(self.settings.get_settings())
                self.logger.info(self.settings.get_settings())
            except Exception as e:
                self.logger.exception(e)
                QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap(
                    str(bundle_dir.joinpath("./Resources/leftarrow_80360.ico"))
                ),
                QtGui.QIcon.Normal,
                # QtGui.QIcon.Off
            )

            self.treeButton.setIcon(icon)
            self.treeButton.setIconSize(QtCore.QSize(8, 8))
            self.treeButton.setToolTip(self.tr("Открыть проводник"))
            self.clipboard = QtGui.QGuiApplication.clipboard()
            self.threadPool = QtCore.QThreadPool.globalInstance()
            self.logger.info(f"active Threads: {str(self.threadPool.activeThreadCount())},"
                             f" max threads: {str(self.threadPool.maxThreadCount())}", )
            self.helpWindow = HelpWindow(QtCore.QUrl.fromLocalFile(str(bundle_dir.joinpath("./Resources/help.html"))),
                                         self)
            self.helpWindow.hide()
            self.setAnimated(True)
            self.browser.setTabBar(CustomTabBar(self.browser, self, self.browser))
            self.browser.setDocumentMode(True)
            self.browser.setTabsClosable(True)
        except Exception as e:
            self.logger.exception(e)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.logger.debug("closing")
        return super().closeEvent(a0)

    def update_browser(self, project):
        project_path, compilers, tabs, _ = project
        self.documents.clear()
        self.browser.clear()

        # todo: disconnect signals from closed tab
        for tab in tabs:
            docName = tab.compiler.JSON_editor.file
            self.logger.debug("adding tab:%s", str(docName))
            for i in range(len(self.documents)):
                if self.documents[i][0] == Path(docName):
                    self.browser.setCurrentIndex(i)
                    return

            tab.import_completed.connect(self.on_import_completed)
            tab.cancelled.connect(self.on_cancel)
            tab.export_finished.connect(self.on_export_finished)
            tab.compile_finished.connect(self.on_compile_finished)
            tab.tableModel.dataChanged.connect(self.on_data_changed)
            tab.tableView.selectionModel().selectionChanged.connect(self.on_selection_changed)
            tab.undoStack.canUndoChanged.connect(self.on_canUndo)
            tab.undoStack.canRedoChanged.connect(self.on_canRedo)
            # append new document to browser
            self.documents.append([docName, tab.compiler, project_path])
            self.logger.debug(tab.compiler.json_langs)
            self.browser.addTab(tab, "/".join((docName.parents[1].name, docName.parents[0].name)))
            self.browser.setCurrentIndex(self.browser.count() - 1)
            self.browser.setTabIcon(
                self.browser.count() - 1,
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/cmdSave.ico"))
                    )
                )
            )
            self.browser.setTabToolTip(self.browser.count() - 1, str(docName))

    def addEditTab(self, compiler, main_lang: str, langs, service: str, project: Path = None, fLoad: bool = False):
        try:
            docName = compiler.JSON_editor.file
            self.logger.debug("adding tab:%s", str(docName))
            for i in range(len(self.documents)):
                if self.documents[i][0] == Path(docName):
                    self.browser.setCurrentIndex(i)
                    return self.browser.widget(i)
            # create tab and connect it to mainwindow
            tab = EditTab(str(docName), compiler)
            tab.import_completed.connect(self.on_import_completed)
            tab.cancelled.connect(self.on_cancel)
            tab.export_finished.connect(self.on_export_finished)
            tab.compile_finished.connect(self.on_compile_finished)
            tab.tableModel.dataChanged.connect(self.on_data_changed)
            tab.tableView.selectionModel().selectionChanged.connect(self.on_selection_changed)
            tab.undoStack.canUndoChanged.connect(self.on_canUndo)
            tab.undoStack.canRedoChanged.connect(self.on_canRedo)
            # append new document to browser
            self.documents.append([docName, compiler, project])
            self.logger.debug(compiler.json_langs)
            self.browser.addTab(tab, "/".join((docName.parents[1].name, docName.parents[0].name)))
            self.browser.setCurrentIndex(self.browser.count() - 1)
            self.browser.setTabIcon(
                self.browser.count() - 1,
                QtGui.QIcon(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/cmdSave.ico"))
                    )
                )
            )
            self.browser.setTabToolTip(self.browser.count() - 1, str(docName))
            # update model
            if fLoad:
                self.statusBar().showMessage(f"loading {str(compiler.JSON_editor.file)}")
                tab.load(compiler, main_lang, langs, service)
            else:
                tab.on_import_complete()
            return tab
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

    @pyqtSlot(name="on_clear_triggered")
    def on_clear_triggered(self):
        """
        'Clear' action
        :return:
        """
        try:
            self.logger.debug("clear triggered")
            tab = self.browser.currentWidget()
            tab.undoStack.push(ClearCommand(tab))
        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="on_copy_triggered")
    def on_copy_triggered(self):
        """'Copy' action."""
        try:
            self.logger.debug("copy triggered")
            tab = self.browser.currentWidget()
            index = tab.tableView.currentIndex()
            if index:
                text = str(index.data(QtCore.Qt.EditRole))
                self.logger.debug(text)
                self.clipboard.setText(text)
        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="on_paste_triggered")
    def on_paste_triggered(self):
        """
        'Paste' action
        :return:
        """
        try:
            self.logger.debug("paste triggered")
            tab = self.browser.currentWidget()
            tab.undoStack.push(PasteCommand(tab, self.clipboard))
        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="on_translate_triggered")
    def on_translate_triggered(self):
        try:
            self.logger.debug("translate triggered")
            tab = self.browser.currentWidget()
            service = tab.compiler.service
            ok = True
            if not service:
                service, ok = QtWidgets.QInputDialog.getItem(
                    tab,
                    tab.tr("Выберите сервис"),
                    tab.tr("Сервис:"),
                    [serv for serv in ApcCompiler.services if
                     ApcCompiler.services[serv]])
            if not ok:
                return
            # tab.compiler.service = service
            self.logger.info("Translate with service: %s", service)
            tab.undoStack.push(TranslateCommand(service, tab))

        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="searchTextInEditor")
    def searchTextInEditor(self):
        tab = self.browser.currentWidget()
        tab.search_text(self.searchField.text())

    @pyqtSlot(name="on_search_triggered")
    def on_search_triggered(self):
        try:
            self.logger.debug("search triggered")
            self.searchBar.show()
            self.searchField.setFocus()

        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="on_undo_triggered")
    def on_undo_triggered(self):
        try:
            self.logger.debug("undo triggered")
            tab = self.browser.currentWidget()
            tab.undoStack.undo()

        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="on_redo_triggered")
    def on_redo_triggered(self):
        try:
            self.logger.debug("redo triggered")
            tab = self.browser.currentWidget()
            tab.undoStack.redo()

        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(bool, name="on_canRedo")
    def on_canRedo(self, canRedo: bool):
        try:
            self.logger.debug("can redo %s", canRedo)
            self.redoAction.setEnabled(True) if canRedo else self.redoAction.setEnabled(False)

        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(bool, name="on_canUndo")
    def on_canUndo(self, canUndo: bool):
        try:
            self.logger.debug("can redo %s", canUndo)
            self.undoAction.setEnabled(True) if canUndo else self.undoAction.setEnabled(False)

        except Exception as e:
            self.logger.exception(e)

    def on_selection_changed(self):
        try:
            self.logger.debug("selection_changed")
            tab = self.browser.currentWidget()
            indexes = tab.tableView.selectedIndexes()
            if indexes:
                self.actionCopy.setEnabled(True)
                self.actionTranslate.setEnabled(True)
                self.actionPaste.setEnabled(True)
                self.actionClear.setEnabled(True)
            else:
                self.actionCopy.setEnabled(False)
                self.actionTranslate.setEnabled(False)
                self.actionPaste.setEnabled(False)
                self.actionClear.setEnabled(False)

        except Exception as e:
            self.logger.exception(e)

    def on_data_changed(self):
        try:
            self.logger.debug("data_changed")
            tab = self.browser.currentWidget()
            if not tab.changed:
                tab.changed = True
                current_index = self.browser.currentIndex()
                self.browser.setTabIcon(current_index, QtGui.QIcon(QtGui.QPixmap(
                    str(bundle_dir.joinpath("./Resources/cmdSave.ico"))
                )))
        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="on_open_triggered")
    def on_open_triggered(self):
        try:
            self.logger.info("open json")
            fileName = QFileDialog.getOpenFileName(self, self.tr("Открыть файл"),
                                                   str(self.wd),
                                                   self.tr("JSON files (*.json)"))
            self.logger.info(f"open json {fileName}")
            file = Path(fileName[0])
            if not fileName[0]:
                return
            if file.exists():
                if self.documents:
                    index = -1
                    for name, _ in self.documents:
                        index += 1
                        if file == name:
                            self.logger.debug(file)
                            self.logger.debug(name)
                            self.browser.setCurrentIndex(index)
                            return
                xml_file = None
                wd = file.parent
                # Добавляем новый проект
                index = -1
                flag = False
                for i in range(self.projectName.count()):
                    index += 1
                    if self.projects[i][0] == wd:
                        flag = True
                        break
                if flag:
                    self.projectName.setCurrentIndex(index)
                    return
                compiler = ApcCompiler(xml_file=xml_file, wd=wd)

                project = (wd, [compiler], {wd})
                self.projects.append(project)
                index = self.projectName.count()
                self.projectName.addItem(wd.name)
                self.projectName.setCurrentIndex(index)
                self.addEditTab(compiler, compiler.main_lang, compiler.json_langs, compiler.service, project=wd,
                                fLoad=True)
                # изменяем ProjectView
                self.actionExport.setEnabled(True)
                self.wd = compiler.wd
                self._set_project_view_with_project(project)
                if self.projectView.isHidden():
                    self.on_tree_button_pressed()
                self.statusBar().showMessage(f"{str(compiler.JSON_editor.file)} imported", 1500)
            self.logger.info("Working directory: %s", str(self.wd))
        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(name="on_tree_button_pressed")
    def on_tree_button_pressed(self):
        try:
            self.logger.debug("tree button pressed")
            if self.projectView.isHidden():
                self.projectView.setHidden(False)
                self.projectName.setHidden(False)
                icon = self.treeButton.icon()
                icon.addPixmap(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/rightarrow_121279.ico"))
                    ),
                    QtGui.QIcon.Normal,
                    # QtGui.QIcon.Off
                )
                self.treeButton.setIcon(icon)
                self.treeButton.setToolTip(self.tr("Закрыть проводник"))

            else:
                self.projectView.setHidden(True)
                self.projectName.setHidden(True)
                icon = self.treeButton.icon()
                icon.addPixmap(
                    QtGui.QPixmap(
                        str(bundle_dir.joinpath("./Resources/leftarrow_80360"))
                    ),
                    QtGui.QIcon.Normal,
                    # QtGui.QIcon.Off
                )
                self.treeButton.setIcon(icon)
                self.treeButton.setToolTip(self.tr("Открыть проводник"))
        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(QtCore.QModelIndex, name='on_doubleclicked')
    def on_doubleclicked(self, index: QtCore.QModelIndex):
        try:
            self.logger.debug("DoubleClicked")

            # curdir = Path(self.FileSystem.data(index))
            # if curdir.is_dir():
            #   self.wd = curdir
            #   self.logger.info(self.wd)
            #   self.projectView.setRootIndex(index)
            #   self.importDialog.setup(str(self.wd), ApcCompiler.languages)
        except Exception as e:
            self.logger.exception(e)

    def currentProject(self):
        return self.projects[self.projectName.currentIndex()] if self.projects else None

    @pyqtSlot(int, name='on_currentProjectChanged')
    def on_currentProjectChanged(self, index: int):
        self._set_project_view_with_project(self.projects[index])

    @pyqtSlot(int, name='on_currentTabChanged')
    def on_currentTabChanged(self, index: int):
        try:
            self.logger.debug("current changed")
            if self.documents:
                name, compiler, project = self.documents[index]
                if compiler:
                    self.actionExport.setEnabled(True)
                    self.searchAction.setEnabled(True)
                    tab = self.browser.currentWidget()
                    self.undoAction.setEnabled(True) if tab.undoStack.canUndo() else self.undoAction.setEnabled(False)
                    self.redoAction.setEnabled(True) if tab.undoStack.canRedo() else self.redoAction.setEnabled(False)
                    self.propertiesWidget.set_compiler(compiler)
                    self.propertiesWidget.show()
                else:
                    self.actionExport.setEnabled(False)
                    self.propertiesWidget.hide()
                if project:
                    self.propertiesWidget.value_project_files.setText(f'{self.browser.count()}')

            else:
                self.actionExport.setEnabled(False)
                self.actionClear.setEnabled(False)
                self.actionTranslate.setEnabled(False)
                self.actionCopy.setEnabled(False)
                self.actionPaste.setEnabled(False)
                self.searchAction.setEnabled(False)
                self.undoAction.setEnabled(False)
                self.redoAction.setEnabled(False)

        except Exception as e:
            self.logger.exception(e)

    @pyqtSlot(int, name='on_tab_close')
    def on_tab_close(self, index: int):
        try:
            self.logger.debug("closed")
            self.documents.pop(index)
            self.currentProject()[2].pop(index)
            tab = self.browser.widget(index)
            if isinstance(tab, EditTab):
                if tab.changed and QtWidgets.QMessageBox.Yes == \
                        QtWidgets.QMessageBox.question(self,
                                                       self.tr("Сохранение"),
                                                       self.tr("Хотите сохранить изменения?")):
                    tab.save()
            self.browser.removeTab(index)
            if not self.documents:
                self.actionExport.setEnabled(False)
                self.actionClear.setEnabled(False)
                self.actionTranslate.setEnabled(False)
                self.actionCopy.setEnabled(False)
                self.actionPaste.setEnabled(False)
                self.undoAction.setEnabled(False)
                self.redoAction.setEnabled(False)
                self.propertiesWidget.hide()
            self.logger.info("Documents: %s", self.documents)
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

    @pyqtSlot(QtCore.QModelIndex, name='on_expanded')
    def on_expanded(self, index):
        self.logger.warning("Expanded")

    @pyqtSlot(name='on_import_triggered')
    def on_import_triggered(self):
        """"""
        try:
            self.logger.info("importing..")
            if self.documents:  # если есть документы, ImportDialog устанавливаем с настройками текущего документа
                name, compiler, project = self.documents[self.browser.currentIndex()]
                if compiler:
                    self.logger.info("update %s", name)
                    self.importDialog.set_compiler(compiler)
                    nResult = self.importDialog.exec()
                    if nResult and self.importDialog.langs:  # if any lang was chosen:
                        wd = compiler.wd
                        xml_file = compiler.XML_editor.file
                        if self.importDialog.source.is_dir():  # if source is dir open as a project
                            if wd != self.importDialog.source:
                                self.open_project(self.importDialog.source)
                                self.logger.debug(f"Projects: {self.projects}")
                                return
                        else:  # if source is file open as a tab in browser
                            if xml_file != self.importDialog.source:
                                xml_file = self.importDialog.source
                                wd = xml_file.parent
                                compiler = ApcCompiler(xml_file, wd=wd)
                                self.addEditTab(compiler, self.importDialog.main_lang, self.importDialog.langs,
                                                self.importDialog.service, fLoad=True)
                                return
                        # if wd == compiler.wd that is same compiler - just reload with needed prefs
                        self.logger.info("working directory: %s", str(wd))
                        tab = self.browser.currentWidget()
                        tab.load(compiler, self.importDialog.main_lang, self.importDialog.langs,
                                 self.importDialog.service)
                        self.statusBar().showMessage(f"importing {str(compiler.JSON_editor.file)}", 1500)
                    return
            # если нет документов, то ImportDialog будет с настройками из SettingsDialog
            self.importDialog.setup(
                self.wd,
                langs=list(self.settingsDialog.langs.keys()),
                main_lang=self.settingsDialog.main_lang,
                service=self.settingsDialog.service
            )
            nResult = self.importDialog.exec()
            if nResult and self.importDialog.langs:  # ok
                self.logger.debug("From: %s", self.importDialog.source)
                if self.importDialog.source.is_dir():  # if source is dir open as a project
                    self.open_project(self.importDialog.source)
                    self.logger.info(f"Projects: {self.projects}")
                    return
                else:  # if source is file open as a tab in browser
                    xml_file = self.importDialog.source
                    compiler = ApcCompiler(xml_file, wd=xml_file.parent)
                    self.addEditTab(compiler, self.importDialog.main_lang, self.importDialog.langs,
                                    self.importDialog.service, fLoad=True)
                    return
        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.error(traceback.format_exc())
            self.ErrorDialog.setText(str(value))
            self.ErrorDialog.show()

    def open_project(self, wd):
        self.wd = wd
        projectPath = self.wd
        xml_files = [file for file in projectPath.rglob("*.xml") if file.is_file()]
        if not xml_files:
            raise ValueError(f"Can't find any XML file in {str(self.wd.resolve())}")
        # Добавляем новый проект
        index = -1
        flag = False
        for i in range(self.projectName.count()):
            index += 1
            if self.projects[i][0] == projectPath:
                flag = True
                break
        if flag:
            self.projectName.setCurrentIndex(index)
            return
        compilers = []
        for file in xml_files:
            try:
                compilers.append(ApcCompiler(xml_file=file, wd=file.parent))
            except (ValueError, SyntaxError):
                continue

        # если один файл, то можно и открыть его
        tabs = []
        if len(compilers) == 1:
            tab = self.addEditTab(
                compilers[0],
                self.importDialog.main_lang,
                self.importDialog.langs,
                self.importDialog.service,
                project=projectPath,
                fLoad=True)
            tabs.append(tab)
        else:
            for compiler in compilers:
                tab = self.addEditTab(
                    compiler,
                    self.importDialog.main_lang,
                    self.importDialog.langs,
                    self.importDialog.service,
                    project=projectPath,
                    fLoad=True)
                tabs.append(tab)

        # создаем проект
        project = (projectPath, compilers, tabs, {path for path in projectPath.rglob("*")
                                            if path.is_dir() and not any(
                map(lambda x: os.path.commonpath((path, x)) == str(path),
                    (str(c.XML_editor.file) for c in compilers)))
                                            })
        self.projects.append(project)
        index = self.projectName.count()
        self.projectName.addItem(projectPath.name)
        self.projectName.setCurrentIndex(index)
        # изменяем ProjectView
        self._set_project_view_with_project(project)
        if self.projectView.isHidden():
            self.on_tree_button_pressed()

    def _set_project_view_with_project(self, project):
        try:
            if not project:
                return

            project_path, compilers, tabs, file_paths = project
            paths = file_paths if file_paths else {path for path in project[0].rglob("*")
                                                   if path.is_dir() and not any(
                    map(lambda x: os.path.commonpath((path, x)) == str(path),
                        (str(c.XML_editor.file) for c in compilers)))
                                                   }
            root = self.FileSystem.setRootPath(str(project_path))
            self.projectView.setRootIndex(root)
            for path in paths:
                index = self.FileSystem.index(str(path))
                self.projectView.setRowHidden(index.row(), index.parent(), True)
            self.update_browser(project)

        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)
            self.ErrorDialog.setText(traceback.format_exception(exctype, value, exctb))
            self.ErrorDialog.show()

    @pyqtSlot(ApcCompiler, name='on_import_completed')
    def on_import_completed(self, compiler):
        try:
            if self.documents:
                index = -1
                for docname, comp, _ in self.documents:
                    index += 1
                    if docname == compiler.JSON_editor.file:
                        self.documents[index][1] = compiler
                        tab = self.browser.widget(index)
                        tab.tableView.horizontalHeader().setDefaultSectionSize(tab.width() // len(compiler.json_langs))
                        self.browser.setTabIcon(index, QtGui.QIcon(QtGui.QPixmap(
                            str(bundle_dir.joinpath("./Resources/cmdSave.ico"))
                        )))
                        break

            self.importDialog.set_compiler(compiler)
            self.propertiesWidget.set_compiler(compiler)
            self.actionExport.setEnabled(True)
            self.statusBar().showMessage(f"{str(compiler.JSON_editor.file)} imported", 1500)
            self.logger.info(f"import completed {str(compiler.JSON_editor.file)}")
            loaded = 0
            for i in range(self.browser.count()):
                loaded = loaded + 1 if self.browser.widget(i).loaded else loaded
            self.propertiesWidget.value_project_files.setText(f'{loaded} из {self.browser.count()}')

        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)
            self.ErrorDialog.setText(traceback.format_exception(exctype, value, exctb))
            self.ErrorDialog.show()

    @pyqtSlot(name='on_export_triggered')
    def on_export_triggered(self):
        try:
            self.logger.info("saving started")
            if self.documents:
                if len(self.documents) > 1:
                    multi_export = QtWidgets.QMessageBox.Yes == QtWidgets.QMessageBox.question(
                        self,
                        self.tr("Сохранение"),
                        self.tr("Хотите сохранить все?"))
                    if multi_export:
                        # self.statusBar().showMessage(f"saving {}")
                        for index, document in enumerate(self.documents):
                            name, compiler, _ = document
                            if compiler:
                                tab = self.browser.widget(index)
                                if isinstance(tab, EditTab):
                                    if tab.changed:
                                        tab.save()

                    else:
                        current_index = self.browser.currentIndex()
                        name, compiler, _ = self.documents[current_index]
                        if compiler:
                            self.statusBar().showMessage(f"saving {name}")
                            self.browser.currentWidget().save()

                else:
                    current_index = self.browser.currentIndex()
                    name, compiler, _ = self.documents[current_index]
                    if compiler:
                        self.statusBar().showMessage(f"saving {name}")
                        self.browser.currentWidget().save()

        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)
            self.ErrorDialog.setText(traceback.format_exc())
            self.ErrorDialog.show()

    @pyqtSlot(ApcCompiler, name="on_export_finished")
    def on_export_finished(self, compiler):
        try:
            self.statusBar().showMessage(f"{str(compiler.JSON_editor.file)} saved", 1500)
            index = -1
            flag = False
            for docname, comp, _ in self.documents:
                index += 1
                if docname == compiler.JSON_editor.file:
                    flag = True
                    break
            if flag:
                self.browser.setTabIcon(
                    index,
                    QtGui.QIcon(
                        QtGui.QPixmap(
                            str(bundle_dir.joinpath("./Resources/cmdSaveDisabled.ico"))
                        )
                    )
                )
            self.logger.info("saving finished")
        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)
            self.ErrorDialog.setText(traceback.format_exc())
            self.ErrorDialog.show()

    @pyqtSlot(name='on_settings_triggered')
    def on_settings_triggered(self):
        try:
            self.logger.info("Settings editing.")
            self.settingsDialog.set_settings(self.settings.get_settings())
            nResult = self.settingsDialog.exec()
            if nResult:
                _settings = {
                    "main_lang": self.settingsDialog.main_lang,
                    "langs": list(self.settingsDialog.langs.keys()),
                    "service": self.settingsDialog.service,
                    "tokens": self.settingsDialog.tokens
                }
                self.settings.set_settings(_settings)
            else:
                self.logger.info("Settings editing was canceled")
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

    @pyqtSlot(name='on_compile_triggered')
    def on_compile_triggered(self):
        try:
            self.logger.info("Compiling..")
            if self.documents:
                current_index = self.browser.currentIndex()
                name, compiler, _ = self.documents[current_index]
                if compiler:
                    self.browser.currentWidget().compile()
                    self.statusBar().showMessage(f"compiling {str(compiler.XML_editor.file)}")
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

    def on_compile_finished(self, compiler):
        try:
            self.logger.info("Compiling finished")
            self.statusBar().showMessage(f"{str(compiler.XML_editor.file)} compiled", 1500)
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

    @pyqtSlot(ApcCompiler, str, name='on_cancel')
    def on_cancel(self, compiler: ApcCompiler, cmd: str):
        try:
            self.logger.info(f"Cancelled {cmd}")
            if self.documents and cmd == "update":
                if self.documents:
                    index = -1
                    for docname, comp, _ in self.documents:
                        index += 1
                        if docname == compiler.JSON_editor.file:
                            self.documents.pop(index)
                            self.browser.removeTab(index)
                            self.propertiesWidget.hide()
            self.statusBar().showMessage(f"{str(compiler.JSON_editor.file)} cancelled", 1500)
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

    @pyqtSlot(name='on_help_triggered')
    def on_help_triggered(self):
        try:
            self.logger.info("Help triggered")
            self.helpWindow.show()
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)

    @pyqtSlot(name='on_about_triggered')
    def on_about_triggered(self):
        try:
            self.logger.debug("About")
        except Exception as e:
            self.logger.exception(e)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(e), QtWidgets.QMessageBox.Ok)


class FileBrowserDelegate(QtWidgets.QStyledItemDelegate):
    """нужен для обработки нажатия на редактирование."""

    def __init__(self, logger, window: QtWidgets.QMainWindow, browser: QtWidgets.QTabWidget, documents: list,
                 parent=None):
        super(FileBrowserDelegate, self).__init__(parent)
        self.logger = logger
        self.window = window
        self.documents = documents
        self.browser = browser

    def addBrowseTab(self, model: QtWidgets.QFileSystemModel, index: QtCore.QModelIndex):
        try:
            file = model.filePath(index)
            for i in range(len(self.documents)):
                if self.documents[i][0] == Path(file):
                    self.browser.setCurrentIndex(i)
                    return
            self.documents.append([Path(file), None, None])
            tab = BrowseTab(str(file))
            self.browser.addTab(tab, str(file))
            self.browser.setCurrentIndex(self.browser.count() - 1)
            self.browser.setTabToolTip(self.browser.count() - 1, str(file))
            textBrowser = tab.textBrowser
            editor = Editor(file)
            editor.open()
            textBrowser.setPlainText(editor.text)
            # self.logger.info(self.documents)
        except Exception as e:
            self.logger.exception(e)

    def editorEvent(self, event: QtCore.QEvent,
                    model: QtCore.QAbstractItemModel,
                    option: 'QtWidgets.QStyleOptionViewItem',
                    index: QtCore.QModelIndex) -> bool:
        """запускается, когда срабатывает EditTrigger на projectView."""
        try:
            project = self.window.currentProject()
            if not project:
                return super().editorEvent(event, model, option, index)
            if event.type() == QtCore.QEvent.MouseButtonDblClick:  # double click on item
                if not model.isDir(index):  # double click on file
                    file = Path(model.filePath(index))
                    if file.suffix == ".json":
                        if self.documents:  # check if already exists in browser
                            ind = -1
                            flag = False
                            for name, _, _ in self.documents:
                                ind += 1
                                if file == name:
                                    flag = True
                                    break
                            if flag:
                                self.browser.setCurrentIndex(ind)
                                return True
                        xml_file = None
                        wd = file.parent
                        compiler = ApcCompiler(xml_file=xml_file, wd=wd)
                        self.window.addEditTab(
                            compiler,
                            self.window.importDialog.main_lang,
                            self.window.importDialog.langs,
                            self.window.importDialog.service)
                        root = self.window.FileSystem.setRootPath(str(wd))
                        self.window.projectView.setRootIndex(root)
                        self.window.statusBar().showMessage(f"{str(compiler.JSON_editor.file)} imported", 1500)
                        return True
                    self.addBrowseTab(model, index)  # if not json
                    return True
                else:  # double click on directory
                    directory = Path(model.filePath(index))
                    if self.documents:  # check if already exists in browser
                        ind = -1
                        flag = False
                        for name, _, _ in self.documents:
                            ind += 1
                            if directory == str(name.parent):
                                flag = True
                                break
                        if flag:
                            self.browser.setCurrentIndex(ind)
                            return True

                    for c in project[1]:
                        if c.wd == directory:  # if compiler was already created as part of project
                            compiler = c
                            self.window.addEditTab(
                                compiler,
                                self.window.importDialog.main_lang,
                                self.window.importDialog.langs,
                                self.window.importDialog.service,
                                project=project[0],
                                fLoad=True)
                            self.window.statusBar().showMessage(f"{str(compiler.JSON_editor.file)} imported", 1500)
                            return True

                    try:
                        compiler = ApcCompiler(wd=directory)
                        self.window.addEditTab(
                            compiler,
                            self.window.importDialog.main_lang,
                            self.window.importDialog.langs,
                            self.window.importDialog.service, fLoad=True)
                        self.window.statusBar().showMessage(f"{str(compiler.JSON_editor.file)} imported", 1500)
                    except ValueError:
                        return True

        except Exception as e:
            self.logger.exception(e)
        finally:
            return super().editorEvent(event, model, option, index)


class CustomTabBar(QtWidgets.QTabBar):
    logger = getLogger("CustomTabBar")

    def __init__(self, browser: QtWidgets.QTabWidget, window: MainWindow, parent=None):
        super().__init__(parent)
        self._browser = browser
        self._window = window

        self.actionCopyPath = QtWidgets.QAction(self.tr("Копировать путь"), self)
        self.actionCopyPath.triggered.connect(self.on_copy_triggered)
        # self.actionShowInExplorer = QtWidgets.QAction(self.tr("Показать в проводнике"), self)
        self._contextMenu = QtWidgets.QMenu("contextMenu", self)
        self._contextMenu.addAction(self.actionCopyPath)

    def on_copy_triggered(self):
        try:
            index = self.tabAt(self._contextMenu.pos())
            if index:
                text = str(self._window.documents[index][0])
                self.logger.debug(text)
                self._window.clipboard.setText(text)
        except Exception as e:
            self.logger.exception(e)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        index = self.tabAt(a0.pos())
        self.logger.debug(f"tab {index}: {a0.pos()} < {self._browser.tabText(index)}")
        if a0.reason() == QtGui.QContextMenuEvent.Mouse:
            self._contextMenu.setFocus()
            self._contextMenu.exec(self.mapToGlobal(a0.pos()), self.actionCopyPath)
            return
        return super().contextMenuEvent(a0)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == QtCore.Qt.MiddleButton:
            index = self.tabAt(a0.pos())
            self._window.on_tab_close(index)
            self._browser.removeTab(index)
            return
        return super().mousePressEvent(a0)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    app.setWindowIcon(QtGui.QIcon(
        QtGui.QPixmap(
            str(bundle_dir.joinpath("./Resources/education.png").resolve())
        )
    ))
    app.setApplicationName("ApcResourcesTranslator")
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
    window.threadPool.waitForDone()


if __name__ == '__main__':
    main()
