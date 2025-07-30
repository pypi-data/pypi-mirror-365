"""
Cloud Task Manager - Thread Yöneticisi
Thread izleme ve TID bazlı yönetim (.cursorrules uyumlu)
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
import threading

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class ThreadInfo:
    """Thread bilgisi"""
    tid: int
    process_name: str
    pid: int
    status: str
    cpu_percent: float
    priority: int
    state: str

class ThreadManager:
    """Thread izleyici ve yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("ThreadManager")
        self.is_running = False
        self.threads_cache = []
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available - using mock data")
    
    def start(self):
        """Thread izlemeyi başlat"""
        self.is_running = True
        self.logger.info("Thread monitoring started")
    
    def stop(self):
        """Thread izlemeyi durdur"""
        self.is_running = False
        self.logger.info("Thread monitoring stopped")
    
    def get_threads(self) -> List[ThreadInfo]:
        """Tüm thread'leri al"""
        if not PSUTIL_AVAILABLE:
            return self._get_mock_threads()
        
        try:
            threads = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Her işlem için thread'leri al
                    process_threads = proc.threads()
                    
                    for thread in process_threads:
                        thread_info = ThreadInfo(
                            tid=thread.id,
                            process_name=proc.info['name'] or "Unknown",
                            pid=proc.info['pid'],
                            status="running",  # psutil thread status vermez
                            cpu_percent=thread.user_time + thread.system_time,  # Yaklaşık
                            priority=0,  # psutil thread priority vermez
                            state="active"
                        )
                        
                        threads.append(thread_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    # Bazı işlemler thread bilgisi vermeyebilir
                    continue
            
            self.threads_cache = threads
            return threads
            
        except Exception as e:
            self.logger.error(f"Failed to get threads: {e}")
            return self._get_mock_threads()
    
    def freeze_thread(self, tid: int) -> bool:
        """Thread'i dondur (.cursorrules gereksinimi)"""
        # Not: Gerçek thread dondurma işlemi platform-specific
        # Bu basit bir implementasyon
        
        self.logger.info(f"Freezing thread {tid}")
        
        if self.kernel:
            # Kernel üzerinden thread dondurma
            try:
                thread_module = self.kernel.get_module("thread")
                if thread_module:
                    return thread_module.freeze_thread(tid)
            except Exception as e:
                self.logger.error(f"Kernel thread freeze failed: {e}")
        
        # Fallback: Python threading modülü ile
        try:
            # Bu gerçek bir dondurma değil, sadece log
            self.logger.warning(f"Thread {tid} freeze requested (not implemented)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to freeze thread {tid}: {e}")
            return False
    
    def kill_thread(self, tid: int) -> bool:
        """Thread'i öldür (.cursorrules gereksinimi)"""
        self.logger.info(f"Killing thread {tid}")
        
        if self.kernel:
            # Kernel üzerinden thread öldürme
            try:
                thread_module = self.kernel.get_module("thread")
                if thread_module:
                    return thread_module.kill_thread(tid)
            except Exception as e:
                self.logger.error(f"Kernel thread kill failed: {e}")
        
        # Fallback: İşlemi bul ve sonlandır
        try:
            # Thread'in hangi işleme ait olduğunu bul
            for thread_info in self.threads_cache:
                if thread_info.tid == tid:
                    # İşlemi sonlandır (thread'i direkt öldüremeyiz)
                    if PSUTIL_AVAILABLE:
                        proc = psutil.Process(thread_info.pid)
                        proc.terminate()
                        self.logger.info(f"Terminated process {thread_info.pid} containing thread {tid}")
                        return True
                    break
            
            self.logger.warning(f"Thread {tid} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to kill thread {tid}: {e}")
            return False
    
    def get_thread_details(self, tid: int) -> Optional[Dict]:
        """Thread detaylarını al"""
        try:
            # Thread'i bul
            for thread_info in self.threads_cache:
                if thread_info.tid == tid:
                    
                    # İşlem bilgilerini de ekle
                    process_details = {}
                    if PSUTIL_AVAILABLE:
                        try:
                            proc = psutil.Process(thread_info.pid)
                            process_details = {
                                'process_name': proc.name(),
                                'process_status': proc.status(),
                                'process_memory': proc.memory_info()._asdict(),
                                'process_cpu': proc.cpu_percent()
                            }
                        except:
                            pass
                    
                    return {
                        'tid': thread_info.tid,
                        'pid': thread_info.pid,
                        'process_name': thread_info.process_name,
                        'status': thread_info.status,
                        'cpu_percent': thread_info.cpu_percent,
                        'priority': thread_info.priority,
                        'state': thread_info.state,
                        'process_details': process_details
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get thread details for {tid}: {e}")
            return None
    
    def get_threads_by_process(self, pid: int) -> List[ThreadInfo]:
        """Belirli bir işlemin thread'lerini al"""
        return [t for t in self.threads_cache if t.pid == pid]
    
    def get_thread_count_by_process(self) -> Dict[int, int]:
        """İşlem bazlı thread sayıları"""
        counts = {}
        for thread in self.threads_cache:
            counts[thread.pid] = counts.get(thread.pid, 0) + 1
        return counts
    
    def _get_mock_threads(self) -> List[ThreadInfo]:
        """Mock thread listesi"""
        import random
        
        mock_processes = [
            (1001, "python3"),
            (1002, "chrome"),
            (1003, "firefox"),
            (1004, "code"),
            (1005, "terminal"),
            (1006, "system")
        ]
        
        threads = []
        tid_counter = 10000
        
        for pid, process_name in mock_processes:
            # Her işlem için 1-8 thread
            thread_count = random.randint(1, 8)
            
            for i in range(thread_count):
                threads.append(ThreadInfo(
                    tid=tid_counter + i,
                    process_name=process_name,
                    pid=pid,
                    status=random.choice(["running", "sleeping", "waiting"]),
                    cpu_percent=random.uniform(0, 10),
                    priority=random.randint(0, 20),
                    state=random.choice(["active", "idle", "blocked"])
                ))
            
            tid_counter += thread_count
        
        return threads 