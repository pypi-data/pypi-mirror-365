"""
Cloud Browser Ana Uygulama
Modern sekmeli web tarayıcısı
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import base64

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWebEngineWidgets import *
    from PyQt6.QtWebEngineCore import *
    WEBENGINE_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
        WEBENGINE_AVAILABLE = False
    except ImportError:
        raise ImportError("PyQt6 is required for Cloud Browser")

from .browser_ui import BrowserTabWidget, NavigationToolbar, StatusBarWidget
from .bookmarks import BookmarkManager
from .settings import BrowserSettings
from .pdf_viewer import PDFViewer

class CloudBrowser(QMainWindow):
    """
    Cloud Browser Ana Sınıfı
    Modern sekmeli web tarayıcısı
    """
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("CloudBrowser")
        
        # Managers
        self.bookmark_manager = BookmarkManager()
        self.settings = BrowserSettings()
        
        # UI Components
        self.tab_widget = None
        self.navigation_toolbar = None
        self.status_widget = None
        
        # State
        self.is_fullscreen = False
        self.closed_tabs = []  # Son kapatılan sekmeler
        
        self.init_ui()
        self.setup_shortcuts()
        self.apply_theme()
        self.load_settings()
        
        # İlk sekmeyi aç (UI hazır olduktan sonra)
        QTimer.singleShot(10, lambda: self.new_tab("https://www.google.com"))
        
        self.logger.info("CloudBrowser initialized successfully")
    
    def init_ui(self):
        """UI'yı başlat"""
        self.setWindowTitle("Cloud Browser v2.0.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigasyon toolbar
        self.navigation_toolbar = NavigationToolbar(self)
        main_layout.addWidget(self.navigation_toolbar)
        
        # Tab widget
        self.tab_widget = BrowserTabWidget(self)
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_widget = StatusBarWidget(self)
        self.setStatusBar(self.status_widget)
        
        # Menü çubuğu
        self.create_menu_bar()
        
        self.logger.info("UI initialized")
    
    def create_menu_bar(self):
        """Menü çubuğu oluştur"""
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu('📁 Dosya')
        
        # Yeni sekme
        new_tab_action = QAction('🆕 Yeni Sekme', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(lambda: self.new_tab())
        file_menu.addAction(new_tab_action)
        
        # Yeni pencere
        new_window_action = QAction('🪟 Yeni Pencere', self)
        new_window_action.setShortcut('Ctrl+N')
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        # Dosya aç
        open_file_action = QAction('�� Dosya Aç...', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        file_menu.addSeparator()
        
        # Çıkış
        exit_action = QAction('❌ Çıkış', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Düzenle menüsü
        edit_menu = menubar.addMenu('✏️ Düzenle')
        
        # Geri al
        undo_action = QAction('↶ Geri Al', self)
        undo_action.setShortcut('Ctrl+Z')
        edit_menu.addAction(undo_action)
        
        # İleri al
        redo_action = QAction('↷ İleri Al', self)
        redo_action.setShortcut('Ctrl+Y')
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # Kopyala
        copy_action = QAction('📋 Kopyala', self)
        copy_action.setShortcut('Ctrl+C')
        edit_menu.addAction(copy_action)
        
        # Yapıştır
        paste_action = QAction('📌 Yapıştır', self)
        paste_action.setShortcut('Ctrl+V')
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        # Sayfada bul
        find_action = QAction('🔍 Sayfada Bul...', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # Görünüm menüsü
        view_menu = menubar.addMenu('👁️ Görünüm')
        
        # Tam ekran
        fullscreen_action = QAction('🖥️ Tam Ekran', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        view_menu.addSeparator()
        
        # Yakınlaştır
        zoom_in_action = QAction('🔍+ Yakınlaştır', self)
        zoom_in_action.setShortcut('Ctrl+=')
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        # Uzaklaştır
        zoom_out_action = QAction('🔍- Uzaklaştır', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        # Normal boyut
        zoom_reset_action = QAction('🔍 Normal Boyut', self)
        zoom_reset_action.setShortcut('Ctrl+0')
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Yer imleri menüsü
        bookmarks_menu = menubar.addMenu('⭐ Yer İmleri')
        
        # Yer imi ekle
        add_bookmark_action = QAction('➕ Bu Sayfayı Yer İmlerine Ekle', self)
        add_bookmark_action.setShortcut('Ctrl+D')
        add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)
        
        # Yer imi yöneticisi
        manage_bookmarks_action = QAction('📚 Yer İmi Yöneticisi', self)
        manage_bookmarks_action.setShortcut('Ctrl+Shift+O')
        manage_bookmarks_action.triggered.connect(self.show_bookmark_manager)
        bookmarks_menu.addAction(manage_bookmarks_action)
        
        bookmarks_menu.addSeparator()
        
        # Dinamik yer imi listesi
        self.update_bookmarks_menu(bookmarks_menu)
        
        # Araçlar menüsü
        tools_menu = menubar.addMenu('🔧 Araçlar')
        
        # İndirme yöneticisi
        downloads_action = QAction('📥 İndirme Yöneticisi', self)
        downloads_action.setShortcut('Ctrl+Shift+Y')
        downloads_action.triggered.connect(self.show_download_manager)
        tools_menu.addAction(downloads_action)
        
        # Geliştirici araçları
        devtools_action = QAction('🛠️ Geliştirici Araçları', self)
        devtools_action.setShortcut('F12')
        devtools_action.triggered.connect(self.toggle_devtools)
        tools_menu.addAction(devtools_action)
        
        tools_menu.addSeparator()
        
        # Ayarlar
        settings_action = QAction('⚙️ Ayarlar', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Yardım menüsü
        help_menu = menubar.addMenu('❓ Yardım')
        
        # Hakkında
        about_action = QAction('ℹ️ Cloud Browser Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        shortcuts = {
            'Ctrl+T': lambda: self.new_tab(),
            'Ctrl+W': self.close_current_tab,
            'Ctrl+Shift+T': self.reopen_closed_tab,
            'Ctrl+Tab': self.next_tab,
            'Ctrl+Shift+Tab': self.prev_tab,
            'Ctrl+1': lambda: self.switch_to_tab(0),
            'Ctrl+2': lambda: self.switch_to_tab(1),
            'Ctrl+3': lambda: self.switch_to_tab(2),
            'Ctrl+4': lambda: self.switch_to_tab(3),
            'Ctrl+5': lambda: self.switch_to_tab(4),
            'Ctrl+6': lambda: self.switch_to_tab(5),
            'Ctrl+7': lambda: self.switch_to_tab(6),
            'Ctrl+8': lambda: self.switch_to_tab(7),
            'Ctrl+9': self.switch_to_last_tab,
            'Alt+Left': self.go_back,
            'Alt+Right': self.go_forward,
            'F5': self.reload_page,
            'Ctrl+R': self.reload_page,
            'Ctrl+L': self.focus_address_bar,
            'Escape': self.stop_loading
        }
        
        for key, func in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)
        
        self.logger.info("Shortcuts configured")
    
    def apply_theme(self):
        """Tema uygula"""
        if self.settings.get('dark_mode', True):
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: none;
                    padding: 4px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 8px 12px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #4a4a4a;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #4a4a4a;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #555555;
                    margin: 4px 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: none;
                    padding: 4px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 8px 12px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #cccccc;
                    margin: 4px 8px;
                }
            """)
    
    def load_settings(self):
        """Ayarları yükle"""
        # Pencere boyutu ve konumu
        geometry_str = self.settings.get('window_geometry')
        if geometry_str:
            try:
                # Base64 string'i QByteArray'e çevir
                geometry = base64.b64decode(geometry_str.encode('utf-8'))
                self.restoreGeometry(geometry)
            except Exception as e:
                self.logger.warning(f"Geometry restore failed: {e}")
        
        # Not: İlk sekme manuel olarak açılıyor, burada eski sekmeleri geri yükleme
    
    def save_settings(self):
        """Ayarları kaydet"""
        # Pencere boyutu ve konumu
        geometry = self.saveGeometry()
        if geometry:
            # QByteArray'i base64 string'e çevir
            geometry_str = base64.b64encode(geometry).decode('utf-8')
            self.settings.set('window_geometry', geometry_str)
        
        # Açık sekmeler
        current_tabs = []
        if self.tab_widget:
            for i in range(self.tab_widget.count()):
                web_view = self.tab_widget.widget(i)
                if hasattr(web_view, 'url'):
                    url = web_view.url().toString()
                    if url and url != "about:blank":
                        current_tabs.append(url)
        
        self.settings.set('last_tabs', current_tabs)
        self.settings.save()
    
    # Tab Management Methods
    def new_tab(self, url="about:blank"):
        """Yeni sekme aç"""
        if self.tab_widget is not None:
            self.tab_widget.new_tab(url)
    
    def close_current_tab(self):
        """Mevcut sekmeyi kapat"""
        if self.tab_widget:
            current_index = self.tab_widget.currentIndex()
            if current_index >= 0:
                self.close_tab(current_index)
    
    def close_tab(self, index):
        """Belirtilen sekmeyi kapat"""
        if self.tab_widget:
            self.tab_widget.close_tab(index)
    
    def next_tab(self):
        """Sonraki sekmeye geç"""
        if self.tab_widget:
            self.tab_widget.next_tab()
    
    def prev_tab(self):
        """Önceki sekmeye geç"""
        if self.tab_widget:
            self.tab_widget.prev_tab()
    
    def switch_to_tab(self, index):
        """Belirtilen sekmeye geç"""
        if self.tab_widget and 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def switch_to_last_tab(self):
        """Son sekmeye geç"""
        if self.tab_widget:
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
    
    def reopen_closed_tab(self):
        """Son kapatılan sekmeyi yeniden aç"""
        if self.closed_tabs:
            url = self.closed_tabs.pop()
            self.new_tab(url)
    
    # Navigation Methods
    def go_back(self):
        """Geri git"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'back'):
                current_web_view.back()
    
    def go_forward(self):
        """İleri git"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'forward'):
                current_web_view.forward()
    
    def reload_page(self):
        """Sayfayı yenile"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'reload'):
                current_web_view.reload()
    
    def stop_loading(self):
        """Yüklemeyi durdur"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'stop'):
                current_web_view.stop()
    
    def focus_address_bar(self):
        """Adres çubuğuna odaklan"""
        if self.navigation_toolbar:
            self.navigation_toolbar.focus_address_bar()
    
    # View Methods
    def zoom_in(self):
        """Yakınlaştır"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'setZoomFactor'):
                current_zoom = current_web_view.zoomFactor()
                current_web_view.setZoomFactor(min(current_zoom * 1.1, 3.0))
    
    def zoom_out(self):
        """Uzaklaştır"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'setZoomFactor'):
                current_zoom = current_web_view.zoomFactor()
                current_web_view.setZoomFactor(max(current_zoom * 0.9, 0.25))
    
    def zoom_reset(self):
        """Normal boyut"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'setZoomFactor'):
                current_web_view.setZoomFactor(1.0)
    
    def toggle_fullscreen(self):
        """Tam ekran aç/kapat"""
        if self.isFullScreen():
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
    
    # File Methods
    def open_file(self):
        """Dosya aç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Dosya Aç",
            "",
            "Web Dosyaları (*.html *.htm);;PDF Dosyaları (*.pdf);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            file_url = f"file://{file_path}"
            self.new_tab(file_url)
    
    def new_window(self):
        """Yeni pencere aç"""
        new_browser = CloudBrowser(self.kernel)
        new_browser.show()
    
    # Bookmark Methods
    def add_bookmark(self):
        """Yer imi ekle"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'url'):
                url = current_web_view.url().toString()
                title = current_web_view.title() if hasattr(current_web_view, 'title') else url
                
                if self.bookmark_manager.add_bookmark(title, url):
                    self.status_widget.show_message(f"Yer imi eklendi: {title}", 3000)
                else:
                    self.status_widget.show_message("Bu sayfa zaten yer imlerinde", 3000)
            else:
                self.status_widget.show_message("Yer imi eklenemedi", 3000)
    
    def show_bookmark_manager(self):
        """Yer imi yöneticisini göster"""
        from .bookmarks import BookmarkManagerDialog
        dialog = BookmarkManagerDialog(self.bookmark_manager, self)
        dialog.exec()
    
    def update_bookmarks_menu(self, menu):
        """Yer imi menüsünü güncelle"""
        # Mevcut dinamik öğeleri temizle
        actions = menu.actions()
        for action in actions[3:]:  # İlk 3 sabit öğe
            menu.removeAction(action)
        
        # Yer imlerini ekle
        bookmarks = self.bookmark_manager.get_bookmarks()
        if bookmarks:
            for bookmark in bookmarks[:10]:  # İlk 10 yer imi
                action = QAction(f"⭐ {bookmark['title']}", self)
                action.triggered.connect(lambda checked, url=bookmark['url']: self.new_tab(url))
                menu.addAction(action)
    
    # Tool Methods
    def show_download_manager(self):
        """İndirme yöneticisini göster"""
        # Basit indirme yöneticisi dialog'u
        dialog = QDialog(self)
        dialog.setWindowTitle("İndirme Yöneticisi")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Başlık
        title_label = QLabel("📥 İndirme Yöneticisi")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # İçerik
        content_label = QLabel("""
        <p>İndirme yöneticisi henüz tam olarak implementasyonda.</p>
        <p><b>Planlanan özellikler:</b></p>
        <ul>
        <li>Aktif indirmeler listesi</li>
        <li>İndirme geçmişi</li>
        <li>İndirme klasörü yönetimi</li>
        <li>İndirme hızı ve ilerleme göstergesi</li>
        <li>İndirmeleri duraklat/devam ettir</li>
        </ul>
        <p>Şu anda dosyalar varsayılan indirme klasörüne kaydedilir.</p>
        """)
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def toggle_devtools(self):
        """Geliştirici araçlarını aç/kapat"""
        if self.tab_widget:
            current_web_view = self.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'page'):
                # TODO: DevTools implementasyonu
                QMessageBox.information(self, "Geliştirici Araçları", "Geliştirici araçları henüz implementasyonda...")
    
    def show_find_dialog(self):
        """Sayfada bul dialog'unu göster"""
        # TODO: Find dialog implementasyonu
        QMessageBox.information(self, "Sayfada Bul", "Sayfada bul özelliği henüz implementasyonda...")
    
    def show_settings(self):
        """Ayarlar dialog'unu göster"""
        from .settings import BrowserSettingsDialog
        dialog = BrowserSettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_theme()
    
    def show_about(self):
        """Hakkında dialog'unu göster"""
        QMessageBox.about(self, "Cloud Browser Hakkında", 
            """<h3>Cloud Browser v2.0.0</h3>
            <p>PyCloud OS için modern web tarayıcısı</p>
            <p><b>Özellikler:</b></p>
            <ul>
            <li>Sekmeli gezinti</li>
            <li>PDF desteği</li>
            <li>Yer imi yönetimi</li>
            <li>Modern UI</li>
            <li>Klavye kısayolları</li>
            </ul>
            <p><b>Geliştirici:</b> PyCloud OS Team</p>
            <p><b>Lisans:</b> MIT</p>""")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.save_settings()
        self.logger.info("CloudBrowser closing...")
        event.accept() 