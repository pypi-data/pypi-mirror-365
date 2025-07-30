"""
Cloud Task Manager - Sistem İzleyici
Sistem kaynaklarını izleme ve istatistik toplama
"""

import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class SystemStats:
    """Sistem istatistikleri"""
    cpu_percent: float = 0.0
    cpu_cores: int = 1
    memory_percent: float = 0.0
    memory_total_gb: float = 0.0
    memory_used_gb: float = 0.0
    memory_available_gb: float = 0.0
    disk_percent: float = 0.0
    disk_total_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_io_mb: float = 0.0
    network_mb: float = 0.0
    uptime_hours: float = 0.0
    process_count: int = 0

class SystemMonitor:
    """Sistem kaynak izleyicisi"""
    
    def __init__(self):
        self.logger = logging.getLogger("SystemMonitor")
        self.is_running = False
        self.last_disk_io = None
        self.last_network_io = None
        self.last_time = None
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available - using mock data")
    
    def start(self):
        """İzlemeyi başlat"""
        self.is_running = True
        self.logger.info("System monitoring started")
    
    def stop(self):
        """İzlemeyi durdur"""
        self.is_running = False
        self.logger.info("System monitoring stopped")
    
    def get_system_stats(self) -> SystemStats:
        """Sistem istatistiklerini al"""
        if not PSUTIL_AVAILABLE:
            return self._get_mock_stats()
        
        try:
            stats = SystemStats()
            
            # CPU
            stats.cpu_percent = psutil.cpu_percent(interval=0.1)
            stats.cpu_cores = psutil.cpu_count()
            
            # Memory
            memory = psutil.virtual_memory()
            stats.memory_percent = memory.percent
            stats.memory_total_gb = memory.total / (1024**3)
            stats.memory_used_gb = memory.used / (1024**3)
            stats.memory_available_gb = memory.available / (1024**3)
            
            # Disk
            disk = psutil.disk_usage('/')
            stats.disk_percent = disk.percent
            stats.disk_total_gb = disk.total / (1024**3)
            stats.disk_used_gb = disk.used / (1024**3)
            
            # Disk I/O
            stats.disk_io_mb = self._get_disk_io_rate()
            
            # Network
            stats.network_mb = self._get_network_rate()
            
            # Uptime
            boot_time = psutil.boot_time()
            stats.uptime_hours = (time.time() - boot_time) / 3600
            
            # Process count
            stats.process_count = len(psutil.pids())
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            return self._get_mock_stats()
    
    def _get_disk_io_rate(self) -> float:
        """Disk I/O hızını hesapla (MB/s)"""
        try:
            current_io = psutil.disk_io_counters()
            current_time = time.time()
            
            if self.last_disk_io and self.last_time:
                time_diff = current_time - self.last_time
                bytes_diff = (current_io.read_bytes + current_io.write_bytes) - \
                           (self.last_disk_io.read_bytes + self.last_disk_io.write_bytes)
                
                rate_mb = (bytes_diff / time_diff) / (1024**2)
                
                self.last_disk_io = current_io
                self.last_time = current_time
                
                return max(0, rate_mb)
            
            self.last_disk_io = current_io
            self.last_time = current_time
            return 0.0
            
        except Exception:
            return 0.0
    
    def _get_network_rate(self) -> float:
        """Ağ trafiği hızını hesapla (MB/s)"""
        try:
            current_net = psutil.net_io_counters()
            current_time = time.time()
            
            if self.last_network_io and self.last_time:
                time_diff = current_time - self.last_time
                bytes_diff = (current_net.bytes_sent + current_net.bytes_recv) - \
                           (self.last_network_io.bytes_sent + self.last_network_io.bytes_recv)
                
                rate_mb = (bytes_diff / time_diff) / (1024**2)
                
                self.last_network_io = current_net
                
                return max(0, rate_mb)
            
            self.last_network_io = current_net
            return 0.0
            
        except Exception:
            return 0.0
    
    def _get_mock_stats(self) -> SystemStats:
        """Mock sistem istatistikleri (psutil yoksa)"""
        import random
        
        return SystemStats(
            cpu_percent=random.uniform(10, 80),
            cpu_cores=4,
            memory_percent=random.uniform(30, 70),
            memory_total_gb=8.0,
            memory_used_gb=random.uniform(2, 6),
            memory_available_gb=random.uniform(2, 6),
            disk_percent=random.uniform(40, 80),
            disk_total_gb=256.0,
            disk_used_gb=random.uniform(100, 200),
            disk_io_mb=random.uniform(0, 10),
            network_mb=random.uniform(0, 5),
            uptime_hours=random.uniform(1, 24),
            process_count=random.randint(50, 200)
        ) 