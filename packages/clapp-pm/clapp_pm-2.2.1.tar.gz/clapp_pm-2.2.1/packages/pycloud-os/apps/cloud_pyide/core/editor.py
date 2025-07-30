"""
Cloud PyIDE - Sekmeli Editör Arayüzü
Modern kod editörü ve sekme yönetimi
"""

import os
import logging
from pathlib import Path
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
class EditorTab:
    """Editör sekmesi"""
    file_path: str
    editor: 'ModernCodeEditor'
    is_modified: bool = False
    is_new_file: bool = True

class ModernCodeEditor(QPlainTextEdit):
    """Modern kod editörü"""
    
    # Sinyaller
    content_changed = pyqtSignal()
    file_saved = pyqtSignal(str)
    breakpoint_toggled = pyqtSignal(int, bool)
    
    def __init__(self, parent=None, theme_mode="dark"):
        super().__init__(parent)
        self.theme_mode = theme_mode
        self.file_path = None
        self.is_modified = False
        
        # Line number area
        self.line_number_area = LineNumberArea(self)
        
        # Breakpoints
        self.breakpoints: Dict[int, bool] = {}
        
        # Setup
        self.setup_editor()
        self.setup_connections()
        self.apply_theme()
    
    def setup_editor(self):
        """Editör kurulumu"""
        # Font
        font = QFont("JetBrains Mono", 12)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Tab ayarları
        tab_width = 4
        metrics = QFontMetrics(font)
        self.setTabStopDistance(tab_width * metrics.horizontalAdvance(' '))
        
        # Line wrapping
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Cursor
        self.setCursorWidth(2)
        
        # Margins
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
        # Current line highlighting
        self.highlight_current_line()
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.textChanged.connect(self.on_text_changed)
    
    def apply_theme(self):
        """Tema uygula"""
        if self.theme_mode == "dark":
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: none;
                    selection-background-color: #264f78;
                }
            """)
        else:
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: none;
                    selection-background-color: #add6ff;
                }
            """)
    
    def line_number_area_width(self):
        """Line number area genişliği"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self):
        """Line number area genişliğini güncelle"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Line number area'yı güncelle"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                       self.line_number_area.width(), 
                                       rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()
    
    def resizeEvent(self, event):
        """Resize olayı"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), 
                  self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Line number area paint olayı"""
        painter = QPainter(self.line_number_area)
        
        if self.theme_mode == "dark":
            painter.fillRect(event.rect(), QColor("#252526"))
            painter.setPen(QColor("#858585"))
        else:
            painter.fillRect(event.rect(), QColor("#f8f8f8"))
            painter.setPen(QColor("#237893"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                
                # Breakpoint kontrolü
                if block_number + 1 in self.breakpoints:
                    # Breakpoint çiz
                    painter.fillRect(0, int(top), self.line_number_area.width(), height, 
                                   QColor("#ff0000"))
                
                painter.drawText(0, int(top), self.line_number_area.width(), height,
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlight_current_line(self):
        """Mevcut satırı vurgula"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            if self.theme_mode == "dark":
                line_color = QColor("#2a2d2e")
            else:
                line_color = QColor("#f0f0f0")
            
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def toggle_breakpoint(self, line_number: int):
        """Breakpoint toggle"""
        if line_number in self.breakpoints:
            del self.breakpoints[line_number]
            enabled = False
        else:
            self.breakpoints[line_number] = True
            enabled = True
        
        self.line_number_area.update()
        self.breakpoint_toggled.emit(line_number, enabled)
    
    def mousePressEvent(self, event):
        """Mouse press olayı"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Line number area'da tıklama kontrolü
            if event.position().x() < self.line_number_area_width():
                cursor = self.cursorForPosition(event.position().toPoint())
                line_number = cursor.blockNumber() + 1
                self.toggle_breakpoint(line_number)
                return
        
        super().mousePressEvent(event)
    
    def on_text_changed(self):
        """Metin değişti"""
        self.is_modified = True
        self.content_changed.emit()
    
    def set_file_path(self, file_path: str):
        """Dosya yolunu ayarla"""
        self.file_path = file_path
        self.is_modified = False
    
    def get_current_line(self) -> int:
        """Mevcut satır numarası"""
        return self.textCursor().blockNumber() + 1
    
    def get_current_column(self) -> int:
        """Mevcut sütun numarası"""
        return self.textCursor().columnNumber()
    
    def goto_line(self, line_number: int):
        """Belirtilen satıra git"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.Down, 
                          QTextCursor.MoveMode.MoveAnchor, line_number - 1)
        self.setTextCursor(cursor)
        self.centerCursor()
    
    def insert_text_at_cursor(self, text: str):
        """Cursor pozisyonuna metin ekle"""
        cursor = self.textCursor()
        cursor.insertText(text)
    
    def get_selected_text(self) -> str:
        """Seçili metni al"""
        return self.textCursor().selectedText()
    
    def replace_selected_text(self, text: str):
        """Seçili metni değiştir"""
        cursor = self.textCursor()
        cursor.insertText(text)

class LineNumberArea(QWidget):
    """Line number area widget'ı"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

class TabWidget(QTabWidget):
    """Editör sekme widget'ı"""
    
    # Sinyaller
    tab_closed = pyqtSignal(int)
    tab_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        
        # Bağlantılar
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.tab_changed.emit)
    
    def close_tab(self, index: int):
        """Sekme kapat"""
        self.tab_closed.emit(index)
    
    def add_editor_tab(self, editor: ModernCodeEditor, title: str) -> int:
        """Editör sekmesi ekle"""
        index = self.addTab(editor, title)
        self.setCurrentIndex(index)
        return index
    
    def get_current_editor(self) -> Optional[ModernCodeEditor]:
        """Mevcut editörü al"""
        widget = self.currentWidget()
        if isinstance(widget, ModernCodeEditor):
            return widget
        return None
    
    def get_editor_at(self, index: int) -> Optional[ModernCodeEditor]:
        """Belirtilen indeksteki editörü al"""
        widget = self.widget(index)
        if isinstance(widget, ModernCodeEditor):
            return widget
        return None
    
    def update_tab_title(self, index: int, title: str, is_modified: bool = False):
        """Sekme başlığını güncelle"""
        if is_modified:
            title = f"● {title}"
        self.setTabText(index, title) 