"""
Cloud Python Console - PyCloud OS Python REPL Konsolu
Anlık Python kodu çalıştırma ve test etme
"""

import sys
import code
import io
import logging
import traceback
import threading
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import contextlib

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                                QLabel, QSplitter, QFrame)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
    from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Dummy classes
    class QMainWindow: pass
    class QObject: pass
    class pyqtSignal: pass

@dataclass
class CommandHistory:
    """Komut geçmişi"""
    commands: List[str]
    current_index: int = -1
    max_size: int = 100

class PythonInterpreter(QObject):
    """Python yorumlayıcı thread"""
    
    # Sinyaller
    output_ready = pyqtSignal(str, str)  # output, error
    
    def __init__(self):
        super().__init__()
        self.locals_dict = {}
        self.globals_dict = {'__name__': '__console__', '__doc__': None}
        
        # Temel modülleri ekle
        self._setup_environment()
    
    def _setup_environment(self):
        """Konsol ortamını hazırla"""
        # Standart modülleri import et
        import builtins
        import os
        import sys
        import json
        import time
        import datetime
        import math
        import random
        
        # Globals'a ekle
        self.globals_dict.update({
            'os': os,
            'sys': sys,
            'json': json,
            'time': time,
            'datetime': datetime,
            'math': math,
            'random': random,
        })
        
        # PyCloud modüllerini yükle (eğer varsa)
        try:
            # PyCloud core modüllerini import et
            sys.path.insert(0, '.')
            
            import core.kernel
            import core.fs
            import core.users
            
            self.globals_dict.update({
                'kernel': core.kernel,
                'fs': core.fs,
                'users': core.users,
            })
        except ImportError:
            pass
    
    def execute_code(self, code_str: str) -> tuple[str, str]:
        """Python kodunu çalıştır"""
        try:
            # Output ve error yakalama için StringIO kullan
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            try:
                # Kodu derlemeyi dene
                compiled = compile(code_str, '<console>', 'eval')
                # eval ile çalıştır (expression)
                result = eval(compiled, self.globals_dict, self.locals_dict)
                
                output = stdout_capture.getvalue()
                if result is not None:
                    output += repr(result)
                
                error = stderr_capture.getvalue()
                
            except SyntaxError:
                # exec ile dene (statement)
                try:
                    exec(code_str, self.globals_dict, self.locals_dict)
                    output = stdout_capture.getvalue()
                    error = stderr_capture.getvalue()
                except Exception as e:
                    output = stdout_capture.getvalue()
                    error = stderr_capture.getvalue() + traceback.format_exc()
            
            except Exception as e:
                output = stdout_capture.getvalue()
                error = stderr_capture.getvalue() + traceback.format_exc()
            
            finally:
                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            return output, error
            
        except Exception as e:
            return "", f"Kritik hata: {str(e)}"

class PythonConsole(QMainWindow):
    """Ana Python konsol penceresi"""
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("PythonConsole")
        
        # Python yorumlayıcı
        self.interpreter = PythonInterpreter()
        self.interpreter.output_ready.connect(self.on_output_ready)
        
        # Komut geçmişi
        self.history = CommandHistory(commands=[])
        
        # UI bileşenleri
        self.output_display: Optional[QTextEdit] = None
        self.input_line: Optional[QLineEdit] = None
        self.current_command = ""
        
        if not PYQT_AVAILABLE:
            self.logger.error("PyQt6 not available")
            return
        
        self.setup_ui()
        self.setup_connections()
        
        # Karşılama mesajı
        self.show_welcome_message()
        
        self.logger.info("Python Console initialized")
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle("Cloud Python Console")
        self.setGeometry(100, 100, 800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Başlık
        self.create_header(main_layout)
        
        # Splitter (çıktı ve giriş alanları)
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter, 1)
        
        # Çıktı alanı
        self.create_output_area(splitter)
        
        # Giriş alanı
        self.create_input_area(splitter)
        
        # Splitter oranları
        splitter.setSizes([400, 200])
        
        # Durum çubuğu
        self.create_status_bar()
        
        # Tema uygula
        self.apply_theme()
    
    def create_header(self, parent_layout):
        """Başlık alanını oluştur"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setMaximumHeight(60)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Başlık
        title_label = QLabel("🐍 Python Console")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Sistem uyumlu monospace font
        title_font = QFont()
        title_font.setFamily("Courier")
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title_font.setStyleHint(QFont.StyleHint.Monospace)
        title_label.setFont(title_font)
        
        title_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                background-color: #1e1e1e;
                padding: 10px;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Kontrol butonları
        clear_btn = QPushButton("Temizle")
        clear_btn.clicked.connect(self.clear_output)
        header_layout.addWidget(clear_btn)
        
        reset_btn = QPushButton("Sıfırla")
        reset_btn.clicked.connect(self.reset_interpreter)
        header_layout.addWidget(reset_btn)
        
        parent_layout.addWidget(header_frame)
    
    def create_output_area(self, parent_splitter):
        """Çıktı alanını oluştur"""
        # Output display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        
        # Monospace font
        output_font = QFont()
        output_font.setFamily("Courier")
        output_font.setPointSize(11)
        output_font.setStyleHint(QFont.StyleHint.Monospace)
        self.output_display.setFont(output_font)
        
        parent_splitter.addWidget(self.output_display)
    
    def create_input_area(self, parent_splitter):
        """Giriş alanını oluştur"""
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(4, 4, 4, 4)
        
        # Label
        input_label = QLabel("Python Kodu:")
        input_font = QFont()
        input_font.setFamily("Courier")
        input_font.setPointSize(10)
        input_font.setStyleHint(QFont.StyleHint.Monospace)
        input_label.setFont(input_font)
        input_layout.addWidget(input_label)
        
        # Giriş satırı layout
        input_line_layout = QHBoxLayout()
        
        # Prompt
        prompt_label = QLabel(">>> ")
        prompt_font = QFont()
        prompt_font.setFamily("Courier")
        prompt_font.setPointSize(11)
        prompt_font.setWeight(QFont.Weight.Bold)
        prompt_font.setStyleHint(QFont.StyleHint.Monospace)
        prompt_label.setFont(prompt_font)
        prompt_label.setStyleSheet("color: #00ff88;")
        input_line_layout.addWidget(prompt_label)
        
        # Giriş kutusu
        self.input_line = QLineEdit()
        console_font = QFont()
        console_font.setFamily("Courier")
        console_font.setPointSize(11)
        console_font.setStyleHint(QFont.StyleHint.Monospace)
        self.input_line.setFont(console_font)
        self.input_line.setPlaceholderText("Python kodu yazın ve Enter'a basın...")
        input_line_layout.addWidget(self.input_line, 1)
        
        # Çalıştır butonu
        run_btn = QPushButton("Çalıştır")
        run_btn.clicked.connect(self.execute_current_command)
        input_line_layout.addWidget(run_btn)
        
        input_layout.addLayout(input_line_layout)
        parent_splitter.addWidget(input_frame)
    
    def create_status_bar(self):
        """Durum çubuğu"""
        status_bar = self.statusBar()
        status_bar.showMessage("Hazır - Python komutlarını yazmaya başlayın")
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        if self.input_line:
            self.input_line.returnPressed.connect(self.execute_current_command)
            self.input_line.keyPressEvent = self.input_key_press_event
    
    def apply_theme(self):
        """Tema uygula"""
        # Ana stil
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Courier', 'Consolas', monospace;
            }
            
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier', 'Consolas', monospace;
                font-size: 11px;
                selection-background-color: #404040;
            }
            
            QLineEdit {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
            }
            
            QLineEdit:focus {
                border-color: #58a6ff;
            }
            
            QPushButton {
                background-color: #238636;
                color: #ffffff;
                border: 1px solid #2ea043;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2ea043;
            }
            
            QPushButton:pressed {
                background-color: #1f6f32;
            }
            
            QLabel {
                color: #c9d1d9;
                background-color: transparent;
            }
            
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
        """)
    
    def show_welcome_message(self):
        """Karşılama mesajı göster"""
        welcome_msg = f"""🐍 Cloud Python Console
PyCloud OS Python REPL v{sys.version.split()[0]}

Python yolu: {sys.executable}
Çalışma dizini: {sys.path[0]}

Kullanılabilir modüller:
• os, sys, json, time, datetime, math, random
• PyCloud core modülleri (kernel, fs, users)

Komutlar:
• help() - Python yardımı
• dir() - Değişken listesi
• clear() - Ekranı temizle

Kodunuzu yazın ve Enter'a basın...
{'='*50}
"""
        self.append_output(welcome_msg, "info")
    
    def input_key_press_event(self, event):
        """Giriş kutusu klavye olayları"""
        if event.key() == Qt.Key.Key_Up:
            self.history_previous()
        elif event.key() == Qt.Key.Key_Down:
            self.history_next()
        else:
            # Varsayılan davranış
            QLineEdit.keyPressEvent(self.input_line, event)
    
    def history_previous(self):
        """Geçmişte önceki komut"""
        if not self.history.commands:
            return
        
        if self.history.current_index <= 0:
            self.history.current_index = len(self.history.commands) - 1
        else:
            self.history.current_index -= 1
        
        if 0 <= self.history.current_index < len(self.history.commands):
            self.input_line.setText(self.history.commands[self.history.current_index])
    
    def history_next(self):
        """Geçmişte sonraki komut"""
        if not self.history.commands:
            return
        
        if self.history.current_index >= len(self.history.commands) - 1:
            self.history.current_index = 0
        else:
            self.history.current_index += 1
        
        if 0 <= self.history.current_index < len(self.history.commands):
            self.input_line.setText(self.history.commands[self.history.current_index])
    
    def add_to_history(self, command: str):
        """Komut geçmişine ekle"""
        if command.strip() and (not self.history.commands or self.history.commands[-1] != command):
            self.history.commands.append(command)
            
            # Maksimum boyut kontrolü
            if len(self.history.commands) > self.history.max_size:
                self.history.commands.pop(0)
        
        self.history.current_index = -1
    
    def execute_current_command(self):
        """Mevcut komutu çalıştır"""
        if not self.input_line:
            return
        
        command = self.input_line.text().strip()
        if not command:
            return
        
        # Komut geçmişine ekle
        self.add_to_history(command)
        
        # Komutu göster
        self.append_output(f">>> {command}", "command")
        
        # Özel komutları kontrol et
        if self.handle_special_commands(command):
            self.input_line.clear()
            return
        
        # Python kodunu çalıştır
        self.statusBar().showMessage("Çalıştırılıyor...")
        
        # Thread'de çalıştır (UI donmasını önlemek için)
        QTimer.singleShot(10, lambda: self.run_python_code(command))
        
        self.input_line.clear()
    
    def handle_special_commands(self, command: str) -> bool:
        """Özel komutları işle"""
        if command.lower() in ['clear()', 'clear']:
            self.clear_output()
            return True
        elif command.lower() in ['exit()', 'quit()', 'exit', 'quit']:
            self.close()
            return True
        elif command.lower() in ['reset()', 'reset']:
            self.reset_interpreter()
            return True
        elif command.lower().startswith('help'):
            self.show_help()
            return True
        
        return False
    
    def run_python_code(self, code: str):
        """Python kodunu çalıştır"""
        try:
            output, error = self.interpreter.execute_code(code)
            self.on_output_ready(output, error)
        except Exception as e:
            self.on_output_ready("", f"Yorumlayıcı hatası: {str(e)}")
    
    def on_output_ready(self, output: str, error: str):
        """Çıktı hazır olduğunda"""
        if output:
            self.append_output(output, "output")
        
        if error:
            self.append_output(error, "error")
        
        self.statusBar().showMessage("Hazır")
    
    def append_output(self, text: str, message_type: str = "output"):
        """Çıktı alanına metin ekle"""
        if not self.output_display:
            return
        
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Renk formatı
        format = QTextCharFormat()
        
        if message_type == "command":
            format.setForeground(QColor("#58a6ff"))  # Mavi
        elif message_type == "error":
            format.setForeground(QColor("#f85149"))  # Kırmızı
        elif message_type == "output":
            format.setForeground(QColor("#7ee787"))  # Yeşil
        elif message_type == "info":
            format.setForeground(QColor("#a5a5a5"))  # Gri
        else:
            format.setForeground(QColor("#c9d1d9"))  # Varsayılan beyaz
        
        cursor.setCharFormat(format)
        cursor.insertText(text + "\n")
        
        # Otomatik scroll
        self.output_display.setTextCursor(cursor)
        self.output_display.ensureCursorVisible()
    
    def clear_output(self):
        """Çıktı alanını temizle"""
        if self.output_display:
            self.output_display.clear()
            self.show_welcome_message()
    
    def reset_interpreter(self):
        """Yorumlayıcıyı sıfırla"""
        self.interpreter = PythonInterpreter()
        self.interpreter.output_ready.connect(self.on_output_ready)
        self.clear_output()
        self.append_output("Yorumlayıcı sıfırlandı.", "info")
    
    def show_help(self):
        """Yardım göster"""
        help_text = """
Python Console Yardımı:

Temel komutlar:
• help() - Python built-in yardımı
• dir() - Mevcut değişkenleri listele
• clear() - Ekranı temizle
• reset() - Yorumlayıcıyı sıfırla
• exit() - Konsolu kapat

Klavye kısayolları:
• ↑/↓ - Komut geçmişinde gezin
• Enter - Komutu çalıştır
• Ctrl+C - Kopyala
• Ctrl+V - Yapıştır

Python örnekleri:
>>> 2 + 2
>>> import math; math.pi
>>> for i in range(3): print(i)
>>> def hello(): return "Merhaba PyCloud!"
>>> hello()

PyCloud örnekleri:
>>> kernel.get_system_info()
>>> fs.list_files("/")
>>> users.get_current_user()
"""
        self.append_output(help_text, "info")
    
    def closeEvent(self, event):
        """Pencere kapatma olayı"""
        self.logger.info("Python Console closing")
        event.accept()

def main():
    """Ana fonksiyon"""
    if not PYQT_AVAILABLE:
        print("PyQt6 gerekli ancak bulunamadı.")
        return 1
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Ana pencere
    console = PythonConsole()
    console.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 