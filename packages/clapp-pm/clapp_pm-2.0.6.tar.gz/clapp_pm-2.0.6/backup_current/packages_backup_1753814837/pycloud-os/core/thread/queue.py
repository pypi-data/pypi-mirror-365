"""
Core Thread Queue - Thread Kuyruğu Yöneticisi
Zamanlanmış görevleri kontrol altında sırayla yürüten thread kuyruğu
"""

import logging
import threading
import time
import queue
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
import uuid

class TaskPriority(Enum):
    """Görev öncelik seviyeleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    """Görev durumları"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QueueTask:
    """Kuyruk görevi"""
    task_id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3

class ThreadQueue:
    """
    Zamanlanmış görevleri kontrol altında sırayla yürüten thread kuyruğu.
    FIFO yürütme, öncelik bazlı sıraya alma, senkronizasyon kilitleri.
    """
    
    def __init__(self, kernel, max_workers: int = 4):
        self.kernel = kernel
        self.logger = logging.getLogger("ThreadQueue")
        
        # Kuyruk ayarları
        self.max_workers = max_workers
        self.running = False
        
        # Task kuyruğu (öncelik bazlı)
        self.task_queue = queue.PriorityQueue()
        self.pending_tasks: Dict[str, QueueTask] = {}
        self.completed_tasks: Dict[str, QueueTask] = {}
        
        # Worker thread'leri
        self.workers: List[threading.Thread] = []
        self.active_tasks: Dict[str, QueueTask] = {}
        
        # Senkronizasyon
        self.task_lock = threading.RLock()
        self.shutdown_event = threading.Event()
        
        # İstatistikler
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0
        }
        
    def start(self):
        """Kuyruk işlemcisini başlat"""
        try:
            if self.running:
                return
            
            self.running = True
            self.shutdown_event.clear()
            
            # Worker thread'leri başlat
            for i in range(self.max_workers):
                worker = threading.Thread(
                    target=self._worker_loop,
                    name=f"QueueWorker-{i}",
                    daemon=True
                )
                worker.start()
                self.workers.append(worker)
            
            self.logger.info(f"Thread queue started with {self.max_workers} workers")
            
        except Exception as e:
            self.logger.error(f"Failed to start thread queue: {e}")
    
    def stop(self, timeout: int = 10):
        """Kuyruk işlemcisini durdur"""
        try:
            if not self.running:
                return
            
            self.running = False
            self.shutdown_event.set()
            
            # Worker thread'lerin bitmesini bekle
            for worker in self.workers:
                worker.join(timeout=timeout)
            
            self.workers.clear()
            self.logger.info("Thread queue stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop thread queue: {e}")
    
    def add_task(self, name: str, function: Callable, *args, 
                 priority: TaskPriority = TaskPriority.NORMAL,
                 max_retries: int = 3, **kwargs) -> str:
        """Kuyruğa görev ekle"""
        try:
            task_id = str(uuid.uuid4())
            
            task = QueueTask(
                task_id=task_id,
                name=name,
                function=function,
                args=args,
                kwargs=kwargs,
                priority=priority,
                max_retries=max_retries
            )
            
            with self.task_lock:
                self.pending_tasks[task_id] = task
                # Öncelik bazlı sıralama (yüksek öncelik = düşük sayı)
                priority_value = 5 - priority.value
                self.task_queue.put((priority_value, time.time(), task_id))
                self.stats["total_tasks"] += 1
            
            self.logger.debug(f"Task added to queue: {name} (ID: {task_id})")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to add task {name}: {e}")
            return ""
    
    def cancel_task(self, task_id: str) -> bool:
        """Görevi iptal et"""
        try:
            with self.task_lock:
                if task_id in self.pending_tasks:
                    task = self.pending_tasks[task_id]
                    task.status = TaskStatus.CANCELLED
                    del self.pending_tasks[task_id]
                    self.completed_tasks[task_id] = task
                    self.logger.info(f"Task cancelled: {task.name}")
                    return True
                
                if task_id in self.active_tasks:
                    # Aktif task'i iptal etmek daha karmaşık
                    task = self.active_tasks[task_id]
                    task.status = TaskStatus.CANCELLED
                    self.logger.warning(f"Active task marked for cancellation: {task.name}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Görev durumunu al"""
        try:
            with self.task_lock:
                if task_id in self.pending_tasks:
                    return self.pending_tasks[task_id].status
                if task_id in self.active_tasks:
                    return self.active_tasks[task_id].status
                if task_id in self.completed_tasks:
                    return self.completed_tasks[task_id].status
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get task status {task_id}: {e}")
            return None
    
    def get_task_result(self, task_id: str) -> Any:
        """Görev sonucunu al"""
        try:
            with self.task_lock:
                if task_id in self.completed_tasks:
                    task = self.completed_tasks[task_id]
                    if task.status == TaskStatus.COMPLETED:
                        return task.result
                    elif task.status == TaskStatus.FAILED:
                        raise task.error
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get task result {task_id}: {e}")
            return None
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """Görevin tamamlanmasını bekle"""
        try:
            start_time = time.time()
            
            while True:
                status = self.get_task_status(task_id)
                if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    return True
                
                if timeout and (time.time() - start_time) > timeout:
                    return False
                
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Failed to wait for task {task_id}: {e}")
            return False
    
    def _worker_loop(self):
        """Worker thread ana döngüsü"""
        worker_name = threading.current_thread().name
        self.logger.debug(f"Worker started: {worker_name}")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Kuyruktan görev al (1 saniye timeout)
                try:
                    priority, timestamp, task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Task'i al ve çalıştır
                task = None
                with self.task_lock:
                    if task_id in self.pending_tasks:
                        task = self.pending_tasks[task_id]
                        del self.pending_tasks[task_id]
                        self.active_tasks[task_id] = task
                        task.status = TaskStatus.RUNNING
                        task.started_at = datetime.now()
                
                if task:
                    self._execute_task(task)
                    
                    # Task'i tamamlanmış listesine taşı
                    with self.task_lock:
                        if task_id in self.active_tasks:
                            del self.active_tasks[task_id]
                        self.completed_tasks[task_id] = task
                        task.completed_at = datetime.now()
                        
                        # İstatistik güncelle
                        if task.status == TaskStatus.COMPLETED:
                            self.stats["completed_tasks"] += 1
                        elif task.status == TaskStatus.FAILED:
                            self.stats["failed_tasks"] += 1
                        
                        # Ortalama çalışma süresi
                        if task.started_at and task.completed_at:
                            duration = (task.completed_at - task.started_at).total_seconds()
                            self._update_average_execution_time(duration)
                
                # Kuyruk görev işaretini tamamla
                self.task_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Worker error in {worker_name}: {e}")
                time.sleep(1)
        
        self.logger.debug(f"Worker stopped: {worker_name}")
    
    def _execute_task(self, task: QueueTask):
        """Görevi çalıştır"""
        try:
            self.logger.debug(f"Executing task: {task.name}")
            
            # Fonksiyonu çalıştır
            result = task.function(*task.args, **task.kwargs)
            
            # Sonucu kaydet
            task.result = result
            task.status = TaskStatus.COMPLETED
            
            self.logger.debug(f"Task completed: {task.name}")
            
        except Exception as e:
            self.logger.error(f"Task failed: {task.name} - {e}")
            
            task.error = e
            task.retry_count += 1
            
            # Retry logic
            if task.retry_count <= task.max_retries:
                self.logger.info(f"Retrying task: {task.name} (attempt {task.retry_count})")
                
                # Task'i tekrar kuyruğa ekle
                with self.task_lock:
                    task.status = TaskStatus.PENDING
                    self.pending_tasks[task.task_id] = task
                    priority_value = 5 - task.priority.value
                    self.task_queue.put((priority_value, time.time(), task.task_id))
            else:
                task.status = TaskStatus.FAILED
                self.logger.error(f"Task failed after {task.max_retries} retries: {task.name}")
    
    def _update_average_execution_time(self, duration: float):
        """Ortalama çalışma süresini güncelle"""
        try:
            completed = self.stats["completed_tasks"]
            if completed > 0:
                current_avg = self.stats["average_execution_time"]
                new_avg = ((current_avg * (completed - 1)) + duration) / completed
                self.stats["average_execution_time"] = new_avg
                
        except Exception as e:
            self.logger.debug(f"Failed to update average execution time: {e}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Kuyruk istatistiklerini al"""
        with self.task_lock:
            pending_count = len(self.pending_tasks)
            active_count = len(self.active_tasks)
            completed_count = len(self.completed_tasks)
        
        return {
            "pending_tasks": pending_count,
            "active_tasks": active_count,
            "completed_tasks": completed_count,
            "workers": len(self.workers),
            "running": self.running,
            **self.stats
        }
    
    def clear_completed_tasks(self, keep_recent: int = 100):
        """Tamamlanmış görevleri temizle"""
        try:
            with self.task_lock:
                if len(self.completed_tasks) > keep_recent:
                    # Son N görevi koru, eskilerini sil
                    sorted_tasks = sorted(
                        self.completed_tasks.items(),
                        key=lambda x: x[1].completed_at or datetime.min,
                        reverse=True
                    )
                    
                    tasks_to_keep = dict(sorted_tasks[:keep_recent])
                    removed_count = len(self.completed_tasks) - len(tasks_to_keep)
                    
                    self.completed_tasks = tasks_to_keep
                    self.logger.info(f"Cleared {removed_count} old completed tasks")
                    
        except Exception as e:
            self.logger.error(f"Failed to clear completed tasks: {e}") 