from functools import lru_cache
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot, QModelIndex
from ApcLogger import getLogger
from ApcWorkObj import ApcCompiler


class MyItem(QtGui.QStandardItem):
    def __init__(self, text: str, option: dict, lang: str):
        super().__init__(text)
        self.setToolTip(text)
        self.option = option
        self.lang = lang

    def update(self):
        self.option[self.lang] = self.text()
        self.setToolTip(self.text())

    def type(self) -> int:
        return QtGui.QStandardItem.UserType + 1


class JSONModel(QtGui.QStandardItemModel):
    logger = getLogger("JSONModel")

    def __init__(self, *args):
        super().__init__(*args)
        self.itemChanged.connect(self.on_item_changed)
        self.sections = None
        self.headers = None
        self.main_header = None
        self.searchIters = dict()

    def import_resources(self, compiler: ApcCompiler):
        sections = compiler.JSON_editor.sections
        headers = {lang: compiler.languages[lang] for lang in compiler.json_langs}
        main_header = compiler.main_lang
        mark = compiler.auto_tr_ch
        self.clear()
        try:
            if sections:
                self.sections = sections
                self.headers = headers
                self.main_header = main_header
                json_repr = sections.get("RESOURCES")
                self.setColumnCount(len(headers))
                langs = []
                if main_header in headers:
                    item = MyItem(headers[main_header], headers, main_header)
                    self.setHorizontalHeaderItem(0, item)
                    item.setBackground(QtGui.QColor(204, 204, 255, 204))
                    index = 1
                    langs.append(main_header)
                    for l in set(headers) - {main_header}:
                        item = MyItem(headers[l], headers, l)
                        self.setHorizontalHeaderItem(index, item)
                        langs.append(l)
                        index += 1
                # s = set()
                if not json_repr:
                    return
                index = 0
                for obj in json_repr:
                    dObj = json_repr[obj]
                    for section in dObj:
                        dOptions = dObj[section]
                        for option in dOptions:
                            row = []
                            for l in langs:
                                self.logger.debug("dOptions:%s", str(dOptions))
                                translation = dOptions[option][l]
                                item = MyItem(translation, dOptions[option], l)
                                if str(translation).startswith(mark):
                                    item.setText(translation[len(mark):])
                                    item.setBackground(QtGui.QColor(120, 186, 0, 60))
                                    item.setForeground(QtGui.QColor(0, 30, 78))
                                row.append(item)

                            item = QtGui.QStandardItem(f"{index + 1}.{option}")
                            item.setToolTip(option)
                            self.appendRow(row)
                            self.setVerticalHeaderItem(index, item)
                            index += 1

        except Exception as e:
            self.logger.exception(e)

    # def save_resourses(self, compiler: ApcCompiler):
    #     sections = compiler.JSON_editor.sections
    #     headers = {lang: compiler.languages[lang] for lang in compiler.json_langs}
    #     main_header = compiler.main_lang
    #     mark = compiler.auto_tr_ch
    #     try:
    #         if sections:
    #             self.sections = sections
    #             self.headers = headers
    #             self.main_header = main_header
    #             json_repr = sections.get("RESOURCES")
    #             self.setColumnCount(len(headers))
    #             langs = []
    #             if main_header in headers:
    #                 item = MyItem(headers[main_header], headers, main_header)
    #                 self.setHorizontalHeaderItem(0, item)
    #                 item.setBackground(QtGui.QColor(204, 204, 255, 204))
    #                 index = 1
    #                 langs.append(main_header)
    #                 for l in set(headers) - {main_header}:
    #                     item = MyItem(headers[l], headers, l)
    #                     self.setHorizontalHeaderItem(index, item)
    #                     langs.append(l)
    #                     index += 1
    #             # s = set()
    #             if not json_repr:
    #                 return
    #             index = 0
    #             for obj in json_repr:
    #                 dObj = json_repr[obj]
    #                 for section in dObj:
    #                     dOptions = dObj[section]
    #                     for option in dOptions:
    #                         row = []
    #                         for l in langs:
    #                             self.logger.debug("dOptions:%s", str(dOptions))
    #                             translation = dOptions[option][l]
    #                             item = MyItem(translation, dOptions[option], l)
    #                             if str(translation).startswith(mark):
    #                                 item.setText(translation[len(mark):])
    #                                 item.setBackground(QtGui.QColor(120, 186, 0, 60))
    #                                 item.setForeground(QtGui.QColor(0, 30, 78))
    #                             row.append(item)
    #
    #                         item = QtGui.QStandardItem(f"{index + 1}.{option}")
    #                         item.setToolTip(option)
    #                         self.appendRow(row)
    #                         self.setVerticalHeaderItem(index, item)
    #                         index += 1
    #
    #     except Exception as e:
    #         self.logger.exception(e)

    @lru_cache(maxsize=20)
    def getLangColumn(self, lang):
        for c in range(self.columnCount()):
            item = self.takeHorizontalHeaderItem(c)
            if item.text() == self.headers[lang]:
                return c
        return -1

    @pyqtSlot(QtGui.QStandardItem, name="on_item_changed")
    def on_item_changed(self, item: MyItem):
        try:
            self.logger.debug("Changed: %s,%s,%s", item.text(), item.row(), item.column())
            # item.setBackground(QtGui.QColor(38, 115, 236, 60))
            item.update()
        except Exception as e:
            self.logger.exception(e)

    def searchElement(self, text: str, matchFlags) -> (QModelIndex, str):
        # find elems which matches given text
        index = None
        view = None
        self.logger.debug("iterate_over_items")
        searchIter, items = self.searchIters.get(text, (None, None))
        if not items:  # если такого еще не было
            items = self.find_items_with_text(text, matchFlags)  # возвращается список
            self.logger.debug(items)
            if not items:  # ничего не нашли
                self.logger.debug(f"nothing found with {text}")
                return index, view
            searchIter = iter(items)  # создаем новый итератор
            self.searchIters[text] = [searchIter, items]
        try:
            index, view = next(searchIter)
            if view == "central":
                item = self.itemFromIndex(index)
                self.logger.debug(f"r: {item.row()}, c:{item.column()}, text: {item.text()}")

        except StopIteration:  # закончился итератор
            searchIter = iter(items)  # создаем новый
            self.logger.debug(f"new iter")
            index, view = next(searchIter)
            if view == "central":
                item = self.itemFromIndex(index)
                self.logger.debug(f"r: {item.row()}, c:{item.column()}, text: {item.text()}")
            self.searchIters[text][0] = searchIter
        return index, view

    def find_items_with_text(self, text: str, matchFlags) -> list:
        items = []
        try:
            for i in range(self.columnCount()):
                items.extend([(elem, "central") for elem in
                              map(lambda elem: self.indexFromItem(elem), self.findItems(text, matchFlags, i))])
            # items.extend(  # indexes from verticalHeader
            #   (
            #     (self.verticalHeaderItem(i).index(), "vertical") for i in range(self.rowCount())
            #     if re.search(text, self.verticalHeaderItem(i).text())
            #   )
            # )
            self.logger.debug(items)
        except Exception as e:
            self.logger.exception(e)
        finally:
            return items


class EditCommand(QtWidgets.QUndoCommand):
    def __init__(self, model: QtGui.QStandardItemModel, data: list, parent: QtWidgets.QUndoCommand = None):
        super().__init__(parent)
        self.data = data
        self.model = model

    def undo(self) -> None:
        for index, old, _ in self.data:
            self.model.setData(index, old)

    def redo(self) -> None:
        for index, _, new in self.data:
            self.model.setData(index, new)
