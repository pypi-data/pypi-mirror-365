"""
Cloud Browser UI Bileşenleri
Sekmeli arayüz, navigasyon toolbar ve status bar
"""

import os
from typing import Optional, List
from urllib.parse import urlparse

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWebEngineWidgets import *
    from PyQt6.QtWebEngineCore import *
    WEBENGINE_AVAILABLE = True
except ImportError as e:
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
        WEBENGINE_AVAILABLE = False
    except ImportError:
        raise ImportError("PyQt6 is required for Cloud Browser")

class BrowserTabWidget(QTabWidget):
    """
    Sekmeli tarayıcı widget'ı
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.tab_changed)
        
        # Tab bar styling
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                min-width: 120px;
                max-width: 200px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-color: #999999;
            }
            QTabBar::tab:hover {
                background-color: #e8e8e8;
            }
            QTabBar::close-button {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDRMNCA4TDEyIDEyIiBzdHJva2U9IiM2NjY2NjYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                subcontrol-position: right;
                subcontrol-origin: padding;
                width: 16px;
                height: 16px;
            }
            QTabBar::close-button:hover {
                background-color: #ff6b6b;
                border-radius: 8px;
            }
        """)
    
    def new_tab(self, url="about:blank"):
        """Yeni sekme oluştur"""
        if WEBENGINE_AVAILABLE:
            web_view = QWebEngineView()
            
            # URL yükle
            if url and url != "about:blank":
                web_view.setUrl(QUrl(url))
            else:
                web_view.setHtml(self.get_new_tab_page())
            
            # Signals bağla
            web_view.titleChanged.connect(lambda title: self.update_tab_title(web_view, title))
            web_view.urlChanged.connect(lambda qurl: self.update_tab_url(web_view, qurl))
            web_view.loadStarted.connect(lambda: self.load_started(web_view))
            web_view.loadFinished.connect(lambda: self.load_finished(web_view))
            
        else:
            # WebEngine yoksa basit text widget
            web_view = QTextEdit()
            web_view.setReadOnly(True)
            web_view.setHtml(f"""
                <h2>Cloud Browser - Basit Mod</h2>
                <p>WebEngine mevcut değil. Basit metin görüntüleme modu aktif.</p>
                <p>URL: {url}</p>
            """)
        
        # Sekme başlığı
        if url and url != "about:blank":
            domain = urlparse(url).netloc or "Yerel Dosya"
            title = domain
        else:
            title = "Yeni Sekme"
        
        # Sekmeyi ekle
        index = self.addTab(web_view, title)
        self.setCurrentIndex(index)
        
        # Tab icon
        self.setTabIcon(index, self.get_tab_icon(url))
        
        return web_view
    
    def close_tab(self, index):
        """Sekme kapat"""
        if self.count() <= 1:
            # Son sekme ise yeni boş sekme aç
            self.new_tab()
        
        # Kapatılan sekmenin URL'sini kaydet
        web_view = self.widget(index)
        if hasattr(web_view, 'url') and self.parent_browser:
            url = web_view.url().toString()
            if url and url != "about:blank":
                self.parent_browser.closed_tabs.append(url)
        
        # Sekmeyi kaldır
        self.removeTab(index)
    
    def tab_changed(self, index):
        """Sekme değiştiğinde"""
        if index >= 0 and self.parent_browser:
            web_view = self.widget(index)
            if hasattr(web_view, 'url'):
                url = web_view.url().toString()
                # Navigation toolbar'ı güncelle
                if self.parent_browser.navigation_toolbar:
                    self.parent_browser.navigation_toolbar.update_url(url)
                    self.parent_browser.navigation_toolbar.update_navigation_buttons(web_view)
    
    def update_tab_title(self, web_view, title):
        """Sekme başlığını güncelle"""
        index = self.indexOf(web_view)
        if index >= 0:
            # Başlığı kısalt
            if len(title) > 25:
                title = title[:22] + "..."
            self.setTabText(index, title)
    
    def update_tab_url(self, web_view, qurl):
        """Sekme URL'sini güncelle"""
        index = self.indexOf(web_view)
        if index >= 0:
            url = qurl.toString()
            # Tab icon'unu güncelle
            self.setTabIcon(index, self.get_tab_icon(url))
            
            # Navigation toolbar'ı güncelle
            if self.parent_browser and self.parent_browser.navigation_toolbar:
                self.parent_browser.navigation_toolbar.update_url(url)
    
    def load_started(self, web_view):
        """Yükleme başladığında"""
        index = self.indexOf(web_view)
        if index >= 0:
            # Loading icon
            self.setTabIcon(index, self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
            
            # Status bar güncelle
            if self.parent_browser and self.parent_browser.status_widget:
                self.parent_browser.status_widget.show_message("Yükleniyor...")
    
    def load_finished(self, web_view):
        """Yükleme bittiğinde"""
        index = self.indexOf(web_view)
        if index >= 0:
            # Normal icon
            url = web_view.url().toString() if hasattr(web_view, 'url') else ""
            self.setTabIcon(index, self.get_tab_icon(url))
            
            # Status bar güncelle
            if self.parent_browser and self.parent_browser.status_widget:
                self.parent_browser.status_widget.show_message("Hazır")
    
    def get_tab_icon(self, url):
        """URL'ye göre tab icon'u al"""
        if not url or url == "about:blank":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        
        if url.endswith('.pdf'):
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        elif url.startswith('file://'):
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        elif url.startswith('https://'):
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
        else:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
    
    def get_new_tab_page(self):
        """Yeni sekme sayfası HTML'i"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Yeni Sekme</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    padding: 40px;
                    text-align: center;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding-top: 100px;
                }
                h1 {
                    font-size: 3em;
                    margin-bottom: 20px;
                }
                .search-box {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    border-radius: 25px;
                    padding: 15px 25px;
                    font-size: 18px;
                    width: 60%;
                    color: white;
                    margin: 20px 0;
                }
                .search-box::placeholder {
                    color: rgba(255,255,255,0.7);
                }
                .shortcuts {
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-top: 40px;
                    flex-wrap: wrap;
                }
                .shortcut {
                    background: rgba(255,255,255,0.2);
                    border-radius: 15px;
                    padding: 20px;
                    text-decoration: none;
                    color: white;
                    transition: transform 0.2s;
                    min-width: 120px;
                }
                .shortcut:hover {
                    transform: translateY(-5px);
                    background: rgba(255,255,255,0.3);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 Cloud Browser</h1>
                <input type="text" class="search-box" placeholder="Arama yapın veya web adresi girin..." 
                       onkeypress="if(event.key==='Enter') window.location.href='https://www.google.com/search?q='+encodeURIComponent(this.value)">
                
                <div class="shortcuts">
                    <a href="https://www.google.com" class="shortcut">
                        <div class="shortcut-icon">🔍</div>
                        <div>Google</div>
                    </a>
                    <a href="https://www.youtube.com" class="shortcut">
                        <div class="shortcut-icon">📺</div>
                        <div>YouTube</div>
                    </a>
                    <a href="https://www.github.com" class="shortcut">
                        <div class="shortcut-icon">💻</div>
                        <div>GitHub</div>
                    </a>
                    <a href="https://www.wikipedia.org" class="shortcut">
                        <div class="shortcut-icon">📚</div>
                        <div>Wikipedia</div>
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def current_web_view(self):
        """Mevcut web view'ı al"""
        return self.currentWidget()
    
    def next_tab(self):
        """Sonraki sekmeye geç"""
        current = self.currentIndex()
        next_index = (current + 1) % self.count()
        self.setCurrentIndex(next_index)
    
    def prev_tab(self):
        """Önceki sekmeye geç"""
        current = self.currentIndex()
        prev_index = (current - 1) % self.count()
        self.setCurrentIndex(prev_index)

class NavigationToolbar(QToolBar):
    """
    Navigasyon araç çubuğu
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        
        self.setMovable(False)
        self.setFloatable(False)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        
        self.setup_toolbar()
        self.apply_style()
    
    def setup_toolbar(self):
        """Toolbar'ı kur"""
        # Geri butonu
        self.back_btn = QAction("⬅️", self)
        self.back_btn.setToolTip("Geri (Alt+Left)")
        self.back_btn.triggered.connect(self.go_back)
        self.addAction(self.back_btn)
        
        # İleri butonu
        self.forward_btn = QAction("➡️", self)
        self.forward_btn.setToolTip("İleri (Alt+Right)")
        self.forward_btn.triggered.connect(self.go_forward)
        self.addAction(self.forward_btn)
        
        # Yenile butonu
        self.reload_btn = QAction("🔄", self)
        self.reload_btn.setToolTip("Yenile (F5)")
        self.reload_btn.triggered.connect(self.reload_page)
        self.addAction(self.reload_btn)
        
        # Ana sayfa butonu
        self.home_btn = QAction("🏠", self)
        self.home_btn.setToolTip("Ana Sayfa")
        self.home_btn.triggered.connect(self.go_home)
        self.addAction(self.home_btn)
        
        # Separator
        self.addSeparator()
        
        # Adres çubuğu
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Arama yapın veya web adresi girin...")
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.address_bar.setMinimumWidth(400)
        self.addWidget(self.address_bar)
        
        # Separator
        self.addSeparator()
        
        # Yer imi butonu
        self.bookmark_btn = QAction("⭐", self)
        self.bookmark_btn.setToolTip("Yer İmi Ekle (Ctrl+D)")
        self.bookmark_btn.triggered.connect(self.toggle_bookmark)
        self.addAction(self.bookmark_btn)
        
        # Menü butonu
        self.menu_btn = QAction("☰", self)
        self.menu_btn.setToolTip("Menü")
        self.menu_btn.triggered.connect(self.show_menu)
        self.addAction(self.menu_btn)
    
    def apply_style(self):
        """Stil uygula"""
        self.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #dee2e6;
                padding: 8px;
                spacing: 4px;
            }
            QToolBar QAction {
                padding: 8px;
                margin: 2px;
                border-radius: 6px;
                font-size: 16px;
            }
            QToolBar QAction:hover {
                background-color: #e9ecef;
            }
            QLineEdit {
                border: 2px solid #dee2e6;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
        """)
    
    def update_url(self, url):
        """Adres çubuğunu güncelle"""
        self.address_bar.setText(url)
    
    def update_navigation_buttons(self, web_view):
        """Navigasyon butonlarını güncelle"""
        if hasattr(web_view, 'history'):
            history = web_view.history()
            self.back_btn.setEnabled(history.canGoBack())
            self.forward_btn.setEnabled(history.canGoForward())
        else:
            self.back_btn.setEnabled(False)
            self.forward_btn.setEnabled(False)
    
    def focus_address_bar(self):
        """Adres çubuğuna odaklan"""
        self.address_bar.setFocus()
        self.address_bar.selectAll()
    
    def navigate_to_url(self):
        """URL'ye git"""
        url = self.address_bar.text().strip()
        if not url:
            return
        
        # URL formatını düzelt
        if not url.startswith(('http://', 'https://', 'file://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                # Arama yap
                url = f'https://www.google.com/search?q={url}'
        
        # Mevcut sekmeye yükle
        if self.parent_browser:
            tab_widget = self.parent_browser.tab_widget
            if tab_widget is not None:
                current_web_view = tab_widget.current_web_view()
                if current_web_view and hasattr(current_web_view, 'setUrl'):
                    current_web_view.setUrl(QUrl(url))
    
    def go_back(self):
        """Geri git"""
        if self.parent_browser:
            self.parent_browser.go_back()
    
    def go_forward(self):
        """İleri git"""
        if self.parent_browser:
            self.parent_browser.go_forward()
    
    def reload_page(self):
        """Sayfayı yenile"""
        if self.parent_browser:
            self.parent_browser.reload_page()
    
    def go_home(self):
        """Ana sayfaya git"""
        if self.parent_browser and self.parent_browser.tab_widget:
            current_web_view = self.parent_browser.tab_widget.current_web_view()
            if current_web_view and hasattr(current_web_view, 'setUrl'):
                current_web_view.setUrl(QUrl("https://www.google.com"))
    
    def toggle_bookmark(self):
        """Yer imi ekle/çıkar"""
        if self.parent_browser:
            self.parent_browser.add_bookmark()
    
    def show_menu(self):
        """Menü göster"""
        if not self.parent_browser:
            return
            
        menu = QMenu(self)
        
        # Yeni sekme
        new_tab_action = menu.addAction("🆕 Yeni Sekme")
        new_tab_action.triggered.connect(lambda: self.parent_browser.new_tab())
        
        # Yeni pencere
        new_window_action = menu.addAction("🪟 Yeni Pencere")
        new_window_action.triggered.connect(self.parent_browser.new_window)
        
        menu.addSeparator()
        
        # Yer imi yöneticisi
        bookmarks_action = menu.addAction("📚 Yer İmleri")
        bookmarks_action.triggered.connect(self.parent_browser.show_bookmark_manager)
        
        # İndirme yöneticisi
        downloads_action = menu.addAction("📥 İndirmeler")
        downloads_action.triggered.connect(self.parent_browser.show_download_manager)
        
        menu.addSeparator()
        
        # Ayarlar
        settings_action = menu.addAction("⚙️ Ayarlar")
        settings_action.triggered.connect(self.parent_browser.show_settings)
        
        # Hakkında
        about_action = menu.addAction("ℹ️ Hakkında")
        about_action.triggered.connect(self.parent_browser.show_about)
        
        # Menüyü göster
        menu.exec(self.mapToGlobal(self.menu_btn.parent().pos()))

class StatusBarWidget(QStatusBar):
    """
    Durum çubuğu widget'ı
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        
        self.setup_statusbar()
        self.apply_style()
    
    def setup_statusbar(self):
        """Status bar'ı kur"""
        # Ana mesaj
        self.main_label = QLabel("Hazır")
        self.addWidget(self.main_label)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)
        
        # Zoom seviyesi
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.addPermanentWidget(self.zoom_label)
        
        # Güvenlik durumu
        self.security_label = QLabel("🔒")
        self.security_label.setToolTip("Güvenli bağlantı")
        self.addPermanentWidget(self.security_label)
    
    def apply_style(self):
        """Stil uygula"""
        self.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 4px 8px;
            }
            QLabel {
                color: #6c757d;
                font-size: 12px;
                padding: 2px 4px;
            }
        """)
    
    def show_message(self, message, timeout=0):
        """Mesaj göster"""
        self.main_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.main_label.setText("Hazır"))
    
    def update_zoom(self, zoom_factor):
        """Zoom seviyesini güncelle"""
        zoom_percent = int(zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percent}%")
    
    def update_security(self, is_secure):
        """Güvenlik durumunu güncelle"""
        if is_secure:
            self.security_label.setText("🔒")
            self.security_label.setToolTip("Güvenli bağlantı")
        else:
            self.security_label.setText("🔓")
            self.security_label.setToolTip("Güvenli olmayan bağlantı") 