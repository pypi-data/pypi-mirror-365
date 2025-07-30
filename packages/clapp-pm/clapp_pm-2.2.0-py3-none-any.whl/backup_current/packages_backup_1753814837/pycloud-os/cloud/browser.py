"""
Cloud Browser - PyCloud OS Web Tarayıcısı
WebEngine tabanlı modern sekmeli tarayıcı, PDF desteği ve yer imi yönetimi
"""

import sys
import os
import json
import logging
import argparse
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin

# PyQt6 import with fallback
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWebEngineWidgets import *
    from PyQt6.QtWebEngineCore import *
    PYQT_AVAILABLE = True
    WEBENGINE_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
        PYQT_AVAILABLE = True
        WEBENGINE_AVAILABLE = False
        print("PyQt6 WebEngine bulunamadı - Basit tarayıcı modu")
    except ImportError:
        PYQT_AVAILABLE = False
        WEBENGINE_AVAILABLE = False
        print("PyQt6 bulunamadı - Browser text modunda çalışacak")

class BrowserTab:
    """Tarayıcı sekmesi"""
    
    def __init__(self, title: str = "Yeni Sekme", url: str = "about:blank"):
        self.title = title
        self.url = url
        self.history: List[str] = []
        self.history_index = -1
        self.is_loading = False
        self.favicon = None
        self.created_at = datetime.now()
        
    def add_to_history(self, url: str):
        """Geçmişe URL ekle"""
        if url and url != "about:blank":
            # Mevcut pozisyondan sonrasını sil
            self.history = self.history[:self.history_index + 1]
            # Yeni URL'yi ekle
            self.history.append(url)
            self.history_index = len(self.history) - 1
    
    def can_go_back(self) -> bool:
        """Geri gidebilir mi?"""
        return self.history_index > 0
    
    def can_go_forward(self) -> bool:
        """İleri gidebilir mi?"""
        return self.history_index < len(self.history) - 1
    
    def go_back(self) -> Optional[str]:
        """Geri git"""
        if self.can_go_back():
            self.history_index -= 1
            return self.history[self.history_index]
        return None
    
    def go_forward(self) -> Optional[str]:
        """İleri git"""
        if self.can_go_forward():
            self.history_index += 1
            return self.history[self.history_index]
        return None

class BookmarkManager:
    """Yer imi yöneticisi"""
    
    def __init__(self):
        self.bookmarks: List[Dict[str, Any]] = []
        self.bookmarks_file = "system/browser_bookmarks.json"
        self.load_bookmarks()
    
    def load_bookmarks(self):
        """Yer imlerini yükle"""
        try:
            if os.path.exists(self.bookmarks_file):
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    self.bookmarks = json.load(f)
        except Exception as e:
            print(f"Yer imi yükleme hatası: {e}")
            self.bookmarks = []
    
    def save_bookmarks(self):
        """Yer imlerini kaydet"""
        try:
            os.makedirs(os.path.dirname(self.bookmarks_file), exist_ok=True)
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Yer imi kaydetme hatası: {e}")
    
    def add_bookmark(self, title: str, url: str, folder: str = "Genel"):
        """Yer imi ekle"""
        bookmark = {
            "title": title,
            "url": url,
            "folder": folder,
            "created": datetime.now().isoformat(),
            "visits": 0
        }
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
    
    def remove_bookmark(self, url: str):
        """Yer imi sil"""
        self.bookmarks = [b for b in self.bookmarks if b["url"] != url]
        self.save_bookmarks()
    
    def get_bookmarks(self, folder: Optional[str] = None) -> List[Dict[str, Any]]:
        """Yer imlerini al"""
        if folder:
            return [b for b in self.bookmarks if b.get("folder") == folder]
        return self.bookmarks
    
    def is_bookmarked(self, url: str) -> bool:
        """URL yer imi var mı?"""
        return any(b["url"] == url for b in self.bookmarks)

if PYQT_AVAILABLE and WEBENGINE_AVAILABLE:
    class BrowserWindow(QMainWindow):
        """Ana tarayıcı penceresi"""
        
        def __init__(self, kernel=None):
            super().__init__()
            self.kernel = kernel
            self.tabs: Dict[int, BrowserTab] = {}
            self.current_tab_index = -1
            self.bookmark_manager = BookmarkManager()
            
            self.init_ui()
            self.apply_theme()
            self.new_tab("https://www.google.com")
        
        def init_ui(self):
            """UI'yı başlat"""
            self.setWindowTitle("PyCloud Browser")
            self.setGeometry(100, 100, 1200, 800)
            
            # Ana widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout()
            
            # Navigasyon araç çubuğu
            nav_toolbar = self.create_navigation_toolbar()
            layout.addWidget(nav_toolbar)
            
            # Tab widget
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.tabCloseRequested.connect(self.close_tab)
            self.tab_widget.currentChanged.connect(self.tab_changed)
            layout.addWidget(self.tab_widget)
            
            # Durum çubuğu
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Hazır")
            
            central_widget.setLayout(layout)
            
            # Menü çubuğu
            self.create_menu_bar()
            
            # Kısayollar
            self.setup_shortcuts()
        
        def create_menu_bar(self):
            """Menü çubuğu oluştur"""
            menubar = self.menuBar()
            
            # Dosya menüsü
            file_menu = menubar.addMenu('Dosya')
            
            new_tab_action = QAction('Yeni Sekme', self)
            new_tab_action.setShortcut('Ctrl+T')
            new_tab_action.triggered.connect(lambda: self.new_tab())
            file_menu.addAction(new_tab_action)
            
            new_window_action = QAction('Yeni Pencere', self)
            new_window_action.setShortcut('Ctrl+N')
            new_window_action.triggered.connect(self.new_window)
            file_menu.addAction(new_window_action)
            
            file_menu.addSeparator()
            
            close_tab_action = QAction('Sekmeyi Kapat', self)
            close_tab_action.setShortcut('Ctrl+W')
            close_tab_action.triggered.connect(self.close_current_tab)
            file_menu.addAction(close_tab_action)
            
            exit_action = QAction('Çıkış', self)
            exit_action.setShortcut('Ctrl+Q')
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Yer imleri menüsü
            bookmark_menu = menubar.addMenu('Yer İmleri')
            
            add_bookmark_action = QAction('Bu Sayfayı Yer İmine Ekle', self)
            add_bookmark_action.setShortcut('Ctrl+D')
            add_bookmark_action.triggered.connect(self.add_current_bookmark)
            bookmark_menu.addAction(add_bookmark_action)
            
            manage_bookmarks_action = QAction('Yer İmlerini Yönet', self)
            manage_bookmarks_action.triggered.connect(self.manage_bookmarks)
            bookmark_menu.addAction(manage_bookmarks_action)
            
            bookmark_menu.addSeparator()
            
            # Yer imi listesi
            self.update_bookmark_menu()
            
            # Görünüm menüsü
            view_menu = menubar.addMenu('Görünüm')
            
            reload_action = QAction('Yenile', self)
            reload_action.setShortcut('F5')
            reload_action.triggered.connect(self.reload_page)
            view_menu.addAction(reload_action)
            
            fullscreen_action = QAction('Tam Ekran', self)
            fullscreen_action.setShortcut('F11')
            fullscreen_action.triggered.connect(self.toggle_fullscreen)
            view_menu.addAction(fullscreen_action)
        
        def create_navigation_toolbar(self):
            """Navigasyon araç çubuğu oluştur"""
            toolbar = QToolBar()
            toolbar.setMovable(False)
            
            # Geri buton
            self.back_btn = QPushButton("◀")
            self.back_btn.setToolTip("Geri")
            self.back_btn.clicked.connect(self.go_back)
            self.back_btn.setEnabled(False)
            toolbar.addWidget(self.back_btn)
            
            # İleri buton
            self.forward_btn = QPushButton("▶")
            self.forward_btn.setToolTip("İleri")
            self.forward_btn.clicked.connect(self.go_forward)
            self.forward_btn.setEnabled(False)
            toolbar.addWidget(self.forward_btn)
            
            # Yenile buton
            self.reload_btn = QPushButton("🔄")
            self.reload_btn.setToolTip("Yenile")
            self.reload_btn.clicked.connect(self.reload_page)
            toolbar.addWidget(self.reload_btn)
            
            # Ana sayfa
            home_btn = QPushButton("🏠")
            home_btn.setToolTip("Ana Sayfa")
            home_btn.clicked.connect(self.go_home)
            toolbar.addWidget(home_btn)
            
            # Adres çubuğu
            self.address_bar = QLineEdit()
            self.address_bar.setPlaceholderText("Bir URL girin veya arama yapın...")
            self.address_bar.returnPressed.connect(self.navigate_to_url)
            toolbar.addWidget(self.address_bar)
            
            # Yer imi butonu
            self.bookmark_btn = QPushButton("⭐")
            self.bookmark_btn.setToolTip("Yer İmine Ekle")
            self.bookmark_btn.clicked.connect(self.toggle_bookmark)
            toolbar.addWidget(self.bookmark_btn)
            
            # Yeni sekme
            new_tab_btn = QPushButton("➕")
            new_tab_btn.setToolTip("Yeni Sekme")
            new_tab_btn.clicked.connect(lambda: self.new_tab())
            toolbar.addWidget(new_tab_btn)
            
            return toolbar
        
        def setup_shortcuts(self):
            """Kısayolları ayarla"""
            # Tab gezinme
            next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
            next_tab_shortcut.activated.connect(self.next_tab)
            
            prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
            prev_tab_shortcut.activated.connect(self.prev_tab)
            
            # Yeniden aç
            reopen_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
            reopen_shortcut.activated.connect(self.reopen_closed_tab)
        
        def apply_theme(self):
            """Tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QToolBar {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    spacing: 3px;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
                QPushButton:disabled {
                    background-color: #f5f5f5;
                    color: #999999;
                }
                QLineEdit {
                    border: 1px solid #cccccc;
                    padding: 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 2px solid #0078d4;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f5f5f5;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                }
                QStatusBar {
                    background-color: #f5f5f5;
                    border-top: 1px solid #cccccc;
                }
            """)
        
        def new_tab(self, url: str = "about:blank"):
            """Yeni sekme oluştur"""
            # Tab bilgisi oluştur
            tab_info = BrowserTab("Yeni Sekme", url)
            
            # Web view oluştur
            web_view = QWebEngineView()
            
            # Sayfa yüklenme olayları
            web_view.titleChanged.connect(lambda title: self.update_tab_title(web_view, title))
            web_view.urlChanged.connect(lambda qurl: self.update_tab_url(web_view, qurl))
            web_view.loadStarted.connect(lambda: self.page_load_started(web_view))
            web_view.loadFinished.connect(lambda: self.page_load_finished(web_view))
            
            # Tab ekle
            if url == "about:blank":
                title = "Yeni Sekme"
            else:
                title = "Yükleniyor..."
                
            index = self.tab_widget.addTab(web_view, title)
            self.tabs[index] = tab_info
            self.tab_widget.setCurrentIndex(index)
            
            # URL'ye git
            if url != "about:blank":
                web_view.setUrl(QUrl(url))
            
            return index
        
        def close_tab(self, index: int):
            """Sekme kapat"""
            if self.tab_widget.count() <= 1:
                # Son sekme kapatılırsa yeni bir tane oluştur
                self.new_tab()
            
            # Tab bilgisini sil
            if index in self.tabs:
                del self.tabs[index]
            
            # Tab'ı kapat
            self.tab_widget.removeTab(index)
            
            # Index'leri yeniden düzenle
            new_tabs = {}
            for i, tab_index in enumerate(sorted(self.tabs.keys())):
                if tab_index > index:
                    new_tabs[tab_index - 1] = self.tabs[tab_index]
                else:
                    new_tabs[tab_index] = self.tabs[tab_index]
            self.tabs = new_tabs
        
        def close_current_tab(self):
            """Mevcut sekmeyi kapat"""
            current_index = self.tab_widget.currentIndex()
            if current_index != -1:
                self.close_tab(current_index)
        
        def tab_changed(self, index: int):
            """Sekme değişti"""
            self.current_tab_index = index
            if index != -1 and index in self.tabs:
                tab_info = self.tabs[index]
                web_view = self.tab_widget.widget(index)
                
                if isinstance(web_view, QWebEngineView):
                    current_url = web_view.url().toString()
                    self.address_bar.setText(current_url)
                    
                    # Navigasyon butonları
                    self.back_btn.setEnabled(web_view.history().canGoBack())
                    self.forward_btn.setEnabled(web_view.history().canGoForward())
                    
                    # Yer imi durumu
                    self.update_bookmark_button(current_url)
        
        def navigate_to_url(self):
            """Adres çubuğundaki URL'ye git"""
            url_text = self.address_bar.text().strip()
            if not url_text:
                return
            
            # URL formatını düzelt
            if not url_text.startswith(('http://', 'https://', 'file://')):
                if '.' in url_text and ' ' not in url_text:
                    url_text = 'https://' + url_text
                else:
                    # Arama yap
                    url_text = f'https://www.google.com/search?q={url_text}'
            
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                current_widget.setUrl(QUrl(url_text))
        
        def go_back(self):
            """Geri git"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                current_widget.back()
        
        def go_forward(self):
            """İleri git"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                current_widget.forward()
        
        def reload_page(self):
            """Sayfayı yenile"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                current_widget.reload()
        
        def go_home(self):
            """Ana sayfaya git"""
            home_url = "https://www.google.com"
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                current_widget.setUrl(QUrl(home_url))
        
        def update_tab_title(self, web_view, title):
            """Sekme başlığını güncelle"""
            for index in range(self.tab_widget.count()):
                if self.tab_widget.widget(index) == web_view:
                    self.tab_widget.setTabText(index, title[:30] + "..." if len(title) > 30 else title)
                    if index in self.tabs:
                        self.tabs[index].title = title
                    break
        
        def update_tab_url(self, web_view, qurl):
            """Sekme URL'sini güncelle"""
            url = qurl.toString()
            for index in range(self.tab_widget.count()):
                if self.tab_widget.widget(index) == web_view:
                    if index in self.tabs:
                        self.tabs[index].url = url
                        self.tabs[index].add_to_history(url)
                    
                    # Adres çubuğunu güncelle (sadece aktif sekme için)
                    if index == self.tab_widget.currentIndex():
                        self.address_bar.setText(url)
                        self.update_bookmark_button(url)
                    break
        
        def page_load_started(self, web_view):
            """Sayfa yüklenmeye başladı"""
            for index in range(self.tab_widget.count()):
                if self.tab_widget.widget(index) == web_view:
                    if index in self.tabs:
                        self.tabs[index].is_loading = True
                    break
            
            self.status_bar.showMessage("Yükleniyor...")
        
        def page_load_finished(self, web_view):
            """Sayfa yüklenme bitti"""
            for index in range(self.tab_widget.count()):
                if self.tab_widget.widget(index) == web_view:
                    if index in self.tabs:
                        self.tabs[index].is_loading = False
                    break
            
            self.status_bar.showMessage("Hazır")
            
            # Navigasyon butonlarını güncelle
            if web_view == self.tab_widget.currentWidget():
                self.back_btn.setEnabled(web_view.history().canGoBack())
                self.forward_btn.setEnabled(web_view.history().canGoForward())
        
        def add_current_bookmark(self):
            """Mevcut sayfayı yer imine ekle"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                url = current_widget.url().toString()
                title = current_widget.title() or "Başlıksız"
                
                if not self.bookmark_manager.is_bookmarked(url):
                    self.bookmark_manager.add_bookmark(title, url)
                    self.update_bookmark_button(url)
                    self.update_bookmark_menu()
                    self.status_bar.showMessage("Yer imine eklendi", 2000)
        
        def toggle_bookmark(self):
            """Yer imi ekle/çıkar"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                url = current_widget.url().toString()
                
                if self.bookmark_manager.is_bookmarked(url):
                    self.bookmark_manager.remove_bookmark(url)
                    self.status_bar.showMessage("Yer iminden çıkarıldı", 2000)
                else:
                    title = current_widget.title() or "Başlıksız"
                    self.bookmark_manager.add_bookmark(title, url)
                    self.status_bar.showMessage("Yer imine eklendi", 2000)
                
                self.update_bookmark_button(url)
                self.update_bookmark_menu()
        
        def update_bookmark_button(self, url: str):
            """Yer imi butonunu güncelle"""
            if self.bookmark_manager.is_bookmarked(url):
                self.bookmark_btn.setText("★")
                self.bookmark_btn.setToolTip("Yer İminden Çıkar")
            else:
                self.bookmark_btn.setText("⭐")
                self.bookmark_btn.setToolTip("Yer İmine Ekle")
        
        def update_bookmark_menu(self):
            """Yer imi menüsünü güncelle"""
            # Bu fonksiyon menü güncelleme için kullanılacak
            pass
        
        def manage_bookmarks(self):
            """Yer imi yönetim penceresi"""
            dialog = QDialog(self)
            dialog.setWindowTitle("Yer İmi Yöneticisi")
            dialog.setGeometry(200, 200, 600, 400)
            
            layout = QVBoxLayout()
            
            # Yer imi listesi
            bookmark_list = QListWidget()
            for bookmark in self.bookmark_manager.get_bookmarks():
                item = QListWidgetItem(f"{bookmark['title']} - {bookmark['url']}")
                item.setData(Qt.ItemDataRole.UserRole, bookmark['url'])
                bookmark_list.addItem(item)
            
            layout.addWidget(bookmark_list)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            open_btn = QPushButton("Aç")
            open_btn.clicked.connect(lambda: self.open_bookmark_from_dialog(bookmark_list, dialog))
            button_layout.addWidget(open_btn)
            
            delete_btn = QPushButton("Sil")
            delete_btn.clicked.connect(lambda: self.delete_bookmark_from_dialog(bookmark_list))
            button_layout.addWidget(delete_btn)
            
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            dialog.exec()
        
        def open_bookmark_from_dialog(self, bookmark_list, dialog):
            """Dialog'dan yer imi aç"""
            current_item = bookmark_list.currentItem()
            if current_item:
                url = current_item.data(Qt.ItemDataRole.UserRole)
                self.new_tab(url)
                dialog.close()
        
        def delete_bookmark_from_dialog(self, bookmark_list):
            """Dialog'dan yer imi sil"""
            current_item = bookmark_list.currentItem()
            if current_item:
                url = current_item.data(Qt.ItemDataRole.UserRole)
                self.bookmark_manager.remove_bookmark(url)
                bookmark_list.takeItem(bookmark_list.row(current_item))
        
        def next_tab(self):
            """Sonraki sekme"""
            current = self.tab_widget.currentIndex()
            count = self.tab_widget.count()
            next_index = (current + 1) % count
            self.tab_widget.setCurrentIndex(next_index)
        
        def prev_tab(self):
            """Önceki sekme"""
            current = self.tab_widget.currentIndex()
            count = self.tab_widget.count()
            prev_index = (current - 1) % count
            self.tab_widget.setCurrentIndex(prev_index)
        
        def reopen_closed_tab(self):
            """Kapatılmış sekmeyi yeniden aç"""
            # Basit implementasyon - geliştirilecek
            self.new_tab("https://www.google.com")
        
        def new_window(self):
            """Yeni pencere aç"""
            new_browser = BrowserWindow(self.kernel)
            new_browser.show()
        
        def toggle_fullscreen(self):
            """Tam ekran değiştir"""
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

elif PYQT_AVAILABLE and not WEBENGINE_AVAILABLE:
    class SimpleBrowserWindow(QMainWindow):
        """Basit tarayıcı penceresi (WebEngine olmadan)"""
        
        def __init__(self, kernel=None):
            super().__init__()
            self.kernel = kernel
            self.bookmark_manager = BookmarkManager()
            
            self.init_ui()
        
        def init_ui(self):
            """UI'yı başlat"""
            self.setWindowTitle("PyCloud Browser (Basit Mod)")
            self.setGeometry(100, 100, 800, 600)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout()
            
            # Adres çubuğu
            address_layout = QHBoxLayout()
            self.address_bar = QLineEdit()
            self.address_bar.setPlaceholderText("Dosya yolu girin (file:// veya http://)")
            self.address_bar.returnPressed.connect(self.load_content)
            
            load_btn = QPushButton("Git")
            load_btn.clicked.connect(self.load_content)
            
            address_layout.addWidget(self.address_bar)
            address_layout.addWidget(load_btn)
            layout.addLayout(address_layout)
            
            # İçerik alanı
            self.content_area = QTextEdit()
            self.content_area.setReadOnly(True)
            layout.addWidget(self.content_area)
            
            central_widget.setLayout(layout)
            
            # Başlangıç mesajı
            self.content_area.setText("""
PyCloud Browser - Basit Mod

WebEngine mevcut olmadığı için basit metin görüntüleme modu aktif.

Desteklenen özellikler:
- Yerel HTML dosyalarını görüntüleme (file://)
- Metin dosyalarını okuma
- Basit HTTP istekleri

Örnek kullanım:
- file:///Users/kullanici/dosya.html
- file:///home/kullanici/dosya.txt
- http://example.com (basit içerik)
            """)
        
        def load_content(self):
            """İçerik yükle"""
            url = self.address_bar.text().strip()
            if not url:
                return
            
            try:
                if url.startswith('file://'):
                    # Yerel dosya
                    file_path = url[7:]  # file:// kısmını çıkar
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if file_path.endswith('.html'):
                        # HTML dosyası olarak göster
                        self.content_area.setHtml(content)
                    else:
                        # Düz metin olarak göster
                        self.content_area.setPlainText(content)
                
                elif url.startswith(('http://', 'https://')):
                    # Basit HTTP isteği
                    import urllib.request
                    with urllib.request.urlopen(url) as response:
                        content = response.read().decode('utf-8')
                    self.content_area.setPlainText(content[:5000] + "..." if len(content) > 5000 else content)
                
                else:
                    self.content_area.setPlainText("Desteklenmeyen URL formatı")
                    
            except Exception as e:
                self.content_area.setPlainText(f"Hata: {e}")

# Text-mode Browser (PyQt6 yoksa)
class TextBrowser:
    """Text-mode browser"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.bookmark_manager = BookmarkManager()
    
    def run(self):
        """Browser'ı çalıştır"""
        print("PyCloud Browser v1.0 (Text Mode)")
        print("Komutlar: go <url>, bookmarks, add <title> <url>, quit")
        print()
        
        while True:
            try:
                command = input("browser> ").strip()
                if not command:
                    continue
                
                if not self.handle_command(command):
                    break
                    
            except KeyboardInterrupt:
                print("\nBrowser kapatılıyor...")
                break
            except EOFError:
                break
    
    def handle_command(self, command: str) -> bool:
        """Komut işle"""
        parts = command.split(maxsplit=1)
        if not parts:
            return True
        
        cmd = parts[0].lower()
        
        if cmd == 'quit' or cmd == 'exit':
            return False
        
        elif cmd == 'go':
            if len(parts) > 1:
                self.visit_url(parts[1])
            else:
                print("Kullanım: go <url>")
        
        elif cmd == 'bookmarks':
            self.show_bookmarks()
        
        elif cmd == 'add':
            if len(parts) > 1:
                bookmark_parts = parts[1].split(maxsplit=1)
                if len(bookmark_parts) >= 2:
                    title, url = bookmark_parts
                    self.bookmark_manager.add_bookmark(title, url)
                    print(f"Yer imi eklendi: {title}")
                else:
                    print("Kullanım: add <başlık> <url>")
            else:
                print("Kullanım: add <başlık> <url>")
        
        else:
            print(f"Bilinmeyen komut: {cmd}")
            print("Komutlar: go, bookmarks, add, quit")
        
        return True
    
    def visit_url(self, url: str):
        """URL'yi ziyaret et"""
        try:
            if url.startswith('file://'):
                file_path = url[7:]
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"\n=== {file_path} ===")
                print(content[:500] + "..." if len(content) > 500 else content)
            
            elif url.startswith(('http://', 'https://')):
                import urllib.request
                with urllib.request.urlopen(url) as response:
                    content = response.read().decode('utf-8')
                print(f"\n=== {url} ===")
                print(content[:500] + "..." if len(content) > 500 else content)
            
            else:
                print("Desteklenmeyen URL formatı")
                
        except Exception as e:
            print(f"Hata: {e}")
    
    def show_bookmarks(self):
        """Yer imlerini göster"""
        bookmarks = self.bookmark_manager.get_bookmarks()
        if bookmarks:
            print("\nYer İmleri:")
            for i, bookmark in enumerate(bookmarks, 1):
                print(f"{i}. {bookmark['title']} - {bookmark['url']}")
        else:
            print("Yer imi yok")

# Ana fonksiyonlar
def create_browser_app(kernel=None):
    """Browser uygulaması oluştur"""
    if PYQT_AVAILABLE:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        if WEBENGINE_AVAILABLE:
            browser = BrowserWindow(kernel)
        else:
            browser = SimpleBrowserWindow(kernel)
        
        browser.show()
        return browser
    else:
        return TextBrowser(kernel)

def run_browser(kernel=None):
    """Browser'ı çalıştır"""
    if PYQT_AVAILABLE:
        # QApplication oluştur
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        if WEBENGINE_AVAILABLE:
            browser = BrowserWindow(kernel)
        else:
            browser = SimpleBrowserWindow(kernel)
        
        # ✅ ÇÖZÜM: Command line argumentlarını parse et
        import argparse
        parser = argparse.ArgumentParser(description='Cloud Browser')
        parser.add_argument('--open-file', dest='open_file', help='Açılacak dosya yolu')
        parser.add_argument('--url', dest='url', help='Açılacak URL')
        parser.add_argument('files', nargs='*', help='Açılacak dosyalar/URL\'ler')
        
        # sys.argv'yi parse et
        try:
            args, unknown = parser.parse_known_args()
            
            # Dosya açma parametresi varsa
            if args.open_file:
                file_path = Path(args.open_file).absolute()
                file_url = f"file://{file_path}"
                print(f"🚀 Browser dosya açıyor: {file_url}")
                if hasattr(browser, 'new_tab'):
                    browser.new_tab(file_url)
                else:
                    browser.address_bar.setText(file_url)
                    browser.load_content()
            
            # URL parametresi varsa
            elif args.url:
                print(f"🚀 Browser URL açıyor: {args.url}")
                if hasattr(browser, 'new_tab'):
                    browser.new_tab(args.url)
                else:
                    browser.address_bar.setText(args.url)
                    browser.load_content()
            
            # Doğrudan dosya/URL listesi varsa
            elif args.files:
                for item in args.files:
                    if Path(item).exists():
                        # Dosya ise file:// protokolü ekle
                        file_path = Path(item).absolute()
                        file_url = f"file://{file_path}"
                        print(f"🚀 Browser dosya açıyor: {file_url}")
                        if hasattr(browser, 'new_tab'):
                            browser.new_tab(file_url)
                        else:
                            browser.address_bar.setText(file_url)
                            browser.load_content()
                            break  # Basit mode'da sadece ilkini aç
                    elif item.startswith(('http://', 'https://', 'file://')):
                        # URL ise doğrudan aç
                        print(f"🚀 Browser URL açıyor: {item}")
                        if hasattr(browser, 'new_tab'):
                            browser.new_tab(item)
                        else:
                            browser.address_bar.setText(item)
                            browser.load_content()
                            break  # Basit mode'da sadece ilkini aç
                        
        except Exception as e:
            print(f"⚠️ Browser argument parsing error: {e}")
            # Argumentlar parse edilemezse normal başlat
        
        browser.show()
        return browser
    else:
        browser = TextBrowser(kernel)
        
        # Text mode için de dosya/URL açma desteği
        import argparse
        parser = argparse.ArgumentParser(description='Cloud Browser (Text Mode)')
        parser.add_argument('--open-file', dest='open_file', help='Açılacak dosya yolu')
        parser.add_argument('--url', dest='url', help='Açılacak URL')
        parser.add_argument('files', nargs='*', help='Açılacak dosyalar/URL\'ler')
        
        try:
            args, unknown = parser.parse_known_args()
            
            if args.open_file and Path(args.open_file).exists():
                file_path = Path(args.open_file).absolute()
                file_url = f"file://{file_path}"
                print(f"🚀 Browser (Text) dosya açıyor: {file_url}")
                browser.visit_url(file_url)
            elif args.url:
                print(f"🚀 Browser (Text) URL açıyor: {args.url}")
                browser.visit_url(args.url)
            elif args.files:
                for item in args.files:
                    if Path(item).exists():
                        file_path = Path(item).absolute()
                        file_url = f"file://{file_path}"
                        print(f"🚀 Browser (Text) dosya açıyor: {file_url}")
                        browser.visit_url(file_url)
                        break
                    elif item.startswith(('http://', 'https://', 'file://')):
                        print(f"🚀 Browser (Text) URL açıyor: {item}")
                        browser.visit_url(item)
                        break
        except Exception as e:
            print(f"⚠️ Browser (Text) argument parsing error: {e}")
        
        browser.run()
        return None

if __name__ == "__main__":
    run_browser() 