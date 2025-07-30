"""
Cloud Terminal - Modern Ana Uygulama
Sekmeli terminal arayüzü ve gelişmiş özellikler
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not available for Cloud Terminal")
    sys.exit(1)

from .terminal_ui import TerminalWidget, TabWidget
from .command_runner import CommandRunner
from .history import CommandHistory
from .autocomplete import AutoCompleter
from .themes import TerminalThemes

class CloudTerminal(QMainWindow):
    """Modern Cloud Terminal Ana Uygulaması"""
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("CloudTerminal")
        
        # Core components
        self.command_runner = CommandRunner(kernel)
        self.history_manager = CommandHistory()
        self.autocompleter = AutoCompleter(self.command_runner)
        self.theme_manager = TerminalThemes()
        
        # Terminal sessions
        self.sessions = {}
        self.session_counter = 0
        
        # UI kurulumu
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
        # İlk terminal sekmesi
        self.new_terminal_session()
        
        self.logger.info("Cloud Terminal v2.0.0 initialized")
    
    def setup_ui(self):
        """Modern UI kurulumu"""
        self.setWindowTitle("Cloud Terminal")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 500)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget (sekmeli arayüz)
        self.tab_widget = TabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_terminal_session)
        main_layout.addWidget(self.tab_widget, 1)
        
        # Alt panel (kontroller)
        self.setup_control_panel()
        main_layout.addWidget(self.control_panel)
        
        # Toolbar
        self.setup_toolbar()
        
        # Status bar
        self.setup_statusbar()
        
        # Modern stil uygula
        self.apply_modern_style()
    
    def setup_control_panel(self):
        """Alt kontrol paneli"""
        self.control_panel = QWidget()
        self.control_panel.setFixedHeight(50)
        
        layout = QHBoxLayout(self.control_panel)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # Sol taraf - terminal kontrolleri
        self.new_tab_btn = QPushButton("+ New Tab")
        self.new_tab_btn.setObjectName("primaryButton")
        self.new_tab_btn.clicked.connect(self.new_terminal_session)
        layout.addWidget(self.new_tab_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_current_terminal)
        layout.addWidget(self.clear_btn)
        
        self.save_output_btn = QPushButton("Save Output")
        self.save_output_btn.clicked.connect(self.save_terminal_output)
        layout.addWidget(self.save_output_btn)
        
        layout.addStretch()
        
        # Sağ taraf - tema ve ayarlar
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Hacker", "Glass", "Classic"])
        self.theme_combo.setCurrentText("Dark")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        layout.addWidget(QLabel("Theme:"))
        layout.addWidget(self.theme_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(13)
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        layout.addWidget(QLabel("Font:"))
        layout.addWidget(self.font_size_spin)
    
    def setup_toolbar(self):
        """Toolbar kurulumu"""
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setMovable(False)
        
        # Dosya menüsü
        file_menu = self.menuBar().addMenu("File")
        
        new_action = QAction("New Terminal", self)
        new_action.setShortcut("Ctrl+T")
        new_action.triggered.connect(self.new_terminal_session)
        file_menu.addAction(new_action)
        
        close_action = QAction("Close Tab", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close_current_session)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save Output", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_terminal_output)
        file_menu.addAction(save_action)
        
        # Edit menüsü
        edit_menu = self.menuBar().addMenu("Edit")
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_selection)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_text)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        clear_action = QAction("Clear Terminal", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.clear_current_terminal)
        edit_menu.addAction(clear_action)
        
        # View menüsü
        view_menu = self.menuBar().addMenu("View")
        
        for theme in ["Dark", "Light", "Hacker", "Glass", "Classic"]:
            theme_action = QAction(f"{theme} Theme", self)
            theme_action.triggered.connect(lambda checked, t=theme: self.change_theme(t))
            view_menu.addAction(theme_action)
        
        # Tools menüsü
        tools_menu = self.menuBar().addMenu("Tools")
        
        history_action = QAction("Command History", self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(self.show_command_history)
        tools_menu.addAction(history_action)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
    
    def setup_statusbar(self):
        """Status bar kurulumu"""
        self.status_bar = self.statusBar()
        
        # Sol taraf - durum
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Sağ taraf - bilgiler
        self.session_count_label = QLabel("1 session")
        self.status_bar.addPermanentWidget(self.session_count_label)
        
        self.current_dir_label = QLabel(os.getcwd())
        self.status_bar.addPermanentWidget(self.current_dir_label)
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def apply_modern_style(self):
        """Modern stil uygula"""
        self.setStyleSheet("""
            /* Ana pencere */
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            /* Tab widget */
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom-color: #1e1e1e;
            }
            
            QTabBar::tab:hover {
                background-color: #3c3c3c;
            }
            
            /* Butonlar */
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: 600;
            }
            
            QPushButton:hover {
                background-color: #14a085;
            }
            
            QPushButton#primaryButton {
                background-color: #007acc;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #1e90ff;
            }
            
            /* Kontrol paneli */
            QWidget#controlPanel {
                background-color: #2d2d2d;
                border-top: 1px solid #3c3c3c;
            }
            
            /* ComboBox */
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                padding: 4px 8px;
                border-radius: 4px;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            
            /* SpinBox */
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                padding: 4px;
                border-radius: 4px;
            }
            
            /* MenuBar */
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #3c3c3c;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            
            QMenuBar::item:selected {
                background-color: #3c3c3c;
            }
            
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
            }
            
            QMenu::item:selected {
                background-color: #3c3c3c;
            }
            
            /* Status bar */
            QStatusBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-top: 1px solid #3c3c3c;
            }
        """)
    
    def apply_theme(self):
        """Tema uygula"""
        current_theme = self.theme_combo.currentText().lower()
        self.theme_manager.apply_theme(self, current_theme)
    
    def new_terminal_session(self):
        """Yeni terminal sekmesi oluştur"""
        self.session_counter += 1
        session_id = f"session_{self.session_counter}"
        
        # Terminal widget oluştur
        terminal_widget = TerminalWidget(
            kernel=self.kernel,
            command_runner=self.command_runner,
            history_manager=self.history_manager,
            autocompleter=self.autocompleter
        )
        
        # Sekmede göster
        tab_title = f"Terminal {self.session_counter}"
        index = self.tab_widget.addTab(terminal_widget, tab_title)
        self.tab_widget.setCurrentIndex(index)
        
        # Session kaydet
        self.sessions[session_id] = {
            'widget': terminal_widget,
            'index': index,
            'title': tab_title
        }
        
        # Terminal widget'a focus ver
        terminal_widget.setFocus()
        
        # Status güncelle
        self.update_session_count()
        self.status_label.setText(f"New terminal session: {tab_title}")
        
        self.logger.info(f"New terminal session created: {session_id}")
    
    def close_terminal_session(self, index: int):
        """Terminal sekmesini kapat"""
        if self.tab_widget.count() <= 1:
            # Son sekme - uygulamayı kapat
            self.close()
            return
        
        # Session'ı bul ve kaldır
        session_to_remove = None
        for session_id, session_data in self.sessions.items():
            if session_data['index'] == index:
                session_to_remove = session_id
                break
        
        if session_to_remove:
            del self.sessions[session_to_remove]
        
        # Sekmeyi kapat
        self.tab_widget.removeTab(index)
        
        # Index'leri güncelle
        self.update_session_indices()
        self.update_session_count()
        
        self.status_label.setText("Terminal session closed")
    
    def close_current_session(self):
        """Aktif sekmeyi kapat"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_terminal_session(current_index)
    
    def update_session_indices(self):
        """Session index'lerini güncelle"""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            for session_id, session_data in self.sessions.items():
                if session_data['widget'] == widget:
                    session_data['index'] = i
                    break
    
    def update_session_count(self):
        """Session sayısını güncelle"""
        count = len(self.sessions)
        self.session_count_label.setText(f"{count} session{'s' if count != 1 else ''}")
    
    def get_current_terminal(self) -> Optional[TerminalWidget]:
        """Aktif terminal widget'ını al"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_widget.widget(current_index)
        return None
    
    def clear_current_terminal(self):
        """Aktif terminal'i temizle"""
        terminal = self.get_current_terminal()
        if terminal:
            terminal.clear_output()
            self.status_label.setText("Terminal cleared")
    
    def save_terminal_output(self):
        """Terminal çıktısını kaydet"""
        terminal = self.get_current_terminal()
        if not terminal:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Terminal Output", 
            f"terminal_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(terminal.get_output_text())
                self.status_label.setText(f"Output saved to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"Failed to save output: {e}")
    
    def copy_selection(self):
        """Seçili metni kopyala"""
        terminal = self.get_current_terminal()
        if terminal:
            terminal.copy_selection()
    
    def paste_text(self):
        """Metin yapıştır"""
        terminal = self.get_current_terminal()
        if terminal:
            terminal.paste_text()
    
    def change_theme(self, theme_name: str):
        """Tema değiştir"""
        self.theme_manager.apply_theme(self, theme_name.lower())
        
        # Tüm terminal widget'larına tema uygula
        for session_data in self.sessions.values():
            terminal_widget = session_data['widget']
            self.theme_manager.apply_terminal_theme(terminal_widget, theme_name.lower())
        
        self.status_label.setText(f"Theme changed to {theme_name}")
    
    def change_font_size(self, size: int):
        """Font boyutunu değiştir"""
        for session_data in self.sessions.values():
            terminal_widget = session_data['widget']
            terminal_widget.set_font_size(size)
        
        self.status_label.setText(f"Font size changed to {size}px")
    
    def show_command_history(self):
        """Komut geçmişini göster"""
        history_dialog = CommandHistoryDialog(self.history_manager, self)
        history_dialog.exec()
    
    def show_settings(self):
        """Ayarları göster"""
        settings_dialog = TerminalSettingsDialog(self)
        settings_dialog.exec()
    
    def on_tab_changed(self, index):
        """Sekme değişti"""
        if index >= 0:
            terminal = self.tab_widget.widget(index)
            if terminal:
                terminal.setFocus()
                # Mevcut dizini güncelle
                current_dir = terminal.get_current_directory()
                self.current_dir_label.setText(current_dir)
    
    def closeEvent(self, event):
        """Pencere kapatılıyor"""
        # Tüm terminal session'larını temizle
        for session_data in self.sessions.values():
            terminal_widget = session_data['widget']
            terminal_widget.cleanup()
        
        event.accept()
        self.logger.info("Cloud Terminal closed")

class CommandHistoryDialog(QDialog):
    """Komut geçmişi dialog'u"""
    
    def __init__(self, history_manager: CommandHistory, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle("Command History")
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(self)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Geçmiş listesi
        self.history_list = QListWidget()
        self.populate_history()
        layout.addWidget(self.history_list)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def populate_history(self):
        """Geçmişi doldur"""
        self.history_list.clear()
        for command in self.history_manager.get_history():
            self.history_list.addItem(command)
    
    def filter_history(self, text: str):
        """Geçmişi filtrele"""
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def clear_history(self):
        """Geçmişi temizle"""
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear command history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_manager.clear_history()
            self.populate_history()

class TerminalSettingsDialog(QDialog):
    """Terminal ayarları dialog'u"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle("Terminal Settings")
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout(self)
        
        # Ayar seçenekleri
        settings_group = QGroupBox("Appearance")
        settings_layout = QFormLayout(settings_group)
        
        # Font ayarları
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Consolas", "Monaco", "Courier New", "JetBrains Mono"])
        settings_layout.addRow("Font:", self.font_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(13)
        settings_layout.addRow("Font Size:", self.font_size_spin)
        
        # Tema ayarları
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Hacker", "Glass", "Classic"])
        settings_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(settings_group)
        
        # Davranış ayarları
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        self.autocomplete_cb = QCheckBox("Enable autocomplete")
        self.autocomplete_cb.setChecked(True)
        behavior_layout.addRow(self.autocomplete_cb)
        
        self.history_size_spin = QSpinBox()
        self.history_size_spin.setRange(100, 10000)
        self.history_size_spin.setValue(1000)
        behavior_layout.addRow("History Size:", self.history_size_spin)
        
        layout.addWidget(behavior_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def apply_settings(self):
        """Ayarları uygula"""
        # Ayarları parent'a gönder
        if self.parent():
            # Font değişikliği
            font_size = self.font_size_spin.value()
            self.parent().change_font_size(font_size)
            
            # Tema değişikliği
            theme = self.theme_combo.currentText()
            self.parent().change_theme(theme)
        
        self.close() 