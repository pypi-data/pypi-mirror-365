"""
Cloud AppStore - Modern PyCloud OS Uygulama Mağazası
Kategori bazlı gezinme, arama, kurulum/kaldırma, kullanıcı puanları
"""

import os
import sys
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtNetwork import *
except ImportError:
    print("PyQt6 not available for Cloud AppStore")
    sys.exit(1)

class AppStatus(Enum):
    """Uygulama durumları"""
    AVAILABLE = "available"
    INSTALLED = "installed"
    UPDATING = "updating"
    INSTALLING = "installing"
    REMOVING = "removing"
    ERROR = "error"

class ViewMode(Enum):
    """Görünüm modları"""
    GRID = "grid"
    LIST = "list"
    DETAILED = "detailed"

class SortMode(Enum):
    """Sıralama modları"""
    NAME = "name"
    CATEGORY = "category"
    DEVELOPER = "developer"
    RATING = "rating"
    DOWNLOADS = "downloads"
    DATE = "date"

class AppInfo:
    """Uygulama bilgi sınıfı"""
    
    def __init__(self, data: Dict[str, Any]):
        self.app_id = data.get("app_id", "")
        self.name = data.get("name", "")
        self.version = data.get("version", "1.0.0")
        self.description = data.get("description", "")
        self.category = data.get("category", "Diğer")
        self.developer = data.get("developer", "Bilinmeyen")
        self.icon_path = data.get("icon_path", "")
        self.app_path = data.get("app_path", "")
        self.tags = data.get("tags", [])
        self.screenshots = data.get("screenshots", [])
        self.homepage = data.get("homepage", "")
        self.license = data.get("license", "")
        self.requires = data.get("requires", [])
        self.permissions = data.get("permissions", [])
        
        # Ek bilgiler
        self.rating = data.get("rating", 0.0)
        self.downloads = data.get("downloads", 0)
        self.reviews = data.get("reviews", [])
        self.last_updated = data.get("last_updated", "")
        self.size = data.get("size", 0)
        
        # Durum
        self.status = AppStatus.AVAILABLE
        self.is_installed = False
        self.installed_version = ""
        
    def has_update(self) -> bool:
        """Güncelleme var mı?"""
        if not self.is_installed:
            return False
        try:
            from packaging import version
            return version.parse(self.version) > version.parse(self.installed_version)
        except:
            return self.version != self.installed_version

class AppDataManager:
    """Uygulama veri yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("AppDataManager")
        self.apps: Dict[str, AppInfo] = {}
        self.installed_apps: Set[str] = set()
        
        # AppExplorer entegrasyonu
        self.app_explorer = None
        if kernel:
            self.app_explorer = kernel.get_module("appexplorer")
        
        # Clapp entegrasyonu
        self.clapp_core = None
        self.clapp_repo = None
        if kernel:
            self.clapp_core = kernel.get_module("clapp_core")
            self.clapp_repo = kernel.get_module("clapp_repo")
    
    def load_apps(self) -> List[AppInfo]:
        """Uygulamaları yükle"""
        apps = []
        
        try:
            # AppExplorer'dan yüklü uygulamaları al
            if self.app_explorer:
                discovered_apps = self.app_explorer.get_all_apps()
                
                for discovered_app in discovered_apps:
                    app_data = {
                        "app_id": discovered_app.app_id,
                        "name": discovered_app.name,
                        "version": discovered_app.version,
                        "description": discovered_app.description,
                        "category": discovered_app.category,
                        "developer": discovered_app.developer,
                        "icon_path": discovered_app.icon_path,
                        "app_path": discovered_app.app_path,
                        "tags": discovered_app.tags,
                        "rating": 4.0,  # Varsayılan rating
                        "downloads": 100,  # Varsayılan indirme sayısı
                        "last_updated": discovered_app.last_validated
                    }
                    
                    app_info = AppInfo(app_data)
                    app_info.is_installed = True
                    app_info.installed_version = app_info.version
                    app_info.status = AppStatus.INSTALLED
                    
                    apps.append(app_info)
                    self.apps[app_info.app_id] = app_info
                    self.installed_apps.add(app_info.app_id)
                
                self.logger.info(f"Loaded {len(apps)} installed apps from AppExplorer")
            
            # Clapp Repository'den mevcut uygulamaları ekle
            if self.clapp_repo:
                repo_apps = self._load_clapp_repository_apps()
                for app_info in repo_apps:
                    if app_info.app_id not in self.apps:
                        apps.append(app_info)
                        self.apps[app_info.app_id] = app_info
                    else:
                        # Güncelleme kontrolü
                        existing_app = self.apps[app_info.app_id]
                        if app_info.version != existing_app.version:
                            existing_app.version = app_info.version
            else:
                # Fallback: Mock veriler
                repo_apps = self._load_repository_apps()
                for app_info in repo_apps:
                    if app_info.app_id not in self.apps:
                        apps.append(app_info)
                        self.apps[app_info.app_id] = app_info
                        
        except Exception as e:
            self.logger.error(f"Failed to load apps: {e}")
        
        return apps
    
    def _load_clapp_repository_apps(self) -> List[AppInfo]:
        """Clapp Repository'den uygulamaları yükle"""
        apps = []
        
        try:
            if not self.clapp_repo:
                return apps
            
            # Tüm repository'leri yenile
            self.clapp_repo.refresh_repositories()
            
            # Tüm paketleri al
            packages = self.clapp_repo.get_all_packages()
            
            for package in packages:
                app_data = {
                    "app_id": package.id,
                    "name": package.name,
                    "version": package.version,
                    "description": package.description,
                    "category": package.category,
                    "developer": package.developer,
                    "icon_path": "",  # Repository'den ikon URL'si gelecek
                    "app_path": "",
                    "tags": getattr(package, 'tags', []),
                    "rating": getattr(package, 'rating', 4.0),
                    "downloads": getattr(package, 'downloads', 0),
                    "last_updated": getattr(package, 'last_updated', ""),
                    "homepage": getattr(package, 'homepage', ""),
                    "license": getattr(package, 'license', ""),
                    "requires": getattr(package, 'requires', []),
                    "permissions": getattr(package, 'permissions', []),
                    "screenshots": getattr(package, 'screenshots', []),
                    "size": getattr(package, 'size', 0)
                }
                
                app_info = AppInfo(app_data)
                apps.append(app_info)
                
            self.logger.info(f"Loaded {len(apps)} apps from Clapp repositories")
            
        except Exception as e:
            self.logger.error(f"Failed to load Clapp repository apps: {e}")
        
        return apps
    
    def _load_repository_apps(self) -> List[AppInfo]:
        """Repository'den uygulamaları yükle (simülasyon)"""
        # Simülasyon verisi - gerçek uygulamada repository'den gelecek
        mock_apps = [
            {
                "app_id": "cloud_calculator",
                "name": "Cloud Calculator",
                "version": "1.2.0",
                "description": "Modern hesap makinesi uygulaması. Temel matematik işlemleri, bilimsel hesaplamalar ve geçmiş desteği.",
                "category": "Araçlar",
                "developer": "PyCloud Team",
                "icon_path": "",
                "app_path": "",
                "tags": ["calculator", "math", "utility"],
                "rating": 4.5,
                "downloads": 1250,
                "last_updated": "2024-01-15"
            },
            {
                "app_id": "cloud_music",
                "name": "Cloud Music Player",
                "version": "2.1.0",
                "description": "Güçlü müzik çalar. MP3, FLAC, OGG desteği. Playlist yönetimi ve equalizer.",
                "category": "Multimedya",
                "developer": "AudioSoft",
                "icon_path": "",
                "app_path": "",
                "tags": ["music", "player", "audio"],
                "rating": 4.8,
                "downloads": 3400,
                "last_updated": "2024-01-20"
            },
            {
                "app_id": "cloud_paint",
                "name": "Cloud Paint",
                "version": "1.5.0",
                "description": "Basit çizim ve boyama uygulaması. Fırça araçları, katmanlar ve filtreler.",
                "category": "Grafik",
                "developer": "ArtStudio",
                "icon_path": "",
                "app_path": "",
                "tags": ["paint", "drawing", "graphics"],
                "rating": 4.2,
                "downloads": 890,
                "last_updated": "2024-01-10"
            },
            {
                "app_id": "cloud_chess",
                "name": "Cloud Chess",
                "version": "1.0.0",
                "description": "Klasik satranç oyunu. AI rakip, çoklu oyuncu desteği ve turnuva modu.",
                "category": "Oyunlar",
                "developer": "GameDev Studio",
                "icon_path": "",
                "app_path": "",
                "tags": ["chess", "game", "strategy"],
                "rating": 4.6,
                "downloads": 2100,
                "last_updated": "2024-01-05"
            },
            {
                "app_id": "cloud_markdown",
                "name": "Markdown Editor",
                "version": "1.3.0",
                "description": "Gelişmiş Markdown editörü. Canlı önizleme, syntax highlighting ve export seçenekleri.",
                "category": "Geliştirme",
                "developer": "DevTools Inc",
                "icon_path": "",
                "app_path": "",
                "tags": ["markdown", "editor", "development"],
                "rating": 4.4,
                "downloads": 1680,
                "last_updated": "2024-01-18"
            }
        ]
        
        apps = []
        for app_data in mock_apps:
            app_info = AppInfo(app_data)
            apps.append(app_info)
        
        return apps
    
    def get_apps_by_category(self, category: str) -> List[AppInfo]:
        """Kategoriye göre uygulamaları getir"""
        if category == "Tümü":
            return list(self.apps.values())
        elif category == "Yüklü":
            return [app for app in self.apps.values() if app.is_installed]
        elif category == "Güncellemeler":
            return [app for app in self.apps.values() if app.has_update()]
        else:
            return [app for app in self.apps.values() if app.category == category]
    
    def search_apps(self, query: str) -> List[AppInfo]:
        """Uygulama ara"""
        if not query:
            return list(self.apps.values())
        
        query = query.lower()
        results = []
        
        for app in self.apps.values():
            # Ad, açıklama, geliştirici ve etiketlerde ara
            if (query in app.name.lower() or 
                query in app.description.lower() or
                query in app.developer.lower() or
                any(query in tag.lower() for tag in app.tags)):
                results.append(app)
        
        return results
    
    def get_category_counts(self) -> Dict[str, int]:
        """Kategori sayılarını getir"""
        counts = {}
        
        # Tüm uygulamalar
        counts["Tümü"] = len(self.apps)
        
        # Yüklü uygulamalar
        counts["Yüklü"] = len([app for app in self.apps.values() if app.is_installed])
        
        # Güncellemeler
        counts["Güncellemeler"] = len([app for app in self.apps.values() if app.has_update()])
        
        # Kategoriler
        for app in self.apps.values():
            if app.category not in counts:
                counts[app.category] = 0
            counts[app.category] += 1
        
        return counts
    
    def install_app(self, app_id: str) -> bool:
        """Uygulama kur"""
        if app_id not in self.apps:
            return False
        
        app = self.apps[app_id]
        app.status = AppStatus.INSTALLING
        
        try:
            # Clapp Core kullanarak kurulum yap
            if self.clapp_core:
                result, message = self.clapp_core._cmd_install([app_id])
                
                if result.name == "SUCCESS":
                    app.is_installed = True
                    app.installed_version = app.version
                    app.status = AppStatus.INSTALLED
                    self.installed_apps.add(app_id)
                    
                    self.logger.info(f"App installed via Clapp: {app.name}")
                    return True
                else:
                    app.status = AppStatus.ERROR
                    self.logger.error(f"Clapp install failed: {message}")
                    return False
            
            # Fallback: AppKit kullanarak kurulum yap
            elif self.kernel:
                appkit = self.kernel.get_module("appkit")
                if appkit:
                    # Gerçek kurulum işlemi burada olacak
                    pass
            
            # Simülasyon için başarılı kabul et
            app.is_installed = True
            app.installed_version = app.version
            app.status = AppStatus.INSTALLED
            self.installed_apps.add(app_id)
            
            self.logger.info(f"App installed (fallback): {app.name}")
            return True
            
        except Exception as e:
            app.status = AppStatus.ERROR
            self.logger.error(f"Failed to install app {app_id}: {e}")
            return False
    
    def remove_app(self, app_id: str) -> bool:
        """Uygulama kaldır"""
        if app_id not in self.apps or app_id not in self.installed_apps:
            return False
        
        app = self.apps[app_id]
        app.status = AppStatus.REMOVING
        
        try:
            # Clapp Core kullanarak kaldırma yap
            if self.clapp_core:
                result, message = self.clapp_core._cmd_remove([app_id])
                
                if result.name == "SUCCESS":
                    app.is_installed = False
                    app.installed_version = ""
                    app.status = AppStatus.AVAILABLE
                    self.installed_apps.discard(app_id)
                    
                    self.logger.info(f"App removed via Clapp: {app.name}")
                    return True
                else:
                    app.status = AppStatus.ERROR
                    self.logger.error(f"Clapp remove failed: {message}")
                    return False
            
            # Fallback: AppExplorer'dan kaldır
            elif self.app_explorer:
                self.app_explorer.indexer.remove_app(app_id)
            
            # AppKit kullanarak kaldırma işlemi
            elif self.kernel:
                appkit = self.kernel.get_module("appkit")
                if appkit:
                    # Gerçek kaldırma işlemi burada olacak
                    pass
            
            # Simülasyon için başarılı kabul et
            app.is_installed = False
            app.installed_version = ""
            app.status = AppStatus.AVAILABLE
            self.installed_apps.discard(app_id)
            
            self.logger.info(f"App removed (fallback): {app.name}")
            return True
            
        except Exception as e:
            app.status = AppStatus.ERROR
            self.logger.error(f"Failed to remove app {app_id}: {e}")
            return False
    
    def update_app(self, app_id: str) -> bool:
        """Uygulama güncelle"""
        if app_id not in self.apps or not self.apps[app_id].has_update():
            return False
        
        app = self.apps[app_id]
        app.status = AppStatus.UPDATING
        
        try:
            # Clapp Core kullanarak güncelleme yap
            if self.clapp_core:
                result, message = self.clapp_core._cmd_update([app_id])
                
                if result.name == "SUCCESS":
                    app.installed_version = app.version
                    app.status = AppStatus.INSTALLED
                    
                    self.logger.info(f"App updated via Clapp: {app.name}")
                    return True
                else:
                    app.status = AppStatus.ERROR
                    self.logger.error(f"Clapp update failed: {message}")
                    return False
            
            # Fallback: Güncelleme işlemi (simülasyon)
            app.installed_version = app.version
            app.status = AppStatus.INSTALLED
            
            self.logger.info(f"App updated (fallback): {app.name}")
            return True
            
        except Exception as e:
            app.status = AppStatus.ERROR
            self.logger.error(f"Failed to update app {app_id}: {e}")
            return False

class CloudAppStore(QMainWindow):
    """Modern Cloud AppStore ana sınıfı"""
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("CloudAppStore")
        
        # Veri yöneticisi
        self.data_manager = AppDataManager(kernel)
        
        # UI durumu
        self.current_apps: List[AppInfo] = []
        self.filtered_apps: List[AppInfo] = []
        self.current_category = "Tümü"
        self.current_search = ""
        self.current_view_mode = ViewMode.GRID
        self.current_sort_mode = SortMode.NAME
        
        # Tema
        self.dark_mode = self.detect_dark_mode()
        
        # UI kurulumu
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
        # Veri yükleme
        self.load_data()
        
        self.logger.info("Cloud AppStore initialized")
    
    def detect_dark_mode(self) -> bool:
        """Dark mode algıla"""
        try:
            if self.kernel:
                config = self.kernel.get_module("config")
                if config:
                    theme_config = config.get("theme", {})
                    return theme_config.get("dark_mode", False)
            
            # Fallback
            palette = QApplication.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            return window_color.lightness() < 128
            
        except Exception:
            return False
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle("Cloud AppStore - Modern Uygulama Mağazası")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sol panel (kategoriler)
        from .widgets import CategorySidebar
        self.sidebar = CategorySidebar(self.dark_mode)
        self.sidebar.setFixedWidth(250)
        main_layout.addWidget(self.sidebar)
        
        # Sağ panel (ana içerik)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Üst bar (arama ve filtreler)
        from .widgets import SearchBar
        self.search_bar = SearchBar(self.dark_mode)
        right_layout.addWidget(self.search_bar)
        
        # Toolbar
        self.setup_toolbar()
        right_layout.addWidget(self.toolbar)
        
        # Uygulama listesi (scroll area)
        self.setup_app_area()
        right_layout.addWidget(self.app_scroll_area, 1)
        
        # Alt bar (durum)
        self.setup_status_bar()
        right_layout.addWidget(self.status_bar)
        
        main_layout.addWidget(right_panel, 1)
    
    def setup_toolbar(self):
        """Toolbar kurulumu"""
        self.toolbar = QWidget()
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)
        
        # Sol taraf: Görünüm butonları
        view_group = QButtonGroup(self)
        
        self.grid_view_btn = QPushButton("⊞ Izgara")
        self.grid_view_btn.setCheckable(True)
        self.grid_view_btn.setChecked(True)
        view_group.addButton(self.grid_view_btn, 0)
        
        self.list_view_btn = QPushButton("☰ Liste")
        self.list_view_btn.setCheckable(True)
        view_group.addButton(self.list_view_btn, 1)
        
        self.detailed_view_btn = QPushButton("📋 Detaylı")
        self.detailed_view_btn.setCheckable(True)
        view_group.addButton(self.detailed_view_btn, 2)
        
        toolbar_layout.addWidget(self.grid_view_btn)
        toolbar_layout.addWidget(self.list_view_btn)
        toolbar_layout.addWidget(self.detailed_view_btn)
        
        toolbar_layout.addWidget(QFrame())  # Ayırıcı
        
        # Orta: Sıralama
        toolbar_layout.addWidget(QLabel("Sırala:"))
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Ada göre",
            "Kategoriye göre", 
            "Geliştiriciye göre",
            "Puana göre",
            "İndirme sayısına göre"
        ])
        toolbar_layout.addWidget(self.sort_combo)
        
        toolbar_layout.addStretch()
        
        # Sağ taraf: Yenile ve ayarlar
        self.refresh_btn = QPushButton("🔄 Yenile")
        toolbar_layout.addWidget(self.refresh_btn)
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(32, 32)
        toolbar_layout.addWidget(self.settings_btn)
    
    def setup_app_area(self):
        """Uygulama alanı kurulumu"""
        self.app_scroll_area = QScrollArea()
        self.app_scroll_area.setWidgetResizable(True)
        self.app_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # İçerik widget'ı
        self.app_content_widget = QWidget()
        self.app_scroll_area.setWidget(self.app_content_widget)
        
        # Layout (grid olarak başla)
        self.setup_grid_layout()
    
    def setup_grid_layout(self):
        """Grid layout kurulumu"""
        # Eski layout'u temizle
        if self.app_content_widget.layout():
            QWidget().setLayout(self.app_content_widget.layout())
        
        # Grid layout
        self.app_layout = QGridLayout(self.app_content_widget)
        self.app_layout.setContentsMargins(12, 12, 12, 12)
        self.app_layout.setSpacing(12)
        
        # Responsive grid (pencere boyutuna göre sütun sayısı)
        self.update_grid_columns()
    
    def setup_list_layout(self):
        """Liste layout kurulumu"""
        # Eski layout'u temizle
        if self.app_content_widget.layout():
            QWidget().setLayout(self.app_content_widget.layout())
        
        # Vertical layout
        self.app_layout = QVBoxLayout(self.app_content_widget)
        self.app_layout.setContentsMargins(12, 12, 12, 12)
        self.app_layout.setSpacing(8)
        self.app_layout.addStretch()  # Alt boşluk
    
    def setup_status_bar(self):
        """Durum çubuğu kurulumu"""
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(12, 8, 12, 8)
        
        self.status_label = QLabel("Hazır")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.app_count_label = QLabel("")
        status_layout.addWidget(self.app_count_label)
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        # Sidebar
        self.sidebar.category_selected.connect(self.on_category_changed)
        
        # Search bar
        self.search_bar.search_requested.connect(self.on_search_requested)
        self.search_bar.filter_changed.connect(self.on_filter_changed)
        
        # Toolbar
        self.grid_view_btn.clicked.connect(lambda: self.change_view_mode(ViewMode.GRID))
        self.list_view_btn.clicked.connect(lambda: self.change_view_mode(ViewMode.LIST))
        self.detailed_view_btn.clicked.connect(lambda: self.change_view_mode(ViewMode.DETAILED))
        
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.settings_btn.clicked.connect(self.show_settings)
    
    def apply_theme(self):
        """Tema uygula"""
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        """Koyu tema"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QScrollArea {
                border: none;
                background-color: #2d2d2d;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:checked {
                background-color: #2196f3;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def apply_light_theme(self):
        """Açık tema"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333;
            }
            QWidget {
                background-color: #f5f5f5;
                color: #333;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px 12px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:checked {
                background-color: #2196f3;
                color: white;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px;
                color: #333;
            }
            QLabel {
                color: #333;
            }
        """)
    
    def load_data(self):
        """Veri yükle"""
        try:
            self.current_apps = self.data_manager.load_apps()
            self.update_category_counts()
            self.filter_and_display_apps()
            
            self.status_label.setText(f"{len(self.current_apps)} uygulama yüklendi")
            
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            self.status_label.setText("Veri yükleme hatası")
    
    def refresh_data(self):
        """Veriyi yenile"""
        self.status_label.setText("Yenileniyor...")
        
        # Thread'de yenile
        def refresh_worker():
            try:
                self.current_apps = self.data_manager.load_apps()
                QTimer.singleShot(0, self.on_refresh_completed)
            except Exception as e:
                self.logger.error(f"Refresh failed: {e}")
                QTimer.singleShot(0, lambda: self.status_label.setText("Yenileme hatası"))
        
        thread = threading.Thread(target=refresh_worker)
        thread.daemon = True
        thread.start()
    
    def on_refresh_completed(self):
        """Yenileme tamamlandı"""
        self.update_category_counts()
        self.filter_and_display_apps()
        self.status_label.setText("Yenileme tamamlandı")
    
    def update_category_counts(self):
        """Kategori sayılarını güncelle"""
        counts = self.data_manager.get_category_counts()
        self.sidebar.update_category_counts(counts)
    
    def filter_and_display_apps(self):
        """Uygulamaları filtrele ve göster"""
        # Kategori filtresi
        if self.current_category:
            self.filtered_apps = self.data_manager.get_apps_by_category(self.current_category)
        else:
            self.filtered_apps = self.current_apps.copy()
        
        # Arama filtresi
        if self.current_search:
            self.filtered_apps = [app for app in self.filtered_apps 
                                if self.current_search.lower() in app.name.lower() or
                                   self.current_search.lower() in app.description.lower()]
        
        # Sıralama
        self.sort_apps()
        
        # Görüntüle
        self.display_apps()
        
        # Durum güncelle
        self.app_count_label.setText(f"{len(self.filtered_apps)} uygulama")
    
    def sort_apps(self):
        """Uygulamaları sırala"""
        if self.current_sort_mode == SortMode.NAME:
            self.filtered_apps.sort(key=lambda app: app.name.lower())
        elif self.current_sort_mode == SortMode.CATEGORY:
            self.filtered_apps.sort(key=lambda app: app.category)
        elif self.current_sort_mode == SortMode.DEVELOPER:
            self.filtered_apps.sort(key=lambda app: app.developer)
        elif self.current_sort_mode == SortMode.RATING:
            self.filtered_apps.sort(key=lambda app: app.rating, reverse=True)
        elif self.current_sort_mode == SortMode.DOWNLOADS:
            self.filtered_apps.sort(key=lambda app: app.downloads, reverse=True)
    
    def display_apps(self):
        """Uygulamaları görüntüle"""
        # Mevcut widget'ları temizle
        self.clear_app_layout()
        
        if not self.filtered_apps:
            # Boş durum
            empty_label = QLabel("Hiç uygulama bulunamadı")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("font-size: 16px; color: #666; margin: 50px;")
            
            if self.current_view_mode == ViewMode.GRID:
                self.app_layout.addWidget(empty_label, 0, 0)
            else:
                self.app_layout.addWidget(empty_label)
            return
        
        # Uygulama kartlarını oluştur
        from .widgets import ModernAppCard
        
        for i, app_info in enumerate(self.filtered_apps):
            card = ModernAppCard(app_info, self.current_view_mode, self.dark_mode)
            
            # Sinyal bağlantıları
            card.install_requested.connect(self.install_app)
            card.remove_requested.connect(self.remove_app)
            card.update_requested.connect(self.update_app)
            card.info_requested.connect(self.show_app_info)
            
            # Layout'a ekle
            if self.current_view_mode == ViewMode.GRID:
                row = i // self.grid_columns
                col = i % self.grid_columns
                self.app_layout.addWidget(card, row, col)
            else:
                self.app_layout.addWidget(card)
    
    def clear_app_layout(self):
        """Uygulama layout'unu temizle"""
        while self.app_layout.count():
            child = self.app_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def update_grid_columns(self):
        """Grid sütun sayısını güncelle"""
        width = self.app_scroll_area.width() - 50  # Scroll bar için boşluk
        card_width = 220  # Kart genişliği + margin
        self.grid_columns = max(1, width // card_width)
    
    def change_view_mode(self, mode: ViewMode):
        """Görünüm modunu değiştir"""
        self.current_view_mode = mode
        
        if mode == ViewMode.GRID:
            self.setup_grid_layout()
        else:
            self.setup_list_layout()
        
        self.display_apps()
    
    def on_category_changed(self, category: str):
        """Kategori değişti"""
        self.current_category = category
        self.filter_and_display_apps()
    
    def on_search_requested(self, query: str):
        """Arama yapıldı"""
        self.current_search = query
        self.filter_and_display_apps()
    
    def on_filter_changed(self, filters: Dict[str, Any]):
        """Filtre değişti"""
        if "sort" in filters:
            sort_map = {
                "name": SortMode.NAME,
                "category": SortMode.CATEGORY,
                "developer": SortMode.DEVELOPER,
                "rating": SortMode.RATING,
                "downloads": SortMode.DOWNLOADS
            }
            self.current_sort_mode = sort_map.get(filters["sort"], SortMode.NAME)
            self.filter_and_display_apps()
        
        if "view" in filters:
            view_map = {
                "grid": ViewMode.GRID,
                "list": ViewMode.LIST,
                "detailed": ViewMode.DETAILED
            }
            mode = view_map.get(filters["view"], ViewMode.GRID)
            self.change_view_mode(mode)
    
    def on_sort_changed(self, sort_text: str):
        """Sıralama değişti"""
        sort_map = {
            "Ada göre": SortMode.NAME,
            "Kategoriye göre": SortMode.CATEGORY,
            "Geliştiriciye göre": SortMode.DEVELOPER,
            "Puana göre": SortMode.RATING,
            "İndirme sayısına göre": SortMode.DOWNLOADS
        }
        self.current_sort_mode = sort_map.get(sort_text, SortMode.NAME)
        self.filter_and_display_apps()
    
    def install_app(self, app_id: str):
        """Uygulama kur"""
        self.status_label.setText(f"Kuruluyor: {app_id}")
        
        # Thread'de kur
        def install_worker():
            success = self.data_manager.install_app(app_id)
            QTimer.singleShot(0, lambda: self.on_install_completed(app_id, success))
        
        thread = threading.Thread(target=install_worker)
        thread.daemon = True
        thread.start()
    
    def remove_app(self, app_id: str):
        """Uygulama kaldır"""
        # Onay al
        app = self.data_manager.apps.get(app_id)
        if not app:
            return
        
        reply = QMessageBox.question(
            self, "Uygulama Kaldır",
            f"'{app.name}' uygulamasını kaldırmak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText(f"Kaldırılıyor: {app.name}")
            
            # Thread'de kaldır
            def remove_worker():
                success = self.data_manager.remove_app(app_id)
                QTimer.singleShot(0, lambda: self.on_remove_completed(app_id, success))
            
            thread = threading.Thread(target=remove_worker)
            thread.daemon = True
            thread.start()
    
    def update_app(self, app_id: str):
        """Uygulama güncelle"""
        self.status_label.setText(f"Güncelleniyor: {app_id}")
        
        # Thread'de güncelle
        def update_worker():
            success = self.data_manager.update_app(app_id)
            QTimer.singleShot(0, lambda: self.on_update_completed(app_id, success))
        
        thread = threading.Thread(target=update_worker)
        thread.daemon = True
        thread.start()
    
    def on_install_completed(self, app_id: str, success: bool):
        """Kurulum tamamlandı"""
        if success:
            self.status_label.setText("Kurulum başarılı")
            self.update_category_counts()
            self.filter_and_display_apps()
        else:
            self.status_label.setText("Kurulum başarısız")
    
    def on_remove_completed(self, app_id: str, success: bool):
        """Kaldırma tamamlandı"""
        if success:
            self.status_label.setText("Kaldırma başarılı")
            self.update_category_counts()
            self.filter_and_display_apps()
        else:
            self.status_label.setText("Kaldırma başarısız")
    
    def on_update_completed(self, app_id: str, success: bool):
        """Güncelleme tamamlandı"""
        if success:
            self.status_label.setText("Güncelleme başarılı")
            self.filter_and_display_apps()
        else:
            self.status_label.setText("Güncelleme başarısız")
    
    def show_app_info(self, app_id: str):
        """Uygulama bilgilerini göster"""
        app = self.data_manager.apps.get(app_id)
        if not app:
            return
        
        # Detay dialog'u göster
        from .dialogs import AppDetailDialog
        dialog = AppDetailDialog(app, self.dark_mode, self)
        
        # Sinyal bağlantıları
        dialog.install_requested.connect(self.install_app)
        dialog.remove_requested.connect(self.remove_app)
        dialog.update_requested.connect(self.update_app)
        
        dialog.exec()
    
    def show_settings(self):
        """Ayarları göster"""
        # Ayar dialog'u
        dialog = QDialog(self)
        dialog.setWindowTitle("AppStore Ayarları")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Tema seçimi
        theme_group = QGroupBox("Tema")
        theme_layout = QVBoxLayout(theme_group)
        
        light_radio = QRadioButton("Açık Tema")
        dark_radio = QRadioButton("Koyu Tema")
        
        if self.dark_mode:
            dark_radio.setChecked(True)
        else:
            light_radio.setChecked(True)
        
        theme_layout.addWidget(light_radio)
        theme_layout.addWidget(dark_radio)
        layout.addWidget(theme_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Tamam")
        cancel_btn = QPushButton("İptal")
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Bağlantılar
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Tema değişikliği
        def on_theme_changed():
            self.dark_mode = dark_radio.isChecked()
            self.apply_theme()
            self.sidebar.dark_mode = self.dark_mode
            self.sidebar.apply_theme()
            self.search_bar.dark_mode = self.dark_mode
            self.search_bar.apply_theme()
            self.filter_and_display_apps()  # Kartları yenile
        
        light_radio.toggled.connect(on_theme_changed)
        dark_radio.toggled.connect(on_theme_changed)
        
        dialog.exec()
    
    def resizeEvent(self, event):
        """Pencere boyutu değişti"""
        super().resizeEvent(event)
        if self.current_view_mode == ViewMode.GRID:
            self.update_grid_columns()
            self.display_apps()

def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud AppStore")
    app.setApplicationVersion("2.0.0")
    
    # Ana pencere
    window = CloudAppStore()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 