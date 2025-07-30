"""
PyCloud OS Application Monitor
Çalışan uygulamaları izler, kaynak kullanımını takip eder ve performans analizi yapar.
"""

import os
import json
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

class AppStatus(Enum):
    """Uygulama durumu"""
    RUNNING = "running"
    SUSPENDED = "suspended"
    CRASHED = "crashed"
    STARTING = "starting"
    STOPPING = "stopping"

class ResourceLevel(Enum):
    """Kaynak kullanım seviyesi"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AppResourceUsage:
    """Uygulama kaynak kullanımı"""
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_read_mb: float
    disk_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    threads_count: int
    open_files: int
    timestamp: float

@dataclass
class AppInfo:
    """Uygulama bilgileri"""
    app_id: str
    name: str
    version: str
    pid: int
    status: AppStatus
    start_time: float
    last_seen: float
    resource_usage: AppResourceUsage
    resource_level: ResourceLevel
    crash_count: int
    total_runtime: float
    app_path: str
    metadata: Dict[str, Any]

@dataclass
class AppLimits:
    """Uygulama kaynak sınırları"""
    max_cpu_percent: float = 80.0
    max_memory_mb: float = 1024.0
    max_memory_percent: float = 50.0
    max_threads: int = 100
    max_open_files: int = 1000
    suspension_threshold: float = 300.0  # 5 dakika
    crash_limit: int = 3

class ApplicationMonitor:
    """Uygulama izleme sistemi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.monitored_apps: Dict[str, AppInfo] = {}
        self.app_limits: Dict[str, AppLimits] = {}
        self.default_limits = AppLimits()
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitor_lock = threading.Lock()
        self.config_file = "system/config/appmon.json"
        self.stats_file = "system/logs/app_stats.json"
        self.monitor_interval = 5.0  # 5 saniye
        
        # Callbacks
        self.on_app_started = None
        self.on_app_stopped = None
        self.on_app_crashed = None
        self.on_resource_warning = None
        
        self._load_config()
        self._load_stats()
    
    def _load_config(self):
        """Konfigürasyon yükle"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Varsayılan limitleri yükle
                if 'default_limits' in config:
                    limits_data = config['default_limits']
                    self.default_limits = AppLimits(**limits_data)
                
                # Uygulama özel limitleri yükle
                if 'app_limits' in config:
                    for app_id, limits_data in config['app_limits'].items():
                        self.app_limits[app_id] = AppLimits(**limits_data)
                
                # Monitor ayarları
                self.monitor_interval = config.get('monitor_interval', 5.0)
                
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"AppMon config yükleme hatası: {e}", "ERROR")
    
    def _save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'default_limits': asdict(self.default_limits),
                'app_limits': {app_id: asdict(limits) for app_id, limits in self.app_limits.items()},
                'monitor_interval': self.monitor_interval,
                'last_updated': time.time()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"AppMon config kaydetme hatası: {e}", "ERROR")
    
    def _load_stats(self):
        """İstatistikleri yükle"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    
                # Önceki oturumdaki uygulamaları yükle
                for app_id, app_data in stats.get('apps', {}).items():
                    if app_data.get('status') == AppStatus.RUNNING.value:
                        # Çalışıyor olarak işaretlenmiş ama PID yoksa crashed olarak işaretle
                        pid = app_data.get('pid')
                        if not pid or not psutil.pid_exists(pid):
                            app_data['status'] = AppStatus.CRASHED.value
                            app_data['crash_count'] = app_data.get('crash_count', 0) + 1
                    
                    # AppInfo nesnesini yeniden oluştur
                    resource_data = app_data.get('resource_usage', {})
                    resource_usage = AppResourceUsage(**resource_data) if resource_data else None
                    
                    if resource_usage:
                        app_info = AppInfo(
                            app_id=app_data['app_id'],
                            name=app_data['name'],
                            version=app_data['version'],
                            pid=app_data['pid'],
                            status=AppStatus(app_data['status']),
                            start_time=app_data['start_time'],
                            last_seen=app_data['last_seen'],
                            resource_usage=resource_usage,
                            resource_level=ResourceLevel(app_data.get('resource_level', 'normal')),
                            crash_count=app_data.get('crash_count', 0),
                            total_runtime=app_data.get('total_runtime', 0),
                            app_path=app_data.get('app_path', ''),
                            metadata=app_data.get('metadata', {})
                        )
                        self.monitored_apps[app_id] = app_info
                        
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"AppMon stats yükleme hatası: {e}", "ERROR")
    
    def _save_stats(self):
        """İstatistikleri kaydet"""
        try:
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            
            stats = {
                'apps': {},
                'last_updated': time.time(),
                'monitor_session': {
                    'start_time': getattr(self, 'session_start_time', time.time()),
                    'total_apps_monitored': len(self.monitored_apps),
                    'active_apps': len([app for app in self.monitored_apps.values() 
                                      if app.status == AppStatus.RUNNING])
                }
            }
            
            # Uygulama verilerini kaydet
            for app_id, app_info in self.monitored_apps.items():
                stats['apps'][app_id] = {
                    'app_id': app_info.app_id,
                    'name': app_info.name,
                    'version': app_info.version,
                    'pid': app_info.pid,
                    'status': app_info.status.value,
                    'start_time': app_info.start_time,
                    'last_seen': app_info.last_seen,
                    'resource_usage': asdict(app_info.resource_usage),
                    'resource_level': app_info.resource_level.value,
                    'crash_count': app_info.crash_count,
                    'total_runtime': app_info.total_runtime,
                    'app_path': app_info.app_path,
                    'metadata': app_info.metadata
                }
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"AppMon stats kaydetme hatası: {e}", "ERROR")
    
    def start_monitoring(self):
        """İzlemeyi başlat"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.session_start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        if self.kernel:
            self.kernel.log("AppMon izleme başlatıldı", "INFO")
    
    def stop_monitoring(self):
        """İzlemeyi durdur"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        self._save_stats()
        self._save_config()
        
        if self.kernel:
            self.kernel.log("AppMon izleme durduruldu", "INFO")
    
    def _monitor_loop(self):
        """Ana izleme döngüsü"""
        while self.monitoring_active:
            try:
                with self.monitor_lock:
                    self._update_app_stats()
                    self._check_resource_limits()
                    self._check_suspended_apps()
                    self._cleanup_dead_apps()
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                if self.kernel:
                    self.kernel.log(f"AppMon izleme hatası: {e}", "ERROR")
                time.sleep(1.0)
    
    def _update_app_stats(self):
        """Uygulama istatistiklerini güncelle"""
        current_time = time.time()
        
        for app_id, app_info in self.monitored_apps.items():
            if app_info.status != AppStatus.RUNNING:
                continue
            
            try:
                # PID kontrolü
                if not psutil.pid_exists(app_info.pid):
                    self._mark_app_crashed(app_id)
                    continue
                
                # Process bilgilerini al
                process = psutil.Process(app_info.pid)
                
                # CPU ve bellek kullanımı
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = process.memory_percent()
                
                # IO bilgileri
                try:
                    io_counters = process.io_counters()
                    disk_read_mb = io_counters.read_bytes / 1024 / 1024
                    disk_write_mb = io_counters.write_bytes / 1024 / 1024
                except (psutil.AccessDenied, AttributeError):
                    disk_read_mb = disk_write_mb = 0
                
                # Ağ bilgileri (sistem geneli)
                try:
                    net_io = psutil.net_io_counters()
                    network_sent_mb = net_io.bytes_sent / 1024 / 1024
                    network_recv_mb = net_io.bytes_recv / 1024 / 1024
                except AttributeError:
                    network_sent_mb = network_recv_mb = 0
                
                # Thread ve dosya sayısı
                threads_count = process.num_threads()
                try:
                    open_files = len(process.open_files())
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    open_files = 0
                
                # Kaynak kullanımını güncelle
                app_info.resource_usage = AppResourceUsage(
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    memory_percent=memory_percent,
                    disk_read_mb=disk_read_mb,
                    disk_write_mb=disk_write_mb,
                    network_sent_mb=network_sent_mb,
                    network_recv_mb=network_recv_mb,
                    threads_count=threads_count,
                    open_files=open_files,
                    timestamp=current_time
                )
                
                # Kaynak seviyesini belirle
                app_info.resource_level = self._calculate_resource_level(app_info)
                
                # Son görülme zamanını güncelle
                app_info.last_seen = current_time
                
                # Toplam çalışma süresini güncelle
                app_info.total_runtime += self.monitor_interval
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self._mark_app_crashed(app_id)
            except Exception as e:
                if self.kernel:
                    self.kernel.log(f"AppMon {app_id} güncelleme hatası: {e}", "WARNING")
    
    def _calculate_resource_level(self, app_info: AppInfo) -> ResourceLevel:
        """Kaynak kullanım seviyesini hesapla"""
        limits = self.app_limits.get(app_info.app_id, self.default_limits)
        usage = app_info.resource_usage
        
        # Kritik seviye kontrolü
        if (usage.cpu_percent > limits.max_cpu_percent * 1.2 or
            usage.memory_mb > limits.max_memory_mb * 1.2 or
            usage.memory_percent > limits.max_memory_percent * 1.2):
            return ResourceLevel.CRITICAL
        
        # Yüksek seviye kontrolü
        if (usage.cpu_percent > limits.max_cpu_percent or
            usage.memory_mb > limits.max_memory_mb or
            usage.memory_percent > limits.max_memory_percent):
            return ResourceLevel.HIGH
        
        # Normal seviye kontrolü
        if (usage.cpu_percent > limits.max_cpu_percent * 0.5 or
            usage.memory_mb > limits.max_memory_mb * 0.5):
            return ResourceLevel.NORMAL
        
        return ResourceLevel.LOW
    
    def _check_resource_limits(self):
        """Kaynak limitlerini kontrol et"""
        for app_id, app_info in self.monitored_apps.items():
            if app_info.status != AppStatus.RUNNING:
                continue
            
            limits = self.app_limits.get(app_id, self.default_limits)
            usage = app_info.resource_usage
            
            # Kritik seviye uyarısı
            if app_info.resource_level == ResourceLevel.CRITICAL:
                if self.on_resource_warning:
                    self.on_resource_warning(app_id, app_info, "critical")
                
                if self.kernel:
                    self.kernel.log(f"AppMon: {app_info.name} kritik kaynak kullanımı", "WARNING")
            
            # Thread limiti kontrolü
            if usage.threads_count > limits.max_threads:
                if self.kernel:
                    self.kernel.log(f"AppMon: {app_info.name} thread limiti aşıldı", "WARNING")
            
            # Açık dosya limiti kontrolü
            if usage.open_files > limits.max_open_files:
                if self.kernel:
                    self.kernel.log(f"AppMon: {app_info.name} dosya limiti aşıldı", "WARNING")
    
    def _check_suspended_apps(self):
        """Askıya alınabilir uygulamaları kontrol et"""
        current_time = time.time()
        
        for app_id, app_info in self.monitored_apps.items():
            if app_info.status != AppStatus.RUNNING:
                continue
            
            limits = self.app_limits.get(app_id, self.default_limits)
            
            # Uzun süre kullanılmayan uygulamalar
            if (current_time - app_info.last_seen > limits.suspension_threshold and
                app_info.resource_level == ResourceLevel.LOW):
                
                self._suspend_app(app_id)
    
    def _cleanup_dead_apps(self):
        """Ölü uygulamaları temizle"""
        current_time = time.time()
        to_remove = []
        
        for app_id, app_info in self.monitored_apps.items():
            # 1 saatten fazla görülmeyen crashed uygulamaları temizle
            if (app_info.status == AppStatus.CRASHED and
                current_time - app_info.last_seen > 3600):
                to_remove.append(app_id)
        
        for app_id in to_remove:
            del self.monitored_apps[app_id]
            if self.kernel:
                self.kernel.log(f"AppMon: {app_id} temizlendi", "INFO")
    
    def _mark_app_crashed(self, app_id: str):
        """Uygulamayı crashed olarak işaretle"""
        if app_id in self.monitored_apps:
            app_info = self.monitored_apps[app_id]
            app_info.status = AppStatus.CRASHED
            app_info.crash_count += 1
            app_info.last_seen = time.time()
            
            if self.on_app_crashed:
                self.on_app_crashed(app_id, app_info)
            
            if self.kernel:
                self.kernel.log(f"AppMon: {app_info.name} çöktü (#{app_info.crash_count})", "ERROR")
    
    def _suspend_app(self, app_id: str):
        """Uygulamayı askıya al"""
        if app_id in self.monitored_apps:
            app_info = self.monitored_apps[app_id]
            
            try:
                process = psutil.Process(app_info.pid)
                process.suspend()
                app_info.status = AppStatus.SUSPENDED
                
                if self.kernel:
                    self.kernel.log(f"AppMon: {app_info.name} askıya alındı", "INFO")
                    
            except Exception as e:
                if self.kernel:
                    self.kernel.log(f"AppMon: {app_info.name} askıya alma hatası: {e}", "ERROR")
    
    def register_app(self, app_id: str, name: str, version: str, pid: int, app_path: str, metadata: Dict[str, Any] = None):
        """Yeni uygulama kaydet"""
        current_time = time.time()
        
        # Varsayılan kaynak kullanımı
        default_usage = AppResourceUsage(
            cpu_percent=0.0,
            memory_mb=0.0,
            memory_percent=0.0,
            disk_read_mb=0.0,
            disk_write_mb=0.0,
            network_sent_mb=0.0,
            network_recv_mb=0.0,
            threads_count=1,
            open_files=0,
            timestamp=current_time
        )
        
        app_info = AppInfo(
            app_id=app_id,
            name=name,
            version=version,
            pid=pid,
            status=AppStatus.STARTING,
            start_time=current_time,
            last_seen=current_time,
            resource_usage=default_usage,
            resource_level=ResourceLevel.LOW,
            crash_count=0,
            total_runtime=0.0,
            app_path=app_path,
            metadata=metadata or {}
        )
        
        with self.monitor_lock:
            self.monitored_apps[app_id] = app_info
        
        if self.on_app_started:
            self.on_app_started(app_id, app_info)
        
        if self.kernel:
            self.kernel.log(f"AppMon: {name} kaydedildi (PID: {pid})", "INFO")
        
        # Birkaç saniye sonra RUNNING durumuna geçir
        threading.Timer(2.0, lambda: self._mark_app_running(app_id)).start()
    
    def _mark_app_running(self, app_id: str):
        """Uygulamayı running olarak işaretle"""
        if app_id in self.monitored_apps:
            self.monitored_apps[app_id].status = AppStatus.RUNNING
    
    def unregister_app(self, app_id: str):
        """Uygulamayı kayıttan çıkar"""
        if app_id in self.monitored_apps:
            app_info = self.monitored_apps[app_id]
            app_info.status = AppStatus.STOPPING
            app_info.last_seen = time.time()
            
            if self.on_app_stopped:
                self.on_app_stopped(app_id, app_info)
            
            if self.kernel:
                self.kernel.log(f"AppMon: {app_info.name} durduruldu", "INFO")
            
            # 30 saniye sonra tamamen kaldır
            threading.Timer(30.0, lambda: self._remove_app(app_id)).start()
    
    def _remove_app(self, app_id: str):
        """Uygulamayı tamamen kaldır"""
        with self.monitor_lock:
            if app_id in self.monitored_apps:
                del self.monitored_apps[app_id]
    
    def get_app_info(self, app_id: str) -> Optional[AppInfo]:
        """Uygulama bilgilerini al"""
        return self.monitored_apps.get(app_id)
    
    def get_all_apps(self) -> Dict[str, AppInfo]:
        """Tüm uygulamaları al"""
        return self.monitored_apps.copy()
    
    def get_running_apps(self) -> Dict[str, AppInfo]:
        """Çalışan uygulamaları al"""
        return {app_id: app_info for app_id, app_info in self.monitored_apps.items()
                if app_info.status == AppStatus.RUNNING}
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Kaynak kullanım özeti"""
        running_apps = self.get_running_apps()
        
        if not running_apps:
            return {
                'total_apps': 0,
                'total_cpu': 0.0,
                'total_memory_mb': 0.0,
                'total_threads': 0,
                'resource_levels': {'low': 0, 'normal': 0, 'high': 0, 'critical': 0}
            }
        
        total_cpu = sum(app.resource_usage.cpu_percent for app in running_apps.values())
        total_memory = sum(app.resource_usage.memory_mb for app in running_apps.values())
        total_threads = sum(app.resource_usage.threads_count for app in running_apps.values())
        
        resource_levels = {'low': 0, 'normal': 0, 'high': 0, 'critical': 0}
        for app in running_apps.values():
            resource_levels[app.resource_level.value] += 1
        
        return {
            'total_apps': len(running_apps),
            'total_cpu': total_cpu,
            'total_memory_mb': total_memory,
            'total_threads': total_threads,
            'resource_levels': resource_levels,
            'timestamp': time.time()
        }
    
    def set_app_limits(self, app_id: str, limits: AppLimits):
        """Uygulama limitlerini ayarla"""
        self.app_limits[app_id] = limits
        self._save_config()
    
    def get_app_limits(self, app_id: str) -> AppLimits:
        """Uygulama limitlerini al"""
        return self.app_limits.get(app_id, self.default_limits)
    
    def resume_app(self, app_id: str) -> bool:
        """Askıya alınan uygulamayı devam ettir"""
        if app_id not in self.monitored_apps:
            return False
        
        app_info = self.monitored_apps[app_id]
        if app_info.status != AppStatus.SUSPENDED:
            return False
        
        try:
            process = psutil.Process(app_info.pid)
            process.resume()
            app_info.status = AppStatus.RUNNING
            app_info.last_seen = time.time()
            
            if self.kernel:
                self.kernel.log(f"AppMon: {app_info.name} devam ettirildi", "INFO")
            
            return True
            
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"AppMon: {app_info.name} devam ettirme hatası: {e}", "ERROR")
            return False
    
    def kill_app(self, app_id: str) -> bool:
        """Uygulamayı zorla sonlandır"""
        if app_id not in self.monitored_apps:
            return False
        
        app_info = self.monitored_apps[app_id]
        
        try:
            process = psutil.Process(app_info.pid)
            process.terminate()
            
            # 5 saniye bekle, sonra kill
            threading.Timer(5.0, lambda: self._force_kill_app(app_id)).start()
            
            if self.kernel:
                self.kernel.log(f"AppMon: {app_info.name} sonlandırılıyor", "INFO")
            
            return True
            
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"AppMon: {app_info.name} sonlandırma hatası: {e}", "ERROR")
            return False
    
    def _force_kill_app(self, app_id: str):
        """Uygulamayı zorla öldür"""
        if app_id not in self.monitored_apps:
            return
        
        app_info = self.monitored_apps[app_id]
        
        try:
            if psutil.pid_exists(app_info.pid):
                process = psutil.Process(app_info.pid)
                process.kill()
                
                if self.kernel:
                    self.kernel.log(f"AppMon: {app_info.name} zorla sonlandırıldı", "WARNING")
                    
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"AppMon: {app_info.name} zorla sonlandırma hatası: {e}", "ERROR")
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri al"""
        return {
            'monitored_apps': len(self.monitored_apps),
            'running_apps': len(self.get_running_apps()),
            'monitoring_active': self.monitoring_active,
            'monitor_interval': self.monitor_interval,
            'session_start_time': getattr(self, 'session_start_time', 0),
            'resource_summary': self.get_resource_summary(),
            'apps': {app_id: {
                'name': app.name,
                'status': app.status.value,
                'resource_level': app.resource_level.value,
                'cpu_percent': app.resource_usage.cpu_percent,
                'memory_mb': app.resource_usage.memory_mb,
                'crash_count': app.crash_count,
                'total_runtime': app.total_runtime
            } for app_id, app in self.monitored_apps.items()}
        }

# Global instance
appmon = None

def get_appmon():
    """Global AppMon instance'ını al"""
    global appmon
    return appmon

def init_appmon(kernel=None):
    """AppMon'u başlat"""
    global appmon
    if appmon is None:
        appmon = ApplicationMonitor(kernel)
        appmon.start_monitoring()
    return appmon 