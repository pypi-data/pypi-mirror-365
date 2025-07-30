"""
Cloud Task Manager - Modern UI Widget'ları
macOS Activity Monitor tarzı modern bileşenler
"""

import sys
from typing import List, Optional
from collections import deque

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("PyQt6 not available for widgets")
    sys.exit(1)

class ModernTabWidget(QTabWidget):
    """Modern sekmeli widget"""
    
    def __init__(self):
        super().__init__()
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setMovable(False)
        self.setTabsClosable(False)
        
        # Modern stil
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #ffffff;
                margin-top: -1px;
            }
            
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
                color: #007bff;
            }
            
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)

class SystemOverviewWidget(QWidget):
    """Sistem özeti widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(120)
        self.setup_ui()
        
    def setup_ui(self):
        """UI kurulumu"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(30)
        
        # CPU
        self.cpu_widget = self.create_metric_widget("CPU", "0%", "#007bff")
        layout.addWidget(self.cpu_widget)
        
        # Memory
        self.memory_widget = self.create_metric_widget("Memory", "0%", "#28a745")
        layout.addWidget(self.memory_widget)
        
        # Disk
        self.disk_widget = self.create_metric_widget("Disk", "0%", "#ffc107")
        layout.addWidget(self.disk_widget)
        
        # Network
        self.network_widget = self.create_metric_widget("Network", "0 MB/s", "#dc3545")
        layout.addWidget(self.network_widget)
        
        # Processes
        self.processes_widget = self.create_metric_widget("Processes", "0", "#6f42c1")
        layout.addWidget(self.processes_widget)
        
        # Modern stil
        self.setStyleSheet("""
            SystemOverviewWidget {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 12px;
            }
        """)
    
    def create_metric_widget(self, title: str, value: str, color: str) -> QWidget:
        """Metrik widget'ı oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: #6c757d;
            margin-bottom: 5px;
        """)
        layout.addWidget(title_label)
        
        # Değer
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {color};
        """)
        layout.addWidget(value_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setTextVisible(False)
        progress.setFixedHeight(6)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: #e9ecef;
            }}
            
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)
        
        # Widget'a referansları sakla
        widget.title_label = title_label
        widget.value_label = value_label
        widget.progress = progress
        
        return widget
    
    def update_stats(self, stats):
        """İstatistikleri güncelle"""
        # CPU
        self.cpu_widget.value_label.setText(f"{stats.cpu_percent:.1f}%")
        self.cpu_widget.progress.setValue(int(stats.cpu_percent))
        
        # Memory
        self.memory_widget.value_label.setText(f"{stats.memory_percent:.1f}%")
        self.memory_widget.progress.setValue(int(stats.memory_percent))
        
        # Disk
        self.disk_widget.value_label.setText(f"{stats.disk_percent:.1f}%")
        self.disk_widget.progress.setValue(int(stats.disk_percent))
        
        # Network
        self.network_widget.value_label.setText(f"{stats.network_mb:.1f} MB/s")
        network_percent = min(100, (stats.network_mb / 10) * 100)  # 10 MB/s = 100%
        self.network_widget.progress.setValue(int(network_percent))
        
        # Processes
        self.processes_widget.value_label.setText(str(stats.process_count))
        process_percent = min(100, (stats.process_count / 500) * 100)  # 500 process = 100%
        self.processes_widget.progress.setValue(int(process_percent))

class ProcessTableWidget(QTableWidget):
    """Modern işlem tablosu"""
    
    def __init__(self, table_type: str = "processes"):
        super().__init__()
        self.table_type = table_type
        self.setup_table()
    
    def setup_table(self):
        """Tablo kurulumu"""
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        
        # Header ayarları
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setHighlightSections(False)
        
        # Vertical header gizle
        self.verticalHeader().setVisible(False)
        
        # Modern stil
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #f8f9fa;
                selection-background-color: #007bff;
                selection-color: white;
                font-size: 13px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 2px solid #dee2e6;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #495057;
            }
            
            QHeaderView::section:hover {
                background-color: #e9ecef;
            }
        """)

class ThreadTableWidget(QTableWidget):
    """Modern thread tablosu"""
    
    def __init__(self):
        super().__init__()
        self.setup_table()
    
    def setup_table(self):
        """Tablo kurulumu"""
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        
        # Header ayarları
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setHighlightSections(False)
        
        # Vertical header gizle
        self.verticalHeader().setVisible(False)
        
        # Thread tablosu için özel stil
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #f8f9fa;
                selection-background-color: #6f42c1;
                selection-color: white;
                font-size: 13px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f8f9fa;
            }
            
            QTableWidget::item:selected {
                background-color: #6f42c1;
                color: white;
            }
            
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 2px solid #dee2e6;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #495057;
            }
        """)

class ResourceGraphWidget(QWidget):
    """Kaynak kullanımı grafiği"""
    
    def __init__(self, title: str, unit: str, max_value: float = 100):
        super().__init__()
        self.title = title
        self.unit = unit
        self.max_value = max_value
        self.data_points = deque(maxlen=60)  # Son 60 veri noktası
        self.setMinimumSize(300, 200)
        
        # Başlangıç verileri
        for _ in range(60):
            self.data_points.append(0)
    
    def add_data_point(self, value: float):
        """Yeni veri noktası ekle"""
        self.data_points.append(value)
        self.update()  # Widget'ı yeniden çiz
    
    def paintEvent(self, event):
        """Grafik çizimi"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor("#ffffff"))
        
        # Kenarlık
        painter.setPen(QPen(QColor("#dee2e6"), 1))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 8, 8)
        
        # Başlık
        painter.setPen(QColor("#495057"))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_rect = QRect(10, 10, self.width() - 20, 20)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft, self.title)
        
        # Grafik alanı
        graph_rect = QRect(20, 40, self.width() - 40, self.height() - 70)
        
        # Grid çizgileri
        painter.setPen(QPen(QColor("#f8f9fa"), 1))
        for i in range(5):
            y = graph_rect.top() + (graph_rect.height() * i / 4)
            painter.drawLine(graph_rect.left(), y, graph_rect.right(), y)
        
        # Veri çizgisi
        if len(self.data_points) > 1:
            painter.setPen(QPen(QColor("#007bff"), 2))
            
            points = []
            for i, value in enumerate(self.data_points):
                x = graph_rect.left() + (graph_rect.width() * i / (len(self.data_points) - 1))
                y = graph_rect.bottom() - (graph_rect.height() * value / self.max_value)
                points.append(QPointF(x, y))
            
            # Çizgiyi çiz
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
        
        # Değer etiketi
        if self.data_points:
            current_value = self.data_points[-1]
            painter.setPen(QColor("#495057"))
            painter.setFont(QFont("Arial", 10))
            value_text = f"{current_value:.1f} {self.unit}"
            value_rect = QRect(10, self.height() - 25, self.width() - 20, 20)
            painter.drawText(value_rect, Qt.AlignmentFlag.AlignRight, value_text)

class ModernProgressBar(QProgressBar):
    """Modern progress bar"""
    
    def __init__(self, color: str = "#007bff"):
        super().__init__()
        self.color = color
        self.setTextVisible(False)
        self.setFixedHeight(8)
        
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #e9ecef;
            }}
            
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

class ModernButton(QPushButton):
    """Modern buton"""
    
    def __init__(self, text: str, button_type: str = "primary"):
        super().__init__(text)
        
        colors = {
            "primary": "#007bff",
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "secondary": "#6c757d"
        }
        
        color = colors.get(button_type, "#007bff")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.2)};
            }}
            
            QPushButton:disabled {{
                background-color: #e9ecef;
                color: #6c757d;
            }}
        """)
    
    def _darken_color(self, color: str, factor: float = 0.1) -> str:
        """Rengi koyulaştır"""
        # Basit renk koyulaştırma
        if color == "#007bff":
            return "#0056b3"
        elif color == "#28a745":
            return "#1e7e34"
        elif color == "#dc3545":
            return "#c82333"
        elif color == "#ffc107":
            return "#e0a800"
        elif color == "#6c757d":
            return "#545b62"
        return color

class ModernSearchBox(QLineEdit):
    """Modern arama kutusu"""
    
    def __init__(self, placeholder: str = "Search..."):
        super().__init__()
        self.setPlaceholderText(placeholder)
        
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #ffffff;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QLineEdit:hover {
                border-color: #dee2e6;
            }
        """)

class StatusIndicator(QWidget):
    """Durum göstergesi"""
    
    def __init__(self, status: str = "unknown"):
        super().__init__()
        self.status = status
        self.setFixedSize(12, 12)
    
    def set_status(self, status: str):
        """Durumu değiştir"""
        self.status = status
        self.update()
    
    def paintEvent(self, event):
        """Durum göstergesi çizimi"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = {
            "running": "#28a745",
            "stopped": "#dc3545",
            "suspended": "#ffc107",
            "unknown": "#6c757d"
        }
        
        color = QColor(colors.get(self.status, "#6c757d"))
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect()) 