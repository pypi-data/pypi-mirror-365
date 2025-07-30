"""
PyCloud OS Process Manager
Aktif çalışan uygulama ve sistem süreçlerini yönetir
"""

import os
import sys
import subprocess
import threading
import time
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class ProcessStatus(Enum):
    """Süreç durumları"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CRASHED = "crashed"
    ZOMBIE = "zombie"

class ProcessType(Enum):
    """Süreç türleri"""
    SYSTEM = "system"
    APPLICATION = "application"
    SERVICE = "service"
    BACKGROUND = "background"

@dataclass
class ProcessInfo:
    """Süreç bilgi sınıfı"""
    pid: int
    name: str
    app_id: str
    process_type: ProcessType
    status: ProcessStatus
    command: str
    working_dir: str
    started_at: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    user: str = "system"
    parent_pid: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['process_type'] = self.process_type.value
        data['status'] = self.status.value
        return data

class ProcessManager:
    """Süreç yöneticisi"""
    
    def __init__(self):
        self.logger = logging.getLogger("ProcessManager")
        self.processes: Dict[int, ProcessInfo] = {}  # PID -> ProcessInfo
        self.app_processes: Dict[str, List[int]] = {}  # app_id -> [PID list]
        self.running = False
        self.monitor_thread = None
        
        # Kaynak sınırları
        self.max_cpu_percent = 80.0
        self.max_memory_mb = 1024.0
        self.resource_warnings: Dict[int, int] = {}  # PID -> warning count
        
        # Callbacks
        self.process_callbacks: Dict[str, List[Callable]] = {
            "started": [],
            "stopped": [],
            "crashed": [],
            "resource_warning": []
        }
        
        self.start_monitoring()
    
    def start_monitoring(self):
        """Süreç izlemeyi başlat"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Process monitoring started")
    
    def stop_monitoring(self):
        """Süreç izlemeyi durdur"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Process monitoring stopped")
    
    def _monitor_loop(self):
        """Süreç izleme döngüsü"""
        while self.running:
            try:
                self._update_process_stats()
                self._check_resource_limits()
                self._cleanup_dead_processes()
                time.sleep(2.0)  # Her 2 saniyede güncelle
            except Exception as e:
                self.logger.error(f"Process monitor error: {e}")
                time.sleep(5.0)
    
    def _update_process_stats(self):
        """Süreç istatistiklerini güncelle"""
        for pid, process_info in list(self.processes.items()):
            try:
                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)
                    
                    # CPU ve bellek kullanımını güncelle
                    process_info.cpu_percent = proc.cpu_percent()
                    process_info.memory_mb = proc.memory_info().rss / 1024 / 1024
                    
                    # Durum kontrolü
                    if proc.status() == psutil.STATUS_ZOMBIE:
                        process_info.status = ProcessStatus.ZOMBIE
                    elif proc.status() == psutil.STATUS_STOPPED:
                        process_info.status = ProcessStatus.PAUSED
                    else:
                        process_info.status = ProcessStatus.RUNNING
                
                else:
                    # Süreç artık yok
                    process_info.status = ProcessStatus.STOPPED
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_info.status = ProcessStatus.STOPPED
            except Exception as e:
                self.logger.warning(f"Failed to update stats for PID {pid}: {e}")
    
    def _check_resource_limits(self):
        """Kaynak sınırlarını kontrol et"""
        for pid, process_info in self.processes.items():
            if process_info.status != ProcessStatus.RUNNING:
                continue
            
            warning_count = self.resource_warnings.get(pid, 0)
            
            # CPU kontrolü
            if process_info.cpu_percent > self.max_cpu_percent:
                warning_count += 1
                self.logger.warning(f"High CPU usage: {process_info.name} (PID {pid}) - {process_info.cpu_percent:.1f}%")
                
                self._trigger_callback("resource_warning", {
                    "pid": pid,
                    "type": "cpu",
                    "value": process_info.cpu_percent,
                    "limit": self.max_cpu_percent
                })
            
            # Bellek kontrolü
            if process_info.memory_mb > self.max_memory_mb:
                warning_count += 1
                self.logger.warning(f"High memory usage: {process_info.name} (PID {pid}) - {process_info.memory_mb:.1f}MB")
                
                self._trigger_callback("resource_warning", {
                    "pid": pid,
                    "type": "memory",
                    "value": process_info.memory_mb,
                    "limit": self.max_memory_mb
                })
            
            # Çok fazla uyarı varsa süreç öldürülmeli
            if warning_count > 5:
                self.logger.error(f"Process {process_info.name} (PID {pid}) exceeded resource limits, terminating")
                self.kill_process(pid, force=True)
            
            self.resource_warnings[pid] = warning_count
    
    def _cleanup_dead_processes(self):
        """Ölü süreçleri temizle"""
        dead_pids = []
        
        for pid, process_info in self.processes.items():
            if process_info.status in [ProcessStatus.STOPPED, ProcessStatus.CRASHED, ProcessStatus.ZOMBIE]:
                dead_pids.append(pid)
        
        for pid in dead_pids:
            self._remove_process(pid)
    
    def start_process(self, command: str, app_id: str, name: str = None,
                     working_dir: str = None, process_type: ProcessType = ProcessType.APPLICATION,
                     user: str = "system") -> Optional[int]:
        """Yeni süreç başlat"""
        try:
            if not name:
                name = app_id
            
            if not working_dir:
                working_dir = os.getcwd()
            
            # Süreç başlat
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            pid = process.pid
            
            # ProcessInfo oluştur
            process_info = ProcessInfo(
                pid=pid,
                name=name,
                app_id=app_id,
                process_type=process_type,
                status=ProcessStatus.STARTING,
                command=command,
                working_dir=working_dir,
                started_at=datetime.now().isoformat(),
                user=user
            )
            
            # Kaydet
            self.processes[pid] = process_info
            
            # App ID ile ilişkilendir
            if app_id not in self.app_processes:
                self.app_processes[app_id] = []
            self.app_processes[app_id].append(pid)
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.APP_LAUNCH, {
                "app_id": app_id,
                "pid": pid,
                "name": name
            }, source="ProcessManager")
            
            self._trigger_callback("started", process_info.to_dict())
            
            self.logger.info(f"Process started: {name} (PID {pid})")
            return pid
            
        except Exception as e:
            self.logger.error(f"Failed to start process {command}: {e}")
            return None
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Süreç öldür"""
        try:
            if pid not in self.processes:
                return False
            
            process_info = self.processes[pid]
            
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                
                if force:
                    proc.kill()  # SIGKILL
                else:
                    proc.terminate()  # SIGTERM
                
                # Biraz bekle
                try:
                    proc.wait(timeout=3.0)
                except psutil.TimeoutExpired:
                    if not force:
                        # Zorla öldür
                        proc.kill()
                        proc.wait(timeout=1.0)
            
            # Durumu güncelle
            process_info.status = ProcessStatus.STOPPED
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.APP_CLOSE, {
                "app_id": process_info.app_id,
                "pid": pid,
                "name": process_info.name
            }, source="ProcessManager")
            
            self._trigger_callback("stopped", process_info.to_dict())
            
            self.logger.info(f"Process killed: {process_info.name} (PID {pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to kill process {pid}: {e}")
            return False
    
    def pause_process(self, pid: int) -> bool:
        """Süreç duraklat"""
        try:
            if pid not in self.processes:
                return False
            
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.suspend()
                
                self.processes[pid].status = ProcessStatus.PAUSED
                self.logger.info(f"Process paused: PID {pid}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to pause process {pid}: {e}")
            return False
    
    def resume_process(self, pid: int) -> bool:
        """Süreç devam ettir"""
        try:
            if pid not in self.processes:
                return False
            
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                proc.resume()
                
                self.processes[pid].status = ProcessStatus.RUNNING
                self.logger.info(f"Process resumed: PID {pid}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to resume process {pid}: {e}")
            return False
    
    def get_process_info(self, pid: int) -> Optional[ProcessInfo]:
        """Süreç bilgisi al"""
        return self.processes.get(pid)
    
    def get_app_processes(self, app_id: str) -> List[ProcessInfo]:
        """Uygulama süreçlerini al"""
        pids = self.app_processes.get(app_id, [])
        return [self.processes[pid] for pid in pids if pid in self.processes]
    
    def get_all_processes(self) -> List[ProcessInfo]:
        """Tüm süreçleri al"""
        return list(self.processes.values())
    
    def get_running_processes(self) -> List[ProcessInfo]:
        """Çalışan süreçleri al"""
        return [p for p in self.processes.values() if p.status == ProcessStatus.RUNNING]
    
    def is_app_running(self, app_id: str) -> bool:
        """Uygulama çalışıyor mu?"""
        app_processes = self.get_app_processes(app_id)
        return any(p.status == ProcessStatus.RUNNING for p in app_processes)
    
    def get_system_stats(self) -> Dict:
        """Sistem istatistikleri"""
        try:
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Bellek kullanımı
            memory = psutil.virtual_memory()
            
            # Disk kullanımı
            disk = psutil.disk_usage('/')
            
            # Süreç sayıları
            total_processes = len(self.processes)
            running_processes = len(self.get_running_processes())
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total_mb": memory.total / 1024 / 1024,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_percent": memory.percent,
                "disk_total_gb": disk.total / 1024 / 1024 / 1024,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "disk_percent": (disk.used / disk.total) * 100,
                "total_processes": total_processes,
                "running_processes": running_processes,
                "system_load": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            return {}
    
    def _remove_process(self, pid: int):
        """Süreç kaydını kaldır"""
        if pid in self.processes:
            process_info = self.processes[pid]
            
            # App processes listesinden kaldır
            app_id = process_info.app_id
            if app_id in self.app_processes:
                if pid in self.app_processes[app_id]:
                    self.app_processes[app_id].remove(pid)
                
                # Liste boşsa app kaydını sil
                if not self.app_processes[app_id]:
                    del self.app_processes[app_id]
            
            # Process kaydını sil
            del self.processes[pid]
            
            # Resource warnings'i temizle
            if pid in self.resource_warnings:
                del self.resource_warnings[pid]
    
    def add_callback(self, event_type: str, callback: Callable):
        """Callback ekle"""
        if event_type in self.process_callbacks:
            self.process_callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: str, callback: Callable):
        """Callback kaldır"""
        if event_type in self.process_callbacks:
            if callback in self.process_callbacks[event_type]:
                self.process_callbacks[event_type].remove(callback)
    
    def _trigger_callback(self, event_type: str, data: Dict):
        """Callback tetikle"""
        for callback in self.process_callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Callback error for {event_type}: {e}")
    
    def set_resource_limits(self, max_cpu_percent: float = None, max_memory_mb: float = None):
        """Kaynak sınırlarını ayarla"""
        if max_cpu_percent is not None:
            self.max_cpu_percent = max_cpu_percent
        
        if max_memory_mb is not None:
            self.max_memory_mb = max_memory_mb
        
        self.logger.info(f"Resource limits updated: CPU {self.max_cpu_percent}%, Memory {self.max_memory_mb}MB")
    
    def get_process_tree(self, pid: int) -> Dict:
        """Süreç ağacını al"""
        try:
            if not psutil.pid_exists(pid):
                return {}
            
            proc = psutil.Process(pid)
            
            tree = {
                "pid": pid,
                "name": proc.name(),
                "status": proc.status(),
                "cpu_percent": proc.cpu_percent(),
                "memory_mb": proc.memory_info().rss / 1024 / 1024,
                "children": []
            }
            
            # Alt süreçleri ekle
            for child in proc.children(recursive=False):
                try:
                    child_tree = self.get_process_tree(child.pid)
                    if child_tree:
                        tree["children"].append(child_tree)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return tree
            
        except Exception as e:
            self.logger.error(f"Failed to get process tree for {pid}: {e}")
            return {}
    
    def cleanup_zombie_processes(self):
        """Zombi süreçleri temizle"""
        zombie_count = 0
        
        for pid, process_info in list(self.processes.items()):
            if process_info.status == ProcessStatus.ZOMBIE:
                try:
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        proc.kill()
                    
                    self._remove_process(pid)
                    zombie_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup zombie process {pid}: {e}")
        
        if zombie_count > 0:
            self.logger.info(f"Cleaned up {zombie_count} zombie processes")
    
    def shutdown(self):
        """Modül kapatma"""
        self.logger.info("Shutting down process manager...")
        
        # Monitoring'i durdur
        self.stop_monitoring()
        
        # Tüm uygulama süreçlerini kapat
        app_processes = [p for p in self.processes.values() 
                        if p.process_type == ProcessType.APPLICATION]
        
        for process_info in app_processes:
            if process_info.status == ProcessStatus.RUNNING:
                self.kill_process(process_info.pid)
        
        # Zombi süreçleri temizle
        self.cleanup_zombie_processes()
        
        self.logger.info("Process manager shutdown completed")

# Global process manager instance
_process_manager = None

def init_process(kernel=None) -> ProcessManager:
    """Process manager'ı başlat"""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
        _process_manager.start_monitoring()
    return _process_manager

def get_process_manager() -> Optional[ProcessManager]:
    """Process manager'ı al"""
    return _process_manager 