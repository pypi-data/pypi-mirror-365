"""
Cloud Settings - Görünüm Sayfası
Tema, duvar kağıdı, dock ve UI ayarları
"""

from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from .base_page import BasePage

class AppearancePage(BasePage):
    """Görünüm ayarları sayfası"""
    
    def __init__(self, kernel=None, preview_manager=None):
        super().__init__("appearance", "Görünüm", "🎨", kernel, preview_manager)
    
    def setup_ui(self):
        """UI kurulumu"""
        super().setup_ui()
        
        # Tema ayarları
        self.setup_theme_section()
        
        # Duvar kağıdı ayarları
        self.setup_wallpaper_section()
        
        # Dock ayarları
        self.setup_dock_section()
        
        # Topbar ayarları
        self.setup_topbar_section()
        
        # Renk ve efekt ayarları
        self.setup_colors_section()
        
        self.add_spacer()
    
    def setup_theme_section(self):
        """Tema ayarları bölümü"""
        group = self.add_group("Tema")
        layout = QVBoxLayout(group)
        
        # Tema seçimi
        theme_widget = QWidget()
        theme_layout = QHBoxLayout(theme_widget)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tema butonları
        self.theme_buttons = QButtonGroup()
        
        themes = [
            ("light", "☀️ Açık", "Açık renkli arayüz"),
            ("dark", "🌙 Koyu", "Koyu renkli arayüz"),
            ("auto", "🔄 Otomatik", "Sistem temasını takip et")
        ]
        
        for theme_id, theme_name, theme_desc in themes:
            theme_btn = QRadioButton()
            theme_btn.setObjectName(f"theme_{theme_id}")
            
            # Özel tema kartı
            card = QWidget()
            card.setFixedSize(120, 80)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 8, 8, 8)
            
            icon_label = QLabel(theme_name.split()[0])
            icon_label.setStyleSheet("font-size: 24px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(icon_label)
            
            name_label = QLabel(theme_name.split()[1])
            name_label.setStyleSheet("font-size: 12px; font-weight: 600;")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(name_label)
            
            # Kart stili
            card.setStyleSheet(f"""
                QWidget {{
                    background-color: #ffffff;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                }}
                
                QWidget:hover {{
                    border-color: #007bff;
                }}
            """)
            
            # Buton ve kart bağlantısı
            theme_btn.toggled.connect(lambda checked, tid=theme_id: self.on_theme_changed(tid, checked))
            card.mousePressEvent = lambda e, btn=theme_btn: btn.setChecked(True)
            
            self.theme_buttons.addButton(theme_btn)
            self.widgets[f"theme_{theme_id}"] = theme_btn
            
            btn_layout = QVBoxLayout()
            btn_layout.addWidget(theme_btn)
            btn_layout.addWidget(card)
            
            theme_layout.addLayout(btn_layout)
        
        theme_layout.addStretch()
        layout.addWidget(theme_widget)
        
        # Tema açıklaması
        self.theme_description = QLabel("Sistem temasını otomatik olarak takip eder")
        self.theme_description.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.theme_description)
    
    def setup_wallpaper_section(self):
        """Duvar kağıdı ayarları bölümü"""
        group = self.add_group("Duvar Kağıdı")
        layout = QVBoxLayout(group)
        
        # Duvar kağıdı seçimi
        self.add_file_picker(
            layout, 
            "Duvar Kağıdı", 
            "wallpaper_path",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.gif *.webp)",
            "Masaüstü arka plan resmi seçin"
        )
        
        # Duvar kağıdı modu
        self.add_combobox(
            layout,
            "Görüntüleme Modu",
            "wallpaper_mode",
            ["Sığdır", "Uzat", "Döşe", "Merkez", "Doldur"],
            "Duvar kağıdının nasıl görüntüleneceğini belirler"
        )
        
        # Duvar kağıdı önizlemesi
        self.wallpaper_preview = QLabel()
        self.wallpaper_preview.setFixedSize(200, 120)
        self.wallpaper_preview.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                color: #6c757d;
            }
        """)
        self.wallpaper_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wallpaper_preview.setText("Önizleme")
        
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Önizleme:"))
        preview_layout.addWidget(self.wallpaper_preview)
        preview_layout.addStretch()
        
        layout.addLayout(preview_layout)
    
    def setup_dock_section(self):
        """Dock ayarları bölümü"""
        group = self.add_group("Dock")
        layout = QVBoxLayout(group)
        
        # Dock konumu
        self.add_combobox(
            layout,
            "Konum",
            "dock_position", 
            ["Alt", "Sol", "Sağ", "Üst"],
            "Dock'un ekrandaki konumu"
        )
        
        # Dock boyutu
        self.add_slider(
            layout,
            "Boyut",
            "dock_size",
            32, 128, 64,
            "Dock simgelerinin boyutu (piksel)"
        )
        
        # Otomatik gizleme
        self.add_checkbox(
            layout,
            "Otomatik gizle",
            "dock_autohide",
            "Dock'u kullanılmadığında otomatik olarak gizle"
        )
        
        # Dock efektleri
        self.add_checkbox(
            layout,
            "Büyütme efekti",
            "dock_magnification",
            "Fare üzerine gelindiğinde simgeleri büyüt"
        )
    
    def setup_topbar_section(self):
        """Topbar ayarları bölümü"""
        group = self.add_group("Üst Çubuk")
        layout = QVBoxLayout(group)
        
        # Topbar öğeleri
        self.add_checkbox(
            layout,
            "Saati göster",
            "show_clock",
            "Üst çubukta saat ve tarihi göster"
        )
        
        self.add_checkbox(
            layout,
            "Kullanıcı menüsünü göster", 
            "show_user",
            "Üst çubukta kullanıcı menüsünü göster"
        )
        
        self.add_checkbox(
            layout,
            "Bildirimleri göster",
            "show_notifications", 
            "Üst çubukta bildirim simgesini göster"
        )
        
        self.add_checkbox(
            layout,
            "Widget'ları göster",
            "show_widgets",
            "Üst çubukta widget butonlarını göster"
        )
    
    def setup_colors_section(self):
        """Renk ve efekt ayarları bölümü"""
        group = self.add_group("Renkler ve Efektler")
        layout = QVBoxLayout(group)
        
        # Vurgu rengi
        self.add_color_picker(
            layout,
            "Vurgu Rengi",
            "accent_color",
            "#007bff",
            "Butonlar ve vurgular için kullanılan ana renk"
        )
        
        # Şeffaflık
        self.add_checkbox(
            layout,
            "Şeffaflık efektleri",
            "transparency",
            "Pencere ve menülerde şeffaflık efektleri kullan"
        )
        
        # Animasyonlar
        self.add_checkbox(
            layout,
            "Animasyonları etkinleştir",
            "animations",
            "Pencere geçişleri ve UI animasyonları"
        )
        
        # Gölge efektleri
        self.add_checkbox(
            layout,
            "Gölge efektleri",
            "shadows",
            "Pencere ve menülerde gölge efektleri"
        )
    
    def on_theme_changed(self, theme_id: str, checked: bool):
        """Tema değişti"""
        if checked:
            self.on_setting_changed("theme", theme_id)
            
            # Tema açıklamasını güncelle
            descriptions = {
                "light": "Açık renkli arayüz kullanılıyor",
                "dark": "Koyu renkli arayüz kullanılıyor", 
                "auto": "Sistem temasını otomatik olarak takip eder"
            }
            self.theme_description.setText(descriptions.get(theme_id, ""))
    
    def update_ui(self):
        """UI'yi ayarlara göre güncelle"""
        super().update_ui()
        
        # Tema butonlarını güncelle
        theme = self.settings.get("theme", "auto")
        for theme_id in ["light", "dark", "auto"]:
            widget_key = f"theme_{theme_id}"
            if widget_key in self.widgets:
                self.widgets[widget_key].setChecked(theme_id == theme)
        
        # Duvar kağıdı önizlemesini güncelle
        self.update_wallpaper_preview()
    
    def update_wallpaper_preview(self):
        """Duvar kağıdı önizlemesini güncelle"""
        wallpaper_path = self.settings.get("wallpaper_path", "")
        
        if wallpaper_path and Path(wallpaper_path).exists():
            try:
                from PyQt6.QtGui import QPixmap
                
                pixmap = QPixmap(wallpaper_path)
                if not pixmap.isNull():
                    # Önizleme boyutuna ölçekle
                    scaled_pixmap = pixmap.scaled(
                        self.wallpaper_preview.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.wallpaper_preview.setPixmap(scaled_pixmap)
                else:
                    self.wallpaper_preview.setText("Geçersiz resim")
            except Exception as e:
                self.wallpaper_preview.setText("Yüklenemedi")
                self.logger.warning(f"Failed to load wallpaper preview: {e}")
        else:
            from PyQt6.QtGui import QPixmap
            self.wallpaper_preview.setText("Önizleme")
            self.wallpaper_preview.setPixmap(QPixmap())  # Temizle 