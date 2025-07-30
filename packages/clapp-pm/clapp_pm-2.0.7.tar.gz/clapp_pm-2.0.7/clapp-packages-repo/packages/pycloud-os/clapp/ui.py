"""
PyCloud OS Clapp UI
Clapp altyapısıyla entegre çalışan, kullanıcıya uygulamaları grafik olarak sunan modern App Store arayüzü
"""

import os
import sys
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtNetwork import *
except ImportError:
    print("PyQt6 not available for Clapp UI")
    sys.exit(1)

from .core import ClappCore, CommandResult
from .repo import RepositoryManager, PackageInfo, Repository

class AppCard(QWidget):
    """Uygulama kartı widget'ı"""
    
    install_requested = pyqtSignal(str)  # app_id
    remove_requested = pyqtSignal(str)   # app_id
    info_requested = pyqtSignal(str)     # app_id
    
    def __init__(self, package: PackageInfo, is_installed: bool = False):
        super().__init__()
        self.package = package
        self.is_installed = is_installed
        self.logger = logging.getLogger("AppCard")
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Üst kısım: İkon ve temel bilgiler
        top_layout = QHBoxLayout()
        
        # İkon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f5f5f5;
            }
        """)
        self.load_icon()
        top_layout.addWidget(self.icon_label)
        
        # Bilgiler
        info_layout = QVBoxLayout()
        
        # Uygulama adı
        self.name_label = QLabel(self.package.name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.name_label)
        
        # Geliştirici
        self.developer_label = QLabel(f"by {self.package.developer}")
        self.developer_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(self.developer_label)
        
        # Kategori ve sürüm
        meta_layout = QHBoxLayout()
        self.category_label = QLabel(self.package.category)
        self.category_label.setStyleSheet("""
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
        """)
        
        self.version_label = QLabel(f"v{self.package.version}")
        self.version_label.setStyleSheet("color: #888; font-size: 11px;")
        
        meta_layout.addWidget(self.category_label)
        meta_layout.addStretch()
        meta_layout.addWidget(self.version_label)
        info_layout.addLayout(meta_layout)
        
        top_layout.addLayout(info_layout)
        layout.addLayout(top_layout)
        
        # Açıklama
        self.description_label = QLabel(self.package.description[:100] + "..." if len(self.package.description) > 100 else self.package.description)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555; font-size: 12px; margin: 5px 0;")
        layout.addWidget(self.description_label)
        
        # Etiketler
        if self.package.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(4)
            
            for tag in self.package.tags[:3]:  # Maksimum 3 etiket
                tag_label = QLabel(f"#{tag}")
                tag_label.setStyleSheet("""
                    background-color: #f0f0f0;
                    color: #666;
                    padding: 1px 4px;
                    border-radius: 6px;
                    font-size: 10px;
                """)
                tags_layout.addWidget(tag_label)
            
            tags_layout.addStretch()
            layout.addLayout(tags_layout)
        
        # Alt kısım: Butonlar
        buttons_layout = QHBoxLayout()
        
        # Ana buton (Kur/Kaldır)
        if self.is_installed:
            self.main_button = QPushButton("Kaldır")
            self.main_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            self.main_button.clicked.connect(lambda: self.remove_requested.emit(self.package.id))
        else:
            self.main_button = QPushButton("Kur")
            self.main_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.main_button.clicked.connect(lambda: self.install_requested.emit(self.package.id))
        
        # Bilgi butonu
        self.info_button = QPushButton("Bilgi")
        self.info_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.info_button.clicked.connect(lambda: self.info_requested.emit(self.package.id))
        
        buttons_layout.addWidget(self.main_button)
        buttons_layout.addWidget(self.info_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
    
    def setup_style(self):
        """Kart stilini ayarla"""
        self.setStyleSheet("""
            AppCard {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                margin: 5px;
            }
            AppCard:hover {
                border-color: #2196f3;
            }
        """)
        self.setFixedHeight(180)
    
    def load_icon(self):
        """İkonu yükle"""
        try:
            # Önce yerel kurulu uygulamanın ikonunu kontrol et
            local_icon_path = Path(f"apps/{self.package.id}/icon.png")
            if local_icon_path.exists():
                local_pixmap = QPixmap(str(local_icon_path))
                if not local_pixmap.isNull():
                    # İkonu yüksek kalitede boyutlandır
                    scaled_pixmap = local_pixmap.scaled(
                        48, 48, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    # Şeffaf arka plan ile temiz ikon oluştur
                    clean_pixmap = QPixmap(48, 48)
                    clean_pixmap.fill(Qt.GlobalColor.transparent)
                    
                    painter = QPainter(clean_pixmap)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                    
                    # İkonu ortala
                    x = (48 - scaled_pixmap.width()) // 2
                    y = (48 - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x, y, scaled_pixmap)
                    painter.end()
                    
                    self.icon_label.setPixmap(clean_pixmap)
                    return
            
            # İkon URL'si varsa indir (basit implementasyon)
            if self.package.icon_url:
                # TODO: Asenkron ikon indirme
                pass
            
            # Fallback: varsayılan ikon
            pixmap = QPixmap(48, 48)
            pixmap.fill(QColor("#e0e0e0"))
            self.icon_label.setPixmap(pixmap)
            
        except Exception as e:
            self.logger.error(f"Failed to load icon: {e}")
            # Hata durumunda varsayılan ikon göster
            fallback_pixmap = QPixmap(48, 48)
            fallback_pixmap.fill(QColor("#e0e0e0"))
            self.icon_label.setPixmap(fallback_pixmap)

class AppDetailDialog(QDialog):
    """Uygulama detay dialog'u"""
    
    install_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    
    def __init__(self, package: PackageInfo, is_installed: bool = False, parent=None):
        super().__init__(parent)
        self.package = package
        self.is_installed = is_installed
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle(f"{self.package.name} - Uygulama Detayları")
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Başlık alanı
        header_layout = QHBoxLayout()
        
        # İkon
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setStyleSheet("""
            border: 1px solid #ddd;
            border-radius: 12px;
            background-color: #f5f5f5;
        """)
        header_layout.addWidget(icon_label)
        
        # Başlık bilgileri
        title_layout = QVBoxLayout()
        
        name_label = QLabel(self.package.name)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(name_label)
        
        developer_label = QLabel(f"Geliştirici: {self.package.developer}")
        developer_label.setStyleSheet("color: #666;")
        title_layout.addWidget(developer_label)
        
        version_label = QLabel(f"Sürüm: {self.package.version}")
        version_label.setStyleSheet("color: #666;")
        title_layout.addWidget(version_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Bilgi alanları
        info_scroll = QScrollArea()
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # Açıklama
        desc_group = QGroupBox("Açıklama")
        desc_layout = QVBoxLayout(desc_group)
        desc_label = QLabel(self.package.description)
        desc_label.setWordWrap(True)
        desc_layout.addWidget(desc_label)
        info_layout.addWidget(desc_group)
        
        # Teknik bilgiler
        tech_group = QGroupBox("Teknik Bilgiler")
        tech_layout = QFormLayout(tech_group)
        tech_layout.addRow("Kategori:", QLabel(self.package.category))
        tech_layout.addRow("Lisans:", QLabel(self.package.license))
        tech_layout.addRow("Boyut:", QLabel(f"{self.package.size_mb:.1f} MB"))
        tech_layout.addRow("Repository:", QLabel(self.package.repository_name))
        info_layout.addWidget(tech_group)
        
        # Etiketler
        if self.package.tags:
            tags_group = QGroupBox("Etiketler")
            tags_layout = QHBoxLayout(tags_group)
            
            for tag in self.package.tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setStyleSheet("""
                    background-color: #e3f2fd;
                    color: #1976d2;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                """)
                tags_layout.addWidget(tag_label)
            
            tags_layout.addStretch()
            info_layout.addWidget(tags_group)
        
        # Bağımlılıklar
        if self.package.depends:
            deps_group = QGroupBox("Bağımlılıklar")
            deps_layout = QVBoxLayout(deps_group)
            
            for dep in self.package.depends:
                dep_label = QLabel(f"• {dep}")
                deps_layout.addWidget(dep_label)
            
            info_layout.addWidget(deps_group)
        
        # Homepage
        if self.package.homepage:
            homepage_group = QGroupBox("Bağlantılar")
            homepage_layout = QVBoxLayout(homepage_group)
            
            homepage_label = QLabel(f'<a href="{self.package.homepage}">Ana Sayfa</a>')
            homepage_label.setOpenExternalLinks(True)
            homepage_layout.addWidget(homepage_label)
            
            info_layout.addWidget(homepage_group)
        
        info_scroll.setWidget(info_widget)
        info_scroll.setWidgetResizable(True)
        layout.addWidget(info_scroll)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        if self.is_installed:
            remove_button = QPushButton("Kaldır")
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            remove_button.clicked.connect(lambda: self.remove_requested.emit(self.package.id))
            buttons_layout.addWidget(remove_button)
        else:
            install_button = QPushButton("Kur")
            install_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            install_button.clicked.connect(lambda: self.install_requested.emit(self.package.id))
            buttons_layout.addWidget(install_button)
        
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def setup_style(self):
        """Dialog stilini ayarla"""
        self.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

class ProgressDialog(QDialog):
    """İlerleme dialog'u"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 120)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("İşlem başlatılıyor...")
        layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)
    
    def update_status(self, message: str):
        """Durum mesajını güncelle"""
        self.label.setText(message)

class ClappUI(QMainWindow):
    """Ana Clapp UI sınıfı"""
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("ClappUI")
        
        # Core modüller
        self.clapp_core = ClappCore(kernel)
        self.repo_manager = None
        
        # UI durumu
        self.current_packages = []
        self.installed_apps = set()
        self.current_category = "Tümü"
        self.search_query = ""
        
        # Repository manager'ı başlat
        self.init_repo_manager()
        
        # UI kurulumu
        self.setup_ui()
        self.setup_style()
        self.setup_connections()
        
        # İlk yükleme
        self.refresh_data()
    
    def init_repo_manager(self):
        """Repository manager'ı başlat"""
        try:
            from .repo import init_repository_manager
            self.repo_manager = init_repository_manager(self.kernel)
        except Exception as e:
            self.logger.error(f"Failed to initialize repository manager: {e}")
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle("PyCloud App Store")
        self.setGeometry(100, 100, 1000, 700)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        
        # Sol panel (kategoriler)
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Sağ panel (uygulamalar)
        self.setup_main_panel()
        main_layout.addWidget(self.main_panel, 1)
        
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
        title_label = QLabel("Kategoriler")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Kategori listesi
        self.category_list = QListWidget()
        self.category_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        
        # Varsayılan kategoriler
        categories = ["Tümü", "Sistem", "Geliştirme", "Ofis", "Eğlence", "Grafik", "İnternet", "Multimedya", "Araçlar", "Oyunlar", "Eğitim"]
        for category in categories:
            self.category_list.addItem(category)
        
        self.category_list.setCurrentRow(0)
        layout.addWidget(self.category_list)
        
        layout.addStretch()
        
        # Yenile butonu
        refresh_button = QPushButton("Yenile")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        refresh_button.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_button)
    
    def setup_main_panel(self):
        """Ana panel kurulumu"""
        self.main_panel = QWidget()
        
        layout = QVBoxLayout(self.main_panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Üst araç çubuğu
        toolbar_layout = QHBoxLayout()
        
        # Arama kutusu
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Uygulama ara...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 20px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2196f3;
            }
        """)
        toolbar_layout.addWidget(self.search_input)
        
        # Arama butonu
        search_button = QPushButton("Ara")
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        search_button.clicked.connect(self.search_apps)
        toolbar_layout.addWidget(search_button)
        
        layout.addLayout(toolbar_layout)
        
        # Uygulama listesi
        self.setup_app_list()
        layout.addWidget(self.app_scroll_area)
    
    def setup_app_list(self):
        """Uygulama listesi kurulumu"""
        self.app_scroll_area = QScrollArea()
        self.app_scroll_area.setWidgetResizable(True)
        self.app_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        self.app_container = QWidget()
        self.app_layout = QVBoxLayout(self.app_container)
        self.app_layout.setSpacing(10)
        self.app_layout.addStretch()
        
        self.app_scroll_area.setWidget(self.app_container)
    
    def setup_statusbar(self):
        """Durum çubuğu kurulumu"""
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Hazır")
        self.status_bar.addWidget(self.status_label)
        
        # Sağ tarafta istatistikler
        self.stats_label = QLabel("")
        self.status_bar.addPermanentWidget(self.stats_label)
    
    def setup_style(self):
        """Ana stil ayarları"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        self.category_list.currentTextChanged.connect(self.on_category_changed)
        self.search_input.returnPressed.connect(self.search_apps)
    
    def refresh_data(self):
        """Verileri yenile"""
        self.status_label.setText("Veriler yenileniyor...")
        
        # Thread'de yenile
        self.refresh_thread = QThread()
        self.refresh_worker = RefreshWorker(self.repo_manager, self.clapp_core)
        self.refresh_worker.moveToThread(self.refresh_thread)
        
        self.refresh_thread.started.connect(self.refresh_worker.run)
        self.refresh_worker.finished.connect(self.on_refresh_finished)
        self.refresh_worker.error.connect(self.on_refresh_error)
        
        self.refresh_thread.start()
    
    def on_refresh_finished(self, packages, installed_apps):
        """Yenileme tamamlandı"""
        self.current_packages = packages
        self.installed_apps = set(installed_apps)
        
        self.update_app_list()
        self.update_stats()
        
        self.status_label.setText("Hazır")
        self.refresh_thread.quit()
    
    def on_refresh_error(self, error_message):
        """Yenileme hatası"""
        self.status_label.setText(f"Hata: {error_message}")
        self.refresh_thread.quit()
        
        QMessageBox.warning(self, "Hata", f"Veriler yenilenirken hata oluştu:\n{error_message}")
    
    def on_category_changed(self, category):
        """Kategori değişti"""
        self.current_category = category
        self.update_app_list()
    
    def search_apps(self):
        """Uygulama ara"""
        self.search_query = self.search_input.text().strip()
        self.update_app_list()
    
    def update_app_list(self):
        """Uygulama listesini güncelle"""
        # Mevcut kartları temizle
        for i in reversed(range(self.app_layout.count() - 1)):  # -1 çünkü stretch var
            child = self.app_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Filtreleme
        filtered_packages = self.filter_packages()
        
        if not filtered_packages:
            no_apps_label = QLabel("Hiç uygulama bulunamadı")
            no_apps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_apps_label.setStyleSheet("color: #666; font-size: 16px; margin: 50px;")
            self.app_layout.insertWidget(0, no_apps_label)
            return
        
        # Uygulama kartlarını oluştur
        for package in filtered_packages:
            is_installed = package.id in self.installed_apps
            card = AppCard(package, is_installed)
            
            # Sinyal bağlantıları
            card.install_requested.connect(self.install_app)
            card.remove_requested.connect(self.remove_app)
            card.info_requested.connect(self.show_app_info)
            
            self.app_layout.insertWidget(self.app_layout.count() - 1, card)
    
    def filter_packages(self) -> List[PackageInfo]:
        """Paketleri filtrele"""
        filtered = self.current_packages
        
        # Kategori filtresi
        if self.current_category != "Tümü":
            filtered = [p for p in filtered if p.category == self.current_category]
        
        # Arama filtresi
        if self.search_query:
            query_lower = self.search_query.lower()
            filtered = [p for p in filtered if 
                       query_lower in p.name.lower() or 
                       query_lower in p.description.lower() or
                       query_lower in p.developer.lower() or
                       any(query_lower in tag.lower() for tag in p.tags)]
        
        # Alfabetik sırala
        filtered.sort(key=lambda p: p.name.lower())
        
        return filtered
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        total_packages = len(self.current_packages)
        installed_count = len(self.installed_apps)
        
        self.stats_label.setText(f"Toplam: {total_packages} | Kurulu: {installed_count}")
    
    def install_app(self, app_id: str):
        """Uygulama kur"""
        package = next((p for p in self.current_packages if p.id == app_id), None)
        if not package:
            return
        
        # Onay dialog'u
        reply = QMessageBox.question(
            self, "Kurulum Onayı",
            f"{package.name} uygulamasını kurmak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # İlerleme dialog'u
        progress_dialog = ProgressDialog("Uygulama Kuruluyor", self)
        progress_dialog.show()
        
        # Thread'de kur
        self.install_thread = QThread()
        self.install_worker = InstallWorker(self.clapp_core, app_id, "install")
        self.install_worker.moveToThread(self.install_thread)
        
        self.install_thread.started.connect(self.install_worker.run)
        self.install_worker.status_updated.connect(progress_dialog.update_status)
        self.install_worker.finished.connect(lambda success, message: self.on_install_finished(success, message, progress_dialog))
        
        self.install_thread.start()
    
    def remove_app(self, app_id: str):
        """Uygulama kaldır"""
        package = next((p for p in self.current_packages if p.id == app_id), None)
        if not package:
            return
        
        # Onay dialog'u
        reply = QMessageBox.question(
            self, "Kaldırma Onayı",
            f"{package.name} uygulamasını kaldırmak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # İlerleme dialog'u
        progress_dialog = ProgressDialog("Uygulama Kaldırılıyor", self)
        progress_dialog.show()
        
        # Thread'de kaldır
        self.remove_thread = QThread()
        self.remove_worker = InstallWorker(self.clapp_core, app_id, "remove")
        self.remove_worker.moveToThread(self.remove_thread)
        
        self.remove_thread.started.connect(self.remove_worker.run)
        self.remove_worker.status_updated.connect(progress_dialog.update_status)
        self.remove_worker.finished.connect(lambda success, message: self.on_install_finished(success, message, progress_dialog))
        
        self.remove_thread.start()
    
    def on_install_finished(self, success: bool, message: str, progress_dialog: ProgressDialog):
        """Kurulum/kaldırma tamamlandı"""
        progress_dialog.close()
        
        if success:
            QMessageBox.information(self, "Başarılı", message)
            # Listeyi yenile
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Hata", message)
        
        # Thread'i temizle
        if hasattr(self, 'install_thread'):
            self.install_thread.quit()
        if hasattr(self, 'remove_thread'):
            self.remove_thread.quit()
    
    def show_app_info(self, app_id: str):
        """Uygulama bilgilerini göster"""
        package = next((p for p in self.current_packages if p.id == app_id), None)
        if not package:
            return
        
        is_installed = app_id in self.installed_apps
        dialog = AppDetailDialog(package, is_installed, self)
        
        # Sinyal bağlantıları
        dialog.install_requested.connect(self.install_app)
        dialog.remove_requested.connect(self.remove_app)
        
        dialog.exec()

class RefreshWorker(QObject):
    """Veri yenileme worker'ı"""
    
    finished = pyqtSignal(list, list)  # packages, installed_apps
    error = pyqtSignal(str)
    
    def __init__(self, repo_manager, clapp_core):
        super().__init__()
        self.repo_manager = repo_manager
        self.clapp_core = clapp_core
    
    def run(self):
        """Worker çalıştır"""
        try:
            packages = []
            installed_apps = []
            
            # Repository paketlerini al
            if self.repo_manager:
                self.repo_manager.refresh_repositories()
                packages = self.repo_manager.get_all_packages()
            
            # Kurulu uygulamaları al
            appkit = self.clapp_core._get_appkit()
            if appkit:
                installed_app_infos = appkit.get_installed_apps()
                installed_apps = [app.metadata.id for app in installed_app_infos]
            
            self.finished.emit(packages, installed_apps)
            
        except Exception as e:
            self.error.emit(str(e))

class InstallWorker(QObject):
    """Kurulum/kaldırma worker'ı"""
    
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, clapp_core, app_id: str, operation: str):
        super().__init__()
        self.clapp_core = clapp_core
        self.app_id = app_id
        self.operation = operation
    
    def run(self):
        """Worker çalıştır"""
        try:
            if self.operation == "install":
                self.status_updated.emit(f"{self.app_id} kuruluyor...")
                result = self.clapp_core.execute_command(f"install {self.app_id}")
            elif self.operation == "remove":
                self.status_updated.emit(f"{self.app_id} kaldırılıyor...")
                result = self.clapp_core.execute_command(f"remove {self.app_id}")
            else:
                self.finished.emit(False, "Bilinmeyen işlem")
                return
            
            success = result.result == CommandResult.SUCCESS
            self.finished.emit(success, result.output)
            
        except Exception as e:
            self.finished.emit(False, str(e))

def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setApplicationName("PyCloud App Store")
    app.setApplicationVersion("1.0.0")
    
    # Ana pencere
    window = ClappUI()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 