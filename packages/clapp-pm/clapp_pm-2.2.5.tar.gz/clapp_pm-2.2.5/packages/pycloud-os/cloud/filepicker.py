"""
Cloud FilePicker - PyCloud OS Dosya Seçim Penceresi
VFS ile entegre çalışan güvenli dosya seçici
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Callable
from datetime import datetime

# PyQt6 import
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class FilePickerMode:
    """Dosya seçici modları"""
    OPEN_FILE = "open_file"
    SAVE_FILE = "save_file"
    SELECT_DIRECTORY = "select_directory"
    MULTIPLE_FILES = "multiple_files"

class FilePickerFilter:
    """Dosya filtreleri"""
    ALL_FILES = ("Tüm Dosyalar", "*")
    TEXT_FILES = ("Metin Dosyaları", "*.txt;*.md;*.py;*.json;*.log")
    PYTHON_FILES = ("Python Dosyaları", "*.py;*.pyw;*.pyi")
    IMAGES = ("Resim Dosyaları", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")
    DOCUMENTS = ("Belgeler", "*.pdf;*.doc;*.docx;*.odt")
    ARCHIVES = ("Arşiv Dosyaları", "*.zip;*.tar;*.gz;*.rar")
    CODE_FILES = ("Kod Dosyaları", "*.py;*.js;*.html;*.css;*.json;*.xml;*.yaml;*.yml")
    
    @staticmethod
    def custom(name: str, extensions: str):
        """Özel filtre oluştur"""
        return (name, extensions)

if PYQT_AVAILABLE:
    class CloudFilePicker(QDialog):
        """PyCloud OS Dosya Seçici"""
        
        # Sinyaller
        fileSelected = pyqtSignal(str)  # Dosya seçildi
        filesSelected = pyqtSignal(list)  # Çoklu dosya seçildi
        directorySelected = pyqtSignal(str)  # Dizin seçildi
        
        def __init__(self, parent=None, kernel=None):
            super().__init__(parent)
            self.kernel = kernel
            self.logger = logging.getLogger("CloudFilePicker")
            
            # VFS referansı
            self.vfs = None
            if self.kernel:
                try:
                    self.vfs = self.kernel.get_module("vfs")
                except:
                    self.logger.warning("VFS module not available")
            
            # UI bileşenleri
            self.path_bar = None
            self.file_list = None
            self.file_name_edit = None
            self.filter_combo = None
            self.button_box = None
            
            # Durum
            self.current_path = "/home"
            self.mode = FilePickerMode.OPEN_FILE
            self.filters = [FilePickerFilter.ALL_FILES]
            self.selected_files = []
            self.app_id = "unknown"
            self.multi_select = False
            
            # Tema
            self.is_dark_mode = self._detect_dark_mode()
            
            self._init_ui()
            self._connect_signals()
            self._apply_theme()
            
        def _detect_dark_mode(self) -> bool:
            """Sistem temasını tespit et"""
            try:
                if self.kernel:
                    config = self.kernel.get_module("config")
                    if config:
                        theme_config = config.get("theme", {})
                        return theme_config.get("dark_mode", False)
            except:
                pass
            return False
        
        def _init_ui(self):
            """UI bileşenlerini oluştur"""
            self.setWindowTitle("Dosya Seç")
            self.setFixedSize(800, 600)
            
            # Ana layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(8)
            
            # Üst panel - navigation
            nav_layout = QHBoxLayout()
            
            # Geri/İleri butonları
            self.back_btn = QPushButton("←")
            self.back_btn.setFixedSize(32, 32)
            self.back_btn.setToolTip("Geri")
            nav_layout.addWidget(self.back_btn)
            
            self.forward_btn = QPushButton("→")
            self.forward_btn.setFixedSize(32, 32)
            self.forward_btn.setToolTip("İleri")
            nav_layout.addWidget(self.forward_btn)
            
            # Ana dizin butonu
            self.home_btn = QPushButton("🏠")
            self.home_btn.setFixedSize(32, 32)
            self.home_btn.setToolTip("Ana Dizin")
            nav_layout.addWidget(self.home_btn)
            
            # Yol çubuğu
            self.path_bar = QLineEdit()
            self.path_bar.setPlaceholderText("Dosya yolu...")
            nav_layout.addWidget(self.path_bar)
            
            layout.addLayout(nav_layout)
            
            # Orta panel - dosya listesi
            self.file_list = QListWidget()
            self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.file_list.setIconSize(QSize(24, 24))
            layout.addWidget(self.file_list)
            
            # Alt panel - dosya adı ve filtreler
            bottom_layout = QGridLayout()
            
            # Dosya adı
            bottom_layout.addWidget(QLabel("Dosya adı:"), 0, 0)
            self.file_name_edit = QLineEdit()
            bottom_layout.addWidget(self.file_name_edit, 0, 1, 1, 2)
            
            # Filtre
            bottom_layout.addWidget(QLabel("Dosya türü:"), 1, 0)
            self.filter_combo = QComboBox()
            bottom_layout.addWidget(self.filter_combo, 1, 1, 1, 2)
            
            layout.addLayout(bottom_layout)
            
            # Buton panel
            self.button_box = QDialogButtonBox()
            self.ok_btn = self.button_box.addButton("Tamam", QDialogButtonBox.ButtonRole.AcceptRole)
            self.cancel_btn = self.button_box.addButton("İptal", QDialogButtonBox.ButtonRole.RejectRole)
            layout.addWidget(self.button_box)
            
        def _connect_signals(self):
            """Sinyalleri bağla"""
            # Navigation
            self.back_btn.clicked.connect(self._go_back)
            self.forward_btn.clicked.connect(self._go_forward)
            self.home_btn.clicked.connect(self._go_home)
            self.path_bar.returnPressed.connect(self._navigate_to_path)
            
            # File list
            self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)
            self.file_list.itemSelectionChanged.connect(self.selection_changed)
            
            # Filter
            self.filter_combo.currentTextChanged.connect(self._apply_filter)
            
            # Buttons
            self.button_box.accepted.connect(self.accept_selection)
            self.button_box.rejected.connect(self.reject)
            
        def _apply_theme(self):
            """Tema uygula"""
            if self.is_dark_mode:
                # Koyu tema
                self.setStyleSheet("""
                    QDialog {
                        background-color: #2b2b2b;
                        color: white;
                    }
                    QListWidget {
                        background-color: #353535;
                        border: 1px solid #555;
                        border-radius: 4px;
                    }
                    QListWidget::item {
                        padding: 8px;
                        border-bottom: 1px solid #444;
                    }
                    QListWidget::item:selected {
                        background-color: #0078d4;
                    }
                    QLineEdit, QComboBox {
                        background-color: #353535;
                        border: 1px solid #555;
                        border-radius: 4px;
                        padding: 6px;
                    }
                    QPushButton {
                        background-color: #404040;
                        border: 1px solid #555;
                        border-radius: 4px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #4a4a4a;
                    }
                    QPushButton:pressed {
                        background-color: #333;
                    }
                """)
            else:
                # Açık tema
                self.setStyleSheet("""
                    QDialog {
                        background-color: white;
                        color: black;
                    }
                    QListWidget {
                        background-color: white;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }
                    QListWidget::item {
                        padding: 8px;
                        border-bottom: 1px solid #eee;
                    }
                    QListWidget::item:selected {
                        background-color: #0078d4;
                        color: white;
                    }
                    QLineEdit, QComboBox {
                        background-color: white;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        padding: 6px;
                    }
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)
        
        def setup(self, mode: str, filters: List[tuple] = None, app_id: str = "unknown", 
                 multi_select: bool = False, initial_path: str = None):
            """FilePicker'ı yapılandır"""
            self.mode = mode
            self.app_id = app_id
            self.multi_select = multi_select
            
            # Çoklu seçim
            if multi_select:
                self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
            
            # Filtreler
            if filters:
                self.filters = filters
            
            self.filter_combo.clear()
            for name, ext in self.filters:
                self.filter_combo.addItem(f"{name} ({ext})")
            
            # Başlangıç dizini
            if initial_path and self._is_path_allowed(initial_path):
                self.current_path = initial_path
            else:
                self.current_path = self._get_default_path()
            
            # UI güncellemeleri
            self._update_title()
            self._navigate_to(self.current_path)
            
        def _update_title(self):
            """Pencere başlığını güncelle"""
            titles = {
                FilePickerMode.OPEN_FILE: "Dosya Aç",
                FilePickerMode.SAVE_FILE: "Dosyayı Kaydet",
                FilePickerMode.SELECT_DIRECTORY: "Dizin Seç",
                FilePickerMode.MULTIPLE_FILES: "Dosyalar Seç"
            }
            self.setWindowTitle(titles.get(self.mode, "Dosya Seç"))
            
        def _get_default_path(self) -> str:
            """Varsayılan başlangıç yolu"""
            if self.vfs:
                allowed_paths = self.vfs.list_allowed_paths(self.app_id)
                if "/home" in allowed_paths:
                    return "/home"
                elif allowed_paths:
                    return allowed_paths[0]
            return "/home"
        
        def _is_path_allowed(self, path: str) -> bool:
            """Yola erişim izni var mı?"""
            if not self.vfs:
                return True
            return self.vfs.validate_path(path, self.app_id)
        
        def _navigate_to(self, path: str):
            """Belirtilen dizine git"""
            try:
                if not self._is_path_allowed(path):
                    self.logger.warning(f"Access denied to path: {path}")
                    return
                
                self.current_path = path
                self.path_bar.setText(path)
                self._load_directory()
                
            except Exception as e:
                self.logger.error(f"Navigation error: {e}")
        
        def _load_directory(self):
            """Dizin içeriğini yükle"""
            try:
                self.file_list.clear()
                
                # VFS üzerinden dizin listesi al
                if self.vfs:
                    real_path = self.vfs.resolve_path(self.current_path)
                    if not real_path or not os.path.exists(real_path):
                        return
                    
                    real_path_obj = Path(real_path)
                else:
                    # Fallback - direkt sistem
                    real_path_obj = Path(self.current_path)
                
                # Üst dizin (".." seçeneği)
                if self.current_path != "/":
                    parent_item = QListWidgetItem("📁 ..")
                    parent_item.setData(Qt.ItemDataRole.UserRole, "directory")
                    self.file_list.addItem(parent_item)
                
                # Dizin ve dosyaları listele
                if real_path_obj.exists():
                    items = []
                    for item in real_path_obj.iterdir():
                        try:
                            if item.is_dir():
                                items.append((item.name, "directory"))
                            else:
                                items.append((item.name, "file"))
                        except:
                            continue
                    
                    # Sırala: dizinler önce, sonra dosyalar
                    items.sort(key=lambda x: (x[1] != "directory", x[0].lower()))
                    
                    for name, item_type in items:
                        icon = "📁" if item_type == "directory" else self._get_file_icon(name)
                        list_item = QListWidgetItem(f"{icon} {name}")
                        list_item.setData(Qt.ItemDataRole.UserRole, item_type)
                        self.file_list.addItem(list_item)
                
            except Exception as e:
                self.logger.error(f"Failed to load directory: {e}")
        
        def _get_file_icon(self, filename: str) -> str:
            """Dosya türüne göre ikon"""
            ext = Path(filename).suffix.lower()
            icons = {
                '.txt': '📄', '.md': '📝', '.py': '🐍', '.js': '📜',
                '.html': '🌐', '.css': '🎨', '.json': '📋',
                '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
                '.mp3': '🎵', '.wav': '🎵', '.mp4': '🎬', '.avi': '🎬',
                '.pdf': '📕', '.zip': '📦', '.tar': '📦', '.gz': '📦'
            }
            return icons.get(ext, '📄')
        
        def _navigate_to_path(self):
            """Yol çubuğundan navigasyon"""
            path = self.path_bar.text().strip()
            if path:
                self._navigate_to(path)
        
        def _go_back(self):
            """Üst dizine git"""
            if self.current_path != "/":
                parent = str(Path(self.current_path).parent)
                if parent != self.current_path:
                    self._navigate_to(parent)
        
        def _go_forward(self):
            """İleri git (şimdilik placeholder)"""
            pass
        
        def _go_home(self):
            """Ana dizine git"""
            home_path = self._get_default_path()
            self._navigate_to(home_path)
        
        def _on_item_double_clicked(self, item: QListWidgetItem):
            """Öğeye çift tıklama"""
            item_type = item.data(Qt.ItemDataRole.UserRole)
            item_text = item.text()
            
            # İkon prefixi kaldır
            name = item_text.split(" ", 1)[1] if " " in item_text else item_text
            
            if item_type == "directory":
                if name == "..":
                    self._go_back()
                else:
                    new_path = str(Path(self.current_path) / name)
                    self._navigate_to(new_path)
            elif self.mode in [FilePickerMode.OPEN_FILE, FilePickerMode.MULTIPLE_FILES]:
                # Dosya seçildi, dialog'u kapat
                self.accept()
        
        def selection_changed(self):
            """Seçim değiştiğinde çağrılır"""
            try:
                if self.mode == FilePickerMode.MULTIPLE_FILES:
                    # Multiple selection handling
                    selected_items = self.file_list.selectedItems()
                    selected_count = len(selected_items)
                    
                    self.selection_info.setText(f"{selected_count} dosya seçildi")
                    self.action_button.setEnabled(selected_count > 0)
                    
                    # Seçili dosyaları sakla
                    self.selected_files = []
                    for item in selected_items:
                        filename = item.text()
                        if not filename.startswith("📁"):  # Klasör değilse
                            file_path = str(Path(self.current_path) / filename)
                            self.selected_files.append(file_path)
                    
                else:
                    # Single selection handling
                    selected_items = self.file_list.selectedItems()
                    if selected_items:
                        filename = selected_items[0].text()
                        if filename.startswith("📁"):  # Klasör
                            self.action_button.setEnabled(self.mode == FilePickerMode.SELECT_DIRECTORY)
                        else:  # Dosya
                            self.action_button.setEnabled(self.mode in [FilePickerMode.OPEN_FILE])
                            if hasattr(self, 'filename_input'):
                                self.filename_input.setText(filename)
                    else:
                        self.action_button.setEnabled(False)
                    
            except Exception as e:
                self.logger.error(f"Selection changed error: {e}")
        
        def accept_selection(self):
            """Seçimi kabul et"""
            try:
                if self.mode == FilePickerMode.MULTIPLE_FILES:
                    # Multiple files return
                    if hasattr(self, 'selected_files') and self.selected_files:
                        self.selected_paths = self.selected_files
                        self.accept()
                    
                elif self.mode == FilePickerMode.SAVE_FILE:
                    # Save file handling
                    if hasattr(self, 'filename_input'):
                        filename = self.filename_input.text().strip()
                        if filename:
                            self.selected_path = str(Path(self.current_path) / filename)
                            self.accept()
                            
                elif self.mode == FilePickerMode.OPEN_FILE:
                    # Open file handling
                    selected_items = self.file_list.selectedItems()
                    if selected_items:
                        filename = selected_items[0].text()
                        if not filename.startswith("📁"):
                            self.selected_path = str(Path(self.current_path) / filename)
                            self.accept()
                            
                elif self.mode == FilePickerMode.SELECT_DIRECTORY:
                    # Directory selection
                    self.selected_path = self.current_path
                    self.accept()
                    
            except Exception as e:
                self.logger.error(f"Accept selection error: {e}")
        
        def get_selected_files(self) -> List[str]:
            """Seçili dosyaları al (multiple mode için)"""
            if hasattr(self, 'selected_paths'):
                return self.selected_paths
            elif hasattr(self, 'selected_path'):
                return [self.selected_path]
            else:
                return []
        
        def _apply_filter(self):
            """Filtre uygula"""
            # Şimdilik placeholder - gelecekte dosya filtreleme eklenebilir
            pass

def show_file_picker(mode: str = FilePickerMode.OPEN_FILE, 
                    filters: List[tuple] = None,
                    app_id: str = "unknown",
                    multi_select: bool = False,
                    initial_path: str = None,
                    parent=None,
                    kernel=None) -> Optional[str]:
    """Dosya seçici göster"""
    if not PYQT_AVAILABLE:
        return None
    
    try:
        picker = CloudFilePicker(parent=parent, kernel=kernel)
        picker.setup(mode=mode, filters=filters, app_id=app_id, 
                    multi_select=multi_select, initial_path=initial_path)
        
        # Modal dialog olarak göster
        if picker.exec() == QDialog.DialogCode.Accepted:
            if mode == FilePickerMode.SELECT_DIRECTORY:
                return picker.current_path
            else:
                filename = picker.file_name_edit.text().strip()
                if filename:
                    return str(Path(picker.current_path) / filename)
        
        return None
        
    except Exception as e:
        logging.getLogger("CloudFilePicker").error(f"FilePicker error: {e}")
        return None

# Convenience functions
def open_file_dialog(app_id: str = "unknown", filters: List[tuple] = None, 
                    parent=None, kernel=None) -> Optional[str]:
    """Dosya açma dialog'u"""
    return show_file_picker(
        mode=FilePickerMode.OPEN_FILE,
        filters=filters or [FilePickerFilter.ALL_FILES],
        app_id=app_id,
        parent=parent,
        kernel=kernel
    )

def save_file_dialog(app_id: str = "unknown", filters: List[tuple] = None,
                    parent=None, kernel=None) -> Optional[str]:
    """Dosya kaydetme dialog'u"""
    return show_file_picker(
        mode=FilePickerMode.SAVE_FILE,
        filters=filters or [FilePickerFilter.ALL_FILES],
        app_id=app_id,
        parent=parent,
        kernel=kernel
    )

def select_directory_dialog(app_id: str = "unknown", parent=None, kernel=None) -> Optional[str]:
    """Dizin seçme dialog'u"""
    return show_file_picker(
        mode=FilePickerMode.SELECT_DIRECTORY,
        app_id=app_id,
        parent=parent,
        kernel=kernel
    )

def select_multiple_files_dialog(app_id: str = "unknown", filters: List[tuple] = None,
                                parent=None, kernel=None) -> Optional[List[str]]:
    """Çoklu dosya seçme dialog'u"""
    if not PYQT_AVAILABLE:
        return None
    
    try:
        from PyQt6.QtWidgets import QApplication
        
        # App instance kontrolü
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Custom FilePicker window oluştur
        picker = CloudFilePicker(
            parent=parent,
            kernel=kernel
        )
        picker.setup(
            mode=FilePickerMode.MULTIPLE_FILES,
            filters=filters or [FilePickerFilter.ALL_FILES],
            app_id=app_id,
            multi_select=True
        )
        
        if picker.exec() == QDialog.DialogCode.Accepted:
            return picker.get_selected_files()
        
        return None
        
    except Exception as e:
        logging.getLogger("CloudFilePicker").error(f"Multiple files picker error: {e}")
        return None

def setup_ui(self):
    """UI kurulumu"""
    layout = QVBoxLayout()
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)
    
    # Başlık
    title_text = {
        FilePickerMode.OPEN_FILE: "📁 Dosya Aç",
        FilePickerMode.SAVE_FILE: "💾 Dosya Kaydet", 
        FilePickerMode.SELECT_DIRECTORY: "📂 Klasör Seç",
        FilePickerMode.MULTIPLE_FILES: "📋 Çoklu Dosya Seç"
    }
    
    title = QLabel(title_text.get(self.mode, "📁 Dosya İşlemi"))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
    layout.addWidget(title)
    
    # VFS bilgi paneli
    self.vfs_info_panel = QWidget()
    self.setup_vfs_info_panel()
    layout.addWidget(self.vfs_info_panel)
    
    # Ana panel (yan yana)
    main_panel = QWidget()
    main_layout = QHBoxLayout(main_panel)
    main_layout.setSpacing(12)
    
    # Sol panel - Dizin ağacı
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)
    
    # Dizin ağacı
    tree_label = QLabel("🗂️ Dizinler")
    tree_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
    left_layout.addWidget(tree_label)
    
    self.tree_view = QTreeView()
    self.tree_view.setHeaderHidden(True)
    self.tree_view.setMinimumWidth(200)
    left_layout.addWidget(self.tree_view)
    
    # Sağ panel - Dosya listesi
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    
    # Dosya listesi başlığı
    files_label = QLabel("📄 Dosyalar")
    files_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
    right_layout.addWidget(files_label)
    
    # Dosya listesi
    self.file_list = QListWidget()
    
    # Multiple selection mode için ayar
    if self.mode == FilePickerMode.MULTIPLE_FILES:
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.file_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 2px solid #2196f3;
            }
        """)
    else:
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    
    self.file_list.setMinimumHeight(300)
    self.file_list.itemDoubleClicked.connect(self.file_double_clicked)
    self.file_list.itemSelectionChanged.connect(self.selection_changed)
    right_layout.addWidget(self.file_list)
    
    # Dosya adı girişi (save mode için)
    if self.mode == FilePickerMode.SAVE_FILE:
        filename_label = QLabel("📝 Dosya Adı:")
        right_layout.addWidget(filename_label)
        
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("dosya_adi.txt")
        self.filename_input.textChanged.connect(self.validate_selection)
        right_layout.addWidget(self.filename_input)
    
    # Multiple files için seçim bilgisi
    if self.mode == FilePickerMode.MULTIPLE_FILES:
        self.selection_info = QLabel("0 dosya seçildi")
        self.selection_info.setStyleSheet("color: #666; font-style: italic;")
        right_layout.addWidget(self.selection_info)
    
    # Panel boyutları
    left_panel.setMaximumWidth(250)
    
    main_layout.addWidget(left_panel)
    main_layout.addWidget(right_panel)
    layout.addWidget(main_panel)
    
    # Filtre seçimi
    if self.filters:
        filter_label = QLabel("🔍 Dosya Türü:")
        layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        for filter_item in self.filters:
            self.filter_combo.addItem(filter_item.description, filter_item.extensions)
        self.filter_combo.currentTextChanged.connect(self.filter_changed)
        layout.addWidget(self.filter_combo)
    
    # Butonlar
    button_layout = QHBoxLayout()
    
    # Cancel butonu
    self.cancel_button = QPushButton("❌ İptal")
    self.cancel_button.clicked.connect(self.reject)
    button_layout.addWidget(self.cancel_button)
    
    button_layout.addStretch()
    
    # Ana eylem butonu
    action_text = {
        FilePickerMode.OPEN_FILE: "📂 Aç",
        FilePickerMode.SAVE_FILE: "💾 Kaydet",
        FilePickerMode.SELECT_DIRECTORY: "📂 Seç",
        FilePickerMode.MULTIPLE_FILES: "📋 Seç"
    }
    
    self.action_button = QPushButton(action_text.get(self.mode, "✅ Tamam"))
    self.action_button.setEnabled(False)
    self.action_button.clicked.connect(self.accept_selection)
    button_layout.addWidget(self.action_button)
    
    layout.addLayout(button_layout)
    self.setLayout(layout)

# Export yapılacak fonksiyonlar
__all__ = [
    'FilePickerMode', 
    'FilePickerFilter', 
    'CloudFilePicker',
    'open_file_dialog', 
    'save_file_dialog', 
    'select_directory_dialog',
    'select_multiple_files_dialog',
    'show_file_picker'
] 