from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QGroupBox,
                            QListWidget, QStyledItemDelegate, QStyle)
from PyQt5.QtCore import QSettings, Qt, QSize, QRectF, QRect
from PyQt5.QtGui import QIcon, QPainter, QPainterPath
from importlib.resources import files

class RoundedIconDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        # Save the painter state
        painter.save()

        # Draw selection background if item is selected
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())
        else:
            painter.setPen(option.palette.text().color())
        
        # Get the icon from the item
        icon = index.data(Qt.DecorationRole)
        if icon:
            # Create a rounded rectangle path
            path = QPainterPath()
            rect = option.rect
            icon_size = option.decorationSize
            
            # Calculate icon position (centered vertically)
            icon_x = rect.left() + 4  # 4 pixels padding
            icon_y = rect.top() + (rect.height() - icon_size.height()) // 2
            icon_rect = QRect(icon_x, icon_y, icon_size.width(), icon_size.height())
            
            # Create rounded rectangle path
            path.addRoundedRect(QRectF(icon_rect), 5, 5)  # 8 pixel radius for corners
            
            # Set the clip path for rounded corners
            painter.setClipPath(path)
            
            # Draw the icon
            icon.paint(painter, icon_rect)
        
        # Restore painter state
        painter.restore()
        
        # Draw the text
        text_rect = option.rect.adjusted(icon_size.width() + 8, 0, 0, 0)  # 8 pixels padding after icon
        painter.drawText(text_rect, Qt.AlignVCenter, index.data(Qt.DisplayRole))

class OpenAISettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('cjtool', 'codebook')
        
        self.setWindowTitle('OpenAI Settings')
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Add provider selection list
        self.provider_list = QListWidget()
        self.provider_list.setIconSize(QSize(24, 24))
        self.provider_list.setItemDelegate(RoundedIconDelegate())
        # Set uniform item sizes and alignment
        self.provider_list.setUniformItemSizes(True)
        self.provider_list.setSpacing(2)
        
        # Add items with icons
        self.provider_list.addItem('DeepSeek')
        icon_path = files('callbook').joinpath('image', 'deepseek.png')
        self.provider_list.item(0).setIcon(QIcon(str(icon_path)))
        
        self.provider_list.addItem('Groq')
        icon_path = files('callbook').joinpath('image', 'groq.png')
        self.provider_list.item(1).setIcon(QIcon(str(icon_path)))
        
        # Get provider from settings or default to DeepSeek
        current_provider = self.settings.value('selected_provider', 'DeepSeek')
        matching_items = self.provider_list.findItems(current_provider, Qt.MatchExactly)
        if matching_items:
            self.provider_list.setCurrentItem(matching_items[0])
        else:
            self.provider_list.setCurrentRow(0)  # Default to first item (DeepSeek)
            
        self.provider_list.currentItemChanged.connect(self.on_provider_changed)
        layout.addWidget(self.provider_list)
        
        # Create GroupBox for API settings
        api_group = QGroupBox("API Settings")
        api_group_layout = QVBoxLayout()
        
        current_provider = current_provider.lower()

        # Base URL input
        base_url_layout = QHBoxLayout()
        base_url_label = QLabel('API URL:')
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText('https://api.deepseek.com')
        self.base_url_input.setFixedWidth(300)
        base_url_layout.addWidget(base_url_label)
        base_url_layout.addWidget(self.base_url_input)
        
        # API Key input
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel('API Key:')
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        
        # Model selection input
        model_layout = QHBoxLayout()
        model_label = QLabel('Model:')
        self.model_input = QComboBox()
        self.model_input.setMinimumWidth(300)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_input)
        
        # Add inputs to group layout
        api_group_layout.addLayout(base_url_layout)
        api_group_layout.addLayout(api_key_layout)
        api_group_layout.addLayout(model_layout)
        api_group.setLayout(api_group_layout)
        
        # Add group to main layout
        layout.addWidget(api_group)
        
        # Connect input focus events to save settings
        self.base_url_input.editingFinished.connect(self.save_current_settings)
        self.api_key_input.editingFinished.connect(self.save_current_settings)
        self.model_input.currentTextChanged.connect(self.save_current_settings)
        
        # Button
        button_layout = QHBoxLayout()
        ok_button = QPushButton('OK')
        ok_button.setFixedWidth(100)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load initial provider settings
        self.load_provider_settings(current_provider)
        
    def on_provider_changed(self, current, previous):
        if current is None:
            return
        provider = current.text().lower()
        self.load_provider_settings(provider)
    
    def load_provider_settings(self, provider: str) -> None:
        if provider == 'deepseek':
            self.base_url_input.setText(self.settings.value('deepseek/base_url', 'https://api.deepseek.com'))
            self.api_key_input.setText(self.settings.value('deepseek/api_key', ''))
            self.model_input.blockSignals(True)  # Block signals temporarily
            self.model_input.clear()
            self.model_input.addItems(['deepseek-chat', 'deepseek-reasoner'])
            self.model_input.setCurrentText(self.settings.value('deepseek/model', 'deepseek-chat'))
            self.model_input.blockSignals(False)  # Re-enable signals
        else:  # groq
            self.base_url_input.setText(self.settings.value('groq/base_url', 'https://api.groq.com/openai/v1'))
            self.api_key_input.setText(self.settings.value('groq/api_key', ''))
            self.model_input.blockSignals(True)  # Block signals temporarily
            self.model_input.clear()
            self.model_input.addItems(['llama-3.3-70b-versatile', 'deepseek-r1-distill-llama-70b'])
            self.model_input.setCurrentText(self.settings.value('groq/model', 'llama-3.3-70b-versatile'))
            self.model_input.blockSignals(False)  # Re-enable signals
    
    def save_current_settings(self):
        provider = self.provider_list.currentItem().text()
        # Save the selected provider
        self.settings.setValue('selected_provider', provider)
        # Save the provider-specific settings
        provider = provider.lower()
        self.settings.setValue(f'{provider}/base_url', self.base_url_input.text())
        self.settings.setValue(f'{provider}/api_key', self.api_key_input.text())
        self.settings.setValue(f'{provider}/model', self.model_input.currentText()) 