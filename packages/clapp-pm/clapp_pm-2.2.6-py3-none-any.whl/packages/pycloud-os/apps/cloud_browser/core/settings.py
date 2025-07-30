"""
Cloud Browser Ayarları
JSON tabanlı ayar sistemi ve ayarlar dialog'u
"""

import json
from typing import Any, Dict
from pathlib import Path

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    raise ImportError("PyQt6 is required for Cloud Browser")

class BrowserSettings:
    """
    Browser ayarları yöneticisi
    """
    
    def __init__(self):
        self.settings_file = Path.home() / ".cloud_browser" / "settings.json"
        self.settings_file.parent.mkdir(exist_ok=True)
        self.settings = {}
        self.load_settings()
    
    def load_settings(self):
        """Ayarları yükle"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                # Varsayılan ayarlar
                self.settings = {
                    "dark_mode": True,
                    "home_page": "about:blank",
                    "download_path": str(Path.home() / "Downloads"),
                    "auto_save_tabs": True,
                    "show_bookmarks_bar": True,
                    "enable_javascript": True,
                    "enable_plugins": True,
                    "enable_images": True,
                    "enable_notifications": True,
                    "zoom_factor": 1.0,
                    "font_family": "Arial",
                    "font_size": 14,
                    "privacy_mode": False,
                    "clear_data_on_exit": False,
                    "block_popups": True,
                    "enable_developer_tools": True,
                    "user_agent": "Cloud Browser 2.0.0",
                    "proxy_enabled": False,
                    "proxy_host": "",
                    "proxy_port": 8080,
                    "search_engine": "https://www.google.com/search?q=%s"
                }
                self.save_settings()
        except Exception as e:
            print(f"Ayar yükleme hatası: {e}")
            self.settings = {}
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ayar kaydetme hatası: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Ayar değeri al"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Ayar değeri belirle"""
        self.settings[key] = value
    
    def save(self):
        """Ayarları kaydet"""
        self.save_settings()
    
    def reset_to_defaults(self):
        """Varsayılan ayarlara dön"""
        self.settings.clear()
        self.load_settings()

class BrowserSettingsDialog(QDialog):
    """
    Browser ayarları dialog'u
    """
    
    def __init__(self, settings: BrowserSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.temp_settings = self.settings.settings.copy()
        
        self.setWindowTitle("Cloud Browser Ayarları")
        self.setModal(True)
        self.resize(700, 600)
        
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """UI'yı başlat"""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Genel ayarlar sekmesi
        self.create_general_tab()
        
        # Görünüm ayarları sekmesi
        self.create_appearance_tab()
        
        # Gizlilik ayarları sekmesi
        self.create_privacy_tab()
        
        # Gelişmiş ayarlar sekmesi
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Alt butonlar
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 Varsayılanlara Dön")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ İptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("✅ Uygula")
        apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_btn)
        
        ok_btn = QPushButton("💾 Tamam")
        ok_btn.clicked.connect(self.accept_settings)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Stil uygula
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-color: #007bff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox, QRadioButton {
                padding: 4px;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #007bff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
    
    def create_general_tab(self):
        """Genel ayarlar sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Başlangıç grubu
        startup_group = QGroupBox("🚀 Başlangıç")
        startup_layout = QFormLayout(startup_group)
        
        self.home_page_edit = QLineEdit()
        self.home_page_edit.setPlaceholderText("about:blank veya https://example.com")
        startup_layout.addRow("Ana Sayfa:", self.home_page_edit)
        
        self.auto_save_tabs_cb = QCheckBox("Son açık sekmeleri hatırla")
        startup_layout.addRow("", self.auto_save_tabs_cb)
        
        layout.addWidget(startup_group)
        
        # İndirme grubu
        download_group = QGroupBox("📥 İndirmeler")
        download_layout = QFormLayout(download_group)
        
        download_path_layout = QHBoxLayout()
        self.download_path_edit = QLineEdit()
        download_path_layout.addWidget(self.download_path_edit)
        
        browse_btn = QPushButton("📁 Gözat")
        browse_btn.clicked.connect(self.browse_download_path)
        download_path_layout.addWidget(browse_btn)
        
        download_layout.addRow("İndirme Klasörü:", download_path_layout)
        
        layout.addWidget(download_group)
        
        # Arama grubu
        search_group = QGroupBox("🔍 Arama")
        search_layout = QFormLayout(search_group)
        
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems([
            "Google - https://www.google.com/search?q=%s",
            "Bing - https://www.bing.com/search?q=%s",
            "DuckDuckGo - https://duckduckgo.com/?q=%s",
            "Yandex - https://yandex.com/search/?text=%s",
            "Özel..."
        ])
        self.search_engine_combo.currentTextChanged.connect(self.search_engine_changed)
        search_layout.addRow("Arama Motoru:", self.search_engine_combo)
        
        self.custom_search_edit = QLineEdit()
        self.custom_search_edit.setPlaceholderText("https://example.com/search?q=%s")
        self.custom_search_edit.setVisible(False)
        search_layout.addRow("Özel URL:", self.custom_search_edit)
        
        layout.addWidget(search_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "⚙️ Genel")
    
    def create_appearance_tab(self):
        """Görünüm ayarları sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tema grubu
        theme_group = QGroupBox("🎨 Tema")
        theme_layout = QVBoxLayout(theme_group)
        
        self.dark_mode_cb = QCheckBox("Koyu tema kullan")
        theme_layout.addWidget(self.dark_mode_cb)
        
        self.show_bookmarks_bar_cb = QCheckBox("Yer imi çubuğunu göster")
        theme_layout.addWidget(self.show_bookmarks_bar_cb)
        
        layout.addWidget(theme_group)
        
        # Yazı tipi grubu
        font_group = QGroupBox("🔤 Yazı Tipi")
        font_layout = QFormLayout(font_group)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Arial", "Helvetica", "Times New Roman", "Courier New",
            "Verdana", "Georgia", "Comic Sans MS", "Impact"
        ])
        font_layout.addRow("Yazı Tipi:", self.font_family_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setSuffix(" px")
        font_layout.addRow("Yazı Boyutu:", self.font_size_spin)
        
        layout.addWidget(font_group)
        
        # Zoom grubu
        zoom_group = QGroupBox("🔍 Yakınlaştırma")
        zoom_layout = QFormLayout(zoom_group)
        
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(25, 500)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.setSingleStep(25)
        zoom_layout.addRow("Varsayılan Zoom:", self.zoom_spin)
        
        layout.addWidget(zoom_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "👁️ Görünüm")
    
    def create_privacy_tab(self):
        """Gizlilik ayarları sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Gizlilik grubu
        privacy_group = QGroupBox("🔒 Gizlilik")
        privacy_layout = QVBoxLayout(privacy_group)
        
        self.privacy_mode_cb = QCheckBox("Gizlilik modu (geçmiş kaydetme)")
        privacy_layout.addWidget(self.privacy_mode_cb)
        
        self.clear_data_on_exit_cb = QCheckBox("Çıkışta verileri temizle")
        privacy_layout.addWidget(self.clear_data_on_exit_cb)
        
        self.block_popups_cb = QCheckBox("Açılır pencereleri engelle")
        privacy_layout.addWidget(self.block_popups_cb)
        
        layout.addWidget(privacy_group)
        
        # İçerik grubu
        content_group = QGroupBox("🌐 İçerik")
        content_layout = QVBoxLayout(content_group)
        
        self.enable_javascript_cb = QCheckBox("JavaScript'i etkinleştir")
        content_layout.addWidget(self.enable_javascript_cb)
        
        self.enable_plugins_cb = QCheckBox("Eklentileri etkinleştir")
        content_layout.addWidget(self.enable_plugins_cb)
        
        self.enable_images_cb = QCheckBox("Resimleri yükle")
        content_layout.addWidget(self.enable_images_cb)
        
        self.enable_notifications_cb = QCheckBox("Web bildirimlerine izin ver")
        content_layout.addWidget(self.enable_notifications_cb)
        
        layout.addWidget(content_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔒 Gizlilik")
    
    def create_advanced_tab(self):
        """Gelişmiş ayarlar sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Geliştirici grubu
        dev_group = QGroupBox("🛠️ Geliştirici")
        dev_layout = QVBoxLayout(dev_group)
        
        self.enable_devtools_cb = QCheckBox("Geliştirici araçlarını etkinleştir")
        dev_layout.addWidget(self.enable_devtools_cb)
        
        layout.addWidget(dev_group)
        
        # User Agent grubu
        ua_group = QGroupBox("🤖 User Agent")
        ua_layout = QFormLayout(ua_group)
        
        self.user_agent_edit = QLineEdit()
        self.user_agent_edit.setPlaceholderText("Cloud Browser 2.0.0")
        ua_layout.addRow("User Agent:", self.user_agent_edit)
        
        layout.addWidget(ua_group)
        
        # Proxy grubu
        proxy_group = QGroupBox("🌐 Proxy")
        proxy_layout = QFormLayout(proxy_group)
        
        self.proxy_enabled_cb = QCheckBox("Proxy kullan")
        proxy_layout.addRow("", self.proxy_enabled_cb)
        
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("proxy.example.com")
        proxy_layout.addRow("Proxy Sunucusu:", self.proxy_host_edit)
        
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        proxy_layout.addRow("Port:", self.proxy_port_spin)
        
        layout.addWidget(proxy_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "🔧 Gelişmiş")
    
    def load_current_settings(self):
        """Mevcut ayarları yükle"""
        # Genel
        self.home_page_edit.setText(self.temp_settings.get("home_page", ""))
        self.auto_save_tabs_cb.setChecked(self.temp_settings.get("auto_save_tabs", True))
        self.download_path_edit.setText(self.temp_settings.get("download_path", ""))
        
        # Arama motoru
        search_engine = self.temp_settings.get("search_engine", "")
        for i in range(self.search_engine_combo.count() - 1):
            if search_engine in self.search_engine_combo.itemText(i):
                self.search_engine_combo.setCurrentIndex(i)
                break
        else:
            self.search_engine_combo.setCurrentIndex(self.search_engine_combo.count() - 1)
            self.custom_search_edit.setText(search_engine)
            self.custom_search_edit.setVisible(True)
        
        # Görünüm
        self.dark_mode_cb.setChecked(self.temp_settings.get("dark_mode", True))
        self.show_bookmarks_bar_cb.setChecked(self.temp_settings.get("show_bookmarks_bar", True))
        
        font_family = self.temp_settings.get("font_family", "Arial")
        index = self.font_family_combo.findText(font_family)
        if index >= 0:
            self.font_family_combo.setCurrentIndex(index)
        
        self.font_size_spin.setValue(self.temp_settings.get("font_size", 14))
        self.zoom_spin.setValue(int(self.temp_settings.get("zoom_factor", 1.0) * 100))
        
        # Gizlilik
        self.privacy_mode_cb.setChecked(self.temp_settings.get("privacy_mode", False))
        self.clear_data_on_exit_cb.setChecked(self.temp_settings.get("clear_data_on_exit", False))
        self.block_popups_cb.setChecked(self.temp_settings.get("block_popups", True))
        self.enable_javascript_cb.setChecked(self.temp_settings.get("enable_javascript", True))
        self.enable_plugins_cb.setChecked(self.temp_settings.get("enable_plugins", True))
        self.enable_images_cb.setChecked(self.temp_settings.get("enable_images", True))
        self.enable_notifications_cb.setChecked(self.temp_settings.get("enable_notifications", True))
        
        # Gelişmiş
        self.enable_devtools_cb.setChecked(self.temp_settings.get("enable_developer_tools", True))
        self.user_agent_edit.setText(self.temp_settings.get("user_agent", ""))
        self.proxy_enabled_cb.setChecked(self.temp_settings.get("proxy_enabled", False))
        self.proxy_host_edit.setText(self.temp_settings.get("proxy_host", ""))
        self.proxy_port_spin.setValue(self.temp_settings.get("proxy_port", 8080))
    
    def save_current_settings(self):
        """Mevcut ayarları kaydet"""
        # Genel
        self.temp_settings["home_page"] = self.home_page_edit.text()
        self.temp_settings["auto_save_tabs"] = self.auto_save_tabs_cb.isChecked()
        self.temp_settings["download_path"] = self.download_path_edit.text()
        
        # Arama motoru
        if self.search_engine_combo.currentIndex() == self.search_engine_combo.count() - 1:
            self.temp_settings["search_engine"] = self.custom_search_edit.text()
        else:
            text = self.search_engine_combo.currentText()
            self.temp_settings["search_engine"] = text.split(" - ")[1] if " - " in text else text
        
        # Görünüm
        self.temp_settings["dark_mode"] = self.dark_mode_cb.isChecked()
        self.temp_settings["show_bookmarks_bar"] = self.show_bookmarks_bar_cb.isChecked()
        self.temp_settings["font_family"] = self.font_family_combo.currentText()
        self.temp_settings["font_size"] = self.font_size_spin.value()
        self.temp_settings["zoom_factor"] = self.zoom_spin.value() / 100.0
        
        # Gizlilik
        self.temp_settings["privacy_mode"] = self.privacy_mode_cb.isChecked()
        self.temp_settings["clear_data_on_exit"] = self.clear_data_on_exit_cb.isChecked()
        self.temp_settings["block_popups"] = self.block_popups_cb.isChecked()
        self.temp_settings["enable_javascript"] = self.enable_javascript_cb.isChecked()
        self.temp_settings["enable_plugins"] = self.enable_plugins_cb.isChecked()
        self.temp_settings["enable_images"] = self.enable_images_cb.isChecked()
        self.temp_settings["enable_notifications"] = self.enable_notifications_cb.isChecked()
        
        # Gelişmiş
        self.temp_settings["enable_developer_tools"] = self.enable_devtools_cb.isChecked()
        self.temp_settings["user_agent"] = self.user_agent_edit.text()
        self.temp_settings["proxy_enabled"] = self.proxy_enabled_cb.isChecked()
        self.temp_settings["proxy_host"] = self.proxy_host_edit.text()
        self.temp_settings["proxy_port"] = self.proxy_port_spin.value()
    
    def search_engine_changed(self):
        """Arama motoru değiştiğinde"""
        is_custom = self.search_engine_combo.currentIndex() == self.search_engine_combo.count() - 1
        self.custom_search_edit.setVisible(is_custom)
    
    def browse_download_path(self):
        """İndirme klasörü seç"""
        path = QFileDialog.getExistingDirectory(
            self,
            "İndirme Klasörü Seç",
            self.download_path_edit.text()
        )
        if path:
            self.download_path_edit.setText(path)
    
    def reset_settings(self):
        """Ayarları sıfırla"""
        reply = QMessageBox.question(
            self,
            "Ayarları Sıfırla",
            "Tüm ayarlar varsayılan değerlere döndürülecek. Emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self.temp_settings = self.settings.settings.copy()
            self.load_current_settings()
    
    def apply_settings(self):
        """Ayarları uygula"""
        self.save_current_settings()
        self.settings.settings = self.temp_settings.copy()
        self.settings.save_settings()
    
    def accept_settings(self):
        """Ayarları kabul et ve kapat"""
        self.apply_settings()
        self.accept()
    
    def reject(self):
        """İptal et"""
        # Değişiklikleri geri al
        self.temp_settings = self.settings.settings.copy()
        super().reject() 