"""
Cloud Settings - Modern UI Widget'ları
Özel widget bileşenleri
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class ModernSearchBar(QLineEdit):
    """Modern arama çubuğu"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setPlaceholderText("🔍 Ayarlarda ara...")
        self.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                color: #495057;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                background-color: #ffffff;
            }
        """)

class SettingsCard(QWidget):
    """Ayar kategorisi kartı"""
    
    def __init__(self, icon: str, title: str, description: str):
        super().__init__()
        self.icon = icon
        self.title = title
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # İkon
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Metin alanı
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # Başlık
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #212529;
        """)
        text_layout.addWidget(title_label)
        
        # Açıklama
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #6c757d;
        """)
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout, 1)
        
        # Hover efekti için stil
        self.setStyleSheet("""
            SettingsCard {
                background-color: transparent;
                border-radius: 8px;
            }
            
            SettingsCard:hover {
                background-color: #f8f9fa;
            }
        """)

class LivePreviewWidget(QWidget):
    """Canlı önizleme widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.preview_data = {}
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık
        title_label = QLabel("Canlı Önizleme")
        title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #6c757d;
            margin-bottom: 5px;
        """)
        layout.addWidget(title_label)
        
        # Önizleme alanı
        self.preview_area = QLabel()
        self.preview_area.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                color: #495057;
                font-size: 11px;
            }
        """)
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setText("Önizleme hazır")
        layout.addWidget(self.preview_area, 1)
        
        # Genel stil
        self.setStyleSheet("""
            LivePreviewWidget {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
    
    def update_preview(self, preview_data: dict):
        """Önizlemeyi güncelle"""
        self.preview_data = preview_data
        
        # Önizleme metnini oluştur
        preview_text = []
        
        if "theme" in preview_data:
            preview_text.append(f"Tema: {preview_data['theme']}")
        
        if "wallpaper" in preview_data:
            preview_text.append(f"Duvar kağıdı: {preview_data['wallpaper']}")
        
        if "dock_position" in preview_data:
            preview_text.append(f"Dock: {preview_data['dock_position']}")
        
        if preview_text:
            self.preview_area.setText("\n".join(preview_text))
        else:
            self.preview_area.setText("Önizleme hazır")

class ColorPickerButton(QPushButton):
    """Renk seçici butonu"""
    
    color_changed = pyqtSignal(str)  # hex color
    
    def __init__(self, initial_color: str = "#007bff"):
        super().__init__()
        self.current_color = initial_color
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setFixedSize(40, 40)
        self.clicked.connect(self.pick_color)
        self.update_button_style()
    
    def update_button_style(self):
        """Buton stilini güncelle"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                border: 2px solid #e9ecef;
                border-radius: 20px;
            }}
            
            QPushButton:hover {{
                border-color: #007bff;
            }}
        """)
    
    def pick_color(self):
        """Renk seç"""
        color = QColorDialog.getColor(QColor(self.current_color), self)
        
        if color.isValid():
            self.current_color = color.name()
            self.update_button_style()
            self.color_changed.emit(self.current_color)
    
    def set_color(self, color: str):
        """Rengi ayarla"""
        self.current_color = color
        self.update_button_style()

class ModernSlider(QWidget):
    """Modern slider widget'ı"""
    
    value_changed = pyqtSignal(int)
    
    def __init__(self, minimum: int = 0, maximum: int = 100, value: int = 50):
        super().__init__()
        self.setup_ui(minimum, maximum, value)
    
    def setup_ui(self, minimum: int, maximum: int, value: int):
        """UI kurulumu"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #e9ecef;
                height: 6px;
                background: #f8f9fa;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #007bff;
                border: 2px solid #ffffff;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
            
            QSlider::handle:horizontal:hover {
                background: #0056b3;
            }
            
            QSlider::sub-page:horizontal {
                background: #007bff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.slider, 1)
        
        # Değer etiketi
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #495057;
                font-weight: 600;
                min-width: 30px;
            }
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Sinyal bağlantısı
        self.slider.valueChanged.connect(self.on_value_changed)
    
    def on_value_changed(self, value: int):
        """Değer değişti"""
        self.value_label.setText(str(value))
        self.value_changed.emit(value)
    
    def value(self) -> int:
        """Mevcut değeri al"""
        return self.slider.value()
    
    def setValue(self, value: int):
        """Değer ayarla"""
        self.slider.setValue(value)

class ModernGroupBox(QGroupBox):
    """Modern grup kutusu"""
    
    def __init__(self, title: str):
        super().__init__(title)
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #212529;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
            }
        """)

class ModernCheckBox(QCheckBox):
    """Modern checkbox"""
    
    def __init__(self, text: str = ""):
        super().__init__(text)
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #495057;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #e9ecef;
                border-radius: 4px;
                background-color: #ffffff;
            }
            
            QCheckBox::indicator:hover {
                border-color: #007bff;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)

class ModernComboBox(QComboBox):
    """Modern combo box"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #495057;
                min-width: 120px;
            }
            
            QComboBox:hover {
                border-color: #007bff;
            }
            
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzZjNzU3ZCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                selection-background-color: #007bff;
                selection-color: #ffffff;
                padding: 4px;
            }
        """)

class ModernSpinBox(QSpinBox):
    """Modern spin box"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setStyleSheet("""
            QSpinBox {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #495057;
                min-width: 80px;
            }
            
            QSpinBox:hover {
                border-color: #007bff;
            }
            
            QSpinBox:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: transparent;
            }
            
            QSpinBox::up-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMSA3TDYgMkwxIDciIHN0cm9rZT0iIzZjNzU3ZCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
            }
            
            QSpinBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzZjNzU3ZCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+Cg==);
            }
        """)

class ModernButton(QPushButton):
    """Modern buton"""
    
    def __init__(self, text: str, button_type: str = "primary"):
        super().__init__(text)
        self.button_type = button_type
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        base_style = """
            QPushButton {
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                min-width: 80px;
            }
        """
        
        if self.button_type == "primary":
            style = base_style + """
                QPushButton {
                    background-color: #007bff;
                    color: #ffffff;
                }
                
                QPushButton:hover {
                    background-color: #0056b3;
                }
                
                QPushButton:pressed {
                    background-color: #004085;
                }
            """
        elif self.button_type == "secondary":
            style = base_style + """
                QPushButton {
                    background-color: #6c757d;
                    color: #ffffff;
                }
                
                QPushButton:hover {
                    background-color: #5a6268;
                }
                
                QPushButton:pressed {
                    background-color: #495057;
                }
            """
        elif self.button_type == "success":
            style = base_style + """
                QPushButton {
                    background-color: #28a745;
                    color: #ffffff;
                }
                
                QPushButton:hover {
                    background-color: #218838;
                }
                
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """
        elif self.button_type == "danger":
            style = base_style + """
                QPushButton {
                    background-color: #dc3545;
                    color: #ffffff;
                }
                
                QPushButton:hover {
                    background-color: #c82333;
                }
                
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """
        else:  # outline
            style = base_style + """
                QPushButton {
                    background-color: transparent;
                    color: #007bff;
                    border: 2px solid #007bff;
                }
                
                QPushButton:hover {
                    background-color: #007bff;
                    color: #ffffff;
                }
                
                QPushButton:pressed {
                    background-color: #0056b3;
                }
            """
        
        self.setStyleSheet(style) 