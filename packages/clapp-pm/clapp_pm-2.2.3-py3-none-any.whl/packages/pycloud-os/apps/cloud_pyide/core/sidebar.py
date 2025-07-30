"""
Cloud PyIDE - Dosya Gezgini Paneli
Proje dosyalarını yönetmek için sidebar
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class ProjectExplorer(QTreeWidget):
    """Proje gezgini widget'ı"""
    
    # Sinyaller
    file_opened = pyqtSignal(str)
    file_context_menu = pyqtSignal(str, QPoint)
    folder_context_menu = pyqtSignal(str, QPoint)
    
    def __init__(self, parent=None, theme_mode="dark"):
        super().__init__(parent)
        self.theme_mode = theme_mode
        self.logger = logging.getLogger("ProjectExplorer")
        
        # Proje yolu
        self.project_path = None
        
        # Setup
        self.setup_explorer()
        self.apply_theme()
    
    def setup_explorer(self):
        """Explorer kurulumu"""
        # Header
        self.setHeaderLabel("📁 Proje Dosyaları")
        
        # Ayarlar
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Double click
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def apply_theme(self):
        """Tema uygula"""
        if self.theme_mode == "dark":
            self.setStyleSheet("""
                QTreeWidget {
                    background-color: #252526;
                    color: #cccccc;
                    border: none;
                    outline: none;
                }
                
                QTreeWidget::item {
                    padding: 4px;
                    border: none;
                }
                
                QTreeWidget::item:selected {
                    background-color: #094771;
                    color: #ffffff;
                }
                
                QTreeWidget::item:hover {
                    background-color: #2a2d2e;
                }
                
                QTreeWidget::branch {
                    background-color: transparent;
                }
                
                QTreeWidget::branch:has-siblings:!adjoins-item {
                    border-image: url(vline.png) 0;
                }
                
                QTreeWidget::branch:has-siblings:adjoins-item {
                    border-image: url(branch-more.png) 0;
                }
                
                QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                    border-image: url(branch-end.png) 0;
                }
                
                QTreeWidget::branch:has-children:!has-siblings:closed,
                QTreeWidget::branch:closed:has-children:has-siblings {
                    border-image: none;
                    image: url(branch-closed.png);
                }
                
                QTreeWidget::branch:open:has-children:!has-siblings,
                QTreeWidget::branch:open:has-children:has-siblings {
                    border-image: none;
                    image: url(branch-open.png);
                }
            """)
        else:
            self.setStyleSheet("""
                QTreeWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    outline: none;
                }
                
                QTreeWidget::item {
                    padding: 4px;
                    border: none;
                }
                
                QTreeWidget::item:selected {
                    background-color: #0078d4;
                    color: #ffffff;
                }
                
                QTreeWidget::item:hover {
                    background-color: #f0f0f0;
                }
            """)
    
    def set_theme(self, theme_mode: str):
        """Tema değiştir"""
        self.theme_mode = theme_mode
        self.apply_theme()
    
    def load_project(self, project_path: str):
        """Proje yükle"""
        self.project_path = project_path
        self.clear()
        
        if not os.path.exists(project_path):
            self.logger.warning(f"Project path does not exist: {project_path}")
            return
        
        # Root item
        root_item = QTreeWidgetItem(self)
        root_item.setText(0, f"📁 {os.path.basename(project_path)}")
        root_item.setData(0, Qt.ItemDataRole.UserRole, project_path)
        
        # Dizini yükle
        self.load_directory(project_path, root_item)
        
        # Expand root
        root_item.setExpanded(True)
        
        self.logger.info(f"Project loaded: {project_path}")
    
    def load_directory(self, dir_path: str, parent_item: QTreeWidgetItem):
        """Dizin içeriğini yükle"""
        try:
            items = []
            
            # Dosya ve klasörleri al
            for item_name in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item_name)
                
                # Gizli dosyaları atla
                if item_name.startswith('.'):
                    continue
                
                # __pycache__ klasörlerini atla
                if item_name == '__pycache__':
                    continue
                
                items.append((item_name, item_path))
            
            # Sırala: önce klasörler, sonra dosyalar
            items.sort(key=lambda x: (not os.path.isdir(x[1]), x[0].lower()))
            
            for item_name, item_path in items:
                tree_item = QTreeWidgetItem(parent_item)
                tree_item.setData(0, Qt.ItemDataRole.UserRole, item_path)
                
                if os.path.isdir(item_path):
                    # Klasör
                    tree_item.setText(0, f"📁 {item_name}")
                    
                    # Alt klasörleri yükle (lazy loading için placeholder)
                    if self.has_subdirectories(item_path):
                        placeholder = QTreeWidgetItem(tree_item)
                        placeholder.setText(0, "Loading...")
                else:
                    # Dosya
                    icon = self.get_file_icon(item_name)
                    tree_item.setText(0, f"{icon} {item_name}")
        
        except PermissionError:
            self.logger.warning(f"Permission denied: {dir_path}")
        except Exception as e:
            self.logger.error(f"Error loading directory {dir_path}: {e}")
    
    def has_subdirectories(self, dir_path: str) -> bool:
        """Dizinin alt klasörleri var mı?"""
        try:
            for item in os.listdir(dir_path):
                if not item.startswith('.') and os.path.isdir(os.path.join(dir_path, item)):
                    return True
        except:
            pass
        return False
    
    def get_file_icon(self, filename: str) -> str:
        """Dosya tipine göre ikon al"""
        ext = Path(filename).suffix.lower()
        
        icon_map = {
            '.py': '🐍',
            '.pyw': '🐍',
            '.pyi': '🐍',
            '.txt': '📄',
            '.md': '📝',
            '.json': '📋',
            '.yaml': '📋',
            '.yml': '📋',
            '.xml': '📋',
            '.html': '🌐',
            '.css': '🎨',
            '.js': '📜',
            '.ts': '📜',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.gif': '🖼️',
            '.svg': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.exe': '⚙️',
            '.app': '📱',
            '.sh': '⚡',
            '.bat': '⚡',
            '.cmd': '⚡',
        }
        
        return icon_map.get(ext, '📄')
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Item çift tıklandı"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if file_path and os.path.isfile(file_path):
            self.file_opened.emit(file_path)
        elif file_path and os.path.isdir(file_path):
            # Klasör expand/collapse
            item.setExpanded(not item.isExpanded())
            
            # Lazy loading
            if item.isExpanded() and item.childCount() == 1:
                first_child = item.child(0)
                if first_child and first_child.text(0) == "Loading...":
                    item.removeChild(first_child)
                    self.load_directory(file_path, item)
    
    def show_context_menu(self, position: QPoint):
        """Context menü göster"""
        item = self.itemAt(position)
        if not item:
            return
        
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if not file_path:
            return
        
        global_pos = self.mapToGlobal(position)
        
        if os.path.isfile(file_path):
            self.file_context_menu.emit(file_path, global_pos)
        else:
            self.folder_context_menu.emit(file_path, global_pos)
    
    def refresh_project(self):
        """Projeyi yenile"""
        if self.project_path:
            self.load_project(self.project_path)
    
    def create_new_file(self, parent_dir: str, filename: str) -> bool:
        """Yeni dosya oluştur"""
        try:
            file_path = os.path.join(parent_dir, filename)
            
            if os.path.exists(file_path):
                QMessageBox.warning(self, "Hata", f"Dosya zaten mevcut: {filename}")
                return False
            
            # Boş dosya oluştur
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")
            
            # Explorer'ı yenile
            self.refresh_project()
            
            # Dosyayı aç
            self.file_opened.emit(file_path)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya oluşturulamadı: {e}")
            return False
    
    def create_new_folder(self, parent_dir: str, folder_name: str) -> bool:
        """Yeni klasör oluştur"""
        try:
            folder_path = os.path.join(parent_dir, folder_name)
            
            if os.path.exists(folder_path):
                QMessageBox.warning(self, "Hata", f"Klasör zaten mevcut: {folder_name}")
                return False
            
            os.makedirs(folder_path)
            
            # Explorer'ı yenile
            self.refresh_project()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Klasör oluşturulamadı: {e}")
            return False
    
    def delete_item(self, item_path: str) -> bool:
        """Dosya/klasör sil"""
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                import shutil
                shutil.rmtree(item_path)
            
            # Explorer'ı yenile
            self.refresh_project()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Silme işlemi başarısız: {e}")
            return False
    
    def rename_item(self, old_path: str, new_name: str) -> bool:
        """Dosya/klasör yeniden adlandır"""
        try:
            parent_dir = os.path.dirname(old_path)
            new_path = os.path.join(parent_dir, new_name)
            
            if os.path.exists(new_path):
                QMessageBox.warning(self, "Hata", f"Bu isimde bir öğe zaten mevcut: {new_name}")
                return False
            
            os.rename(old_path, new_path)
            
            # Explorer'ı yenile
            self.refresh_project()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Yeniden adlandırma başarısız: {e}")
            return False
    
    def get_selected_path(self) -> Optional[str]:
        """Seçili öğenin yolunu al"""
        current_item = self.currentItem()
        if current_item:
            return current_item.data(0, Qt.ItemDataRole.UserRole)
        return None
    
    def expand_to_file(self, file_path: str):
        """Belirtilen dosyaya kadar expand et"""
        if not self.project_path or not file_path.startswith(self.project_path):
            return
        
        # Relative path al
        rel_path = os.path.relpath(file_path, self.project_path)
        path_parts = rel_path.split(os.sep)
        
        # Root item'dan başla
        current_item = self.topLevelItem(0)
        if not current_item:
            return
        
        # Her path part için item bul ve expand et
        for part in path_parts[:-1]:  # Son part dosya adı
            for i in range(current_item.childCount()):
                child = current_item.child(i)
                child_path = child.data(0, Qt.ItemDataRole.UserRole)
                
                if child_path and os.path.basename(child_path) == part:
                    child.setExpanded(True)
                    
                    # Lazy loading kontrolü
                    if child.childCount() == 1:
                        first_child = child.child(0)
                        if first_child and first_child.text(0) == "Loading...":
                            child.removeChild(first_child)
                            self.load_directory(child_path, child)
                    
                    current_item = child
                    break
        
        # Son dosyayı seç
        for i in range(current_item.childCount()):
            child = current_item.child(i)
            child_path = child.data(0, Qt.ItemDataRole.UserRole)
            
            if child_path == file_path:
                self.setCurrentItem(child)
                break 