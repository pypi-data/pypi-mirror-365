"""
PyCloud OS Cloud Settings
Rain arayüzü için özelleştirme ve sistemsel ayarları yöneten uygulama
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not available for Cloud Settings")
    sys.exit(1)

class SettingsPage(QWidget):
    """Ayar sayfası temel sınıfı"""
    
    settings_changed = pyqtSignal(str, dict)  # category, settings
    
    def __init__(self, title: str, icon: str = "⚙️"):
        super().__init__()
        self.title = title
        self.icon = icon
        self.settings = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu - alt sınıflarda override edilecek"""
        layout = QVBoxLayout(self)
        
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
    
    def load_settings(self, settings: Dict):
        """Ayarları yükle"""
        self.settings = settings
        self.update_ui()
    
    def update_ui(self):
        """UI'yi ayarlara göre güncelle"""
        pass
    
    def get_settings(self) -> Dict:
        """Mevcut ayarları al"""
        return self.settings.copy()

class AppearancePage(SettingsPage):
    """Görünüm ayarları sayfası"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("AppearancePage")
        super().__init__("Görünüm", "🎨")
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Tema seçimi
        theme_group = QGroupBox("Tema")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_light = QRadioButton("Açık Tema")
        self.theme_dark = QRadioButton("Koyu Tema")
        self.theme_auto = QRadioButton("Sistem Teması")
        
        theme_layout.addWidget(self.theme_light)
        theme_layout.addWidget(self.theme_dark)
        theme_layout.addWidget(self.theme_auto)
        
        layout.addWidget(theme_group)
        
        # Duvar kağıdı
        wallpaper_group = QGroupBox("Duvar Kağıdı")
        wallpaper_layout = QVBoxLayout(wallpaper_group)
        
        wallpaper_select_layout = QHBoxLayout()
        self.wallpaper_path = QLineEdit()
        self.wallpaper_path.setPlaceholderText("Duvar kağıdı dosyası seçin...")
        wallpaper_browse = QPushButton("Gözat")
        wallpaper_browse.clicked.connect(self.browse_wallpaper)
        
        wallpaper_select_layout.addWidget(self.wallpaper_path)
        wallpaper_select_layout.addWidget(wallpaper_browse)
        wallpaper_layout.addLayout(wallpaper_select_layout)
        
        # Duvar kağıdı modu
        wallpaper_mode_layout = QHBoxLayout()
        wallpaper_mode_layout.addWidget(QLabel("Mod:"))
        
        self.wallpaper_mode = QComboBox()
        self.wallpaper_mode.addItems(["Sığdır", "Uzat", "Döşe", "Merkez", "Doldur"])
        wallpaper_mode_layout.addWidget(self.wallpaper_mode)
        wallpaper_mode_layout.addStretch()
        
        wallpaper_layout.addLayout(wallpaper_mode_layout)
        layout.addWidget(wallpaper_group)
        
        # Dock ayarları
        dock_group = QGroupBox("Dock")
        dock_layout = QFormLayout(dock_group)
        
        self.dock_position = QComboBox()
        self.dock_position.addItems(["Alt", "Sol", "Sağ", "Üst"])
        dock_layout.addRow("Konum:", self.dock_position)
        
        self.dock_size = QSlider(Qt.Orientation.Horizontal)
        self.dock_size.setRange(32, 128)
        self.dock_size.setValue(64)
        self.dock_size_label = QLabel("64px")
        self.dock_size.valueChanged.connect(lambda v: self.dock_size_label.setText(f"{v}px"))
        
        dock_size_layout = QHBoxLayout()
        dock_size_layout.addWidget(self.dock_size)
        dock_size_layout.addWidget(self.dock_size_label)
        dock_layout.addRow("Boyut:", dock_size_layout)
        
        self.dock_autohide = QCheckBox("Otomatik gizle")
        dock_layout.addRow("", self.dock_autohide)
        
        layout.addWidget(dock_group)
        
        # Topbar ayarları
        topbar_group = QGroupBox("Üst Çubuk")
        topbar_layout = QFormLayout(topbar_group)
        
        self.show_clock = QCheckBox("Saati göster")
        self.show_clock.setChecked(True)
        topbar_layout.addRow("", self.show_clock)
        
        self.show_user = QCheckBox("Kullanıcı menüsünü göster")
        self.show_user.setChecked(True)
        topbar_layout.addRow("", self.show_user)
        
        self.show_notifications = QCheckBox("Bildirimleri göster")
        self.show_notifications.setChecked(True)
        topbar_layout.addRow("", self.show_notifications)
        
        layout.addWidget(topbar_group)
        
        layout.addStretch()
        
        # Sinyal bağlantıları
        self.theme_light.toggled.connect(self.on_settings_changed)
        self.theme_dark.toggled.connect(self.on_settings_changed)
        self.theme_auto.toggled.connect(self.on_settings_changed)
        self.wallpaper_path.textChanged.connect(self.on_settings_changed)
        self.wallpaper_mode.currentTextChanged.connect(self.on_settings_changed)
        self.dock_position.currentTextChanged.connect(self.on_settings_changed)
        self.dock_size.valueChanged.connect(self.on_settings_changed)
        self.dock_autohide.toggled.connect(self.on_settings_changed)
        self.show_clock.toggled.connect(self.on_settings_changed)
        self.show_user.toggled.connect(self.on_settings_changed)
        self.show_notifications.toggled.connect(self.on_settings_changed)
    
    def browse_wallpaper(self):
        """Duvar kağıdı dosyası seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Duvar Kağıdı Seç",
            str(Path.home()),
            "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        
        if file_path:
            # Wallpaper manager'ı kullanarak ayarla
            try:
                if self.kernel:
                    wallpaper_manager = self.kernel.get_module("wallpaper")
                    if wallpaper_manager:
                        # Önce system/wallpapers'a kopyala
                        if wallpaper_manager.add_wallpaper(file_path):
                            # Sonra yeni dosyayı ayarla
                            new_file_name = Path(file_path).name
                            system_wallpaper_path = Path("system/wallpapers") / new_file_name
                            
                            if wallpaper_manager.set_wallpaper(str(system_wallpaper_path)):
                                self.wallpaper_path.setText(str(system_wallpaper_path))
                                QMessageBox.information(self, "Başarılı", "Duvar kağıdı başarıyla ayarlandı!")
                            else:
                                self.wallpaper_path.setText(file_path)
                                QMessageBox.warning(self, "Uyarı", "Duvar kağıdı ayarlanamadı, sadece yol güncellendi.")
                        else:
                            # Direkt dosya yolunu kullan
                            self.wallpaper_path.setText(file_path)
                    else:
                        # Wallpaper manager yoksa sadece yol ayarla
                        self.wallpaper_path.setText(file_path)
                else:
                    self.wallpaper_path.setText(file_path)
                    
            except Exception as e:
                self.logger.error(f"Wallpaper setting error: {e}")
                self.wallpaper_path.setText(file_path)
    
    def on_settings_changed(self):
        """Ayar değişti"""
        settings = {
            "theme": "light" if self.theme_light.isChecked() else "dark" if self.theme_dark.isChecked() else "auto",
            "wallpaper_path": self.wallpaper_path.text(),
            "wallpaper_mode": self.wallpaper_mode.currentText().lower(),
            "dock_position": self.dock_position.currentText().lower(),
            "dock_size": self.dock_size.value(),
            "dock_autohide": self.dock_autohide.isChecked(),
            "show_clock": self.show_clock.isChecked(),
            "show_user": self.show_user.isChecked(),
            "show_notifications": self.show_notifications.isChecked()
        }
        
        self.settings = settings
        self.settings_changed.emit("appearance", settings)
    
    def update_ui(self):
        """UI'yi ayarlara göre güncelle"""
        theme = self.settings.get("theme", "auto")
        if theme == "light":
            self.theme_light.setChecked(True)
        elif theme == "dark":
            self.theme_dark.setChecked(True)
        else:
            self.theme_auto.setChecked(True)
        
        self.wallpaper_path.setText(self.settings.get("wallpaper_path", ""))
        
        wallpaper_mode = self.settings.get("wallpaper_mode", "sığdır")
        index = self.wallpaper_mode.findText(wallpaper_mode.title())
        if index >= 0:
            self.wallpaper_mode.setCurrentIndex(index)
        
        dock_position = self.settings.get("dock_position", "alt")
        index = self.dock_position.findText(dock_position.title())
        if index >= 0:
            self.dock_position.setCurrentIndex(index)
        
        self.dock_size.setValue(self.settings.get("dock_size", 64))
        self.dock_autohide.setChecked(self.settings.get("dock_autohide", False))
        self.show_clock.setChecked(self.settings.get("show_clock", True))
        self.show_user.setChecked(self.settings.get("show_user", True))
        self.show_notifications.setChecked(self.settings.get("show_notifications", True))

class SystemPage(SettingsPage):
    """Sistem ayarları sayfası"""
    
    def __init__(self):
        super().__init__("Sistem", "💻")
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Başlangıç ayarları
        startup_group = QGroupBox("Başlangıç")
        startup_layout = QVBoxLayout(startup_group)
        
        self.auto_login = QCheckBox("Otomatik giriş")
        startup_layout.addWidget(self.auto_login)
        
        self.startup_sound = QCheckBox("Başlangıç sesi")
        startup_layout.addWidget(self.startup_sound)
        
        layout.addWidget(startup_group)
        
        # Güvenlik ayarları
        security_group = QGroupBox("Güvenlik")
        security_layout = QFormLayout(security_group)
        
        self.session_timeout = QSpinBox()
        self.session_timeout.setRange(0, 1440)  # 0-24 saat
        self.session_timeout.setValue(0)
        self.session_timeout.setSuffix(" dakika (0 = sınırsız)")
        security_layout.addRow("Oturum zaman aşımı:", self.session_timeout)
        
        self.require_password = QCheckBox("Uyku modundan çıkarken şifre iste")
        security_layout.addRow("", self.require_password)
        
        layout.addWidget(security_group)
        
        # Performans ayarları
        performance_group = QGroupBox("Performans")
        performance_layout = QFormLayout(performance_group)
        
        self.animations = QCheckBox("Animasyonları etkinleştir")
        self.animations.setChecked(True)
        performance_layout.addRow("", self.animations)
        
        self.transparency = QCheckBox("Saydamlık efektleri")
        self.transparency.setChecked(True)
        performance_layout.addRow("", self.transparency)
        
        self.memory_limit = QSpinBox()
        self.memory_limit.setRange(256, 8192)
        self.memory_limit.setValue(1024)
        self.memory_limit.setSuffix(" MB")
        performance_layout.addRow("Bellek sınırı:", self.memory_limit)
        
        layout.addWidget(performance_group)
        
        # Sistem bilgileri
        info_group = QGroupBox("Sistem Bilgileri")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("İşletim Sistemi:", QLabel("PyCloud OS 0.9.0-dev"))
        info_layout.addRow("Python Sürümü:", QLabel(f"{sys.version.split()[0]}"))
        info_layout.addRow("PyQt Sürümü:", QLabel("6.x"))
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        # Sinyal bağlantıları
        self.auto_login.toggled.connect(self.on_settings_changed)
        self.startup_sound.toggled.connect(self.on_settings_changed)
        self.session_timeout.valueChanged.connect(self.on_settings_changed)
        self.require_password.toggled.connect(self.on_settings_changed)
        self.animations.toggled.connect(self.on_settings_changed)
        self.transparency.toggled.connect(self.on_settings_changed)
        self.memory_limit.valueChanged.connect(self.on_settings_changed)
    
    def on_settings_changed(self):
        """Ayar değişti"""
        settings = {
            "auto_login": self.auto_login.isChecked(),
            "startup_sound": self.startup_sound.isChecked(),
            "session_timeout": self.session_timeout.value(),
            "require_password": self.require_password.isChecked(),
            "animations": self.animations.isChecked(),
            "transparency": self.transparency.isChecked(),
            "memory_limit": self.memory_limit.value()
        }
        
        self.settings = settings
        self.settings_changed.emit("system", settings)
    
    def update_ui(self):
        """UI'yi ayarlara göre güncelle"""
        self.auto_login.setChecked(self.settings.get("auto_login", False))
        self.startup_sound.setChecked(self.settings.get("startup_sound", True))
        self.session_timeout.setValue(self.settings.get("session_timeout", 0))
        self.require_password.setChecked(self.settings.get("require_password", True))
        self.animations.setChecked(self.settings.get("animations", True))
        self.transparency.setChecked(self.settings.get("transparency", True))
        self.memory_limit.setValue(self.settings.get("memory_limit", 1024))

class NotificationsPage(SettingsPage):
    """Bildirim ayarları sayfası"""
    
    def __init__(self):
        super().__init__("Bildirimler", "🔔")
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Genel ayarlar
        general_group = QGroupBox("Genel")
        general_layout = QVBoxLayout(general_group)
        
        self.enable_notifications = QCheckBox("Bildirimleri etkinleştir")
        self.enable_notifications.setChecked(True)
        general_layout.addWidget(self.enable_notifications)
        
        self.notification_sound = QCheckBox("Bildirim sesi")
        self.notification_sound.setChecked(True)
        general_layout.addWidget(self.notification_sound)
        
        self.show_preview = QCheckBox("Bildirim önizlemesi göster")
        self.show_preview.setChecked(True)
        general_layout.addWidget(self.show_preview)
        
        layout.addWidget(general_group)
        
        # Görünüm ayarları
        display_group = QGroupBox("Görünüm")
        display_layout = QFormLayout(display_group)
        
        self.notification_position = QComboBox()
        self.notification_position.addItems(["Sağ Üst", "Sol Üst", "Sağ Alt", "Sol Alt", "Merkez"])
        display_layout.addRow("Konum:", self.notification_position)
        
        self.notification_duration = QSpinBox()
        self.notification_duration.setRange(1, 30)
        self.notification_duration.setValue(5)
        self.notification_duration.setSuffix(" saniye")
        display_layout.addRow("Süre:", self.notification_duration)
        
        self.max_notifications = QSpinBox()
        self.max_notifications.setRange(1, 10)
        self.max_notifications.setValue(3)
        display_layout.addRow("Maksimum sayı:", self.max_notifications)
        
        layout.addWidget(display_group)
        
        # Uygulama bildirimleri
        apps_group = QGroupBox("Uygulama Bildirimleri")
        apps_layout = QVBoxLayout(apps_group)
        
        # Uygulama listesi (örnek)
        app_list = QListWidget()
        app_items = [
            ("Sistem", True),
            ("Güvenlik", True),
            ("Güncellemeler", True),
            ("Clapp", False),
            ("Cloud Files", False)
        ]
        
        for app_name, enabled in app_items:
            item = QListWidgetItem(app_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
            app_list.addItem(item)
        
        apps_layout.addWidget(app_list)
        layout.addWidget(apps_group)
        
        layout.addStretch()
        
        # Sinyal bağlantıları
        self.enable_notifications.toggled.connect(self.on_settings_changed)
        self.notification_sound.toggled.connect(self.on_settings_changed)
        self.show_preview.toggled.connect(self.on_settings_changed)
        self.notification_position.currentTextChanged.connect(self.on_settings_changed)
        self.notification_duration.valueChanged.connect(self.on_settings_changed)
        self.max_notifications.valueChanged.connect(self.on_settings_changed)
    
    def on_settings_changed(self):
        """Ayar değişti"""
        settings = {
            "enable_notifications": self.enable_notifications.isChecked(),
            "notification_sound": self.notification_sound.isChecked(),
            "show_preview": self.show_preview.isChecked(),
            "notification_position": self.notification_position.currentText().lower().replace(" ", "_"),
            "notification_duration": self.notification_duration.value(),
            "max_notifications": self.max_notifications.value()
        }
        
        self.settings = settings
        self.settings_changed.emit("notifications", settings)
    
    def update_ui(self):
        """UI'yi ayarlara göre güncelle"""
        self.enable_notifications.setChecked(self.settings.get("enable_notifications", True))
        self.notification_sound.setChecked(self.settings.get("notification_sound", True))
        self.show_preview.setChecked(self.settings.get("show_preview", True))
        
        position = self.settings.get("notification_position", "sağ_üst").replace("_", " ").title()
        index = self.notification_position.findText(position)
        if index >= 0:
            self.notification_position.setCurrentIndex(index)
        
        self.notification_duration.setValue(self.settings.get("notification_duration", 5))
        self.max_notifications.setValue(self.settings.get("max_notifications", 3))

class CloudSettings(QMainWindow):
    """Ana ayarlar uygulaması"""
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("CloudSettings")
        
        # Ayar dosyası
        self.settings_file = Path("system/config/ui_settings.json")
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Ayarlar
        self.all_settings = {}
        
        # Sayfalar
        self.pages = {}
        
        # UI kurulumu
        self.setup_ui()
        self.load_settings()
        
        # İlk sayfa
        self.show_page("appearance")
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle("PyCloud Ayarları")
        self.setGeometry(100, 100, 800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        
        # Sol panel (kategori listesi)
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Sağ panel (ayar sayfaları)
        self.setup_content_area()
        main_layout.addWidget(self.content_area, 1)
        
        # Durum çubuğu
        self.setup_statusbar()
    
    def setup_sidebar(self):
        """Sol panel kurulumu"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-right: 1px solid #ddd;
            }
        """)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık
        title_label = QLabel("Ayarlar")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Kategori listesi
        self.category_list = QListWidget()
        self.category_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 12px 8px;
                border-radius: 6px;
                margin: 2px 0;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        
        # Kategoriler
        categories = [
            ("appearance", "🎨 Görünüm"),
            ("system", "💻 Sistem"),
            ("notifications", "🔔 Bildirimler")
        ]
        
        for category_id, category_name in categories:
            item = QListWidgetItem(category_name)
            item.setData(Qt.ItemDataRole.UserRole, category_id)
            self.category_list.addItem(item)
        
        self.category_list.setCurrentRow(0)
        self.category_list.currentItemChanged.connect(self.on_category_changed)
        
        layout.addWidget(self.category_list)
        layout.addStretch()
        
        # Alt butonlar
        buttons_layout = QVBoxLayout()
        
        # Varsayılanlara dön
        reset_button = QPushButton("Varsayılanlara Dön")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        reset_button.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(reset_button)
        
        # Uygula
        apply_button = QPushButton("Uygula")
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_button.clicked.connect(self.apply_settings)
        buttons_layout.addWidget(apply_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_content_area(self):
        """İçerik alanı kurulumu"""
        self.content_area = QStackedWidget()
        
        # Sayfaları oluştur
        self.pages["appearance"] = AppearancePage(self.kernel)
        self.pages["system"] = SystemPage()
        self.pages["notifications"] = NotificationsPage()
        
        # Sayfaları ekle
        for page in self.pages.values():
            self.content_area.addWidget(page)
            page.settings_changed.connect(self.on_settings_changed)
    
    def setup_statusbar(self):
        """Durum çubuğu kurulumu"""
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Hazır")
        self.status_bar.addWidget(self.status_label)
        
        # Sağ tarafta son kaydetme zamanı
        self.last_saved_label = QLabel("")
        self.status_bar.addPermanentWidget(self.last_saved_label)
    
    def on_category_changed(self, current, previous):
        """Kategori değişti"""
        if current:
            category_id = current.data(Qt.ItemDataRole.UserRole)
            self.show_page(category_id)
    
    def show_page(self, category_id: str):
        """Sayfa göster"""
        if category_id in self.pages:
            page = self.pages[category_id]
            self.content_area.setCurrentWidget(page)
            
            # Sayfaya ayarları yükle
            if category_id in self.all_settings:
                page.load_settings(self.all_settings[category_id])
    
    def on_settings_changed(self, category: str, settings: Dict):
        """Ayar değişti"""
        self.all_settings[category] = settings
        self.status_label.setText(f"{category.title()} ayarları değiştirildi")
    
    def load_settings(self):
        """Ayarları yükle"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.all_settings = json.load(f)
                
                self.logger.info("Settings loaded successfully")
                self.status_label.setText("Ayarlar yüklendi")
            else:
                # Varsayılan ayarlar
                self.all_settings = self.get_default_settings()
                self.save_settings()
                
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self.all_settings = self.get_default_settings()
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_settings, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Settings saved successfully")
            self.last_saved_label.setText(f"Son kayıt: {datetime.now().strftime('%H:%M:%S')}")
            
            # Kernel'e bildir
            if self.kernel:
                config_manager = self.kernel.get_module("config")
                if config_manager:
                    config_manager.set("ui_settings", self.all_settings)
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilemedi:\n{e}")
    
    def apply_settings(self):
        """Ayarları uygula"""
        self.save_settings()
        self.status_label.setText("Ayarlar uygulandı")
        
        # Rain UI'ye bildir
        if self.kernel:
            rain_ui = self.kernel.get_module("rain_ui")
            if rain_ui:
                rain_ui.apply_settings(self.all_settings)
    
    def reset_to_defaults(self):
        """Varsayılan ayarlara dön"""
        reply = QMessageBox.question(
            self, "Varsayılanlara Dön",
            "Tüm ayarları varsayılan değerlere döndürmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.all_settings = self.get_default_settings()
            
            # Tüm sayfaları güncelle
            for category_id, page in self.pages.items():
                if category_id in self.all_settings:
                    page.load_settings(self.all_settings[category_id])
            
            self.save_settings()
            self.status_label.setText("Varsayılan ayarlar yüklendi")
    
    def get_default_settings(self) -> Dict:
        """Varsayılan ayarları al"""
        return {
            "appearance": {
                "theme": "auto",
                "wallpaper_path": "",
                "wallpaper_mode": "sığdır",
                "dock_position": "alt",
                "dock_size": 64,
                "dock_autohide": False,
                "show_clock": True,
                "show_user": True,
                "show_notifications": True
            },
            "system": {
                "auto_login": False,
                "startup_sound": True,
                "session_timeout": 0,
                "require_password": True,
                "animations": True,
                "transparency": True,
                "memory_limit": 1024
            },
            "notifications": {
                "enable_notifications": True,
                "notification_sound": True,
                "show_preview": True,
                "notification_position": "sağ_üst",
                "notification_duration": 5,
                "max_notifications": 3
            }
        }
    
    def closeEvent(self, event):
        """Pencere kapatılıyor"""
        # Değişiklikleri kaydet
        self.save_settings()
        event.accept()

def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setApplicationName("PyCloud Settings")
    app.setApplicationVersion("1.0.0")
    
    # Ana pencere
    window = CloudSettings()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 