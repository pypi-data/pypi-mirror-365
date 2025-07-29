from callbook.call import Call, FunctionData, CallData
from callbook.database import Database
from PyQt5.Qt import QStandardItem, QIcon
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QItemSelection
from importlib.resources import files


class StandardItem(QStandardItem):
    def __init__(self, txt=''):
        super().__init__()
        self.setEditable(False)
        self.setText(txt)
        self.id = 0
        self.callData: CallData = None

    @property
    def functionData(self) -> FunctionData:
        if not self.callData:
            return None
        return self.callData.func

    def functionName(self):
        arr = self.text().split('*')
        return arr[0].rstrip()


class Document(QObject):
    contentChanged = pyqtSignal()
    curItemChanged = pyqtSignal(StandardItem)
    commentChanged = pyqtSignal(str)
    annotationChanged = pyqtSignal(int, str)

    def __init__(self, filename: str, rootNode: StandardItem) -> None:
        super(Document, self).__init__()
        self.tempdir = None
        self.filename = filename
        self.rootNode = rootNode
        self.isDirty = False
        self.curItem: StandardItem = rootNode
        self.database: Database = None
        self.call: Call = None
        comment_path = files('callbook').joinpath('image/comment.png')
        self.comment_icon = QIcon(str(comment_path))

    def open(self):
        self.database = Database(self.filename)
        self.call = self.database.load_call()

    def close(self):
        if self.database:
            if self.isDirty:
                self.save()
            self.database = None
            self.call = None

    def get_source(self, functionData: FunctionData) -> str:
        """
        Read the source code from the document
        """
        if functionData.source:
            return functionData.source

        source = ''
        try:
            source = functionData.content()  # 从源代码读入数据
            functionData.source = source
        except:
            pass

        return source

    def get_annotations(self, functionData: FunctionData) -> dict:
        """
        Read the annotation from the document
        """
        return functionData.annotations if functionData.annotations else {}

    def get_comment(self, functionData: FunctionData) -> str:
        """
        Read the comment from the document
        """
        return functionData.comment if functionData.comment else ''

    def fill_tree(self) -> None:
        """从 self.call 树形结构填充 QStandardItem 树"""
        def add_node(call_node: Call, parent_item: StandardItem):
            node = StandardItem(call_node.data.func.name)
            node.id = call_node.get_id()
            node.callData = call_node.data

            # 如果有注释或标注，显示注释图标
            if call_node.function.comment or call_node.function.annotations:
                node.setIcon(self.comment_icon)

            parent_item.appendRow(node)

            # 递归处理所有子节点
            for child in call_node.subcalls:
                add_node(child, node)

        # 从根节点开始构建树
        for root_call in self.call.subcalls:
            add_node(root_call, self.rootNode)

    def save(self) -> None:
        if not self.database:
            raise Exception("No database to save.")

        self.database.save_call(self.call)
        self.isDirty = False  # 文件保存后重新设置标记
        self.contentChanged.emit()

    def save_as(self, filename: str):
        self.filename = filename
        self.save()

    @pyqtSlot(str)
    def on_comment_changed(self, comment: str):
        if not hasattr(self.curItem, 'functionData'):
            return

        if not self.curItem.functionData:
            return

        if self.curItem.functionData.comment != comment:
            self.curItem.functionData.comment = comment
            if not comment:
                self.curItem.functionData.comment_delete_flag = True
            self.commentChanged.emit(comment)
            self.isDirty = True
            self.contentChanged.emit()

    @pyqtSlot(str)
    def on_source_changed(self, source: str):
        if not hasattr(self.curItem, 'functionData'):
            return

        if not self.curItem.functionData:
            return
        
        normalized_source = source.replace("\r\n", "\n").replace("\r", "\n")

        self.curItem.functionData.source = normalized_source
        self.isDirty = True
        self.contentChanged.emit()

    @pyqtSlot()
    def on_callstack_changed(self):
        if not hasattr(self.curItem, 'functionData'):
            return

        if not self.curItem.functionData:
            return

        self.isDirty = True
        self.contentChanged.emit()

    @pyqtSlot(int, str)
    def on_annotation_changed(self, line: int, comment: str):
        if not hasattr(self.curItem, 'functionData'):
            return

        if not self.curItem.functionData:
            return

        annotations = self.curItem.functionData.annotations

        if not comment:
            if line in annotations:
                del annotations[line]
                self.isDirty = True
                if not annotations:
                    self.curItem.functionData.annotations_delete_flag = True
        elif line in annotations and annotations[line] == comment:
            pass
        else:
            annotations[line] = comment
            self.isDirty = True

        self.annotationChanged.emit(line, comment)

        if self.isDirty:
            self.contentChanged.emit()

    @pyqtSlot(QItemSelection, QItemSelection)
    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        " Slot is called when the selection has been changed "
        if not selected.indexes():
            return

        selectedIndex = selected.indexes()[0]
        self.curItem = selectedIndex.model().itemFromIndex(selectedIndex)
        self.curItemChanged.emit(self.curItem)

    def get_cur_item(self) -> StandardItem:
        return self.curItem
