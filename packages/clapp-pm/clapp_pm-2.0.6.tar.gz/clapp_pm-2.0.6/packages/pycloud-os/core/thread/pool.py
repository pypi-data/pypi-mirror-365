"""
Core Thread Pool - Thread Havuzu Yöneticisi  
Thread yoğunluğunu sınırlı sayıda thread ile dengeleyen sistemsel yürütme havuzu
"""

import logging
import threading
import time
import concurrent.futures
import os
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
import uuid
import psutil

# Python 3.8+ için Future import
try:
    from typing import Future
except ImportError:
    from concurrent.futures import Future

@dataclass
class PoolStats:
    """Thread pool istatistikleri"""
    active_threads: int = 0
    idle_threads: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_task_time: float = 0.0
    peak_threads: int = 0
    total_uptime: float = 0.0

class ThreadPool:
    """
    Thread yoğunluğunu sınırlı sayıda thread ile dengeleyen sistemsel yürütme havuzu.
    Çekirdek sayısına göre sabit havuz oluşturma, aşırı yoğunlukta bekletme.
    """
    
    def __init__(self, kernel, max_workers: Optional[int] = None):
        self.kernel = kernel
        self.logger = logging.getLogger("ThreadPool")
        
        # Worker sayısını belirle
        if max_workers is None:
            # CPU çekirdek sayısının 2 katı (I/O intensive işler için)
            max_workers = min(32, (os.cpu_count() or 1) * 2)
        
        self.max_workers = max_workers
        self.min_workers = max(1, max_workers // 4)  # Minimum %25
        
        # Thread pool executor
        self.executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self.running = False
        self.start_time = None
        
        # Görev takibi
        self.active_futures: Dict[str, Future] = {}
        self.task_results: Dict[str, Any] = {}
        
        # İstatistikler
        self.stats = PoolStats()
        self.task_completion_times: List[float] = []
        
        # Monitoring
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_active = False
        
        # Thread limit ve backpressure
        self.task_limit = max_workers * 10  # Maksimum bekleyen görev sayısı
        self.backpressure_enabled = True
        
        # Locks
        self.stats_lock = threading.RLock()
        
    def start(self):
        """Thread pool'u başlat"""
        try:
            if self.running:
                return
            
            # ThreadPoolExecutor'ı başlat
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="PyCloudPool"
            )
            
            self.running = True
            self.start_time = time.time()
            
            # Monitoring başlat
            self._start_monitoring()
            
            self.logger.info(f"Thread pool started with {self.max_workers} max workers")
            
        except Exception as e:
            self.logger.error(f"Failed to start thread pool: {e}")
    
    def stop(self, wait: bool = True, timeout: Optional[float] = None):
        """Thread pool'u durdur"""
        try:
            if not self.running:
                return
            
            self.running = False
            
            # Monitoring'i durdur
            self._stop_monitoring()
            
            # Executor'ı kapat
            if self.executor:
                self.executor.shutdown(wait=wait, timeout=timeout)
                self.executor = None
            
            # İstatistikleri güncelle
            if self.start_time:
                self.stats.total_uptime = time.time() - self.start_time
            
            self.logger.info("Thread pool stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop thread pool: {e}")
    
    def submit(self, function: Callable, *args, **kwargs) -> Optional[str]:
        """Thread pool'a görev gönder"""
        try:
            if not self.running or not self.executor:
                self.logger.warning("Thread pool not running")
                return None
            
            # Backpressure kontrolü
            if self.backpressure_enabled and len(self.active_futures) >= self.task_limit:
                self.logger.warning("Thread pool at capacity, rejecting task")
                return None
            
            # Görevi gönder
            task_id = str(uuid.uuid4())
            future = self.executor.submit(self._execute_with_tracking, function, task_id, *args, **kwargs)
            
            # Takip listesine ekle
            self.active_futures[task_id] = future
            
            self.logger.debug(f"Task submitted: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {e}")
            return None
    
    def submit_batch(self, tasks: List[tuple]) -> List[str]:
        """Toplu görev gönderimi"""
        try:
            task_ids = []
            
            for task in tasks:
                if len(task) >= 1:
                    function = task[0]
                    args = task[1:] if len(task) > 1 else ()
                    task_id = self.submit(function, *args)
                    if task_id:
                        task_ids.append(task_id)
            
            self.logger.info(f"Batch submitted: {len(task_ids)} tasks")
            return task_ids
            
        except Exception as e:
            self.logger.error(f"Failed to submit batch: {e}")
            return []
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Görev sonucunu al"""
        try:
            # Önce cache'den kontrol et
            if task_id in self.task_results:
                return self.task_results[task_id]
            
            # Future'dan al
            if task_id in self.active_futures:
                future = self.active_futures[task_id]
                result = future.result(timeout=timeout)
                
                # Cache'e ekle
                self.task_results[task_id] = result
                
                return result
            
            return None
            
        except concurrent.futures.TimeoutError:
            self.logger.warning(f"Task {task_id} timed out")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get result for task {task_id}: {e}")
            return None
    
    def wait_for_completion(self, task_ids: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        """Birden fazla görevin tamamlanmasını bekle"""
        try:
            results = {}
            futures_to_wait = {}
            
            # Future'ları topla
            for task_id in task_ids:
                if task_id in self.active_futures:
                    futures_to_wait[self.active_futures[task_id]] = task_id
            
            # Tamamlanmasını bekle
            completed_futures = concurrent.futures.as_completed(futures_to_wait.keys(), timeout=timeout)
            
            for future in completed_futures:
                task_id = futures_to_wait[future]
                try:
                    result = future.result()
                    results[task_id] = result
                    self.task_results[task_id] = result
                except Exception as e:
                    results[task_id] = {"error": str(e)}
                    self.logger.error(f"Task {task_id} failed: {e}")
            
            return results
            
        except concurrent.futures.TimeoutError:
            self.logger.warning("Wait for completion timed out")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to wait for completion: {e}")
            return {}
    
    def _execute_with_tracking(self, function: Callable, task_id: str, *args, **kwargs):
        """Takip ile görev çalıştır"""
        start_time = time.time()
        
        try:
            # Aktif thread sayısını artır
            with self.stats_lock:
                self.stats.active_threads += 1
                if self.stats.active_threads > self.stats.peak_threads:
                    self.stats.peak_threads = self.stats.active_threads
            
            # Fonksiyonu çalıştır
            result = function(*args, **kwargs)
            
            # Başarılı tamamlama
            execution_time = time.time() - start_time
            
            with self.stats_lock:
                self.stats.completed_tasks += 1
                self.task_completion_times.append(execution_time)
                self._update_average_task_time()
            
            return result
            
        except Exception as e:
            # Hata durumu
            with self.stats_lock:
                self.stats.failed_tasks += 1
            
            self.logger.error(f"Task {task_id} failed: {e}")
            raise
            
        finally:
            # Aktif thread sayısını azalt
            with self.stats_lock:
                self.stats.active_threads = max(0, self.stats.active_threads - 1)
            
            # Future'ı temizle
            if task_id in self.active_futures:
                del self.active_futures[task_id]
    
    def _update_average_task_time(self):
        """Ortalama görev süresini güncelle"""
        try:
            if self.task_completion_times:
                # Son 1000 görevin ortalamasını al
                recent_times = self.task_completion_times[-1000:]
                self.stats.average_task_time = sum(recent_times) / len(recent_times)
                
        except Exception as e:
            self.logger.debug(f"Failed to update average task time: {e}")
    
    def _start_monitoring(self):
        """Pool monitoring'ini başlat"""
        try:
            self.monitor_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                name="ThreadPoolMonitor",
                daemon=True
            )
            self.monitor_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def _stop_monitoring(self):
        """Pool monitoring'ini durdur"""
        try:
            self.monitor_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
                
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def _monitor_loop(self):
        """Monitoring ana döngüsü"""
        while self.monitor_active and self.running:
            try:
                self._update_pool_stats()
                self._cleanup_completed_tasks()
                time.sleep(10)  # 10 saniyede bir kontrol
                
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(5)
    
    def _update_pool_stats(self):
        """Pool istatistiklerini güncelle"""
        try:
            with self.stats_lock:
                # İdeal thread sayısı
                total_threads = len(threading.enumerate())
                self.stats.idle_threads = max(0, self.max_workers - self.stats.active_threads)
                
            # Sistem kaynak kullanımı
            if hasattr(psutil, 'cpu_percent'):
                cpu_usage = psutil.cpu_percent(interval=0.1)
                if cpu_usage > 80:  # CPU yoğunluğu kontrolü
                    self.logger.debug(f"High CPU usage detected: {cpu_usage}%")
                    
        except Exception as e:
            self.logger.debug(f"Failed to update pool stats: {e}")
    
    def _cleanup_completed_tasks(self):
        """Tamamlanmış görevleri temizle"""
        try:
            # Eski task sonuçlarını temizle (1000'den fazla varsa)
            if len(self.task_results) > 1000:
                # En eskilerini sil
                items = list(self.task_results.items())
                self.task_results = dict(items[-500:])  # Son 500'ü koru
                
            # Tamamlanmış future'ları temizle
            completed_tasks = []
            for task_id, future in self.active_futures.items():
                if future.done():
                    completed_tasks.append(task_id)
            
            for task_id in completed_tasks:
                del self.active_futures[task_id]
                
        except Exception as e:
            self.logger.debug(f"Failed to cleanup completed tasks: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Pool istatistiklerini al"""
        with self.stats_lock:
            uptime = time.time() - self.start_time if self.start_time else 0
            
            return {
                "max_workers": self.max_workers,
                "active_threads": self.stats.active_threads,
                "idle_threads": self.stats.idle_threads,
                "completed_tasks": self.stats.completed_tasks,
                "failed_tasks": self.stats.failed_tasks,
                "average_task_time": self.stats.average_task_time,
                "peak_threads": self.stats.peak_threads,
                "pending_tasks": len(self.active_futures),
                "cached_results": len(self.task_results),
                "uptime_seconds": uptime,
                "running": self.running
            }
    
    def resize_pool(self, new_max_workers: int):
        """Pool boyutunu değiştir (dinamik)"""
        try:
            if not self.running:
                self.max_workers = new_max_workers
                return
            
            # Yeni executor oluştur
            old_executor = self.executor
            
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=new_max_workers,
                thread_name_prefix="PyCloudPool"
            )
            
            self.max_workers = new_max_workers
            
            # Eski executor'ı kapat
            if old_executor:
                old_executor.shutdown(wait=False)
            
            self.logger.info(f"Thread pool resized to {new_max_workers} workers")
            
        except Exception as e:
            self.logger.error(f"Failed to resize pool: {e}")
    
    def force_cleanup(self):
        """Zorla temizlik yap"""
        try:
            # Tüm tamamlanmış task'ları temizle
            self.task_results.clear()
            
            # Tamamlanmış future'ları temizle
            completed_tasks = []
            for task_id, future in self.active_futures.items():
                if future.done():
                    completed_tasks.append(task_id)
            
            for task_id in completed_tasks:
                del self.active_futures[task_id]
            
            # İstatistikleri sıfırla
            with self.stats_lock:
                self.task_completion_times = self.task_completion_times[-100:]  # Son 100'ü koru
            
            self.logger.info("Force cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to force cleanup: {e}") 