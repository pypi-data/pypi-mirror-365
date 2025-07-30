"""
Cloud Notepad - PyCloud OS Modern Metin Düzenleyici
Basit, hafif ve kullanıcı dostu metin düzenleyici. Modern UI, dark mode, sekmeli yapı ve gelişmiş özellikler.
"""

import sys
import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import argparse

# PyQt6 import with fallback
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 bulunamadı - Notepad text modunda çalışacak")

class DocumentTab:
    """Doküman sekmesi - modernize edilmiş"""
    
    def __init__(self, title: str = "Yeni Doküman", file_path: Optional[str] = None):
        self.title = title
        self.file_path = file_path
        self.content = ""
        self.modified = False
        self.created_at = datetime.now()
        self.encoding = "utf-8"
        self.word_wrap = True
        self.line_numbers = False
        self.syntax_highlighting = False
        
    def set_content(self, content: str):
        """İçerik değiştir"""
        if self.content != content:
            self.content = content
            self.modified = True
    
    def mark_saved(self):
        """Kaydedildi olarak işaretle"""
        self.modified = False
    
    def get_display_title(self) -> str:
        """Görüntülenecek başlığı al"""
        title = self.title
        if self.modified:
            title += " *"
        return title

class ModernTextEdit(QTextEdit):
    """Modern metin düzenleyici widget'ı"""
    
    def __init__(self, dark_mode: bool = False):
        super().__init__()
        self.dark_mode = dark_mode
        self.setup_ui()
        
    def setup_ui(self):
        """UI kurulumu"""
        # Modern font
        font = QFont("JetBrains Mono", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Satır numaraları için margin
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        self.apply_theme()
    
    def apply_theme(self):
        """Tema uygula"""
        if self.dark_mode:
            self.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 8px;
                    padding: 12px;
                    selection-background-color: #264f78;
                    selection-color: #ffffff;
                }
                QScrollBar:vertical {
                    background-color: #2d2d2d;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: #555555;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #212529;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    selection-background-color: #b3d4fc;
                    selection-color: #000000;
                }
                QScrollBar:vertical {
                    background-color: #f5f5f5;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: #cccccc;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #999999;
                }
            """)
    
    def set_dark_mode(self, dark_mode: bool):
        """Dark mode ayarla"""
        self.dark_mode = dark_mode
        self.apply_theme()

if PYQT_AVAILABLE:
    class ModernNotepadWindow(QMainWindow):
        """Modern Notepad ana penceresi"""
        
        def __init__(self, kernel=None):
            super().__init__()
            self.kernel = kernel
            self.logger = logging.getLogger("CloudNotepad")
            self.logger.setLevel(logging.DEBUG)  # Debug loglarını aktif et
            self.tabs: Dict[int, DocumentTab] = {}
            self.current_tab_index = -1
            
            # Kernel debug
            if self.kernel:
                self.logger.info(f"✅ Kernel referansı alındı: {type(self.kernel)}")
                fs_module = self.kernel.get_module("fs")
                self.logger.info(f"FS modülü: {type(fs_module) if fs_module else 'None'}")
            else:
                self.logger.warning("⚠️ Kernel referansı None")
            
            # Tema sistemi
            self.is_dark_mode = self.detect_dark_mode()
            
            # Ayarlar
            self.settings_file = Path("users/default/.apps/cloud_notepad/settings.json")
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Varsayılan ayarlar
            self.settings = {
                "font_family": "JetBrains Mono",
                "font_size": 12,
                "word_wrap": True,
                "auto_save": True,
                "auto_save_interval": 30,  # saniye
                "recent_files": [],
                "max_recent_files": 10
            }
            
            self.load_settings()
            self.init_ui()
            self.apply_theme()
            self.new_document()
            
            # Auto-save timer
            if self.settings["auto_save"]:
                self.auto_save_timer = QTimer()
                self.auto_save_timer.timeout.connect(self.auto_save)
                self.auto_save_timer.start(self.settings["auto_save_interval"] * 1000)
            
            self.logger.info("Modern Cloud Notepad initialized")
        
        def detect_dark_mode(self) -> bool:
            """Dark mode algıla"""
            try:
                # PyCloud OS kernel'dan tema bilgisi al
                if self.kernel:
                    config = self.kernel.get_module("config")
                    if config:
                        theme_config = config.get("theme", {})
                        return theme_config.get("dark_mode", False)
                
                # Fallback - sistem temasını algıla
                palette = QApplication.palette()
                window_color = palette.color(QPalette.ColorRole.Window)
                return window_color.lightness() < 128
                
            except Exception:
                return False  # Varsayılan olarak açık tema
        
        def load_settings(self):
            """Ayarları yükle"""
            try:
                # PyCloud OS kullanıcı ayarları dizini
                settings_dir = Path("users") / "default" / ".apps" / "cloud_notepad"
                settings_dir.mkdir(parents=True, exist_ok=True)
                settings_file = settings_dir / "settings.json"
                
                if settings_file.exists():
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        saved_settings = json.load(f)
                        self.settings.update(saved_settings)
                        
                self.logger.info(f"Settings loaded from: {settings_file}")
            except Exception as e:
                self.logger.warning(f"Settings could not be loaded: {e}")
        
        def save_settings(self):
            """Ayarları kaydet"""
            try:
                # PyCloud OS kullanıcı ayarları dizini
                settings_dir = Path("users") / "default" / ".apps" / "cloud_notepad"
                settings_dir.mkdir(parents=True, exist_ok=True)
                settings_file = settings_dir / "settings.json"
                
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2, ensure_ascii=False)
                    
                self.logger.info(f"Settings saved to: {settings_file}")
            except Exception as e:
                self.logger.warning(f"Settings could not be saved: {e}")
        
        def init_ui(self):
            """Modern UI'yı başlat"""
            self.setWindowTitle("Cloud Notepad - Modern Metin Düzenleyici")
            self.setGeometry(200, 200, 1000, 700)
            self.setMinimumSize(600, 400)
            
            # Ana widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout()
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)
            
            # Modern araç çubuğu
            self.toolbar = self.create_modern_toolbar()
            layout.addWidget(self.toolbar)
            
            # Tab widget
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.setMovable(True)
            self.tab_widget.setDocumentMode(True)
            self.tab_widget.tabCloseRequested.connect(self.close_tab)
            self.tab_widget.currentChanged.connect(self.tab_changed)
            layout.addWidget(self.tab_widget)
            
            # Modern durum çubuğu
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            
            # Durum çubuğu widget'ları
            self.status_label = QLabel("Hazır")
            self.status_bar.addWidget(self.status_label)
            
            self.cursor_position_label = QLabel("Satır: 1, Sütun: 1")
            self.status_bar.addPermanentWidget(self.cursor_position_label)
            
            self.encoding_label = QLabel("UTF-8")
            self.status_bar.addPermanentWidget(self.encoding_label)
            
            self.word_count_label = QLabel("0 kelime")
            self.status_bar.addPermanentWidget(self.word_count_label)
            
            central_widget.setLayout(layout)
            
            # Modern menü çubuğu
            self.create_modern_menu_bar()
            
            # Kısayollar
            self.setup_shortcuts()
        
        def create_modern_menu_bar(self):
            """Modern menü çubuğu oluştur"""
            menubar = self.menuBar()
            
            # Dosya menüsü
            file_menu = menubar.addMenu('📄 Dosya')
            
            new_action = QAction('🆕 Yeni', self)
            new_action.setShortcut('Ctrl+N')
            new_action.triggered.connect(self.new_document)
            file_menu.addAction(new_action)
            
            open_action = QAction('📂 Aç', self)
            open_action.setShortcut('Ctrl+O')
            open_action.triggered.connect(self.open_file)
            file_menu.addAction(open_action)
            
            # Son açılan dosyalar
            recent_menu = file_menu.addMenu('🕒 Son Açılanlar')
            self.update_recent_files_menu(recent_menu)
            
            file_menu.addSeparator()
            
            save_action = QAction('💾 Kaydet', self)
            save_action.setShortcut('Ctrl+S')
            save_action.triggered.connect(self.save_file)
            file_menu.addAction(save_action)
            
            save_as_action = QAction('💾 Farklı Kaydet', self)
            save_as_action.setShortcut('Ctrl+Shift+S')
            save_as_action.triggered.connect(self.save_file_as)
            file_menu.addAction(save_as_action)
            
            save_all_action = QAction('💾 Tümünü Kaydet', self)
            save_all_action.setShortcut('Ctrl+Alt+S')
            save_all_action.triggered.connect(self.save_all_files)
            file_menu.addAction(save_all_action)
            
            file_menu.addSeparator()
            
            close_action = QAction('❌ Sekmeyi Kapat', self)
            close_action.setShortcut('Ctrl+W')
            close_action.triggered.connect(self.close_current_tab)
            file_menu.addAction(close_action)
            
            close_all_action = QAction('❌ Tümünü Kapat', self)
            close_all_action.setShortcut('Ctrl+Shift+W')
            close_all_action.triggered.connect(self.close_all_tabs)
            file_menu.addAction(close_all_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction('🚪 Çıkış', self)
            exit_action.setShortcut('Ctrl+Q')
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Düzen menüsü
            edit_menu = menubar.addMenu('✏️ Düzen')
            
            undo_action = QAction('↶ Geri Al', self)
            undo_action.setShortcut('Ctrl+Z')
            undo_action.triggered.connect(self.undo)
            edit_menu.addAction(undo_action)
            
            redo_action = QAction('↷ İleri Al', self)
            redo_action.setShortcut('Ctrl+Y')
            redo_action.triggered.connect(self.redo)
            edit_menu.addAction(redo_action)
            
            edit_menu.addSeparator()
            
            cut_action = QAction('✂️ Kes', self)
            cut_action.setShortcut('Ctrl+X')
            cut_action.triggered.connect(self.cut)
            edit_menu.addAction(cut_action)
            
            copy_action = QAction('📋 Kopyala', self)
            copy_action.setShortcut('Ctrl+C')
            copy_action.triggered.connect(self.copy)
            edit_menu.addAction(copy_action)
            
            paste_action = QAction('📄 Yapıştır', self)
            paste_action.setShortcut('Ctrl+V')
            paste_action.triggered.connect(self.paste)
            edit_menu.addAction(paste_action)
            
            edit_menu.addSeparator()
            
            select_all_action = QAction('🔘 Tümünü Seç', self)
            select_all_action.setShortcut('Ctrl+A')
            select_all_action.triggered.connect(self.select_all)
            edit_menu.addAction(select_all_action)
            
            edit_menu.addSeparator()
            
            find_action = QAction('🔍 Bul', self)
            find_action.setShortcut('Ctrl+F')
            find_action.triggered.connect(self.find_text)
            edit_menu.addAction(find_action)
            
            replace_action = QAction('🔄 Bul ve Değiştir', self)
            replace_action.setShortcut('Ctrl+H')
            replace_action.triggered.connect(self.find_replace)
            edit_menu.addAction(replace_action)
            
            # Görünüm menüsü
            view_menu = menubar.addMenu('👁️ Görünüm')
            
            font_action = QAction('🔤 Yazı Tipi', self)
            font_action.triggered.connect(self.change_font)
            view_menu.addAction(font_action)
            
            view_menu.addSeparator()
            
            word_wrap_action = QAction('📝 Kelime Kaydırma', self)
            word_wrap_action.setCheckable(True)
            word_wrap_action.setChecked(self.settings["word_wrap"])
            word_wrap_action.triggered.connect(self.toggle_word_wrap)
            view_menu.addAction(word_wrap_action)
            
            view_menu.addSeparator()
            
            theme_action = QAction('🌙 Tema Değiştir', self)
            theme_action.triggered.connect(self.toggle_theme)
            view_menu.addAction(theme_action)
            
            fullscreen_action = QAction('🖥️ Tam Ekran', self)
            fullscreen_action.setShortcut('F11')
            fullscreen_action.triggered.connect(self.toggle_fullscreen)
            view_menu.addAction(fullscreen_action)
            
            # Araçlar menüsü
            tools_menu = menubar.addMenu('🔧 Araçlar')
            
            settings_action = QAction('⚙️ Ayarlar', self)
            settings_action.triggered.connect(self.show_settings)
            tools_menu.addAction(settings_action)
            
            stats_action = QAction('📊 İstatistikler', self)
            stats_action.triggered.connect(self.show_statistics)
            tools_menu.addAction(stats_action)
        
        def create_modern_toolbar(self):
            """Modern araç çubuğu oluştur"""
            toolbar = QToolBar()
            toolbar.setMovable(False)
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            # Dosya işlemleri
            new_btn = QPushButton("🆕 Yeni")
            new_btn.setToolTip("Yeni doküman oluştur (Ctrl+N)")
            new_btn.clicked.connect(self.new_document)
            toolbar.addWidget(new_btn)
            
            open_btn = QPushButton("📂 Aç")
            open_btn.setToolTip("Dosya aç (Ctrl+O)")
            open_btn.clicked.connect(self.open_file)
            toolbar.addWidget(open_btn)
            
            save_btn = QPushButton("💾 Kaydet")
            save_btn.setToolTip("Kaydet (Ctrl+S)")
            save_btn.clicked.connect(self.save_file)
            toolbar.addWidget(save_btn)
            
            toolbar.addSeparator()
            
            # Düzenleme işlemleri
            undo_btn = QPushButton("↶")
            undo_btn.setToolTip("Geri al (Ctrl+Z)")
            undo_btn.clicked.connect(self.undo)
            toolbar.addWidget(undo_btn)
            
            redo_btn = QPushButton("↷")
            redo_btn.setToolTip("İleri al (Ctrl+Y)")
            redo_btn.clicked.connect(self.redo)
            toolbar.addWidget(redo_btn)
            
            toolbar.addSeparator()
            
            # Arama
            find_btn = QPushButton("🔍 Bul")
            find_btn.setToolTip("Metin ara (Ctrl+F)")
            find_btn.clicked.connect(self.find_text)
            toolbar.addWidget(find_btn)
            
            toolbar.addSeparator()
            
            # Font boyutu
            font_size_label = QLabel("Boyut:")
            toolbar.addWidget(font_size_label)
            
            self.font_size_combo = QComboBox()
            self.font_size_combo.addItems(["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "32"])
            self.font_size_combo.setCurrentText(str(self.settings["font_size"]))
            self.font_size_combo.currentTextChanged.connect(self.change_font_size)
            toolbar.addWidget(self.font_size_combo)
            
            toolbar.addSeparator()
            
            # Tema değiştirme
            theme_btn = QPushButton("🌙" if not self.is_dark_mode else "☀️")
            theme_btn.setToolTip("Tema değiştir")
            theme_btn.clicked.connect(self.toggle_theme)
            toolbar.addWidget(theme_btn)
            
            return toolbar
        
        def apply_theme(self):
            """Temayı uygula"""
            if self.is_dark_mode:
                self.apply_dark_theme()
            else:
                self.apply_light_theme()
            
            # Mevcut sekmelerdeki text edit'lerin temasını güncelle
            for i in range(self.tab_widget.count()):
                text_edit = self.tab_widget.widget(i)
                if isinstance(text_edit, ModernTextEdit):
                    text_edit.set_dark_mode(self.is_dark_mode)
        
        def apply_light_theme(self):
            """Açık tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                    color: #212529;
                }
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                }
                QTabBar::tab {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f5f5f5, stop:1 #e8e8e8);
                    border: 1px solid #d0d0d0;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    color: #212529;
                }
                QTabBar::tab:selected {
                    background: white;
                    border-bottom-color: white;
                }
                QTabBar::tab:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f0f0f0);
                }
                QToolBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f5f5f5);
                    border: none;
                    border-bottom: 1px solid #e0e0e0;
                    padding: 4px;
                    spacing: 8px;
                }
                QPushButton {
                    background-color: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 6px;
                    padding: 6px 12px;
                    color: #1565c0;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #bbdefb;
                }
                QPushButton:pressed {
                    background-color: #90caf9;
                }
                QComboBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 4px 8px;
                    background-color: white;
                }
                QStatusBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f5f5f5, stop:1 #e8e8e8);
                    border-top: 1px solid #e0e0e0;
                    color: #212529;
                }
                QMenuBar {
                    background-color: #f8f9fa;
                    color: #212529;
                }
                QMenuBar::item:selected {
                    background-color: #e3f2fd;
                }
                QMenu {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                QMenu::item:selected {
                    background-color: #e3f2fd;
                }
            """)
        
        def apply_dark_theme(self):
            """Koyu tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #404040;
                    border-radius: 8px;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #404040, stop:1 #353535);
                    border: 1px solid #555555;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    color: #ffffff;
                }
                QTabBar::tab:selected {
                    background: #2d2d2d;
                    border-bottom-color: #2d2d2d;
                }
                QTabBar::tab:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #505050, stop:1 #454545);
                }
                QToolBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #404040, stop:1 #353535);
                    border: none;
                    border-bottom: 1px solid #555555;
                    padding: 4px;
                    spacing: 8px;
                }
                QPushButton {
                    background-color: #1976d2;
                    border: 1px solid #2196f3;
                    border-radius: 6px;
                    padding: 6px 12px;
                    color: #ffffff;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0d47a1;
                }
                QComboBox {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px 8px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QStatusBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #353535, stop:1 #2d2d2d);
                    border-top: 1px solid #555555;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #1976d2;
                }
                QMenu {
                    background-color: #2d2d2d;
                    border: 1px solid #555555;
                    border-radius: 8px;
                    color: #ffffff;
                }
                QMenu::item:selected {
                    background-color: #1976d2;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        
        def new_document(self):
            """Yeni doküman oluştur"""
            doc = DocumentTab(f"Doküman {len(self.tabs) + 1}")
            
            # Metin editörü oluştur
            text_edit = ModernTextEdit(self.is_dark_mode)
            text_edit.textChanged.connect(lambda: self.text_changed(text_edit))
            
            # Tab ekle
            index = self.tab_widget.addTab(text_edit, doc.get_display_title())
            self.tabs[index] = doc
            self.tab_widget.setCurrentIndex(index)
            
            self.status_bar.showMessage("Yeni doküman oluşturuldu")
        
        def open_file(self):
            """Dosya aç - FilePicker ile"""
            try:
                # Önce PyCloud FilePicker'ı dene
                try:
                    from cloud.filepicker import open_file_dialog, FilePickerFilter
                    
                    # Metin dosyası filtreleri
                    filters = [
                        FilePickerFilter.TEXT_FILES,
                        FilePickerFilter.ALL_FILES
                    ]
                    
                    # FilePicker'ı göster
                    file_path = open_file_dialog(
                        app_id="cloud_notepad",
                        filters=filters,
                        parent=self,
                        kernel=self.kernel
                    )
                    
                    if file_path:
                        self.logger.info(f"📁 FilePicker'dan dosya seçildi: {file_path}")
                        self.open_specific_file(file_path)
                        return
                    
                except Exception as filepicker_error:
                    self.logger.warning(f"FilePicker kullanılamadı: {filepicker_error}")
                
                # Fallback - standart Qt file dialog
                self.logger.info("Fallback: Qt file dialog kullanılıyor")
                filters = "Metin Dosyaları (*.txt *.md *.py *.json *.log);;Tüm Dosyalar (*.*)"
                file_path, _ = QFileDialog.getOpenFileName(
                    self, 
                    "Dosya Aç", 
                    str(Path.home()),
                    filters
                )
                
                if file_path:
                    self.logger.info(f"📁 Qt dialog'dan dosya seçildi: {file_path}")
                    self.open_specific_file(file_path)
                
            except Exception as e:
                self.logger.error(f"Dosya açma hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {e}")
        
        def save_file(self):
            """Dosyayı kaydet"""
            current_index = self.tab_widget.currentIndex()
            if current_index == -1:
                return False
            
            doc = self.tabs[current_index]
            text_edit = self.tab_widget.widget(current_index)
            
            if doc.file_path is None:
                self.save_file_as()
                return False
            
            try:
                # PyCloud OS sanal dosya sistemi yolunu kullan
                save_path = Path(doc.file_path)
                
                # Dizini oluştur
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(text_edit.toPlainText())
                
                doc.mark_saved()
                self.tab_widget.setTabText(current_index, doc.get_display_title())
                self.status_bar.showMessage(f"Dosya kaydedildi: {doc.title}")
                
                return True
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi:\n{e}")
                return False
        
        def save_file_as(self):
            """Farklı kaydet - FilePicker ile"""
            current_index = self.tab_widget.currentIndex()
            if current_index == -1:
                return
            
            try:
                # Önce PyCloud FilePicker'ı dene
                try:
                    from cloud.filepicker import save_file_dialog, FilePickerFilter
                    
                    # Metin dosyası filtreleri
                    filters = [
                        FilePickerFilter.TEXT_FILES,
                        FilePickerFilter.ALL_FILES
                    ]
                    
                    # FilePicker'ı göster
                    file_path = save_file_dialog(
                        app_id="cloud_notepad",
                        filters=filters,
                        parent=self,
                        kernel=self.kernel
                    )
                    
                    if file_path:
                        self.logger.info(f"💾 FilePicker'dan kaydetme yolu seçildi: {file_path}")
                        
                        # Tab bilgilerini güncelle
                        tab_info = self.tab_widget.tabText(current_index)
                        if tab_info.endswith(" *"):
                            tab_info = tab_info[:-2]
                        
                        current_widget = self.tab_widget.currentWidget()
                        content = current_widget.toPlainText()
                        
                        # Dosyayı kaydet
                        success = self._save_content_to_file(file_path, content)
                        
                        if success:
                            # Tab bilgilerini güncelle
                            file_name = Path(file_path).name
                            self.tab_widget.setTabText(current_index, file_name)
                            self.tab_widget.setTabToolTip(current_index, file_path)
                            
                            # Tab metadata güncelle
                            if hasattr(current_widget, 'file_path'):
                                current_widget.file_path = file_path
                            
                            self.add_to_recent_files(file_path)
                            self.logger.info(f"✅ Dosya başarıyla kaydedildi: {file_path}")
                        
                        return
                    
                except Exception as filepicker_error:
                    self.logger.warning(f"FilePicker kullanılamadı: {filepicker_error}")
                
                # Fallback - standart Qt file dialog
                self.logger.info("Fallback: Qt save dialog kullanılıyor")
                filters = "Metin Dosyaları (*.txt);;Markdown (*.md);;Python (*.py);;JSON (*.json);;Tüm Dosyalar (*.*)"
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Farklı Kaydet", 
                    str(Path.home()),
                    filters
                )
                
                if file_path:
                    self.logger.info(f"💾 Qt dialog'dan kaydetme yolu seçildi: {file_path}")
                    
                    current_widget = self.tab_widget.currentWidget()
                    content = current_widget.toPlainText()
                    
                    success = self._save_content_to_file(file_path, content)
                    
                    if success:
                        # Tab bilgilerini güncelle
                        file_name = Path(file_path).name
                        self.tab_widget.setTabText(current_index, file_name)
                        self.tab_widget.setTabToolTip(current_index, file_path)
                        
                        if hasattr(current_widget, 'file_path'):
                            current_widget.file_path = file_path
                        
                        self.add_to_recent_files(file_path)
                        self.logger.info(f"✅ Dosya başarıyla kaydedildi: {file_path}")
                
            except Exception as e:
                self.logger.error(f"Dosya kaydetme hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {e}")
        
        def _save_content_to_file(self, file_path: str, content: str) -> bool:
            """İçeriği dosyaya kaydet"""
            try:
                # VFS kullanarak güvenli kaydetme
                if self.kernel:
                    bridge_manager = self.kernel.get_bridge_manager() if hasattr(self.kernel, 'get_bridge_manager') else None
                    if bridge_manager:
                        success, result = bridge_manager.call_module_method(
                            "cloud_notepad", "fs", "vfs_write_file", 
                            file_path, content, "cloud_notepad"
                        )
                        if success:
                            return True
                        else:
                            self.logger.warning(f"VFS yazma başarısız: {result}")
                
                # Fallback - direkt dosya sistemi
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
            except Exception as e:
                self.logger.error(f"Dosya kaydetme hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {e}")
                return False
        
        def text_changed(self, text_edit):
            """Metin değişti"""
            current_index = self.tab_widget.currentIndex()
            if current_index in self.tabs:
                doc = self.tabs[current_index]
                doc.set_content(text_edit.toPlainText())
                
                # Sekme başlığını güncelle
                self.tab_widget.setTabText(current_index, doc.get_display_title())
                
                # Durum çubuğunu güncelle
                self.update_status_bar(text_edit)
        
        def update_status_bar(self, text_edit):
            """Durum çubuğunu güncelle"""
            if isinstance(text_edit, ModernTextEdit):
                # Cursor pozisyonu
                cursor = text_edit.textCursor()
                line = cursor.blockNumber() + 1
                column = cursor.columnNumber() + 1
                self.cursor_position_label.setText(f"Satır: {line}, Sütun: {column}")
                
                # Kelime sayısı
                text = text_edit.toPlainText()
                word_count = len(text.split()) if text.strip() else 0
                char_count = len(text)
                self.word_count_label.setText(f"{word_count} kelime, {char_count} karakter")
        
        def close_tab(self, index: int):
            """Sekme kapat"""
            if index in self.tabs:
                doc = self.tabs[index]
                
                # Değişiklik varsa kaydetme sor
                if doc.modified:
                    reply = QMessageBox.question(
                        self, "Kaydet",
                        f"'{doc.title}' dosyasında değişiklikler var. Kaydetmek istiyor musunuz?",
                        QMessageBox.StandardButton.Save | 
                        QMessageBox.StandardButton.Discard | 
                        QMessageBox.StandardButton.Cancel
                    )
                    
                    if reply == QMessageBox.StandardButton.Save:
                        if not self.save_file():
                            return  # Kaydetme iptal edildi
                    elif reply == QMessageBox.StandardButton.Cancel:
                        return  # Kapatma iptal edildi
                
                # Sekmeyi kapat
                self.tab_widget.removeTab(index)
                del self.tabs[index]
                
                # Index'leri yeniden düzenle
                new_tabs = {}
                for i, (old_index, doc) in enumerate(self.tabs.items()):
                    if old_index > index:
                        new_tabs[old_index - 1] = doc
                    else:
                        new_tabs[old_index] = doc
                self.tabs = new_tabs
                
                # Hiç sekme kalmadıysa yeni doküman oluştur
                if self.tab_widget.count() == 0:
                    self.new_document()
        
        def close_current_tab(self):
            """Mevcut sekmeyi kapat"""
            current_index = self.tab_widget.currentIndex()
            if current_index >= 0:
                self.close_tab(current_index)
        
        def tab_changed(self, index: int):
            """Sekme değişti"""
            self.current_tab_index = index
            if index >= 0 and index in self.tabs:
                doc = self.tabs[index]
                self.status_label.setText(f"Açık: {doc.title}")
                
                # Text edit'i al ve durum çubuğunu güncelle
                text_edit = self.tab_widget.widget(index)
                if isinstance(text_edit, ModernTextEdit):
                    self.update_status_bar(text_edit)
        
        def next_tab(self):
            """Sonraki sekme"""
            current = self.tab_widget.currentIndex()
            count = self.tab_widget.count()
            if count > 1:
                next_index = (current + 1) % count
                self.tab_widget.setCurrentIndex(next_index)
        
        def prev_tab(self):
            """Önceki sekme"""
            current = self.tab_widget.currentIndex()
            count = self.tab_widget.count()
            if count > 1:
                prev_index = (current - 1) % count
                self.tab_widget.setCurrentIndex(prev_index)
        
        def select_all(self):
            """Tümünü seç"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                current_widget.selectAll()
        
        def find_replace(self):
            """Bul ve değiştir"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                # Basit bul ve değiştir dialog'u
                find_text, ok1 = QInputDialog.getText(self, "Bul ve Değiştir", "Aranacak metin:")
                if ok1 and find_text:
                    replace_text, ok2 = QInputDialog.getText(self, "Bul ve Değiştir", "Değiştirilecek metin:")
                    if ok2:
                        content = current_widget.toPlainText()
                        new_content = content.replace(find_text, replace_text)
                        current_widget.setPlainText(new_content)
                        
                        # Değişiklik sayısını göster
                        count = content.count(find_text)
                        if count > 0:
                            self.status_label.setText(f"{count} değişiklik yapıldı")
                        else:
                            self.status_label.setText("Değişiklik yapılmadı")
        
        def save_all_files(self):
            """Tüm dosyaları kaydet"""
            saved_count = 0
            for index, doc in self.tabs.items():
                if doc.modified:
                    # Mevcut sekmeyi geçici olarak değiştir
                    current_index = self.tab_widget.currentIndex()
                    self.tab_widget.setCurrentIndex(index)
                    
                    if self.save_file():
                        saved_count += 1
                    
                    # Orijinal sekmeye geri dön
                    self.tab_widget.setCurrentIndex(current_index)
            
            self.status_label.setText(f"{saved_count} dosya kaydedildi")
        
        def auto_save(self):
            """Otomatik kaydetme"""
            if self.settings["auto_save"]:
                current_index = self.tab_widget.currentIndex()
                if current_index in self.tabs:
                    doc = self.tabs[current_index]
                    if doc.modified and doc.file_path:
                        # Sadece dosya yolu olan ve değişiklik yapılan dosyaları otomatik kaydet
                        self.save_file()
                        self.status_label.setText("Otomatik kaydedildi")
        
        def update_recent_files_menu(self, menu):
            """Son açılan dosyalar menüsünü güncelle"""
            menu.clear()
            
            if not self.settings["recent_files"]:
                no_recent_action = QAction("Son açılan dosya yok", self)
                no_recent_action.setEnabled(False)
                menu.addAction(no_recent_action)
                return
            
            for file_path in self.settings["recent_files"][:self.settings["max_recent_files"]]:
                if Path(file_path).exists():
                    file_name = Path(file_path).name
                    action = QAction(f"📄 {file_name}", self)
                    action.setToolTip(file_path)
                    action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
                    menu.addAction(action)
            
            if self.settings["recent_files"]:
                menu.addSeparator()
                clear_action = QAction("🗑️ Listeyi Temizle", self)
                clear_action.triggered.connect(self.clear_recent_files)
                menu.addAction(clear_action)
        
        def open_recent_file(self, file_path: str):
            """Son açılan dosyayı aç"""
            self.open_specific_file(file_path)
        
        def clear_recent_files(self):
            """Son açılan dosyalar listesini temizle"""
            self.settings["recent_files"] = []
            self.save_settings()
        
        def add_to_recent_files(self, file_path: str):
            """Dosyayı son açılanlar listesine ekle"""
            if file_path in self.settings["recent_files"]:
                self.settings["recent_files"].remove(file_path)
            
            self.settings["recent_files"].insert(0, file_path)
            
            # Maksimum sayıyı aş
            if len(self.settings["recent_files"]) > self.settings["max_recent_files"]:
                self.settings["recent_files"] = self.settings["recent_files"][:self.settings["max_recent_files"]]
            
            self.save_settings()
        
        def toggle_theme(self):
            """Tema değiştir"""
            self.is_dark_mode = not self.is_dark_mode
            self.apply_theme()
            
            # Toolbar'daki tema butonunu güncelle
            for widget in self.toolbar.findChildren(QPushButton):
                if widget.toolTip() == "Tema değiştir":
                    widget.setText("🌙" if not self.is_dark_mode else "☀️")
                    break
            
            # Kernel'a tema değişikliğini bildir
            if self.kernel:
                config = self.kernel.get_module("config")
                if config:
                    config.set("theme.dark_mode", self.is_dark_mode)
            
            self.logger.info(f"Theme toggled to: {'dark' if self.is_dark_mode else 'light'}")
        
        def show_settings(self):
            """Ayarları göster"""
            # Bu işlev, geliştirilecek
            pass
        
        def show_statistics(self):
            """İstatistikleri göster"""
            # Bu işlev, geliştirilecek
            pass
        
        def closeEvent(self, event):
            """Pencere kapatılıyor"""
            # Tüm tab'lardaki değişiklikleri kontrol et
            modified_docs = []
            for index, doc in self.tabs.items():
                if doc.modified:
                    modified_docs.append(doc.title)
            
            if modified_docs:
                reply = QMessageBox.question(
                    self,
                    "Kaydetilmemiş Değişiklikler",
                    f"Aşağıdaki dosyalarda kaydedilmemiş değişiklikler var:\n\n" +
                    "\n".join(modified_docs) +
                    "\n\nYine de çıkmak istiyor musunuz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    event.ignore()
                    return
            
            event.accept()
        
        def open_specific_file(self, file_path: str):
            """Belirli bir dosyayı aç (komut satırından)"""
            try:
                # PyCloud OS FS API kullan
                content = None
                file_name = Path(file_path).name
                
                if self.kernel:
                    # FS API üzerinden dosya oku
                    fs = self.kernel.get_module("fs")
                    if fs:
                        try:
                            content = fs.read_file(file_path)
                            self.logger.info(f"✅ Dosya FS API ile okundu: {file_path}")
                            self.logger.debug(f"📄 Dosya içeriği: {repr(content[:100])}...")  # İlk 100 karakter
                        except Exception as e:
                            self.logger.warning(f"⚠️ FS API ile okuma başarısız: {e}")
                
                # Fallback - doğrudan dosya sistemi
                if content is None:
                    path = Path(file_path)
                    if not path.exists():
                        self.status_bar.showMessage(f"Dosya bulunamadı: {file_path}")
                        return
                    
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.logger.info(f"📁 Dosya fallback ile okundu: {file_path}")
                    self.logger.debug(f"📄 Fallback içeriği: {repr(content[:100])}...")
                
                # İçerik kontrolü
                if content is None:
                    self.logger.error(f"❌ Dosya içeriği None: {file_path}")
                    self.status_bar.showMessage(f"Dosya içeriği okunamadı: {file_path}")
                    return
                
                self.logger.info(f"📝 Text widget'a yazılacak içerik uzunluğu: {len(content)} karakter")
                
                # Eğer sadece bir tab var ve o da boş ise, onu değiştir
                should_replace_empty_tab = False
                if self.tab_widget.count() == 1:
                    current_widget = self.tab_widget.widget(0)
                    if current_widget and isinstance(current_widget, ModernTextEdit):
                        current_content = current_widget.toPlainText().strip()
                        current_doc = self.tabs.get(0)
                        if current_doc and current_doc.file_path is None and not current_content:
                            # Boş tab var, onu değiştir
                            should_replace_empty_tab = True
                            self.logger.info("🔄 Boş tab tespit edildi, dosya onun yerine açılacak")
                
                if should_replace_empty_tab:
                    # Mevcut boş tab'ı güncelle
                    current_widget = self.tab_widget.widget(0)
                    current_doc = self.tabs[0]
                    
                    # İçeriği ayarla - GÜÇLÜ REFRESH
                    current_widget.clear()  # Önce temizle
                    current_widget.setPlainText(content)  # Sonra yaz
                    
                    # Doküman bilgilerini güncelle
                    current_doc.title = file_name
                    current_doc.file_path = str(file_path)
                    current_doc.content = content
                    current_doc.modified = False
                    
                    # Tab başlığını güncelle
                    self.tab_widget.setTabText(0, current_doc.get_display_title())
                    
                    # Text widget'tan içeriği kontrol et
                    actual_content = current_widget.toPlainText()
                    self.logger.info(f"📋 Text widget'tan okunan içerik uzunluğu: {len(actual_content)} karakter")
                    
                    # GÜÇLÜ REFRESH İŞLEMLERİ
                    current_widget.update()
                    current_widget.repaint()
                    
                    # Cursor'ı başa al
                    cursor = current_widget.textCursor()
                    cursor.movePosition(cursor.MoveOperation.Start)
                    current_widget.setTextCursor(cursor)
                    
                    # Widget'ı yeniden focus et
                    current_widget.setFocus()
                    
                    # Delayed refresh - PyQt6 için gerekli
                    def delayed_refresh():
                        current_widget.update()
                        current_widget.repaint()
                        # Viewport'u da refresh et
                        if hasattr(current_widget, 'viewport'):
                            current_widget.viewport().update()
                        self.logger.info("🔄 Delayed refresh tamamlandı")
                    
                    QTimer.singleShot(100, delayed_refresh)  # 100ms sonra refresh
                    
                    self.logger.info(f"🎯 Boş tab güncellendi, toplam tab: {self.tab_widget.count()}")
                    self.logger.info(f"🎯 Aktif tab index: {self.tab_widget.currentIndex()}")
                    
                else:
                    # Yeni tab oluştur
                    doc = DocumentTab(file_name, str(file_path))
                    doc.content = content
                    
                    text_edit = ModernTextEdit(self.is_dark_mode)
                    text_edit.setPlainText(content)
                    text_edit.textChanged.connect(lambda: self.text_changed(text_edit))
                    
                    # Text widget'tan içeriği kontrol et
                    actual_content = text_edit.toPlainText()
                    self.logger.info(f"📋 Text widget'tan okunan içerik uzunluğu: {len(actual_content)} karakter")
                    
                    index = self.tab_widget.addTab(text_edit, doc.get_display_title())
                    self.tabs[index] = doc
                    self.tab_widget.setCurrentIndex(index)
                    
                    # Yeni tab için de refresh
                    text_edit.update()
                    text_edit.repaint()
                    text_edit.setFocus()
                    
                    self.logger.info(f"🎯 Yeni tab eklendi, index: {index}, toplam tab: {self.tab_widget.count()}")
                    self.logger.info(f"🎯 Aktif tab index: {self.tab_widget.currentIndex()}")
                
                self.status_bar.showMessage(f"Dosya açıldı: {file_name}")
                self.add_to_recent_files(file_path)
                
                # Widget'ı görünür olduğunu kontrol et
                current_widget = self.tab_widget.currentWidget()
                if current_widget and current_widget.isVisible():
                    self.logger.info("✅ Text widget görünür")
                    
                    # İçerik kontrolü
                    widget_content = current_widget.toPlainText()
                    if len(widget_content) > 0:
                        self.logger.info(f"✅ Widget'ta {len(widget_content)} karakter içerik var!")
                        self.logger.info(f"📄 İçerik önizlemesi: {repr(widget_content[:50])}...")
                    else:
                        self.logger.warning("⚠️ Widget'ta içerik yok!")
                        
                        # İçerik yoksa tekrar yüklemeyi dene
                        self.logger.info("🔄 İçerik yok, tekrar yükleme deneniyor...")
                        current_widget.clear()
                        current_widget.setPlainText(content)
                        current_widget.update()
                        current_widget.repaint()
                        
                        # Tekrar kontrol et
                        widget_content_retry = current_widget.toPlainText()
                        self.logger.info(f"🔄 Tekrar yükleme sonrası: {len(widget_content_retry)} karakter")
                        
                else:
                    self.logger.warning("⚠️ Text widget görünür değil")
                
                # Pencere durumunu kontrol et
                if self.isVisible():
                    self.logger.info("✅ Ana pencere görünür")
                else:
                    self.logger.warning("⚠️ Ana pencere görünür değil")
                
                # Final refresh
                if current_widget:
                    current_widget.update()
                    current_widget.repaint()
                    self.logger.info("🔄 Final widget refresh edildi")
                
                # Ana pencereyi de refresh et
                self.update()
                self.repaint()
                self.logger.info("🔄 Ana pencere refresh edildi")
                
            except Exception as e:
                self.logger.error(f"❌ Dosya açılamadı: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                self.status_bar.showMessage(f"Dosya açılamadı: {e}")
        
        def setup_shortcuts(self):
            """Kısayolları ayarla"""
            # Tab gezinme
            next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
            next_tab_shortcut.activated.connect(self.next_tab)
            
            prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
            prev_tab_shortcut.activated.connect(self.prev_tab)
            
            # Tam ekran
            fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
            fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
        def undo(self):
            """Geri al"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                current_widget.undo()
        
        def redo(self):
            """İleri al"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                current_widget.redo()
        
        def cut(self):
            """Kes"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                current_widget.cut()
        
        def copy(self):
            """Kopyala"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                current_widget.copy()
        
        def paste(self):
            """Yapıştır"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                current_widget.paste()
        
        def find_text(self):
            """Metin bul"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                text, ok = QInputDialog.getText(self, "Bul", "Aranacak metin:")
                if ok and text:
                    cursor = current_widget.textCursor()
                    found = current_widget.find(text)
                    if not found:
                        QMessageBox.information(self, "Bulunamadı", f"'{text}' metni bulunamadı.")
        
        def change_font(self):
            """Yazı tipi değiştir"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                font, ok = QFontDialog.getFont(current_widget.font(), self)
                if ok:
                    current_widget.setFont(font)
        
        def change_font_size(self, size_text: str):
            """Yazı boyutu değiştir"""
            try:
                size = int(size_text)
                current_widget = self.tab_widget.currentWidget()
                if isinstance(current_widget, ModernTextEdit):
                    font = current_widget.font()
                    font.setPointSize(size)
                    current_widget.setFont(font)
            except ValueError:
                pass
        
        def toggle_word_wrap(self):
            """Kelime kaydırma değiştir"""
            current_widget = self.tab_widget.currentWidget()
            if isinstance(current_widget, ModernTextEdit):
                current_widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth if current_widget.lineWrapMode() == QTextEdit.LineWrapMode.NoWrap else QTextEdit.LineWrapMode.NoWrap)
        
        def toggle_fullscreen(self):
            """Tam ekran değiştir"""
            self.showFullScreen() if self.isFullScreen() else self.showNormal()
        
        def close_all_tabs(self):
            """Tüm sekmeleri kapat"""
            while self.tab_widget.count() > 0:
                self.close_tab(0)

# Text-mode Notepad (PyQt6 yoksa)
class TextNotepad:
    """Text-mode notepad"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.content = ""
        self.file_path = None
        self.modified = False
    
    def run(self):
        """Notepad'i çalıştır"""
        print("PyCloud Notepad v1.0 (Text Mode)")
        print("Komutlar: :w (kaydet), :wq (kaydet ve çık), :q (çık), :o <dosya> (aç)")
        print("Metin girişi için satır satır yazın, komut için ':' ile başlayın.\n")
        
        while True:
            try:
                line = input("> ")
                
                if line.startswith(':'):
                    if not self.handle_command(line[1:]):
                        break
                else:
                    self.content += line + "\n"
                    self.modified = True
                    
            except KeyboardInterrupt:
                print("\nÇıkılıyor...")
                break
            except EOFError:
                break
    
    def handle_command(self, command: str) -> bool:
        """Komut işle"""
        parts = command.split()
        if not parts:
            return True
        
        cmd = parts[0]
        
        if cmd == 'q':
            if self.modified:
                confirm = input("Kaydedilmemiş değişiklikler var. Çıkmak istiyor musunuz? (y/n): ")
                if confirm.lower() != 'y':
                    return True
            return False
        
        elif cmd == 'w':
            if len(parts) > 1:
                self.file_path = parts[1]
            
            if self.file_path:
                try:
                    with open(self.file_path, 'w', encoding='utf-8') as f:
                        f.write(self.content)
                    print(f"Dosya kaydedildi: {self.file_path}")
                    self.modified = False
                except Exception as e:
                    print(f"Hata: {e}")
            else:
                print("Dosya yolu belirtilmedi")
        
        elif cmd == 'wq':
            if self.file_path:
                try:
                    with open(self.file_path, 'w', encoding='utf-8') as f:
                        f.write(self.content)
                    print(f"Dosya kaydedildi: {self.file_path}")
                    return False
                except Exception as e:
                    print(f"Hata: {e}")
            else:
                print("Dosya yolu belirtilmedi")
        
        elif cmd == 'o':
            if len(parts) > 1:
                try:
                    with open(parts[1], 'r', encoding='utf-8') as f:
                        self.content = f.read()
                    self.file_path = parts[1]
                    self.modified = False
                    print(f"Dosya yüklendi: {parts[1]}")
                    print(f"İçerik ({len(self.content)} karakter):")
                    print(self.content[:200] + "..." if len(self.content) > 200 else self.content)
                except Exception as e:
                    print(f"Hata: {e}")
            else:
                print("Dosya yolu belirtilmedi")
        
        elif cmd == 'help':
            print("Komutlar:")
            print("  :w [dosya]  - Kaydet")
            print("  :wq         - Kaydet ve çık")
            print("  :q          - Çık")
            print("  :o <dosya>  - Dosya aç")
            print("  :help       - Bu yardımı göster")
        
        else:
            print(f"Bilinmeyen komut: {cmd}")
            print("Yardım için ':help' yazın")
        
        return True

# Ana fonksiyonlar
def create_notepad_app(kernel=None):
    """Notepad uygulaması oluştur"""
    if not PYQT_AVAILABLE:
        print("PyQt6 mevcut değil - Text modu kullanılıyor")
        return TextNotepad(kernel)
    
    # QApplication kontrolü
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    notepad = ModernNotepadWindow(kernel)
    notepad.show()
    return notepad

def run_notepad(kernel=None):
    """Notepad'i çalıştır"""
    if not PYQT_AVAILABLE:
        notepad = TextNotepad(kernel)
        notepad.run()
        return
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    notepad = ModernNotepadWindow(kernel)
    
    # ✅ ÇÖZÜM: Command line argumentlarını parse et
    parser = argparse.ArgumentParser(description='Cloud Notepad')
    parser.add_argument('--open-file', dest='open_file', help='Açılacak dosya yolu')
    parser.add_argument('files', nargs='*', help='Açılacak dosyalar')
    
    # sys.argv'yi parse et
    try:
        args, unknown = parser.parse_known_args()
        
        # Dosya açma parametresi varsa
        if args.open_file:
            print(f"🚀 Notepad dosya açıyor: {args.open_file}")
            notepad.open_specific_file(args.open_file)
        
        # Doğrudan dosya listesi varsa
        elif args.files:
            for file_path in args.files:
                if Path(file_path).exists():
                    print(f"🚀 Notepad dosya açıyor: {file_path}")
                    notepad.open_specific_file(file_path)
                    
    except Exception as e:
        print(f"⚠️ Notepad argument parsing error: {e}")
        # Argumentlar parse edilemezse normal başlat
    
    notepad.show()
    return app.exec()

if __name__ == "__main__":
    run_notepad() 