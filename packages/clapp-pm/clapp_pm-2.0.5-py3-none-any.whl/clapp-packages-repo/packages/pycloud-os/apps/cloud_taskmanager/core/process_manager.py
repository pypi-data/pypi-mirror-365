"""
Cloud Task Manager - İşlem Yöneticisi
Sistem işlemlerini ve PyCloud uygulamalarını yönetme
"""

import os
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class ProcessInfo:
    """İşlem bilgisi"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    thread_count: int
    username: str
    cmdline: str
    create_time: float

@dataclass
class ApplicationInfo:
    """PyCloud uygulama bilgisi"""
    name: str
    app_id: str
    status: str
    pid: Optional[int]
    memory_mb: float
    cpu_percent: float
    thread_count: int
    path: str

class ProcessManager:
    """İşlem ve uygulama yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("ProcessManager")
        self.is_running = False
        self.processes_cache = []
        self.applications_cache = []
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available - using mock data")
    
    def start(self):
        """İzlemeyi başlat"""
        self.is_running = True
        self.logger.info("Process monitoring started")
    
    def stop(self):
        """İzlemeyi durdur"""
        self.is_running = False
        self.logger.info("Process monitoring stopped")
    
    def get_processes(self) -> List[ProcessInfo]:
        """Tüm sistem işlemlerini al"""
        if not PSUTIL_AVAILABLE:
            return self._get_mock_processes()
        
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 
                                           'memory_info', 'memory_percent', 'num_threads',
                                           'username', 'cmdline', 'create_time']):
                try:
                    info = proc.info
                    
                    # Memory MB'a çevir
                    memory_mb = 0.0
                    if info['memory_info']:
                        memory_mb = info['memory_info'].rss / (1024 * 1024)
                    
                    # Cmdline string'e çevir
                    cmdline = ""
                    if info['cmdline']:
                        cmdline = " ".join(info['cmdline'])
                    
                    process_info = ProcessInfo(
                        pid=info['pid'],
                        name=info['name'] or "Unknown",
                        status=info['status'] or "unknown",
                        cpu_percent=info['cpu_percent'] or 0.0,
                        memory_mb=memory_mb,
                        memory_percent=info['memory_percent'] or 0.0,
                        thread_count=info['num_threads'] or 0,
                        username=info['username'] or "unknown",
                        cmdline=cmdline,
                        create_time=info['create_time'] or 0.0
                    )
                    
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            self.processes_cache = processes
            return processes
            
        except Exception as e:
            self.logger.error(f"Failed to get processes: {e}")
            return self._get_mock_processes()
    
    def get_applications(self) -> List[ApplicationInfo]:
        """PyCloud uygulamalarını al"""
        try:
            applications = []
            
            # Apps klasörünü tara
            apps_dir = Path("../../apps")  # Task Manager'dan apps klasörüne
            if not apps_dir.exists():
                apps_dir = Path("../../../apps")  # Alternatif yol
            
            if not apps_dir.exists():
                self.logger.warning("Apps directory not found")
                return self._get_mock_applications()
            
            for app_dir in apps_dir.iterdir():
                if not app_dir.is_dir():
                    continue
                
                app_json_path = app_dir / "app.json"
                if not app_json_path.exists():
                    continue
                
                try:
                    with open(app_json_path, 'r', encoding='utf-8') as f:
                        app_data = json.load(f)
                    
                    # Uygulamanın çalışıp çalışmadığını kontrol et
                    app_pid = self._find_app_process(app_data.get('name', ''))
                    
                    if app_pid:
                        # Çalışan uygulama - psutil'den bilgi al
                        try:
                            proc = psutil.Process(app_pid)
                            memory_mb = proc.memory_info().rss / (1024 * 1024)
                            cpu_percent = proc.cpu_percent()
                            thread_count = proc.num_threads()
                            status = "Running"
                        except:
                            memory_mb = 0.0
                            cpu_percent = 0.0
                            thread_count = 0
                            status = "Unknown"
                    else:
                        # Çalışmayan uygulama
                        memory_mb = 0.0
                        cpu_percent = 0.0
                        thread_count = 0
                        status = "Stopped"
                    
                    app_info = ApplicationInfo(
                        name=app_data.get('name', 'Unknown App'),
                        app_id=app_data.get('id', ''),
                        status=status,
                        pid=app_pid,
                        memory_mb=memory_mb,
                        cpu_percent=cpu_percent,
                        thread_count=thread_count,
                        path=str(app_dir)
                    )
                    
                    applications.append(app_info)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse app {app_dir}: {e}")
                    continue
            
            self.applications_cache = applications
            return applications
            
        except Exception as e:
            self.logger.error(f"Failed to get applications: {e}")
            return self._get_mock_applications()
    
    def _find_app_process(self, app_name: str) -> Optional[int]:
        """Uygulama adına göre PID bul"""
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # İsim kontrolü
                    if app_name.lower() in proc.info['name'].lower():
                        return proc.info['pid']
                    
                    # Cmdline kontrolü
                    if proc.info['cmdline']:
                        cmdline = " ".join(proc.info['cmdline'])
                        if app_name.lower() in cmdline.lower():
                            return proc.info['pid']
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return None
            
        except Exception:
            return None
    
    def terminate_process(self, pid: int) -> bool:
        """İşlemi sonlandır"""
        if not PSUTIL_AVAILABLE:
            self.logger.warning("Cannot terminate process - psutil not available")
            return False
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            
            # 3 saniye bekle
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                # Zorla öldür
                proc.kill()
                proc.wait()
            
            self.logger.info(f"Process {pid} terminated")
            return True
            
        except psutil.NoSuchProcess:
            self.logger.warning(f"Process {pid} not found")
            return False
        except psutil.AccessDenied:
            self.logger.error(f"Access denied to terminate process {pid}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to terminate process {pid}: {e}")
            return False
    
    def suspend_process(self, pid: int) -> bool:
        """İşlemi askıya al"""
        if not PSUTIL_AVAILABLE:
            return False
        
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            self.logger.info(f"Process {pid} suspended")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to suspend process {pid}: {e}")
            return False
    
    def resume_process(self, pid: int) -> bool:
        """İşlemi devam ettir"""
        if not PSUTIL_AVAILABLE:
            return False
        
        try:
            proc = psutil.Process(pid)
            proc.resume()
            self.logger.info(f"Process {pid} resumed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume process {pid}: {e}")
            return False
    
    def get_process_details(self, pid: int) -> Optional[Dict]:
        """İşlem detaylarını al"""
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            proc = psutil.Process(pid)
            
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_info': proc.memory_info()._asdict(),
                'memory_percent': proc.memory_percent(),
                'num_threads': proc.num_threads(),
                'username': proc.username(),
                'cmdline': proc.cmdline(),
                'create_time': proc.create_time(),
                'cwd': proc.cwd(),
                'exe': proc.exe(),
                'environ': dict(proc.environ()),
                'connections': [conn._asdict() for conn in proc.connections()],
                'open_files': [f._asdict() for f in proc.open_files()]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get process details for {pid}: {e}")
            return None
    
    def _get_mock_processes(self) -> List[ProcessInfo]:
        """Mock işlem listesi"""
        import random
        
        mock_processes = [
            "python3", "chrome", "firefox", "code", "terminal", "finder",
            "system", "kernel_task", "launchd", "WindowServer", "dock"
        ]
        
        processes = []
        for i, name in enumerate(mock_processes):
            processes.append(ProcessInfo(
                pid=1000 + i,
                name=name,
                status="running",
                cpu_percent=random.uniform(0, 20),
                memory_mb=random.uniform(10, 500),
                memory_percent=random.uniform(0.1, 5.0),
                thread_count=random.randint(1, 10),
                username="user",
                cmdline=f"/usr/bin/{name}",
                create_time=1234567890.0
            ))
        
        return processes
    
    def _get_mock_applications(self) -> List[ApplicationInfo]:
        """Mock uygulama listesi"""
        import random
        
        mock_apps = [
            ("Cloud Settings", "cloud_settings"),
            ("Cloud Files", "cloud_files"),
            ("Cloud Terminal", "cloud_terminal"),
            ("Cloud PyIDE", "cloud_pyide"),
            ("Cloud Browser", "cloud_browser")
        ]
        
        applications = []
        for name, app_id in mock_apps:
            status = random.choice(["Running", "Stopped", "Suspended"])
            
            applications.append(ApplicationInfo(
                name=name,
                app_id=app_id,
                status=status,
                pid=random.randint(2000, 9999) if status == "Running" else None,
                memory_mb=random.uniform(50, 300) if status == "Running" else 0.0,
                cpu_percent=random.uniform(0, 15) if status == "Running" else 0.0,
                thread_count=random.randint(2, 8) if status == "Running" else 0,
                path=f"/apps/{app_id}"
            ))
        
        return applications 