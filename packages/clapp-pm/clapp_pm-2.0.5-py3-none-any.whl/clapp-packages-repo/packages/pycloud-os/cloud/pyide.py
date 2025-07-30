"""
Cloud PyIDE - PyCloud OS Modern Python IDE
Modern ve modüler Python IDE. Syntax renklendirme, eklenti desteği, proje şablonları, 
versiyon takibi ve temel hata ayıklama içerir.
"""

import sys
import os
import json
import logging
import threading
import time
import subprocess
import shutil
import argparse
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 bulunamadı - PyIDE text modunda çalışacak")

# Core modüllerini import et
try:
    from apps.cloud_pyide.core import (
        ModernCodeEditor,
        ProjectExplorer,
        AutoCompleteEngine,
        SnippetManager,
        CodeRunner,
        PluginManager,
        ThemeManager,
        DebugManager,
        TemplateManager
    )
    from apps.cloud_pyide.core.autocomplete import CompletionItem
    from apps.cloud_pyide.core.snippets import CodeSnippet
    from apps.cloud_pyide.core.debugger import DebugBreakpoint
    from apps.cloud_pyide.core.templates import ProjectTemplate
    from apps.cloud_pyide.core.theme import ThemeMode
    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Core modüller yüklenemedi: {e}")
    CORE_MODULES_AVAILABLE = False
    
    # Fallback için eski enum'ları kullan
    class ThemeMode(Enum):
        """Tema modları"""
        LIGHT = "light"
        DARK = "dark"
        MONOKAI = "monokai"
        DRACULA = "dracula"

    @dataclass
    class ProjectTemplate:
        """Proje şablonu"""
        name: str
        description: str
        template_dir: str
        main_file: str
        files: List[str]
        dependencies: List[str] = None
        category: str = "General"

    @dataclass
    class CodeSnippet:
        """Kod parçacığı"""
        name: str
        trigger: str
        code: str
        description: str
        language: str = "python"

    @dataclass
    class DebugBreakpoint:
        """Debug breakpoint"""
        file_path: str
        line_number: int
        enabled: bool = True
        condition: str = ""

# Terminal ve FilePicker modül kontrolü
try:
    from cloud.terminal import CloudTerminal
    TERMINAL_AVAILABLE = True
except ImportError:
    TERMINAL_AVAILABLE = False

try:
    from cloud.filepicker import CloudFilePicker, FilePickerFilter
    FILEPICKER_AVAILABLE = True
except ImportError:
    FILEPICKER_AVAILABLE = False

class ModernSyntaxHighlighter(QSyntaxHighlighter):
    """Modern Python kod renklendirici"""
    
    def __init__(self, parent=None, theme_mode: ThemeMode = ThemeMode.DARK):
        super().__init__(parent)
        self.theme_mode = theme_mode
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """Renklendirme kurallarını kur"""
        self.highlighting_rules = []
        
        # Tema renklerini ayarla
        if self.theme_mode == ThemeMode.DARK:
            colors = {
                'keyword': '#569cd6',
                'string': '#ce9178',
                'comment': '#6a9955',
                'number': '#b5cea8',
                'function': '#dcdcaa',
                'class': '#4ec9b0',
                'decorator': '#ffd700',
                'builtin': '#569cd6'
            }
        elif self.theme_mode == ThemeMode.MONOKAI:
            colors = {
                'keyword': '#f92672',
                'string': '#e6db74',
                'comment': '#75715e',
                'number': '#ae81ff',
                'function': '#a6e22e',
                'class': '#66d9ef',
                'decorator': '#fd971f',
                'builtin': '#f92672'
            }
        elif self.theme_mode == ThemeMode.DRACULA:
            colors = {
                'keyword': '#ff79c6',
                'string': '#f1fa8c',
                'comment': '#6272a4',
                'number': '#bd93f9',
                'function': '#50fa7b',
                'class': '#8be9fd',
                'decorator': '#ffb86c',
                'builtin': '#ff79c6'
            }
        else:  # LIGHT
            colors = {
                'keyword': '#0000ff',
                'string': '#008000',
                'comment': '#808080',
                'number': '#800080',
                'function': '#000080',
                'class': '#008080',
                'decorator': '#ff8000',
                'builtin': '#0000ff'
            }
        
        # Python anahtar kelimeleri
        keyword_format = QTextCharFormat()
        keyword_format.setColor(QColor(colors['keyword']))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'exec', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'not', 'or', 'pass', 'print', 'raise', 'return', 'try',
            'while', 'with', 'yield', 'async', 'await', 'nonlocal'
        ]
        
        for keyword in keywords:
            pattern = f'\\b{keyword}\\b'
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Built-in fonksiyonlar
        builtin_format = QTextCharFormat()
        builtin_format.setColor(QColor(colors['builtin']))
        
        builtins = [
            'None', 'True', 'False', 'len', 'str', 'int', 'float', 'list',
            'dict', 'tuple', 'set', 'range', 'enumerate', 'zip', 'map',
            'filter', 'sum', 'max', 'min', 'abs', 'round', 'sorted',
            'reversed', 'any', 'all', 'isinstance', 'hasattr', 'getattr',
            'setattr', 'delattr', 'type', 'super', 'property', 'staticmethod',
            'classmethod', 'open', 'print', 'input'
        ]
        
        for builtin in builtins:
            pattern = f'\\b{builtin}\\b'
            self.highlighting_rules.append((pattern, builtin_format))
        
        # Stringler
        string_format = QTextCharFormat()
        string_format.setColor(QColor(colors['string']))
        self.highlighting_rules.append((r'"[^"\\\\]*(\\\\.[^"\\\\]*)*"', string_format))
        self.highlighting_rules.append((r"'[^'\\\\]*(\\\\.[^'\\\\]*)*'", string_format))
        self.highlighting_rules.append((r'""".*?"""', string_format))
        self.highlighting_rules.append((r"'''.*?'''", string_format))
        
        # f-strings
        fstring_format = QTextCharFormat()
        fstring_format.setColor(QColor(colors['string']))
        fstring_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'f"[^"\\\\]*(\\\\.[^"\\\\]*)*"', fstring_format))
        self.highlighting_rules.append((r"f'[^'\\\\]*(\\\\.[^'\\\\]*)*'", fstring_format))
        
        # Yorumlar
        comment_format = QTextCharFormat()
        comment_format.setColor(QColor(colors['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((r'#[^\\n]*', comment_format))
        
        # Sayılar
        number_format = QTextCharFormat()
        number_format.setColor(QColor(colors['number']))
        self.highlighting_rules.append((r'\\b\\d+\\.?\\d*\\b', number_format))
        self.highlighting_rules.append((r'\\b0x[0-9a-fA-F]+\\b', number_format))
        self.highlighting_rules.append((r'\\b0o[0-7]+\\b', number_format))
        self.highlighting_rules.append((r'\\b0b[01]+\\b', number_format))
        
        # Fonksiyonlar
        function_format = QTextCharFormat()
        function_format.setColor(QColor(colors['function']))
        self.highlighting_rules.append((r'\\b[A-Za-z_][A-Za-z0-9_]*(?=\\()', function_format))
        
        # Sınıflar
        class_format = QTextCharFormat()
        class_format.setColor(QColor(colors['class']))
        class_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'\\bclass\\s+([A-Za-z_][A-Za-z0-9_]*)', class_format))
        
        # Decoratorler
        decorator_format = QTextCharFormat()
        decorator_format.setColor(QColor(colors['decorator']))
        decorator_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'@[A-Za-z_][A-Za-z0-9_]*', decorator_format))
    
    def highlightBlock(self, text):
        """Blok renklendirme"""
        import re
        for pattern, format_obj in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format_obj)
    
    def set_theme(self, theme_mode: ThemeMode):
        """Tema değiştir"""
        self.theme_mode = theme_mode
        self.setup_highlighting_rules()
        self.rehighlight()

if PYQT_AVAILABLE:
    class ModernCodeEditor(QPlainTextEdit):
        """Modern kod editörü"""
        
        def __init__(self, parent=None, theme_mode: ThemeMode = ThemeMode.DARK):
            super().__init__(parent)
            self.theme_mode = theme_mode
            self.line_number_area = LineNumberArea(self)
            self.highlighter = ModernSyntaxHighlighter(self.document(), theme_mode)
            self.breakpoints: Set[int] = set()
            self.current_line = -1
            
            self.setup_editor()
            self.setup_connections()
        
        def setup_editor(self):
            """Editör ayarlarını kur"""
            # Modern font
            editor_font = QFont("Fira Code", 13)
            if not editor_font.exactMatch():
                editor_font = QFont("JetBrains Mono", 13)
                if not editor_font.exactMatch():
                    editor_font = QFont("Consolas", 13)
                    if not editor_font.exactMatch():
                        editor_font = QFont("Courier", 13)
            
            editor_font.setStyleHint(QFont.StyleHint.Monospace)
            self.setFont(editor_font)
            
            # Tab ayarları
            self.setTabStopDistance(40)  # 4 spaces
            
            # Satır numaraları için alan
            self.update_line_number_area_width()
            
            self.apply_theme()
        
        def apply_theme(self):
            """Tema uygula"""
            if self.theme_mode == ThemeMode.DARK:
                self.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #1e1e1e;
                        color: #d4d4d4;
                        border: 1px solid #404040;
                        border-radius: 8px;
                        padding: 8px;
                        selection-background-color: #264f78;
                        selection-color: #ffffff;
                        font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                        font-size: 13px;
                        line-height: 1.6;
                    }
                """)
            elif self.theme_mode == ThemeMode.MONOKAI:
                self.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #272822;
                        color: #f8f8f2;
                        border: 1px solid #49483e;
                        border-radius: 8px;
                        padding: 8px;
                        selection-background-color: #49483e;
                        selection-color: #f8f8f2;
                        font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                        font-size: 13px;
                        line-height: 1.6;
                    }
                """)
            elif self.theme_mode == ThemeMode.DRACULA:
                self.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #282a36;
                        color: #f8f8f2;
                        border: 1px solid #44475a;
                        border-radius: 8px;
                        padding: 8px;
                        selection-background-color: #44475a;
                        selection-color: #f8f8f2;
                        font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                        font-size: 13px;
                        line-height: 1.6;
                    }
                """)
            else:  # LIGHT
                self.setStyleSheet("""
                    QPlainTextEdit {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 8px;
                        selection-background-color: #b3d4fc;
                        selection-color: #000000;
                        font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                        font-size: 13px;
                        line-height: 1.6;
                    }
                """)
        
        def setup_connections(self):
            """Sinyal bağlantıları"""
            self.blockCountChanged.connect(self.update_line_number_area_width)
            self.updateRequest.connect(self.update_line_number_area)
            self.cursorPositionChanged.connect(self.highlight_current_line)
        
        def set_theme(self, theme_mode: ThemeMode):
            """Tema değiştir"""
            self.theme_mode = theme_mode
            self.highlighter.set_theme(theme_mode)
            self.apply_theme()
            self.line_number_area.update()
        
        def line_number_area_width(self):
            """Satır numarası alanı genişliği"""
            digits = 1
            max_num = max(1, self.blockCount())
            while max_num >= 10:
                max_num //= 10
                digits += 1
            
            space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
            return space
        
        def update_line_number_area_width(self):
            """Satır numarası alanı genişliğini güncelle"""
            self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
        def update_line_number_area(self, rect, dy):
            """Satır numarası alanını güncelle"""
            if dy:
                self.line_number_area.scroll(0, dy)
            else:
                self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
            if rect.contains(self.viewport().rect()):
                self.update_line_number_area_width()
        
        def resizeEvent(self, event):
            """Yeniden boyutlandırma"""
            super().resizeEvent(event)
            cr = self.contentsRect()
            self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        
        def line_number_area_paint_event(self, event):
            """Satır numarası alanı çizimi"""
            painter = QPainter(self.line_number_area)
            
            if self.theme_mode == ThemeMode.DARK:
                painter.fillRect(event.rect(), QColor("#252526"))
                painter.setPen(QColor("#858585"))
            elif self.theme_mode == ThemeMode.MONOKAI:
                painter.fillRect(event.rect(), QColor("#3e3d32"))
                painter.setPen(QColor("#75715e"))
            elif self.theme_mode == ThemeMode.DRACULA:
                painter.fillRect(event.rect(), QColor("#44475a"))
                painter.setPen(QColor("#6272a4"))
            else:  # LIGHT
                painter.fillRect(event.rect(), QColor("#f5f5f5"))
                painter.setPen(QColor("#666666"))
            
            block = self.firstVisibleBlock()
            block_number = block.blockNumber()
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            bottom = top + self.blockBoundingRect(block).height()
            
            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    number = str(block_number + 1)
                    
                    # Breakpoint kontrolü
                    if (block_number + 1) in self.breakpoints:
                        painter.fillRect(0, int(top), self.line_number_area.width(), 
                                       self.fontMetrics().height(), QColor("#ff0000"))
                        painter.setPen(QColor("#ffffff"))
                    
                    painter.drawText(0, int(top), self.line_number_area.width(), 
                                   self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
                
                block = block.next()
                top = bottom
                bottom = top + self.blockBoundingRect(block).height()
                block_number += 1
        
        def highlight_current_line(self):
            """Mevcut satırı vurgula"""
            extra_selections = []
            
            if not self.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                
                if self.theme_mode == ThemeMode.DARK:
                    line_color = QColor("#2a2d2e")
                elif self.theme_mode == ThemeMode.MONOKAI:
                    line_color = QColor("#3e3d32")
                elif self.theme_mode == ThemeMode.DRACULA:
                    line_color = QColor("#44475a")
                else:  # LIGHT
                    line_color = QColor("#f0f0f0")
                
                selection.format.setBackground(line_color)
                selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                selection.cursor = self.textCursor()
                selection.cursor.clearSelection()
                extra_selections.append(selection)
            
            self.setExtraSelections(extra_selections)
        
        def toggle_breakpoint(self, line_number: int):
            """Breakpoint aç/kapat"""
            if line_number in self.breakpoints:
                self.breakpoints.remove(line_number)
            else:
                self.breakpoints.add(line_number)
            self.line_number_area.update()
        
        def mousePressEvent(self, event):
            """Mouse tıklama"""
            if event.button() == Qt.MouseButton.LeftButton:
                # Satır numarası alanında tıklama - breakpoint toggle
                if event.x() < self.line_number_area_width():
                    cursor = self.cursorForPosition(event.pos())
                    line_number = cursor.blockNumber() + 1
                    self.toggle_breakpoint(line_number)
                    return
            
            super().mousePressEvent(event)
    
    class LineNumberArea(QWidget):
        """Satır numarası alanı"""
        
        def __init__(self, editor):
            super().__init__(editor)
            self.code_editor = editor
        
        def sizeHint(self):
            return QSize(self.code_editor.line_number_area_width(), 0)
        
        def paintEvent(self, event):
            self.code_editor.line_number_area_paint_event(event)
    
    class ModernProjectExplorer(QTreeWidget):
        """Modern proje gezgini"""
        
        file_opened = pyqtSignal(str)
        
        def __init__(self, parent=None, theme_mode: ThemeMode = ThemeMode.DARK):
            super().__init__(parent)
            self.theme_mode = theme_mode
            self.setup_explorer()
        
        def setup_explorer(self):
            """Gezgini kur"""
            self.setHeaderLabel("📁 Proje Dosyaları")
            self.setRootIsDecorated(True)
            self.setIndentation(20)
            
            self.apply_theme()
            self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        def apply_theme(self):
            """Tema uygula"""
            if self.theme_mode == ThemeMode.DARK:
                self.setStyleSheet("""
                    QTreeWidget {
                        background-color: #252526;
                        color: #cccccc;
                        border: none;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 13px;
                    }
                    QTreeWidget::item {
                        padding: 6px 4px;
                        border-radius: 4px;
                        margin: 1px;
                    }
                    QTreeWidget::item:hover {
                        background-color: #2a2d2e;
                    }
                    QTreeWidget::item:selected {
                        background-color: #37373d;
                        color: #ffffff;
                    }
                    QTreeWidget::branch:has-siblings:!adjoins-item {
                        border-image: none;
                        border: none;
                    }
                    QTreeWidget::branch:has-siblings:adjoins-item {
                        border-image: none;
                        border: none;
                    }
                    QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                        border-image: none;
                        border: none;
                    }
                """)
            elif self.theme_mode == ThemeMode.MONOKAI:
                self.setStyleSheet("""
                    QTreeWidget {
                        background-color: #3e3d32;
                        color: #f8f8f2;
                        border: none;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 13px;
                    }
                    QTreeWidget::item {
                        padding: 6px 4px;
                        border-radius: 4px;
                        margin: 1px;
                    }
                    QTreeWidget::item:hover {
                        background-color: #49483e;
                    }
                    QTreeWidget::item:selected {
                        background-color: #75715e;
                        color: #f8f8f2;
                    }
                """)
            elif self.theme_mode == ThemeMode.DRACULA:
                self.setStyleSheet("""
                    QTreeWidget {
                        background-color: #44475a;
                        color: #f8f8f2;
                        border: none;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 13px;
                    }
                    QTreeWidget::item {
                        padding: 6px 4px;
                        border-radius: 4px;
                        margin: 1px;
                    }
                    QTreeWidget::item:hover {
                        background-color: #6272a4;
                    }
                    QTreeWidget::item:selected {
                        background-color: #bd93f9;
                        color: #282a36;
                    }
                """)
            else:  # LIGHT
                self.setStyleSheet("""
                    QTreeWidget {
                        background-color: #f8f9fa;
                        color: #212529;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 13px;
                    }
                    QTreeWidget::item {
                        padding: 6px 4px;
                        border-radius: 4px;
                        margin: 1px;
                    }
                    QTreeWidget::item:hover {
                        background-color: #e3f2fd;
                    }
                    QTreeWidget::item:selected {
                        background-color: #2196f3;
                        color: #ffffff;
                    }
                """)
        
        def set_theme(self, theme_mode: ThemeMode):
            """Tema değiştir"""
            self.theme_mode = theme_mode
            self.apply_theme()
        
        def load_project(self, project_path: str):
            """Projeyi yükle"""
            self.clear()
            
            root_item = QTreeWidgetItem(self)
            root_item.setText(0, f"📁 {Path(project_path).name}")
            root_item.setData(0, Qt.ItemDataRole.UserRole, project_path)
            
            self.load_directory(project_path, root_item)
            root_item.setExpanded(True)
        
        def load_directory(self, dir_path: str, parent_item: QTreeWidgetItem):
            """Dizini yükle"""
            try:
                path = Path(dir_path)
                
                # Önce dizinleri, sonra dosyaları ekle
                items = list(path.iterdir())
                dirs = [item for item in items if item.is_dir() and not item.name.startswith('.')]
                files = [item for item in items if item.is_file() and not item.name.startswith('.')]
                
                # Dizinleri ekle
                for item in sorted(dirs):
                    tree_item = QTreeWidgetItem(parent_item)
                    tree_item.setText(0, f"📁 {item.name}")
                    tree_item.setData(0, Qt.ItemDataRole.UserRole, str(item))
                    self.load_directory(str(item), tree_item)
                
                # Dosyaları ekle
                for item in sorted(files):
                    tree_item = QTreeWidgetItem(parent_item)
                    tree_item.setData(0, Qt.ItemDataRole.UserRole, str(item))
                    
                    # Dosya türüne göre ikon
                    if item.suffix == '.py':
                        tree_item.setText(0, f"🐍 {item.name}")
                    elif item.suffix in ['.txt', '.md', '.rst']:
                        tree_item.setText(0, f"📄 {item.name}")
                    elif item.suffix in ['.json', '.yaml', '.yml', '.toml']:
                        tree_item.setText(0, f"⚙️ {item.name}")
                    elif item.suffix in ['.html', '.css', '.js']:
                        tree_item.setText(0, f"🌐 {item.name}")
                    elif item.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                        tree_item.setText(0, f"🖼️ {item.name}")
                    elif item.suffix in ['.zip', '.tar', '.gz']:
                        tree_item.setText(0, f"📦 {item.name}")
                    elif item.name in ['requirements.txt', 'setup.py', 'pyproject.toml']:
                        tree_item.setText(0, f"📋 {item.name}")
                    elif item.name in ['.gitignore', 'README.md', 'LICENSE']:
                        tree_item.setText(0, f"📋 {item.name}")
                    else:
                        tree_item.setText(0, f"📄 {item.name}")
            
            except Exception as e:
                logging.getLogger("ProjectExplorer").error(f"Failed to load directory: {e}")
        
        def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
            """Öğe çift tıklandı"""
            file_path = item.data(0, Qt.ItemDataRole.UserRole)
            if file_path and Path(file_path).is_file():
                self.file_opened.emit(file_path)
    
    class ModernOutputPanel(QTextEdit):
        """Modern çıktı paneli"""
        
        def __init__(self, parent=None, theme_mode: ThemeMode = ThemeMode.DARK):
            super().__init__(parent)
            self.theme_mode = theme_mode
            self.setup_panel()
        
        def setup_panel(self):
            """Panel kurulumu"""
            self.setReadOnly(True)
            self.setFont(QFont("Consolas", 11))
            self.apply_theme()
        
        def apply_theme(self):
            """Tema uygula"""
            if self.theme_mode == ThemeMode.DARK:
                self.setStyleSheet("""
                    QTextEdit {
                        background-color: #1e1e1e;
                        color: #d4d4d4;
                        border: 1px solid #404040;
                        border-radius: 8px;
                        padding: 8px;
                        font-family: 'Consolas', monospace;
                        font-size: 11px;
                    }
                """)
            elif self.theme_mode == ThemeMode.MONOKAI:
                self.setStyleSheet("""
                    QTextEdit {
                        background-color: #272822;
                        color: #f8f8f2;
                        border: 1px solid #49483e;
                        border-radius: 8px;
                        padding: 8px;
                        font-family: 'Consolas', monospace;
                        font-size: 11px;
                    }
                """)
            elif self.theme_mode == ThemeMode.DRACULA:
                self.setStyleSheet("""
                    QTextEdit {
                        background-color: #282a36;
                        color: #f8f8f2;
                        border: 1px solid #44475a;
                        border-radius: 8px;
                        padding: 8px;
                        font-family: 'Consolas', monospace;
                        font-size: 11px;
                    }
                """)
            else:  # LIGHT
                self.setStyleSheet("""
                    QTextEdit {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 8px;
                        font-family: 'Consolas', monospace;
                        font-size: 11px;
                    }
                """)
        
        def set_theme(self, theme_mode: ThemeMode):
            """Tema değiştir"""
            self.theme_mode = theme_mode
            self.apply_theme()
        
        def append_output(self, text: str, color: str = None):
            """Çıktı ekle"""
            if color:
                self.setTextColor(QColor(color))
            else:
                if self.theme_mode == ThemeMode.DARK:
                    self.setTextColor(QColor("#d4d4d4"))
                else:
                    self.setTextColor(QColor("#000000"))
            
            self.append(text)
            self.ensureCursorVisible()
        
        def append_error(self, text: str):
            """Hata mesajı ekle"""
            self.append_output(text, "#ff6b6b")
        
        def append_success(self, text: str):
            """Başarı mesajı ekle"""
            self.append_output(text, "#51cf66")
        
        def append_warning(self, text: str):
            """Uyarı mesajı ekle"""
            self.append_output(text, "#ffd43b")
    
    class RunWorker(QThread):
        """Kod çalıştırma worker'ı"""
        
        output_ready = pyqtSignal(str, str)  # text, color
        finished = pyqtSignal()
        
        def __init__(self, file_path: str, working_dir: str, python_path: str = "python"):
            super().__init__()
            self.file_path = file_path
            self.working_dir = working_dir
            self.python_path = python_path
        
        def run(self):
            """Kodu çalıştır"""
            try:
                self.output_ready.emit(f"🚀 Çalıştırılıyor: {self.file_path}\\n", "#51cf66")
                
                process = subprocess.Popen(
                    [self.python_path, self.file_path],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Çıktıyı gerçek zamanlı oku
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.output_ready.emit(output.strip(), "#d4d4d4")
                
                # Hata çıktısını oku
                stderr_output = process.stderr.read()
                if stderr_output:
                    self.output_ready.emit(stderr_output, "#ff6b6b")
                
                # Sonuç
                return_code = process.poll()
                if return_code == 0:
                    self.output_ready.emit("\\n✅ Başarıyla tamamlandı", "#51cf66")
                else:
                    self.output_ready.emit(f"\\n❌ Hata kodu: {return_code}", "#ff6b6b")
                
            except Exception as e:
                self.output_ready.emit(f"❌ Çalıştırma hatası: {e}", "#ff6b6b")
            
            finally:
                self.finished.emit()
    
    class SnippetManager:
        """Kod parçacığı yöneticisi"""
        
        def __init__(self):
            self.snippets: List[CodeSnippet] = []
            self.load_default_snippets()
        
        def load_default_snippets(self):
            """Varsayılan kod parçacıklarını yükle"""
            default_snippets = [
                CodeSnippet(
                    name="Main Function",
                    trigger="main",
                    code='if __name__ == "__main__":\\n    main()',
                    description="Ana fonksiyon şablonu"
                ),
                CodeSnippet(
                    name="Class Definition",
                    trigger="class",
                    code='class ${1:ClassName}:\\n    def __init__(self):\\n        pass',
                    description="Sınıf tanımı şablonu"
                ),
                CodeSnippet(
                    name="Function Definition",
                    trigger="def",
                    code='def ${1:function_name}(${2:args}):\\n    """${3:Description}"""\\n    pass',
                    description="Fonksiyon tanımı şablonu"
                ),
                CodeSnippet(
                    name="Try-Except Block",
                    trigger="try",
                    code='try:\\n    ${1:code}\\nexcept ${2:Exception} as e:\\n    ${3:handle_exception}',
                    description="Try-except bloku"
                ),
                CodeSnippet(
                    name="For Loop",
                    trigger="for",
                    code='for ${1:item} in ${2:iterable}:\\n    ${3:code}',
                    description="For döngüsü"
                ),
                CodeSnippet(
                    name="List Comprehension",
                    trigger="lc",
                    code='[${1:expression} for ${2:item} in ${3:iterable}]',
                    description="Liste anlama"
                ),
                CodeSnippet(
                    name="Import Statement",
                    trigger="imp",
                    code='import ${1:module}',
                    description="Import ifadesi"
                ),
                CodeSnippet(
                    name="From Import",
                    trigger="from",
                    code='from ${1:module} import ${2:name}',
                    description="From import ifadesi"
                )
            ]
            
            self.snippets.extend(default_snippets)
        
        def get_snippet_by_trigger(self, trigger: str) -> Optional[CodeSnippet]:
            """Trigger'a göre snippet bul"""
            for snippet in self.snippets:
                if snippet.trigger == trigger:
                    return snippet
            return None
        
        def expand_snippet(self, snippet: CodeSnippet) -> str:
            """Snippet'i genişlet"""
            # Basit placeholder değiştirme
            code = snippet.code
            code = code.replace('${1:ClassName}', 'ClassName')
            code = code.replace('${1:function_name}', 'function_name')
            code = code.replace('${2:args}', 'args')
            code = code.replace('${3:Description}', 'Description')
            code = code.replace('${1:code}', 'code')
            code = code.replace('${2:Exception}', 'Exception')
            code = code.replace('${3:handle_exception}', 'handle_exception')
            code = code.replace('${1:item}', 'item')
            code = code.replace('${2:iterable}', 'iterable')
            code = code.replace('${3:code}', 'code')
            code = code.replace('${1:expression}', 'expression')
            code = code.replace('${1:module}', 'module')
            code = code.replace('${2:name}', 'name')
            code = code.replace('\\n', '\n')
            return code

    class ModernCloudPyIDE(QMainWindow):
        """Modern PyCloud Python IDE"""
        
        def __init__(self, kernel=None):
            super().__init__()
            self.kernel = kernel
            self.logger = logging.getLogger("CloudPyIDE")
            
            # VFS ve Bridge entegrasyonu
            self.bridge_client = None
            self.vfs = None
            self.fs = None
            self.launcher = None
            self.setup_system_integration()
            
            # Core modüller
            if CORE_MODULES_AVAILABLE:
                # Yeni core modüllerini kullan
                self.theme_manager = ThemeManager()
                self.autocomplete_engine = AutoCompleteEngine()
                self.snippet_manager = SnippetManager()
                self.code_runner = CodeRunner()
                self.plugin_manager = PluginManager(self)
                self.debug_manager = DebugManager(self)
                self.template_manager = TemplateManager(self)
                
                # Tema modunu ayarla
                self.theme_mode = self.detect_theme_mode()
                self.theme_manager.set_theme(self.theme_mode.value)
                
                # Code runner callback'lerini ayarla
                self.code_runner.set_output_callback(self.on_code_output)
                self.code_runner.set_finished_callback(self.on_code_finished)
                
                self.logger.info("✅ Yeni core modüller yüklendi")
            else:
                # Fallback: eski modülleri kullan
                self.theme_mode = self.detect_theme_mode()
                self.snippet_manager = SnippetManager()
                self.plugin_manager = PluginManager(self)
                self.app_compiler = AppCompiler(self)
                
                self.logger.warning("⚠️ Fallback modüller kullanılıyor")
            
            # Proje ve dosya yönetimi
            self.current_project_path = None
            self.open_files: Dict[str, ModernCodeEditor] = {}
            self.run_worker = None
            
            # Terminal entegrasyonu
            self.terminal_widget = None
            if TERMINAL_AVAILABLE:
                try:
                    self.terminal_widget = CloudTerminal(kernel=self.kernel)
                    self.logger.info("✅ Terminal widget oluşturuldu")
                except Exception as e:
                    self.logger.warning(f"⚠️ Terminal widget oluşturulamadı: {e}")
                    self.terminal_widget = None
            
            # Autosave sistemi
            self.autosave_timer = QTimer()
            self.autosave_timer.timeout.connect(self.auto_save)
            self.autosave_timer.start(60000)  # 60 saniye
            
            # UI kurulumu
            self.setup_ui()
            self.setup_menu()
            self.setup_toolbar()
            self.setup_statusbar()
            self.setup_connections()
            
            # Template'leri yükle
            if CORE_MODULES_AVAILABLE:
                # Yeni template manager kullan
                pass  # Template manager kendi template'lerini yükler
            else:
                # Eski template sistemi
                self.load_templates()
            
            # Tema uygula
            self.apply_theme()
            
            self.logger.info("Modern CloudPyIDE initialized with full system integration")
        
        def setup_system_integration(self):
            """Sistem entegrasyonu kurulumu"""
            try:
                # Bridge IPC client ile bağlan
                from core.bridge import BridgeIPCClient
                
                self.bridge_client = BridgeIPCClient()
                
                if self.kernel:
                    # VFS modülünü al
                    self.vfs = self.kernel.get_module('vfs')
                    self.fs = self.kernel.get_module('fs')
                    self.launcher = self.kernel.get_module('launcher')
                    
                    if self.vfs:
                        # PyIDE için app profili kontrol et/oluştur
                        profile_success, profile_result = self.bridge_client.call_module_method(
                            'vfs', 'get_app_profile', 'cloud_pyide'
                        )
                        
                        if not profile_success:
                            # Profil yoksa oluştur
                            create_success, create_result = self.bridge_client.call_module_method(
                                'vfs', 'create_app_profile',
                                'cloud_pyide',
                                ['/home', '/apps', '/temp'],  # allowed_mounts
                                {
                                    '/home': ['read', 'write', 'delete'],
                                    '/apps': ['read', 'execute'],
                                    '/temp': ['read', 'write', 'delete']
                                },  # permissions
                                True,  # sandbox_mode
                                'Python IDE - proje geliştirme'  # description
                            )
                            
                            if create_success:
                                self.logger.info("✅ PyIDE VFS profili oluşturuldu")
                            else:
                                self.logger.warning(f"⚠️ VFS profili oluşturulamadı: {create_result}")
                        else:
                            self.logger.info("✅ PyIDE VFS profili mevcut")
                        
                        self.logger.info("✅ PyIDE VFS entegrasyonu başarılı")
                    else:
                        self.logger.warning("⚠️ VFS modülü bulunamadı")
                    
                    if self.launcher:
                        # PyIDE'yi launcher'a kaydet
                        self.launcher.register_app_handler('cloud_pyide', self.handle_launcher_request)
                        self.logger.info("✅ PyIDE launcher entegrasyonu başarılı")
                    else:
                        self.logger.warning("⚠️ Launcher modülü bulunamadı")
                        
                else:
                    self.logger.warning("⚠️ Kernel referansı alınamadı")
                    
            except ImportError:
                self.logger.warning("⚠️ Bridge modülü bulunamadı - VFS entegrasyonu devre dışı")
                self.bridge_client = None
                self.vfs = None
                self.fs = None
                self.launcher = None
            except Exception as e:
                self.logger.error(f"❌ Sistem entegrasyon hatası: {e}")
                self.bridge_client = None
                self.vfs = None
                self.fs = None
                self.launcher = None
        
        def handle_launcher_request(self, action: str, **kwargs):
            """Launcher'dan gelen istekleri işle"""
            try:
                if action == "open_file":
                    file_path = kwargs.get("file_path")
                    if file_path:
                        self.open_file_in_editor(file_path)
                        self.show()
                        self.raise_()
                        self.activateWindow()
                        self.logger.info(f"📂 Launcher'dan dosya açıldı: {file_path}")
                        return True
                
                elif action == "open_project":
                    project_path = kwargs.get("project_path")
                    if project_path:
                        self.current_project_path = project_path
                        self.project_explorer.load_project(project_path)
                        self.show()
                        self.raise_()
                        self.activateWindow()
                        self.logger.info(f"📁 Launcher'dan proje açıldı: {project_path}")
                        return True
                
                elif action == "new_file":
                    self.new_file()
                    self.show()
                    self.raise_()
                    self.activateWindow()
                    self.logger.info("📄 Launcher'dan yeni dosya oluşturuldu")
                    return True
                
                else:
                    self.logger.warning(f"⚠️ Bilinmeyen launcher action: {action}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"❌ Launcher request işleme hatası: {e}")
                return False
        
        def detect_theme_mode(self) -> ThemeMode:
            """Tema modunu algıla"""
            try:
                if self.kernel:
                    config = self.kernel.get_module("config")
                    if config:
                        theme_config = config.get("theme", {})
                        theme_name = theme_config.get("pyide_theme", "dark")
                        return ThemeMode(theme_name)
                
                # Varsayılan
                return ThemeMode.DARK
                
            except Exception:
                return ThemeMode.DARK
        
        def setup_ui(self):
            """Modern UI kurulumu"""
            self.setWindowTitle("🐍 Cloud PyIDE - Modern Python IDE")
            self.setGeometry(100, 100, 1600, 1000)
            
            # Ana widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Ana layout
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(8)
            
            # Sol panel (Proje gezgini)
            left_panel = QWidget()
            left_panel.setFixedWidth(300)
            left_layout = QVBoxLayout(left_panel)
            left_layout.setContentsMargins(0, 0, 0, 0)
            
            # Proje gezgini
            if CORE_MODULES_AVAILABLE:
                # Yeni ProjectExplorer kullan
                self.project_explorer = ProjectExplorer(theme_mode=self.theme_mode.value)
            else:
                # Fallback: eski ModernProjectExplorer kullan
                self.project_explorer = ModernProjectExplorer(theme_mode=self.theme_mode)
            
            left_layout.addWidget(self.project_explorer)
            main_layout.addWidget(left_panel)
            
            # Orta panel (Editor + Alt panel)
            center_panel = QWidget()
            center_layout = QVBoxLayout(center_panel)
            center_layout.setContentsMargins(0, 0, 0, 0)
            center_layout.setSpacing(8)
            
            # Editor sekmeler
            self.editor_tabs = QTabWidget()
            self.editor_tabs.setTabsClosable(True)
            self.editor_tabs.setMovable(True)
            self.editor_tabs.setDocumentMode(True)
            self.editor_tabs.tabCloseRequested.connect(self.close_file)
            center_layout.addWidget(self.editor_tabs, 1)
            
            # Alt panel (Çıktı + Debug)
            bottom_tabs = QTabWidget()
            bottom_tabs.setFixedHeight(250)
            
            # Çıktı paneli
            self.output_panel = ModernOutputPanel(theme_mode=self.theme_mode)
            bottom_tabs.addTab(self.output_panel, "📤 Çıktı")
            
            # Debug paneli
            if CORE_MODULES_AVAILABLE and hasattr(self, 'debug_manager'):
                # Yeni debug manager kullan
                debug_widget = self.debug_manager.get_debug_panel()
                if debug_widget:
                    bottom_tabs.addTab(debug_widget, "🐛 Debug")
                else:
                    # Fallback
                    self.debug_panel = QTextEdit()
                    self.debug_panel.setReadOnly(True)
                    bottom_tabs.addTab(self.debug_panel, "🐛 Debug")
            else:
                # Fallback: eski debug paneli
                self.debug_panel = QTextEdit()
                self.debug_panel.setReadOnly(True)
                bottom_tabs.addTab(self.debug_panel, "🐛 Debug")
            
            # Terminal paneli
            if self.terminal_widget:
                # Gerçek terminal widget'ı kullan
                bottom_tabs.addTab(self.terminal_widget, "💻 Terminal")
                self.logger.info("✅ Terminal paneli eklendi")
            else:
                # Fallback: placeholder
                self.terminal_panel = QTextEdit()
                self.terminal_panel.setReadOnly(True)
                self.terminal_panel.setPlaceholderText("Terminal modülü yüklenmedi. Çıktı panelini kullanın.")
                self.terminal_panel.setStyleSheet("""
                    QTextEdit {
                        background-color: #1e1e1e;
                        color: #888888;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 12px;
                    }
                """)
                bottom_tabs.addTab(self.terminal_panel, "💻 Terminal")
                self.logger.info("⚠️ Terminal placeholder eklendi")
            
            center_layout.addWidget(bottom_tabs)
            main_layout.addWidget(center_panel, 1)
            
            # Sağ panel (Outline + Değişkenler)
            right_panel = QWidget()
            right_panel.setFixedWidth(250)
            right_layout = QVBoxLayout(right_panel)
            right_layout.setContentsMargins(0, 0, 0, 0)
            
            right_tabs = QTabWidget()
            
            # Outline
            self.outline_tree = QTreeWidget()
            self.outline_tree.setHeaderLabel("📋 Outline")
            right_tabs.addTab(self.outline_tree, "Outline")
            
            # Değişkenler
            self.variables_tree = QTreeWidget()
            self.variables_tree.setHeaderLabel("🔢 Değişkenler")
            right_tabs.addTab(self.variables_tree, "Variables")
            
            right_layout.addWidget(right_tabs)
            main_layout.addWidget(right_panel)
        
        def setup_menu(self):
            """Modern menü çubuğu"""
            menubar = self.menuBar()
            
            # Dosya menüsü
            file_menu = menubar.addMenu("📁 Dosya")
            
            # Yeni proje
            new_project_action = QAction("🆕 Yeni Proje", self)
            new_project_action.setShortcut("Ctrl+Shift+N")
            new_project_action.triggered.connect(self.new_project)
            file_menu.addAction(new_project_action)
            
            # Proje aç
            open_project_action = QAction("📂 Proje Aç", self)
            open_project_action.setShortcut("Ctrl+Shift+O")
            open_project_action.triggered.connect(self.open_project)
            file_menu.addAction(open_project_action)
            
            file_menu.addSeparator()
            
            # Yeni dosya
            new_file_action = QAction("📄 Yeni Dosya", self)
            new_file_action.setShortcut("Ctrl+N")
            new_file_action.triggered.connect(self.new_file)
            file_menu.addAction(new_file_action)
            
            # Dosya aç
            open_file_action = QAction("📂 Dosya Aç", self)
            open_file_action.setShortcut("Ctrl+O")
            open_file_action.triggered.connect(self.open_file)
            file_menu.addAction(open_file_action)
            
            # Kaydet
            save_action = QAction("💾 Kaydet", self)
            save_action.setShortcut("Ctrl+S")
            save_action.triggered.connect(self.save_current_file)
            file_menu.addAction(save_action)
            
            # Farklı kaydet
            save_as_action = QAction("💾 Farklı Kaydet", self)
            save_as_action.setShortcut("Ctrl+Shift+S")
            save_as_action.triggered.connect(self.save_as_file)
            file_menu.addAction(save_as_action)
            
            # Düzenle menüsü
            edit_menu = menubar.addMenu("✏️ Düzenle")
            
            # Geri al
            undo_action = QAction("↶ Geri Al", self)
            undo_action.setShortcut("Ctrl+Z")
            undo_action.triggered.connect(self.undo_text)
            edit_menu.addAction(undo_action)
            
            # İleri al
            redo_action = QAction("↷ İleri Al", self)
            redo_action.setShortcut("Ctrl+Y")
            redo_action.triggered.connect(self.redo_text)
            edit_menu.addAction(redo_action)
            
            edit_menu.addSeparator()
            
            # Kes
            cut_action = QAction("✂️ Kes", self)
            cut_action.setShortcut("Ctrl+X")
            cut_action.triggered.connect(self.cut_text)
            edit_menu.addAction(cut_action)
            
            # Kopyala
            copy_action = QAction("📋 Kopyala", self)
            copy_action.setShortcut("Ctrl+C")
            copy_action.triggered.connect(self.copy_text)
            edit_menu.addAction(copy_action)
            
            # Yapıştır
            paste_action = QAction("📄 Yapıştır", self)
            paste_action.setShortcut("Ctrl+V")
            paste_action.triggered.connect(self.paste_text)
            edit_menu.addAction(paste_action)
            
            edit_menu.addSeparator()
            
            # Bul
            find_action = QAction("🔍 Bul", self)
            find_action.setShortcut("Ctrl+F")
            find_action.triggered.connect(self.find_text)
            edit_menu.addAction(find_action)
            
            # Değiştir
            replace_action = QAction("🔄 Değiştir", self)
            replace_action.setShortcut("Ctrl+H")
            replace_action.triggered.connect(self.replace_text)
            edit_menu.addAction(replace_action)
            
            # Görünüm menüsü
            view_menu = menubar.addMenu("👁️ Görünüm")
            
            # Tema alt menüsü
            theme_menu = view_menu.addMenu("🎨 Tema")
            
            # Tema seçenekleri
            theme_group = QActionGroup(self)
            
            dark_theme_action = QAction("🌙 Dark", self)
            dark_theme_action.setCheckable(True)
            dark_theme_action.setChecked(self.theme_mode == ThemeMode.DARK)
            dark_theme_action.triggered.connect(lambda: self.set_theme(ThemeMode.DARK))
            theme_group.addAction(dark_theme_action)
            theme_menu.addAction(dark_theme_action)
            
            light_theme_action = QAction("☀️ Light", self)
            light_theme_action.setCheckable(True)
            light_theme_action.setChecked(self.theme_mode == ThemeMode.LIGHT)
            light_theme_action.triggered.connect(lambda: self.set_theme(ThemeMode.LIGHT))
            theme_group.addAction(light_theme_action)
            theme_menu.addAction(light_theme_action)
            
            monokai_theme_action = QAction("🔥 Monokai", self)
            monokai_theme_action.setCheckable(True)
            monokai_theme_action.setChecked(self.theme_mode == ThemeMode.MONOKAI)
            monokai_theme_action.triggered.connect(lambda: self.set_theme(ThemeMode.MONOKAI))
            theme_group.addAction(monokai_theme_action)
            theme_menu.addAction(monokai_theme_action)
            
            dracula_theme_action = QAction("🧛 Dracula", self)
            dracula_theme_action.setCheckable(True)
            dracula_theme_action.setChecked(self.theme_mode == ThemeMode.DRACULA)
            dracula_theme_action.triggered.connect(lambda: self.set_theme(ThemeMode.DRACULA))
            theme_group.addAction(dracula_theme_action)
            theme_menu.addAction(dracula_theme_action)
            
            # Çalıştır menüsü
            run_menu = menubar.addMenu("▶️ Çalıştır")
            
            # Çalıştır
            run_action = QAction("▶️ Çalıştır", self)
            run_action.setShortcut("F5")
            run_action.triggered.connect(self.run_current_file)
            run_menu.addAction(run_action)
            
            # Debug
            debug_action = QAction("🐛 Debug", self)
            debug_action.setShortcut("F9")
            debug_action.triggered.connect(self.debug_current_file)
            run_menu.addAction(debug_action)
            
            # Araçlar menüsü
            tools_menu = menubar.addMenu("🔧 Araçlar")
            
            # Snippet yöneticisi
            snippets_action = QAction("📝 Kod Parçacıkları", self)
            snippets_action.setShortcut("Ctrl+Shift+P")
            snippets_action.triggered.connect(self.show_snippets)
            tools_menu.addAction(snippets_action)
            
            # Plugin yöneticisi
            plugins_action = QAction("🧩 Plugin Yöneticisi", self)
            plugins_action.triggered.connect(self.show_plugins)
            tools_menu.addAction(plugins_action)
            
            tools_menu.addSeparator()
            
            # .app derleme
            compile_action = QAction("📦 .app Olarak Derle", self)
            compile_action.setShortcut("Ctrl+Shift+B")
            compile_action.triggered.connect(self.compile_to_app)
            tools_menu.addAction(compile_action)
            
            tools_menu.addSeparator()
            
            # Ayarlar
            settings_action = QAction("⚙️ Ayarlar", self)
            settings_action.triggered.connect(self.show_settings)
            tools_menu.addAction(settings_action)
            
            # Yardım menüsü
            help_menu = menubar.addMenu("❓ Yardım")
            
            # Hakkında
            about_action = QAction("ℹ️ Hakkında", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
        
        def setup_toolbar(self):
            """Modern araç çubuğu"""
            toolbar = self.addToolBar("Ana")
            toolbar.setMovable(False)
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            
            # Yeni proje
            new_project_btn = QPushButton("🆕 Yeni Proje")
            new_project_btn.clicked.connect(self.new_project)
            toolbar.addWidget(new_project_btn)
            
            # Proje aç
            open_project_btn = QPushButton("📂 Proje Aç")
            open_project_btn.clicked.connect(self.open_project)
            toolbar.addWidget(open_project_btn)
            
            toolbar.addSeparator()
            
            # Kaydet
            save_btn = QPushButton("💾 Kaydet")
            save_btn.clicked.connect(self.save_current_file)
            toolbar.addWidget(save_btn)
            
            toolbar.addSeparator()
            
            # Çalıştır
            run_btn = QPushButton("▶️ Çalıştır")
            run_btn.clicked.connect(self.run_current_file)
            toolbar.addWidget(run_btn)
            
            # Debug
            debug_btn = QPushButton("🐛 Debug")
            debug_btn.clicked.connect(self.debug_current_file)
            toolbar.addWidget(debug_btn)
            
            toolbar.addSeparator()
            
            # Snippets
            snippets_btn = QPushButton("📝 Snippets")
            snippets_btn.clicked.connect(self.show_snippets)
            toolbar.addWidget(snippets_btn)
            
            # Plugins
            plugins_btn = QPushButton("🧩 Plugins")
            plugins_btn.clicked.connect(self.show_plugins)
            toolbar.addWidget(plugins_btn)
            
            # .app Derle
            compile_btn = QPushButton("📦 Derle")
            compile_btn.clicked.connect(self.compile_to_app)
            toolbar.addWidget(compile_btn)
            
            toolbar.addSeparator()
            
            # Tema değiştirici
            theme_combo = QComboBox()
            theme_combo.addItems(["🌙 Dark", "☀️ Light", "🔥 Monokai", "🧛 Dracula"])
            theme_combo.setCurrentIndex(list(ThemeMode).index(self.theme_mode))
            theme_combo.currentIndexChanged.connect(self.on_theme_combo_changed)
            toolbar.addWidget(theme_combo)
        
        def setup_statusbar(self):
            """Modern durum çubuğu"""
            self.status_bar = self.statusBar()
            
            # Sol taraf - durum mesajı
            self.status_label = QLabel("Hazır")
            self.status_bar.addWidget(self.status_label)
            
            # Sağ taraf - dosya bilgisi
            self.file_info_label = QLabel("")
            self.status_bar.addPermanentWidget(self.file_info_label)
            
            # Satır/sütun bilgisi
            self.cursor_info_label = QLabel("Satır: 1, Sütun: 1")
            self.status_bar.addPermanentWidget(self.cursor_info_label)
        
        def setup_connections(self):
            """Sinyal bağlantıları"""
            # Proje gezgini
            self.project_explorer.file_opened.connect(self.open_file_in_editor)
            
            # Editor sekmeler
            self.editor_tabs.currentChanged.connect(self.on_tab_changed)
        
        def apply_theme(self):
            """Tema uygula"""
            # Ana pencere teması
            if self.theme_mode == ThemeMode.DARK:
                self.apply_dark_theme()
            elif self.theme_mode == ThemeMode.LIGHT:
                self.apply_light_theme()
            elif self.theme_mode == ThemeMode.MONOKAI:
                self.apply_monokai_theme()
            elif self.theme_mode == ThemeMode.DRACULA:
                self.apply_dracula_theme()
            
            # Widget'ların temasını güncelle
            self.project_explorer.set_theme(self.theme_mode)
            self.output_panel.set_theme(self.theme_mode)
            
            # Açık editörlerin temasını güncelle
            for editor in self.open_files.values():
                editor.set_theme(self.theme_mode)
        
        def apply_dark_theme(self):
            """Dark tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                }
                QMenuBar {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border-bottom: 1px solid #3e3e42;
                    padding: 4px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #3e3e42;
                }
                QMenu {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border: 1px solid #3e3e42;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #3e3e42;
                }
                QToolBar {
                    background-color: #2d2d30;
                    border: none;
                    spacing: 8px;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #0e639c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QPushButton:pressed {
                    background-color: #0d5a8a;
                }
                QTabWidget::pane {
                    border: 1px solid #3e3e42;
                    background-color: #1e1e1e;
                    border-radius: 8px;
                }
                QTabBar::tab {
                    background-color: #2d2d30;
                    color: #cccccc;
                    padding: 10px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    border-bottom: 2px solid #007acc;
                }
                QTabBar::tab:hover {
                    background-color: #3e3e42;
                }
                QStatusBar {
                    background-color: #007acc;
                    color: white;
                    padding: 4px;
                }
                QComboBox {
                    background-color: #3e3e42;
                    color: #cccccc;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QComboBox:hover {
                    border: 1px solid #007acc;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
            """)
        
        def apply_light_theme(self):
            """Light tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #000000;
                    border-bottom: 1px solid #d0d0d0;
                    padding: 4px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #e3f2fd;
                }
                QToolBar {
                    background-color: #f0f0f0;
                    border: none;
                    spacing: 8px;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976d2;
                }
                QPushButton:pressed {
                    background-color: #1565c0;
                }
                QTabWidget::pane {
                    border: 1px solid #d0d0d0;
                    background-color: #ffffff;
                    border-radius: 8px;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    color: #000000;
                    padding: 10px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 2px solid #2196f3;
                }
                QTabBar::tab:hover {
                    background-color: #e0e0e0;
                }
                QStatusBar {
                    background-color: #2196f3;
                    color: white;
                    padding: 4px;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QComboBox:hover {
                    border: 1px solid #2196f3;
                }
            """)
        
        def apply_monokai_theme(self):
            """Monokai tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #272822;
                    color: #f8f8f2;
                }
                QMenuBar {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    border-bottom: 1px solid #49483e;
                    padding: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #49483e;
                }
                QMenu {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    border: 1px solid #49483e;
                    border-radius: 6px;
                }
                QMenu::item:selected {
                    background-color: #49483e;
                }
                QToolBar {
                    background-color: #3e3d32;
                    border: none;
                    spacing: 8px;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #a6e22e;
                    color: #272822;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #90c91e;
                }
                QTabWidget::pane {
                    border: 1px solid #49483e;
                    background-color: #272822;
                    border-radius: 8px;
                }
                QTabBar::tab {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    padding: 10px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #272822;
                    border-bottom: 2px solid #a6e22e;
                }
                QStatusBar {
                    background-color: #a6e22e;
                    color: #272822;
                    padding: 4px;
                }
            """)
        
        def apply_dracula_theme(self):
            """Dracula tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #282a36;
                    color: #f8f8f2;
                }
                QMenuBar {
                    background-color: #44475a;
                    color: #f8f8f2;
                    border-bottom: 1px solid #6272a4;
                    padding: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #6272a4;
                }
                QMenu {
                    background-color: #44475a;
                    color: #f8f8f2;
                    border: 1px solid #6272a4;
                    border-radius: 6px;
                }
                QMenu::item:selected {
                    background-color: #6272a4;
                }
                QToolBar {
                    background-color: #44475a;
                    border: none;
                    spacing: 8px;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #bd93f9;
                    color: #282a36;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #a080e6;
                }
                QTabWidget::pane {
                    border: 1px solid #6272a4;
                    background-color: #282a36;
                    border-radius: 8px;
                }
                QTabBar::tab {
                    background-color: #44475a;
                    color: #f8f8f2;
                    padding: 10px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #282a36;
                    border-bottom: 2px solid #bd93f9;
                }
                QStatusBar {
                    background-color: #bd93f9;
                    color: #282a36;
                    padding: 4px;
                }
            """)
        
        def set_theme(self, theme_mode: ThemeMode):
            """Tema değiştir"""
            self.theme_mode = theme_mode
            self.apply_theme()
            
            # Kernel'a tema değişikliğini bildir
            if self.kernel:
                config = self.kernel.get_module("config")
                if config:
                    config.set("theme.pyide_theme", theme_mode.value)
            
            self.logger.info(f"Theme changed to: {theme_mode.value}")
        
        def on_theme_combo_changed(self, index: int):
            """Tema combo değişti"""
            themes = [ThemeMode.DARK, ThemeMode.LIGHT, ThemeMode.MONOKAI, ThemeMode.DRACULA]
            self.set_theme(themes[index])
        
        def load_templates(self):
            """Proje şablonlarını yükle"""
            self.templates = [
                ProjectTemplate(
                    name="Basit Python Uygulaması",
                    description="Tek dosyalı basit Python uygulaması",
                    template_dir="basic",
                    main_file="main.py",
                    files=["main.py", "README.md"],
                    category="Basic"
                ),
                ProjectTemplate(
                    name="Flask Web Uygulaması",
                    description="Flask ile web uygulaması şablonu",
                    template_dir="flask",
                    main_file="app.py",
                    files=["app.py", "requirements.txt", "templates/index.html", "static/style.css"],
                    dependencies=["flask"],
                    category="Web"
                ),
                ProjectTemplate(
                    name="PyQt6 Desktop Uygulaması",
                    description="PyQt6 ile masaüstü uygulaması",
                    template_dir="pyqt",
                    main_file="main.py",
                    files=["main.py", "requirements.txt", "ui/main_window.py"],
                    dependencies=["PyQt6"],
                    category="Desktop"
                ),
                ProjectTemplate(
                    name="CLI Uygulaması",
                    description="Komut satırı uygulaması şablonu",
                    template_dir="cli",
                    main_file="cli.py",
                    files=["cli.py", "requirements.txt", "README.md"],
                    dependencies=["click"],
                    category="CLI"
                )
            ]
        
        def new_project(self):
            """Yeni proje oluştur"""
            if CORE_MODULES_AVAILABLE and hasattr(self, 'template_manager'):
                # Yeni template manager kullan
                try:
                    # Template seçim dialog'u
                    templates = self.template_manager.get_available_templates()
                    if not templates:
                        QMessageBox.warning(self, "Uyarı", "Hiç template bulunamadı.")
                        return
                    
                    # Template seçimi
                    template_names = [f"{t.icon} {t.name}" for t in templates]
                    template_name, ok = QInputDialog.getItem(
                        self, "Template Seç", "Proje template'i seçin:", 
                        template_names, 0, False
                    )
                    
                    if not ok:
                        return
                    
                    # Seçilen template'i bul
                    selected_template = None
                    for template in templates:
                        if f"{template.icon} {template.name}" == template_name:
                            selected_template = template
                            break
                    
                    if not selected_template:
                        return
                    
                    # Proje adı
                    project_name, ok = QInputDialog.getText(
                        self, "Proje Adı", "Proje adını girin:"
                    )
                    
                    if not ok or not project_name:
                        return
                    
                    # Proje dizini seç
                    project_dir = QFileDialog.getExistingDirectory(
                        self, "Proje Dizini Seçin"
                    )
                    
                    if not project_dir:
                        return
                    
                    # Template değişkenleri
                    variables = {}
                    if selected_template.variables:
                        for var_name, default_value in selected_template.variables.items():
                            if var_name == "project_name":
                                variables[var_name] = project_name
                            elif var_name == "author_name":
                                variables[var_name] = "PyCloud Developer"
                            elif var_name == "description":
                                variables[var_name] = f"A {selected_template.name.lower()} project"
                            else:
                                value, ok = QInputDialog.getText(
                                    self, f"Template Değişkeni", 
                                    f"{var_name} değerini girin:", 
                                    text=default_value
                                )
                                if ok:
                                    variables[var_name] = value
                                else:
                                    variables[var_name] = default_value
                    
                    # Proje oluştur
                    project_path = Path(project_dir) / project_name
                    success = self.template_manager.create_project_from_template(
                        selected_template.id, str(project_path), variables
                    )
                    
                    if success:
                        # Projeyi aç
                        self.current_project_path = str(project_path)
                        self.project_explorer.load_project(str(project_path))
                        self.status_label.setText(f"Proje oluşturuldu: {project_name}")
                        
                        # Ana dosyayı aç
                        if selected_template.files:
                            main_file = selected_template.files[0]
                            main_file_path = project_path / main_file
                            if main_file_path.exists():
                                self.open_file_in_editor(str(main_file_path))
                        
                        self.logger.info(f"✅ Yeni proje oluşturuldu: {project_name}")
                    else:
                        QMessageBox.critical(self, "Hata", "Proje oluşturulamadı.")
                        
                except Exception as e:
                    self.logger.error(f"❌ Proje oluşturma hatası: {e}")
                    QMessageBox.critical(self, "Hata", f"Proje oluşturulamadı: {str(e)}")
            else:
                # Fallback: eski sistem
                dialog = QInputDialog()
                dialog.setWindowTitle("Yeni Proje")
                dialog.setLabelText("Proje adını girin:")
                
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    project_name = dialog.textValue()
                    if project_name:
                        # Proje dizini seç
                        project_dir = QFileDialog.getExistingDirectory(
                            self, "Proje Dizini Seçin"
                        )
                        
                        if project_dir:
                            self.create_project_from_template(project_dir, project_name, self.templates[0])
        
        def create_project_from_template(self, base_dir: str, project_name: str, template: ProjectTemplate):
            """Şablondan proje oluştur"""
            try:
                project_path = Path(base_dir) / project_name
                project_path.mkdir(exist_ok=True)
                
                # Şablon dosyalarını oluştur
                if template.name == "Basit Python Uygulaması":
                    (project_path / "main.py").write_text('''#!/usr/bin/env python3
"""
Basit Python Uygulaması
"""

def main():
    print("Merhaba PyCloud OS!")
    print("Bu basit bir Python uygulamasıdır.")

if __name__ == "__main__":
    main()
''')
                    
                    (project_path / "README.md").write_text(f'''# {project_name}

Bu proje PyCloud OS Python IDE ile oluşturulmuştur.

## Çalıştırma

```bash
python main.py
```
''')
                
                # Projeyi aç
                self.current_project_path = str(project_path)
                self.project_explorer.load_project(str(project_path))
                self.status_label.setText(f"Proje oluşturuldu: {project_name}")
                
                # Ana dosyayı aç
                main_file_path = project_path / template.main_file
                if main_file_path.exists():
                    self.open_file_in_editor(str(main_file_path))
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Proje oluşturulamadı: {str(e)}")
        
        def open_project(self):
            """Proje aç - FilePicker entegreli"""
            try:
                # FilePicker ile klasör seçmeyi dene
                project_path = self._try_filepicker_select_directory()
                
                if not project_path:
                    # Fallback - QFileDialog
                    self.logger.info("🔄 FilePicker mevcut değil, QFileDialog kullanılıyor")
                    project_path = QFileDialog.getExistingDirectory(
                        self, "Proje Klasörü Seç"
                    )
                
                if project_path:
                    self.current_project_path = project_path
                    self.project_explorer.load_project(project_path)
                    self.status_label.setText(f"Proje açıldı: {Path(project_path).name}")
                    self.logger.info(f"📁 Proje açıldı: {project_path}")
                    
            except Exception as e:
                self.logger.error(f"❌ Proje açma hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Proje açılamadı: {str(e)}")
        
        def _try_filepicker_select_directory(self) -> Optional[str]:
            """FilePicker ile klasör seçmeyi dene"""
            try:
                from cloud.filepicker import select_directory_dialog
                
                # FilePicker ile klasör seç
                directory_path = select_directory_dialog(
                    app_id="cloud_pyide",
                    parent=self,
                    kernel=self.kernel
                )
                
                if directory_path:
                    self.logger.info(f"✅ FilePicker ile klasör seçildi: {directory_path}")
                    return directory_path
                
                return None
                
            except ImportError:
                self.logger.warning("⚠️ FilePicker modülü bulunamadı")
                return None
            except Exception as e:
                self.logger.error(f"❌ FilePicker klasör seçme hatası: {e}")
                return None
        
        def new_file(self):
            """Yeni dosya"""
            if not self.current_project_path:
                QMessageBox.warning(self, "Uyarı", "Önce bir proje açmalısınız.")
                return
            
            file_name, ok = QInputDialog.getText(
                self, "Yeni Dosya", "Dosya adını girin (örn: script.py):"
            )
            
            if ok and file_name:
                file_path = Path(self.current_project_path) / file_name
                file_path.write_text("")
                self.project_explorer.load_project(self.current_project_path)
                self.open_file_in_editor(str(file_path))
        
        def open_file(self):
            """Dosya aç - FilePicker ve VFS entegreli"""
            try:
                # FilePicker kullanmayı dene
                if self._try_filepicker_open():
                    return
                
                # Fallback - QFileDialog
                self.logger.info("🔄 FilePicker mevcut değil, QFileDialog kullanılıyor")
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Dosya Aç", "", 
                    "Python Files (*.py);;Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
                )
                
                if file_path:
                    self.open_file_in_editor(file_path)
                    
            except Exception as e:
                self.logger.error(f"❌ Dosya açma hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {str(e)}")
        
        def _try_filepicker_open(self) -> bool:
            """FilePicker ile dosya açmayı dene"""
            try:
                from cloud.filepicker import open_file_dialog, FilePickerFilter
                
                # FilePicker ile dosya seç
                file_path = open_file_dialog(
                    app_id="cloud_pyide",
                    filters=[
                        FilePickerFilter.PYTHON_FILES,
                        FilePickerFilter.TEXT_FILES,
                        FilePickerFilter.ALL_FILES
                    ],
                    parent=self,
                    kernel=self.kernel
                )
                
                if file_path:
                    self.open_file_in_editor(file_path)
                    self.logger.info(f"✅ FilePicker ile dosya açıldı: {file_path}")
                    return True
                
                return False
                
            except ImportError:
                self.logger.warning("⚠️ FilePicker modülü bulunamadı")
                return False
            except Exception as e:
                self.logger.error(f"❌ FilePicker hatası: {e}")
                return False
        
        def open_file_in_editor(self, file_path: str):
            """Dosyayı editörde aç - VFS entegreli"""
            try:
                # Zaten açık mı?
                if file_path in self.open_files:
                    # Sekmeyi aktif et
                    for i in range(self.editor_tabs.count()):
                        if self.editor_tabs.widget(i) == self.open_files[file_path]:
                            self.editor_tabs.setCurrentIndex(i)
                            return
                
                # Dosyayı VFS ile oku
                content = self._read_file_content(file_path)
                if content is None:
                    QMessageBox.critical(self, "Hata", f"Dosya okunamadı: {file_path}")
                    return
                
                # Yeni editör oluştur
                editor = ModernCodeEditor(theme_mode=self.theme_mode)
                editor.setPlainText(content)
                
                # Dosya ismini sekme olarak ekle
                file_name = Path(file_path).name
                tab_index = self.editor_tabs.addTab(editor, file_name)
                self.editor_tabs.setCurrentIndex(tab_index)
                
                # Kayıt tut
                self.open_files[file_path] = editor
                
                self.status_label.setText(f"Dosya açıldı: {file_name}")
                self.logger.info(f"📂 Dosya editörde açıldı: {file_path}")
                
            except Exception as e:
                self.logger.error(f"❌ Editörde dosya açma hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Dosya açılamadı: {str(e)}")
        
        def _read_file_content(self, file_path: str) -> Optional[str]:
            """Dosya içeriğini VFS ile oku"""
            try:
                # VFS ile okumayı dene
                if self.vfs and self.bridge_client:
                    # VFS path'e çevir
                    vfs_path = self._real_path_to_vfs_path(file_path)
                    
                    # VFS ile oku
                    read_success, content = self.bridge_client.call_module_method(
                        'fs', 'read_file', vfs_path
                    )
                    
                    if read_success and content is not None:
                        self.logger.info(f"✅ VFS ile dosya okundu: {vfs_path}")
                        return content
                    else:
                        self.logger.warning(f"⚠️ VFS okuma başarısız: {vfs_path}")
                
                # Fallback - direkt dosya sistemi
                self.logger.info(f"🔄 Fallback: direkt dosya okuma")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.logger.info(f"✅ Direkt dosya okundu: {file_path}")
                    return content
                
            except Exception as e:
                self.logger.error(f"❌ Dosya okuma hatası: {e}")
                return None
        
        def _real_path_to_vfs_path(self, real_path: str) -> str:
            """Gerçek dosya yolunu VFS yoluna çevir"""
            try:
                path_obj = Path(real_path)
                path_str = str(path_obj)
                
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
                    
                # Relative path'leri /home'a ekle
                return f"/home/{Path(real_path).name}"
                    
            except Exception as e:
                self.logger.error(f"Path conversion error: {e}")
                return f"/home/{Path(real_path).name}"
        
        def save_current_file(self):
            """Aktif dosyayı kaydet - VFS entegreli"""
            current_editor = self.editor_tabs.currentWidget()
            if not isinstance(current_editor, ModernCodeEditor):
                return
            
            # Dosya yolunu bul
            file_path = None
            for path, editor in self.open_files.items():
                if editor == current_editor:
                    file_path = path
                    break
            
            if file_path:
                content = current_editor.toPlainText()
                if self._save_file_content(file_path, content):
                    self.status_label.setText(f"Kaydedildi: {Path(file_path).name}")
                    self.logger.info(f"💾 Dosya kaydedildi: {file_path}")
                else:
                    QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {Path(file_path).name}")
        
        def save_as_file(self):
            """Farklı kaydet - FilePicker entegreli"""
            try:
                current_editor = self.editor_tabs.currentWidget()
                if not current_editor:
                    return
                
                # FilePicker ile kaydetmeyi dene
                save_path = self._try_filepicker_save()
                
                if not save_path:
                    # Fallback - QFileDialog
                    self.logger.info("🔄 FilePicker mevcut değil, QFileDialog kullanılıyor")
                    save_path, _ = QFileDialog.getSaveFileName(
                        self, "Farklı Kaydet", "",
                        "Python Files (*.py);;Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
                    )
                
                if save_path:
                    content = current_editor.toPlainText()
                    
                    if self._save_file_content(save_path, content):
                        # Sekme başlığını güncelle
                        current_index = self.editor_tabs.currentIndex()
                        file_name = Path(save_path).name
                        self.editor_tabs.setTabText(current_index, file_name)
                        
                        # Dosya kaydını güncelle
                        old_path = None
                        for path, editor in self.open_files.items():
                            if editor == current_editor:
                                old_path = path
                                break
                        
                        if old_path:
                            del self.open_files[old_path]
                        self.open_files[save_path] = current_editor
                        
                        self.status_label.setText(f"Dosya kaydedildi: {file_name}")
                        self.logger.info(f"💾 Dosya farklı kaydedildi: {save_path}")
                    
            except Exception as e:
                self.logger.error(f"❌ Farklı kaydetme hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {str(e)}")
        
        def _try_filepicker_save(self) -> Optional[str]:
            """FilePicker ile kaydetmeyi dene"""
            try:
                from cloud.filepicker import save_file_dialog, FilePickerFilter
                
                # FilePicker ile kaydet
                file_path = save_file_dialog(
                    app_id="cloud_pyide",
                    filters=[
                        FilePickerFilter.PYTHON_FILES,
                        FilePickerFilter.TEXT_FILES,
                        FilePickerFilter.ALL_FILES
                    ],
                    parent=self,
                    kernel=self.kernel
                )
                
                if file_path:
                    self.logger.info(f"✅ FilePicker ile kaydetme yolu seçildi: {file_path}")
                    return file_path
                
                return None
                
            except ImportError:
                self.logger.warning("⚠️ FilePicker modülü bulunamadı")
                return None
            except Exception as e:
                self.logger.error(f"❌ FilePicker kaydetme hatası: {e}")
                return None
        
        def _save_file_content(self, file_path: str, content: str) -> bool:
            """Dosya içeriğini VFS ile kaydet"""
            try:
                # VFS ile kaydetmeyi dene
                if self.vfs and self.bridge_client:
                    # VFS path'e çevir
                    vfs_path = self._real_path_to_vfs_path(file_path)
                    
                    # VFS ile kaydet
                    save_success, result = self.bridge_client.call_module_method(
                        'fs', 'write_file', vfs_path, content, 'cloud_pyide'
                    )
                    
                    if save_success:
                        self.logger.info(f"✅ VFS ile dosya kaydedildi: {vfs_path}")
                        return True
                    else:
                        self.logger.warning(f"⚠️ VFS kaydetme başarısız: {vfs_path} - {result}")
                
                # Fallback - direkt dosya sistemi
                self.logger.info(f"🔄 Fallback: direkt dosya kaydetme")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    self.logger.info(f"✅ Direkt dosya kaydedildi: {file_path}")
                    return True
                
            except Exception as e:
                self.logger.error(f"❌ Dosya kaydetme hatası: {e}")
                return False
        
        def close_file(self, index: int):
            """Dosyayı kapat"""
            widget = self.editor_tabs.widget(index)
            if isinstance(widget, ModernCodeEditor):
                # Dosya yolunu bul ve kayıttan çıkar
                file_path = None
                for path, editor in self.open_files.items():
                    if editor == widget:
                        file_path = path
                        break
                
                if file_path:
                    del self.open_files[file_path]
                    self.status_label.setText(f"Dosya kapatıldı: {Path(file_path).name}")
            
            self.editor_tabs.removeTab(index)
        
        def run_current_file(self):
            """Mevcut dosyayı çalıştır - Core modül entegreli"""
            try:
                current_editor = self.editor_tabs.currentWidget()
                if not current_editor:
                    QMessageBox.warning(self, "Uyarı", "Çalıştırılacak dosya yok.")
                    return
                
                # Dosya yolunu bul
                current_file_path = None
                for file_path, editor in self.open_files.items():
                    if editor == current_editor:
                        current_file_path = file_path
                        break
                
                if not current_file_path:
                    QMessageBox.warning(self, "Uyarı", "Dosya kaydedilmemiş.")
                    return
                
                # Önce kaydet
                self.save_current_file()
                
                # Çıktı panelini temizle
                self.output_panel.clear()
                self.output_panel.append_output(f"🚀 Çalıştırılıyor: {Path(current_file_path).name}")
                
                # Core modül ile çalıştır
                if CORE_MODULES_AVAILABLE and hasattr(self, 'code_runner'):
                    working_dir = str(Path(current_file_path).parent)
                    success = self.code_runner.run_file(current_file_path, working_dir)
                    
                    if success:
                        self.logger.info(f"🚀 Core runner ile çalıştırıldı: {current_file_path}")
                        # UI durumunu güncelle
                        if hasattr(self, 'run_action'):
                            self.run_action.setEnabled(False)
                    else:
                        self.output_panel.append_error("❌ Çalıştırma başlatılamadı")
                else:
                    # Fallback: eski worker sistemi
                    self.logger.info("🔄 Fallback worker kullanılıyor")
                    working_dir = str(Path(current_file_path).parent)
                    
                    self.run_worker = RunWorker(current_file_path, working_dir)
                    self.run_worker.output_ready.connect(self.output_panel.append_output)
                    self.run_worker.finished.connect(self.on_run_finished)
                    self.run_worker.start()
                
            except Exception as e:
                self.logger.error(f"❌ Çalıştırma hatası: {e}")
                self.output_panel.append_error(f"❌ Hata: {str(e)}")
        
        def debug_current_file(self):
            """Debug modu"""
            QMessageBox.information(self, "Debug", "Debug özelliği yakında eklenecek!")
        
        def on_run_finished(self):
            """Çalıştırma tamamlandı"""
            self.status_label.setText("Hazır")
            self.run_worker = None
        
        def on_tab_changed(self, index: int):
            """Sekme değişti"""
            if index >= 0:
                widget = self.editor_tabs.widget(index)
                if isinstance(widget, ModernCodeEditor):
                    # Dosya bilgisini güncelle
                    file_path = None
                    for path, editor in self.open_files.items():
                        if editor == widget:
                            file_path = path
                            break
                    
                    if file_path:
                        self.file_info_label.setText(f"📄 {Path(file_path).name}")
        
        def auto_save(self):
            """Otomatik kaydetme - VFS entegreli"""
            try:
                current_editor = self.editor_tabs.currentWidget()
                if isinstance(current_editor, ModernCodeEditor):
                    # Aktif editörün dosya yolunu bul
                    for file_path, editor in self.open_files.items():
                        if editor == current_editor:
                            content = editor.toPlainText()
                            
                            # VFS ile otomatik kaydet
                            if self._save_file_content(file_path, content):
                                self.logger.debug(f"🔄 Otomatik kaydetme başarılı: {Path(file_path).name}")
                            else:
                                self.logger.warning(f"⚠️ Otomatik kaydetme başarısız: {Path(file_path).name}")
                            break
                            
            except Exception as e:
                self.logger.error(f"❌ Otomatik kaydetme hatası: {e}")
                # Otomatik kaydetme hatası sessizce geçilir
        
        # Düzenleme işlemleri
        def cut_text(self):
            """Metni kes"""
            current_editor = self.editor_tabs.currentWidget()
            if isinstance(current_editor, ModernCodeEditor):
                current_editor.cut()
        
        def copy_text(self):
            """Metni kopyala"""
            current_editor = self.editor_tabs.currentWidget()
            if isinstance(current_editor, ModernCodeEditor):
                current_editor.copy()
        
        def paste_text(self):
            """Metni yapıştır"""
            current_editor = self.editor_tabs.currentWidget()
            if isinstance(current_editor, ModernCodeEditor):
                current_editor.paste()
        
        def undo_text(self):
            """Geri al"""
            current_editor = self.editor_tabs.currentWidget()
            if isinstance(current_editor, ModernCodeEditor):
                current_editor.undo()
        
        def redo_text(self):
            """İleri al"""
            current_editor = self.editor_tabs.currentWidget()
            if isinstance(current_editor, ModernCodeEditor):
                current_editor.redo()
        
        def find_text(self):
            """Metin bul"""
            current_editor = self.editor_tabs.currentWidget()
            if not isinstance(current_editor, ModernCodeEditor):
                return
            
            text, ok = QInputDialog.getText(self, "Bul", "Aranacak metin:")
            if ok and text:
                found = current_editor.find(text)
                if not found:
                    QMessageBox.information(self, "Bulunamadı", f"'{text}' metni bulunamadı.")
        
        def replace_text(self):
            """Metni değiştir"""
            current_editor = self.editor_tabs.currentWidget()
            if not isinstance(current_editor, ModernCodeEditor):
                return
            
            # Basit değiştirme dialogu
            find_text, ok1 = QInputDialog.getText(self, "Değiştir", "Bulunacak metin:")
            if not ok1 or not find_text:
                return
            
            replace_text, ok2 = QInputDialog.getText(self, "Değiştir", "Yeni metin:")
            if not ok2:
                return
            
            # Metni değiştir
            content = current_editor.toPlainText()
            new_content = content.replace(find_text, replace_text)
            current_editor.setPlainText(new_content)
            
            self.status_label.setText("Değiştirme tamamlandı")
        
        def show_snippets(self):
            """Snippet dialog'unu göster - Core modül entegreli"""
            try:
                if CORE_MODULES_AVAILABLE and hasattr(self, 'snippet_manager'):
                    # Core snippet manager kullan
                    dialog = CoreSnippetDialog(self.snippet_manager, self)
                else:
                    # Fallback: eski snippet dialog
                    dialog = SnippetDialog(self.snippet_manager, self)
                
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    # Seçilen snippet'i editöre ekle
                    current_editor = self.editor_tabs.currentWidget()
                    if current_editor and hasattr(dialog, 'selected_snippet'):
                        snippet = dialog.selected_snippet
                        if snippet:
                            if CORE_MODULES_AVAILABLE:
                                # Core snippet manager ile expand et
                                expanded_code = self.snippet_manager.expand_snippet(snippet)
                            else:
                                # Fallback
                                expanded_code = self.snippet_manager.expand_snippet(snippet)
                            
                            current_editor.insertPlainText(expanded_code)
                            
            except Exception as e:
                self.logger.error(f"❌ Snippet dialog hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Snippet dialog açılamadı: {str(e)}")
        
        def show_plugins(self):
            """Plugin dialog'unu göster - Core modül entegreli"""
            try:
                if CORE_MODULES_AVAILABLE and hasattr(self, 'plugin_manager'):
                    # Core plugin manager kullan
                    dialog = CorePluginDialog(self.plugin_manager, self)
                else:
                    # Fallback: eski plugin dialog
                    dialog = PluginDialog(self.plugin_manager, self)
                
                dialog.exec()
                
            except Exception as e:
                self.logger.error(f"❌ Plugin dialog hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Plugin dialog açılamadı: {str(e)}")
        
        def new_project(self):
            """Yeni proje oluştur - Core modül entegreli"""
            try:
                if CORE_MODULES_AVAILABLE and hasattr(self, 'template_manager'):
                    # Core template manager kullan
                    dialog = CoreNewProjectDialog(self.template_manager, self)
                else:
                    # Fallback: eski template sistemi
                    dialog = NewProjectDialog(self)
                
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    project_data = dialog.get_project_data()
                    if project_data:
                        self.create_project_from_template_core(project_data)
                        
            except Exception as e:
                self.logger.error(f"❌ Yeni proje dialog hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Yeni proje dialog açılamadı: {str(e)}")
        
        def create_project_from_template_core(self, project_data: Dict[str, Any]):
            """Core template manager ile proje oluştur"""
            try:
                template_id = project_data.get('template_id')
                project_name = project_data.get('project_name')
                project_path = project_data.get('project_path')
                variables = project_data.get('variables', {})
                
                if not all([template_id, project_name, project_path]):
                    QMessageBox.warning(self, "Uyarı", "Eksik proje bilgileri.")
                    return
                
                # Core template manager ile oluştur
                success = self.template_manager.create_project_from_template(
                    template_id, project_path, variables
                )
                
                if success:
                    # Projeyi aç
                    self.current_project_path = project_path
                    self.project_explorer.load_project(project_path)
                    self.status_label.setText(f"Proje oluşturuldu: {project_name}")
                    self.logger.info(f"✅ Core template ile proje oluşturuldu: {project_path}")
                    
                    # Ana dosyayı aç
                    template = self.template_manager.get_template(template_id)
                    if template and hasattr(template, 'files') and template.files:
                        main_file = Path(project_path) / template.files[0]
                        if main_file.exists():
                            self.open_file_in_editor(str(main_file))
                else:
                    QMessageBox.critical(self, "Hata", "Proje oluşturulamadı.")
                    
            except Exception as e:
                self.logger.error(f"❌ Core proje oluşturma hatası: {e}")
                QMessageBox.critical(self, "Hata", f"Proje oluşturulamadı: {str(e)}")
        
        def compile_to_app(self):
            """Projeyi .app olarak derle"""
            if not self.current_project_path:
                QMessageBox.warning(self, "Uyarı", "Önce bir proje açmalısınız!")
                return
            
            if not hasattr(self, 'app_compiler'):
                self.app_compiler = AppCompiler(self)
            
            dialog = CompileDialog(self.app_compiler, self.current_project_path, self)
            dialog.exec()
        
        def show_settings(self):
            """Ayarları göster"""
            QMessageBox.information(self, "Ayarlar", "Ayarlar paneli yakında!")
        
        def show_about(self):
            """Hakkında dialogu"""
            QMessageBox.about(self, "Cloud PyIDE Hakkında", 
                            """🐍 Cloud PyIDE - Modern Python IDE
                            
Sürüm: 2.0.0
PyCloud OS için geliştirilmiş modern Python geliştirme ortamı

Özellikler:
• Modern syntax highlighting (4 tema)
• Proje yönetimi ve şablonları
• Satır numaraları ve breakpoint desteği
• Gerçek zamanlı kod çalıştırma
• Otomatik kaydetme
• Çoklu sekme desteği

Geliştirici: PyCloud OS Team
Lisans: MIT""")
        
        def closeEvent(self, event):
            """Pencere kapatılıyor"""
            # Otomatik kaydetme durdur
            self.autosave_timer.stop()
            
            # Çalışan worker'ı durdur
            if self.run_worker and self.run_worker.isRunning():
                self.run_worker.terminate()
                self.run_worker.wait()
            
            event.accept()
        
        def on_code_output(self, text: str, output_type: str):
            """Code runner çıktısı geldi"""
            if output_type == "stderr":
                self.output_panel.append_error(text)
            else:
                self.output_panel.append_output(text)
        
        def on_code_finished(self, result):
            """Code runner tamamlandı"""
            if hasattr(result, 'success'):
                if result.success:
                    self.output_panel.append_success(f"✅ Çalıştırma tamamlandı ({result.execution_time:.2f}s)")
                else:
                    self.output_panel.append_error(f"❌ Çalıştırma başarısız (exit code: {result.exit_code})")
            
            # UI durumunu güncelle
            if hasattr(self, 'run_action'):
                self.run_action.setEnabled(True)

    class SnippetDialog(QDialog):
        """Kod parçacıkları dialogu"""
        
        def __init__(self, snippet_manager: SnippetManager, parent=None):
            super().__init__(parent)
            self.snippet_manager = snippet_manager
            self.setup_ui()
        
        def setup_ui(self):
            """Dialog UI kurulumu"""
            self.setWindowTitle("📝 Kod Parçacıkları")
            self.setGeometry(200, 200, 600, 400)
            
            layout = QVBoxLayout(self)
            
            # Üst panel - arama
            search_layout = QHBoxLayout()
            search_layout.addWidget(QLabel("🔍 Arama:"))
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Snippet adı veya trigger...")
            self.search_input.textChanged.connect(self.filter_snippets)
            search_layout.addWidget(self.search_input)
            layout.addLayout(search_layout)
            
            # Ana panel - snippet listesi
            self.snippet_list = QListWidget()
            self.snippet_list.itemDoubleClicked.connect(self.insert_snippet)
            layout.addWidget(self.snippet_list)
            
            # Alt panel - önizleme
            preview_label = QLabel("📋 Önizleme:")
            layout.addWidget(preview_label)
            
            self.preview_text = QTextEdit()
            self.preview_text.setReadOnly(True)
            self.preview_text.setMaximumHeight(150)
            self.preview_text.setFont(QFont("Consolas", 10))
            layout.addWidget(self.preview_text)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            insert_btn = QPushButton("✅ Ekle")
            insert_btn.clicked.connect(self.insert_snippet)
            button_layout.addWidget(insert_btn)
            
            new_btn = QPushButton("🆕 Yeni")
            new_btn.clicked.connect(self.new_snippet)
            button_layout.addWidget(new_btn)
            
            edit_btn = QPushButton("✏️ Düzenle")
            edit_btn.clicked.connect(self.edit_snippet)
            button_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️ Sil")
            delete_btn.clicked.connect(self.delete_snippet)
            button_layout.addWidget(delete_btn)
            
            button_layout.addStretch()
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(self.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            # Snippet listesini doldur
            self.load_snippets()
            
            # İlk öğeyi seç
            if self.snippet_list.count() > 0:
                self.snippet_list.setCurrentRow(0)
                self.show_preview()
            
            # Sinyal bağlantıları
            self.snippet_list.currentItemChanged.connect(self.show_preview)
        
        def load_snippets(self):
            """Snippet'ları yükle"""
            self.snippet_list.clear()
            for snippet in self.snippet_manager.snippets:
                item = QListWidgetItem(f"🔧 {snippet.name} ({snippet.trigger})")
                item.setData(Qt.ItemDataRole.UserRole, snippet)
                self.snippet_list.addItem(item)
        
        def filter_snippets(self):
            """Snippet'ları filtrele"""
            search_text = self.search_input.text().lower()
            for i in range(self.snippet_list.count()):
                item = self.snippet_list.item(i)
                snippet = item.data(Qt.ItemDataRole.UserRole)
                visible = (search_text in snippet.name.lower() or 
                          search_text in snippet.trigger.lower() or
                          search_text in snippet.description.lower())
                item.setHidden(not visible)
        
        def show_preview(self):
            """Önizleme göster"""
            current_item = self.snippet_list.currentItem()
            if current_item:
                snippet = current_item.data(Qt.ItemDataRole.UserRole)
                expanded_code = self.snippet_manager.expand_snippet(snippet)
                self.preview_text.setPlainText(f"# {snippet.description}\n\n{expanded_code}")
        
        def insert_snippet(self):
            """Snippet'i ekle"""
            current_item = self.snippet_list.currentItem()
            if current_item:
                snippet = current_item.data(Qt.ItemDataRole.UserRole)
                self.accept()
                # Parent'a snippet bilgisini gönder
                self.selected_snippet = snippet
        
        def new_snippet(self):
            """Yeni snippet oluştur"""
            dialog = SnippetEditDialog(None, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_snippet = dialog.get_snippet()
                self.snippet_manager.snippets.append(new_snippet)
                self.load_snippets()
        
        def edit_snippet(self):
            """Snippet düzenle"""
            current_item = self.snippet_list.currentItem()
            if current_item:
                snippet = current_item.data(Qt.ItemDataRole.UserRole)
                dialog = SnippetEditDialog(snippet, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    updated_snippet = dialog.get_snippet()
                    # Mevcut snippet'i güncelle
                    index = self.snippet_manager.snippets.index(snippet)
                    self.snippet_manager.snippets[index] = updated_snippet
                    self.load_snippets()
        
        def delete_snippet(self):
            """Snippet sil"""
            current_item = self.snippet_list.currentItem()
            if current_item:
                snippet = current_item.data(Qt.ItemDataRole.UserRole)
                reply = QMessageBox.question(self, "Sil", 
                                           f"'{snippet.name}' snippet'ini silmek istediğinizden emin misiniz?")
                if reply == QMessageBox.StandardButton.Yes:
                    self.snippet_manager.snippets.remove(snippet)
                    self.load_snippets()
    
    class SnippetEditDialog(QDialog):
        """Snippet düzenleme dialogu"""
        
        def __init__(self, snippet: Optional[CodeSnippet] = None, parent=None):
            super().__init__(parent)
            self.snippet = snippet
            self.setup_ui()
            if snippet:
                self.load_snippet()
        
        def setup_ui(self):
            """Dialog UI kurulumu"""
            self.setWindowTitle("✏️ Snippet Düzenle" if self.snippet else "🆕 Yeni Snippet")
            self.setGeometry(250, 250, 500, 400)
            
            layout = QVBoxLayout(self)
            
            # Form alanları
            form_layout = QFormLayout()
            
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("Snippet adı...")
            form_layout.addRow("📝 Ad:", self.name_input)
            
            self.trigger_input = QLineEdit()
            self.trigger_input.setPlaceholderText("Tetikleyici kelime...")
            form_layout.addRow("🔧 Trigger:", self.trigger_input)
            
            self.description_input = QLineEdit()
            self.description_input.setPlaceholderText("Açıklama...")
            form_layout.addRow("📋 Açıklama:", self.description_input)
            
            layout.addLayout(form_layout)
            
            # Kod alanı
            layout.addWidget(QLabel("💻 Kod:"))
            self.code_input = QTextEdit()
            self.code_input.setFont(QFont("Consolas", 11))
            self.code_input.setPlaceholderText("Python kodu...\n\nPlaceholder'lar:\n${1:name} - İlk parametre\n${2:value} - İkinci parametre")
            layout.addWidget(self.code_input)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            save_btn = QPushButton("💾 Kaydet")
            save_btn.clicked.connect(self.accept)
            button_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
        
        def load_snippet(self):
            """Snippet verilerini yükle"""
            if self.snippet:
                self.name_input.setText(self.snippet.name)
                self.trigger_input.setText(self.snippet.trigger)
                self.description_input.setText(self.snippet.description)
                self.code_input.setPlainText(self.snippet.code)
        
        def get_snippet(self) -> CodeSnippet:
            """Snippet nesnesini döndür"""
            return CodeSnippet(
                name=self.name_input.text(),
                trigger=self.trigger_input.text(),
                code=self.code_input.toPlainText(),
                description=self.description_input.text()
            )
    
    class PluginManager:
        """Plugin yöneticisi"""
        
        def __init__(self, ide_instance):
            self.ide = ide_instance
            self.plugins: List[Dict] = []
            self.plugin_dir = Path("plugins")
            self.plugin_dir.mkdir(exist_ok=True)
            self.load_plugins()
        
        def load_plugins(self):
            """Plugin'leri yükle"""
            try:
                for plugin_file in self.plugin_dir.glob("*.plug"):
                    with open(plugin_file, 'r', encoding='utf-8') as f:
                        plugin_data = json.load(f)
                        plugin_data['file_path'] = str(plugin_file)
                        self.plugins.append(plugin_data)
            except Exception as e:
                logging.getLogger("PluginManager").error(f"Plugin loading error: {e}")
        
        def install_plugin(self, plugin_path: str) -> bool:
            """Plugin kur"""
            try:
                # .plug dosyasını kopyala
                plugin_file = Path(plugin_path)
                if plugin_file.suffix != '.plug':
                    return False
                
                dest_path = self.plugin_dir / plugin_file.name
                shutil.copy2(plugin_path, dest_path)
                
                # Plugin'i yükle
                with open(dest_path, 'r', encoding='utf-8') as f:
                    plugin_data = json.load(f)
                    plugin_data['file_path'] = str(dest_path)
                    self.plugins.append(plugin_data)
                
                return True
            except Exception as e:
                logging.getLogger("PluginManager").error(f"Plugin install error: {e}")
                return False
        
        def uninstall_plugin(self, plugin_id: str) -> bool:
            """Plugin kaldır"""
            try:
                for plugin in self.plugins[:]:
                    if plugin.get('id') == plugin_id:
                        # Dosyayı sil
                        Path(plugin['file_path']).unlink()
                        # Listeden çıkar
                        self.plugins.remove(plugin)
                        return True
                return False
            except Exception as e:
                logging.getLogger("PluginManager").error(f"Plugin uninstall error: {e}")
                return False
        
        def get_available_plugins(self) -> List[Dict]:
            """Mevcut plugin'leri döndür"""
            return self.plugins.copy()
    
    class PluginDialog(QDialog):
        """Plugin yönetimi dialogu"""
        
        def __init__(self, plugin_manager: PluginManager, parent=None):
            super().__init__(parent)
            self.plugin_manager = plugin_manager
            self.setup_ui()
        
        def setup_ui(self):
            """Dialog UI kurulumu"""
            self.setWindowTitle("🧩 Plugin Yöneticisi")
            self.setGeometry(200, 200, 700, 500)
            
            layout = QVBoxLayout(self)
            
            # Üst panel
            top_layout = QHBoxLayout()
            top_layout.addWidget(QLabel("🧩 Kurulu Plugin'ler:"))
            top_layout.addStretch()
            
            install_btn = QPushButton("📥 Plugin Kur")
            install_btn.clicked.connect(self.install_plugin)
            top_layout.addWidget(install_btn)
            
            create_btn = QPushButton("🆕 Plugin Oluştur")
            create_btn.clicked.connect(self.create_plugin)
            top_layout.addWidget(create_btn)
            
            layout.addLayout(top_layout)
            
            # Plugin listesi
            self.plugin_list = QListWidget()
            layout.addWidget(self.plugin_list)
            
            # Plugin detayları
            details_label = QLabel("📋 Plugin Detayları:")
            layout.addWidget(details_label)
            
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setMaximumHeight(150)
            layout.addWidget(self.details_text)
            
            # Alt butonlar
            button_layout = QHBoxLayout()
            
            uninstall_btn = QPushButton("🗑️ Kaldır")
            uninstall_btn.clicked.connect(self.uninstall_plugin)
            button_layout.addWidget(uninstall_btn)
            
            button_layout.addStretch()
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(self.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            # Plugin'leri yükle
            self.load_plugins()
            
            # Sinyal bağlantıları
            self.plugin_list.currentItemChanged.connect(self.show_plugin_details)
        
        def load_plugins(self):
            """Plugin'leri listele"""
            self.plugin_list.clear()
            for plugin in self.plugin_manager.get_available_plugins():
                item = QListWidgetItem(f"🧩 {plugin.get('name', 'Unknown')} v{plugin.get('version', '1.0')}")
                item.setData(Qt.ItemDataRole.UserRole, plugin)
                self.plugin_list.addItem(item)
        
        def show_plugin_details(self):
            """Plugin detaylarını göster"""
            current_item = self.plugin_list.currentItem()
            if current_item:
                plugin = current_item.data(Qt.ItemDataRole.UserRole)
                details = f"""
📝 Ad: {plugin.get('name', 'Unknown')}
🔢 Sürüm: {plugin.get('version', '1.0')}
👤 Geliştirici: {plugin.get('developer', 'Unknown')}
📋 Açıklama: {plugin.get('description', 'Açıklama yok')}
🏷️ Kategori: {plugin.get('category', 'General')}
📁 Dosya: {Path(plugin.get('file_path', '')).name}
                """.strip()
                self.details_text.setPlainText(details)
        
        def install_plugin(self):
            """Plugin kur"""
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Plugin Dosyası Seç", "", "Plugin Files (*.plug);;All Files (*)"
            )
            
            if file_path:
                if self.plugin_manager.install_plugin(file_path):
                    QMessageBox.information(self, "Başarılı", "Plugin başarıyla kuruldu!")
                    self.load_plugins()
                else:
                    QMessageBox.critical(self, "Hata", "Plugin kurulamadı!")
        
        def uninstall_plugin(self):
            """Plugin kaldır"""
            current_item = self.plugin_list.currentItem()
            if current_item:
                plugin = current_item.data(Qt.ItemDataRole.UserRole)
                plugin_name = plugin.get('name', 'Unknown')
                
                reply = QMessageBox.question(self, "Plugin Kaldır", 
                                           f"'{plugin_name}' plugin'ini kaldırmak istediğinizden emin misiniz?")
                
                if reply == QMessageBox.StandardButton.Yes:
                    if self.plugin_manager.uninstall_plugin(plugin.get('id', '')):
                        QMessageBox.information(self, "Başarılı", "Plugin kaldırıldı!")
                        self.load_plugins()
                    else:
                        QMessageBox.critical(self, "Hata", "Plugin kaldırılamadı!")
        
        def create_plugin(self):
            """Yeni plugin oluştur"""
            dialog = PluginCreateDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                plugin_data = dialog.get_plugin_data()
                
                # Plugin dosyasını oluştur
                plugin_file = self.plugin_manager.plugin_dir / f"{plugin_data['id']}.plug"
                try:
                    with open(plugin_file, 'w', encoding='utf-8') as f:
                        json.dump(plugin_data, f, indent=2, ensure_ascii=False)
                    
                    QMessageBox.information(self, "Başarılı", f"Plugin oluşturuldu: {plugin_file}")
                    self.plugin_manager.load_plugins()
                    self.load_plugins()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Plugin oluşturulamadı: {e}")
    
    class PluginCreateDialog(QDialog):
        """Plugin oluşturma dialogu"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setup_ui()
        
        def setup_ui(self):
            """Dialog UI kurulumu"""
            self.setWindowTitle("🆕 Yeni Plugin Oluştur")
            self.setGeometry(300, 300, 500, 400)
            
            layout = QVBoxLayout(self)
            
            # Form alanları
            form_layout = QFormLayout()
            
            self.id_input = QLineEdit()
            self.id_input.setPlaceholderText("plugin_id")
            form_layout.addRow("🆔 ID:", self.id_input)
            
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("Plugin Adı")
            form_layout.addRow("📝 Ad:", self.name_input)
            
            self.version_input = QLineEdit()
            self.version_input.setText("1.0.0")
            form_layout.addRow("🔢 Sürüm:", self.version_input)
            
            self.developer_input = QLineEdit()
            self.developer_input.setPlaceholderText("Geliştirici Adı")
            form_layout.addRow("👤 Geliştirici:", self.developer_input)
            
            self.category_combo = QComboBox()
            self.category_combo.addItems(["Editor", "Tools", "Themes", "Languages", "Other"])
            form_layout.addRow("🏷️ Kategori:", self.category_combo)
            
            layout.addLayout(form_layout)
            
            # Açıklama
            layout.addWidget(QLabel("📋 Açıklama:"))
            self.description_input = QTextEdit()
            self.description_input.setMaximumHeight(100)
            self.description_input.setPlaceholderText("Plugin açıklaması...")
            layout.addWidget(self.description_input)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            create_btn = QPushButton("🆕 Oluştur")
            create_btn.clicked.connect(self.accept)
            button_layout.addWidget(create_btn)
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
        
        def get_plugin_data(self) -> Dict:
            """Plugin verilerini döndür"""
            return {
                "id": self.id_input.text(),
                "name": self.name_input.text(),
                "version": self.version_input.text(),
                "description": self.description_input.toPlainText(),
                "developer": self.developer_input.text(),
                "category": self.category_combo.currentText(),
                "entry": "main.py",
                "created": datetime.now().isoformat()
            }
    
    class AppCompiler:
        """PyCloud .app derleyicisi"""
        
        def __init__(self, ide_instance):
            self.ide = ide_instance
        
        def compile_to_app(self, project_path: str, app_name: str, main_file: str) -> bool:
            """Projeyi .app formatına derle"""
            try:
                project_dir = Path(project_path)
                app_dir = project_dir.parent / f"{app_name}.app"
                
                # .app dizini oluştur
                app_dir.mkdir(exist_ok=True)
                
                # app.json oluştur
                app_json = {
                    "id": app_name.lower().replace(" ", "_"),
                    "name": app_name,
                    "version": "1.0.0",
                    "description": f"{app_name} - PyCloud OS uygulaması",
                    "entry": main_file,
                    "exec": f"python3 {main_file}",
                    "icon": "icon.png",
                    "category": "Kullanıcı",
                    "developer": "PyCloud IDE User",
                    "license": "MIT",
                    "tags": ["python", "user-app"],
                    "requires": ["python3"],
                    "permissions": ["filesystem"],
                    "signature": f"sha256:{datetime.now().timestamp()}"
                }
                
                with open(app_dir / "app.json", 'w', encoding='utf-8') as f:
                    json.dump(app_json, f, indent=2, ensure_ascii=False)
                
                # Proje dosyalarını kopyala
                for file_path in project_dir.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        relative_path = file_path.relative_to(project_dir)
                        dest_path = app_dir / relative_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                
                # Varsayılan ikon oluştur (basit PNG)
                if not (app_dir / "icon.png").exists():
                    self.create_default_icon(app_dir / "icon.png")
                
                return True
                
            except Exception as e:
                logging.getLogger("AppCompiler").error(f"App compilation error: {e}")
                return False
        
        def create_default_icon(self, icon_path: Path):
            """Varsayılan ikon oluştur"""
            try:
                # Basit bir PNG ikon oluştur (PIL gerekli)
                try:
                    from PIL import Image, ImageDraw
                    
                    # 64x64 boyutunda basit ikon
                    img = Image.new('RGBA', (64, 64), (70, 130, 180, 255))
                    draw = ImageDraw.Draw(img)
                    
                    # Basit bir daire çiz
                    draw.ellipse([10, 10, 54, 54], fill=(255, 255, 255, 255))
                    draw.ellipse([15, 15, 49, 49], fill=(70, 130, 180, 255))
                    
                    img.save(icon_path)
                    
                except ImportError:
                    # PIL yoksa basit bir metin dosyası oluştur
                    with open(icon_path.with_suffix('.txt'), 'w') as f:
                        f.write("Default icon placeholder")
                        
            except Exception as e:
                logging.getLogger("AppCompiler").error(f"Icon creation error: {e}")
    
    class CompileDialog(QDialog):
        """Derleme dialogu"""
        
        def __init__(self, compiler: AppCompiler, project_path: str, parent=None):
            super().__init__(parent)
            self.compiler = compiler
            self.project_path = project_path
            self.setup_ui()
        
        def setup_ui(self):
            """Dialog UI kurulumu"""
            self.setWindowTitle("📦 .app Olarak Derle")
            self.setGeometry(300, 300, 500, 300)
            
            layout = QVBoxLayout(self)
            
            # Bilgi
            info_label = QLabel("🔧 Projenizi PyCloud OS .app formatına derleyin:")
            layout.addWidget(info_label)
            
            # Form alanları
            form_layout = QFormLayout()
            
            self.app_name_input = QLineEdit()
            self.app_name_input.setText(Path(self.project_path).name)
            self.app_name_input.setPlaceholderText("Uygulama adı...")
            form_layout.addRow("📝 Uygulama Adı:", self.app_name_input)
            
            self.main_file_combo = QComboBox()
            self.load_python_files()
            form_layout.addRow("🐍 Ana Dosya:", self.main_file_combo)
            
            layout.addLayout(form_layout)
            
            # Açıklama
            layout.addWidget(QLabel("📋 Açıklama:"))
            self.description_input = QTextEdit()
            self.description_input.setMaximumHeight(100)
            self.description_input.setPlaceholderText("Uygulama açıklaması...")
            layout.addWidget(self.description_input)
            
            # Çıktı dizini
            output_layout = QHBoxLayout()
            output_layout.addWidget(QLabel("📁 Çıktı:"))
            self.output_label = QLabel(str(Path(self.project_path).parent))
            output_layout.addWidget(self.output_label)
            layout.addLayout(output_layout)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            compile_btn = QPushButton("📦 Derle")
            compile_btn.clicked.connect(self.compile_app)
            button_layout.addWidget(compile_btn)
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
        
        def load_python_files(self):
            """Python dosyalarını yükle"""
            project_dir = Path(self.project_path)
            python_files = list(project_dir.glob("*.py"))
            
            for py_file in python_files:
                self.main_file_combo.addItem(py_file.name)
            
            # main.py varsa seç
            if "main.py" in [f.name for f in python_files]:
                index = self.main_file_combo.findText("main.py")
                if index >= 0:
                    self.main_file_combo.setCurrentIndex(index)
        
        def compile_app(self):
            """Uygulamayı derle"""
            app_name = self.app_name_input.text().strip()
            main_file = self.main_file_combo.currentText()
            
            if not app_name:
                QMessageBox.warning(self, "Uyarı", "Uygulama adı gerekli!")
                return
            
            if not main_file:
                QMessageBox.warning(self, "Uyarı", "Ana dosya seçilmedi!")
                return
            
            # Derleme işlemi
            if self.compiler.compile_to_app(self.project_path, app_name, main_file):
                app_path = Path(self.project_path).parent / f"{app_name}.app"
                QMessageBox.information(self, "Başarılı", 
                                      f"Uygulama başarıyla derlendi!\n\n📁 Konum: {app_path}")
                self.accept()
            else:
                QMessageBox.critical(self, "Hata", "Derleme işlemi başarısız!")

    # Core modül dialog'ları
    class CoreSnippetDialog(QDialog):
        """Core snippet manager için dialog"""
        
        def __init__(self, snippet_manager, parent=None):
            super().__init__(parent)
            self.snippet_manager = snippet_manager
            self.selected_snippet = None
            self.setup_ui()
            self.load_snippets()
        
        def setup_ui(self):
            self.setWindowTitle("Kod Parçacıkları")
            self.setFixedSize(800, 600)
            
            layout = QVBoxLayout(self)
            
            # Arama
            search_layout = QHBoxLayout()
            search_layout.addWidget(QLabel("Ara:"))
            self.search_edit = QLineEdit()
            self.search_edit.textChanged.connect(self.filter_snippets)
            search_layout.addWidget(self.search_edit)
            layout.addLayout(search_layout)
            
            # Snippet listesi
            self.snippet_list = QListWidget()
            self.snippet_list.itemClicked.connect(self.show_preview)
            layout.addWidget(self.snippet_list)
            
            # Önizleme
            self.preview_text = QTextEdit()
            self.preview_text.setReadOnly(True)
            self.preview_text.setMaximumHeight(200)
            layout.addWidget(self.preview_text)
        
        def load_snippets(self):
            self.snippet_list.clear()
            if hasattr(self.snippet_manager, 'get_all_snippets'):
                snippets = self.snippet_manager.get_all_snippets()
            else:
                snippets = getattr(self.snippet_manager, 'snippets', [])
            
            for snippet in snippets:
                item = QListWidgetItem(f"{snippet.trigger} - {snippet.name}")
                item.setData(Qt.ItemDataRole.UserRole, snippet)
                self.snippet_list.addItem(item)
        
        def filter_snippets(self):
            query = self.search_edit.text().lower()
            
            for i in range(self.snippet_list.count()):
                item = self.snippet_list.item(i)
                snippet = item.data(Qt.ItemDataRole.UserRole)
                
                visible = (query in snippet.name.lower() or 
                          query in snippet.trigger.lower() or
                          query in snippet.description.lower())
                
                item.setHidden(not visible)
        
        def show_preview(self):
            current_item = self.snippet_list.currentItem()
            if current_item:
                snippet = current_item.data(Qt.ItemDataRole.UserRole)
                self.selected_snippet = snippet
                self.preview_text.setPlainText(snippet.code)
    
    class CorePluginDialog(QDialog):
        """Core plugin manager için dialog"""
        
        def __init__(self, plugin_manager, parent=None):
            super().__init__(parent)
            self.plugin_manager = plugin_manager
            self.setup_ui()
            self.load_plugins()
        
        def setup_ui(self):
            self.setWindowTitle("Eklenti Yöneticisi")
            self.setFixedSize(800, 600)
            
            layout = QVBoxLayout(self)
            
            # Plugin listesi
            self.plugin_list = QListWidget()
            self.plugin_list.itemClicked.connect(self.show_plugin_details)
            layout.addWidget(self.plugin_list)
            
            # Detaylar
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setMaximumHeight(200)
            layout.addWidget(self.details_text)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            enable_btn = QPushButton("Etkinleştir")
            enable_btn.clicked.connect(self.enable_plugin)
            button_layout.addWidget(enable_btn)
            
            disable_btn = QPushButton("Devre Dışı")
            disable_btn.clicked.connect(self.disable_plugin)
            button_layout.addWidget(disable_btn)
            
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(self.accept)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
        
        def load_plugins(self):
            self.plugin_list.clear()
            if hasattr(self.plugin_manager, 'get_available_plugins'):
                plugins = self.plugin_manager.get_available_plugins()
            else:
                plugins = getattr(self.plugin_manager, 'plugins', [])
            
            for plugin in plugins:
                status = "✅" if getattr(plugin, 'enabled', False) else "❌"
                name = getattr(plugin, 'name', 'Unknown')
                version = getattr(plugin, 'version', '1.0')
                item = QListWidgetItem(f"{status} {name} v{version}")
                item.setData(Qt.ItemDataRole.UserRole, plugin)
                self.plugin_list.addItem(item)
        
        def show_plugin_details(self):
            current_item = self.plugin_list.currentItem()
            if current_item:
                plugin = current_item.data(Qt.ItemDataRole.UserRole)
                name = getattr(plugin, 'name', 'Unknown')
                version = getattr(plugin, 'version', '1.0')
                author = getattr(plugin, 'author', 'Unknown')
                description = getattr(plugin, 'description', 'No description')
                enabled = getattr(plugin, 'enabled', False)
                
                details = f"""
Adı: {name}
Sürüm: {version}
Yazar: {author}
Açıklama: {description}
Durum: {'Etkin' if enabled else 'Devre Dışı'}
                """.strip()
                self.details_text.setPlainText(details)
        
        def enable_plugin(self):
            current_item = self.plugin_list.currentItem()
            if current_item:
                plugin = current_item.data(Qt.ItemDataRole.UserRole)
                plugin_id = getattr(plugin, 'id', '')
                if hasattr(self.plugin_manager, 'enable_plugin'):
                    if self.plugin_manager.enable_plugin(plugin_id):
                        self.load_plugins()
        
        def disable_plugin(self):
            current_item = self.plugin_list.currentItem()
            if current_item:
                plugin = current_item.data(Qt.ItemDataRole.UserRole)
                plugin_id = getattr(plugin, 'id', '')
                if hasattr(self.plugin_manager, 'disable_plugin'):
                    if self.plugin_manager.disable_plugin(plugin_id):
                        self.load_plugins()
    
    class CoreNewProjectDialog(QDialog):
        """Core template manager için yeni proje dialog'u"""
        
        def __init__(self, template_manager, parent=None):
            super().__init__(parent)
            self.template_manager = template_manager
            self.setup_ui()
            self.load_templates()
        
        def setup_ui(self):
            self.setWindowTitle("Yeni Proje Oluştur")
            self.setFixedSize(600, 500)
            
            layout = QVBoxLayout(self)
            
            # Proje adı
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Proje Adı:"))
            self.name_edit = QLineEdit()
            name_layout.addWidget(self.name_edit)
            layout.addLayout(name_layout)
            
            # Proje yolu
            path_layout = QHBoxLayout()
            path_layout.addWidget(QLabel("Proje Yolu:"))
            self.path_edit = QLineEdit()
            path_layout.addWidget(self.path_edit)
            
            browse_btn = QPushButton("Gözat")
            browse_btn.clicked.connect(self.browse_path)
            path_layout.addWidget(browse_btn)
            layout.addLayout(path_layout)
            
            # Template seçimi
            layout.addWidget(QLabel("Şablon:"))
            self.template_list = QListWidget()
            self.template_list.itemClicked.connect(self.show_template_details)
            layout.addWidget(self.template_list)
            
            # Template detayları
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setMaximumHeight(100)
            layout.addWidget(self.details_text)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            create_btn = QPushButton("Oluştur")
            create_btn.clicked.connect(self.accept)
            button_layout.addWidget(create_btn)
            
            cancel_btn = QPushButton("İptal")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
        
        def load_templates(self):
            self.template_list.clear()
            if hasattr(self.template_manager, 'get_available_templates'):
                templates = self.template_manager.get_available_templates()
            else:
                templates = []
            
            for template in templates:
                icon = getattr(template, 'icon', '📄')
                name = getattr(template, 'name', 'Unknown')
                item = QListWidgetItem(f"{icon} {name}")
                item.setData(Qt.ItemDataRole.UserRole, template)
                self.template_list.addItem(item)
        
        def show_template_details(self):
            current_item = self.template_list.currentItem()
            if current_item:
                template = current_item.data(Qt.ItemDataRole.UserRole)
                description = getattr(template, 'description', 'No description')
                self.details_text.setPlainText(description)
        
        def browse_path(self):
            path = QFileDialog.getExistingDirectory(self, "Proje Klasörü Seç")
            if path:
                self.path_edit.setText(path)
        
        def get_project_data(self):
            current_item = self.template_list.currentItem()
            if not current_item:
                return None
            
            template = current_item.data(Qt.ItemDataRole.UserRole)
            project_name = self.name_edit.text().strip()
            project_path = self.path_edit.text().strip()
            
            if not project_name or not project_path:
                return None
            
            full_path = str(Path(project_path) / project_name)
            template_id = getattr(template, 'id', 'default')
            
            return {
                'template_id': template_id,
                'project_name': project_name,
                'project_path': full_path,
                'variables': {
                    'project_name': project_name,
                    'author_name': 'PyCloud User',
                    'description': f'{project_name} projesi'
                }
            }

    class NewProjectDialog(QDialog):
        """Fallback yeni proje dialog'u"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setup_ui()
        
        def setup_ui(self):
            self.setWindowTitle("Yeni Proje")
            self.setFixedSize(400, 200)
            
            layout = QVBoxLayout(self)
            
            # Proje adı
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Proje Adı:"))
            self.name_edit = QLineEdit()
            name_layout.addWidget(self.name_edit)
            layout.addLayout(name_layout)
            
            # Proje yolu
            path_layout = QHBoxLayout()
            path_layout.addWidget(QLabel("Proje Yolu:"))
            self.path_edit = QLineEdit()
            path_layout.addWidget(self.path_edit)
            
            browse_btn = QPushButton("Gözat")
            browse_btn.clicked.connect(self.browse_path)
            path_layout.addWidget(browse_btn)
            layout.addLayout(path_layout)
            
            # Template seçimi
            layout.addWidget(QLabel("Şablon:"))
            self.template_list = QListWidget()
            self.template_list.itemClicked.connect(self.show_template_details)
            layout.addWidget(self.template_list)
            
            # Template detayları
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setMaximumHeight(100)
            layout.addWidget(self.details_text)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            create_btn = QPushButton("Oluştur")
            create_btn.clicked.connect(self.accept)
            button_layout.addWidget(create_btn)
            
            cancel_btn = QPushButton("İptal")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
        
        def browse_path(self):
            path = QFileDialog.getExistingDirectory(self, "Proje Klasörü Seç")
            if path:
                self.path_edit.setText(path)
        
        def show_template_details(self):
            current_item = self.template_list.currentItem()
            if current_item:
                template = current_item.data(Qt.ItemDataRole.UserRole)
                self.details_text.setPlainText(template.description)
        
        def get_project_data(self):
            return {
                'project_name': self.name_edit.text().strip(),
                'project_path': self.path_edit.text().strip(),
                'template_id': self.template_list.currentItem().data(Qt.ItemDataRole.UserRole).id,
                'variables': {}
            }

    # Text-mode PyIDE (PyQt6 yoksa)
    class CloudPyIDEText:
        """Text-mode Python IDE"""
        
        def __init__(self, kernel=None):
            self.kernel = kernel
            self.current_file = None
            self.content = ""
        
        def show(self):
            """IDE'yi göster"""
            print("PyCloud Python IDE v1.0 (Text Mode)")
            print("Komutlar: :new, :open <file>, :save, :run, :quit")
            print()
            
            while True:
                try:
                    line = input("pyide> ")
                    
                    if line.startswith(':'):
                        if not self.handle_command(line[1:]):
                            break
                    else:
                        self.content += line + "\n"
                        
                except KeyboardInterrupt:
                    print("\nIDE kapatılıyor...")
                    break
                except EOFError:
                    break
        
        def handle_command(self, command: str) -> bool:
            """Komut işle"""
            parts = command.split()
            if not parts:
                return True
            
            cmd = parts[0]
            
            if cmd == 'quit' or cmd == 'q':
                return False
            
            elif cmd == 'new':
                self.content = ""
                self.current_file = None
                print("Yeni dosya oluşturuldu")
            
            elif cmd == 'open':
                if len(parts) > 1:
                    try:
                        with open(parts[1], 'r', encoding='utf-8') as f:
                            self.content = f.read()
                        self.current_file = parts[1]
                        print(f"Dosya yüklendi: {parts[1]}")
                        print(f"İçerik ({len(self.content)} karakter):")
                        print(self.content[:200] + "..." if len(self.content) > 200 else self.content)
                    except Exception as e:
                        print(f"Hata: {e}")
                else:
                    print("Kullanım: :open <dosya>")
            
            elif cmd == 'save':
                if len(parts) > 1:
                    self.current_file = parts[1]
                
                if self.current_file:
                    try:
                        with open(self.current_file, 'w', encoding='utf-8') as f:
                            f.write(self.content)
                        print(f"Dosya kaydedildi: {self.current_file}")
                    except Exception as e:
                        print(f"Hata: {e}")
                else:
                    print("Dosya yolu belirtilmedi")
            
            elif cmd == 'run':
                if self.current_file and self.current_file.endswith('.py'):
                    try:
                        print(f"Çalıştırılıyor: {self.current_file}")
                        os.system(f"python3 {self.current_file}")
                    except Exception as e:
                        print(f"Hata: {e}")
                else:
                    print("Python dosyası seçili değil")
            
            elif cmd == 'help':
                print("Komutlar:")
                print("  :new         - Yeni dosya")
                print("  :open <file> - Dosya aç")
                print("  :save [file] - Kaydet")
                print("  :run         - Python dosyasını çalıştır")
                print("  :quit        - Çık")
            
            else:
                print(f"Bilinmeyen komut: {cmd}")
            
            return True

    # Ana fonksiyonlar
    def create_pyide(kernel=None):
        """PyIDE uygulaması oluştur"""
        if PYQT_AVAILABLE:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            ide = ModernCloudPyIDE(kernel)
            ide.show()
            return ide
        else:
            return CloudPyIDEText(kernel)

    def create_pyide_app(kernel=None):
        """PyIDE uygulaması oluştur (alias)"""
        return create_pyide(kernel)

    def run_pyide(kernel=None):
        """PyIDE'yi çalıştır"""
        if PYQT_AVAILABLE:
            # QApplication oluştur
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            ide = ModernCloudPyIDE(kernel)
            
            # ✅ ÇÖZÜM: Command line argumentlarını parse et
            import argparse
            parser = argparse.ArgumentParser(description='Cloud PyIDE')
            parser.add_argument('--open-file', dest='open_file', help='Açılacak dosya yolu')
            parser.add_argument('--open-path', dest='open_path', help='Açılacak proje yolu')
            parser.add_argument('files', nargs='*', help='Açılacak dosyalar')
            
            # sys.argv'yi parse et
            try:
                args, unknown = parser.parse_known_args()
                
                # Dosya açma parametresi varsa
                if args.open_file:
                    print(f"🚀 PyIDE dosya açıyor: {args.open_file}")
                    ide.open_file_in_editor(args.open_file)
                
                # Proje açma parametresi varsa
                elif args.open_path:
                    print(f"🚀 PyIDE proje açıyor: {args.open_path}")
                    if Path(args.open_path).exists():
                        ide.explorer.load_project(args.open_path)
                
                # Doğrudan dosya listesi varsa
                elif args.files:
                    for file_path in args.files:
                        if Path(file_path).exists():
                            print(f"🚀 PyIDE dosya açıyor: {file_path}")
                            ide.open_file_in_editor(file_path)
                            
            except Exception as e:
                print(f"⚠️ PyIDE argument parsing error: {e}")
                # Argumentlar parse edilemezse normal başlat
            
            ide.show()
            return ide
        else:
            ide = CloudPyIDEText(kernel)
            
            # Text mode için de dosya açma desteği
            import argparse
            parser = argparse.ArgumentParser(description='Cloud PyIDE (Text Mode)')
            parser.add_argument('--open-file', dest='open_file', help='Açılacak dosya yolu')
            parser.add_argument('files', nargs='*', help='Açılacak dosyalar')
            
            try:
                args, unknown = parser.parse_known_args()
                
                if args.open_file and Path(args.open_file).exists():
                    print(f"🚀 PyIDE (Text) dosya açıyor: {args.open_file}")
                    ide.handle_command(f"open {args.open_file}")
                elif args.files:
                    for file_path in args.files:
                        if Path(file_path).exists():
                            print(f"🚀 PyIDE (Text) dosya açıyor: {file_path}")
                            ide.handle_command(f"open {file_path}")
                            break  # Text mode'da sadece ilk dosyayı aç
            except Exception as e:
                print(f"⚠️ PyIDE (Text) argument parsing error: {e}")
            
            ide.show()
            return None

    if __name__ == "__main__":
        run_pyide() 