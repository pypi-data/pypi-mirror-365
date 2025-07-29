from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QMenu, QTreeView
from PyQt5.QtGui import QStandardItemModel, QFont, QColor
from PyQt5.Qt import QIcon
from callbook.call import FunctionData
from .Document import StandardItem, Document
from pathlib import Path
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from importlib.resources import files


class CallStackView(QTreeView):
    callStackChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._rightClickMenu)
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.ContiguousSelection)
        self.setModel(QStandardItemModel())
        self.document = None
        self.bStyleSheetNone = False
        font = QFont('Inconsolata')
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)

        comment_path = files('callbook').joinpath('image/comment.png')
        self.comment_icon = QIcon(str(comment_path))

    def setDocument(self, document: Document):
        self.document = document
        self.callStackChanged.connect(document.on_callstack_changed)
        self.selectionModel().selectionChanged.connect(document.on_selection_changed)

    def clear(self):
        self.model().beginResetModel()
        rowCount = self.model().rowCount()
        for i in range(rowCount):
            self.model().removeRow(0)
        self.model().endResetModel()

    def _rightClickMenu(self, pos) -> None:
        try:
            self.contextMenu = QMenu(self)

            indexes = self.selectedIndexes()
            if len(indexes) > 0:
                self.contextMenu.addAction('复制').triggered.connect(self._copy)
                self.contextMenu.addAction(
                    '复制路径').triggered.connect(self._copyPath)
                self.contextMenu.addAction(
                    '删除').triggered.connect(self._delete)
                self.contextMenu.addSeparator()

            self.contextMenu.addAction(
                '样式切换').triggered.connect(self._styleSheetChange)
            self.contextMenu.addAction(
                '全部展开').triggered.connect(self.expandAll)

            arr = ['一级展开', '二级展开', '三级展开', '四级展开']
            def foo(i): return lambda: self.expandToDepth(i)
            for i, mi in enumerate(arr):
                self.contextMenu.addAction(mi).triggered.connect(foo(i))

            self.contextMenu.addAction(
                '循环识别').triggered.connect(self._loopMatch)

            self.contextMenu.exec_(self.mapToGlobal(pos))
        except Exception as e:
            print(e)

    def _copy(self) -> None:
        names = []
        for index in self.selectedIndexes():
            item = index.model().itemFromIndex(index)
            names.append(item.text())

        clipboard = QApplication.clipboard()
        clipboard.setText('\n'.join(names))

    def _delete(self) -> None:
        while self.selectedIndexes():
            idx = self.selectedIndexes()[0]
            self.model().removeRow(idx.row(), idx.parent())
        self.callStackChanged.emit()

    def _copyPath(self) -> None:
        index = self.selectedIndexes()[0]
        item: StandardItem = index.model().itemFromIndex(index)
        if not item.functionData:
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(item.functionData.filename)

    def _styleSheetChange(self) -> None:
        if self.bStyleSheetNone:
            self.setStyleSheet(
                "QTreeView::branch: {border-image: url(:/vline.png);}")
        else:
            self.setStyleSheet(
                "QTreeView::branch {border-image: url(none.png);}")

        self.bStyleSheetNone = not self.bStyleSheetNone

    def _loopMatch(self):
        model = self.model()
        rootNode = model.invisibleRootItem()
        queue = []
        queue.append(rootNode)
        nCount = 0
        while (queue):
            elem = queue.pop(0)
            nCount += 1
            preChild = None
            row = 0
            while row < elem.rowCount():
                child = elem.child(row, 0)
                if row > 0 and preChild.functionName() == child.text():
                    elem.removeRow(row)
                    preChild.increaseCount()
                else:
                    row += 1
                    preChild = child
                    queue.append(child)

    def iterItems(self):
        # https://stackoverflow.com/questions/41949370/collect-all-items-in-qtreeview-recursively
        def recurse(parent):
            for row in range(parent.rowCount()):
                for column in range(parent.columnCount()):
                    child = parent.child(row, column)
                    yield child
                    if child.hasChildren():
                        yield from recurse(child)

        model = self.model()
        root = model.invisibleRootItem()
        if root is not None:
            yield from recurse(root)

    def getSameItems(self, startOffset: int) -> list[StandardItem]:
        arr = []
        for node in self.iterItems():
            if node.functionData.start_offset == startOffset:
                arr.append(node)

        return arr

    def getCurrentFunctionData(self) -> FunctionData:
        indexes = self.selectedIndexes()
        if len(indexes) == 0:
            return None

        index = self.selectedIndexes()[0]
        item: StandardItem = index.model().itemFromIndex(index)
        return item.functionData

    @pyqtSlot(str)
    def on_comment_changed(self, comment: str):
        functionData = self.getCurrentFunctionData()
        if not functionData:
            return
        
        if functionData.annotations:
            return

        items = self.getSameItems(functionData.start_offset)  # 修改属性名从startOffset为start_offset
        for item in items:
            icon = self.comment_icon if comment else QIcon()
            item.setIcon(icon)

    def on_annotation_changed(self, line: int, comment: str):
        functionData = self.getCurrentFunctionData()
        if not functionData:
            return
        
        if functionData.comment:
            return

        items = self.getSameItems(functionData.start_offset)
        for item in items:
            icon = self.comment_icon if functionData.annotations else QIcon()
            item.setIcon(icon)

    def search(self, text: str) -> None:
        for node in self.iterItems():
            if text and text.lower() in node.functionData.name.lower():
                node.setData(QColor(255, 255, 0), Qt.BackgroundRole)
            else:
                node.setData(QColor(255, 255, 255) , Qt.BackgroundRole)
