"""
Cloud Settings - Modern Ana Uygulama
macOS Big Sur/Monterey tarzı sistem ayarları
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

from .pages import (
    AppearancePage, SystemPage, NotificationsPage, 
    WidgetsPage, PrivacyPage, NetworkPage
)
from .widgets import ModernSearchBar, SettingsCard, LivePreviewWidget
from .preview import LivePreviewManager

class CloudSettings(QMainWindow):
    """Modern Cloud Settings Ana Uygulaması"""
    
    # Sinyaller
    settings_changed = pyqtSignal(str, dict)  # category, settings
    theme_changed = pyqtSignal(str)  # theme_name
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("CloudSettings")
        
        # Ayar dosyaları
        self.settings_file = Path("system/config/ui_settings.json")
        self.history_file = Path("system/config/settings_history.json")
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Ayarlar ve geçmiş
        self.all_settings = {}
        self.settings_history = []
        self.current_theme = "auto"
        
        # Sayfalar ve widget'lar
        self.pages = {}
        self.search_results = []
        
        # Canlı önizleme yöneticisi
        self.preview_manager = LivePreviewManager(self.kernel)
        
        # UI kurulumu
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        self.apply_theme()
        
        # İlk sayfa
        self.show_page("appearance")
        
        self.logger.info("Cloud Settings v2.0.0 initialized")
    
    def setup_ui(self):
        """Modern UI kurulumu"""
        self.setWindowTitle("Cloud Settings")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sol panel (sidebar)
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Sağ panel (content)
        self.setup_content_area()
        main_layout.addWidget(self.content_area, 1)
        
        # Toolbar
        self.setup_toolbar()
        
        # Status bar
        self.setup_statusbar()
        
        # Modern stil uygula
        self.apply_modern_style()
    
    def setup_sidebar(self):
        """Modern sidebar kurulumu"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(280)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık ve arama
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Ayarlar")
        title_label.setObjectName("sidebarTitle")
        header_layout.addWidget(title_label)
        
        # Arama çubuğu
        self.search_bar = ModernSearchBar()
        self.search_bar.textChanged.connect(self.on_search_changed)
        header_layout.addWidget(self.search_bar)
        
        layout.addLayout(header_layout)
        
        # Kategori listesi
        self.setup_category_list()
        layout.addWidget(self.category_list)
        
        layout.addStretch()
        
        # Alt butonlar
        self.setup_sidebar_buttons()
        layout.addLayout(self.sidebar_buttons)
    
    def setup_category_list(self):
        """Kategori listesi kurulumu"""
        self.category_list = QListWidget()
        self.category_list.setObjectName("categoryList")
        
        # Kategoriler - .cursorrules gereksinimlerine uygun
        categories = [
            ("appearance", "🎨", "Görünüm", "Tema, duvar kağıdı, dock ayarları"),
            ("widgets", "🧩", "Widget'lar", "Masaüstü widget'ları yönetimi"),
            ("system", "💻", "Sistem", "Genel sistem ayarları"),
            ("notifications", "🔔", "Bildirimler", "Bildirim tercihleri"),
            ("privacy", "🔒", "Gizlilik", "Güvenlik ve gizlilik ayarları"),
            ("network", "🌐", "Ağ", "İnternet ve ağ ayarları")
        ]
        
        for category_id, icon, title, description in categories:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, category_id)
            
            # Özel widget oluştur
            widget = SettingsCard(icon, title, description)
            item.setSizeHint(widget.sizeHint())
            
            self.category_list.addItem(item)
            self.category_list.setItemWidget(item, widget)
        
        self.category_list.setCurrentRow(0)
        self.category_list.currentItemChanged.connect(self.on_category_changed)
    
    def setup_sidebar_buttons(self):
        """Sidebar butonları kurulumu"""
        self.sidebar_buttons = QVBoxLayout()
        self.sidebar_buttons.setSpacing(10)
        
        # Canlı önizleme toggle
        self.live_preview_btn = QPushButton("🔍 Canlı Önizleme")
        self.live_preview_btn.setObjectName("livePreviewButton")
        self.live_preview_btn.setCheckable(True)
        self.live_preview_btn.setChecked(True)
        self.live_preview_btn.clicked.connect(self.toggle_live_preview)
        self.sidebar_buttons.addWidget(self.live_preview_btn)
        
        # Geri al
        self.undo_btn = QPushButton("↶ Geri Al")
        self.undo_btn.setObjectName("undoButton")
        self.undo_btn.clicked.connect(self.undo_changes)
        self.undo_btn.setEnabled(False)
        self.sidebar_buttons.addWidget(self.undo_btn)
        
        # Varsayılanlara dön
        self.reset_btn = QPushButton("🔄 Varsayılanlara Dön")
        self.reset_btn.setObjectName("resetButton")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.sidebar_buttons.addWidget(self.reset_btn)
        
        # Uygula
        self.apply_btn = QPushButton("✓ Uygula")
        self.apply_btn.setObjectName("applyButton")
        self.apply_btn.clicked.connect(self.apply_settings)
        self.sidebar_buttons.addWidget(self.apply_btn)
    
    def setup_content_area(self):
        """İçerik alanı kurulumu"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Üst kısım - sayfa başlığı ve canlı önizleme
        header_layout = QHBoxLayout()
        
        # Sayfa başlığı
        self.page_title = QLabel()
        self.page_title.setObjectName("pageTitle")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        # Canlı önizleme widget'ı
        self.live_preview_widget = LivePreviewWidget()
        self.live_preview_widget.setFixedSize(200, 120)
        header_layout.addWidget(self.live_preview_widget)
        
        content_layout.addLayout(header_layout)
        
        # Sayfa içeriği
        self.content_stack = QStackedWidget()
        self.setup_pages()
        content_layout.addWidget(self.content_stack, 1)
        
        self.content_area = content_widget
    
    def setup_pages(self):
        """Ayar sayfalarını kur"""
        # Sayfaları oluştur
        self.pages["appearance"] = AppearancePage(self.kernel, self.preview_manager)
        self.pages["widgets"] = WidgetsPage(self.kernel, self.preview_manager)
        self.pages["system"] = SystemPage(self.kernel)
        self.pages["notifications"] = NotificationsPage(self.kernel)
        self.pages["privacy"] = PrivacyPage(self.kernel)
        self.pages["network"] = NetworkPage(self.kernel)
        
        # Sayfaları stack'e ekle
        for page in self.pages.values():
            self.content_stack.addWidget(page)
            page.settings_changed.connect(self.on_settings_changed)
    
    def setup_toolbar(self):
        """Toolbar kurulumu"""
        self.toolbar = self.addToolBar("Ana")
        self.toolbar.setMovable(False)
        
        # Tema değiştirici
        theme_action = QAction("🌓", self)
        theme_action.setToolTip("Tema Değiştir")
        theme_action.triggered.connect(self.cycle_theme)
        self.toolbar.addAction(theme_action)
        
        self.toolbar.addSeparator()
        
        # Ayarları dışa aktar
        export_action = QAction("📤", self)
        export_action.setToolTip("Ayarları Dışa Aktar")
        export_action.triggered.connect(self.export_settings)
        self.toolbar.addAction(export_action)
        
        # Ayarları içe aktar
        import_action = QAction("📥", self)
        import_action.setToolTip("Ayarları İçe Aktar")
        import_action.triggered.connect(self.import_settings)
        self.toolbar.addAction(import_action)
        
        self.toolbar.addSeparator()
        
        # Yardım
        help_action = QAction("❓", self)
        help_action.setToolTip("Yardım")
        help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(help_action)
    
    def setup_statusbar(self):
        """Status bar kurulumu"""
        self.status_bar = self.statusBar()
        
        # Sol taraf - durum mesajı
        self.status_label = QLabel("Hazır")
        self.status_bar.addWidget(self.status_label)
        
        # Sağ taraf - bilgiler
        self.info_layout = QHBoxLayout()
        
        # Son kaydetme zamanı
        self.last_saved_label = QLabel("")
        self.status_bar.addPermanentWidget(self.last_saved_label)
        
        # Değişiklik sayısı
        self.changes_label = QLabel("0 değişiklik")
        self.status_bar.addPermanentWidget(self.changes_label)
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        # Canlı önizleme
        self.settings_changed.connect(self.preview_manager.update_preview)
        self.preview_manager.preview_updated.connect(self.live_preview_widget.update_preview)
        
        # Tema değişiklikleri
        self.theme_changed.connect(self.apply_theme)
    
    def apply_modern_style(self):
        """Modern stil uygula"""
        self.setStyleSheet("""
            /* Ana pencere */
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            /* Sidebar */
            QWidget#sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e9ecef;
            }
            
            /* Sidebar başlık */
            QLabel#sidebarTitle {
                font-size: 24px;
                font-weight: 700;
                color: #212529;
                margin-bottom: 10px;
            }
            
            /* Kategori listesi */
            QListWidget#categoryList {
                border: none;
                background-color: transparent;
                outline: none;
            }
            
            QListWidget#categoryList::item {
                border: none;
                margin: 2px 0;
                border-radius: 8px;
            }
            
            QListWidget#categoryList::item:selected {
                background-color: #007bff;
            }
            
            QListWidget#categoryList::item:hover {
                background-color: #f8f9fa;
            }
            
            /* Sayfa başlığı */
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
                color: #212529;
                margin-bottom: 20px;
            }
            
            /* Butonlar */
            QPushButton#livePreviewButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton#livePreviewButton:hover {
                background-color: #218838;
            }
            
            QPushButton#livePreviewButton:checked {
                background-color: #155724;
            }
            
            QPushButton#undoButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton#undoButton:hover {
                background-color: #5a6268;
            }
            
            QPushButton#undoButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
            
            QPushButton#resetButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton#resetButton:hover {
                background-color: #c82333;
            }
            
            QPushButton#applyButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton#applyButton:hover {
                background-color: #0056b3;
            }
            
            /* Toolbar */
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e9ecef;
                spacing: 10px;
                padding: 8px;
            }
            
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-size: 16px;
            }
            
            QToolBar QToolButton:hover {
                background-color: #f8f9fa;
            }
            
            /* Status bar */
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e9ecef;
                color: #6c757d;
            }
        """)
    
    def on_search_changed(self, text: str):
        """Arama değişti"""
        if not text.strip():
            # Tüm kategorileri göster
            for i in range(self.category_list.count()):
                self.category_list.item(i).setHidden(False)
            return
        
        # Arama sonuçlarını filtrele
        text = text.lower()
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            widget = self.category_list.itemWidget(item)
            
            # Başlık ve açıklamada ara
            title = widget.title.lower()
            description = widget.description.lower()
            
            visible = text in title or text in description
            item.setHidden(not visible)
    
    def on_category_changed(self, current, previous):
        """Kategori değişti"""
        if current:
            category_id = current.data(Qt.ItemDataRole.UserRole)
            self.show_page(category_id)
    
    def show_page(self, category_id: str):
        """Sayfa göster"""
        if category_id in self.pages:
            page = self.pages[category_id]
            self.content_stack.setCurrentWidget(page)
            
            # Sayfa başlığını güncelle
            page_titles = {
                "appearance": "🎨 Görünüm",
                "widgets": "🧩 Widget'lar",
                "system": "💻 Sistem",
                "notifications": "🔔 Bildirimler",
                "privacy": "🔒 Gizlilik",
                "network": "🌐 Ağ"
            }
            self.page_title.setText(page_titles.get(category_id, category_id.title()))
            
            # Sayfaya ayarları yükle
            if category_id in self.all_settings:
                page.load_settings(self.all_settings[category_id])
            
            self.logger.info(f"Switched to page: {category_id}")
    
    def on_settings_changed(self, category: str, settings: Dict):
        """Ayar değişti"""
        # Geçmişe ekle
        self.add_to_history(category, self.all_settings.get(category, {}))
        
        # Ayarları güncelle
        self.all_settings[category] = settings
        
        # UI güncellemeleri
        self.update_changes_count()
        self.undo_btn.setEnabled(len(self.settings_history) > 0)
        self.status_label.setText(f"{category.title()} ayarları değiştirildi")
        
        # Sinyal gönder
        self.settings_changed.emit(category, settings)
        
        self.logger.debug(f"Settings changed: {category}")
    
    def add_to_history(self, category: str, old_settings: Dict):
        """Ayar geçmişine ekle"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "old_settings": old_settings.copy(),
            "action": "change"
        }
        
        self.settings_history.append(history_entry)
        
        # Geçmişi sınırla (son 50 değişiklik)
        if len(self.settings_history) > 50:
            self.settings_history = self.settings_history[-50:]
    
    def update_changes_count(self):
        """Değişiklik sayısını güncelle"""
        count = len(self.settings_history)
        self.changes_label.setText(f"{count} değişiklik")
    
    def toggle_live_preview(self, enabled: bool):
        """Canlı önizlemeyi aç/kapat"""
        self.preview_manager.set_enabled(enabled)
        self.live_preview_widget.setVisible(enabled)
        
        if enabled:
            self.live_preview_btn.setText("🔍 Canlı Önizleme")
            self.status_label.setText("Canlı önizleme etkinleştirildi")
        else:
            self.live_preview_btn.setText("👁️ Önizleme Kapalı")
            self.status_label.setText("Canlı önizleme devre dışı")
    
    def undo_changes(self):
        """Son değişikliği geri al"""
        if not self.settings_history:
            return
        
        # Son değişikliği al
        last_change = self.settings_history.pop()
        category = last_change["category"]
        old_settings = last_change["old_settings"]
        
        # Ayarları geri yükle
        self.all_settings[category] = old_settings
        
        # Sayfayı güncelle
        if category in self.pages:
            self.pages[category].load_settings(old_settings)
        
        # UI güncellemeleri
        self.update_changes_count()
        self.undo_btn.setEnabled(len(self.settings_history) > 0)
        self.status_label.setText(f"{category.title()} ayarları geri alındı")
        
        self.logger.info(f"Undid changes for: {category}")
    
    def reset_to_defaults(self):
        """Varsayılan ayarlara dön"""
        reply = QMessageBox.question(
            self, "Varsayılanlara Dön",
            "Tüm ayarları varsayılan değerlere döndürmek istediğinizden emin misiniz?\n\n"
            "Bu işlem geri alınamaz!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Geçmişe ekle
            self.add_to_history("all", self.all_settings.copy())
            
            # Varsayılan ayarları yükle
            self.all_settings = self.get_default_settings()
            
            # Tüm sayfaları güncelle
            for category_id, page in self.pages.items():
                if category_id in self.all_settings:
                    page.load_settings(self.all_settings[category_id])
            
            # Ayarları kaydet
            self.save_settings()
            self.status_label.setText("Varsayılan ayarlar yüklendi")
            
            self.logger.info("Reset to default settings")
    
    def apply_settings(self):
        """Ayarları uygula"""
        self.save_settings()
        
        # Sistem modüllerine bildir
        self.notify_system_modules()
        
        self.status_label.setText("Ayarlar uygulandı ve kaydedildi")
        self.logger.info("Settings applied and saved")
    
    def notify_system_modules(self):
        """Sistem modüllerine ayar değişikliklerini bildir"""
        if not self.kernel:
            self.logger.info("Kernel not available - running in standalone mode")
            return
            
        try:
            # Config manager'a bildir
            config_manager = self.kernel.get_module("config")
            if config_manager:
                config_manager.set("ui_settings", self.all_settings)
            
            # Rain UI'ye bildir
            rain_ui = self.kernel.get_module("rain_ui")
            if rain_ui:
                rain_ui.apply_settings(self.all_settings)
            
            # Wallpaper manager'a bildir
            if "appearance" in self.all_settings:
                wallpaper_manager = self.kernel.get_module("wallpaper")
                if wallpaper_manager:
                    appearance = self.all_settings["appearance"]
                    if "wallpaper_path" in appearance:
                        wallpaper_manager.set_wallpaper(appearance["wallpaper_path"])
            
        except Exception as e:
            self.logger.error(f"Failed to notify system modules: {e}")
    
    def cycle_theme(self):
        """Tema döngüsü"""
        themes = ["light", "dark", "auto"]
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        
        self.current_theme = themes[next_index]
        self.theme_changed.emit(self.current_theme)
        
        # Appearance ayarlarını güncelle
        if "appearance" not in self.all_settings:
            self.all_settings["appearance"] = {}
        self.all_settings["appearance"]["theme"] = self.current_theme
        
        self.status_label.setText(f"Tema değiştirildi: {self.current_theme}")
    
    def apply_theme(self):
        """Temayı uygula"""
        # Tema değişikliklerini UI'ye yansıt
        if self.current_theme == "dark":
            self.apply_dark_theme()
        elif self.current_theme == "light":
            self.apply_light_theme()
        else:
            # Auto - sistem temasını kullan
            self.apply_auto_theme()
    
    def apply_dark_theme(self):
        """Koyu tema uygula"""
        dark_style = """
            QMainWindow { background-color: #2b2b2b; }
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QLabel#sidebarTitle { color: #ffffff; }
            QLabel#pageTitle { color: #ffffff; }
            QListWidget#categoryList::item:hover { background-color: #3c3c3c; }
        """
        self.setStyleSheet(self.styleSheet() + dark_style)
    
    def apply_light_theme(self):
        """Açık tema uygula"""
        # Varsayılan stil zaten açık tema
        self.apply_modern_style()
    
    def apply_auto_theme(self):
        """Otomatik tema uygula"""
        # Sistem temasını algıla ve uygula
        self.apply_light_theme()  # Şimdilik açık tema
    
    def export_settings(self):
        """Ayarları dışa aktar"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Ayarları Dışa Aktar",
            f"pycloud_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Dosyaları (*.json)"
        )
        
        if file_path:
            try:
                export_data = {
                    "version": "2.0.0",
                    "timestamp": datetime.now().isoformat(),
                    "settings": self.all_settings,
                    "history": self.settings_history[-10:]  # Son 10 değişiklik
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Başarılı", "Ayarlar başarıyla dışa aktarıldı!")
                self.logger.info(f"Settings exported to: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız:\n{e}")
                self.logger.error(f"Export failed: {e}")
    
    def import_settings(self):
        """Ayarları içe aktar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ayarları İçe Aktar",
            str(Path.home()),
            "JSON Dosyaları (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                # Veri doğrulama
                if "settings" not in import_data:
                    raise ValueError("Geçersiz ayar dosyası")
                
                # Onay al
                reply = QMessageBox.question(
                    self, "Ayarları İçe Aktar",
                    "Mevcut ayarlar değiştirilecek. Devam etmek istediğinizden emin misiniz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Geçmişe ekle
                    self.add_to_history("all", self.all_settings.copy())
                    
                    # Ayarları yükle
                    self.all_settings = import_data["settings"]
                    
                    # Sayfaları güncelle
                    for category_id, page in self.pages.items():
                        if category_id in self.all_settings:
                            page.load_settings(self.all_settings[category_id])
                    
                    # Kaydet
                    self.save_settings()
                    
                    QMessageBox.information(self, "Başarılı", "Ayarlar başarıyla içe aktarıldı!")
                    self.logger.info(f"Settings imported from: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"İçe aktarma başarısız:\n{e}")
                self.logger.error(f"Import failed: {e}")
    
    def show_help(self):
        """Yardım göster"""
        help_text = """
        <h2>Cloud Settings v2.0.0 Yardım</h2>
        
        <h3>🎨 Görünüm</h3>
        <p>Tema, duvar kağıdı ve dock ayarlarını yönetin.</p>
        
        <h3>🧩 Widget'lar</h3>
        <p>Masaüstü widget'larının görünürlüğünü ve sırasını ayarlayın.</p>
        
        <h3>💻 Sistem</h3>
        <p>Genel sistem ayarları ve performans seçenekleri.</p>
        
        <h3>🔔 Bildirimler</h3>
        <p>Bildirim tercihleri ve uygulama bildirimleri.</p>
        
        <h3>🔒 Gizlilik</h3>
        <p>Güvenlik ve gizlilik ayarları.</p>
        
        <h3>🌐 Ağ</h3>
        <p>İnternet ve ağ bağlantı ayarları.</p>
        
        <h3>Özellikler</h3>
        <ul>
        <li><b>Canlı Önizleme:</b> Değişiklikleri anında görün</li>
        <li><b>Geri Al:</b> Son değişiklikleri geri alın</li>
        <li><b>Arama:</b> Ayarları hızlıca bulun</li>
        <li><b>Dışa/İçe Aktarma:</b> Ayarlarınızı yedekleyin</li>
        </ul>
        """
        
        QMessageBox.about(self, "Yardım", help_text)
    
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
            
            # Geçmişi yükle
            self.load_history()
            
            # Tema ayarını al
            if "appearance" in self.all_settings:
                self.current_theme = self.all_settings["appearance"].get("theme", "auto")
                
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self.all_settings = self.get_default_settings()
    
    def load_history(self):
        """Ayar geçmişini yükle"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.settings_history = json.load(f)
                
                # Geçmişi sınırla
                self.settings_history = self.settings_history[-50:]
                self.update_changes_count()
                self.undo_btn.setEnabled(len(self.settings_history) > 0)
                
        except Exception as e:
            self.logger.error(f"Failed to load history: {e}")
            self.settings_history = []
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_settings, f, indent=2, ensure_ascii=False)
            
            # Geçmişi kaydet
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_history, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Settings saved successfully")
            self.last_saved_label.setText(f"Son kayıt: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilemedi:\n{e}")
    
    def get_default_settings(self) -> Dict:
        """Varsayılan ayarları al - .cursorrules uyumlu"""
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
                "show_notifications": True,
                "accent_color": "#007bff",
                "transparency": True
            },
            "widgets": {
                "enabled_widgets": ["clock", "calendar", "weather"],
                "widget_positions": {},
                "widget_settings": {},
                "auto_arrange": True,
                "widget_transparency": 0.9
            },
            "system": {
                "auto_login": False,
                "startup_sound": True,
                "session_timeout": 0,
                "require_password": True,
                "animations": True,
                "transparency": True,
                "memory_limit": 1024,
                "language": "tr_TR",
                "timezone": "Europe/Istanbul"
            },
            "notifications": {
                "enable_notifications": True,
                "notification_sound": True,
                "show_preview": True,
                "notification_position": "sağ_üst",
                "notification_duration": 5,
                "max_notifications": 3,
                "app_notifications": {}
            },
            "privacy": {
                "analytics": False,
                "crash_reports": True,
                "location_services": False,
                "camera_access": True,
                "microphone_access": True,
                "file_access_logging": True
            },
            "network": {
                "auto_connect": True,
                "proxy_enabled": False,
                "proxy_host": "",
                "proxy_port": 8080,
                "dns_servers": ["8.8.8.8", "8.8.4.4"],
                "connection_timeout": 30
            }
        }
    
    def closeEvent(self, event):
        """Pencere kapatılıyor"""
        # Değişiklikleri kaydet
        self.save_settings()
        
        # Canlı önizlemeyi kapat
        self.preview_manager.cleanup()
        
        event.accept()
        self.logger.info("Cloud Settings closed") 