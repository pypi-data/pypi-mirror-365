"""
Cloud PyIDE - Temel Debug Görünümü
Breakpoint, değişken izleyici, çağrı yığını
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

@dataclass
class DebugBreakpoint:
    """Debug breakpoint"""
    file_path: str
    line_number: int
    enabled: bool = True
    condition: str = ""
    hit_count: int = 0

@dataclass
class DebugVariable:
    """Debug değişkeni"""
    name: str
    value: str
    type_name: str
    scope: str = "local"

@dataclass
class StackFrame:
    """Çağrı yığını frame'i"""
    function_name: str
    file_path: str
    line_number: int
    locals_vars: Dict[str, Any] = None

class DebugManager:
    """Debug yöneticisi"""
    
    def __init__(self, ide_instance=None):
        self.ide_instance = ide_instance
        self.logger = logging.getLogger("DebugManager")
        
        # Debug durumu
        self.is_debugging = False
        self.is_paused = False
        
        # Breakpoint'ler
        self.breakpoints: Dict[str, List[DebugBreakpoint]] = {}
        
        # Debug bilgileri
        self.current_frame: Optional[StackFrame] = None
        self.stack_frames: List[StackFrame] = []
        self.variables: List[DebugVariable] = []
        
        # UI bileşenleri
        self.debug_panel = None
        if PYQT_AVAILABLE:
            self.create_debug_panel()
    
    def create_debug_panel(self) -> QWidget:
        """Debug paneli oluştur"""
        if not PYQT_AVAILABLE:
            return None
        
        # Ana panel
        self.debug_panel = QWidget()
        layout = QVBoxLayout(self.debug_panel)
        
        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)
        
        # Debug butonları
        self.start_debug_action = QAction("▶️ Start", self.debug_panel)
        self.start_debug_action.triggered.connect(self.start_debug)
        toolbar.addAction(self.start_debug_action)
        
        self.pause_debug_action = QAction("⏸️ Pause", self.debug_panel)
        self.pause_debug_action.triggered.connect(self.pause_debug)
        self.pause_debug_action.setEnabled(False)
        toolbar.addAction(self.pause_debug_action)
        
        self.stop_debug_action = QAction("⏹️ Stop", self.debug_panel)
        self.stop_debug_action.triggered.connect(self.stop_debug)
        self.stop_debug_action.setEnabled(False)
        toolbar.addAction(self.stop_debug_action)
        
        toolbar.addSeparator()
        
        self.step_over_action = QAction("⏭️ Step Over", self.debug_panel)
        self.step_over_action.triggered.connect(self.step_over)
        self.step_over_action.setEnabled(False)
        toolbar.addAction(self.step_over_action)
        
        self.step_into_action = QAction("⬇️ Step Into", self.debug_panel)
        self.step_into_action.triggered.connect(self.step_into)
        self.step_into_action.setEnabled(False)
        toolbar.addAction(self.step_into_action)
        
        self.step_out_action = QAction("⬆️ Step Out", self.debug_panel)
        self.step_out_action.triggered.connect(self.step_out)
        self.step_out_action.setEnabled(False)
        toolbar.addAction(self.step_out_action)
        
        # Tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Breakpoints tab
        self.breakpoints_widget = self.create_breakpoints_widget()
        tab_widget.addTab(self.breakpoints_widget, "🔴 Breakpoints")
        
        # Variables tab
        self.variables_widget = self.create_variables_widget()
        tab_widget.addTab(self.variables_widget, "📊 Variables")
        
        # Call stack tab
        self.stack_widget = self.create_stack_widget()
        tab_widget.addTab(self.stack_widget, "📚 Call Stack")
        
        return self.debug_panel
    
    def create_breakpoints_widget(self) -> QWidget:
        """Breakpoint widget'ı oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)
        
        clear_all_action = QAction("🗑️ Clear All", widget)
        clear_all_action.triggered.connect(self.clear_all_breakpoints)
        toolbar.addAction(clear_all_action)
        
        toggle_all_action = QAction("🔄 Toggle All", widget)
        toggle_all_action.triggered.connect(self.toggle_all_breakpoints)
        toolbar.addAction(toggle_all_action)
        
        # Breakpoint listesi
        self.breakpoints_list = QTreeWidget()
        self.breakpoints_list.setHeaderLabels(["File", "Line", "Condition", "Enabled"])
        self.breakpoints_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.breakpoints_list.customContextMenuRequested.connect(self.show_breakpoint_context_menu)
        layout.addWidget(self.breakpoints_list)
        
        return widget
    
    def create_variables_widget(self) -> QWidget:
        """Variables widget'ı oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)
        
        refresh_action = QAction("🔄 Refresh", widget)
        refresh_action.triggered.connect(self.refresh_variables)
        toolbar.addAction(refresh_action)
        
        # Variables listesi
        self.variables_list = QTreeWidget()
        self.variables_list.setHeaderLabels(["Name", "Value", "Type", "Scope"])
        layout.addWidget(self.variables_list)
        
        return widget
    
    def create_stack_widget(self) -> QWidget:
        """Call stack widget'ı oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stack listesi
        self.stack_list = QListWidget()
        self.stack_list.itemClicked.connect(self.on_stack_frame_selected)
        layout.addWidget(self.stack_list)
        
        return widget
    
    def add_breakpoint(self, file_path: str, line_number: int, condition: str = "") -> bool:
        """Breakpoint ekle"""
        try:
            if file_path not in self.breakpoints:
                self.breakpoints[file_path] = []
            
            # Aynı satırda breakpoint var mı kontrol et
            for bp in self.breakpoints[file_path]:
                if bp.line_number == line_number:
                    self.logger.warning(f"Breakpoint already exists at {file_path}:{line_number}")
                    return False
            
            # Yeni breakpoint oluştur
            breakpoint = DebugBreakpoint(
                file_path=file_path,
                line_number=line_number,
                condition=condition
            )
            
            self.breakpoints[file_path].append(breakpoint)
            
            # UI'yi güncelle
            self.update_breakpoints_ui()
            
            self.logger.info(f"Added breakpoint at {file_path}:{line_number}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding breakpoint: {e}")
            return False
    
    def remove_breakpoint(self, file_path: str, line_number: int) -> bool:
        """Breakpoint kaldır"""
        try:
            if file_path not in self.breakpoints:
                return False
            
            # Breakpoint'i bul ve kaldır
            for i, bp in enumerate(self.breakpoints[file_path]):
                if bp.line_number == line_number:
                    del self.breakpoints[file_path][i]
                    
                    # Liste boşsa dosyayı kaldır
                    if not self.breakpoints[file_path]:
                        del self.breakpoints[file_path]
                    
                    # UI'yi güncelle
                    self.update_breakpoints_ui()
                    
                    self.logger.info(f"Removed breakpoint at {file_path}:{line_number}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing breakpoint: {e}")
            return False
    
    def toggle_breakpoint(self, file_path: str, line_number: int) -> bool:
        """Breakpoint toggle"""
        try:
            if file_path in self.breakpoints:
                for bp in self.breakpoints[file_path]:
                    if bp.line_number == line_number:
                        bp.enabled = not bp.enabled
                        self.update_breakpoints_ui()
                        return True
            
            # Breakpoint yoksa ekle
            return self.add_breakpoint(file_path, line_number)
            
        except Exception as e:
            self.logger.error(f"Error toggling breakpoint: {e}")
            return False
    
    def clear_all_breakpoints(self):
        """Tüm breakpoint'leri temizle"""
        self.breakpoints.clear()
        self.update_breakpoints_ui()
        self.logger.info("Cleared all breakpoints")
    
    def toggle_all_breakpoints(self):
        """Tüm breakpoint'leri toggle et"""
        for file_breakpoints in self.breakpoints.values():
            for bp in file_breakpoints:
                bp.enabled = not bp.enabled
        
        self.update_breakpoints_ui()
    
    def update_breakpoints_ui(self):
        """Breakpoint UI'sini güncelle"""
        if not PYQT_AVAILABLE or not self.breakpoints_list:
            return
        
        self.breakpoints_list.clear()
        
        for file_path, file_breakpoints in self.breakpoints.items():
            for bp in file_breakpoints:
                item = QTreeWidgetItem()
                item.setText(0, file_path)
                item.setText(1, str(bp.line_number))
                item.setText(2, bp.condition)
                item.setText(3, "✓" if bp.enabled else "✗")
                
                # Renk kodlama
                if bp.enabled:
                    item.setForeground(0, QColor("#ff0000"))
                else:
                    item.setForeground(0, QColor("#808080"))
                
                self.breakpoints_list.addTopLevelItem(item)
    
    def start_debug(self):
        """Debug başlat"""
        try:
            self.is_debugging = True
            self.is_paused = False
            
            # UI durumunu güncelle
            self.update_debug_ui_state()
            
            self.logger.info("Debug session started")
            
            # IDE'ye bildir
            if self.ide_instance and hasattr(self.ide_instance, 'on_debug_started'):
                self.ide_instance.on_debug_started()
                
        except Exception as e:
            self.logger.error(f"Error starting debug: {e}")
    
    def pause_debug(self):
        """Debug duraklat"""
        self.is_paused = True
        self.update_debug_ui_state()
        self.logger.info("Debug session paused")
    
    def stop_debug(self):
        """Debug durdur"""
        try:
            self.is_debugging = False
            self.is_paused = False
            
            # Debug bilgilerini temizle
            self.current_frame = None
            self.stack_frames.clear()
            self.variables.clear()
            
            # UI'yi güncelle
            self.update_debug_ui_state()
            self.update_variables_ui()
            self.update_stack_ui()
            
            self.logger.info("Debug session stopped")
            
            # IDE'ye bildir
            if self.ide_instance and hasattr(self.ide_instance, 'on_debug_stopped'):
                self.ide_instance.on_debug_stopped()
                
        except Exception as e:
            self.logger.error(f"Error stopping debug: {e}")
    
    def step_over(self):
        """Step over"""
        self.logger.info("Step over")
        # TODO: Gerçek debug implementasyonu
    
    def step_into(self):
        """Step into"""
        self.logger.info("Step into")
        # TODO: Gerçek debug implementasyonu
    
    def step_out(self):
        """Step out"""
        self.logger.info("Step out")
        # TODO: Gerçek debug implementasyonu
    
    def update_debug_ui_state(self):
        """Debug UI durumunu güncelle"""
        if not PYQT_AVAILABLE:
            return
        
        # Buton durumları
        if hasattr(self, 'start_debug_action'):
            self.start_debug_action.setEnabled(not self.is_debugging)
            self.pause_debug_action.setEnabled(self.is_debugging and not self.is_paused)
            self.stop_debug_action.setEnabled(self.is_debugging)
            
            self.step_over_action.setEnabled(self.is_debugging and self.is_paused)
            self.step_into_action.setEnabled(self.is_debugging and self.is_paused)
            self.step_out_action.setEnabled(self.is_debugging and self.is_paused)
    
    def refresh_variables(self):
        """Değişkenleri yenile"""
        # TODO: Gerçek debug implementasyonu
        self.update_variables_ui()
    
    def update_variables_ui(self):
        """Variables UI'sini güncelle"""
        if not PYQT_AVAILABLE or not self.variables_list:
            return
        
        self.variables_list.clear()
        
        for var in self.variables:
            item = QTreeWidgetItem()
            item.setText(0, var.name)
            item.setText(1, var.value)
            item.setText(2, var.type_name)
            item.setText(3, var.scope)
            
            self.variables_list.addTopLevelItem(item)
    
    def update_stack_ui(self):
        """Call stack UI'sini güncelle"""
        if not PYQT_AVAILABLE or not self.stack_list:
            return
        
        self.stack_list.clear()
        
        for i, frame in enumerate(self.stack_frames):
            text = f"{frame.function_name} - {frame.file_path}:{frame.line_number}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.stack_list.addItem(item)
    
    def on_stack_frame_selected(self, item):
        """Stack frame seçildi"""
        frame_index = item.data(Qt.ItemDataRole.UserRole)
        if 0 <= frame_index < len(self.stack_frames):
            self.current_frame = self.stack_frames[frame_index]
            self.logger.info(f"Selected stack frame: {self.current_frame.function_name}")
    
    def show_breakpoint_context_menu(self, position):
        """Breakpoint context menü"""
        if not PYQT_AVAILABLE:
            return
        
        item = self.breakpoints_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        edit_action = menu.addAction("Edit Condition")
        edit_action.triggered.connect(lambda: self.edit_breakpoint_condition(item))
        
        toggle_action = menu.addAction("Toggle")
        toggle_action.triggered.connect(lambda: self.toggle_breakpoint_from_ui(item))
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_breakpoint_from_ui(item))
        
        menu.exec(self.breakpoints_list.mapToGlobal(position))
    
    def edit_breakpoint_condition(self, item):
        """Breakpoint koşulunu düzenle"""
        # TODO: Koşul düzenleme dialog'u
        pass
    
    def toggle_breakpoint_from_ui(self, item):
        """UI'den breakpoint toggle"""
        file_path = item.text(0)
        line_number = int(item.text(1))
        self.toggle_breakpoint(file_path, line_number)
    
    def delete_breakpoint_from_ui(self, item):
        """UI'den breakpoint sil"""
        file_path = item.text(0)
        line_number = int(item.text(1))
        self.remove_breakpoint(file_path, line_number)
    
    def get_debug_panel(self) -> Optional[QWidget]:
        """Debug panelini al"""
        return self.debug_panel
    
    def has_breakpoint(self, file_path: str, line_number: int) -> bool:
        """Breakpoint var mı?"""
        if file_path not in self.breakpoints:
            return False
        
        for bp in self.breakpoints[file_path]:
            if bp.line_number == line_number:
                return True
        
        return False
    
    def get_breakpoints_for_file(self, file_path: str) -> List[DebugBreakpoint]:
        """Dosya için breakpoint'leri al"""
        return self.breakpoints.get(file_path, []) 