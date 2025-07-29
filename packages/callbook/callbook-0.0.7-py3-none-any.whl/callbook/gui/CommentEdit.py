from PyQt5.QtWidgets import QWidget, QTextEdit, QToolBar, QToolButton, QMessageBox, QVBoxLayout
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import pyqtSignal, Qt, QUrl, QSettings
from PyQt5.QtWebEngineWidgets import QWebEngineView
from .Document import StandardItem, Document
import markdown
from pygments.formatters import HtmlFormatter
import openai
import os
import re


class CommentEdit(QWidget):
    commentChanged = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.isItemChanged = False
        self.curDocument = None
        self.functionData = None
        self.markdown_text = ''
        self.initUI()

    def initUI(self):
        # Set up main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and setup text edit
        self.textEdit = QTextEdit(self)
        self._setupTextEdit()
        self.textEdit.hide()
        
        # Create web view for markdown preview
        self.webView = QWebEngineView(self)

        # Add widgets to layout
        layout.addWidget(self.textEdit)
        layout.addWidget(self.webView)
        
        # Setup toolbar
        self._setupToolbar()
        
        # Connect signals
        self.textEdit.textChanged.connect(self.textChangedAction)

    def _setupTextEdit(self):
        font = QFont('Inconsolata')
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.textEdit.setFont(font)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        width = QFontMetrics(font).averageCharWidth()
        self.textEdit.setTabStopDistance(4 * width)

    def _setupToolbar(self):
        # Create and setup toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setFixedWidth(150)
        
        # Create and add render button
        self.render_button = QToolButton(self.toolbar)
        self.render_button.setText("Edit")
        self.toolbar.addWidget(self.render_button)
        
        # Create and add AI button
        self.ai_button = QToolButton(self.toolbar)
        self.ai_button.setText("AI")
        self.toolbar.addWidget(self.ai_button)
        
        # Position toolbar at bottom right
        self.toolbar.move(
            self.width() - self.toolbar.width(),
            self.height() - self.toolbar.height()
        )
        
        # Connect signals
        self.render_button.clicked.connect(self.toggle_view)
        self.ai_button.clicked.connect(self.ai_clicked)
        
        # Ensure toolbar stays at bottom right when window is resized
        self.resizeEvent = self.onResize

    def onResize(self, event):
        # Update toolbar position when widget is resized
        self.toolbar.move(
            self.width() - self.toolbar.width(),
            self.height() - self.toolbar.height()
        )
        super().resizeEvent(event)

    def toggle_view(self):
        if self.textEdit.isVisible():
            self.textEdit.hide()
            self.webView.show()
            self.render_button.setText("Edit")
            self.update_html()
        else:
            self.webView.hide()
            self.textEdit.show()
            self.render_button.setText("Preview")

    def update_html(self):
        # Get the Markdown content from the QTextEdit widget
        markdown_content = self.textEdit.toPlainText()

        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables', 'codehilite'])

        # Process local image paths and LaTeX expressions in the HTML content
        html_content = self.handle_local_images(html_content)
        html_content = self.add_mathjax(html_content)

        # Load the HTML content into the QWebEngineView
        self.webView.setHtml(html_content)

    def handle_local_images(self, html_content):
        # Find all image tags in the HTML content
        pattern = r'!\[.*?\]\((.*?)\)'  # Regex to match markdown image links
        matches = re.findall(pattern, html_content)

        # Process each match (image path)
        for match in matches:
            if not match.startswith('http') and not match.startswith('file://'):
                # Convert relative path to absolute file URL
                abs_path = os.path.abspath(match)
                if os.path.exists(abs_path):
                    # Convert local path to file:// URL
                    file_url = QUrl.fromLocalFile(abs_path).toString()
                    # Replace the markdown image path with the file URL
                    html_content = html_content.replace(match, file_url)

        return html_content

    def add_mathjax(self, html_content):
        # Add MathJax to the HTML for LaTeX rendering
        mathjax_script = """
        <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
            inlineMath: [ ['$','$'], ["\\(","\\)"] ],
            processEscapes: true
            }
        });
        </script>

        <script type="text/javascript" async
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
        </script>
        """

        # Add Highlight.js CSS for syntax highlighting
        # Generate Pygments CSS for code syntax highlighting
        formatter = HtmlFormatter(style='monokai')  # Choose a style (e.g., 'default', 'monokai')
        highlight_css = f"<style>{formatter.get_style_defs('.codehilite')}</style>"

        # Insert MathJax script into the head of the HTML content
        if '<head>' not in html_content:
            html_content = f"<html><head>{mathjax_script}{highlight_css}</head><body>{html_content}</body></html>"
        else:
            html_content = html_content.replace('<head>', f'<head>{mathjax_script}{highlight_css}')

        return html_content

    def textChangedAction(self):
        if self.isItemChanged:
            return
        
        comment = self.textEdit.toPlainText()
        self.commentChanged.emit(comment)

    def setDocument(self, doc: Document):
        self.curDocument = doc
        doc.curItemChanged.connect(self.onCurItemChanged)
        self.commentChanged.connect(doc.on_comment_changed)

    def onCurItemChanged(self, item: StandardItem) -> None:
        self.isItemChanged = True
        comment = self.curDocument.get_comment(item.functionData)
        self.functionData = item.functionData
        self.textEdit.setPlainText(comment)
        self.markdown_text = comment
        self.isItemChanged = False
        if not self.textEdit.isVisible():
            self.update_html()

    def ai_clicked(self):
        settings = QSettings('cjtool', 'codebook')
        provider = settings.value('selected_provider', 'DeepSeek').lower()
        
        # Get provider-specific settings
        base_url = settings.value(f"{provider}/base_url", "")
        api_key = settings.value(f"{provider}/api_key", "")
        model = settings.value(f"{provider}/model", "")

        if not base_url:
            QMessageBox.warning(self, "Base URL Missing", f"Please set base_url for {provider} in settings.")
            return

        if not api_key:
            QMessageBox.warning(self, "API Key Missing", f"Please set api_key for {provider} in settings.")
            return

        client = openai.OpenAI(base_url=base_url, api_key=api_key)

        try:
            source = self.functionData.source
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": f"请解释下面这段C++代码的逻辑，并说明完成了什么功能：\n```\n{source}\n```"
                    }
                ]
            )

            content = completion.choices[0].message.content
            self.textEdit.setPlainText(content)
            self.markdown_text = content
            if not self.textEdit.isVisible():
                self.update_html()
            self.commentChanged.emit(content)
        except Exception as e:
            QMessageBox.critical(self, "API Error", f"Failed to get AI response: {str(e)}")

    def clear(self):
        self.textEdit.clear()
