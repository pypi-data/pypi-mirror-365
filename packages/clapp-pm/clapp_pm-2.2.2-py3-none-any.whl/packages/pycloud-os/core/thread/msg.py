"""
Core Thread Messaging - Thread Mesajlaşma Sistemi
Farklı uygulamalardaki thread'lerin birbirine mesaj göndermesi
"""

import logging
from typing import Dict, List, Optional, Any
import threading
import queue
import time

class ThreadMessaging:
    """Thread'ler arası mesajlaşma sistemi"""
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("ThreadMessaging")
        
        # Mesaj kuyruğu
        self.message_queues: Dict[str, queue.Queue] = {}
        self.lock = threading.RLock()
        
    def send_message(self, target_thread: str, message: Any) -> bool:
        """Thread'e mesaj gönder"""
        try:
            with self.lock:
                if target_thread not in self.message_queues:
                    self.message_queues[target_thread] = queue.Queue()
                
                self.message_queues[target_thread].put(message)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_message(self, thread_id: str, timeout: Optional[float] = None) -> Optional[Any]:
        """Thread mesajı al"""
        try:
            with self.lock:
                if thread_id not in self.message_queues:
                    return None
                
                return self.message_queues[thread_id].get(timeout=timeout)
                
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Mesajlaşma istatistikleri"""
        with self.lock:
            return {
                "active_queues": len(self.message_queues),
                "total_messages": sum(q.qsize() for q in self.message_queues.values())
            } 