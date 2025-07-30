"""
PyCloud OS Service Manager
Arka plan servislerinin kontrolü, durumu ve başlatma önceliği
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class ServiceStatus(Enum):
    """Servis durumları"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    DISABLED = "disabled"

class ServicePriority(Enum):
    """Servis öncelikleri"""
    CRITICAL = "critical"  # Sistem kritik servisleri
    HIGH = "high"         # Yüksek öncelik
    NORMAL = "normal"     # Normal öncelik
    LOW = "low"          # Düşük öncelik

class ServiceType(Enum):
    """Servis türleri"""
    SYSTEM = "system"        # Sistem servisleri
    APPLICATION = "application"  # Uygulama servisleri
    USER = "user"           # Kullanıcı servisleri
    BACKGROUND = "background"    # Arka plan servisleri

@dataclass
class ServiceConfig:
    """Servis yapılandırması"""
    name: str
    description: str
    service_type: ServiceType
    priority: ServicePriority
    auto_start: bool = True
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    restart_delay: float = 5.0
    dependencies: List[str] = None
    environment: Dict[str, str] = None
    working_directory: str = None
    user: str = "system"
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.environment is None:
            self.environment = {}

@dataclass
class ServiceInfo:
    """Servis bilgi sınıfı"""
    config: ServiceConfig
    status: ServiceStatus
    pid: Optional[int] = None
    started_at: Optional[str] = None
    stopped_at: Optional[str] = None
    restart_count: int = 0
    last_error: Optional[str] = None
    uptime: float = 0.0
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['config']['service_type'] = self.config.service_type.value
        data['config']['priority'] = self.config.priority.value
        data['status'] = self.status.value
        return data

class Service:
    """Temel servis sınıfı"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"Service.{config.name}")
        self.running = False
        self.thread = None
        
        # Callbacks
        self.start_callback: Optional[Callable] = None
        self.stop_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
    
    def start(self) -> bool:
        """Servisi başlat"""
        if self.running:
            return True
        
        try:
            self.logger.info(f"Starting service {self.config.name}")
            
            # Bağımlılıkları kontrol et
            if not self._check_dependencies():
                self.logger.error("Dependencies not satisfied")
                return False
            
            # Servis thread'ini başlat
            self.thread = threading.Thread(target=self._run_service, daemon=True)
            self.thread.start()
            
            self.running = True
            
            if self.start_callback:
                self.start_callback()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            if self.error_callback:
                self.error_callback(str(e))
            return False
    
    def stop(self) -> bool:
        """Servisi durdur"""
        if not self.running:
            return True
        
        try:
            self.logger.info(f"Stopping service {self.config.name}")
            
            self.running = False
            
            # Thread'in bitmesini bekle
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5.0)
            
            if self.stop_callback:
                self.stop_callback()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop service: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Bağımlılıkları kontrol et"""
        # TODO: Gerçek bağımlılık kontrolü
        return True
    
    def _run_service(self):
        """Servis ana döngüsü - alt sınıflarda override edilmeli"""
        while self.running:
            try:
                self.service_loop()
                time.sleep(1.0)
            except Exception as e:
                self.logger.error(f"Service loop error: {e}")
                if self.error_callback:
                    self.error_callback(str(e))
                break
    
    def service_loop(self):
        """Servis döngüsü - alt sınıflarda implement edilmeli"""
        pass
    
    def is_running(self) -> bool:
        """Servis çalışıyor mu?"""
        return self.running and self.thread and self.thread.is_alive()

class SystemCleanupService(Service):
    """Sistem temizlik servisi"""
    
    def __init__(self):
        config = ServiceConfig(
            name="system_cleanup",
            description="Sistem dosyalarını ve geçici verileri temizler",
            service_type=ServiceType.SYSTEM,
            priority=ServicePriority.LOW,
            auto_start=True
        )
        super().__init__(config)
        self.cleanup_interval = 300  # 5 dakika
        self.last_cleanup = 0
    
    def service_loop(self):
        """Temizlik döngüsü"""
        current_time = time.time()
        
        if current_time - self.last_cleanup >= self.cleanup_interval:
            self._perform_cleanup()
            self.last_cleanup = current_time
        
        time.sleep(30)  # 30 saniye bekle
    
    def _perform_cleanup(self):
        """Temizlik işlemini gerçekleştir"""
        try:
            self.logger.info("Performing system cleanup...")
            
            # Geçici dosyaları temizle
            temp_dir = Path("temp")
            if temp_dir.exists():
                for file in temp_dir.glob("*.tmp"):
                    try:
                        file.unlink()
                    except Exception:
                        pass
            
            # Log dosyalarını rotasyona tabi tut
            logs_dir = Path("logs")
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log"):
                    try:
                        if log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                            # Log dosyasını yeniden adlandır
                            backup_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                            log_file.rename(logs_dir / backup_name)
                    except Exception:
                        pass
            
            self.logger.info("System cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

class HealthMonitorService(Service):
    """Sistem sağlık izleme servisi"""
    
    def __init__(self, kernel):
        config = ServiceConfig(
            name="health_monitor",
            description="Sistem sağlığını ve performansını izler",
            service_type=ServiceType.SYSTEM,
            priority=ServicePriority.HIGH,
            auto_start=True
        )
        super().__init__(config)
        self.kernel = kernel
        self.check_interval = 60  # 1 dakika
        self.last_check = 0
    
    def service_loop(self):
        """Sağlık kontrolü döngüsü"""
        current_time = time.time()
        
        if current_time - self.last_check >= self.check_interval:
            self._perform_health_check()
            self.last_check = current_time
        
        time.sleep(10)  # 10 saniye bekle
    
    def _perform_health_check(self):
        """Sağlık kontrolü gerçekleştir"""
        try:
            self.logger.debug("Performing health check...")
            
            # Bellek kontrolü
            memory_manager = self.kernel.get_module("memory")
            if memory_manager:
                memory_report = memory_manager.get_memory_report()
                system_info = memory_report.get("system", {})
                memory_percent = system_info.get("percent", 0)
                
                if memory_percent > 90:
                    self.logger.warning(f"High memory usage: {memory_percent:.1f}%")
                    # Bellek temizliği tetikle
                    memory_manager.force_cleanup()
            
            # Süreç kontrolü
            process_manager = self.kernel.get_module("process")
            if process_manager:
                running_processes = process_manager.get_running_processes()
                if len(running_processes) > 50:
                    self.logger.warning(f"High process count: {len(running_processes)}")
            
            # Disk alanı kontrolü
            import shutil
            total, used, free = shutil.disk_usage(".")
            usage_percent = (used / total) * 100
            
            if usage_percent > 85:
                self.logger.warning(f"High disk usage: {usage_percent:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

class ServiceManager:
    """Servis yöneticisi"""
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("ServiceManager")
        self.services: Dict[str, ServiceInfo] = {}
        self.service_instances: Dict[str, Service] = {}
        
        # Servis gözlemcisi
        self.watchdog_running = False
        self.watchdog_thread = None
        
        # Boot sırası
        self.boot_order: List[str] = []
        
        self._load_system_services()
        self.start_watchdog()
    
    def _load_system_services(self):
        """Sistem servislerini yükle"""
        try:
            # Sistem temizlik servisi
            cleanup_service = SystemCleanupService()
            self.register_service(cleanup_service)
            
            # Sağlık izleme servisi
            health_service = HealthMonitorService(self.kernel)
            self.register_service(health_service)
            
            self.logger.info("System services loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load system services: {e}")
    
    def register_service(self, service: Service) -> bool:
        """Servis kaydet"""
        try:
            name = service.config.name
            
            if name in self.services:
                self.logger.warning(f"Service {name} already registered")
                return False
            
            # ServiceInfo oluştur
            service_info = ServiceInfo(
                config=service.config,
                status=ServiceStatus.STOPPED
            )
            
            self.services[name] = service_info
            self.service_instances[name] = service
            
            # Callback'leri ayarla
            service.start_callback = lambda: self._on_service_started(name)
            service.stop_callback = lambda: self._on_service_stopped(name)
            service.error_callback = lambda error: self._on_service_error(name, error)
            
            # Boot sırasına ekle (önceliğe göre)
            self._update_boot_order()
            
            self.logger.info(f"Service {name} registered")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service {service.config.name}: {e}")
            return False
    
    def _update_boot_order(self):
        """Boot sırasını güncelle (önceliğe göre)"""
        priority_order = {
            ServicePriority.CRITICAL: 0,
            ServicePriority.HIGH: 1,
            ServicePriority.NORMAL: 2,
            ServicePriority.LOW: 3
        }
        
        services_with_priority = []
        for name, info in self.services.items():
            if info.config.auto_start:
                priority_value = priority_order.get(info.config.priority, 3)
                services_with_priority.append((priority_value, name))
        
        # Önceliğe göre sırala
        services_with_priority.sort(key=lambda x: x[0])
        self.boot_order = [name for _, name in services_with_priority]
    
    def start_service(self, name: str) -> bool:
        """Servis başlat"""
        if name not in self.services:
            self.logger.error(f"Service {name} not found")
            return False
        
        service_info = self.services[name]
        service = self.service_instances[name]
        
        if service_info.status == ServiceStatus.RUNNING:
            self.logger.info(f"Service {name} already running")
            return True
        
        try:
            service_info.status = ServiceStatus.STARTING
            service_info.started_at = datetime.now().isoformat()
            
            if service.start():
                service_info.status = ServiceStatus.RUNNING
                service_info.restart_count = 0
                self.logger.info(f"Service {name} started successfully")
                return True
            else:
                service_info.status = ServiceStatus.FAILED
                service_info.last_error = "Failed to start"
                return False
                
        except Exception as e:
            service_info.status = ServiceStatus.FAILED
            service_info.last_error = str(e)
            self.logger.error(f"Failed to start service {name}: {e}")
            return False
    
    def stop_service(self, name: str) -> bool:
        """Servis durdur"""
        if name not in self.services:
            self.logger.error(f"Service {name} not found")
            return False
        
        service_info = self.services[name]
        service = self.service_instances[name]
        
        if service_info.status != ServiceStatus.RUNNING:
            self.logger.info(f"Service {name} not running")
            return True
        
        try:
            service_info.status = ServiceStatus.STOPPING
            
            if service.stop():
                service_info.status = ServiceStatus.STOPPED
                service_info.stopped_at = datetime.now().isoformat()
                self.logger.info(f"Service {name} stopped successfully")
                return True
            else:
                service_info.status = ServiceStatus.FAILED
                service_info.last_error = "Failed to stop"
                return False
                
        except Exception as e:
            service_info.status = ServiceStatus.FAILED
            service_info.last_error = str(e)
            self.logger.error(f"Failed to stop service {name}: {e}")
            return False
    
    def restart_service(self, name: str) -> bool:
        """Servis yeniden başlat"""
        self.logger.info(f"Restarting service {name}")
        
        if self.stop_service(name):
            time.sleep(1.0)  # Kısa bekleme
            return self.start_service(name)
        
        return False
    
    def get_service_status(self, name: str) -> Optional[ServiceStatus]:
        """Servis durumu al"""
        if name in self.services:
            return self.services[name].status
        return None
    
    def get_service_info(self, name: str) -> Optional[ServiceInfo]:
        """Servis bilgisi al"""
        return self.services.get(name)
    
    def list_services(self) -> List[ServiceInfo]:
        """Tüm servisleri listele"""
        return list(self.services.values())
    
    def start_all_services(self):
        """Tüm servisleri başlat (boot sırasına göre)"""
        self.logger.info("Starting all services...")
        
        for name in self.boot_order:
            service_info = self.services[name]
            if service_info.config.auto_start:
                self.start_service(name)
                time.sleep(0.5)  # Servisler arası kısa bekleme
        
        self.logger.info("All services started")
    
    def stop_all_services(self):
        """Tüm servisleri durdur (ters sırada)"""
        self.logger.info("Stopping all services...")
        
        # Ters sırada durdur
        for name in reversed(self.boot_order):
            if self.services[name].status == ServiceStatus.RUNNING:
                self.stop_service(name)
                time.sleep(0.2)
        
        self.logger.info("All services stopped")
    
    def start_watchdog(self):
        """Servis gözlemcisini başlat"""
        if self.watchdog_running:
            return
        
        self.watchdog_running = True
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.watchdog_thread.start()
        self.logger.info("Service watchdog started")
    
    def stop_watchdog(self):
        """Servis gözlemcisini durdur"""
        self.watchdog_running = False
        if self.watchdog_thread and self.watchdog_thread.is_alive():
            self.watchdog_thread.join(timeout=2.0)
        self.logger.info("Service watchdog stopped")
    
    def _watchdog_loop(self):
        """Servis gözlemci döngüsü"""
        while self.watchdog_running:
            try:
                self._check_services()
                time.sleep(10.0)  # 10 saniye bekle
            except Exception as e:
                self.logger.error(f"Watchdog error: {e}")
                time.sleep(30.0)
    
    def _check_services(self):
        """Servisleri kontrol et"""
        for name, service_info in self.services.items():
            service = self.service_instances[name]
            
            # Çalışması gereken ama çalışmayan servisler
            if (service_info.status == ServiceStatus.RUNNING and 
                not service.is_running()):
                
                self.logger.warning(f"Service {name} appears to have crashed")
                service_info.status = ServiceStatus.FAILED
                service_info.last_error = "Service crashed"
                
                # Yeniden başlatma dene
                if (service_info.config.restart_on_failure and 
                    service_info.restart_count < service_info.config.max_restart_attempts):
                    
                    self.logger.info(f"Attempting to restart service {name}")
                    service_info.restart_count += 1
                    
                    time.sleep(service_info.config.restart_delay)
                    self.start_service(name)
            
            # Uptime güncelle
            if service_info.status == ServiceStatus.RUNNING and service_info.started_at:
                try:
                    started = datetime.fromisoformat(service_info.started_at)
                    service_info.uptime = (datetime.now() - started).total_seconds()
                except Exception:
                    pass
    
    def _on_service_started(self, name: str):
        """Servis başlatma callback'i"""
        self.logger.debug(f"Service {name} started callback")
        
        # Event yayınla
        try:
            from core.events import publish, SystemEvents
            publish(SystemEvents.SERVICE_START, {
                "service_name": name
            }, source="ServiceManager")
        except ImportError:
            pass
    
    def _on_service_stopped(self, name: str):
        """Servis durdurma callback'i"""
        self.logger.debug(f"Service {name} stopped callback")
        
        # Event yayınla
        try:
            from core.events import publish, SystemEvents
            publish(SystemEvents.SERVICE_STOP, {
                "service_name": name
            }, source="ServiceManager")
        except ImportError:
            pass
    
    def _on_service_error(self, name: str, error: str):
        """Servis hata callback'i"""
        self.logger.error(f"Service {name} error: {error}")
        
        if name in self.services:
            self.services[name].last_error = error
    
    def get_services_report(self) -> Dict:
        """Servis raporu al"""
        try:
            services_data = {}
            
            for name, info in self.services.items():
                services_data[name] = info.to_dict()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_services": len(self.services),
                "running_services": len([s for s in self.services.values() if s.status == ServiceStatus.RUNNING]),
                "failed_services": len([s for s in self.services.values() if s.status == ServiceStatus.FAILED]),
                "boot_order": self.boot_order,
                "services": services_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate services report: {e}")
            return {}
    
    def shutdown(self):
        """Modül kapatma"""
        self.logger.info("Shutting down service manager...")
        
        # Watchdog'u durdur
        self.stop_watchdog()
        
        # Tüm servisleri durdur
        self.stop_all_services()
        
        self.logger.info("Service manager shutdown completed")

# Global service manager instance
_service_manager = None

def init_services(kernel=None) -> ServiceManager:
    """Service manager'ı başlat"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager(kernel)
        _service_manager.start_watchdog()
    return _service_manager

def get_service_manager() -> Optional[ServiceManager]:
    """Service manager'ı al"""
    return _service_manager 