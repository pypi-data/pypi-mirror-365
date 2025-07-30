"""
Cloud Settings - Temel Sayfa Sınıfı
Tüm ayar sayfaları için temel sınıf
"""

import logging
from typing import Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class BasePage(QWidget):
    """Ayar sayfası temel sınıfı"""
    
    settings_changed = pyqtSignal(str, dict)  # category, settings
    
    def __init__(self, category: str, title: str, icon: str = "⚙️", kernel=None, preview_manager=None):
        super().__init__()
        self.category = category
        self.title = title
        self.icon = icon
        self.kernel = kernel
        self.preview_manager = preview_manager
        self.logger = logging.getLogger(f"SettingsPage.{category}")
        
        self.settings = {}
        self.widgets = {}
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """UI kurulumu - alt sınıflarda override edilecek"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # İçerik widget'ı
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 20, 0)  # Sağ tarafta scroll bar için boşluk
        self.content_layout.setSpacing(20)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # Scroll area stili
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background-color: #dee2e6;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
    
    def setup_connections(self):
        """Sinyal bağlantıları - alt sınıflarda override edilebilir"""
        pass
    
    def add_group(self, title: str) -> QGroupBox:
        """Grup kutusu ekle"""
        from ..widgets import ModernGroupBox
        
        group = ModernGroupBox(title)
        self.content_layout.addWidget(group)
        return group
    
    def add_setting_row(self, parent_layout, label_text: str, widget: QWidget, description: str = ""):
        """Ayar satırı ekle"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sol taraf - etiket ve açıklama
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #212529;
            }
        """)
        left_layout.addWidget(label)
        
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #6c757d;
                }
            """)
            desc_label.setWordWrap(True)
            left_layout.addWidget(desc_label)
        
        left_layout.addStretch()
        row_layout.addWidget(left_widget, 1)
        
        # Sağ taraf - widget
        row_layout.addWidget(widget)
        
        parent_layout.addWidget(row_widget)
        return row_widget
    
    def add_checkbox(self, parent_layout, text: str, key: str, description: str = ""):
        """Checkbox ekle"""
        from ..widgets import ModernCheckBox
        
        checkbox = ModernCheckBox(text)
        checkbox.toggled.connect(lambda checked: self.on_setting_changed(key, checked))
        
        self.widgets[key] = checkbox
        
        if description:
            self.add_setting_row(parent_layout, "", checkbox, description)
        else:
            parent_layout.addWidget(checkbox)
        
        return checkbox
    
    def add_combobox(self, parent_layout, label: str, key: str, items: list, description: str = ""):
        """ComboBox ekle"""
        from ..widgets import ModernComboBox
        
        combo = ModernComboBox()
        combo.addItems(items)
        combo.currentTextChanged.connect(lambda text: self.on_setting_changed(key, text.lower()))
        
        self.widgets[key] = combo
        self.add_setting_row(parent_layout, label, combo, description)
        
        return combo
    
    def add_slider(self, parent_layout, label: str, key: str, min_val: int, max_val: int, default: int, description: str = ""):
        """Slider ekle"""
        from ..widgets import ModernSlider
        
        slider = ModernSlider(min_val, max_val, default)
        slider.value_changed.connect(lambda value: self.on_setting_changed(key, value))
        
        self.widgets[key] = slider
        self.add_setting_row(parent_layout, label, slider, description)
        
        return slider
    
    def add_spinbox(self, parent_layout, label: str, key: str, min_val: int, max_val: int, default: int, suffix: str = "", description: str = ""):
        """SpinBox ekle"""
        from ..widgets import ModernSpinBox
        
        spinbox = ModernSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        if suffix:
            spinbox.setSuffix(suffix)
        spinbox.valueChanged.connect(lambda value: self.on_setting_changed(key, value))
        
        self.widgets[key] = spinbox
        self.add_setting_row(parent_layout, label, spinbox, description)
        
        return spinbox
    
    def add_color_picker(self, parent_layout, label: str, key: str, default_color: str = "#007bff", description: str = ""):
        """Renk seçici ekle"""
        from ..widgets import ColorPickerButton
        
        color_picker = ColorPickerButton(default_color)
        color_picker.color_changed.connect(lambda color: self.on_setting_changed(key, color))
        
        self.widgets[key] = color_picker
        self.add_setting_row(parent_layout, label, color_picker, description)
        
        return color_picker
    
    def add_file_picker(self, parent_layout, label: str, key: str, file_filter: str = "", description: str = ""):
        """Dosya seçici ekle"""
        file_widget = QWidget()
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Dosya seçin...")
        line_edit.textChanged.connect(lambda text: self.on_setting_changed(key, text))
        
        browse_btn = QPushButton("Gözat")
        browse_btn.clicked.connect(lambda: self._browse_file(line_edit, file_filter))
        
        file_layout.addWidget(line_edit, 1)
        file_layout.addWidget(browse_btn)
        
        self.widgets[key] = line_edit
        self.add_setting_row(parent_layout, label, file_widget, description)
        
        return line_edit
    
    def _browse_file(self, line_edit: QLineEdit, file_filter: str):
        """Dosya gözat"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Dosya Seç",
            line_edit.text() or str(Path.home()),
            file_filter
        )
        
        if file_path:
            line_edit.setText(file_path)
    
    def on_setting_changed(self, key: str, value):
        """Ayar değişti"""
        self.settings[key] = value
        
        # Canlı önizleme güncelle
        if self.preview_manager:
            self.preview_manager.update_preview(self.category, self.settings)
        
        # Sinyal gönder
        self.settings_changed.emit(self.category, self.settings.copy())
        
        self.logger.debug(f"Setting changed: {key} = {value}")
    
    def load_settings(self, settings: Dict[str, Any]):
        """Ayarları yükle"""
        self.settings = settings.copy()
        self.update_ui()
        
        self.logger.debug(f"Settings loaded: {len(settings)} items")
    
    def update_ui(self):
        """UI'yi ayarlara göre güncelle - alt sınıflarda override edilecek"""
        for key, widget in self.widgets.items():
            if key in self.settings:
                value = self.settings[key]
                
                try:
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))
                    elif isinstance(widget, QComboBox):
                        # Değeri bul ve seç
                        for i in range(widget.count()):
                            if widget.itemText(i).lower() == str(value).lower():
                                widget.setCurrentIndex(i)
                                break
                    elif isinstance(widget, QSlider):
                        widget.setValue(int(value))
                    elif isinstance(widget, QSpinBox):
                        widget.setValue(int(value))
                    elif isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif hasattr(widget, 'setValue'):
                        widget.setValue(value)
                    elif hasattr(widget, 'set_color'):
                        widget.set_color(str(value))
                        
                except Exception as e:
                    self.logger.warning(f"Failed to update widget {key}: {e}")
    
    def get_settings(self) -> Dict[str, Any]:
        """Mevcut ayarları al"""
        return self.settings.copy()
    
    def add_spacer(self):
        """Boşluk ekle"""
        self.content_layout.addStretch()
    
    def add_separator(self):
        """Ayırıcı çizgi ekle"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("""
            QFrame {
                color: #e9ecef;
                background-color: #e9ecef;
                border: none;
                height: 1px;
            }
        """)
        self.content_layout.addWidget(line) 