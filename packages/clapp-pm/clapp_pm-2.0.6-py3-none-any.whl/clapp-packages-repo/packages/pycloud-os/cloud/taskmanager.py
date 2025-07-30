"""
Cloud Task Manager - PyCloud OS Görev Yöneticisi
Sistem üzerindeki tüm çalışan uygulama, işlem ve thread'leri takip ve yönetim için kullanılan görev yöneticisi
"""

import sys
import os
import json
import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

# PyQt6 import with fallback
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 bulunamadı - Task Manager text modunda çalışacak")

# psutil import with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil bulunamadı - Bazı özellikler kısıtlı olacak")

@dataclass
class ProcessInfo:
    """İşlem bilgisi"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_info: int  # bytes
    create_time: float
    num_threads: int
    cmdline: str
    user: str

@dataclass
class SystemStats:
    """Sistem istatistikleri"""
    cpu_percent: float
    memory_total: int
    memory_available: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    network_sent: int
    network_recv: int
    boot_time: float
    uptime: float

class ProcessMonitor:
    """İşlem izleyici"""
    
    def __init__(self):
        self.processes: Dict[int, ProcessInfo] = {}
        self.system_stats = SystemStats(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 2.0  # saniye
        
    def start_monitoring(self):
        """İzlemeyi başlat"""
        if not PSUTIL_AVAILABLE:
            return False
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        return True
    
    def stop_monitoring(self):
        """İzlemeyi durdur"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """İzleme döngüsü"""
        while self.monitoring:
            try:
                self._update_processes()
                self._update_system_stats()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Monitor hatası: {e}")
                time.sleep(1.0)
    
    def _update_processes(self):
        """İşlemleri güncelle"""
        if not PSUTIL_AVAILABLE:
            return
        
        new_processes = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 
                                        'memory_percent', 'memory_info', 'create_time',
                                        'num_threads', 'cmdline', 'username']):
            try:
                info = proc.info
                
                # Komut satırını düzenle
                cmdline = ' '.join(info['cmdline']) if info['cmdline'] else info['name']
                if len(cmdline) > 100:
                    cmdline = cmdline[:100] + "..."
                
                process_info = ProcessInfo(
                    pid=info['pid'],
                    name=info['name'] or 'Unknown',
                    status=info['status'] or 'unknown',
                    cpu_percent=info['cpu_percent'] or 0.0,
                    memory_percent=info['memory_percent'] or 0.0,
                    memory_info=info['memory_info'].rss if info['memory_info'] else 0,
                    create_time=info['create_time'] or 0,
                    num_threads=info['num_threads'] or 0,
                    cmdline=cmdline,
                    user=info['username'] or 'unknown'
                )
                
                new_processes[info['pid']] = process_info
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
        
        self.processes = new_processes
    
    def _update_system_stats(self):
        """Sistem istatistiklerini güncelle"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Bellek
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Ağ
            network = psutil.net_io_counters()
            
            # Sistem bilgileri
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            self.system_stats = SystemStats(
                cpu_percent=cpu_percent,
                memory_total=memory.total,
                memory_available=memory.available,
                memory_percent=memory.percent,
                disk_total=disk.total,
                disk_used=disk.used,
                disk_percent=disk.percent,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                boot_time=boot_time,
                uptime=uptime
            )
            
        except Exception as e:
            print(f"Sistem stats hatası: {e}")
    
    def get_processes(self, sort_by: str = 'cpu', reverse: bool = True) -> List[ProcessInfo]:
        """İşlemleri al"""
        processes = list(self.processes.values())
        
        if sort_by == 'cpu':
            processes.sort(key=lambda p: p.cpu_percent, reverse=reverse)
        elif sort_by == 'memory':
            processes.sort(key=lambda p: p.memory_percent, reverse=reverse)
        elif sort_by == 'name':
            processes.sort(key=lambda p: p.name.lower(), reverse=reverse)
        elif sort_by == 'pid':
            processes.sort(key=lambda p: p.pid, reverse=reverse)
        
        return processes
    
    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """PID'ye göre işlem al"""
        return self.processes.get(pid)
    
    def kill_process(self, pid: int, force: bool = False) -> Tuple[bool, str]:
        """İşlemi sonlandır"""
        if not PSUTIL_AVAILABLE:
            return False, "psutil mevcut değil"
        
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return True, "İşlem sonlandırıldı"
        except psutil.NoSuchProcess:
            return False, "İşlem bulunamadı"
        except psutil.AccessDenied:
            return False, "Erişim reddedildi"
        except Exception as e:
            return False, f"Hata: {e}"
    
    def get_system_stats(self) -> SystemStats:
        """Sistem istatistiklerini al"""
        return self.system_stats

if PYQT_AVAILABLE:
    class TaskManagerWindow(QMainWindow):
        """Görev yöneticisi ana penceresi"""
        
        def __init__(self, kernel=None):
            super().__init__()
            self.kernel = kernel
            self.monitor = ProcessMonitor()
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_display)
            
            self.init_ui()
            self.apply_theme()
            self.start_monitoring()
        
        def init_ui(self):
            """UI'yı başlat"""
            self.setWindowTitle("PyCloud Task Manager")
            self.setGeometry(100, 100, 1000, 700)
            
            # Ana widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout()
            
            # Üst panel - Sistem özeti
            self.create_system_overview(layout)
            
            # Tab widget
            self.tab_widget = QTabWidget()
            
            # İşlemler sekmesi
            self.create_processes_tab()
            
            # Kaynak kullanımı sekmesi
            self.create_resources_tab()
            
            # Uygulamalar sekmesi
            self.create_applications_tab()
            
            layout.addWidget(self.tab_widget)
            
            # Alt panel - Eylem butonları
            self.create_action_panel(layout)
            
            central_widget.setLayout(layout)
            
            # Menü çubuğu
            self.create_menu_bar()
        
        def create_menu_bar(self):
            """Menü çubuğu oluştur"""
            menubar = self.menuBar()
            
            # Dosya menüsü
            file_menu = menubar.addMenu('Dosya')
            
            refresh_action = QAction('Yenile', self)
            refresh_action.setShortcut('F5')
            refresh_action.triggered.connect(self.manual_refresh)
            file_menu.addAction(refresh_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction('Çıkış', self)
            exit_action.setShortcut('Ctrl+Q')
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Görünüm menüsü
            view_menu = menubar.addMenu('Görünüm')
            
            update_speed_menu = view_menu.addMenu('Güncelleme Hızı')
            
            speed_group = QActionGroup(self)
            
            for label, interval in [("Hızlı (1s)", 1.0), ("Normal (2s)", 2.0), 
                                  ("Yavaş (5s)", 5.0), ("Çok Yavaş (10s)", 10.0)]:
                action = QAction(label, self)
                action.setCheckable(True)
                action.setData(interval)
                action.triggered.connect(lambda checked, i=interval: self.set_update_interval(i))
                speed_group.addAction(action)
                update_speed_menu.addAction(action)
                
                if interval == 2.0:  # Varsayılan
                    action.setChecked(True)
        
        def create_system_overview(self, parent_layout):
            """Sistem özeti oluştur"""
            overview_frame = QFrame()
            overview_frame.setFrameStyle(QFrame.Shape.Box)
            overview_frame.setMaximumHeight(100)
            
            layout = QHBoxLayout()
            
            # CPU kullanımı
            self.cpu_label = QLabel("CPU: 0%")
            self.cpu_progress = QProgressBar()
            self.cpu_progress.setMaximum(100)
            cpu_layout = QVBoxLayout()
            cpu_layout.addWidget(self.cpu_label)
            cpu_layout.addWidget(self.cpu_progress)
            layout.addLayout(cpu_layout)
            
            # Bellek kullanımı
            self.memory_label = QLabel("Bellek: 0%")
            self.memory_progress = QProgressBar()
            self.memory_progress.setMaximum(100)
            memory_layout = QVBoxLayout()
            memory_layout.addWidget(self.memory_label)
            memory_layout.addWidget(self.memory_progress)
            layout.addLayout(memory_layout)
            
            # Disk kullanımı
            self.disk_label = QLabel("Disk: 0%")
            self.disk_progress = QProgressBar()
            self.disk_progress.setMaximum(100)
            disk_layout = QVBoxLayout()
            disk_layout.addWidget(self.disk_label)
            disk_layout.addWidget(self.disk_progress)
            layout.addLayout(disk_layout)
            
            # Sistem bilgileri
            self.uptime_label = QLabel("Çalışma Süresi: --")
            self.process_count_label = QLabel("İşlem Sayısı: 0")
            info_layout = QVBoxLayout()
            info_layout.addWidget(self.uptime_label)
            info_layout.addWidget(self.process_count_label)
            layout.addLayout(info_layout)
            
            overview_frame.setLayout(layout)
            parent_layout.addWidget(overview_frame)
        
        def create_processes_tab(self):
            """İşlemler sekmesi oluştur"""
            processes_widget = QWidget()
            layout = QVBoxLayout()
            
            # Arama ve filtre
            search_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("İşlem ara...")
            self.search_input.textChanged.connect(self.filter_processes)
            search_layout.addWidget(QLabel("Ara:"))
            search_layout.addWidget(self.search_input)
            
            self.sort_combo = QComboBox()
            self.sort_combo.addItems(["CPU Kullanımı", "Bellek Kullanımı", "İşlem Adı", "PID"])
            self.sort_combo.currentTextChanged.connect(self.sort_processes)
            search_layout.addWidget(QLabel("Sırala:"))
            search_layout.addWidget(self.sort_combo)
            
            search_layout.addStretch()
            layout.addLayout(search_layout)
            
            # İşlem tablosu
            self.process_table = QTableWidget()
            self.process_table.setColumnCount(8)
            self.process_table.setHorizontalHeaderLabels([
                "PID", "İşlem Adı", "Durum", "CPU %", "Bellek %", "Bellek", "Thread", "Kullanıcı"
            ])
            
            header = self.process_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            
            self.process_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.process_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.process_table.customContextMenuRequested.connect(self.show_process_context_menu)
            
            layout.addWidget(self.process_table)
            
            processes_widget.setLayout(layout)
            self.tab_widget.addTab(processes_widget, "İşlemler")
        
        def create_resources_tab(self):
            """Kaynak kullanımı sekmesi oluştur"""
            resources_widget = QWidget()
            layout = QVBoxLayout()
            
            # Kaynak grafikleri burada olacak (basit versiyon)
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            info_text.setText("""
Kaynak Kullanımı İzleme

Bu sekmede sistem kaynaklarının detaylı analizi gösterilir:

• CPU çekirdek bazlı kullanım
• Bellek dağılımı (RSS, VMS, Shared)
• Disk I/O istatistikleri
• Ağ trafiği
• Sistem cache kullanımı

Gerçek zamanlı grafikler ve metrikler yakında eklenecek.
            """)
            
            layout.addWidget(info_text)
            
            resources_widget.setLayout(layout)
            self.tab_widget.addTab(resources_widget, "Kaynaklar")
        
        def create_applications_tab(self):
            """Uygulamalar sekmesi oluştur"""
            apps_widget = QWidget()
            layout = QVBoxLayout()
            
            # PyCloud uygulamaları listesi
            self.app_table = QTableWidget()
            self.app_table.setColumnCount(5)
            self.app_table.setHorizontalHeaderLabels([
                "Uygulama", "Durum", "PID", "Bellek", "CPU"
            ])
            
            header = self.app_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            
            layout.addWidget(self.app_table)
            
            apps_widget.setLayout(layout)
            self.tab_widget.addTab(apps_widget, "Uygulamalar")
        
        def create_action_panel(self, parent_layout):
            """Eylem paneli oluştur"""
            action_layout = QHBoxLayout()
            
            self.end_task_btn = QPushButton("Görevi Sonlandır")
            self.end_task_btn.clicked.connect(self.end_selected_task)
            self.end_task_btn.setEnabled(False)
            action_layout.addWidget(self.end_task_btn)
            
            self.force_end_btn = QPushButton("Zorla Sonlandır")
            self.force_end_btn.clicked.connect(self.force_end_selected_task)
            self.force_end_btn.setEnabled(False)
            action_layout.addWidget(self.force_end_btn)
            
            action_layout.addStretch()
            
            self.auto_refresh_cb = QCheckBox("Otomatik Yenile")
            self.auto_refresh_cb.setChecked(True)
            self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
            action_layout.addWidget(self.auto_refresh_cb)
            
            self.refresh_btn = QPushButton("Yenile")
            self.refresh_btn.clicked.connect(self.manual_refresh)
            action_layout.addWidget(self.refresh_btn)
            
            parent_layout.addLayout(action_layout)
        
        def apply_theme(self):
            """Tema uygula"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QTableWidget {
                    background-color: #ffffff;
                    alternate-background-color: #f8f8f8;
                    gridline-color: #e0e0e0;
                    selection-background-color: #0078d4;
                }
                QTableWidget::item {
                    padding: 4px;
                }
                QHeaderView::section {
                    background-color: #e6e6e6;
                    border: 1px solid #cccccc;
                    padding: 6px;
                    font-weight: bold;
                }
                QProgressBar {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                    border-radius: 2px;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 6px 12px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
                QPushButton:disabled {
                    background-color: #f5f5f5;
                    color: #999999;
                }
                QFrame[frameShape="1"] {
                    border: 1px solid #cccccc;
                    background-color: #ffffff;
                }
            """)
        
        def start_monitoring(self):
            """İzlemeyi başlat"""
            if self.monitor.start_monitoring():
                self.update_timer.start(int(self.monitor.update_interval * 1000))
            else:
                QMessageBox.warning(self, "Uyarı", "Sistem izleme başlatılamadı. psutil modülü gerekli.")
        
        def update_display(self):
            """Görüntüyü güncelle"""
            if not self.auto_refresh_cb.isChecked():
                return
            
            self.update_system_overview()
            self.update_process_table()
            self.update_applications_table()
        
        def update_system_overview(self):
            """Sistem özetini güncelle"""
            stats = self.monitor.get_system_stats()
            
            # CPU
            self.cpu_label.setText(f"CPU: {stats.cpu_percent:.1f}%")
            self.cpu_progress.setValue(int(stats.cpu_percent))
            
            # Bellek
            memory_gb = stats.memory_total / (1024**3)
            available_gb = stats.memory_available / (1024**3)
            self.memory_label.setText(f"Bellek: {stats.memory_percent:.1f}% ({available_gb:.1f}/{memory_gb:.1f} GB)")
            self.memory_progress.setValue(int(stats.memory_percent))
            
            # Disk
            disk_gb = stats.disk_total / (1024**3)
            used_gb = stats.disk_used / (1024**3)
            self.disk_label.setText(f"Disk: {stats.disk_percent:.1f}% ({used_gb:.1f}/{disk_gb:.1f} GB)")
            self.disk_progress.setValue(int(stats.disk_percent))
            
            # Sistem bilgileri
            uptime_hours = stats.uptime / 3600
            self.uptime_label.setText(f"Çalışma Süresi: {uptime_hours:.1f} saat")
            self.process_count_label.setText(f"İşlem Sayısı: {len(self.monitor.processes)}")
        
        def update_process_table(self):
            """İşlem tablosunu güncelle"""
            sort_map = {
                "CPU Kullanımı": "cpu",
                "Bellek Kullanımı": "memory", 
                "İşlem Adı": "name",
                "PID": "pid"
            }
            
            sort_by = sort_map.get(self.sort_combo.currentText(), "cpu")
            processes = self.monitor.get_processes(sort_by=sort_by)
            
            # Arama filtresi
            search_text = self.search_input.text().lower()
            if search_text:
                processes = [p for p in processes if search_text in p.name.lower()]
            
            self.process_table.setRowCount(len(processes))
            
            for row, process in enumerate(processes):
                # PID
                self.process_table.setItem(row, 0, QTableWidgetItem(str(process.pid)))
                
                # İşlem adı
                self.process_table.setItem(row, 1, QTableWidgetItem(process.name))
                
                # Durum
                self.process_table.setItem(row, 2, QTableWidgetItem(process.status))
                
                # CPU %
                cpu_item = QTableWidgetItem(f"{process.cpu_percent:.1f}%")
                cpu_item.setData(Qt.ItemDataRole.UserRole, process.cpu_percent)
                self.process_table.setItem(row, 3, cpu_item)
                
                # Bellek %
                mem_item = QTableWidgetItem(f"{process.memory_percent:.1f}%")
                mem_item.setData(Qt.ItemDataRole.UserRole, process.memory_percent)
                self.process_table.setItem(row, 4, mem_item)
                
                # Bellek boyutu
                memory_mb = process.memory_info / (1024**2)
                self.process_table.setItem(row, 5, QTableWidgetItem(f"{memory_mb:.1f} MB"))
                
                # Thread sayısı
                self.process_table.setItem(row, 6, QTableWidgetItem(str(process.num_threads)))
                
                # Kullanıcı
                self.process_table.setItem(row, 7, QTableWidgetItem(process.user))
        
        def update_applications_table(self):
            """Uygulama tablosunu güncelle"""
            # Bu fonksiyon PyCloud uygulamalarını gösterecek
            # Şimdilik basit bir implementasyon
            
            apps_dir = "apps"
            if not os.path.exists(apps_dir):
                return
            
            # Kurulu uygulamaları bul
            apps = []
            for app_dir in os.listdir(apps_dir):
                app_path = os.path.join(apps_dir, app_dir)
                if os.path.isdir(app_path):
                    app_json = os.path.join(app_path, "app.json")
                    if os.path.exists(app_json):
                        try:
                            with open(app_json, 'r', encoding='utf-8') as f:
                                app_info = json.load(f)
                            apps.append(app_info)
                        except:
                            pass
            
            self.app_table.setRowCount(len(apps))
            
            for row, app in enumerate(apps):
                # Uygulama adı
                self.app_table.setItem(row, 0, QTableWidgetItem(app.get('name', 'Bilinmeyen')))
                
                # Durum (basit kontrol)
                self.app_table.setItem(row, 1, QTableWidgetItem("Kurulu"))
                
                # PID, Bellek, CPU (geliştirilecek)
                self.app_table.setItem(row, 2, QTableWidgetItem("-"))
                self.app_table.setItem(row, 3, QTableWidgetItem("-"))
                self.app_table.setItem(row, 4, QTableWidgetItem("-"))
        
        def filter_processes(self):
            """İşlemleri filtrele"""
            self.update_process_table()
        
        def sort_processes(self):
            """İşlemleri sırala"""
            self.update_process_table()
        
        def show_process_context_menu(self, position):
            """İşlem sağ tık menüsü"""
            if self.process_table.itemAt(position) is None:
                return
            
            menu = QMenu()
            
            end_action = menu.addAction("Görevi Sonlandır")
            end_action.triggered.connect(self.end_selected_task)
            
            force_end_action = menu.addAction("Zorla Sonlandır")
            force_end_action.triggered.connect(self.force_end_selected_task)
            
            menu.addSeparator()
            
            properties_action = menu.addAction("Özellikler")
            properties_action.triggered.connect(self.show_process_properties)
            
            menu.exec(self.process_table.mapToGlobal(position))
        
        def end_selected_task(self):
            """Seçili görevi sonlandır"""
            self._terminate_selected_process(force=False)
        
        def force_end_selected_task(self):
            """Seçili görevi zorla sonlandır"""
            self._terminate_selected_process(force=True)
        
        def _terminate_selected_process(self, force: bool = False):
            """Seçili işlemi sonlandır"""
            current_row = self.process_table.currentRow()
            if current_row == -1:
                return
            
            pid_item = self.process_table.item(current_row, 0)
            if not pid_item:
                return
            
            try:
                pid = int(pid_item.text())
                name = self.process_table.item(current_row, 1).text()
                
                action = "zorla sonlandır" if force else "sonlandır"
                reply = QMessageBox.question(
                    self,
                    "Görevi Sonlandır",
                    f"'{name}' (PID: {pid}) işlemini {action}mak istediğinizden emin misiniz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    success, message = self.monitor.kill_process(pid, force)
                    if success:
                        QMessageBox.information(self, "Başarılı", message)
                        self.manual_refresh()
                    else:
                        QMessageBox.warning(self, "Hata", message)
                        
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçersiz PID")
        
        def show_process_properties(self):
            """İşlem özelliklerini göster"""
            current_row = self.process_table.currentRow()
            if current_row == -1:
                return
            
            pid_item = self.process_table.item(current_row, 0)
            if not pid_item:
                return
            
            try:
                pid = int(pid_item.text())
                process_info = self.monitor.get_process_by_pid(pid)
                
                if process_info:
                    dialog = QDialog(self)
                    dialog.setWindowTitle(f"İşlem Özellikleri - {process_info.name}")
                    dialog.setGeometry(200, 200, 500, 400)
                    
                    layout = QVBoxLayout()
                    
                    info_text = QTextEdit()
                    info_text.setReadOnly(True)
                    
                    create_time = datetime.fromtimestamp(process_info.create_time).strftime("%Y-%m-%d %H:%M:%S")
                    
                    info_text.setText(f"""
İşlem Bilgileri:

PID: {process_info.pid}
İsim: {process_info.name}
Durum: {process_info.status}
Kullanıcı: {process_info.user}
Oluşturma Zamanı: {create_time}

Kaynak Kullanımı:
CPU: {process_info.cpu_percent:.1f}%
Bellek: {process_info.memory_percent:.1f}% ({process_info.memory_info / (1024**2):.1f} MB)
Thread Sayısı: {process_info.num_threads}

Komut Satırı:
{process_info.cmdline}
                    """)
                    
                    layout.addWidget(info_text)
                    
                    close_btn = QPushButton("Kapat")
                    close_btn.clicked.connect(dialog.close)
                    layout.addWidget(close_btn)
                    
                    dialog.setLayout(layout)
                    dialog.exec()
                    
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçersiz PID")
        
        def toggle_auto_refresh(self, enabled: bool):
            """Otomatik yenilemeyi aç/kapat"""
            if enabled:
                self.update_timer.start()
            else:
                self.update_timer.stop()
        
        def manual_refresh(self):
            """Manuel yenile"""
            self.update_display()
        
        def set_update_interval(self, interval: float):
            """Güncelleme aralığını ayarla"""
            self.monitor.update_interval = interval
            if self.update_timer.isActive():
                self.update_timer.setInterval(int(interval * 1000))
        
        def closeEvent(self, event):
            """Pencere kapatılıyor"""
            self.monitor.stop_monitoring()
            self.update_timer.stop()
            event.accept()

# Text-mode Task Manager (PyQt6 yoksa)
class TextTaskManager:
    """Text-mode task manager"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.monitor = ProcessMonitor()
    
    def run(self):
        """Task Manager'ı çalıştır"""
        print("PyCloud Task Manager v1.0 (Text Mode)")
        print("Komutlar: ps, top, kill <pid>, sysinfo, quit")
        print()
        
        if self.monitor.start_monitoring():
            print("Sistem izleme başlatıldı")
        else:
            print("Uyarı: psutil bulunamadı, bazı özellikler çalışmayacak")
        
        try:
            while True:
                try:
                    command = input("taskmanager> ").strip()
                    if not command:
                        continue
                    
                    if not self.handle_command(command):
                        break
                        
                except KeyboardInterrupt:
                    print("\nTask Manager kapatılıyor...")
                    break
                except EOFError:
                    break
        finally:
            self.monitor.stop_monitoring()
    
    def handle_command(self, command: str) -> bool:
        """Komut işle"""
        parts = command.split()
        if not parts:
            return True
        
        cmd = parts[0].lower()
        
        if cmd == 'quit' or cmd == 'exit':
            return False
        
        elif cmd == 'ps':
            self.show_processes()
        
        elif cmd == 'top':
            self.show_top_processes()
        
        elif cmd == 'kill':
            if len(parts) > 1:
                try:
                    pid = int(parts[1])
                    self.kill_process(pid)
                except ValueError:
                    print("Geçersiz PID")
            else:
                print("Kullanım: kill <pid>")
        
        elif cmd == 'sysinfo':
            self.show_system_info()
        
        elif cmd == 'help':
            self.show_help()
        
        else:
            print(f"Bilinmeyen komut: {cmd}")
            print("Yardım için 'help' yazın")
        
        return True
    
    def show_processes(self):
        """İşlemleri göster"""
        processes = self.monitor.get_processes(sort_by='cpu')
        
        print(f"\n{'PID':<8} {'NAME':<20} {'STATUS':<12} {'CPU%':<8} {'MEM%':<8} {'THREADS':<8}")
        print("-" * 80)
        
        for proc in processes[:20]:  # İlk 20'yi göster
            print(f"{proc.pid:<8} {proc.name[:20]:<20} {proc.status:<12} "
                  f"{proc.cpu_percent:<8.1f} {proc.memory_percent:<8.1f} {proc.num_threads:<8}")
    
    def show_top_processes(self):
        """En çok kaynak kullanan işlemleri göster"""
        cpu_processes = self.monitor.get_processes(sort_by='cpu')[:5]
        memory_processes = self.monitor.get_processes(sort_by='memory')[:5]
        
        print("\nEn Çok CPU Kullanan İşlemler:")
        print(f"{'PID':<8} {'NAME':<20} {'CPU%':<8}")
        print("-" * 40)
        for proc in cpu_processes:
            print(f"{proc.pid:<8} {proc.name[:20]:<20} {proc.cpu_percent:<8.1f}")
        
        print("\nEn Çok Bellek Kullanan İşlemler:")
        print(f"{'PID':<8} {'NAME':<20} {'MEM%':<8}")
        print("-" * 40)
        for proc in memory_processes:
            print(f"{proc.pid:<8} {proc.name[:20]:<20} {proc.memory_percent:<8.1f}")
    
    def kill_process(self, pid: int):
        """İşlemi sonlandır"""
        process_info = self.monitor.get_process_by_pid(pid)
        if not process_info:
            print(f"PID {pid} bulunamadı")
            return
        
        confirm = input(f"'{process_info.name}' (PID: {pid}) sonlandırılsın mı? (y/n): ")
        if confirm.lower() == 'y':
            success, message = self.monitor.kill_process(pid)
            print(message)
    
    def show_system_info(self):
        """Sistem bilgilerini göster"""
        stats = self.monitor.get_system_stats()
        
        print(f"\nSistem Bilgileri:")
        print(f"CPU Kullanımı: {stats.cpu_percent:.1f}%")
        print(f"Bellek Kullanımı: {stats.memory_percent:.1f}% "
              f"({stats.memory_available / (1024**3):.1f}/{stats.memory_total / (1024**3):.1f} GB)")
        print(f"Disk Kullanımı: {stats.disk_percent:.1f}% "
              f"({stats.disk_used / (1024**3):.1f}/{stats.disk_total / (1024**3):.1f} GB)")
        print(f"Çalışma Süresi: {stats.uptime / 3600:.1f} saat")
        print(f"İşlem Sayısı: {len(self.monitor.processes)}")
    
    def show_help(self):
        """Yardım göster"""
        print("""
Komutlar:
  ps               - Tüm işlemleri listele
  top              - En çok kaynak kullanan işlemleri göster
  kill <pid>       - İşlemi sonlandır
  sysinfo          - Sistem bilgilerini göster
  help             - Bu yardımı göster
  quit             - Çıkış
        """)

# Ana fonksiyonlar
def create_taskmanager_app(kernel=None):
    """Task Manager uygulaması oluştur"""
    if PYQT_AVAILABLE:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        taskmanager = TaskManagerWindow(kernel)
        taskmanager.show()
        return taskmanager
    else:
        return TextTaskManager(kernel)

def run_taskmanager(kernel=None):
    """Task Manager'ı çalıştır"""
    if PYQT_AVAILABLE:
        taskmanager = create_taskmanager_app(kernel)
        return taskmanager
    else:
        taskmanager = TextTaskManager(kernel)
        taskmanager.run()
        return None

if __name__ == "__main__":
    run_taskmanager() 