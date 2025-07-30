"""
Cloud Terminal - Modern UI Widget'ları
Terminal arayüzü, sekmeli yapı ve etkileşimli bileşenler
"""

import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not available for terminal UI")
    sys.exit(1)

class TabWidget(QTabWidget):
    """Modern sekmeli terminal widget"""
    
    def __init__(self):
        super().__init__()
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setMovable(True)
        self.setTabsClosable(True)
        
        # Modern stil
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
                margin-top: -1px;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
            }
            
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom-color: #1e1e1e;
                color: #00ff88;
            }
            
            QTabBar::tab:hover {
                background-color: #3c3c3c;
            }
            
            QTabBar::close-button {
                image: none;
                background-color: #ff6b6b;
                border-radius: 6px;
                width: 12px;
                height: 12px;
            }
            
            QTabBar::close-button:hover {
                background-color: #ff5252;
            }
        """)

class TerminalOutput(QTextEdit):
    """Terminal çıktı widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 13))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Terminal renkleri
        self.default_color = "#ffffff"
        self.error_color = "#ff6b6b"
        self.success_color = "#51cf66"
        self.warning_color = "#ffd43b"
        self.info_color = "#74c0fc"
        
        # Modern terminal stili
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 10px;
            }
            
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #5c5c5c;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #7c7c7c;
            }
        """)
    
    def append_text(self, text: str, color: str = None):
        """Renkli metin ekle"""
        if not color:
            color = self.default_color
        
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Renk formatı
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        
        cursor.setCharFormat(format)
        cursor.insertText(text)
        
        # Scroll to bottom
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def append_output(self, text: str):
        """Normal çıktı ekle"""
        self.append_text(text, self.default_color)
    
    def append_error(self, text: str):
        """Hata çıktısı ekle"""
        self.append_text(text, self.error_color)
    
    def append_success(self, text: str):
        """Başarı mesajı ekle"""
        self.append_text(text, self.success_color)
    
    def append_warning(self, text: str):
        """Uyarı mesajı ekle"""
        self.append_text(text, self.warning_color)
    
    def append_info(self, text: str):
        """Bilgi mesajı ekle"""
        self.append_text(text, self.info_color)
    
    def clear_output(self):
        """Çıktıyı temizle"""
        self.clear()
    
    def get_all_text(self) -> str:
        """Tüm metni al"""
        return self.toPlainText()

class TerminalInput(QLineEdit):
    """Terminal giriş widget'ı"""
    
    # Sinyaller
    command_entered = pyqtSignal(str)
    history_up = pyqtSignal()
    history_down = pyqtSignal()
    tab_pressed = pyqtSignal(str)  # Autocomplete için
    
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 13))
        self.setPlaceholderText("Enter command...")
        
        # Modern stil
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3c3c3c;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
            }
            
            QLineEdit:focus {
                border-color: #00ff88;
                background-color: #1e1e1e;
            }
            
            QLineEdit::placeholder {
                color: #6c757d;
            }
        """)
        
        # Enter tuşu için bağlantı
        self.returnPressed.connect(self.on_enter_pressed)
    
    def keyPressEvent(self, event):
        """Klavye olayları"""
        key = event.key()
        
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.on_enter_pressed()
        elif key == Qt.Key.Key_Up:
            self.history_up.emit()
        elif key == Qt.Key.Key_Down:
            self.history_down.emit()
        elif key == Qt.Key.Key_Tab:
            self.tab_pressed.emit(self.text())
            event.accept()
            return
        else:
            super().keyPressEvent(event)
    
    def on_enter_pressed(self):
        """Enter tuşuna basıldı"""
        command = self.text().strip()
        if command:
            self.command_entered.emit(command)
            self.clear()

class AutoCompletePopup(QListWidget):
    """Autocomplete popup widget'ı"""
    
    # Sinyaller
    completion_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setMaximumHeight(200)
        self.setMinimumWidth(300)
        
        # Modern stil
        self.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                padding: 4px;
            }
            
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
        """)
        
        # Bağlantılar
        self.itemClicked.connect(self.on_item_clicked)
    
    def show_completions(self, completions: List[str], position: QPoint):
        """Tamamlama seçeneklerini göster"""
        self.clear()
        
        if not completions:
            self.hide()
            return
        
        for completion in completions:
            self.addItem(completion)
        
        # Pozisyonu ayarla
        self.move(position)
        self.show()
        
        # İlk öğeyi seç
        if self.count() > 0:
            self.setCurrentRow(0)
    
    def on_item_clicked(self, item):
        """Öğe tıklandı"""
        self.completion_selected.emit(item.text())
        self.hide()
    
    def keyPressEvent(self, event):
        """Klavye olayları"""
        key = event.key()
        
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            current_item = self.currentItem()
            if current_item:
                self.completion_selected.emit(current_item.text())
                self.hide()
        elif key == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

class TerminalWidget(QWidget):
    """Ana terminal widget'ı"""
    
    def __init__(self, kernel=None, command_runner=None, history_manager=None, autocompleter=None):
        super().__init__()
        self.kernel = kernel
        self.command_runner = command_runner
        self.history_manager = history_manager
        self.autocompleter = autocompleter
        
        # Terminal durumu
        self.current_directory = os.getcwd()
        self.session_id = f"terminal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # UI kurulumu
        self.setup_ui()
        self.setup_connections()
        
        # Hoş geldin mesajı
        self.show_welcome_message()
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Terminal çıktısı
        self.output = TerminalOutput()
        layout.addWidget(self.output, 1)
        
        # Alt panel
        input_panel = QWidget()
        input_panel.setFixedHeight(50)
        input_layout = QHBoxLayout(input_panel)
        input_layout.setContentsMargins(10, 8, 10, 8)
        
        # Prompt label
        self.prompt_label = QLabel("$")
        self.prompt_label.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.prompt_label.setStyleSheet("color: #00ff88; margin-right: 5px;")
        input_layout.addWidget(self.prompt_label)
        
        # Komut girişi
        self.input = TerminalInput()
        input_layout.addWidget(self.input, 1)
        
        layout.addWidget(input_panel)
        
        # Autocomplete popup
        self.autocomplete_popup = AutoCompletePopup(self)
        
        # Modern panel stili
        input_panel.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-top: 1px solid #3c3c3c;
            }
        """)
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        self.input.command_entered.connect(self.execute_command)
        self.input.history_up.connect(self.history_up)
        self.input.history_down.connect(self.history_down)
        self.input.tab_pressed.connect(self.show_autocomplete)
        self.autocomplete_popup.completion_selected.connect(self.apply_completion)
    
    def show_welcome_message(self):
        """Hoş geldin mesajı"""
        welcome_text = f"""
╭─────────────────────────────────────────────────────────────╮
│                    🌩️  Cloud Terminal v2.0.0                │
│                     PyCloud OS Terminal                     │
╰─────────────────────────────────────────────────────────────╯

Welcome to Cloud Terminal! Type 'help' for available commands.
Current directory: {self.current_directory}
Session: {self.session_id}

"""
        self.output.append_info(welcome_text)
        self.show_prompt()
    
    def show_prompt(self):
        """Prompt göster"""
        # Mevcut dizin adını al
        dir_name = os.path.basename(self.current_directory) or "/"
        prompt_text = f"\n{dir_name} $ "
        self.output.append_text(prompt_text, "#00ff88")
    
    def execute_command(self, command: str):
        """Komut çalıştır"""
        # Komutu göster
        self.output.append_text(command + "\n", "#ffffff")
        
        # Geçmişe ekle
        if self.history_manager:
            self.history_manager.add_command(command)
        
        # Komut çalıştır
        if self.command_runner:
            try:
                result = self.command_runner.execute_command(command, self.current_directory)
                
                # Sonucu göster
                if result.get('output'):
                    self.output.append_output(result['output'] + "\n")
                
                if result.get('error'):
                    self.output.append_error(result['error'] + "\n")
                
                # Dizin değişikliği kontrolü
                if result.get('new_directory'):
                    self.current_directory = result['new_directory']
                
                # Özel komutlar
                if result.get('clear'):
                    self.clear_output()
                    return
                
                if result.get('exit'):
                    self.close_terminal()
                    return
                
            except Exception as e:
                self.output.append_error(f"Command execution error: {e}\n")
        
        # Yeni prompt göster
        self.show_prompt()
    
    def history_up(self):
        """Geçmişte yukarı git"""
        if self.history_manager:
            command = self.history_manager.get_previous()
            if command:
                self.input.setText(command)
    
    def history_down(self):
        """Geçmişte aşağı git"""
        if self.history_manager:
            command = self.history_manager.get_next()
            if command:
                self.input.setText(command)
            else:
                self.input.clear()
    
    def show_autocomplete(self, partial_command: str):
        """Autocomplete göster"""
        if not self.autocompleter or not partial_command.strip():
            return
        
        completions = self.autocompleter.get_completions(partial_command, self.current_directory)
        
        if completions:
            # Popup pozisyonunu hesapla
            input_pos = self.input.mapToGlobal(self.input.rect().bottomLeft())
            self.autocomplete_popup.show_completions(completions, input_pos)
    
    def apply_completion(self, completion: str):
        """Tamamlamayı uygula"""
        current_text = self.input.text()
        words = current_text.split()
        
        if words:
            # Son kelimeyi değiştir
            words[-1] = completion
            self.input.setText(" ".join(words))
        else:
            self.input.setText(completion)
        
        # Cursor'u sona taşı
        self.input.setCursorPosition(len(self.input.text()))
    
    def clear_output(self):
        """Çıktıyı temizle"""
        self.output.clear_output()
        self.show_welcome_message()
    
    def get_output_text(self) -> str:
        """Çıktı metnini al"""
        return self.output.get_all_text()
    
    def get_current_directory(self) -> str:
        """Mevcut dizini al"""
        return self.current_directory
    
    def set_font_size(self, size: int):
        """Font boyutunu ayarla"""
        font = QFont("Consolas", size)
        self.output.setFont(font)
        self.input.setFont(font)
        self.prompt_label.setFont(QFont("Consolas", size, QFont.Weight.Bold))
    
    def copy_selection(self):
        """Seçili metni kopyala"""
        if self.output.textCursor().hasSelection():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.output.textCursor().selectedText())
    
    def paste_text(self):
        """Metin yapıştır"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.input.insert(text)
    
    def close_terminal(self):
        """Terminal'i kapat"""
        # Parent window'a kapat sinyali gönder
        parent_window = self.window()
        if hasattr(parent_window, 'close_current_session'):
            parent_window.close_current_session()
    
    def cleanup(self):
        """Temizlik işlemleri"""
        # Autocomplete popup'ı kapat
        if self.autocomplete_popup:
            self.autocomplete_popup.hide()
        
        # Session'ı temizle
        if self.history_manager:
            self.history_manager.save_history() 