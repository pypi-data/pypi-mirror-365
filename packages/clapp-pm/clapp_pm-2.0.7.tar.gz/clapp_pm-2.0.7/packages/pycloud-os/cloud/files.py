"""
PyCloud OS Cloud Files - Mac Finder Benzeri Modern Dosya Yöneticisi
Sade, responsive ve kullanıcı dostu arayüz
"""

import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum

# Logger kurulumu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not available for Cloud Files")
    sys.exit(1)

class ViewMode(Enum):
    """Görünüm modları"""
    ICON = "icon"    # Mac Finder benzeri icon görünümü
    LIST = "list"    # Liste görünümü
    COLUMN = "column"  # Sütun görünümü (Finder Column View)

class FileItem:
    """Dosya öğesi sınıfı - Mac Finder benzeri"""
    
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.is_dir = path.is_dir()
        self.size = 0
        self.modified = ""
        self.created = ""
        self.icon_name = ""
        self.tags: Set[str] = set()
        self.thumbnail = None
        
        try:
            if self.path.exists():
                stat = self.path.stat()
                if not self.is_dir:
                    self.size = stat.st_size
                self.modified = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M")
                self.created = datetime.fromtimestamp(stat.st_ctime).strftime("%d.%m.%Y %H:%M")
                self.icon_name = self._get_icon_name()
                self._load_tags()
        except Exception:
            pass
    
    def _get_icon_name(self) -> str:
        """Mac benzeri dosya türü ikonları"""
        if self.is_dir:
            # Özel klasör isimleri
            folder_icons = {
                'Desktop': 'desktop_folder',
                'Documents': 'documents_folder', 
                'Downloads': 'downloads_folder',
                'Pictures': 'pictures_folder',
                'Music': 'music_folder',
                'Videos': 'videos_folder',
                'Projects': 'projects_folder',
                'Applications': 'applications_folder'
            }
            return folder_icons.get(self.name, 'folder')
        
        suffix = self.path.suffix.lower()
        icon_map = {
            '.txt': 'text_file',
            '.md': 'markdown_file',
            '.py': 'python_file',
            '.js': 'javascript_file',
            '.html': 'web_file',
            '.css': 'style_file',
            '.json': 'data_file',
            '.xml': 'markup_file',
            '.yml': 'config_file',
            '.yaml': 'config_file',
            '.jpg': 'image_file',
            '.jpeg': 'image_file',
            '.png': 'image_file',
            '.gif': 'image_file',
            '.svg': 'vector_file',
            '.pdf': 'pdf_file',
            '.doc': 'word_file',
            '.docx': 'word_file',
            '.xls': 'excel_file',
            '.xlsx': 'excel_file',
            '.ppt': 'powerpoint_file',
            '.pptx': 'powerpoint_file',
            '.zip': 'archive_file',
            '.rar': 'archive_file',
            '.7z': 'archive_file',
            '.tar': 'archive_file',
            '.gz': 'archive_file',
            '.mp3': 'audio_file',
            '.wav': 'audio_file',
            '.flac': 'audio_file',
            '.m4a': 'audio_file',
            '.mp4': 'video_file',
            '.avi': 'video_file',
            '.mkv': 'video_file',
            '.mov': 'video_file',
            '.app': 'application_file'
        }
        
        return icon_map.get(suffix, 'generic_file')
    
    def _load_tags(self):
        """Dosya etiketlerini yükle"""
        try:
            tag_file = self.path.parent / f".{self.name}.tags"
            if tag_file.exists():
                with open(tag_file, 'r', encoding='utf-8') as f:
                    self.tags = set(json.load(f))
        except Exception:
            pass
    
    def save_tags(self):
        """Dosya etiketlerini kaydet"""
        try:
            tag_file = self.path.parent / f".{self.name}.tags"
            if self.tags:
                with open(tag_file, 'w', encoding='utf-8') as f:
                    json.dump(list(self.tags), f)
            elif tag_file.exists():
                tag_file.unlink()
        except Exception:
            pass

class ModernSidebarWidget(QListWidget):
    """Mac Finder benzeri kenar çubuğu"""
    
    location_selected = pyqtSignal(str, str)  # path, display_name
    
    def __init__(self, dark_mode: bool = False):
        super().__init__()
        self.dark_mode = dark_mode
        self.setup_ui()
        
    def setup_ui(self):
        """Modern kenar çubuğu kurulumu"""
        self.setFixedWidth(200)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Mac Finder benzeri stil
        self.setStyleSheet("""
            QListWidget {
                background-color: rgba(246, 246, 246, 0.8);
                border: none;
                border-right: 1px solid rgba(0, 0, 0, 0.1);
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                margin: 1px 8px;
                color: #333333;
            }
            QListWidget::item:selected {
                background-color: rgba(0, 122, 255, 0.2);
                color: #007AFF;
            }
            QListWidget::item:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)
        
        self.populate_sidebar()
        self.itemClicked.connect(self.on_item_clicked)
    
    def populate_sidebar(self):
        """Kenar çubuğunu doldur - Mac Finder benzeri"""
        self.clear()
        
        # Kişisel klasörler - pycloud_fs/home altında
        favorites = [
            ("🏠", "Home", "pycloud_fs/home"),
            ("🖥️", "Desktop", "pycloud_fs/home/Desktop"),
            ("📄", "Documents", "pycloud_fs/home/Documents"),
            ("⬇️", "Downloads", "pycloud_fs/home/Downloads"),
            ("🎬", "Videos", "pycloud_fs/home/Videos"),
            ("📸", "Photos", "pycloud_fs/home/Photos"),
            ("💼", "Projects", "pycloud_fs/home/Projects")
        ]
        
        # Başlık ekle
        header_item = QListWidgetItem("KİŞİSEL")
        header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        header_item.setData(Qt.ItemDataRole.UserRole, None)
        header_font = header_item.font()
        header_font.setPointSize(11)
        header_font.setBold(True)
        header_item.setFont(header_font)
        header_item.setForeground(QColor(120, 120, 120))
        self.addItem(header_item)
        
        for icon, name, path in favorites:
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.ItemDataRole.UserRole, (path, name))
            self.addItem(item)
        
        # Boşluk
        spacer = QListWidgetItem("")
        spacer.setFlags(spacer.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        spacer.setData(Qt.ItemDataRole.UserRole, None)
        self.addItem(spacer)
        
        # Sistem bölümü - Ana dizin
        system_header = QListWidgetItem("SİSTEM")
        system_header.setFlags(system_header.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        system_header.setData(Qt.ItemDataRole.UserRole, None)
        system_font = system_header.font()
        system_font.setPointSize(11)
        system_font.setBold(True)
        system_header.setFont(system_font)
        system_header.setForeground(QColor(120, 120, 120))
        self.addItem(system_header)
        
        # Sistem klasörleri - Ana dizindeki gerçek klasörlerle eşleştir
        system_items = [
            ("📱", "Applications", "apps"),
            ("⚙️", "System", "system"),
            ("🗂️", "Temporary", "temp")
        ]
        
        for icon, name, path in system_items:
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.ItemDataRole.UserRole, (path, name))
            self.addItem(item)
    
    def on_item_clicked(self, item):
        """Öğe tıklandı"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            path, name = data
            self.location_selected.emit(path, name)
    
    def set_dark_mode(self, dark_mode: bool):
        """Dark mode ayarla"""
        self.dark_mode = dark_mode
        if dark_mode:
            self.setStyleSheet("""
                QListWidget {
                    background-color: rgba(40, 40, 40, 0.95);
                    border: none;
                    border-right: 1px solid rgba(255, 255, 255, 0.1);
                    font-size: 13px;
                    color: #ffffff;
                    outline: none;
                }
                QListWidget::item {
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    margin: 1px 2px;
                    color: #ffffff;
                    min-height: 20px;
                }
                QListWidget::item:selected {
                    background-color: rgba(0, 122, 255, 0.3);
                    color: #007AFF;
                }
                QListWidget::item:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
        else:
            self.setStyleSheet("""
                QListWidget {
                    background-color: rgba(246, 246, 246, 0.8);
                    border: none;
                    border-right: 1px solid rgba(0, 0, 0, 0.1);
                    font-size: 13px;
                    outline: none;
                }
                QListWidget::item {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    margin: 1px 8px;
                    color: #333333;
                }
                QListWidget::item:selected {
                    background-color: rgba(0, 122, 255, 0.2);
                    color: #007AFF;
                }
                QListWidget::item:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                }
            """)

class ModernFileListWidget(QListWidget):
    """Mac Finder benzeri dosya listesi"""
    
    file_double_clicked = pyqtSignal(str)
    context_menu_requested = pyqtSignal(str, QPoint)
    files_dropped = pyqtSignal(list, str)
    
    def __init__(self, view_mode: ViewMode = ViewMode.ICON, dark_mode: bool = False):
        super().__init__()
        self.view_mode = view_mode
        self.dark_mode = dark_mode
        self.setup_ui()
        
    def setup_ui(self):
        """Modern dosya listesi kurulumu"""
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Mac Finder benzeri stil
        self.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: none;
                padding: 16px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border: none;
                border-radius: 8px;
                margin: 4px;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: rgba(0, 122, 255, 0.2);
                border: 2px solid rgba(0, 122, 255, 0.5);
            }
            QListWidget::item:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
        """)
        
        self.update_view_mode()
    
    def update_view_mode(self):
        """Görünüm modunu güncelle"""
        if self.view_mode == ViewMode.ICON:
            # Mac Finder benzeri icon view - optimize edilmiş
            self.setViewMode(QListView.ViewMode.IconMode)
            self.setGridSize(QSize(140, 90))  # Dosya adları için yeterli genişlik
            self.setIconSize(QSize(32, 32))   # Kompakt ikon boyutu
            self.setResizeMode(QListView.ResizeMode.Adjust)
            self.setMovement(QListView.Movement.Static)
            self.setWordWrap(True)
            self.setSpacing(6)  # Minimal spacing
        elif self.view_mode == ViewMode.LIST:
            self.setViewMode(QListView.ViewMode.ListMode)
            self.setIconSize(QSize(24, 24))
            self.setSpacing(2)
        elif self.view_mode == ViewMode.COLUMN:
            # Column view (gelecekte implement edilecek)
            self.setViewMode(QListView.ViewMode.ListMode)
            self.setIconSize(QSize(20, 20))
            self.setSpacing(1)
    
    def set_view_mode(self, mode: ViewMode):
        """Görünüm modunu ayarla"""
        self.view_mode = mode
        self.update_view_mode()
    
    def set_dark_mode(self, dark_mode: bool):
        """Dark mode ayarla"""
        self.dark_mode = dark_mode
        if dark_mode:
            self.setStyleSheet("""
                QListWidget {
                    background-color: rgba(30, 30, 30, 0.95);
                    border: none;
                    padding: 16px;
                    color: #ffffff;
                    outline: none;
                }
                QListWidget::item {
                    padding: 12px;
                    border: none;
                    border-radius: 8px;
                    margin: 4px;
                    background-color: transparent;
                    color: #ffffff;
                }
                QListWidget::item:selected {
                    background-color: rgba(0, 122, 255, 0.3);
                    border: 2px solid rgba(0, 122, 255, 0.6);
                }
                QListWidget::item:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
        else:
            self.setStyleSheet("""
                QListWidget {
                    background-color: rgba(255, 255, 255, 0.95);
                    border: none;
                    padding: 16px;
                    outline: none;
                }
                QListWidget::item {
                    padding: 12px;
                    border: none;
                    border-radius: 8px;
                    margin: 4px;
                    background-color: transparent;
                }
                QListWidget::item:selected {
                    background-color: rgba(0, 122, 255, 0.2);
                    border: 2px solid rgba(0, 122, 255, 0.5);
                }
                QListWidget::item:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                }
            """)
    
    def copy_files(self, file_paths: List[str]):
        """Dosyaları kopyala - geliştirilmiş"""
        if not file_paths:
            return
        
        # Clipboard'a dosya yollarını koy
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        
        # Dosya URL'lerini ekle
        urls = [QUrl.fromLocalFile(path) for path in file_paths]
        mime_data.setUrls(urls)
        
        # Metin olarak da ekle
        mime_data.setText("\n".join(file_paths))
        
        clipboard.setMimeData(mime_data)
        # Status mesajı için parent window'a erişim
        parent = self.parent()
        if hasattr(parent, 'status_label'):
            parent.status_label.setText(f"{len(file_paths)} öğe kopyalandı")
        
        logger.info(f"Copied {len(file_paths)} files to clipboard")
    
    def paste_files(self, target_dir: str):
        """Dosyaları yapıştır - FS API entegreli"""
        try:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            
            if mime_data.hasUrls():
                target_path = Path(target_dir)
                if not target_path.is_dir():
                    self.show_error("Hedef bir klasör değil")
                    return
                
                pasted_count = 0
                failed_files = []
                
                for url in mime_data.urls():
                    source_path = Path(url.toLocalFile())
                    if not source_path.exists():
                        continue
                        
                    target_file = target_path / source_path.name
                    
                    # Çakışma kontrolü
                    if target_file.exists():
                        reply = QMessageBox.question(
                            self, "Dosya Var",
                            f"'{source_path.name}' zaten var. Üzerine yazılsın mı?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply != QMessageBox.StandardButton.Yes:
                            continue
                    
                    try:
                        # FS API kullan
                        if self.fs:
                            # Sanal dosya sistemi yolları
                            source_fs_path = str(source_path.relative_to(self.fs.base_path))
                            target_fs_path = str(target_file.relative_to(self.fs.base_path))
                            
                            # FS API ile kopyala
                            if source_path.is_dir():
                                success = self.fs.copy_directory(source_fs_path, target_fs_path)
                            else:
                                success = self.fs.copy_file(source_fs_path, target_fs_path)
                            
                            if success:
                                pasted_count += 1
                            else:
                                failed_files.append(source_path.name)
                                
                        else:
                            # Fallback - doğrudan dosya sistemi
                            import shutil
                            
                            if source_path.is_dir():
                                shutil.copytree(source_path, target_file, dirs_exist_ok=True)
                            else:
                                shutil.copy2(source_path, target_file)
                            
                            pasted_count += 1
                            
                    except Exception as e:
                        failed_files.append(f"{source_path.name} ({e})")
                        logger.error(f"paste_file error: {e}")
                
                # Sonuç mesajı
                if pasted_count > 0:
                    self.populate_file_list()  # Listeyi yenile
                    self.show_status(f"{pasted_count} öğe yapıştırıldı")
                
                if failed_files:
                    error_msg = f"Yapıştırılamadı: {', '.join(failed_files)}"
                    self.show_error(error_msg)
                    
            else:
                self.show_status("Yapıştırılacak dosya yok")
                
        except Exception as e:
            self.show_error(f"Yapıştırma başarısız: {e}")
            logger.error(f"paste_files error: {e}")
    
    def rename_file(self, file_path: str):
        """Dosyayı yeniden adlandır - FS API entegreli"""
        path = Path(file_path)
        
        new_name, ok = QInputDialog.getText(
            self, "Yeniden Adlandır",
            "Yeni ad:", text=path.name
        )
        
        if ok and new_name and new_name != path.name:
            try:
                new_path = path.parent / new_name
                
                # FS API kullan
                if self.fs:
                    # Sanal dosya sistemi yolları
                    old_fs_path = str(path.relative_to(self.fs.base_path))
                    new_fs_path = str(new_path.relative_to(self.fs.base_path))
                    
                    # FS API ile yeniden adlandır (taşı)
                    if path.is_dir():
                        success = self.fs.move_directory(old_fs_path, new_fs_path)
                    else:
                        success = self.fs.move_file(old_fs_path, new_fs_path)
                    
                    if success:
                        self.show_status(f"'{path.name}' → '{new_name}' olarak adlandırıldı")
                        self.populate_file_list()  # Listeyi yenile
                    else:
                        self.show_error(f"Yeniden adlandırma başarısız: {path.name}")
                        
                else:
                    # Fallback - doğrudan dosya sistemi
                    path.rename(new_path)
                    self.show_status(f"'{path.name}' → '{new_name}' olarak adlandırıldı")
                    self.populate_file_list()  # Listeyi yenile
                
            except FileExistsError:
                self.show_error(f"'{new_name}' zaten mevcut")
            except PermissionError:
                self.show_error("Yeniden adlandırma izniniz yok")
            except Exception as e:
                self.show_error(f"Yeniden adlandırma başarısız: {e}")
                logger.error(f"rename_file error: {e}")
    
    def delete_files(self, file_paths: List[str]):
        """Dosyaları sil"""
        if not file_paths:
            return
        
        # Onay dialog'u
        reply = QMessageBox.question(
            self, "Silme Onayı",
            f"{len(file_paths)} öğeyi silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        deleted_count = 0
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                deleted_count += 1
                
            except Exception as e:
                self.show_error(f"'{path.name}' silinemedi: {e}")
        
        self.refresh()
        self.status_label.setText(f"{deleted_count} öğe silindi")
    
    def show_properties(self, file_path: str):
        """Dosya özelliklerini göster"""
        path = Path(file_path)
        
        try:
            stat = path.stat()
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Özellikler - {path.name}")
            dialog.setFixedSize(400, 300)
            
            layout = QFormLayout(dialog)
            
            layout.addRow("Ad:", QLabel(path.name))
            layout.addRow("Yol:", QLabel(str(path.parent)))
            layout.addRow("Tür:", QLabel("Dizin" if path.is_dir() else "Dosya"))
            
            if not path.is_dir():
                layout.addRow("Boyut:", QLabel(self.format_size(stat.st_size)))
            
            layout.addRow("Oluşturulma:", QLabel(
                datetime.fromtimestamp(stat.st_ctime).strftime("%d.%m.%Y %H:%M:%S")
            ))
            layout.addRow("Değiştirilme:", QLabel(
                datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M:%S")
            ))
            layout.addRow("Son Erişim:", QLabel(
                datetime.fromtimestamp(stat.st_atime).strftime("%d.%m.%Y %H:%M:%S")
            ))
            
            # Kapat butonu
            close_button = QPushButton("Kapat")
            close_button.clicked.connect(dialog.close)
            layout.addRow("", close_button)
            
            dialog.exec()
            
        except Exception as e:
            self.show_error(f"Özellikler gösterilemedi: {e}")    
    def get_icon(self, icon_name: str) -> QIcon:
        """Modern ikon sistemi"""
        # Gelişmiş ikon haritası
        icon_map = {
            'folder': '📁',
            'file': '📄',
            'text': '📝',
            'markdown': '📋',
            'python': '🐍',
            'javascript': '🟨',
            'html': '🌐',
            'css': '🎨',
            'json': '📊',
            'xml': '📰',
            'yaml': '⚙️',
            'image': '🖼️',
            'pdf': '📕',
            'document': '📋',
            'spreadsheet': '📊',
            'presentation': '📽️',
            'archive': '📦',
            'audio': '🎵',
            'video': '🎬',
            'executable': '⚙️',
            'application': '📱',
            'package': '📦',
            'disk': '💿'
        }
        
        emoji = icon_map.get(icon_name, '📄')
        
        # Emoji'yi QIcon'a çevir - daha büyük boyut
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Görünüm moduna göre font boyutu
        if self.view_mode == ViewMode.GRID:
            font_size = 32
        else:
            font_size = 20
        
        font = QFont("Apple Color Emoji", font_size)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        
        return QIcon(pixmap)
    
    def format_size(self, size: int) -> str:
        """Dosya boyutunu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def show_error(self, message: str):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)
    
    def show_status(self, message: str):
        """Durum mesajı göster"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
        logger.info(message)
    
    def keyPressEvent(self, event):
        """Klavye olayları - geliştirilmiş"""
        if event.key() == Qt.Key.Key_F5:
            self.refresh()
        elif event.key() == Qt.Key.Key_Delete:
            if self.selected_files:
                self.delete_files(self.selected_files)
        elif event.key() == Qt.Key.Key_F2:
            if len(self.selected_files) == 1:
                self.rename_file(self.selected_files[0])
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if len(self.selected_files) == 1:
                self.open_file(self.selected_files[0])
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                if self.selected_files:
                    self.copy_files(self.selected_files)
            elif event.key() == Qt.Key.Key_X:
                if self.selected_files:
                    self.cut_files(self.selected_files)
            elif event.key() == Qt.Key.Key_V:
                self.paste_files(str(self.current_path))
            elif event.key() == Qt.Key.Key_A:
                self.file_list.selectAll()
            elif event.key() == Qt.Key.Key_N:
                self.create_new_file()
            elif event.key() == Qt.Key.Key_T:
                self.create_new_tab()
            elif event.key() == Qt.Key.Key_W:
                # Sekme kapat
                current_index = self.tab_widget.currentIndex()
                if self.tab_widget.count() > 1:
                    self.tab_widget.close_tab(current_index)
        elif event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            if event.key() == Qt.Key.Key_N:
                self.create_new_folder()
        
        super().keyPressEvent(event)

    def cut_files(self, file_paths: List[str]):
        """Dosyaları kes - geliştirilmiş"""
        if not file_paths:
            return
        
        # Önce kopyala
        self.copy_files(file_paths)
        
        # Kesilen dosyaları işaretle (daha sonra taşınacak)
        self.cut_files_list = file_paths.copy()
        self.show_status(f"{len(file_paths)} öğe kesildi")
        
        # Kesilen dosyaları görsel olarak işaretle
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path in file_paths:
                # Kesilen dosyaları soluk göster
                item.setForeground(QColor(128, 128, 128))
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
        
        logger.info(f"Cut {len(file_paths)} files")

    def delete_selected_files(self):
        """Seçili dosyaları sil"""
        try:
            if not self.selected_files:
                self.show_status("Silinecek dosya seçilmedi")
                return
            
            # Onay al
            reply = QMessageBox.question(
                self, 
                "Dosya Silme Onayı",
                f"{len(self.selected_files)} dosya silinecek. Emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_files(self.selected_files)
        except Exception as e:
            self.show_error(f"Dosya silme hatası: {e}")
            logger.error(f"delete_selected_files error: {e}")

    # ====== FilePicker Entegrasyon Metodları ======
    
    def import_with_filepicker(self):
        """FilePicker ile dosya/klasör içe aktar"""
        if not self._filepicker_available:
            self.show_error("FilePicker mevcut değil")
            return
        
        try:
            from cloud.filepicker import open_file_dialog, select_directory_dialog, FilePickerFilter
            
            # İçe aktarma türünü sor
            options = ["📄 Dosya", "📁 Klasör"]
            choice, ok = QInputDialog.getItem(
                self, "İçe Aktarma Türü", "Ne içe aktarmak istiyorsunuz?",
                options, 0, False
            )
            
            if not ok:
                return
            
            if choice == "📄 Dosya":
                # Dosya seç
                file_path = open_file_dialog(
                    app_id="cloud_files",
                    filters=[FilePickerFilter.ALL_FILES],
                    parent=self,
                    kernel=self.kernel
                )
                
                if file_path:
                    self._import_file_to_current_dir(file_path)
                    
            elif choice == "📁 Klasör":
                # Klasör seç
                dir_path = select_directory_dialog(
                    app_id="cloud_files",
                    parent=self,
                    kernel=self.kernel
                )
                
                if dir_path:
                    self._import_directory_to_current_dir(dir_path)
            
        except Exception as e:
            self.show_error(f"İçe aktarma hatası: {e}")
            logger.error(f"import_with_filepicker error: {e}")
    
    def export_with_filepicker(self):
        """FilePicker ile seçili dosyaları dışa aktar"""
        if not self._filepicker_available:
            self.show_error("FilePicker mevcut değil")
            return
        
        if not self.selected_files:
            self.show_error("Dışa aktarılacak dosya seçilmedi")
            return
        
        try:
            from cloud.filepicker import select_directory_dialog
            
            # Hedef klasör seç
            target_dir = select_directory_dialog(
                app_id="cloud_files",
                parent=self,
                kernel=self.kernel
            )
            
            if target_dir:
                self._export_files_to_directory(self.selected_files, target_dir)
            
        except Exception as e:
            self.show_error(f"Dışa aktarma hatası: {e}")
            logger.error(f"export_with_filepicker error: {e}")
    
    def multi_import_with_filepicker(self):
        """FilePicker ile çoklu dosya içe aktar"""
        if not self._filepicker_available:
            self.show_error("FilePicker mevcut değil")
            return
        
        try:
            from cloud.filepicker import select_multiple_files_dialog, FilePickerFilter
            
            # Çoklu dosya seç
            file_paths = select_multiple_files_dialog(
                app_id="cloud_files",
                filters=[FilePickerFilter.ALL_FILES, FilePickerFilter.TEXT_FILES, FilePickerFilter.IMAGES],
                parent=self,
                kernel=self.kernel
            )
            
            if file_paths:
                for file_path in file_paths:
                    self._import_file_to_current_dir(file_path)
                
                self.show_status(f"{len(file_paths)} dosya içe aktarıldı")
            
        except Exception as e:
            self.show_error(f"Çoklu içe aktarma hatası: {e}")
            logger.error(f"multi_import_with_filepicker error: {e}")
    
    def _import_file_to_current_dir(self, source_path: str):
        """Dosyayı mevcut dizine kopyala"""
        try:
            source = Path(source_path)
            if not source.exists():
                self.show_error(f"Kaynak dosya bulunamadı: {source_path}")
                return
            
            # Hedef yol
            target_name = source.name
            target_path = self.current_path / target_name
            
            # Aynı isimde dosya varsa yeni isim üret
            counter = 1
            original_stem = source.stem
            original_suffix = source.suffix
            
            while target_path.exists():
                target_name = f"{original_stem} ({counter}){original_suffix}"
                target_path = self.current_path / target_name
                counter += 1
            
            # VFS entegre kopyalama
            if self.fs and self.vfs:
                # VFS ile kopyala
                vfs_source = self._path_to_vfs_path(source_path)
                vfs_target = str(target_path)
                
                # Kaynak dosyayı oku
                content = self.fs.read_file(vfs_source)
                if content is not None:
                    # Hedef dosyaya yaz
                    success = self.fs.write_file(vfs_target, content, owner="cloud_files")
                    if success:
                        self.show_status(f"Dosya kopyalandı: {target_name}")
                        self.populate_file_list()
                    else:
                        self.show_error(f"Dosya kopyalama başarısız: {target_name}")
                else:
                    self.show_error(f"Kaynak dosya okunamadı: {source.name}")
            else:
                # Normal kopyalama
                import shutil
                shutil.copy2(source, target_path)
                self.show_status(f"Dosya kopyalandı: {target_name}")
                self.populate_file_list()
                
        except Exception as e:
            self.show_error(f"Dosya kopyalama hatası: {e}")
            logger.error(f"_import_file_to_current_dir error: {e}")
    
    def _import_directory_to_current_dir(self, source_path: str):
        """Klasörü mevcut dizine kopyala"""
        try:
            source = Path(source_path)
            if not source.exists() or not source.is_dir():
                self.show_error(f"Kaynak klasör bulunamadı: {source_path}")
                return
            
            # Hedef yol
            target_name = source.name
            target_path = self.current_path / target_name
            
            # Aynı isimde klasör varsa yeni isim üret
            counter = 1
            original_name = source.name
            
            while target_path.exists():
                target_name = f"{original_name} ({counter})"
                target_path = self.current_path / target_name
                counter += 1
            
            # Klasörü kopyala
            import shutil
            shutil.copytree(source, target_path)
            
            self.show_status(f"Klasör kopyalandı: {target_name}")
            self.populate_file_list()
                
        except Exception as e:
            self.show_error(f"Klasör kopyalama hatası: {e}")
            logger.error(f"_import_directory_to_current_dir error: {e}")
    
    def _export_files_to_directory(self, file_paths: List[str], target_dir: str):
        """Dosyaları hedef dizine kopyala"""
        try:
            target_directory = Path(target_dir)
            if not target_directory.exists():
                target_directory.mkdir(parents=True)
            
            exported_count = 0
            
            for file_path in file_paths:
                source = Path(file_path)
                if not source.exists():
                    continue
                
                target = target_directory / source.name
                
                # Aynı isimde dosya varsa yeni isim üret
                counter = 1
                original_stem = source.stem
                original_suffix = source.suffix
                
                while target.exists():
                    target_name = f"{original_stem} ({counter}){original_suffix}"
                    target = target_directory / target_name
                    counter += 1
                
                # Dosyayı kopyala
                if source.is_file():
                    import shutil
                    shutil.copy2(source, target)
                    exported_count += 1
                elif source.is_dir():
                    import shutil
                    shutil.copytree(source, target)
                    exported_count += 1
            
            self.show_status(f"{exported_count} öğe dışa aktarıldı")
                
        except Exception as e:
            self.show_error(f"Dışa aktarma hatası: {e}")
            logger.error(f"_export_files_to_directory error: {e}")
    
    def _path_to_vfs_path(self, real_path: str) -> str:
        """Gerçek dosya yolunu VFS yoluna çevir"""
        try:
            # Basit bir dönüşüm - gerçek hayatta daha karmaşık olabilir
            path = Path(real_path)
            
            # pycloud_fs kökünden başlayan yolları VFS yoluna çevir
            if "pycloud_fs" in str(path):
                parts = path.parts
                vfs_parts = []
                start_collecting = False
                
                for part in parts:
                    if part == "pycloud_fs":
                        start_collecting = True
                        continue
                    if start_collecting:
                        vfs_parts.append(part)
                
                if vfs_parts:
                    return "/" + "/".join(vfs_parts)
            
            # Fallback - dosya adını koru
            return f"/temp/{path.name}"
                
        except Exception as e:
            logger.error(f"Path conversion error: {e}")
            return f"/temp/{Path(real_path).name}"

class CloudFiles(QMainWindow):
    """Modern Mac Finder benzeri dosya yöneticisi"""
    
    def __init__(self):
        super().__init__()
        self.current_path = Path("pycloud_fs/home")  # Basitleştirilmiş yol - doğrudan home
        self.history = []
        self.history_index = -1
        self.selected_files = []
        self.copied_files = []  # Kopyalanan dosyalar
        self.cut_files_list = []  # Kesilen dosyalar
        self.dark_mode = False
        
        # VFS API referansları
        self.fs = None
        self.vfs = None
        self.kernel = None
        self.bridge_client = None
        
        # VFS entegrasyonu kurulumu
        self.setup_fs_integration()
        
        # UI kurulumu
        self.setup_ui()
        self.setup_connections()
        self.navigate_to_path(self.current_path)
        
        # Pencere ayarları
        self.setWindowTitle("Cloud Files")
        self.setWindowIcon(QIcon("assets/icons/files.png"))
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
    
    def setup_fs_integration(self):
        """FS API ve VFS entegrasyonu kurulumu"""
        try:
            # Bridge IPC client ile bağlan
            from core.bridge import BridgeIPCClient
            
            self.bridge_client = BridgeIPCClient()
            self.kernel = self.bridge_client.get_kernel_reference()
            
            if self.kernel:
                # VFS modülünü al
                self.vfs = self.kernel.get_module('vfs')
                self.fs = self.kernel.get_module('fs')
                
                if self.vfs:
                    # Cloud Files için app profili oluştur (varsa güncelle)
                    profile_success, profile_result = self.bridge_client.call_module_method(
                        'vfs', 'get_app_profile', 'cloud_files'
                    )
                    
                    if not profile_success:
                        # Profil yoksa oluştur
                        create_success, create_result = self.bridge_client.call_module_method(
                            'vfs', 'create_app_profile',
                            'cloud_files',
                            ['/home', '/apps', '/system', '/temp'],  # allowed_mounts
                            {
                                '/home': ['read', 'write', 'delete'],
                                '/apps': ['read'],
                                '/system': ['read'], 
                                '/temp': ['read', 'write', 'delete']
                            },  # permissions
                            True,  # sandbox_mode
                            'Dosya yöneticisi - tam sistem erişimi'  # description
                        )
                        
                        if create_success:
                            logger.info("✅ Cloud Files VFS profili oluşturuldu")
                        else:
                            logger.warning(f"⚠️ VFS profili oluşturulamadı: {create_result}")
                    else:
                        logger.info("✅ Cloud Files VFS profili mevcut")
                    
                    # VFS base path'i al
                    mount_success, mount_info = self.bridge_client.call_module_method(
                        'vfs', 'get_mount_info'
                    )
                    
                    if mount_success and mount_info:
                        # Mount noktalarını logla
                        logger.info(f"📁 VFS Mount Points: {mount_info.get('mount_points', [])}")
                        
                        # Default path'i VFS'e göre ayarla
                        home_success, home_path = self.bridge_client.call_module_method(
                            'vfs', 'resolve_path', '/home'
                        )
                        
                        if home_success and home_path:
                            # VFS'den aldığımız gerçek path'i kullan
                            resolved_path = Path(home_path)
                            if resolved_path.exists():
                                self.current_path = resolved_path
                                logger.info(f"📂 VFS Home path: {resolved_path}")
                            else:
                                # Fallback - mevcut sistem
                                logger.warning(f"⚠️ VFS path mevcut değil: {resolved_path}")
                                self.current_path = Path("pycloud_fs/home")
                        else:
                            logger.warning("⚠️ VFS home path çözümlenemedi")
                            self.current_path = Path("pycloud_fs/home")
                    
                    logger.info("✅ Cloud Files VFS entegrasyonu başarılı")
                else:
                    logger.warning("⚠️ VFS modülü bulunamadı")
                    self.current_path = Path("pycloud_fs/home")
                    
            else:
                logger.warning("⚠️ Kernel referansı alınamadı")
                self.current_path = Path("pycloud_fs/home")
                
        except ImportError:
            logger.warning("⚠️ Bridge modülü bulunamadı - VFS entegrasyonu devre dışı")
            self.kernel = None
            self.vfs = None
            self.fs = None
            self.bridge_client = None
            self.current_path = Path("pycloud_fs/home")
        except Exception as e:
            logger.error(f"❌ VFS entegrasyon hatası: {e}")
            self.kernel = None
            self.vfs = None
            self.fs = None
            self.bridge_client = None
            self.current_path = Path("pycloud_fs/home")
    
    def setup_ui(self):
        """Modern arayüz kurulumu"""
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout - Mac Finder benzeri
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sol panel - Sidebar
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Sağ panel - Ana içerik
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Toolbar
        self.setup_toolbar()
        right_layout.addWidget(self.toolbar)
        
        # Dosya listesi
        self.setup_file_list()
        right_layout.addWidget(self.file_list)
        
        # Status bar
        self.setup_status_bar()
        right_layout.addWidget(self.status_bar)
        
        main_layout.addWidget(right_panel, 1)  # Esnek genişlik
        
        # Tema uygula
        self.apply_theme()
    
    def setup_sidebar(self):
        """Mac Finder benzeri kenar çubuğu"""
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Kişisel klasörler - pycloud_fs/home altında
        favorites = [
            ("🏠", "Home", "pycloud_fs/home"),
            ("🖥️", "Desktop", "pycloud_fs/home/Desktop"),
            ("📄", "Documents", "pycloud_fs/home/Documents"),
            ("⬇️", "Downloads", "pycloud_fs/home/Downloads"),
            ("🎬", "Videos", "pycloud_fs/home/Videos"),
            ("📸", "Photos", "pycloud_fs/home/Photos"),
            ("💼", "Projects", "pycloud_fs/home/Projects")
        ]
        
        # Başlık ekle
        header_item = QListWidgetItem("KİŞİSEL")
        header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        header_item.setData(Qt.ItemDataRole.UserRole, None)
        header_font = header_item.font()
        header_font.setPointSize(11)
        header_font.setBold(True)
        header_item.setFont(header_font)
        header_item.setForeground(QColor(120, 120, 120))
        self.sidebar.addItem(header_item)
        
        for icon, name, path in favorites:
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.ItemDataRole.UserRole, (path, name))
            self.sidebar.addItem(item)
        
        # Boşluk
        spacer = QListWidgetItem("")
        spacer.setFlags(spacer.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        spacer.setData(Qt.ItemDataRole.UserRole, None)
        self.sidebar.addItem(spacer)
        
        # Sistem bölümü - Ana dizin
        system_header = QListWidgetItem("SİSTEM")
        system_header.setFlags(system_header.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        system_header.setData(Qt.ItemDataRole.UserRole, None)
        system_font = system_header.font()
        system_font.setPointSize(11)
        system_font.setBold(True)
        system_header.setFont(system_font)
        system_header.setForeground(QColor(120, 120, 120))
        self.sidebar.addItem(system_header)
        
        # Sistem klasörleri - Ana dizindeki gerçek klasörlerle eşleştir
        system_items = [
            ("📱", "Applications", "apps"),
            ("⚙️", "System", "system"),
            ("🗂️", "Temporary", "temp")
        ]
        
        for icon, name, path in system_items:
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.ItemDataRole.UserRole, (path, name))
            self.sidebar.addItem(item)
    
    def setup_toolbar(self):
        """Modern toolbar"""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        
        # Navigasyon butonları
        self.back_btn = self.toolbar.addAction("◀")
        self.back_btn.setToolTip("Geri")
        self.back_btn.setEnabled(False)
        
        self.forward_btn = self.toolbar.addAction("▶")
        self.forward_btn.setToolTip("İleri")
        self.forward_btn.setEnabled(False)
        
        self.toolbar.addSeparator()
        
        # Yol çubuğu
        self.path_label = QLabel("Home")
        self.path_label.setStyleSheet("""
            QLabel {
                padding: 6px 12px;
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 6px;
                font-weight: bold;
                color: #333;
            }
        """)
        self.toolbar.addWidget(self.path_label)
        
        # Esnek boşluk
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Arama
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Ara...")
        self.search_box.setFixedWidth(200)
        self.toolbar.addWidget(self.search_box)
        
        self.toolbar.addSeparator()
        
        # Görünüm butonları
        self.icon_view_btn = self.toolbar.addAction("⊞")
        self.icon_view_btn.setToolTip("Icon Görünümü")
        self.icon_view_btn.setCheckable(True)
        self.icon_view_btn.setChecked(False)  # Başlangıçta kapalı
        
        self.list_view_btn = self.toolbar.addAction("☰")
        self.list_view_btn.setToolTip("Liste Görünümü")
        self.list_view_btn.setCheckable(True)
        self.list_view_btn.setChecked(True)  # Başlangıçta açık
    
    def setup_file_list(self):
        """Dosya listesi kurulumu"""
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setViewMode(QListView.ViewMode.ListMode)  # Başlangıçta liste görünümü
        
        # Liste görünümü için optimize edilmiş boyutlar
        self.file_list.setIconSize(QSize(24, 24))   # Liste için ideal ikon boyutu
        self.file_list.setSpacing(0)  # Minimum spacing - neredeyse hiç boşluk
        self.file_list.setAlternatingRowColors(True)  # Alternatif satır renkleri
        
        self.file_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.file_list.setMovement(QListView.Movement.Static)
        self.file_list.setWordWrap(False)  # Liste görünümünde word wrap kapalı
        self.file_list.setFrameStyle(QFrame.Shape.NoFrame)
    
    def setup_status_bar(self):
        """Status bar kurulumu"""
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Hazır")
        self.selection_label = QLabel("")
        
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.selection_label)
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        # Sidebar
        self.sidebar.itemClicked.connect(self.on_sidebar_clicked)
        
        # Toolbar
        self.back_btn.triggered.connect(self.go_back)
        self.forward_btn.triggered.connect(self.go_forward)
        self.icon_view_btn.triggered.connect(lambda: self.set_view_mode('icon'))
        self.list_view_btn.triggered.connect(lambda: self.set_view_mode('list'))
        
        # File list
        self.file_list.itemDoubleClicked.connect(self.on_file_double_click)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Arama
        self.search_box.textChanged.connect(self.filter_files)
    
    def apply_theme(self):
        """Modern tema uygula"""
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_light_theme(self):
        """Açık tema"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f6f6f6;
            }
            
            QListWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: none;
                outline: none;
                font-size: 13px;
                alternate-background-color: rgba(248, 248, 248, 0.8);
            }
            
            QListWidget::item {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                margin: 1px 2px;
                color: #333333;
                min-height: 20px;
            }
            
            QListWidget::item:selected {
                background-color: rgba(0, 122, 255, 0.2);
                color: #007AFF;
                border: 1px solid rgba(0, 122, 255, 0.4);
            }
            
            QListWidget::item:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            
            QListWidget::item:alternate {
                background-color: rgba(248, 248, 248, 0.5);
            }
            
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(251, 251, 251, 0.95),
                    stop:1 rgba(238, 238, 238, 0.95));
                border: none;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                padding: 8px;
                spacing: 12px;
            }
            
            QToolButton {
                border: none;
                border-radius: 6px;
                padding: 6px;
                background-color: transparent;
                color: #333333;
            }
            
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            QToolButton:checked {
                background-color: rgba(0, 122, 255, 0.2);
                color: #007AFF;
            }
            
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 0.2);
                border-radius: 6px;
                padding: 6px 12px;
                background-color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border: 2px solid rgba(0, 122, 255, 0.6);
                background-color: white;
            }
            
            QStatusBar {
                background-color: rgba(246, 246, 246, 0.9);
                border-top: 1px solid rgba(0, 0, 0, 0.1);
                padding: 4px;
            }
        """)
    
    def apply_dark_theme(self):
        """Koyu tema"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            
            QListWidget {
                background-color: rgba(40, 40, 40, 0.95);
                border: none;
                outline: none;
                color: #ffffff;
                font-size: 13px;
                alternate-background-color: rgba(50, 50, 50, 0.8);
            }
            
            QListWidget::item {
                padding: 10px 16px;
                border: none;
                border-radius: 6px;
                margin: 2px 4px;
                color: #ffffff;
                min-height: 24px;
            }
            
            QListWidget::item:selected {
                background-color: rgba(0, 122, 255, 0.3);
                color: #007AFF;
                border: 1px solid rgba(0, 122, 255, 0.5);
            }
            
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            QListWidget::item:alternate {
                background-color: rgba(50, 50, 50, 0.5);
            }
            
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(55, 55, 55, 0.95),
                    stop:1 rgba(40, 40, 40, 0.95));
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 8px;
                spacing: 12px;
            }
            
            QToolButton {
                border: none;
                border-radius: 6px;
                padding: 6px;
                background-color: transparent;
                color: #ffffff;
            }
            
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            QToolButton:checked {
                background-color: rgba(0, 122, 255, 0.3);
                color: #007AFF;
            }
            
            QLineEdit {
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 6px 12px;
                background-color: rgba(60, 60, 60, 0.9);
                color: #ffffff;
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border: 2px solid rgba(0, 122, 255, 0.8);
                background-color: rgba(40, 40, 40, 1.0);
            }
            
            QStatusBar {
                background-color: rgba(45, 45, 45, 0.9);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                color: #ffffff;
                padding: 4px;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)
    
    def navigate_to_path(self, path: Path):
        """Belirtilen yola git - VFS entegreli"""
        try:
            logger.info(f"🧭 Navigating to path: {path}")
            
            # VFS path doğrulaması
            if self.vfs and self.bridge_client:
                # VFS üzerinden path'i doğrula
                vfs_path = self._real_path_to_vfs_path(str(path))
                logger.info(f"🔄 VFS path conversion: {path} -> {vfs_path}")
                
                validate_success, is_valid = self.bridge_client.call_module_method(
                    'vfs', 'validate_path', vfs_path
                )
                
                if validate_success and is_valid:
                    # VFS'den gerçek path'i al
                    resolve_success, resolved_path = self.bridge_client.call_module_method(
                        'vfs', 'resolve_path', vfs_path
                    )
                    
                    if resolve_success and resolved_path:
                        actual_path = Path(resolved_path)
                        if actual_path.exists():
                            self.current_path = actual_path
                            logger.info(f"📂 VFS navigated to: {vfs_path} -> {actual_path}")
                        else:
                            logger.warning(f"⚠️ VFS resolved path does not exist: {actual_path}")
                            # VFS path mevcut değilse fallback'e geç
                            logger.info(f"🔄 VFS path not found, falling back to direct navigation")
                            self._navigate_fallback(path)
                            return
                    else:
                        logger.warning(f"⚠️ VFS path resolution failed: {vfs_path}")
                        # VFS resolution başarısızsa fallback'e geç
                        logger.info(f"🔄 VFS resolution failed, falling back to direct navigation")
                        self._navigate_fallback(path)
                        return
                else:
                    logger.warning(f"⚠️ VFS path validation failed: {vfs_path}")
                    # VFS validation başarısızsa fallback'e geç
                    logger.info(f"🔄 VFS validation failed, falling back to direct navigation")
                    self._navigate_fallback(path)
                    return
            else:
                # VFS mevcut değilse fallback kullan
                logger.info(f"🔄 VFS not available, using fallback navigation")
                self._navigate_fallback(path)
                return
            
            # UI güncellemeleri
            self.update_path_label()
            self.populate_file_list()
            self.add_to_history(self.current_path)
            self.update_navigation_buttons()
            
            logger.info(f"🎯 Navigation completed to: {self.current_path}")
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            import traceback
            logger.error(f"❌ Navigation traceback: {traceback.format_exc()}")
            self.show_error(f"Gezinme hatası: {e}")
    
    def _navigate_fallback(self, path: Path):
        """Fallback navigasyon - VFS olmadan doğrudan dosya sistemi"""
        try:
            logger.info(f"🔄 Using fallback navigation for: {path}")
            
            # Path'in varlığını kontrol et
            if not path.exists():
                logger.warning(f"⚠️ Path does not exist: {path}")
                self.show_error(f"Yol bulunamadı: {path}")
                return
            
            # Path'in dizin olduğunu kontrol et
            if not path.is_dir():
                logger.warning(f"⚠️ Path is not a directory: {path}")
                self.show_error(f"Yol bir dizin değil: {path}")
                return
            
            # Başarılı - path'i ayarla
            self.current_path = path
            logger.info(f"✅ Successfully navigated to: {path}")
            
            # UI güncellemeleri
            self.update_path_label()
            self.populate_file_list()
            self.add_to_history(self.current_path)
            self.update_navigation_buttons()
            
            logger.info(f"🎯 Fallback navigation completed to: {self.current_path}")
            
        except Exception as e:
            logger.error(f"❌ Fallback navigation error: {e}")
            self.show_error(f"Fallback gezinme hatası: {e}")
    
    def _real_path_to_vfs_path(self, real_path: str) -> str:
        """Gerçek dosya yolunu VFS yoluna çevir"""
        try:
            path_obj = Path(real_path)
            path_str = str(path_obj)
            
            # Sistem klasörleri için özel işlem
            if path_str in ['apps', 'system', 'temp']:
                return f"/{path_str}"
            
            # pycloud_fs kısmını VFS path'ine çevir
            if "pycloud_fs" in path_str:
                parts = path_obj.parts
                vfs_parts = []
                start_collecting = False
                
                for part in parts:
                    if part == "pycloud_fs":
                        start_collecting = True
                        continue
                    if start_collecting:
                        vfs_parts.append(part)
                
                if vfs_parts:
                    vfs_path = "/" + "/".join(vfs_parts)
                    # /home/default -> /home olarak düzenle
                    if vfs_path.startswith("/home/default"):
                        vfs_path = vfs_path.replace("/home/default", "/home")
                    return vfs_path
            
            # Absolute path ise doğrudan kullan
            if path_str.startswith("/"):
                return path_str
                
            # Relative path'leri kontrol et
            # Eğer sistem klasörlerinden biriyse doğrudan VFS root'a ekle
            if path_str in ['apps', 'system', 'temp']:
                return f"/{path_str}"
            else:
                # Diğer relative path'leri /home'a ekle
                return f"/home/{path_str}"
                
        except Exception as e:
            logger.error(f"Path conversion error: {e}")
            # Fallback - sistem klasörleri için özel kontrol
            if real_path in ['apps', 'system', 'temp']:
                return f"/{real_path}"
            return f"/home/{Path(real_path).name}"
    
    def update_path_label(self):
        """Yol etiketini güncelle"""
        try:
            # Yol gösterimini güzelleştir
            path_parts = self.current_path.parts
            if "pycloud_fs" in path_parts:
                # PyCloud OS yolu göster
                start_index = path_parts.index("pycloud_fs") + 1
                display_parts = path_parts[start_index:]
                
                if not display_parts:
                    display_path = "Root"
                elif display_parts == ("home", "default"):
                    display_path = "Home"
                elif len(display_parts) > 2 and display_parts[:2] == ("home", "default"):
                    display_path = " > ".join(display_parts[2:])
                else:
                    display_path = " > ".join(display_parts)
            else:
                display_path = str(self.current_path.name)
            
            self.path_label.setText(display_path)
            
        except Exception as e:
            self.path_label.setText(str(self.current_path.name))
    
    def populate_file_list(self):
        """Dosya listesini doldur"""
        try:
            self.file_list.clear()
            
            if not self.current_path.exists():
                self.show_error("Dizin bulunamadı")
                return
            
            # Dosya ve klasörleri al
            items = list(self.current_path.iterdir())
            
            # Sırala: önce klasörler, sonra dosyalar
            folders = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            folders.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())
            
            # Klasörleri ekle
            for folder in folders:
                if folder.name.startswith('.'):
                    continue  # Gizli klasörleri atla
                
                # Görünüm moduna göre isim formatı
                current_view = self.file_list.viewMode()
                if current_view == QListView.ViewMode.IconMode:
                    # Grid view için daha uzun isimlere izin ver
                    display_name = folder.name
                    if len(display_name) > 18:  # Klasörler için biraz daha kısa
                        display_name = display_name[:15] + "..."
                else:
                    # Liste view için tam ismi göster
                    display_name = folder.name
                    if len(display_name) > 50:  # Liste'de çok uzun isimleri kısalt
                        display_name = display_name[:47] + "..."
                
                item = QListWidgetItem(f"📁 {display_name}")
                item.setData(Qt.ItemDataRole.UserRole, str(folder))
                item.setToolTip(f"Klasör: {folder.name}")  # Tam isim tooltip'te
                self.file_list.addItem(item)
            
            # Dosyaları ekle
            for file in files:
                if file.name.startswith('.'):
                    continue  # Gizli dosyaları atla
                
                icon = self.get_file_icon(file)
                
                # Görünüm moduna göre isim formatı
                current_view = self.file_list.viewMode()
                if current_view == QListView.ViewMode.IconMode:
                    # Grid view için daha uzun isimlere izin ver
                    display_name = file.name
                    if len(display_name) > 20:  # Artık 20 karaktere kadar
                        name_parts = display_name.rsplit('.', 1)
                        if len(name_parts) == 2:
                            name, ext = name_parts
                            if len(name) > 15:
                                display_name = name[:15] + "..." + "." + ext
                        else:
                            display_name = display_name[:17] + "..."
                else:
                    # Liste view için tam ismi göster (çok uzunsa kısalt)
                    display_name = file.name
                    if len(display_name) > 50:  # Liste'de çok uzun isimleri kısalt
                        display_name = display_name[:47] + "..."
                
                item = QListWidgetItem(f"{icon} {display_name}")
                item.setData(Qt.ItemDataRole.UserRole, str(file))
                
                # Dosya bilgisi tooltip
                try:
                    size = file.stat().st_size
                    size_str = self.format_size(size)
                    modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%d.%m.%Y %H:%M")
                    item.setToolTip(f"Dosya: {file.name}\nBoyut: {size_str}\nDeğiştirilme: {modified}")
                except:
                    item.setToolTip(f"Dosya: {file.name}")  # Tam isim tooltip'te
                
                self.file_list.addItem(item)
            
            # Durum güncellemesi
            folder_count = len(folders)
            file_count = len(files)
            self.status_label.setText(f"{folder_count} klasör, {file_count} dosya")
            
        except Exception as e:
            self.show_error(f"Dosya listesi yüklenemedi: {e}")
            logger.error(f"populate_file_list error: {e}")
    
    def get_file_icon(self, file_path: Path) -> str:
        """Dosya türüne göre emoji ikonu döndür"""
        suffix = file_path.suffix.lower()
        
        icon_map = {
            '.txt': '📄',
            '.md': '📝',
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📊',
            '.xml': '📋',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.svg': '🎨',
            '.pdf': '📕',
            '.doc': '📘',
            '.docx': '📘',
            '.xls': '📗',
            '.xlsx': '📗',
            '.ppt': '📙',
            '.pptx': '📙',
            '.zip': '📦',
            '.rar': '📦',
            '.7z': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.mp3': '🎵',
            '.wav': '🎵',
            '.flac': '🎵',
            '.m4a': '🎵',
            '.mp4': '🎬',
            '.avi': '🎬',
            '.mkv': '🎬',
            '.mov': '🎬',
            '.app': '📱'
        }
        
        return icon_map.get(suffix, '📄')
    
    def format_size(self, size: int) -> str:
        """Dosya boyutunu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def show_error(self, message: str):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "Hata", message)
    
    def show_status(self, message: str):
        """Durum mesajı göster"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
        logger.info(message)
    
    def keyPressEvent(self, event):
        """Klavye olayları - geliştirilmiş"""
        if event.key() == Qt.Key.Key_F5:
            self.refresh()
        elif event.key() == Qt.Key.Key_Delete:
            if self.selected_files:
                self.delete_files(self.selected_files)
        elif event.key() == Qt.Key.Key_F2:
            if len(self.selected_files) == 1:
                self.rename_file(self.selected_files[0])
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if len(self.selected_files) == 1:
                self.open_file(self.selected_files[0])
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                if self.selected_files:
                    self.copy_files(self.selected_files)
            elif event.key() == Qt.Key.Key_X:
                if self.selected_files:
                    self.cut_files(self.selected_files)
            elif event.key() == Qt.Key.Key_V:
                self.paste_files(str(self.current_path))
            elif event.key() == Qt.Key.Key_A:
                self.file_list.selectAll()
            elif event.key() == Qt.Key.Key_N:
                self.create_new_file()
            elif event.key() == Qt.Key.Key_T:
                self.create_new_tab()
            elif event.key() == Qt.Key.Key_W:
                # Sekme kapat
                current_index = self.tab_widget.currentIndex()
                if self.tab_widget.count() > 1:
                    self.tab_widget.close_tab(current_index)
        elif event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            if event.key() == Qt.Key.Key_N:
                self.create_new_folder()
        
        super().keyPressEvent(event)

    def cut_files(self, file_paths: List[str]):
        """Dosyaları kes - geliştirilmiş"""
        if not file_paths:
            return
        
        # Önce kopyala
        self.copy_files(file_paths)
        
        # Kesilen dosyaları işaretle (daha sonra taşınacak)
        self.cut_files_list = file_paths.copy()
        self.show_status(f"{len(file_paths)} öğe kesildi")
        
        # Kesilen dosyaları görsel olarak işaretle
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path in file_paths:
                # Kesilen dosyaları soluk göster
                item.setForeground(QColor(128, 128, 128))
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
        
        logger.info(f"Cut {len(file_paths)} files")

    def delete_selected_files(self):
        """Seçili dosyaları sil"""
        try:
            if not self.selected_files:
                self.show_status("Silinecek dosya seçilmedi")
                return
            
            # Onay al
            reply = QMessageBox.question(
                self, 
                "Dosya Silme Onayı",
                f"{len(self.selected_files)} dosya silinecek. Emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_files(self.selected_files)
        except Exception as e:
            self.show_error(f"Dosya silme hatası: {e}")
            logger.error(f"delete_selected_files error: {e}")

    # ====== FilePicker Entegrasyon Metodları ======
    
    def import_with_filepicker(self):
        """FilePicker ile dosya/klasör içe aktar"""
        if not self._filepicker_available:
            self.show_error("FilePicker mevcut değil")
            return
        
        try:
            from cloud.filepicker import open_file_dialog, select_directory_dialog, FilePickerFilter
            
            # İçe aktarma türünü sor
            options = ["📄 Dosya", "📁 Klasör"]
            choice, ok = QInputDialog.getItem(
                self, "İçe Aktarma Türü", "Ne içe aktarmak istiyorsunuz?",
                options, 0, False
            )
            
            if not ok:
                return
            
            if choice == "📄 Dosya":
                # Dosya seç
                file_path = open_file_dialog(
                    app_id="cloud_files",
                    filters=[FilePickerFilter.ALL_FILES],
                    parent=self,
                    kernel=self.kernel
                )
                
                if file_path:
                    self._import_file_to_current_dir(file_path)
                    
            elif choice == "📁 Klasör":
                # Klasör seç
                dir_path = select_directory_dialog(
                    app_id="cloud_files",
                    parent=self,
                    kernel=self.kernel
                )
                
                if dir_path:
                    self._import_directory_to_current_dir(dir_path)
            
        except Exception as e:
            self.show_error(f"İçe aktarma hatası: {e}")
            logger.error(f"import_with_filepicker error: {e}")
    
    def export_with_filepicker(self):
        """FilePicker ile seçili dosyaları dışa aktar"""
        if not self._filepicker_available:
            self.show_error("FilePicker mevcut değil")
            return
        
        if not self.selected_files:
            self.show_error("Dışa aktarılacak dosya seçilmedi")
            return
        
        try:
            from cloud.filepicker import select_directory_dialog
            
            # Hedef klasör seç
            target_dir = select_directory_dialog(
                app_id="cloud_files",
                parent=self,
                kernel=self.kernel
            )
            
            if target_dir:
                self._export_files_to_directory(self.selected_files, target_dir)
            
        except Exception as e:
            self.show_error(f"Dışa aktarma hatası: {e}")
            logger.error(f"export_with_filepicker error: {e}")
    
    def multi_import_with_filepicker(self):
        """FilePicker ile çoklu dosya içe aktar"""
        if not self._filepicker_available:
            self.show_error("FilePicker mevcut değil")
            return
        
        try:
            from cloud.filepicker import select_multiple_files_dialog, FilePickerFilter
            
            # Çoklu dosya seç
            file_paths = select_multiple_files_dialog(
                app_id="cloud_files",
                filters=[FilePickerFilter.ALL_FILES, FilePickerFilter.TEXT_FILES, FilePickerFilter.IMAGES],
                parent=self,
                kernel=self.kernel
            )
            
            if file_paths:
                for file_path in file_paths:
                    self._import_file_to_current_dir(file_path)
                
                self.show_status(f"{len(file_paths)} dosya içe aktarıldı")
            
        except Exception as e:
            self.show_error(f"Çoklu içe aktarma hatası: {e}")
            logger.error(f"multi_import_with_filepicker error: {e}")
    
    def _import_file_to_current_dir(self, source_path: str):
        """Dosyayı mevcut dizine kopyala"""
        try:
            source = Path(source_path)
            if not source.exists():
                self.show_error(f"Kaynak dosya bulunamadı: {source_path}")
                return
            
            # Hedef yol
            target_name = source.name
            target_path = self.current_path / target_name
            
            # Aynı isimde dosya varsa yeni isim üret
            counter = 1
            original_stem = source.stem
            original_suffix = source.suffix
            
            while target_path.exists():
                target_name = f"{original_stem} ({counter}){original_suffix}"
                target_path = self.current_path / target_name
                counter += 1
            
            # VFS entegre kopyalama
            if self.fs and self.vfs:
                # VFS ile kopyala
                vfs_source = self._path_to_vfs_path(source_path)
                vfs_target = str(target_path)
                
                # Kaynak dosyayı oku
                content = self.fs.read_file(vfs_source)
                if content is not None:
                    # Hedef dosyaya yaz
                    success = self.fs.write_file(vfs_target, content, owner="cloud_files")
                    if success:
                        self.show_status(f"Dosya kopyalandı: {target_name}")
                        self.populate_file_list()
                    else:
                        self.show_error(f"Dosya kopyalama başarısız: {target_name}")
                else:
                    self.show_error(f"Kaynak dosya okunamadı: {source.name}")
            else:
                # Normal kopyalama
                import shutil
                shutil.copy2(source, target_path)
                self.show_status(f"Dosya kopyalandı: {target_name}")
                self.populate_file_list()
                
        except Exception as e:
            self.show_error(f"Dosya kopyalama hatası: {e}")
            logger.error(f"_import_file_to_current_dir error: {e}")
    
    def _import_directory_to_current_dir(self, source_path: str):
        """Klasörü mevcut dizine kopyala"""
        try:
            source = Path(source_path)
            if not source.exists() or not source.is_dir():
                self.show_error(f"Kaynak klasör bulunamadı: {source_path}")
                return
            
            # Hedef yol
            target_name = source.name
            target_path = self.current_path / target_name
            
            # Aynı isimde klasör varsa yeni isim üret
            counter = 1
            original_name = source.name
            
            while target_path.exists():
                target_name = f"{original_name} ({counter})"
                target_path = self.current_path / target_name
                counter += 1
            
            # Klasörü kopyala
            import shutil
            shutil.copytree(source, target_path)
            
            self.show_status(f"Klasör kopyalandı: {target_name}")
            self.populate_file_list()
                
        except Exception as e:
            self.show_error(f"Klasör kopyalama hatası: {e}")
            logger.error(f"_import_directory_to_current_dir error: {e}")
    
    def _export_files_to_directory(self, file_paths: List[str], target_dir: str):
        """Dosyaları hedef dizine kopyala"""
        try:
            target_directory = Path(target_dir)
            if not target_directory.exists():
                target_directory.mkdir(parents=True)
            
            exported_count = 0
            
            for file_path in file_paths:
                source = Path(file_path)
                if not source.exists():
                    continue
                
                target = target_directory / source.name
                
                # Aynı isimde dosya varsa yeni isim üret
                counter = 1
                original_stem = source.stem
                original_suffix = source.suffix
                
                while target.exists():
                    target_name = f"{original_stem} ({counter}){original_suffix}"
                    target = target_directory / target_name
                    counter += 1
                
                # Dosyayı kopyala
                if source.is_file():
                    import shutil
                    shutil.copy2(source, target)
                    exported_count += 1
                elif source.is_dir():
                    import shutil
                    shutil.copytree(source, target)
                    exported_count += 1
            
            self.show_status(f"{exported_count} öğe dışa aktarıldı")
                
        except Exception as e:
            self.show_error(f"Dışa aktarma hatası: {e}")
            logger.error(f"_export_files_to_directory error: {e}")
    
    def _path_to_vfs_path(self, real_path: str) -> str:
        """Gerçek dosya yolunu VFS yoluna çevir"""
        try:
            # Basit bir dönüşüm - gerçek hayatta daha karmaşık olabilir
            path = Path(real_path)
            
            # pycloud_fs kökünden başlayan yolları VFS yoluna çevir
            if "pycloud_fs" in str(path):
                parts = path.parts
                vfs_parts = []
                start_collecting = False
                
                for part in parts:
                    if part == "pycloud_fs":
                        start_collecting = True
                        continue
                    if start_collecting:
                        vfs_parts.append(part)
                
                if vfs_parts:
                    return "/" + "/".join(vfs_parts)
            
            # Fallback - dosya adını koru
            return f"/temp/{path.name}"
                
        except Exception as e:
            logger.error(f"Path conversion error: {e}")
            return f"/temp/{Path(real_path).name}"

    def on_sidebar_clicked(self, item):
        """Sidebar öğesi tıklandı"""
        try:
            data = item.data(Qt.ItemDataRole.UserRole)
            logger.info(f"🖱️ Sidebar clicked: data = {data}")
            
            if data:
                # Data artık tuple format: (path, name)
                if isinstance(data, tuple) and len(data) == 2:
                    path_str, name = data
                else:
                    # Fallback - eski format
                    path_str = data
                    name = str(data)
                
                logger.info(f"📂 Navigating to: {path_str}")
                
                # Sistem klasörleri için absolute path'e çevir
                if path_str in ['apps', 'system', 'temp']:
                    # Ana dizindeki sistem klasörlerini kullan
                    base_dir = Path.cwd()  # PyCloud OS ana dizini
                    path = base_dir / path_str
                    logger.info(f"🔧 System folder converted to absolute: {path}")
                else:
                    # Diğer path'ler için normal işlem
                    path = Path(path_str)
                
                # Eğer path mevcut değilse, sadece kişisel klasörler için oluştur
                if not path.exists():
                    # Sistem klasörleri için oluşturma yapma
                    if path_str in ['apps', 'system', 'temp']:
                        logger.warning(f"⚠️ System folder not found: {path}")
                        self.show_error(f"Sistem klasörü bulunamadı: {path}")
                        return
                    else:
                        # Kişisel klasörler için oluştur
                        logger.info(f"📁 Creating missing directory: {path}")
                        try:
                            path.mkdir(parents=True, exist_ok=True)
                            logger.info(f"✅ Directory created: {path}")
                        except Exception as e:
                            logger.error(f"❌ Failed to create directory {path}: {e}")
                            self.show_error(f"Dizin oluşturulamadı: {path}")
                            return
                
                # Şimdi navigate et
                if path.exists() and path.is_dir():
                    self.navigate_to_path(path)
                else:
                    logger.warning(f"⚠️ Path not found or not a directory: {path}")
                    self.show_error(f"Dizin bulunamadı: {path}")
            else:
                logger.warning("⚠️ Sidebar item has no UserRole data")
                
        except Exception as e:
            logger.error(f"❌ Sidebar click error: {e}")
            self.show_error(f"Sidebar geçiş hatası: {e}")

    def go_back(self):
        """Geçmişte geri git"""
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.current_path = path
            self.update_path_label()
            self.populate_file_list()
            self.update_navigation_buttons()
    
    def go_forward(self):
        """Geçmişte ileri git"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.current_path = path
            self.update_path_label()
            self.populate_file_list()
            self.update_navigation_buttons()
    
    def add_to_history(self, path: Path):
        """Geçmişe path ekle"""
        # Aynı path'i arka arkaya ekleme
        if self.history and self.history[-1] == path:
            return
        
        # Geçmişten sonrasını sil (eğer ortadaysak)
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(path)
        self.history_index = len(self.history) - 1
    
    def update_navigation_buttons(self):
        """Navigasyon butonlarını güncelle"""
        self.back_btn.setEnabled(self.history_index > 0)
        self.forward_btn.setEnabled(self.history_index < len(self.history) - 1)
    
    def set_view_mode(self, mode: str):
        """Görünüm modunu ayarla"""
        if mode == 'icon':
            self.file_list.setViewMode(QListView.ViewMode.IconMode)
            # Daha büyük grid view - dosya adları için yeterli alan
            self.file_list.setGridSize(QSize(160, 120))  # Genişlik ve yükseklik artırıldı
            self.file_list.setIconSize(QSize(48, 48))    # Daha büyük ikonlar
            self.file_list.setSpacing(12)  # Grid arası daha fazla boşluk
            self.file_list.setWordWrap(True)  # Grid'de word wrap açık
            self.icon_view_btn.setChecked(True)
            self.list_view_btn.setChecked(False)
        elif mode == 'list':
            self.file_list.setViewMode(QListView.ViewMode.ListMode)
            self.file_list.setIconSize(QSize(24, 24))   # Liste için kompakt ikon
            self.file_list.setSpacing(0)  # Minimum boşluk - kompakt liste
            self.file_list.setWordWrap(False)  # Liste'de word wrap kapalı
            self.icon_view_btn.setChecked(False)
            self.list_view_btn.setChecked(True)
        
        # Listeyi yenile
        self.populate_file_list()
    
    def on_file_double_click(self, item):
        """Dosya çift tıklandı"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.open_file_or_folder(Path(file_path))
    
    def open_file_or_folder(self, path: Path):
        """Dosya veya klasörü aç"""
        if path.is_dir():
            # Klasörse içine gir
            self.navigate_to_path(path)
        else:
            # Dosyaysa uygulamayla aç
            self.open_file(path)
    
    def open_file(self, file_path: Path):
        """Dosyayı uygun uygulamayla aç - Launcher API entegreli"""
        try:
            if not file_path.exists():
                self.show_error(f"Dosya bulunamadı: {file_path}")
                return
                
            suffix = file_path.suffix.lower()
            file_path_str = str(file_path.absolute())  # Absolute path kullan
            
            logger.info(f"Opening file: {file_path_str} (suffix: {suffix})")
            
            # Launcher referansını al
            launcher = None
            if self.bridge_client:
                launcher_success, launcher_ref = self.bridge_client.call_module_method(
                    'launcher', 'get_launcher'
                )
                
                if launcher_success and launcher_ref:
                    launcher = launcher_ref
                    logger.info("✅ Launcher referansı alındı")
                else:
                    logger.warning("⚠️ Launcher referansı alınamadı")
            
            # Dosya tipine göre uygulama seç
            app_id = None
            
            if suffix in ['.txt', '.md', '.log']:
                app_id = 'cloud_notepad'
            elif suffix in ['.py', '.js', '.html', '.css', '.json']:
                app_id = 'cloud_pyide'
            elif suffix in ['.pdf', '.html', '.htm']:
                app_id = 'cloud_browser'
            
            # Launcher ile aç
            if launcher and app_id:
                try:
                    logger.info(f"🚀 Launcher ile açılıyor: {app_id} -> {file_path_str}")
                    
                    # Launcher API kullan
                    launch_success, launch_result = self.bridge_client.call_module_method(
                        'launcher', 'launch_app', app_id, open_file=file_path_str
                    )
                    
                    if launch_success:
                        self.show_status(f"'{file_path.name}' {app_id} ile açıldı")
                        logger.info(f"✅ Dosya açıldı: {file_path_str}")
                        return
                    else:
                        logger.warning(f"⚠️ Launcher açma başarısız: {launch_result}")
                
                except Exception as e:
                    logger.error(f"❌ Launcher açma hatası: {e}")
            
            # Fallback - subprocess kullan
            logger.info("🔄 Fallback: subprocess ile açılıyor")
            
            try:
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Darwin":  # macOS
                    subprocess.run(["open", file_path_str], check=True)
                elif system == "Windows":
                    subprocess.run(["start", file_path_str], shell=True, check=True)
                else:  # Linux
                    subprocess.run(["xdg-open", file_path_str], check=True)
                
                self.show_status(f"'{file_path.name}' sistem uygulamasıyla açıldı")
                logger.info(f"✅ Sistem uygulamasıyla açıldı: {file_path_str}")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Subprocess hatası: {e}")
                self.show_error(f"Dosya açılamadı: {file_path.name}")
            except Exception as e:
                logger.error(f"❌ Genel açma hatası: {e}")
                self.show_error(f"Dosya açılırken hata: {e}")
                
        except Exception as e:
            logger.error(f"❌ Open file error: {e}")
            self.show_error(f"Dosya açma hatası: {e}")
    
    def on_selection_changed(self):
        """Seçim değişti"""
        selected_items = self.file_list.selectedItems()
        self.selected_files = []
        
        for item in selected_items:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path:
                self.selected_files.append(file_path)
        
        # Seçim sayısını göster
        count = len(self.selected_files)
        if count == 0:
            self.selection_label.setText("")
        elif count == 1:
            path = Path(self.selected_files[0])
            if path.is_file():
                try:
                    size = path.stat().st_size
                    size_str = self.format_size(size)
                    self.selection_label.setText(f"1 dosya ({size_str})")
                except:
                    self.selection_label.setText("1 öğe")
            else:
                self.selection_label.setText("1 klasör")
        else:
            self.selection_label.setText(f"{count} öğe seçili")
    
    def show_context_menu(self, position):
        """Bağlam menüsü göster"""
        item = self.file_list.itemAt(position)
        
        menu = QMenu(self)
        
        if item:
            # Dosya/klasör seçili
            file_path = item.data(Qt.ItemDataRole.UserRole)
            path = Path(file_path)
            
            if path.is_file():
                menu.addAction("📂 Aç", lambda: self.open_file(path))
                menu.addSeparator()
            else:
                menu.addAction("📂 Aç", lambda: self.navigate_to_path(path))
                menu.addSeparator()
            
            menu.addAction("📋 Kopyala", lambda: self.copy_files([file_path]))
            menu.addAction("✂️ Kes", lambda: self.cut_files([file_path]))
            menu.addSeparator()
            menu.addAction("✏️ Yeniden Adlandır", lambda: self.rename_file(file_path))
            menu.addAction("🗑️ Sil", lambda: self.delete_files([file_path]))
            menu.addSeparator()
            menu.addAction("ℹ️ Özellikler", lambda: self.show_properties(file_path))
        else:
            # Boş alan
            menu.addAction("📁 Yeni Klasör", self.create_new_folder)
            menu.addAction("📄 Yeni Dosya", self.create_new_file)
            menu.addSeparator()
            menu.addAction("📋 Yapıştır", lambda: self.paste_files(str(self.current_path)))
            menu.addSeparator()
            menu.addAction("🔄 Yenile", self.refresh)
        
        menu.exec(self.file_list.mapToGlobal(position))
    
    def filter_files(self, text):
        """Dosyaları filtrele"""
        if not text:
            # Filtreyi temizle
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                item.setHidden(False)
        else:
            # Filtre uygula
            text = text.lower()
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                item_text = item.text().lower()
                item.setHidden(text not in item_text)
    
    def copy_files(self, file_paths: List[str]):
        """Dosyaları kopyala"""
        if not file_paths:
            return
        
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        
        # Dosya URL'lerini ekle
        urls = [QUrl.fromLocalFile(path) for path in file_paths]
        mime_data.setUrls(urls)
        
        # Metin olarak da ekle
        mime_data.setText("\n".join(file_paths))
        
        clipboard.setMimeData(mime_data)
        self.copied_files = file_paths.copy()
        self.show_status(f"{len(file_paths)} öğe kopyalandı")
        logger.info(f"Copied {len(file_paths)} files to clipboard")
    
    def paste_files(self, target_dir: str):
        """Dosyaları yapıştır"""
        try:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            
            if mime_data.hasUrls():
                target_path = Path(target_dir)
                if not target_path.is_dir():
                    self.show_error("Hedef bir klasör değil")
                    return
                
                pasted_count = 0
                
                for url in mime_data.urls():
                    source_path = Path(url.toLocalFile())
                    if not source_path.exists():
                        continue
                        
                    target_file = target_path / source_path.name
                    
                    # Çakışma kontrolü
                    if target_file.exists():
                        reply = QMessageBox.question(
                            self, "Dosya Var",
                            f"'{source_path.name}' zaten var. Üzerine yazılsın mı?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply != QMessageBox.StandardButton.Yes:
                            continue
                    
                    try:
                        import shutil
                        if source_path.is_dir():
                            shutil.copytree(source_path, target_file, dirs_exist_ok=True)
                        else:
                            shutil.copy2(source_path, target_file)
                        pasted_count += 1
                    except Exception as e:
                        logger.error(f"paste_file error: {e}")
                
                if pasted_count > 0:
                    self.populate_file_list()
                    self.show_status(f"{pasted_count} öğe yapıştırıldı")
            else:
                self.show_status("Yapıştırılacak dosya yok")
                
        except Exception as e:
            self.show_error(f"Yapıştırma başarısız: {e}")
            logger.error(f"paste_files error: {e}")
    
    def delete_files(self, file_paths: List[str]):
        """Dosyaları sil"""
        if not file_paths:
            return
        
        reply = QMessageBox.question(
            self, "Silme Onayı",
            f"{len(file_paths)} öğeyi silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        deleted_count = 0
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                deleted_count += 1
            except Exception as e:
                self.show_error(f"'{Path(file_path).name}' silinemedi: {e}")
        
        self.populate_file_list()
        self.show_status(f"{deleted_count} öğe silindi")
    
    def rename_file(self, file_path: str):
        """Dosyayı yeniden adlandır"""
        path = Path(file_path)
        
        new_name, ok = QInputDialog.getText(
            self, "Yeniden Adlandır",
            "Yeni ad:", text=path.name
        )
        
        if ok and new_name and new_name != path.name:
            try:
                new_path = path.parent / new_name
                path.rename(new_path)
                self.show_status(f"'{path.name}' → '{new_name}' olarak adlandırıldı")
                self.populate_file_list()
            except FileExistsError:
                self.show_error(f"'{new_name}' zaten mevcut")
            except Exception as e:
                self.show_error(f"Yeniden adlandırma başarısız: {e}")
    
    def refresh(self):
        """Dosya listesini yenile"""
        self.populate_file_list()
        self.show_status("Yenilendi")
    
    def create_new_folder(self):
        """Yeni klasör oluştur"""
        name, ok = QInputDialog.getText(self, "Yeni Klasör", "Klasör adı:", text="Yeni Klasör")
        
        if ok and name:
            try:
                new_path = self.current_path / name
                new_path.mkdir()
                self.populate_file_list()
                self.show_status(f"'{name}' klasörü oluşturuldu")
            except FileExistsError:
                self.show_error(f"'{name}' zaten mevcut")
            except Exception as e:
                self.show_error(f"Klasör oluşturulamadı: {e}")
    
    def create_new_file(self):
        """Yeni dosya oluştur"""
        name, ok = QInputDialog.getText(self, "Yeni Dosya", "Dosya adı:", text="yeni_dosya.txt")
        
        if ok and name:
            try:
                new_path = self.current_path / name
                new_path.touch()
                self.populate_file_list()
                self.show_status(f"'{name}' dosyası oluşturuldu")
            except FileExistsError:
                self.show_error(f"'{name}' zaten mevcut")
            except Exception as e:
                self.show_error(f"Dosya oluşturulamadı: {e}")
    
    def show_properties(self, file_path: str):
        """Dosya özelliklerini göster"""
        path = Path(file_path)
        
        try:
            stat = path.stat()
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Özellikler - {path.name}")
            dialog.setFixedSize(400, 300)
            
            layout = QFormLayout(dialog)
            
            layout.addRow("Ad:", QLabel(path.name))
            layout.addRow("Yol:", QLabel(str(path.parent)))
            layout.addRow("Tür:", QLabel("Dizin" if path.is_dir() else "Dosya"))
            
            if not path.is_dir():
                layout.addRow("Boyut:", QLabel(self.format_size(stat.st_size)))
            
            layout.addRow("Oluşturulma:", QLabel(
                datetime.fromtimestamp(stat.st_ctime).strftime("%d.%m.%Y %H:%M:%S")
            ))
            layout.addRow("Değiştirilme:", QLabel(
                datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M:%S")
            ))
            
            close_button = QPushButton("Kapat")
            close_button.clicked.connect(dialog.close)
            layout.addRow("", close_button)
            
            dialog.exec()
            
        except Exception as e:
            self.show_error(f"Özellikler gösterilemedi: {e}")

def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Files")
    app.setApplicationVersion("2.0.0")
    
    # Ana pencere
    window = CloudFiles()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
