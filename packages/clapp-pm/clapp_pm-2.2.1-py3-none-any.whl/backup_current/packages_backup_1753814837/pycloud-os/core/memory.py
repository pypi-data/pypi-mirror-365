"""
PyCloud OS Memory Manager
RAM ve geçici bellek kullanımı izleme ve yönetim modülü
"""

import os
import gc
import sys
import time
import logging
import threading
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class MemoryType(Enum):
    """Bellek türleri"""
    SYSTEM = "system"
    APPLICATION = "application"
    CACHE = "cache"
    BUFFER = "buffer"
    RAMDISK = "ramdisk"
    TEMPFS = "tempfs"

@dataclass
class MemoryUsage:
    """Bellek kullanım bilgisi"""
    module_name: str
    memory_type: MemoryType
    allocated_mb: float
    peak_mb: float
    timestamp: str
    details: Dict = None
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['memory_type'] = self.memory_type.value
        return data

@dataclass
class MemoryQuota:
    """Bellek kotası"""
    user_id: str
    max_memory_mb: float
    current_usage_mb: float = 0.0
    warning_threshold: float = 0.8  # %80
    enabled: bool = True

class RAMDisk:
    """RAM disk yöneticisi"""
    
    def __init__(self, name: str, size_mb: float):
        self.name = name
        self.size_mb = size_mb
        self.mount_point = None
        self.created_at = datetime.now()
        self.files: Dict[str, bytes] = {}
        self.usage_mb = 0.0
    
    def create_file(self, filename: str, content: bytes) -> bool:
        """RAM disk'te dosya oluştur"""
        try:
            file_size_mb = len(content) / 1024 / 1024
            
            if self.usage_mb + file_size_mb > self.size_mb:
                return False  # Yetersiz alan
            
            self.files[filename] = content
            self.usage_mb += file_size_mb
            return True
            
        except Exception:
            return False
    
    def read_file(self, filename: str) -> Optional[bytes]:
        """RAM disk'ten dosya oku"""
        return self.files.get(filename)
    
    def delete_file(self, filename: str) -> bool:
        """RAM disk'ten dosya sil"""
        if filename in self.files:
            content = self.files[filename]
            file_size_mb = len(content) / 1024 / 1024
            del self.files[filename]
            self.usage_mb -= file_size_mb
            return True
        return False
    
    def list_files(self) -> List[str]:
        """Dosya listesi"""
        return list(self.files.keys())
    
    def get_usage(self) -> Dict:
        """Kullanım bilgisi"""
        return {
            "name": self.name,
            "size_mb": self.size_mb,
            "usage_mb": self.usage_mb,
            "free_mb": self.size_mb - self.usage_mb,
            "usage_percent": (self.usage_mb / self.size_mb) * 100,
            "file_count": len(self.files)
        }

class TempFS:
    """Geçici dosya sistemi"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or tempfile.gettempdir()
        self.pycloud_temp = Path(self.base_path) / "pycloud_temp"
        self.pycloud_temp.mkdir(exist_ok=True)
        self.temp_files: List[str] = []
        self.logger = logging.getLogger("TempFS")
    
    def create_temp_file(self, prefix: str = "pycloud_", suffix: str = ".tmp") -> str:
        """Geçici dosya oluştur"""
        try:
            fd, filepath = tempfile.mkstemp(
                prefix=prefix,
                suffix=suffix,
                dir=str(self.pycloud_temp)
            )
            os.close(fd)
            
            self.temp_files.append(filepath)
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to create temp file: {e}")
            return None
    
    def create_temp_dir(self, prefix: str = "pycloud_") -> str:
        """Geçici dizin oluştur"""
        try:
            dirpath = tempfile.mkdtemp(
                prefix=prefix,
                dir=str(self.pycloud_temp)
            )
            
            self.temp_files.append(dirpath)
            return dirpath
            
        except Exception as e:
            self.logger.error(f"Failed to create temp dir: {e}")
            return None
    
    def cleanup(self):
        """Geçici dosyaları temizle"""
        cleaned = 0
        
        for filepath in self.temp_files[:]:
            try:
                path = Path(filepath)
                if path.exists():
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(str(path))
                    cleaned += 1
                
                self.temp_files.remove(filepath)
                
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {filepath}: {e}")
        
        if cleaned > 0:
            self.logger.info(f"Cleaned up {cleaned} temporary files/directories")
    
    def get_usage(self) -> Dict:
        """Kullanım bilgisi"""
        total_size = 0
        file_count = 0
        
        for filepath in self.temp_files:
            try:
                path = Path(filepath)
                if path.exists():
                    if path.is_file():
                        total_size += path.stat().st_size
                        file_count += 1
                    elif path.is_dir():
                        for file in path.rglob("*"):
                            if file.is_file():
                                total_size += file.stat().st_size
                                file_count += 1
            except Exception:
                continue
        
        return {
            "base_path": str(self.pycloud_temp),
            "total_size_mb": total_size / 1024 / 1024,
            "file_count": file_count,
            "tracked_items": len(self.temp_files)
        }

class MemoryManager:
    """Bellek yöneticisi"""
    
    def __init__(self):
        self.logger = logging.getLogger("MemoryManager")
        self.memory_usage: Dict[str, MemoryUsage] = {}
        self.memory_quotas: Dict[str, MemoryQuota] = {}
        self.ramdisks: Dict[str, RAMDisk] = {}
        self.tempfs = TempFS()
        
        # Monitoring
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 5.0  # 5 saniye
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "memory_warning": [],
            "quota_exceeded": [],
            "low_memory": [],
            "cleanup_completed": []
        }
        
        # Sistem bellek eşikleri
        self.low_memory_threshold = 0.85  # %85
        self.critical_memory_threshold = 0.95  # %95
        
        self.start_monitoring()
    
    def start_monitoring(self):
        """Bellek izlemeyi başlat"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Bellek izlemeyi durdur"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self):
        """Bellek izleme döngüsü"""
        while self.monitoring:
            try:
                self._update_memory_stats()
                self._check_memory_warnings()
                self._check_quotas()
                time.sleep(self.monitor_interval)
            except Exception as e:
                self.logger.error(f"Memory monitor error: {e}")
                time.sleep(10.0)
    
    def _update_memory_stats(self):
        """Bellek istatistiklerini güncelle"""
        try:
            import psutil
            
            # Sistem bellek bilgisi
            memory = psutil.virtual_memory()
            
            # Python process bellek kullanımı
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Sistem bellek kullanımını kaydet
            system_usage = MemoryUsage(
                module_name="system",
                memory_type=MemoryType.SYSTEM,
                allocated_mb=memory.used / 1024 / 1024,
                peak_mb=memory.total / 1024 / 1024,
                timestamp=datetime.now().isoformat(),
                details={
                    "total_mb": memory.total / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                    "percent": memory.percent,
                    "cached_mb": memory.cached / 1024 / 1024 if hasattr(memory, 'cached') else 0,
                    "buffers_mb": memory.buffers / 1024 / 1024 if hasattr(memory, 'buffers') else 0
                }
            )
            
            self.memory_usage["system"] = system_usage
            
            # PyCloud process bellek kullanımı
            pycloud_usage = MemoryUsage(
                module_name="pycloud",
                memory_type=MemoryType.APPLICATION,
                allocated_mb=process_memory.rss / 1024 / 1024,
                peak_mb=process_memory.peak_wset / 1024 / 1024 if hasattr(process_memory, 'peak_wset') else process_memory.rss / 1024 / 1024,
                timestamp=datetime.now().isoformat(),
                details={
                    "vms_mb": process_memory.vms / 1024 / 1024,
                    "shared_mb": process_memory.shared / 1024 / 1024 if hasattr(process_memory, 'shared') else 0,
                    "text_mb": process_memory.text / 1024 / 1024 if hasattr(process_memory, 'text') else 0,
                    "data_mb": process_memory.data / 1024 / 1024 if hasattr(process_memory, 'data') else 0
                }
            )
            
            self.memory_usage["pycloud"] = pycloud_usage
            
        except ImportError:
            # psutil yoksa basit bellek takibi
            self._simple_memory_tracking()
        except Exception as e:
            self.logger.warning(f"Failed to update memory stats: {e}")
    
    def _simple_memory_tracking(self):
        """Basit bellek takibi (psutil olmadan)"""
        try:
            # Python garbage collector istatistikleri
            gc_stats = gc.get_stats()
            
            # Basit bellek tahmini
            estimated_mb = sys.getsizeof(gc.get_objects()) / 1024 / 1024
            
            simple_usage = MemoryUsage(
                module_name="pycloud_simple",
                memory_type=MemoryType.APPLICATION,
                allocated_mb=estimated_mb,
                peak_mb=estimated_mb,
                timestamp=datetime.now().isoformat(),
                details={
                    "gc_collections": sum(stat['collections'] for stat in gc_stats),
                    "gc_collected": sum(stat['collected'] for stat in gc_stats),
                    "gc_uncollectable": sum(stat['uncollectable'] for stat in gc_stats)
                }
            )
            
            self.memory_usage["pycloud_simple"] = simple_usage
            
        except Exception as e:
            self.logger.warning(f"Simple memory tracking failed: {e}")
    
    def _check_memory_warnings(self):
        """Bellek uyarılarını kontrol et"""
        system_usage = self.memory_usage.get("system")
        if not system_usage or not system_usage.details:
            return
        
        memory_percent = system_usage.details.get("percent", 0)
        
        if memory_percent >= self.critical_memory_threshold * 100:
            self._trigger_callback("low_memory", {
                "level": "critical",
                "usage_percent": memory_percent,
                "available_mb": system_usage.details.get("available_mb", 0)
            })
            
            # Kritik durum - otomatik temizlik
            self.force_cleanup()
            
        elif memory_percent >= self.low_memory_threshold * 100:
            self._trigger_callback("low_memory", {
                "level": "warning",
                "usage_percent": memory_percent,
                "available_mb": system_usage.details.get("available_mb", 0)
            })
    
    def _check_quotas(self):
        """Kullanıcı kotalarını kontrol et"""
        for user_id, quota in self.memory_quotas.items():
            if not quota.enabled:
                continue
            
            # Kullanıcının bellek kullanımını hesapla
            user_usage = self._calculate_user_memory_usage(user_id)
            quota.current_usage_mb = user_usage
            
            usage_ratio = user_usage / quota.max_memory_mb
            
            if usage_ratio >= 1.0:
                self._trigger_callback("quota_exceeded", {
                    "user_id": user_id,
                    "usage_mb": user_usage,
                    "limit_mb": quota.max_memory_mb,
                    "ratio": usage_ratio
                })
            elif usage_ratio >= quota.warning_threshold:
                self._trigger_callback("memory_warning", {
                    "user_id": user_id,
                    "usage_mb": user_usage,
                    "limit_mb": quota.max_memory_mb,
                    "ratio": usage_ratio
                })
    
    def _calculate_user_memory_usage(self, user_id: str) -> float:
        """Kullanıcının bellek kullanımını hesapla"""
        # TODO: Gerçek kullanıcı süreçlerinden hesapla
        # Şimdilik basit tahmin
        return 50.0  # 50MB varsayılan
    
    def register_module_memory(self, module_name: str, memory_type: MemoryType, allocated_mb: float):
        """Modül bellek kullanımını kaydet"""
        usage = MemoryUsage(
            module_name=module_name,
            memory_type=memory_type,
            allocated_mb=allocated_mb,
            peak_mb=allocated_mb,
            timestamp=datetime.now().isoformat()
        )
        
        # Mevcut kayıt varsa peak değeri güncelle
        if module_name in self.memory_usage:
            existing = self.memory_usage[module_name]
            usage.peak_mb = max(existing.peak_mb, allocated_mb)
        
        self.memory_usage[module_name] = usage
        self.logger.debug(f"Registered memory usage for {module_name}: {allocated_mb:.2f}MB")
    
    def create_ramdisk(self, name: str, size_mb: float) -> bool:
        """RAM disk oluştur"""
        try:
            if name in self.ramdisks:
                self.logger.warning(f"RAMDisk {name} already exists")
                return False
            
            ramdisk = RAMDisk(name, size_mb)
            self.ramdisks[name] = ramdisk
            
            # Bellek kullanımını kaydet
            self.register_module_memory(f"ramdisk_{name}", MemoryType.RAMDISK, size_mb)
            
            self.logger.info(f"Created RAMDisk {name} with size {size_mb}MB")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create RAMDisk {name}: {e}")
            return False
    
    def get_ramdisk(self, name: str) -> Optional[RAMDisk]:
        """RAM disk al"""
        return self.ramdisks.get(name)
    
    def destroy_ramdisk(self, name: str) -> bool:
        """RAM disk yok et"""
        try:
            if name not in self.ramdisks:
                return False
            
            del self.ramdisks[name]
            
            # Bellek kaydını sil
            if f"ramdisk_{name}" in self.memory_usage:
                del self.memory_usage[f"ramdisk_{name}"]
            
            self.logger.info(f"Destroyed RAMDisk {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to destroy RAMDisk {name}: {e}")
            return False
    
    def set_user_quota(self, user_id: str, max_memory_mb: float, warning_threshold: float = 0.8):
        """Kullanıcı bellek kotası ayarla"""
        quota = MemoryQuota(
            user_id=user_id,
            max_memory_mb=max_memory_mb,
            warning_threshold=warning_threshold
        )
        
        self.memory_quotas[user_id] = quota
        self.logger.info(f"Set memory quota for user {user_id}: {max_memory_mb}MB")
    
    def get_memory_report(self) -> Dict:
        """Bellek raporu al"""
        try:
            # Sistem bellek durumu
            system_usage = self.memory_usage.get("system")
            system_info = system_usage.details if system_usage else {}
            
            # Modül bellek kullanımları
            module_usage = {}
            for name, usage in self.memory_usage.items():
                module_usage[name] = usage.to_dict()
            
            # RAM disk kullanımları
            ramdisk_usage = {}
            for name, ramdisk in self.ramdisks.items():
                ramdisk_usage[name] = ramdisk.get_usage()
            
            # TempFS kullanımı
            tempfs_usage = self.tempfs.get_usage()
            
            # Kullanıcı kotaları
            quota_info = {}
            for user_id, quota in self.memory_quotas.items():
                quota_info[user_id] = asdict(quota)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system": system_info,
                "modules": module_usage,
                "ramdisks": ramdisk_usage,
                "tempfs": tempfs_usage,
                "quotas": quota_info,
                "thresholds": {
                    "low_memory": self.low_memory_threshold,
                    "critical_memory": self.critical_memory_threshold
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate memory report: {e}")
            return {}
    
    def force_cleanup(self):
        """Zorla bellek temizliği"""
        self.logger.info("Starting forced memory cleanup...")
        
        cleaned_mb = 0.0
        
        try:
            # Python garbage collection
            before_gc = len(gc.get_objects())
            collected = gc.collect()
            after_gc = len(gc.get_objects())
            
            self.logger.info(f"GC collected {collected} objects, {before_gc - after_gc} objects freed")
            
            # TempFS temizliği
            self.tempfs.cleanup()
            
            # RAM disk'lerde gereksiz dosyaları temizle
            for name, ramdisk in self.ramdisks.items():
                # Eski dosyaları temizle (örnek implementasyon)
                files_to_remove = []
                for filename in ramdisk.list_files():
                    if filename.startswith("temp_") or filename.endswith(".tmp"):
                        files_to_remove.append(filename)
                
                for filename in files_to_remove:
                    if ramdisk.delete_file(filename):
                        cleaned_mb += len(ramdisk.files.get(filename, b"")) / 1024 / 1024
            
            self._trigger_callback("cleanup_completed", {
                "cleaned_mb": cleaned_mb,
                "gc_collected": collected
            })
            
            self.logger.info(f"Memory cleanup completed, freed ~{cleaned_mb:.2f}MB")
            
        except Exception as e:
            self.logger.error(f"Memory cleanup failed: {e}")
    
    def add_callback(self, event_type: str, callback: Callable):
        """Callback ekle"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: str, callback: Callable):
        """Callback kaldır"""
        if event_type in self.callbacks:
            if callback in self.callbacks[event_type]:
                self.callbacks[event_type].remove(callback)
    
    def _trigger_callback(self, event_type: str, data: Dict):
        """Callback tetikle"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Memory callback error for {event_type}: {e}")
    
    def shutdown(self):
        """Modül kapatma"""
        self.logger.info("Shutting down memory manager...")
        
        # Monitoring'i durdur
        self.stop_monitoring()
        
        # TempFS temizliği
        self.tempfs.cleanup()
        
        # RAM disk'leri temizle
        for name in list(self.ramdisks.keys()):
            self.destroy_ramdisk(name)
        
        # Son bellek temizliği
        gc.collect()
        
        self.logger.info("Memory manager shutdown completed")

# Global memory manager instance
_memory_manager = None

def init_memory(kernel=None) -> MemoryManager:
    """Memory manager'ı başlat"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
        _memory_manager.start_monitoring()
    return _memory_manager

def get_memory_manager() -> Optional[MemoryManager]:
    """Memory manager'ı al"""
    return _memory_manager 