"""
Core Thread Profiler - Thread Performans Analizi
Her thread'in çalışmasıyla ilgili performans verilerini sunan sistemsel analiz aracı
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class ThreadProfile:
    """Thread profil verisi"""
    thread_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_runtime: float = 0.0
    cpu_time: float = 0.0
    memory_peak: int = 0
    operations: List[str] = field(default_factory=list)

class ThreadProfiler:
    """Thread performans profiler'ı"""
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("ThreadProfiler")
        
        # Profil verileri
        self.profiles: Dict[str, ThreadProfile] = {}
        self.active_profiles: Dict[str, ThreadProfile] = {}
        self.lock = threading.RLock()
    
    def start_profiling(self, thread_id: str, name: str = "") -> bool:
        """Thread profiling'ini başlat"""
        try:
            with self.lock:
                if not name:
                    name = threading.current_thread().name
                
                profile = ThreadProfile(
                    thread_id=thread_id,
                    name=name,
                    start_time=datetime.now()
                )
                
                self.active_profiles[thread_id] = profile
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start profiling: {e}")
            return False
    
    def stop_profiling(self, thread_id: str) -> Optional[ThreadProfile]:
        """Thread profiling'ini durdur"""
        try:
            with self.lock:
                if thread_id in self.active_profiles:
                    profile = self.active_profiles[thread_id]
                    profile.end_time = datetime.now()
                    profile.total_runtime = (profile.end_time - profile.start_time).total_seconds()
                    
                    # Tamamlanmış profillere taşı
                    self.profiles[thread_id] = profile
                    del self.active_profiles[thread_id]
                    
                    return profile
                    
        except Exception as e:
            self.logger.error(f"Failed to stop profiling: {e}")
            
        return None
    
    def add_operation(self, thread_id: str, operation: str):
        """Profile'a operasyon ekle"""
        try:
            with self.lock:
                if thread_id in self.active_profiles:
                    self.active_profiles[thread_id].operations.append(f"{datetime.now().isoformat()}: {operation}")
                    
        except Exception as e:
            self.logger.debug(f"Failed to add operation: {e}")
    
    def get_profile(self, thread_id: str) -> Optional[ThreadProfile]:
        """Thread profil bilgilerini al"""
        with self.lock:
            return self.profiles.get(thread_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Profiler istatistikleri"""
        with self.lock:
            return {
                "active_profiles": len(self.active_profiles),
                "completed_profiles": len(self.profiles),
                "total_runtime": sum(p.total_runtime for p in self.profiles.values())
            } 