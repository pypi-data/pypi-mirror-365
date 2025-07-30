"""
Cloud Task Manager - Modern Ana Uygulama
macOS Activity Monitor tarzı sistem görev yöneticisi
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
    print("PyQt6 not available for Cloud Task Manager")
    sys.exit(1)

from .system_monitor import SystemMonitor
from .process_manager import ProcessManager
from .thread_manager import ThreadManager
from .widgets import ModernTabWidget, SystemOverviewWidget, ProcessTableWidget, ThreadTableWidget, ResourceGraphWidget

class CloudTaskManager(QMainWindow):
    """Modern Cloud Task Manager Ana Uygulaması"""
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("CloudTaskManager")
        
        # Core managers
        self.system_monitor = SystemMonitor()
        self.process_manager = ProcessManager(kernel)
        self.thread_manager = ThreadManager(kernel)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_data)
        self.update_interval = 2000  # 2 saniye
        
        # UI kurulumu
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
        # Monitoring başlat
        self.start_monitoring()
        
        self.logger.info("Cloud Task Manager v2.0.0 initialized")
    
    def setup_ui(self):
        """Modern UI kurulumu"""
        self.setWindowTitle("Cloud Task Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sistem özeti (üst panel)
        self.system_overview = SystemOverviewWidget()
        main_layout.addWidget(self.system_overview)
        
        # Ana tab widget
        self.tab_widget = ModernTabWidget()
        self.setup_tabs()
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
    
    def setup_tabs(self):
        """Sekmeleri kur - .cursorrules uyumlu"""
        # Applications sekmesi
        self.applications_widget = QWidget()
        self.setup_applications_tab()
        self.tab_widget.addTab(self.applications_widget, "🚀 Applications")
        
        # Processes sekmesi
        self.processes_widget = QWidget()
        self.setup_processes_tab()
        self.tab_widget.addTab(self.processes_widget, "⚙️ Processes")
        
        # Threads sekmesi
        self.threads_widget = QWidget()
        self.setup_threads_tab()
        self.tab_widget.addTab(self.threads_widget, "🧵 Threads")
        
        # Resources sekmesi
        self.resources_widget = QWidget()
        self.setup_resources_tab()
        self.tab_widget.addTab(self.resources_widget, "📊 Resources")
    
    def setup_applications_tab(self):
        """Applications sekmesi - PyCloud uygulamaları"""
        layout = QVBoxLayout(self.applications_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık ve açıklama
        title_label = QLabel("Running Applications")
        title_label.setObjectName("tabTitle")
        layout.addWidget(title_label)
        
        desc_label = QLabel("PyCloud OS uygulamaları ve durumları")
        desc_label.setObjectName("tabDescription")
        layout.addWidget(desc_label)
        
        # Filtre ve arama
        filter_layout = QHBoxLayout()
        
        self.app_search = QLineEdit()
        self.app_search.setPlaceholderText("🔍 Uygulama ara...")
        self.app_search.textChanged.connect(self.filter_applications)
        filter_layout.addWidget(self.app_search)
        
        self.app_status_filter = QComboBox()
        self.app_status_filter.addItems(["All", "Running", "Suspended", "Stopped"])
        self.app_status_filter.currentTextChanged.connect(self.filter_applications)
        filter_layout.addWidget(self.app_status_filter)
        
        layout.addLayout(filter_layout)
        
        # Uygulama tablosu
        self.app_table = ProcessTableWidget("applications")
        self.app_table.setColumnCount(6)
        self.app_table.setHorizontalHeaderLabels([
            "Application", "Status", "PID", "Memory", "CPU %", "Threads"
        ])
        
        # Tablo ayarları
        header = self.app_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.app_table, 1)
    
    def setup_processes_tab(self):
        """Processes sekmesi - Sistem işlemleri"""
        layout = QVBoxLayout(self.processes_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel("System Processes")
        title_label.setObjectName("tabTitle")
        layout.addWidget(title_label)
        
        desc_label = QLabel("Tüm sistem işlemleri ve process ağacı")
        desc_label.setObjectName("tabDescription")
        layout.addWidget(desc_label)
        
        # Filtre ve kontroller
        filter_layout = QHBoxLayout()
        
        self.process_search = QLineEdit()
        self.process_search.setPlaceholderText("🔍 İşlem ara...")
        self.process_search.textChanged.connect(self.filter_processes)
        filter_layout.addWidget(self.process_search)
        
        self.process_sort = QComboBox()
        self.process_sort.addItems(["CPU", "Memory", "PID", "Name"])
        self.process_sort.currentTextChanged.connect(self.sort_processes)
        filter_layout.addWidget(self.process_sort)
        
        self.show_system_cb = QCheckBox("Show System Processes")
        self.show_system_cb.setChecked(True)
        self.show_system_cb.toggled.connect(self.filter_processes)
        filter_layout.addWidget(self.show_system_cb)
        
        layout.addLayout(filter_layout)
        
        # İşlem tablosu
        self.process_table = ProcessTableWidget("processes")
        self.process_table.setColumnCount(8)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "Name", "Status", "CPU %", "Memory", "Threads", "User", "Command"
        ])
        
        # Bağlam menüsü
        self.process_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.process_table.customContextMenuRequested.connect(self.show_process_context_menu)
        
        layout.addWidget(self.process_table, 1)
    
    def setup_threads_tab(self):
        """Threads sekmesi - Thread izleme"""
        layout = QVBoxLayout(self.threads_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel("Thread Monitor")
        title_label.setObjectName("tabTitle")
        layout.addWidget(title_label)
        
        desc_label = QLabel("Aktif thread'ler ve TID bazlı görünüm")
        desc_label.setObjectName("tabDescription")
        layout.addWidget(desc_label)
        
        # Thread kontrolleri
        control_layout = QHBoxLayout()
        
        self.thread_search = QLineEdit()
        self.thread_search.setPlaceholderText("🔍 Thread ara...")
        self.thread_search.textChanged.connect(self.filter_threads)
        control_layout.addWidget(self.thread_search)
        
        self.thread_process_filter = QComboBox()
        self.thread_process_filter.addItem("All Processes")
        self.thread_process_filter.currentTextChanged.connect(self.filter_threads)
        control_layout.addWidget(self.thread_process_filter)
        
        layout.addLayout(control_layout)
        
        # Thread tablosu
        self.thread_table = ThreadTableWidget()
        self.thread_table.setColumnCount(7)
        self.thread_table.setHorizontalHeaderLabels([
            "TID", "Process", "PID", "Status", "CPU %", "Priority", "State"
        ])
        
        # Bağlam menüsü
        self.thread_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.thread_table.customContextMenuRequested.connect(self.show_thread_context_menu)
        
        layout.addWidget(self.thread_table, 1)
    
    def setup_resources_tab(self):
        """Resources sekmesi - Kaynak grafikleri"""
        layout = QVBoxLayout(self.resources_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel("System Resources")
        title_label.setObjectName("tabTitle")
        layout.addWidget(title_label)
        
        desc_label = QLabel("Gerçek zamanlı sistem kaynak kullanımı")
        desc_label.setObjectName("tabDescription")
        layout.addWidget(desc_label)
        
        # Kaynak grafikleri
        graphs_layout = QGridLayout()
        
        # CPU grafiği
        self.cpu_graph = ResourceGraphWidget("CPU Usage", "%", max_value=100)
        graphs_layout.addWidget(self.cpu_graph, 0, 0)
        
        # Memory grafiği
        self.memory_graph = ResourceGraphWidget("Memory Usage", "GB", max_value=16)
        graphs_layout.addWidget(self.memory_graph, 0, 1)
        
        # Disk I/O grafiği
        self.disk_graph = ResourceGraphWidget("Disk I/O", "MB/s", max_value=100)
        graphs_layout.addWidget(self.disk_graph, 1, 0)
        
        # Network grafiği
        self.network_graph = ResourceGraphWidget("Network", "MB/s", max_value=100)
        graphs_layout.addWidget(self.network_graph, 1, 1)
        
        layout.addLayout(graphs_layout, 1)
        
        # Detaylı sistem bilgileri
        self.setup_system_info_panel()
        layout.addWidget(self.system_info_panel)
    
    def setup_system_info_panel(self):
        """Sistem bilgi paneli"""
        self.system_info_panel = QGroupBox("System Information")
        layout = QGridLayout(self.system_info_panel)
        
        # Sistem bilgileri
        self.cpu_cores_label = QLabel("CPU Cores: --")
        self.memory_total_label = QLabel("Total Memory: --")
        self.uptime_label = QLabel("Uptime: --")
        self.processes_count_label = QLabel("Processes: --")
        
        layout.addWidget(self.cpu_cores_label, 0, 0)
        layout.addWidget(self.memory_total_label, 0, 1)
        layout.addWidget(self.uptime_label, 1, 0)
        layout.addWidget(self.processes_count_label, 1, 1)
    
    def setup_control_panel(self):
        """Alt kontrol paneli"""
        self.control_panel = QWidget()
        self.control_panel.setFixedHeight(60)
        
        layout = QHBoxLayout(self.control_panel)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Sol taraf - eylem butonları
        self.end_task_btn = QPushButton("End Task")
        self.end_task_btn.setObjectName("dangerButton")
        self.end_task_btn.clicked.connect(self.end_selected_task)
        self.end_task_btn.setEnabled(False)
        layout.addWidget(self.end_task_btn)
        
        self.force_quit_btn = QPushButton("Force Quit")
        self.force_quit_btn.setObjectName("dangerButton")
        self.force_quit_btn.clicked.connect(self.force_quit_selected)
        self.force_quit_btn.setEnabled(False)
        layout.addWidget(self.force_quit_btn)
        
        self.suspend_btn = QPushButton("Suspend")
        self.suspend_btn.clicked.connect(self.suspend_selected)
        self.suspend_btn.setEnabled(False)
        layout.addWidget(self.suspend_btn)
        
        layout.addStretch()
        
        # Sağ taraf - ayarlar
        self.auto_refresh_cb = QCheckBox("Auto Refresh")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        layout.addWidget(self.auto_refresh_cb)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.manual_refresh)
        layout.addWidget(self.refresh_btn)
        
        # Update interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Update:"))
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1s", "2s", "5s", "10s"])
        self.interval_combo.setCurrentText("2s")
        self.interval_combo.currentTextChanged.connect(self.change_update_interval)
        interval_layout.addWidget(self.interval_combo)
        
        layout.addLayout(interval_layout)
    
    def setup_toolbar(self):
        """Toolbar kurulumu"""
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setMovable(False)
        
        # Tema değiştirici
        theme_action = QAction("🌓", self)
        theme_action.setToolTip("Toggle Theme")
        theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(theme_action)
        
        self.toolbar.addSeparator()
        
        # Ayarlar
        settings_action = QAction("⚙️", self)
        settings_action.setToolTip("Settings")
        settings_action.triggered.connect(self.show_settings)
        self.toolbar.addAction(settings_action)
        
        # Yardım
        help_action = QAction("❓", self)
        help_action.setToolTip("Help")
        help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(help_action)
    
    def setup_statusbar(self):
        """Status bar kurulumu"""
        self.status_bar = self.statusBar()
        
        # Sol taraf - durum
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Sağ taraf - bilgiler
        self.update_status_label = QLabel("Last update: --")
        self.status_bar.addPermanentWidget(self.update_status_label)
        
        self.selected_count_label = QLabel("0 selected")
        self.status_bar.addPermanentWidget(self.selected_count_label)
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        # Tab değişimi
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Tablo seçimleri
        self.app_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.process_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.thread_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def apply_modern_style(self):
        """Modern stil uygula"""
        self.setStyleSheet("""
            /* Ana pencere */
            QMainWindow {
                background-color: #f8f9fa;
            }
            
            /* Tab başlıkları */
            QLabel#tabTitle {
                font-size: 24px;
                font-weight: 700;
                color: #212529;
                margin-bottom: 5px;
            }
            
            QLabel#tabDescription {
                font-size: 14px;
                color: #6c757d;
                margin-bottom: 20px;
            }
            
            /* Butonlar */
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
            
            QPushButton#dangerButton {
                background-color: #dc3545;
            }
            
            QPushButton#dangerButton:hover {
                background-color: #c82333;
            }
            
            /* Tablolar */
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #e9ecef;
                selection-background-color: #007bff;
                selection-color: white;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px;
                font-weight: 600;
            }
            
            /* Kontrol paneli */
            QWidget#controlPanel {
                background-color: #ffffff;
                border-top: 1px solid #dee2e6;
            }
            
            /* Toolbar */
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #dee2e6;
                spacing: 10px;
                padding: 8px;
            }
            
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 6px;
                font-size: 16px;
            }
            
            QToolBar QToolButton:hover {
                background-color: #f8f9fa;
            }
            
            /* Status bar */
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
            }
        """)
    
    def apply_theme(self):
        """Tema uygula"""
        # Şimdilik açık tema
        pass
    
    def start_monitoring(self):
        """Monitoring başlat"""
        self.system_monitor.start()
        self.process_manager.start()
        self.thread_manager.start()
        
        self.update_timer.start(self.update_interval)
        self.logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """Monitoring durdur"""
        self.update_timer.stop()
        self.system_monitor.stop()
        self.process_manager.stop()
        self.thread_manager.stop()
        
        self.logger.info("Monitoring stopped")
    
    def update_all_data(self):
        """Tüm verileri güncelle"""
        try:
            # Sistem özeti güncelle
            self.update_system_overview()
            
            # Aktif sekmeye göre güncelle
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 0:  # Applications
                self.update_applications()
            elif current_tab == 1:  # Processes
                self.update_processes()
            elif current_tab == 2:  # Threads
                self.update_threads()
            elif current_tab == 3:  # Resources
                self.update_resources()
            
            # Status bar güncelle
            self.update_status_label.setText(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
    
    def update_system_overview(self):
        """Sistem özeti güncelle"""
        stats = self.system_monitor.get_system_stats()
        self.system_overview.update_stats(stats)
    
    def update_applications(self):
        """Uygulamaları güncelle"""
        apps = self.process_manager.get_applications()
        self.populate_app_table(apps)
    
    def update_processes(self):
        """İşlemleri güncelle"""
        processes = self.process_manager.get_processes()
        self.populate_process_table(processes)
    
    def update_threads(self):
        """Thread'leri güncelle"""
        threads = self.thread_manager.get_threads()
        self.populate_thread_table(threads)
        
        # Process filter güncelle
        processes = list(set([t.process_name for t in threads]))
        current_text = self.thread_process_filter.currentText()
        self.thread_process_filter.clear()
        self.thread_process_filter.addItem("All Processes")
        self.thread_process_filter.addItems(sorted(processes))
        
        # Önceki seçimi geri yükle
        index = self.thread_process_filter.findText(current_text)
        if index >= 0:
            self.thread_process_filter.setCurrentIndex(index)
    
    def update_resources(self):
        """Kaynakları güncelle"""
        stats = self.system_monitor.get_system_stats()
        
        # Grafikleri güncelle
        self.cpu_graph.add_data_point(stats.cpu_percent)
        self.memory_graph.add_data_point(stats.memory_used_gb)
        self.disk_graph.add_data_point(stats.disk_io_mb)
        self.network_graph.add_data_point(stats.network_mb)
        
        # Sistem bilgileri güncelle
        self.cpu_cores_label.setText(f"CPU Cores: {stats.cpu_cores}")
        self.memory_total_label.setText(f"Total Memory: {stats.memory_total_gb:.1f} GB")
        self.uptime_label.setText(f"Uptime: {stats.uptime_hours:.1f} hours")
        self.processes_count_label.setText(f"Processes: {stats.process_count}")
    
    def populate_app_table(self, apps):
        """Uygulama tablosunu doldur"""
        self.app_table.setRowCount(len(apps))
        
        for row, app in enumerate(apps):
            self.app_table.setItem(row, 0, QTableWidgetItem(app.name))
            self.app_table.setItem(row, 1, QTableWidgetItem(app.status))
            self.app_table.setItem(row, 2, QTableWidgetItem(str(app.pid)))
            self.app_table.setItem(row, 3, QTableWidgetItem(f"{app.memory_mb:.1f} MB"))
            self.app_table.setItem(row, 4, QTableWidgetItem(f"{app.cpu_percent:.1f}%"))
            self.app_table.setItem(row, 5, QTableWidgetItem(str(app.thread_count)))
    
    def populate_process_table(self, processes):
        """İşlem tablosunu doldur"""
        self.process_table.setRowCount(len(processes))
        
        for row, proc in enumerate(processes):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(proc.pid)))
            self.process_table.setItem(row, 1, QTableWidgetItem(proc.name))
            self.process_table.setItem(row, 2, QTableWidgetItem(proc.status))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{proc.cpu_percent:.1f}%"))
            self.process_table.setItem(row, 4, QTableWidgetItem(f"{proc.memory_mb:.1f} MB"))
            self.process_table.setItem(row, 5, QTableWidgetItem(str(proc.thread_count)))
            self.process_table.setItem(row, 6, QTableWidgetItem(proc.username))
            self.process_table.setItem(row, 7, QTableWidgetItem(proc.cmdline[:50] + "..." if len(proc.cmdline) > 50 else proc.cmdline))
    
    def populate_thread_table(self, threads):
        """Thread tablosunu doldur"""
        self.thread_table.setRowCount(len(threads))
        
        for row, thread in enumerate(threads):
            self.thread_table.setItem(row, 0, QTableWidgetItem(str(thread.tid)))
            self.thread_table.setItem(row, 1, QTableWidgetItem(thread.process_name))
            self.thread_table.setItem(row, 2, QTableWidgetItem(str(thread.pid)))
            self.thread_table.setItem(row, 3, QTableWidgetItem(thread.status))
            self.thread_table.setItem(row, 4, QTableWidgetItem(f"{thread.cpu_percent:.1f}%"))
            self.thread_table.setItem(row, 5, QTableWidgetItem(str(thread.priority)))
            self.thread_table.setItem(row, 6, QTableWidgetItem(thread.state))
    
    # Event handlers
    def on_tab_changed(self, index):
        """Sekme değişti"""
        tab_names = ["Applications", "Processes", "Threads", "Resources"]
        self.status_label.setText(f"Viewing {tab_names[index]}")
        
        # Hemen güncelle
        self.update_all_data()
    
    def on_selection_changed(self):
        """Seçim değişti"""
        current_table = self.get_current_table()
        if current_table:
            selected_count = len(current_table.selectedItems()) // current_table.columnCount()
            self.selected_count_label.setText(f"{selected_count} selected")
            
            # Butonları etkinleştir/devre dışı bırak
            has_selection = selected_count > 0
            self.end_task_btn.setEnabled(has_selection)
            self.force_quit_btn.setEnabled(has_selection)
            self.suspend_btn.setEnabled(has_selection)
    
    def get_current_table(self):
        """Aktif tabloyu al"""
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:
            return self.app_table
        elif current_tab == 1:
            return self.process_table
        elif current_tab == 2:
            return self.thread_table
        
        return None
    
    # Filter methods
    def filter_applications(self):
        """Uygulamaları filtrele"""
        search_text = self.app_search.text().lower()
        status_filter = self.app_status_filter.currentText()
        
        for row in range(self.app_table.rowCount()):
            app_name = self.app_table.item(row, 0).text().lower()
            app_status = self.app_table.item(row, 1).text()
            
            name_match = search_text in app_name
            status_match = status_filter == "All" or status_filter == app_status
            
            self.app_table.setRowHidden(row, not (name_match and status_match))
    
    def filter_processes(self):
        """İşlemleri filtrele"""
        search_text = self.process_search.text().lower()
        show_system = self.show_system_cb.isChecked()
        
        for row in range(self.process_table.rowCount()):
            if self.process_table.item(row, 1):
                process_name = self.process_table.item(row, 1).text().lower()
                name_match = search_text in process_name
                
                # Sistem işlemi kontrolü (basit)
                is_system = process_name.startswith(('kernel', 'system', 'com.apple', 'launchd'))
                system_match = show_system or not is_system
                
                self.process_table.setRowHidden(row, not (name_match and system_match))
    
    def filter_threads(self):
        """Thread'leri filtrele"""
        search_text = self.thread_search.text().lower()
        process_filter = self.thread_process_filter.currentText()
        
        for row in range(self.thread_table.rowCount()):
            if self.thread_table.item(row, 1):
                process_name = self.thread_table.item(row, 1).text()
                
                name_match = search_text in process_name.lower()
                process_match = process_filter == "All Processes" or process_filter == process_name
                
                self.thread_table.setRowHidden(row, not (name_match and process_match))
    
    def sort_processes(self):
        """İşlemleri sırala"""
        sort_by = self.process_sort.currentText()
        
        if sort_by == "CPU":
            self.process_table.sortItems(3, Qt.SortOrder.DescendingOrder)
        elif sort_by == "Memory":
            self.process_table.sortItems(4, Qt.SortOrder.DescendingOrder)
        elif sort_by == "PID":
            self.process_table.sortItems(0, Qt.SortOrder.AscendingOrder)
        elif sort_by == "Name":
            self.process_table.sortItems(1, Qt.SortOrder.AscendingOrder)
    
    # Context menus
    def show_process_context_menu(self, position):
        """İşlem bağlam menüsü"""
        if self.process_table.itemAt(position) is None:
            return
        
        menu = QMenu()
        
        end_action = menu.addAction("End Process")
        end_action.triggered.connect(self.end_selected_task)
        
        force_action = menu.addAction("Force Quit")
        force_action.triggered.connect(self.force_quit_selected)
        
        menu.addSeparator()
        
        suspend_action = menu.addAction("Suspend")
        suspend_action.triggered.connect(self.suspend_selected)
        
        resume_action = menu.addAction("Resume")
        resume_action.triggered.connect(self.resume_selected)
        
        menu.addSeparator()
        
        properties_action = menu.addAction("Properties")
        properties_action.triggered.connect(self.show_process_properties)
        
        menu.exec(self.process_table.mapToGlobal(position))
    
    def show_thread_context_menu(self, position):
        """Thread bağlam menüsü"""
        if self.thread_table.itemAt(position) is None:
            return
        
        menu = QMenu()
        
        freeze_action = menu.addAction("Freeze Thread")
        freeze_action.triggered.connect(self.freeze_selected_thread)
        
        kill_action = menu.addAction("Kill Thread")
        kill_action.triggered.connect(self.kill_selected_thread)
        
        menu.addSeparator()
        
        properties_action = menu.addAction("Thread Properties")
        properties_action.triggered.connect(self.show_thread_properties)
        
        menu.exec(self.thread_table.mapToGlobal(position))
    
    # Action methods
    def end_selected_task(self):
        """Seçili görevi sonlandır"""
        current_table = self.get_current_table()
        if not current_table:
            return
        
        selected_rows = set()
        for item in current_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        # Onay al
        reply = QMessageBox.question(
            self, "End Task",
            f"Are you sure you want to end {len(selected_rows)} task(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in selected_rows:
                if self.tab_widget.currentIndex() == 0:  # Applications
                    pid_item = current_table.item(row, 2)
                elif self.tab_widget.currentIndex() == 1:  # Processes
                    pid_item = current_table.item(row, 0)
                else:
                    continue
                
                if pid_item:
                    pid = int(pid_item.text())
                    self.process_manager.terminate_process(pid)
            
            self.status_label.setText(f"Ended {len(selected_rows)} task(s)")
    
    def force_quit_selected(self):
        """Seçili görevi zorla sonlandır"""
        # end_selected_task ile benzer ama force=True
        self.end_selected_task()  # Şimdilik aynı
    
    def suspend_selected(self):
        """Seçili görevi askıya al"""
        self.status_label.setText("Suspend functionality not implemented yet")
    
    def resume_selected(self):
        """Seçili görevi devam ettir"""
        self.status_label.setText("Resume functionality not implemented yet")
    
    def freeze_selected_thread(self):
        """Seçili thread'i dondur"""
        selected_rows = set()
        for item in self.thread_table.selectedItems():
            selected_rows.add(item.row())
        
        for row in selected_rows:
            tid_item = self.thread_table.item(row, 0)
            if tid_item:
                tid = int(tid_item.text())
                self.thread_manager.freeze_thread(tid)
        
        self.status_label.setText(f"Froze {len(selected_rows)} thread(s)")
    
    def kill_selected_thread(self):
        """Seçili thread'i öldür"""
        selected_rows = set()
        for item in self.thread_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        reply = QMessageBox.question(
            self, "Kill Thread",
            f"Are you sure you want to kill {len(selected_rows)} thread(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in selected_rows:
                tid_item = self.thread_table.item(row, 0)
                if tid_item:
                    tid = int(tid_item.text())
                    self.thread_manager.kill_thread(tid)
            
            self.status_label.setText(f"Killed {len(selected_rows)} thread(s)")
    
    def show_process_properties(self):
        """İşlem özelliklerini göster"""
        self.status_label.setText("Process properties dialog not implemented yet")
    
    def show_thread_properties(self):
        """Thread özelliklerini göster"""
        self.status_label.setText("Thread properties dialog not implemented yet")
    
    # Control methods
    def toggle_auto_refresh(self, enabled):
        """Otomatik yenilemeyi aç/kapat"""
        if enabled:
            self.update_timer.start(self.update_interval)
            self.status_label.setText("Auto refresh enabled")
        else:
            self.update_timer.stop()
            self.status_label.setText("Auto refresh disabled")
    
    def manual_refresh(self):
        """Manuel yenile"""
        self.update_all_data()
        self.status_label.setText("Manually refreshed")
    
    def change_update_interval(self, interval_text):
        """Güncelleme aralığını değiştir"""
        interval_map = {"1s": 1000, "2s": 2000, "5s": 5000, "10s": 10000}
        self.update_interval = interval_map.get(interval_text, 2000)
        
        if self.update_timer.isActive():
            self.update_timer.setInterval(self.update_interval)
        
        self.status_label.setText(f"Update interval: {interval_text}")
    
    def toggle_theme(self):
        """Temayı değiştir"""
        self.status_label.setText("Theme toggle not implemented yet")
    
    def show_settings(self):
        """Ayarları göster"""
        self.status_label.setText("Settings dialog not implemented yet")
    
    def show_help(self):
        """Yardım göster"""
        help_text = """
        <h2>Cloud Task Manager v2.0.0</h2>
        
        <h3>🚀 Applications</h3>
        <p>PyCloud OS uygulamalarını görüntüleyin ve yönetin.</p>
        
        <h3>⚙️ Processes</h3>
        <p>Sistem işlemlerini izleyin ve kontrol edin.</p>
        
        <h3>🧵 Threads</h3>
        <p>Thread'leri TID bazlı görüntüleyin ve yönetin.</p>
        
        <h3>📊 Resources</h3>
        <p>Sistem kaynaklarını gerçek zamanlı izleyin.</p>
        
        <h3>Klavye Kısayolları</h3>
        <ul>
        <li><b>Ctrl+R:</b> Yenile</li>
        <li><b>Delete:</b> Seçili görevi sonlandır</li>
        <li><b>Ctrl+F:</b> Arama</li>
        </ul>
        """
        
        QMessageBox.about(self, "Help", help_text)
    
    def closeEvent(self, event):
        """Pencere kapatılıyor"""
        self.stop_monitoring()
        event.accept()
        self.logger.info("Cloud Task Manager closed") 