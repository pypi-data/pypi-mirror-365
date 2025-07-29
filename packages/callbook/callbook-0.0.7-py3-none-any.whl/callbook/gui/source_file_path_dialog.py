from PyQt5 import QtWidgets, uic
from pathlib import Path
import os
from importlib.resources import files


class SourceFilePathDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uifile = files('callbook').joinpath('gui', 'source_file_path_dialog.ui')
        uic.loadUi(uifile, self)
        self.setFixedSize(self.width(), self.height())
        source_path = os.environ.get('_NT_SOURCE_PATH')
        if source_path:
            self.plainTextEdit.setPlainText(source_path)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def accept(self):
        os.environ['_NT_SOURCE_PATH'] = self.plainTextEdit.toPlainText()
        super().accept()