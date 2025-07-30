"""
Core Thread Snapshot - Thread Durum Kaydetme
Thread'in anlık durumunu kaydedip daha sonra aynı noktadan devam etme
"""

import logging
import pickle
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime

class ThreadSnapshot:
    """Thread snapshot yönetimi"""
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("ThreadSnapshot")
        
        # Snapshot verileri
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
    
    def take_snapshot(self, thread_id: str, state_data: Dict[str, Any]) -> bool:
        """Thread snapshot'ı al"""
        try:
            with self.lock:
                self.snapshots[thread_id] = {
                    "state": state_data,
                    "timestamp": datetime.now().isoformat(),
                    "thread_name": threading.current_thread().name
                }
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to take snapshot: {e}")
            return False
    
    def restore_snapshot(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Thread snapshot'ını geri yükle"""
        try:
            with self.lock:
                return self.snapshots.get(thread_id)
                
        except Exception as e:
            self.logger.error(f"Failed to restore snapshot: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Snapshot istatistikleri"""
        with self.lock:
            return {
                "total_snapshots": len(self.snapshots),
                "snapshots": list(self.snapshots.keys())
            } 