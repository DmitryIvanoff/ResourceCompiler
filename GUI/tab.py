import typing
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from GUI.model import JSONModel, EditCommand
import sys
import traceback
from GUI.Runnable import Worker
from ApcWorkObj import ApcCompiler
from ApcLogger import getLogger


class MyHeaderStyle(QtWidgets.QProxyStyle):
    """не используется todo: удалить?"""

    def __init__(self):
        super().__init__()

    def drawControl(self, element: QtWidgets.QStyle.ControlElement, option: QtWidgets.QStyleOption,
                    painter: QtGui.QPainter, widget: typing.Optional[QtWidgets.QWidget] = ...) -> None:
        if element == QtWidgets.QStyle.CE_ItemViewItem:
            painter.save()
            painter.setBackground(QtGui.QColor(204, 255, 204))
            painter.fillRect(option.rect, QtGui.QColor(204, 255, 204))
            painter.restore()
            return
        return super().drawControl(element, option, painter, widget)


class EditTab(QtWidgets.QWidget):
    logger = getLogger("EditTab")
    export_finished = pyqtSignal(ApcCompiler)
    import_completed = pyqtSignal(ApcCompiler)
    cancelled = pyqtSignal(ApcCompiler, str)
    compile_finished = pyqtSignal(ApcCompiler)

    def __init__(self, name, compiler, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)
        try:
            _translate = QtCore.QCoreApplication.translate
            self.compiler = compiler
            self.setObjectName("tab_" + name)
            self.tabLayout = QtWidgets.QHBoxLayout()
            self.tabLayout.setObjectName("tabLayout")
            self.tabLayout.setContentsMargins(6, 2, 4, 2)
            self.setLayout(self.tabLayout)
            # -----------------------------------------
            # create tableView
            self.tableView = QtWidgets.QTableView(self)
            self.undoStack = QtWidgets.QUndoStack(self)
            # -----------------------------------------
            # tableView settings
            font = QtGui.QFont()
            font.setFamily("Consolas")
            font.setPointSize(9)
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            self.tableView.setFont(font)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(10)
            sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
            # self.tableView.setShowGrid(True)
            self.tableView.setSizePolicy(sizePolicy)
            self.tableView.setObjectName("tableView")
            self.tableView.setWordWrap(True)
            # self.tableView.setAlternatingRowColors(True)
            # -----------------------------------------
            #  vertical header settings
            self.tableView.verticalHeader().setFont(font)
            self.tableView.verticalHeader().setTextElideMode(QtCore.Qt.ElideRight)
            self.tableView.verticalHeader().setMaximumWidth(100)
            self.tableView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
            self.tableView.verticalHeader().setDefaultSectionSize(30)
            self.tableView.verticalHeader().setMinimumSectionSize(20)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
            self.tableView.verticalHeader().setSizePolicy(sizePolicy)
            self.tableView.verticalHeader().setContentsMargins(1, 1, 1, 1)
            self.tableView.verticalHeader().setAlternatingRowColors(True)
            # self.tableView.verticalHeader().setStyleSheet(":section {"
            #                                               "border: 1px solid #808080;"
            #                                               "}")
            # self.tableView.set
            # -----------------------------------------
            # horizontal header settings
            self.tableView.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
            self.tableView.horizontalHeader().setMinimumHeight(35)
            # self.tableView.horizontalHeader().setDefaultSectionSize(self.width() // 2)
            self.tableView.horizontalHeader().setAlternatingRowColors(True)
            # style = MyHeaderStyle()
            # self.tableView.horizontalHeader().setStyle(style) # через стиль не работает почему-то
            font = QtGui.QFont()
            font.setFamily("Consolas")
            font.setPointSize(12)
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            self.tableView.horizontalHeader().setFont(font)
            # with Path(__file__).parent.joinpath("header.css").open() as f:
            self.tableView.horizontalHeader().setStyleSheet("""
:section:first{
font-weight: bold;
}""")
            # -----------------------------------------
            # model for tableView
            self.tableModel = JSONModel()
            self.tableView.setModel(self.tableModel)
            self.tableView.setItemDelegate(TableViewDelegate(self, self.tableView))
            self.tableView.setItemDelegateForColumn(0, NotEditableDelegate(self.tableView))
            self.tabLayout.addWidget(self.tableView)
            self.threadPool = QtCore.QThreadPool.globalInstance()
            self.worker = None
            self.changed = False
            # ---------------------------------------
            # progress widget
            self.progressDialog = QtWidgets.QProgressDialog(  # todo: progressDialog - widget progress bar
                self.tr(f"Загрузка {str(compiler.JSON_editor.file)}"),
                self.tr("Отменить"),
                0,
                100,
                flags=QtCore.Qt.SubWindow
            )
            self.tabLayout.addWidget(self.progressDialog)
            self.progressDialog.hide()

            self.loaded = False
            self.iterators = dict()
        except Exception as e:
            self.logger.exception(e)

    def save(self):
        self.worker = Worker(self.compiler,
                             "save")
        self.worker.signals.finished.connect(self.on_export_finished)
        self.worker.signals.error.connect(self._on_error)
        self.worker.signals.result.connect(self._print_output)
        self.threadPool.start(self.worker)

    def update_model(self):
        self.tableModel.import_resources(self.compiler)
        self.changed = True

    def compile(self):
        self.worker = Worker(self.compiler,
                             "compile")
        self.worker.signals.finished.connect(self.on_compile_finished)
        self.worker.signals.error.connect(self._on_error)
        self.worker.signals.result.connect(self._print_output)
        self.threadPool.start(self.worker)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.logger.debug("closing")
        if self.worker:
            self.worker.signals.disconnect_all()
        return super().closeEvent(a0)

    def cancel(self):
        """
        # todo: review
        when pressed "cancel" on progressDialog
        :return:
        """
        try:
            self.logger.debug("cancel clicked")
            if self.worker:
                self.worker.signals.disconnect_all()
                # if not self.threadPool.tryTake(self.worker):
                #   self.threadPool.cancel(self.worker)
                # CancelWidget = QtWidgets.QMessageBox(
                #   QtWidgets.QMessageBox.Information,
                #   self.tr("Отмена"),
                #   self.tr(f"Отмена {self.worker.fn} {self.windowIconText()}"),
                #   flags=QtCore.Qt.Widget)
                # self.tabLayout.addWidget(CancelWidget)
                # CancelWidget.show()
                self.cancelled.emit(self.compiler, self.worker.fn)
        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)

    def load(self, compiler: ApcCompiler, mainlang: str, langs, service: str):
        """
        :param compiler:
        :return:
        """
        self.progressDialog.canceled.connect(self.cancel)
        self.loaded = False
        self.tableView.hide()
        if mainlang:
            self.worker = Worker(
                compiler,
                "update",
                langs,
                main_lang=mainlang,
                # auto_tr_ch=self.mark,
                service=service)
        else:
            self.worker = Worker(compiler,
                                 "update",
                                 langs,
                                 # auto_tr_ch=self.mark,
                                 service=service)
        self.worker.signals.progress.connect(self.progressDialog.setValue)
        self.worker.signals.error.connect(self._on_error)
        self.worker.signals.result.connect(self._print_output)
        self.worker.signals.finished.connect(self.on_import_complete)
        self.threadPool.start(self.worker)
        self.logger.info("loading %s", str(compiler.JSON_editor.file))

    def _print_output(self, s):
        try:
            self.logger.debug(s)
        except Exception as e:
            self.logger.exception(e)
            self.ErrorDialog.setText(str(e))
            self.ErrorDialog.show()

    def on_import_complete(self):
        try:
            self.tableView.show()
            if self.progressDialog.wasCanceled():
                return
            self.progressDialog.setValue(100)
            self.progressDialog.hide()
            self.update_model()
            if not self.changed:
                self.changed = True
            self.logger.info("import is completed")
            self.loaded=True
            self.import_completed.emit(self.compiler)
        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)
            self.ErrorDialog.setText(traceback.format_exception(exctype, value, exctb))
            self.ErrorDialog.show()

    def on_compile_finished(self):
        self.logger.info("compile cmd completed")
        self.compile_finished.emit(self.compiler)

    def on_export_finished(self):
        try:
            self.logger.info("export complete")
            columns = self.tableModel.columnCount()
            rows = self.tableModel.rowCount()
            for c in range(columns):
                for r in range(rows):
                    item = self.tableModel.item(r, c)
                    item.setBackground(QtGui.QColor(255, 255, 255))
            self.changed = False
            self.export_finished.emit(self.compiler)
        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)
            self.ErrorDialog.setText(traceback.format_exc())
            self.ErrorDialog.show()

    def _on_error(self, info):
        try:
            exctype, value, traceback = info
            self.logger.exception(value)
            QtWidgets.QMessageBox.critical(self, self.tr("Ошибка"), str(traceback), QtWidgets.QMessageBox.Ok)
        except Exception as e:
            self.logger.exception(e)

    def iterate_over_items(self, text, matchFlags: QtCore.Qt.MatchFlags = QtCore.Qt.MatchContains):
        """если нужно итерироваться по индексам."""
        index, view = self.tableModel.searchElement(text, matchFlags)
        if index:
            # set tableView on item
            if view == "central":
                self.tableView.scrollTo(index)
                self.tableView.setCurrentIndex(index)
            # elif view == "vertical":
            #   headerView = self.tableView.verticalHeader()
            #   headerView.scrollTo(index, QtWidgets.QAbstractItemView.PositionAtTop)
            #   headerView.setCurrentIndex(index)

    def show_rows(self, text: str, matchFlags: QtCore.Qt.MatchFlags = QtCore.Qt.MatchContains):
        """если нужно менять view."""
        # map(self.tableView.showRow, range(self.tableModel.rowCount()))
        if not text:  # если поле ввода пустое
            self.logger.debug(f"show_rows: {text}")
            for r in range(self.tableModel.rowCount()):
                self.tableView.showRow(r)
            return
        self.tableModel.searchElement(text, matchFlags)
        it, indexes = self.tableModel.searchIters.get(text, (None, None))
        # hide all indexes except found
        if indexes:
            rows = [index.row() for index, view in indexes]
            for r in range(self.tableModel.rowCount()):
                if r not in rows:
                    self.tableView.hideRow(r)
                else:
                    self.tableView.showRow(r)
        else:
            for r in range(self.tableModel.rowCount()):
                self.tableView.hideRow(r)

    def search_text(self, text: str):
        try:
            self.logger.debug("searching")
            self.show_rows(text)
            # self.iterate_over_items(text)

        except BaseException:
            exctype, value, exctb = sys.exc_info()
            self.logger.exception(value)
            self.ErrorDialog.setText(traceback.format_exc())
            self.ErrorDialog.show()


class NotEditableDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate for not editable referal language column."""

    def __init__(self, parent: QtWidgets.QTableView = None):
        super().__init__(parent)
        self.triggers = parent.editTriggers()

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        pass


class TableViewDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate for other items (except those in ref column see above)"""

    def __init__(self, tab: EditTab, parent: QtWidgets.QTableView = None):
        super().__init__(parent)
        self.triggers = parent.editTriggers()
        self.tab = tab
        self.data_before_edit = ""

    def editorEvent(self, event: QtCore.QEvent,
                    model: QtCore.QAbstractItemModel,
                    option: 'QtWidgets.QStyleOptionViewItem',
                    index: QtCore.QModelIndex) -> bool:
        self.tab.logger.debug("start editing")

        return super().editorEvent(event, model, option, index)

    def find_similar(self, model: JSONModel, index: QtCore.QModelIndex) -> list:
        item = model.itemFromIndex(index)
        data_all = []
        for i in range(model.rowCount()):
            if i == item.row():
                continue
            ref_item = model.item(item.row(), 0)
            ref_i = model.item(i, 0)
            target_item = model.item(i, item.column())
            if ref_item.text() == ref_i.text() and target_item.text() != item.text():
                data_all.append((target_item.index(), target_item.index().data(), index.data()))
                # model.setData(target_item.index(), index.data())
        return data_all

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        self.data_before_edit = index.data()  # save data before edition
        self.tab.logger.debug("set editor data")
        return super().setEditorData(editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        try:
            self.tab.logger.debug("set model data")
            if isinstance(model, JSONModel):
                # чистим поисковые запросы (итераторы)
                # можно попробовать чистить только там,где изменилось
                model.searchIters.clear()
                # забираем то, что в editor
                user_property = editor.metaObject().userProperty()
                data = editor.property(user_property.name())  # здесь лежит то, что попадет в item
                self.tab.logger.debug(data)
                data_all = [(index, self.data_before_edit, data)]
                model.setData(index, data)
                similar_items = self.find_similar(model, index)
                if similar_items:
                    pressedButton = QtWidgets.QMessageBox.question(
                        self.tab, self.tab.tr("Одинаковый текст"),
                        self.tab.tr("Такой текст встречается еще в нескольких местах. Перевести везде одинаково?"),
                        defaultButton=QtWidgets.QMessageBox.Yes)
                    if pressedButton == QtWidgets.QMessageBox.Yes:
                        data_all.extend(similar_items)
                self.tab.logger.debug(data_all)
                self.tab.undoStack.push(EditCommand(model, data_all))
        except Exception as e:
            self.tab.logger.exception(e)


class BrowseTab(QtWidgets.QWidget):
    def __init__(self, name, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__()
        _translate = QtCore.QCoreApplication.translate
        self.setObjectName("tab_" + name)
        self.tabLayout = QtWidgets.QVBoxLayout(self)
        self.tabLayout.setObjectName("tabLayout")
        self.textBrowser = QtWidgets.QTextBrowser(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setObjectName("textBrowser")
        self.tabLayout.addWidget(self.textBrowser)


class TranslateCommand(QtWidgets.QUndoCommand):
    """"""

    def __init__(self, service: str, tab: EditTab, parent: QtWidgets.QUndoCommand = None):
        super().__init__(parent)
        indexes = tab.tableView.selectedIndexes()
        compiler = tab.compiler
        service = service

        self.items = []
        for index in indexes:
            item = tab.tableModel.itemFromIndex(index)
            ref_item = tab.tableModel.item(index.row(), 0)
            translation = compiler.translate(ref_item.text(), item.lang, service=service)
            self.items.append((item, item.text(), translation))
            item.setText(translation)

    def undo(self) -> None:
        for item, text, _ in self.items:
            item.setText(text)

    def redo(self) -> None:
        for item, _, translation in self.items:
            item.setText(translation)


class ClearCommand(QtWidgets.QUndoCommand):
    """'Clear' text in selected items."""

    def __init__(self, tab: EditTab, parent: QtWidgets.QUndoCommand = None):
        super().__init__(parent)
        indexes = tab.tableView.selectedIndexes()
        model = tab.tableModel
        self.items = []
        for index in indexes:
            item = model.itemFromIndex(index)
            self.items.append((item, item.text()))
            item.setText("")

    def undo(self) -> None:
        for item, text in self.items:
            item.setText(text)

    def redo(self) -> None:
        for item, _ in self.items:
            item.setText("")


class PasteCommand(QtWidgets.QUndoCommand):
    """'Paste' data to current index #todo: check it is the same as current
    selected."""

    def __init__(self, tab: EditTab, clipboard: QtGui.QClipboard, parent: QtWidgets.QUndoCommand = None):
        super().__init__(parent)
        self.model = tab.tableModel
        self.index = tab.tableView.currentIndex()
        self.old = QtCore.QMimeData()
        self.window = tab
        if self.index:
            mimeData = clipboard.mimeData()
            self.mimeData = QtCore.QMimeData()
            if mimeData.hasImage():
                self.old.setImageData(self.model.data(self.index, QtCore.Qt.BackgroundRole))
                pixmap = QtGui.QPixmap(mimeData.imageData())
                self.mimeData.setImageData(pixmap)
                self.model.setData(self.index, pixmap, QtCore.Qt.BackgroundRole)
            elif mimeData.hasHtml():
                self.old.setHtml(self.model.data(self.index, QtCore.Qt.DisplayRole))
                self.mimeData.setHtml(mimeData.html())
                self.model.setData(self.index, mimeData.html(), QtCore.Qt.DisplayRole)
            elif mimeData.hasText():
                self.old.setText(self.model.data(self.index, QtCore.Qt.EditRole))
                self.mimeData.setText(mimeData.text())
                self.model.setData(self.index, mimeData.text())
            else:
                self.old.setText(self.model.data(self.index, QtCore.Qt.EditRole))
                self.model.setData(self.index, self.window.tr("Не могу отобразить"))

    def undo(self) -> None:
        if self.index:
            if self.old.hasImage():
                pixmap = QtGui.QPixmap(self.old.imageData())
                self.model.setData(self.index, pixmap, QtCore.Qt.BackgroundRole)
            elif self.old.hasHtml():
                self.model.setData(self.index, self.old.html(), QtCore.Qt.DisplayRole)
            elif self.old.hasText():
                self.model.setData(self.index, self.old.text())
            else:
                self.model.setData(self.index, self.window.tr("Не могу отобразить"))

    def redo(self) -> None:
        if self.index:
            if self.mimeData.hasImage():
                pixmap = QtGui.QPixmap(self.mimeData.imageData())
                self.model.setData(self.index, pixmap, QtCore.Qt.BackgroundRole)
            elif self.mimeData.hasHtml():
                self.model.setData(self.index, self.mimeData.html(), QtCore.Qt.DisplayRole)
                # setTextFormat(QtCore.Qt.RichText)
            elif self.mimeData.hasText():
                self.model.setData(self.index, self.mimeData.text())
            else:
                self.model.setData(self.index, self.window.tr("Не могу отобразить"))
