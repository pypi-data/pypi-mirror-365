from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QIcon, QColor
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QLabel, QToolButton
from PyQt5.Qsci import QsciScintilla, QsciScintillaBase
from functools import partial
from pathlib import Path
from PyQt5.QtCore import pyqtSignal
from importlib.resources import files


class SearchEdit(QLineEdit):
    buttonToggled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.button_match_case = self._add_button(
            'case-sensitive.svg', 'Match Case')
        self.button_whole_word = self._add_button(
            'whole-word.svg', 'Match Whole Word')
        self.button_regex = self._add_button(
            'regex.svg', 'Use Regular Expression')

        layout = QHBoxLayout(self)
        layout.addStretch(1)
        layout.addWidget(self.button_match_case, 0)
        layout.addWidget(self.button_whole_word, 0)
        layout.addWidget(self.button_regex, 0)

        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

    def _add_button(self, image_name: str, tooltip: str) -> QToolButton:
        button = QToolButton(self)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        icon_path = files('callbook').joinpath('image', image_name)
        button.setIcon(QIcon(str(icon_path)))
        button.setToolTip(tooltip)
        button.setCheckable(True)
        button.setStyleSheet(
            "QToolButton { background: transparent; border: none; } "
            "QToolButton:checked { background: skyblue; border: 1px solid #8f8f91; border-radius: 4px;}")
        button.toggled.connect(lambda: self.buttonToggled.emit())
        return button

    @property
    def match_case(self) -> bool:
        return self.button_match_case.isChecked()

    @property
    def match_whole_word(self) -> bool:
        return self.button_whole_word.isChecked()

    @property
    def regex(self) -> bool:
        return self.button_regex.isChecked()


class SearchWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_WState_Hidden)

        # https://web.archive.org/web/20130613105442/http://blog.qt.digia.com/blog/2007/06/06/lineedit-with-a-clear-button#/
        # https://stackoverflow.com/questions/12462562/how-to-insert-a-button-inside-a-qlineedit#/
        self.edit = SearchEdit()
        self.edit.setFixedWidth(300)
        self.edit.setPlaceholderText("Find")
        self.edit.buttonToggled.connect(self.on_toggled)

        self.edit.textChanged.connect(self.on_text_changed)

        self.label = QLabel("No results")
        self.label.setMinimumWidth(80)

        up_btn = self._add_button("arrow-up.svg", "Previous Match")
        up_btn.clicked.connect(partial(self.search, False))
        down_btn = self._add_button("arrow-down.svg", "Next Match")
        down_btn.clicked.connect(partial(self.search, True))
        close_btn = self._add_button("close.svg", "Close")
        close_btn.clicked.connect(self.hide)

        layout = QHBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.label)
        layout.addWidget(up_btn)
        layout.addWidget(down_btn)
        layout.addWidget(close_btn)
        layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        self.positions: list[tuple] = []

        parent.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE,
                           1, QsciScintilla.INDIC_ROUNDBOX)
        parent.SendScintilla(QsciScintilla.SCI_INDICSETFORE,
                           1, QColor(Qt.GlobalColor.red))

    def _add_button(self, image_name: str, tooltip: str) -> QToolButton:
        button = QToolButton(self)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        icon_path = files('callbook').joinpath('image', image_name)
        button.setIcon(QIcon(str(icon_path)))
        button.setToolTip(tooltip)
        button.setStyleSheet("QToolButton { background: transparent; border: none; } "
                             "QToolButton:hover { background: lightgray; border-radius: 4px;}")
        return button

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.black, 1, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(self.rect())

    def moveEvent(self, event):
        self.update_position()

    def update_position(self):
        if self.parentWidget():
            # Get the geometry of the parent window
            parent_rect = self.parentWidget().geometry()
            # Set the position of the child window to the top-right corner of the parent window
            self.move(parent_rect.right() - self.width() -
                      20, parent_rect.top() + 1)

    def search(self, forward: bool):
        # https://blog.csdn.net/cy19890616/article/details/135066162#/
        parent: QsciScintilla = self.parent()

        if forward:
            line, index = parent.getSelection()[2:]
        else:
            line, index = parent.getSelection()[:2]

        parent.findFirst(self.edit.text(),
                         self.edit.regex,
                         self.edit.match_case,
                         self.edit.match_whole_word,
                         True,
                         forward, line, index)

        # Set label
        self.set_label()

    def on_text_changed(self, txt: str):
        parent: QsciScintilla = self.parent()
        # Clear previous indicators
        parent.clear_indicators(1)

        # Set indicators
        self.positions = parent.get_matched_position(txt,
                                                     self.edit.match_whole_word,
                                                     self.edit.match_case,
                                                     self.edit.regex)
        parent.create_indicators(1, self.positions)

        line, index = parent.getCursorPosition()
        for pos_line, pos_index, len in self.positions:            
            # The cursor is probably in the middle of the search word,
            # We need to highlight the word with the cursor first. It is
            # the reason we need to adjust the index value.
            if pos_line == line and index > pos_index and index <= pos_index + len:
                index = pos_index

        # Find the first match
        parent.findFirst(self.edit.text(),
                         self.edit.regex,
                         self.edit.match_case,
                         self.edit.match_whole_word,
                         True,
                         True, line, index)

        # Set label
        self.set_label()

    def get_current_position_index(self):
        parent: QsciScintilla = self.parent()
        s = parent.getSelection()
        index = -1
        for idx, pos in enumerate(self.positions):
            if pos[:2] == s[:2]:
                index = idx
                break
        return index
    
    def set_label(self):
        current_pos = self.get_current_position_index()
        if current_pos < 0:
            self.label.setText('No results')
        else:
            self.label.setText(f'{current_pos + 1} of {len(self.positions)}')

    def on_toggled(self):
        txt = self.edit.text()
        self.on_text_changed(txt)

    def show(self) -> None:
        parent: QsciScintilla = self.parent()
        s = parent.get_word_under_cursor()
        if s:
            if s != self.edit.text():
                self.edit.setText(s)
            else:
                # if the search text is not changed, the on_text_changed
                # won't be called.
                self.on_text_changed(s)
            self.edit.selectAll()
            self.edit.setFocus()
        return super().show()
    
    def hide(self) -> None:
        parent: QsciScintilla = self.parent()
        parent.clear_indicators(1)
        pos = parent.getCursorPosition()
        parent.SendScintilla(QsciScintillaBase.SCI_CLEARSELECTIONS)
        parent.setCursorPosition(*pos)
        return super().hide()
