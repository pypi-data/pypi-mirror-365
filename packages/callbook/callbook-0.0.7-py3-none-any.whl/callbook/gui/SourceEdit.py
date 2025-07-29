from PyQt5.QtGui import QFont, QFontMetrics, QColor, QCursor, QKeyEvent, QResizeEvent, QKeySequence
from .Document import StandardItem, Document
from .search_window import SearchWindow
from PyQt5.Qsci import QsciScintilla, QsciLexerCPP
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QDialog, QWidget, QDialogButtonBox, QVBoxLayout, QPlainTextEdit, QPushButton, QShortcut, QMenu
import re


class AnnotationDialog(QDialog):
    CustomDeleteStatus = 100

    def __init__(self, parent: QWidget = None, txt: str = '') -> None:
        super().__init__(parent)
        self.setWindowTitle("Annotation")

        font = QFont('Inconsolata')
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        buttonDelete = QPushButton('Delete')
        self.buttonBox.addButton(
            buttonDelete, QDialogButtonBox.ButtonRole.ActionRole)
        buttonDelete.clicked.connect(self.custom_delete)

        self.layout = QVBoxLayout()
        self.edit = QPlainTextEdit()
        self.edit.setPlainText(txt)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.resize(800, 600)
        self.setWindowOpacity(0.9)
        pos = QCursor.pos()
        self.move(pos)

    def custom_delete(self):
        self.done(self.CustomDeleteStatus)


class SourceEdit(QsciScintilla):
    clicked = pyqtSignal()
    sourceChanged = pyqtSignal(str)
    annotationChanged = pyqtSignal(int, str)
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None):
        super(SourceEdit, self).__init__(parent)

        # Set the default font
        font = QFont()
        font.setFamily('Inconsolata')  # Courier
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setUtf8(True)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        # self.setCaretLineVisible(True)
        # self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

        # Set CPP lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        #
        lexer = QsciLexerCPP()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow, self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("#ee1111"), self.ARROW_MARKER_NUM)
        self.setAnnotationDisplay(
            QsciScintilla.AnnotationDisplay.AnnotationBoxed)
        self.SendScintilla(self.SCI_STYLESETBACK,
                           QsciScintilla.STYLE_CALLTIP, QColor(255, 255, 204))

        # Indentation
        #
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setTabIndents(True)
        self.setAutoIndent(True)

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # not too small
        self.setMinimumSize(600, 450)
        self.textChanged.connect(self.onTextChanged)
        self.isItemChanged = False

        self.search_window = SearchWindow(self)
        key = QKeySequence(Qt.CTRL + Qt.Key_F)
        shortcut = QShortcut(key, self)
        shortcut.activated.connect(lambda: self.search_window.show())

        self.clicked.connect(self.on_clicked)
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE,
                           0, QsciScintilla.INDIC_ROUNDBOX)
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE,
                           0, QColor(Qt.GlobalColor.black))
        
        # Marker number for line highlight
        self.line_marker = 1

        # Define marker with background color (using an opaque background color)
        self.markerDefine(QsciScintilla.Background, self.line_marker)
        self.setMarkerBackgroundColor(QColor("#FFFF00"), self.line_marker)  # Yellow highlight

         # Enable custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.current_item: StandardItem = None

    def highlight_line(self, line_number):
        """Highlights a specific line."""
        # Clear all previous markers of this type
        self.markerDeleteAll(self.line_marker)
        
        # Add the new marker to the specified line
        self.markerAdd(line_number, self.line_marker)

    def show_context_menu(self, position):
        """Shows the custom context menu."""
        context_menu = QMenu(self)

        # Add action to highlight the current line
        highlight_action = context_menu.addAction("Highlight Current Line")
        highlight_action.triggered.connect(self.highlight_current_line)

        # Show the context menu at the requested position
        context_menu.exec_(self.mapToGlobal(position))

    def highlight_current_line(self):
        """Highlights the line where the cursor is currently located."""
        # Get the current cursor position (line and column)
        line_number, _ = self.getCursorPosition()

        # Highlight the current line
        self.highlight_line(line_number)

        function_data = self.current_item.functionData
        self.current_item.lineNumber = function_data.startLineNumber + line_number - 1
        # TODO: 目前没有序列化

    def setDocument(self, doc: Document):
        self.document: Document = doc
        self.document.curItemChanged.connect(self.onCurItemChanged)
        self.sourceChanged.connect(doc.on_source_changed)
        self.annotationChanged.connect(doc.on_annotation_changed)

    def onCurItemChanged(self, item: StandardItem) -> None:
        self.isItemChanged = True
        content = self.document.get_source(item.functionData)
        self.setText(content)
        self.isItemChanged = False
        annotations = self.document.get_annotations(item.functionData)
        self.current_item = item
        for k, v in annotations.items():
            self.annotate(k, v, QsciScintilla.STYLE_CALLTIP)
            self.markerAdd(k, self.ARROW_MARKER_NUM)

        if item.callData.line_number != 0:
            line_number = item.callData.line_number - item.functionData.start_line_number + 1
            self.highlight_line(line_number)

    def onTextChanged(self) -> None:
        if self.isItemChanged:
            return

        self.sourceChanged.emit(self.text())

    def annotation(self, nline) -> str:
        # There is a bug in the following cpp method
        # QString QsciScintilla::annotation(int line) const
        # So its parent implementation self.annotation(nline) won't return correct value
        # This method is an reimplementation of the method QsciScintilla::annotation
        size = self.SendScintilla(self.SCI_ANNOTATIONGETTEXT, nline, 0)
        buf = bytearray(size)
        self.SendScintilla(self.SCI_ANNOTATIONGETTEXT, nline, buf)
        string = buf.decode('utf-8')
        return string

    def on_margin_clicked(self, nmargin, nline, modifiers):
        txt = ''
        if self.markersAtLine(nline) != 0:
            txt = self.annotation(nline)

        dlg = AnnotationDialog(self, txt)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            new_txt = dlg.edit.toPlainText()
            if new_txt == txt:
                return

            if new_txt:
                self.annotate(nline, new_txt, QsciScintilla.STYLE_CALLTIP)
                self.markerAdd(nline, self.ARROW_MARKER_NUM)
                self.annotationChanged.emit(nline, new_txt)
            else:
                self.clearAnnotations(nline)
                self.markerDelete(nline, self.ARROW_MARKER_NUM)
                self.annotationChanged.emit(nline, '')

        elif result == AnnotationDialog.CustomDeleteStatus:
            self.clearAnnotations(nline)
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
            self.annotationChanged.emit(nline, '')

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        self.search_window.update_position()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key.Key_Escape:
            self.search_window.hide()
        return super().keyPressEvent(e)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()

    def on_clicked(self):
        self.clear_indicators(0)
        word = self.get_word_under_cursor()
        positions = self.get_matched_position(word, True, False, False)
        self.create_indicators(0, positions)

    def get_word_under_cursor(self):
        pos = self.getCursorPosition()
        word = self.wordAtLineIndex(*pos)
        return word

    def get_matched_position(self, txt: str, match_whole_word: bool, match_case: bool, regex: bool) -> list:
        content = self.text()
        positions = []

        if not regex:
            txt = repr(txt)[1:-1]

        pattern = fr'\b({txt})\b' if match_whole_word else fr'({txt})'

        # Check whether the regex pattern is valid
        try:
            re.compile(pattern)
        except:
            return positions

        # Set the flags
        flags = 0 if match_case else re.IGNORECASE
        arr = re.finditer(pattern, content, flags | re.MULTILINE)

        # Get start and end position of each line
        end = '.*\n'
        lines = []
        for m in re.finditer(end, content):
            lines.append(m.span())

        def line_position(start: int):
            line_num = 0
            if not lines:
                return (line_num, start)

            while (start > lines[line_num][1]):
                line_num = line_num + 1
            return (line_num, start - lines[line_num][0])

        for match in arr:
            line, index = line_position(match.start())
            length = match.end() - match.start()
            positions.append((line, index, length))

        return positions

    def create_indicators(self, indicator_number: int, positions: list[tuple]):
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator_number)
        for pos_line, pos_index, len in positions:
            start_position = self.positionFromLineIndex(pos_line, pos_index)
            self.SendScintilla(
                QsciScintilla.SCI_INDICATORFILLRANGE, start_position, len)

    def clear_indicators(self, indicator_number: int):
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator_number)
        self.SendScintilla(
            QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.length())
