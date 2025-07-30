"""
Cloud Browser Yer İmi Yöneticisi
JSON tabanlı yer imi sistemi
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    raise ImportError("PyQt6 is required for Cloud Browser")

class BookmarkManager:
    """
    Yer imi yöneticisi sınıfı
    """
    
    def __init__(self):
        self.bookmarks: List[Dict[str, Any]] = []
        self.bookmarks_file = Path.home() / ".cloud_browser" / "bookmarks.json"
        self.bookmarks_file.parent.mkdir(exist_ok=True)
        self.load_bookmarks()
    
    def load_bookmarks(self):
        """Yer imlerini dosyadan yükle"""
        try:
            if self.bookmarks_file.exists():
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bookmarks = data.get('bookmarks', [])
            else:
                # Varsayılan yer imleri
                self.bookmarks = [
                    {
                        "title": "Google",
                        "url": "https://www.google.com",
                        "folder": "Genel",
                        "created": datetime.now().isoformat(),
                        "visits": 0,
                        "favicon": "🔍"
                    },
                    {
                        "title": "YouTube",
                        "url": "https://www.youtube.com",
                        "folder": "Genel",
                        "created": datetime.now().isoformat(),
                        "visits": 0,
                        "favicon": "📺"
                    },
                    {
                        "title": "GitHub",
                        "url": "https://www.github.com",
                        "folder": "Geliştirme",
                        "created": datetime.now().isoformat(),
                        "visits": 0,
                        "favicon": "💻"
                    }
                ]
                self.save_bookmarks()
        except Exception as e:
            print(f"Yer imi yükleme hatası: {e}")
            self.bookmarks = []
    
    def save_bookmarks(self):
        """Yer imlerini dosyaya kaydet"""
        try:
            data = {
                "version": "2.0.0",
                "created": datetime.now().isoformat(),
                "bookmarks": self.bookmarks
            }
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Yer imi kaydetme hatası: {e}")
    
    def add_bookmark(self, title: str, url: str, folder: str = "Genel", favicon: str = "🌐"):
        """Yer imi ekle"""
        # Zaten var mı kontrol et
        if self.is_bookmarked(url):
            return False
        
        bookmark = {
            "title": title.strip(),
            "url": url.strip(),
            "folder": folder.strip(),
            "created": datetime.now().isoformat(),
            "visits": 0,
            "favicon": favicon
        }
        
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        return True
    
    def remove_bookmark(self, url: str):
        """Yer imi sil"""
        original_count = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if b["url"] != url]
        
        if len(self.bookmarks) < original_count:
            self.save_bookmarks()
            return True
        return False
    
    def update_bookmark(self, old_url: str, title: str, url: str, folder: str):
        """Yer imi güncelle"""
        for bookmark in self.bookmarks:
            if bookmark["url"] == old_url:
                bookmark["title"] = title.strip()
                bookmark["url"] = url.strip()
                bookmark["folder"] = folder.strip()
                bookmark["modified"] = datetime.now().isoformat()
                self.save_bookmarks()
                return True
        return False
    
    def get_bookmarks(self, folder: Optional[str] = None) -> List[Dict[str, Any]]:
        """Yer imlerini al"""
        if folder:
            return [b for b in self.bookmarks if b.get("folder") == folder]
        return self.bookmarks.copy()
    
    def get_folders(self) -> List[str]:
        """Klasör listesini al"""
        folders = set()
        for bookmark in self.bookmarks:
            folders.add(bookmark.get("folder", "Genel"))
        return sorted(list(folders))
    
    def is_bookmarked(self, url: str) -> bool:
        """URL yer imi var mı?"""
        return any(b["url"] == url for b in self.bookmarks)
    
    def increment_visits(self, url: str):
        """Ziyaret sayısını artır"""
        for bookmark in self.bookmarks:
            if bookmark["url"] == url:
                bookmark["visits"] = bookmark.get("visits", 0) + 1
                bookmark["last_visited"] = datetime.now().isoformat()
                self.save_bookmarks()
                break
    
    def search_bookmarks(self, query: str) -> List[Dict[str, Any]]:
        """Yer imlerinde arama yap"""
        query = query.lower().strip()
        if not query:
            return self.bookmarks.copy()
        
        results = []
        for bookmark in self.bookmarks:
            title = bookmark.get("title", "").lower()
            url = bookmark.get("url", "").lower()
            folder = bookmark.get("folder", "").lower()
            
            if query in title or query in url or query in folder:
                results.append(bookmark)
        
        return results

class BookmarkManagerDialog(QDialog):
    """
    Yer imi yöneticisi dialog'u
    """
    
    def __init__(self, bookmark_manager: BookmarkManager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.parent_browser = parent
        
        self.setWindowTitle("Yer İmi Yöneticisi")
        self.setModal(True)
        self.resize(800, 600)
        
        self.init_ui()
        self.load_bookmarks()
    
    def init_ui(self):
        """UI'yı başlat"""
        layout = QVBoxLayout(self)
        
        # Üst toolbar
        toolbar_layout = QHBoxLayout()
        
        # Arama kutusu
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Yer imlerinde ara...")
        self.search_box.textChanged.connect(self.filter_bookmarks)
        toolbar_layout.addWidget(QLabel("🔍"))
        toolbar_layout.addWidget(self.search_box)
        
        # Klasör filtresi
        self.folder_combo = QComboBox()
        self.folder_combo.addItem("Tüm Klasörler")
        self.folder_combo.currentTextChanged.connect(self.filter_bookmarks)
        toolbar_layout.addWidget(QLabel("📁"))
        toolbar_layout.addWidget(self.folder_combo)
        
        # Spacer
        toolbar_layout.addStretch()
        
        # Yeni yer imi butonu
        add_btn = QPushButton("➕ Yeni Yer İmi")
        add_btn.clicked.connect(self.add_bookmark)
        toolbar_layout.addWidget(add_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Yer imi listesi
        self.bookmark_list = QTreeWidget()
        self.bookmark_list.setHeaderLabels(["Başlık", "URL", "Klasör", "Oluşturulma", "Ziyaret"])
        self.bookmark_list.setRootIsDecorated(False)
        self.bookmark_list.setAlternatingRowColors(True)
        self.bookmark_list.setSortingEnabled(True)
        self.bookmark_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        # Context menu
        self.bookmark_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmark_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Double click
        self.bookmark_list.itemDoubleClicked.connect(self.open_bookmark)
        
        layout.addWidget(self.bookmark_list)
        
        # Alt butonlar
        button_layout = QHBoxLayout()
        
        open_btn = QPushButton("🌐 Aç")
        open_btn.clicked.connect(self.open_bookmark)
        button_layout.addWidget(open_btn)
        
        edit_btn = QPushButton("✏️ Düzenle")
        edit_btn.clicked.connect(self.edit_bookmark)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.clicked.connect(self.delete_bookmark)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        export_btn = QPushButton("📤 Dışa Aktar")
        export_btn.clicked.connect(self.export_bookmarks)
        button_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 İçe Aktar")
        import_btn.clicked.connect(self.import_bookmarks)
        button_layout.addWidget(import_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Kapat")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Stil uygula
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QTreeWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e9ecef;
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
            QPushButton:pressed {
                background-color: #004085;
            }
            QLineEdit, QComboBox {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #007bff;
            }
        """)
    
    def load_bookmarks(self):
        """Yer imlerini yükle"""
        self.bookmark_list.clear()
        
        # Klasör combo'yu güncelle
        self.folder_combo.clear()
        self.folder_combo.addItem("Tüm Klasörler")
        folders = self.bookmark_manager.get_folders()
        self.folder_combo.addItems(folders)
        
        # Yer imlerini ekle
        bookmarks = self.bookmark_manager.get_bookmarks()
        for bookmark in bookmarks:
            self.add_bookmark_item(bookmark)
        
        # Sütun genişliklerini ayarla
        self.bookmark_list.resizeColumnToContents(0)
        self.bookmark_list.resizeColumnToContents(2)
        self.bookmark_list.resizeColumnToContents(3)
        self.bookmark_list.resizeColumnToContents(4)
    
    def add_bookmark_item(self, bookmark: Dict[str, Any]):
        """Yer imi öğesi ekle"""
        item = QTreeWidgetItem()
        
        # Favicon + başlık
        favicon = bookmark.get("favicon", "🌐")
        title = bookmark.get("title", "")
        item.setText(0, f"{favicon} {title}")
        
        # URL
        item.setText(1, bookmark.get("url", ""))
        
        # Klasör
        item.setText(2, bookmark.get("folder", "Genel"))
        
        # Oluşturulma tarihi
        created = bookmark.get("created", "")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                item.setText(3, dt.strftime("%d.%m.%Y"))
            except:
                item.setText(3, created[:10])
        
        # Ziyaret sayısı
        visits = bookmark.get("visits", 0)
        item.setText(4, str(visits))
        
        # Data olarak bookmark'ı sakla
        item.setData(0, Qt.ItemDataRole.UserRole, bookmark)
        
        self.bookmark_list.addTopLevelItem(item)
    
    def filter_bookmarks(self):
        """Yer imlerini filtrele"""
        search_text = self.search_box.text().lower()
        selected_folder = self.folder_combo.currentText()
        
        for i in range(self.bookmark_list.topLevelItemCount()):
            item = self.bookmark_list.topLevelItem(i)
            bookmark = item.data(0, Qt.ItemDataRole.UserRole)
            
            # Arama filtresi
            title_match = search_text in bookmark.get("title", "").lower()
            url_match = search_text in bookmark.get("url", "").lower()
            search_match = not search_text or title_match or url_match
            
            # Klasör filtresi
            folder_match = (selected_folder == "Tüm Klasörler" or 
                          bookmark.get("folder", "Genel") == selected_folder)
            
            # Görünürlük
            item.setHidden(not (search_match and folder_match))
    
    def show_context_menu(self, position):
        """Context menü göster"""
        item = self.bookmark_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        open_action = menu.addAction("🌐 Aç")
        open_action.triggered.connect(self.open_bookmark)
        
        open_new_tab_action = menu.addAction("🆕 Yeni Sekmede Aç")
        open_new_tab_action.triggered.connect(self.open_bookmark_new_tab)
        
        menu.addSeparator()
        
        edit_action = menu.addAction("✏️ Düzenle")
        edit_action.triggered.connect(self.edit_bookmark)
        
        delete_action = menu.addAction("🗑️ Sil")
        delete_action.triggered.connect(self.delete_bookmark)
        
        menu.exec(self.bookmark_list.mapToGlobal(position))
    
    def open_bookmark(self):
        """Yer imini aç"""
        current_item = self.bookmark_list.currentItem()
        if not current_item:
            return
        
        bookmark = current_item.data(0, Qt.ItemDataRole.UserRole)
        url = bookmark.get("url", "")
        
        if url and self.parent_browser:
            # Mevcut sekmede aç
            if hasattr(self.parent_browser, 'tab_widget'):
                current_web_view = self.parent_browser.tab_widget.current_web_view()
                if current_web_view and hasattr(current_web_view, 'setUrl'):
                    current_web_view.setUrl(QUrl(url))
            
            # Ziyaret sayısını artır
            self.bookmark_manager.increment_visits(url)
            
            # Dialog'u kapat
            self.close()
    
    def open_bookmark_new_tab(self):
        """Yer imini yeni sekmede aç"""
        current_item = self.bookmark_list.currentItem()
        if not current_item:
            return
        
        bookmark = current_item.data(0, Qt.ItemDataRole.UserRole)
        url = bookmark.get("url", "")
        
        if url and self.parent_browser:
            # Yeni sekmede aç
            self.parent_browser.new_tab(url)
            
            # Ziyaret sayısını artır
            self.bookmark_manager.increment_visits(url)
    
    def add_bookmark(self):
        """Yeni yer imi ekle"""
        dialog = BookmarkEditDialog(self.bookmark_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_bookmarks()
    
    def edit_bookmark(self):
        """Yer imi düzenle"""
        current_item = self.bookmark_list.currentItem()
        if not current_item:
            return
        
        bookmark = current_item.data(0, Qt.ItemDataRole.UserRole)
        dialog = BookmarkEditDialog(self.bookmark_manager, bookmark, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_bookmarks()
    
    def delete_bookmark(self):
        """Yer imi sil"""
        selected_items = self.bookmark_list.selectedItems()
        if not selected_items:
            return
        
        reply = QMessageBox.question(
            self,
            "Yer İmi Sil",
            f"{len(selected_items)} yer imi silinecek. Emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                bookmark = item.data(0, Qt.ItemDataRole.UserRole)
                url = bookmark.get("url", "")
                self.bookmark_manager.remove_bookmark(url)
            
            self.load_bookmarks()
    
    def export_bookmarks(self):
        """Yer imlerini dışa aktar"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Yer İmlerini Dışa Aktar",
            "bookmarks.json",
            "JSON Dosyaları (*.json);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            try:
                data = {
                    "version": "2.0.0",
                    "exported": datetime.now().isoformat(),
                    "bookmarks": self.bookmark_manager.get_bookmarks()
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                QMessageBox.information(self, "Başarılı", "Yer imleri başarıyla dışa aktarıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma hatası: {e}")
    
    def import_bookmarks(self):
        """Yer imlerini içe aktar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Yer İmlerini İçe Aktar",
            "",
            "JSON Dosyaları (*.json);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                bookmarks = data.get('bookmarks', [])
                imported_count = 0
                
                for bookmark in bookmarks:
                    title = bookmark.get('title', '')
                    url = bookmark.get('url', '')
                    folder = bookmark.get('folder', 'İçe Aktarılan')
                    
                    if title and url:
                        if self.bookmark_manager.add_bookmark(title, url, folder):
                            imported_count += 1
                
                self.load_bookmarks()
                QMessageBox.information(self, "Başarılı", f"{imported_count} yer imi başarıyla içe aktarıldı.")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"İçe aktarma hatası: {e}")

class BookmarkEditDialog(QDialog):
    """
    Yer imi düzenleme dialog'u
    """
    
    def __init__(self, bookmark_manager: BookmarkManager, bookmark: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.bookmark = bookmark
        self.is_edit = bookmark is not None
        
        self.setWindowTitle("Yer İmi Düzenle" if self.is_edit else "Yeni Yer İmi")
        self.setModal(True)
        self.resize(500, 300)
        
        self.init_ui()
        
        if self.is_edit:
            self.load_bookmark_data()
    
    def init_ui(self):
        """UI'yı başlat"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Başlık
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Yer imi başlığı...")
        form_layout.addRow("📝 Başlık:", self.title_edit)
        
        # URL
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com")
        form_layout.addRow("🌐 URL:", self.url_edit)
        
        # Klasör
        self.folder_combo = QComboBox()
        self.folder_combo.setEditable(True)
        folders = self.bookmark_manager.get_folders()
        self.folder_combo.addItems(folders)
        if "Genel" not in folders:
            self.folder_combo.addItem("Genel")
        form_layout.addRow("📁 Klasör:", self.folder_combo)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ İptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Kaydet")
        save_btn.clicked.connect(self.save_bookmark)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Stil
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLineEdit, QComboBox {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
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
    
    def load_bookmark_data(self):
        """Yer imi verilerini yükle"""
        if self.bookmark:
            self.title_edit.setText(self.bookmark.get("title", ""))
            self.url_edit.setText(self.bookmark.get("url", ""))
            
            folder = self.bookmark.get("folder", "Genel")
            index = self.folder_combo.findText(folder)
            if index >= 0:
                self.folder_combo.setCurrentIndex(index)
            else:
                self.folder_combo.setCurrentText(folder)
    
    def save_bookmark(self):
        """Yer imi kaydet"""
        title = self.title_edit.text().strip()
        url = self.url_edit.text().strip()
        folder = self.folder_combo.currentText().strip()
        
        if not title:
            QMessageBox.warning(self, "Uyarı", "Başlık boş olamaz.")
            return
        
        if not url:
            QMessageBox.warning(self, "Uyarı", "URL boş olamaz.")
            return
        
        # URL formatını kontrol et
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url
        
        if not folder:
            folder = "Genel"
        
        try:
            if self.is_edit:
                # Güncelle
                old_url = self.bookmark.get("url", "")
                success = self.bookmark_manager.update_bookmark(old_url, title, url, folder)
            else:
                # Yeni ekle
                success = self.bookmark_manager.add_bookmark(title, url, folder)
            
            if success:
                self.accept()
            else:
                QMessageBox.warning(self, "Uyarı", "Bu URL zaten yer imlerinde mevcut.")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme hatası: {e}") 