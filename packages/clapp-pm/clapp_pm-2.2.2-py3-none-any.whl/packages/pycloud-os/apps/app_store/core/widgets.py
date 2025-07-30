"""
Cloud AppStore Widgets
Modern uygulama kartları ve UI bileşenleri
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .appstore import AppInfo, AppStatus, ViewMode

class ModernAppCard(QWidget):
    """Modern uygulama kartı widget'ı"""
    
    # Sinyaller
    install_requested = pyqtSignal(str)  # app_id
    remove_requested = pyqtSignal(str)   # app_id
    update_requested = pyqtSignal(str)   # app_id
    info_requested = pyqtSignal(str)     # app_id
    rating_changed = pyqtSignal(str, int)  # app_id, rating
    
    def __init__(self, app_info: AppInfo, view_mode: ViewMode = ViewMode.GRID, dark_mode: bool = False):
        super().__init__()
        self.app_info = app_info
        self.view_mode = view_mode
        self.dark_mode = dark_mode
        self.user_rating = 0
        
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        """UI kurulumu"""
        if self.view_mode == ViewMode.GRID:
            self.setup_grid_layout()
        elif self.view_mode == ViewMode.LIST:
            self.setup_list_layout()
        else:  # DETAILED
            self.setup_detailed_layout()
    
    def setup_grid_layout(self):
        """Grid görünüm layoutu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # İkon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_app_icon()
        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Uygulama adı
        self.name_label = QLabel(self.app_info.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.name_label)
        
        # Geliştirici
        self.developer_label = QLabel(f"by {self.app_info.developer}")
        self.developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.developer_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.developer_label)
        
        # Rating
        self.rating_widget = StarRatingWidget(self.app_info.rating, read_only=True)
        layout.addWidget(self.rating_widget, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Kategori badge
        self.category_badge = QLabel(self.app_info.category)
        self.category_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.category_badge.setStyleSheet("""
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
        """)
        layout.addWidget(self.category_badge, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Durum ve butonlar
        self.setup_action_buttons()
        layout.addWidget(self.action_widget)
        
        # Güncelleme badge'i
        if self.app_info.has_update():
            self.update_badge = QLabel("Güncelleme Var!")
            self.update_badge.setStyleSheet("""
                background-color: #ff9800;
                color: white;
                padding: 2px 6px;
                border-radius: 8px;
                font-size: 9px;
                font-weight: bold;
            """)
            layout.addWidget(self.update_badge, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.setFixedSize(200, 280)
    
    def setup_list_layout(self):
        """Liste görünüm layoutu"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # İkon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.load_app_icon()
        layout.addWidget(self.icon_label)
        
        # Ana bilgiler
        info_layout = QVBoxLayout()
        
        # Üst satır: Ad ve kategori
        top_layout = QHBoxLayout()
        self.name_label = QLabel(self.app_info.name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_layout.addWidget(self.name_label)
        
        self.category_badge = QLabel(self.app_info.category)
        self.category_badge.setStyleSheet("""
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 10px;
        """)
        top_layout.addWidget(self.category_badge)
        top_layout.addStretch()
        info_layout.addLayout(top_layout)
        
        # Alt satır: Geliştirici ve rating
        bottom_layout = QHBoxLayout()
        self.developer_label = QLabel(f"by {self.app_info.developer}")
        self.developer_label.setStyleSheet("color: #666; font-size: 12px;")
        bottom_layout.addWidget(self.developer_label)
        
        self.rating_widget = StarRatingWidget(self.app_info.rating, read_only=True, size=16)
        bottom_layout.addWidget(self.rating_widget)
        bottom_layout.addStretch()
        info_layout.addLayout(bottom_layout)
        
        layout.addLayout(info_layout, 1)
        
        # Sağ taraf: Butonlar
        self.setup_action_buttons()
        layout.addWidget(self.action_widget)
        
        self.setFixedHeight(80)
    
    def setup_detailed_layout(self):
        """Detaylı görünüm layoutu"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Sol: İkon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(80, 80)
        self.load_app_icon()
        layout.addWidget(self.icon_label)
        
        # Orta: Detaylı bilgiler
        info_layout = QVBoxLayout()
        
        # Başlık satırı
        title_layout = QHBoxLayout()
        self.name_label = QLabel(self.app_info.name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        title_layout.addWidget(self.name_label)
        
        self.version_label = QLabel(f"v{self.app_info.version}")
        self.version_label.setStyleSheet("color: #888; font-size: 12px;")
        title_layout.addWidget(self.version_label)
        title_layout.addStretch()
        info_layout.addLayout(title_layout)
        
        # Geliştirici ve kategori
        meta_layout = QHBoxLayout()
        self.developer_label = QLabel(f"Geliştirici: {self.app_info.developer}")
        self.developer_label.setStyleSheet("color: #666; font-size: 12px;")
        meta_layout.addWidget(self.developer_label)
        
        self.category_badge = QLabel(self.app_info.category)
        self.category_badge.setStyleSheet("""
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 10px;
            font-size: 11px;
        """)
        meta_layout.addWidget(self.category_badge)
        meta_layout.addStretch()
        info_layout.addLayout(meta_layout)
        
        # Açıklama
        self.description_label = QLabel(self.app_info.description[:150] + "..." if len(self.app_info.description) > 150 else self.app_info.description)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555; font-size: 12px; margin: 4px 0;")
        info_layout.addWidget(self.description_label)
        
        # Rating ve etiketler
        extras_layout = QHBoxLayout()
        self.rating_widget = StarRatingWidget(self.app_info.rating, read_only=True)
        extras_layout.addWidget(self.rating_widget)
        
        # Etiketler
        if self.app_info.tags:
            for tag in self.app_info.tags[:3]:
                tag_label = QLabel(f"#{tag}")
                tag_label.setStyleSheet("""
                    background-color: #f0f0f0;
                    color: #666;
                    padding: 2px 6px;
                    border-radius: 8px;
                    font-size: 10px;
                """)
                extras_layout.addWidget(tag_label)
        
        extras_layout.addStretch()
        info_layout.addLayout(extras_layout)
        
        layout.addLayout(info_layout, 1)
        
        # Sağ: Butonlar
        self.setup_action_buttons()
        layout.addWidget(self.action_widget)
        
        self.setFixedHeight(140)
    
    def setup_action_buttons(self):
        """Aksiyon butonlarını kur"""
        self.action_widget = QWidget()
        layout = QVBoxLayout(self.action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Ana buton (Kur/Kaldır/Güncelle)
        if self.app_info.is_installed:
            if self.app_info.has_update():
                self.main_button = QPushButton("🔄 Güncelle")
                self.main_button.setStyleSheet(self.get_button_style("#ff9800"))
                self.main_button.clicked.connect(lambda: self.update_requested.emit(self.app_info.app_id))
            else:
                self.main_button = QPushButton("🗑️ Kaldır")
                self.main_button.setStyleSheet(self.get_button_style("#f44336"))
                self.main_button.clicked.connect(lambda: self.remove_requested.emit(self.app_info.app_id))
        else:
            self.main_button = QPushButton("⬇️ Kur")
            self.main_button.setStyleSheet(self.get_button_style("#4caf50"))
            self.main_button.clicked.connect(lambda: self.install_requested.emit(self.app_info.app_id))
        
        layout.addWidget(self.main_button)
        
        # Bilgi butonu
        self.info_button = QPushButton("ℹ️ Bilgi")
        self.info_button.setStyleSheet(self.get_button_style("#2196f3"))
        self.info_button.clicked.connect(lambda: self.info_requested.emit(self.app_info.app_id))
        layout.addWidget(self.info_button)
    
    def get_button_style(self, color: str) -> str:
        """Buton stili"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """
    
    def darken_color(self, color: str, factor: float = 0.9) -> str:
        """Rengi koyulaştır"""
        color_map = {
            "#4caf50": "#45a049",
            "#f44336": "#d32f2f", 
            "#2196f3": "#1976d2",
            "#ff9800": "#f57c00"
        }
        return color_map.get(color, color)
    
    def load_app_icon(self):
        """Uygulama ikonunu yükle"""
        try:
            icon_path = Path(self.app_info.icon_path)
            if icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.icon_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.icon_label.setPixmap(scaled_pixmap)
                    return
        except Exception:
            pass
        
        # Varsayılan ikon
        self.set_default_icon()
    
    def set_default_icon(self):
        """Varsayılan ikon ayarla"""
        # Kategori bazlı emoji ikonlar
        category_icons = {
            "Sistem": "⚙️",
            "Geliştirme": "💻",
            "İnternet": "🌐",
            "Multimedya": "🎵",
            "Grafik": "🎨",
            "Oyunlar": "🎮",
            "Ofis": "📄",
            "Eğitim": "📚",
            "Araçlar": "🔧"
        }
        
        emoji = category_icons.get(self.app_info.category, "📱")
        
        # Emoji'yi QPixmap'e çevir
        pixmap = QPixmap(self.icon_label.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        font = QFont("Apple Color Emoji", 32)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        
        self.icon_label.setPixmap(pixmap)
    
    def apply_theme(self):
        """Tema uygula"""
        if self.dark_mode:
            card_style = """
                ModernAppCard {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 12px;
                    margin: 4px;
                }
                ModernAppCard:hover {
                    border-color: #2196f3;
                    background-color: #353535;
                }
            """
        else:
            card_style = """
                ModernAppCard {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 12px;
                    margin: 4px;
                }
                ModernAppCard:hover {
                    border-color: #2196f3;
                    background-color: #f8f9fa;
                }
            """
        
        self.setStyleSheet(card_style)
    
    def update_status(self, status: AppStatus):
        """Durum güncelle"""
        self.app_info.status = status
        
        # Buton durumunu güncelle
        if status == AppStatus.INSTALLING:
            self.main_button.setText("⏳ Kuruluyor...")
            self.main_button.setEnabled(False)
        elif status == AppStatus.REMOVING:
            self.main_button.setText("⏳ Kaldırılıyor...")
            self.main_button.setEnabled(False)
        elif status == AppStatus.UPDATING:
            self.main_button.setText("⏳ Güncelleniyor...")
            self.main_button.setEnabled(False)
        else:
            self.main_button.setEnabled(True)
            self.setup_action_buttons()  # Butonları yeniden kur

class StarRatingWidget(QWidget):
    """Yıldız rating widget'ı"""
    
    rating_changed = pyqtSignal(int)
    
    def __init__(self, rating: float = 0.0, max_rating: int = 5, read_only: bool = False, size: int = 20):
        super().__init__()
        self.rating = rating
        self.max_rating = max_rating
        self.read_only = read_only
        self.star_size = size
        self.hovered_star = -1
        
        self.setFixedSize(max_rating * (size + 2), size + 4)
        self.setMouseTracking(not read_only)
    
    def paintEvent(self, event):
        """Yıldızları çiz"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for i in range(self.max_rating):
            x = i * (self.star_size + 2)
            y = 2
            
            # Yıldız rengi belirle
            if i < int(self.rating):
                color = QColor("#ffc107")  # Dolu yıldız
            elif i < self.rating:
                color = QColor("#ffeb3b")  # Yarım yıldız
            else:
                color = QColor("#e0e0e0")  # Boş yıldız
            
            # Hover efekti
            if not self.read_only and i <= self.hovered_star:
                color = QColor("#ff9800")
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#ddd"), 1))
            
            # Yıldız çiz
            self.draw_star(painter, x, y, self.star_size)
    
    def draw_star(self, painter: QPainter, x: int, y: int, size: int):
        """Yıldız şekli çiz"""
        star = QPolygonF([
            QPointF(x + size/2, y),
            QPointF(x + size*0.6, y + size*0.35),
            QPointF(x + size, y + size*0.35),
            QPointF(x + size*0.7, y + size*0.6),
            QPointF(x + size*0.8, y + size),
            QPointF(x + size/2, y + size*0.75),
            QPointF(x + size*0.2, y + size),
            QPointF(x + size*0.3, y + size*0.6),
            QPointF(x, y + size*0.35),
            QPointF(x + size*0.4, y + size*0.35)
        ])
        painter.drawPolygon(star)
    
    def mousePressEvent(self, event):
        """Fare tıklaması"""
        if self.read_only:
            return
        
        star_index = event.pos().x() // (self.star_size + 2)
        if 0 <= star_index < self.max_rating:
            self.rating = star_index + 1
            self.rating_changed.emit(int(self.rating))
            self.update()
    
    def mouseMoveEvent(self, event):
        """Fare hareketi"""
        if self.read_only:
            return
        
        star_index = event.pos().x() // (self.star_size + 2)
        if 0 <= star_index < self.max_rating:
            self.hovered_star = star_index
        else:
            self.hovered_star = -1
        self.update()
    
    def leaveEvent(self, event):
        """Fare widget'tan çıktı"""
        if not self.read_only:
            self.hovered_star = -1
            self.update()

class CategorySidebar(QWidget):
    """Kategori kenar çubuğu"""
    
    category_selected = pyqtSignal(str)
    
    def __init__(self, dark_mode: bool = False):
        super().__init__()
        self.dark_mode = dark_mode
        self.categories = [
            ("Tümü", "📱", 0),
            ("Yüklü", "✅", 0),
            ("Güncellemeler", "🔄", 0),
            ("---", "", 0),  # Ayırıcı
            ("Sistem", "⚙️", 0),
            ("Geliştirme", "💻", 0),
            ("İnternet", "🌐", 0),
            ("Multimedya", "🎵", 0),
            ("Grafik", "🎨", 0),
            ("Oyunlar", "🎮", 0),
            ("Ofis", "📄", 0),
            ("Eğitim", "📚", 0),
            ("Araçlar", "🔧", 0)
        ]
        self.selected_category = "Tümü"
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        
        # Başlık
        title_label = QLabel("Kategoriler")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # Kategori butonları
        self.category_buttons = {}
        for category, icon, count in self.categories:
            if category == "---":
                # Ayırıcı çizgi
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet("color: #ddd;")
                layout.addWidget(line)
                continue
            
            button = QPushButton(f"{icon} {category}")
            button.setCheckable(True)
            button.setChecked(category == self.selected_category)
            button.clicked.connect(lambda checked, cat=category: self.select_category(cat))
            
            self.category_buttons[category] = button
            layout.addWidget(button)
        
        layout.addStretch()
    
    def apply_theme(self):
        """Tema uygula"""
        if self.dark_mode:
            style = """
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: transparent;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QPushButton:checked {
                    background-color: #2196f3;
                    color: white;
                }
            """
        else:
            style = """
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: transparent;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:checked {
                    background-color: #2196f3;
                    color: white;
                }
            """
        
        for button in self.category_buttons.values():
            button.setStyleSheet(style)
    
    def select_category(self, category: str):
        """Kategori seç"""
        # Önceki seçimi temizle
        if self.selected_category in self.category_buttons:
            self.category_buttons[self.selected_category].setChecked(False)
        
        # Yeni seçim
        self.selected_category = category
        if category in self.category_buttons:
            self.category_buttons[category].setChecked(True)
        
        self.category_selected.emit(category)
    
    def update_category_counts(self, counts: Dict[str, int]):
        """Kategori sayılarını güncelle"""
        for category, count in counts.items():
            if category in self.category_buttons:
                button = self.category_buttons[category]
                # Buton metnini güncelle
                icon = ""
                for cat, ic, _ in self.categories:
                    if cat == category:
                        icon = ic
                        break
                
                if count > 0:
                    button.setText(f"{icon} {category} ({count})")
                else:
                    button.setText(f"{icon} {category}")

class SearchBar(QWidget):
    """Arama çubuğu"""
    
    search_requested = pyqtSignal(str)
    filter_changed = pyqtSignal(dict)
    
    def __init__(self, dark_mode: bool = False):
        super().__init__()
        self.dark_mode = dark_mode
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Arama kutusu
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Uygulama ara...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.on_search_requested)
        layout.addWidget(self.search_input, 1)
        
        # Arama butonu
        self.search_button = QPushButton("🔍")
        self.search_button.setFixedSize(32, 32)
        self.search_button.clicked.connect(self.on_search_requested)
        layout.addWidget(self.search_button)
        
        # Filtre butonu
        self.filter_button = QPushButton("🔽")
        self.filter_button.setFixedSize(32, 32)
        self.filter_button.clicked.connect(self.show_filter_menu)
        layout.addWidget(self.filter_button)
    
    def apply_theme(self):
        """Tema uygula"""
        if self.dark_mode:
            style = """
                QLineEdit {
                    padding: 8px 12px;
                    border: 1px solid #555;
                    border-radius: 6px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border-color: #2196f3;
                }
                QPushButton {
                    border: 1px solid #555;
                    border-radius: 6px;
                    background-color: #404040;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
            """
        else:
            style = """
                QLineEdit {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    background-color: white;
                    color: #333;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border-color: #2196f3;
                }
                QPushButton {
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    background-color: #f5f5f5;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """
        
        self.setStyleSheet(style)
    
    def on_search_changed(self):
        """Arama metni değişti"""
        # Gerçek zamanlı arama (debounce ile)
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.on_search_requested)
        self.search_timer.start(300)  # 300ms bekle
    
    def on_search_requested(self):
        """Arama yapıldı"""
        query = self.search_input.text().strip()
        self.search_requested.emit(query)
    
    def show_filter_menu(self):
        """Filtre menüsünü göster"""
        menu = QMenu(self)
        
        # Sıralama seçenekleri
        sort_menu = menu.addMenu("Sırala")
        
        sort_options = [
            ("Ada göre", "name"),
            ("Kategoriye göre", "category"),
            ("Geliştiriciye göre", "developer"),
            ("Puana göre", "rating"),
            ("İndirme sayısına göre", "downloads")
        ]
        
        for text, value in sort_options:
            action = sort_menu.addAction(text)
            action.triggered.connect(lambda checked, v=value: self.filter_changed.emit({"sort": v}))
        
        menu.addSeparator()
        
        # Görünüm seçenekleri
        view_menu = menu.addMenu("Görünüm")
        
        view_options = [
            ("Izgara", "grid"),
            ("Liste", "list"),
            ("Detaylı", "detailed")
        ]
        
        for text, value in view_options:
            action = view_menu.addAction(text)
            action.triggered.connect(lambda checked, v=value: self.filter_changed.emit({"view": v}))
        
        # Menüyü göster
        menu.exec(self.filter_button.mapToGlobal(self.filter_button.rect().bottomLeft())) 