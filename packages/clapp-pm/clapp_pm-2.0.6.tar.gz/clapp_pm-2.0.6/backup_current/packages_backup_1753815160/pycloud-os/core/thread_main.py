"""
PyCloud OS Thread Manager
Tüm sistem ve uygulamalar için güvenli, izlenebilir ve esnek thread yürütme altyapısı
"""

import os
import time
import uuid
import pickle
import logging
import threading
import queue
import weakref
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future

class ThreadStatus(Enum):
    """Thread durumları"""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    CRASHED = "crashed"
    FROZEN = "frozen"
    CANCELLED = "cancelled"

class ThreadPriority(Enum):
    """Thread öncelikleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class ThreadType(Enum):
    """Thread türleri"""
    SYSTEM = "system"
    APPLICATION = "application"
    SERVICE = "service"
    USER = "user"
    BACKGROUND = "background"

@dataclass
class ThreadInfo:
    """Thread bilgi sınıfı"""
    tid: str  # Thread ID
    name: str
    thread_type: ThreadType
    priority: ThreadPriority
    status: ThreadStatus
    app_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    runtime_seconds: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['thread_type'] = self.thread_type.value
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data

@dataclass
class ThreadProfile:
    """Thread profil bilgisi"""
    tid: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    function_calls: int
    io_operations: int
    created_objects: int
    peak_memory_mb: float
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        return asdict(self)

@dataclass
class ThreadSnapshot:
    """Thread snapshot bilgisi"""
    tid: str
    timestamp: str
    status: ThreadStatus
    local_vars: Dict[str, Any]
    execution_point: str
    stack_trace: List[str]
    memory_state: bytes
    
    def to_dict(self) -> Dict:
        """Dict'e çevir (memory_state hariç)"""
        data = asdict(self)
        data['status'] = self.status.value
        data.pop('memory_state', None)  # Binary veri çıkar
        return data

@dataclass
class ThreadMessage:
    """Thread mesaj sınıfı"""
    message_id: str
    from_tid: str
    to_tid: str
    message_type: str
    payload: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    delivered: bool = False

class ThreadQueue:
    """Thread kuyruğu yöneticisi"""
    
    def __init__(self, max_size: int = 1000):
        self.queue = queue.PriorityQueue(maxsize=max_size)
        self.logger = logging.getLogger("ThreadQueue")
        self._lock = threading.Lock()
        self.stats = {
            "tasks_queued": 0,
            "tasks_executed": 0,
            "tasks_failed": 0
        }
    
    def enqueue(self, func: Callable, args: tuple = (), kwargs: dict = None,
                priority: ThreadPriority = ThreadPriority.NORMAL,
                thread_info: ThreadInfo = None) -> str:
        """Görevi kuyruğa ekle"""
        if kwargs is None:
            kwargs = {}
        
        task_id = str(uuid.uuid4())
        
        # Öncelik değerini ters çevir (düşük sayı = yüksek öncelik)
        priority_value = 5 - priority.value
        
        task = {
            "id": task_id,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "thread_info": thread_info,
            "queued_at": time.time()
        }
        
        try:
            self.queue.put((priority_value, task), block=False)
            self.stats["tasks_queued"] += 1
            self.logger.debug(f"Task queued: {task_id}")
            return task_id
        except queue.Full:
            self.logger.error("Thread queue is full")
            return None
    
    def dequeue(self, timeout: float = 1.0) -> Optional[Dict]:
        """Kuyruktan görev al"""
        try:
            priority, task = self.queue.get(timeout=timeout)
            return task
        except queue.Empty:
            return None
    
    def get_stats(self) -> Dict:
        """Kuyruk istatistikleri"""
        return {
            **self.stats,
            "queue_size": self.queue.qsize(),
            "queue_full": self.queue.full()
        }

class ThreadPool:
    """Thread havuzu yöneticisi"""
    
    def __init__(self, max_workers: int = None):
        if max_workers is None:
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger("ThreadPool")
        self.active_futures: Dict[str, Future] = {}
        self.completed_tasks = 0
        self.failed_tasks = 0
        
    def submit(self, func: Callable, *args, **kwargs) -> str:
        """Görevi havuza gönder"""
        task_id = str(uuid.uuid4())
        
        try:
            future = self.executor.submit(func, *args, **kwargs)
            self.active_futures[task_id] = future
            
            # Tamamlanma callback'i
            future.add_done_callback(lambda f: self._on_task_completed(task_id, f))
            
            self.logger.debug(f"Task submitted to pool: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {e}")
            return None
    
    def _on_task_completed(self, task_id: str, future: Future):
        """Görev tamamlanma callback'i"""
        try:
            if future.exception():
                self.failed_tasks += 1
                self.logger.error(f"Task {task_id} failed: {future.exception()}")
            else:
                self.completed_tasks += 1
                self.logger.debug(f"Task {task_id} completed successfully")
        except Exception as e:
            self.logger.error(f"Error in task completion callback: {e}")
        finally:
            # Future'ı temizle
            self.active_futures.pop(task_id, None)
    
    def cancel_task(self, task_id: str) -> bool:
        """Görevi iptal et"""
        future = self.active_futures.get(task_id)
        if future:
            return future.cancel()
        return False
    
    def get_stats(self) -> Dict:
        """Havuz istatistikleri"""
        return {
            "max_workers": self.max_workers,
            "active_tasks": len(self.active_futures),
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks
        }
    
    def shutdown(self, wait: bool = True):
        """Havuzu kapat"""
        self.executor.shutdown(wait=wait)

class ThreadMessaging:
    """Thread'ler arası mesajlaşma sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger("ThreadMessaging")
        self.message_queues: Dict[str, queue.Queue] = {}
        self.message_history: List[ThreadMessage] = []
        self.max_history = 1000
        self._lock = threading.Lock()
        
        # Mesaj filtreleri
        self.message_filters: Dict[str, Callable] = {}
    
    def register_thread(self, tid: str):
        """Thread'i mesajlaşma için kaydet"""
        with self._lock:
            if tid not in self.message_queues:
                self.message_queues[tid] = queue.Queue(maxsize=100)
                self.logger.debug(f"Thread registered for messaging: {tid}")
    
    def unregister_thread(self, tid: str):
        """Thread'i mesajlaşmadan çıkar"""
        with self._lock:
            if tid in self.message_queues:
                del self.message_queues[tid]
                self.logger.debug(f"Thread unregistered from messaging: {tid}")
    
    def send_message(self, from_tid: str, to_tid: str, message_type: str, payload: Any) -> bool:
        """Mesaj gönder"""
        try:
            # Hedef thread kontrolü
            if to_tid not in self.message_queues:
                self.logger.warning(f"Target thread {to_tid} not registered")
                return False
            
            # Mesaj oluştur
            message = ThreadMessage(
                message_id=str(uuid.uuid4()),
                from_tid=from_tid,
                to_tid=to_tid,
                message_type=message_type,
                payload=payload
            )
            
            # Filtre kontrolü
            if not self._check_message_filter(message):
                self.logger.warning(f"Message filtered: {message_type}")
                return False
            
            # Mesajı kuyruğa ekle
            target_queue = self.message_queues[to_tid]
            target_queue.put(message, block=False)
            
            # Geçmişe ekle
            self._add_to_history(message)
            
            self.logger.debug(f"Message sent: {from_tid} -> {to_tid} ({message_type})")
            return True
            
        except queue.Full:
            self.logger.error(f"Message queue full for thread {to_tid}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_message(self, tid: str, timeout: float = 0.1) -> Optional[ThreadMessage]:
        """Mesaj al"""
        try:
            if tid not in self.message_queues:
                return None
            
            message_queue = self.message_queues[tid]
            message = message_queue.get(timeout=timeout)
            message.delivered = True
            
            return message
            
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return None
    
    def _check_message_filter(self, message: ThreadMessage) -> bool:
        """Mesaj filtresi kontrolü"""
        filter_func = self.message_filters.get(message.message_type)
        if filter_func:
            try:
                return filter_func(message)
            except Exception as e:
                self.logger.error(f"Message filter error: {e}")
                return False
        return True
    
    def _add_to_history(self, message: ThreadMessage):
        """Mesajı geçmişe ekle"""
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
    
    def add_message_filter(self, message_type: str, filter_func: Callable):
        """Mesaj filtresi ekle"""
        self.message_filters[message_type] = filter_func
    
    def get_message_history(self, tid: str = None, limit: int = 100) -> List[Dict]:
        """Mesaj geçmişi al"""
        history = self.message_history
        
        if tid:
            history = [m for m in history if m.from_tid == tid or m.to_tid == tid]
        
        return [m.__dict__ for m in history[-limit:]]

class ThreadSnapshot:
    """Thread snapshot yöneticisi"""
    
    def __init__(self):
        self.logger = logging.getLogger("ThreadSnapshot")
        self.snapshots: Dict[str, ThreadSnapshot] = {}
        self.snapshots_dir = Path("temp/thread_snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def create_snapshot(self, tid: str, thread_info: ThreadInfo) -> bool:
        """Thread snapshot oluştur"""
        try:
            # Stack trace al
            import traceback
            stack_trace = traceback.format_stack()
            
            # Local variables (basit implementasyon)
            local_vars = {}
            
            # Memory state (placeholder)
            memory_state = b""
            
            snapshot = ThreadSnapshot(
                tid=tid,
                timestamp=datetime.now().isoformat(),
                status=thread_info.status,
                local_vars=local_vars,
                execution_point=f"Line {len(stack_trace)}",
                stack_trace=stack_trace,
                memory_state=memory_state
            )
            
            # Dosyaya kaydet
            snapshot_file = self.snapshots_dir / f"{tid}_{int(time.time())}.snapshot"
            with open(snapshot_file, 'wb') as f:
                pickle.dump(snapshot, f)
            
            self.snapshots[tid] = snapshot
            self.logger.info(f"Snapshot created for thread {tid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create snapshot for {tid}: {e}")
            return False
    
    def restore_snapshot(self, tid: str) -> Optional[ThreadSnapshot]:
        """Snapshot'ı geri yükle"""
        try:
            if tid in self.snapshots:
                return self.snapshots[tid]
            
            # Dosyadan yükle
            snapshot_files = list(self.snapshots_dir.glob(f"{tid}_*.snapshot"))
            if snapshot_files:
                latest_file = max(snapshot_files, key=lambda f: f.stat().st_mtime)
                
                with open(latest_file, 'rb') as f:
                    snapshot = pickle.load(f)
                
                self.snapshots[tid] = snapshot
                return snapshot
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to restore snapshot for {tid}: {e}")
            return None

class ThreadProfiler:
    """Thread profiling sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger("ThreadProfiler")
        self.profiles: Dict[str, ThreadProfile] = {}
        self.profiling_enabled = True
    
    def start_profiling(self, tid: str):
        """Profiling başlat"""
        if not self.profiling_enabled:
            return
        
        try:
            profile = ThreadProfile(
                tid=tid,
                execution_time=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                function_calls=0,
                io_operations=0,
                created_objects=0,
                peak_memory_mb=0.0
            )
            
            self.profiles[tid] = profile
            self.logger.debug(f"Profiling started for thread {tid}")
            
        except Exception as e:
            self.logger.error(f"Failed to start profiling for {tid}: {e}")
    
    def update_profile(self, tid: str, **metrics):
        """Profil güncelle"""
        if tid in self.profiles:
            profile = self.profiles[tid]
            
            for key, value in metrics.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
    
    def finish_profiling(self, tid: str) -> Optional[ThreadProfile]:
        """Profiling bitir"""
        return self.profiles.pop(tid, None)
    
    def get_profile(self, tid: str) -> Optional[ThreadProfile]:
        """Profil al"""
        return self.profiles.get(tid)

class ThreadManager:
    """Ana thread yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("ThreadManager")
        
        # Thread bilgileri
        self.threads: Dict[str, ThreadInfo] = {}
        self.thread_objects: Dict[str, threading.Thread] = weakref.WeakValueDictionary()
        
        # Alt sistemler
        self.queue = ThreadQueue()
        self.pool = ThreadPool()
        self.messaging = ThreadMessaging()
        self.snapshots = ThreadSnapshot()
        self.profiler = ThreadProfiler()
        
        # Watchdog
        self.watchdog_running = False
        self.watchdog_thread = None
        self.watchdog_interval = 5.0
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "thread_started": [],
            "thread_finished": [],
            "thread_crashed": [],
            "thread_frozen": []
        }
        
        self.start_watchdog()
    
    def create_thread(self, func: Callable, args: tuple = (), kwargs: dict = None,
                     name: str = None, app_id: str = None,
                     thread_type: ThreadType = ThreadType.APPLICATION,
                     priority: ThreadPriority = ThreadPriority.NORMAL,
                     enable_profiling: bool = True,
                     enable_messaging: bool = True) -> str:
        """Yeni thread oluştur"""
        
        if kwargs is None:
            kwargs = {}
        
        # Thread ID oluştur
        tid = str(uuid.uuid4())
        
        if not name:
            name = f"Thread-{tid[:8]}"
        
        # Thread bilgisi oluştur
        thread_info = ThreadInfo(
            tid=tid,
            name=name,
            thread_type=thread_type,
            priority=priority,
            status=ThreadStatus.IDLE,
            app_id=app_id
        )
        
        # Kaydet
        self.threads[tid] = thread_info
        
        # Mesajlaşma kaydı
        if enable_messaging:
            self.messaging.register_thread(tid)
        
        # Profiling başlat
        if enable_profiling:
            self.profiler.start_profiling(tid)
        
        self.logger.info(f"Thread created: {name} ({tid})")
        return tid
    
    def start_thread(self, tid: str, func: Callable, args: tuple = (), kwargs: dict = None) -> bool:
        """Thread'i başlat"""
        if tid not in self.threads:
            self.logger.error(f"Thread {tid} not found")
            return False
        
        if kwargs is None:
            kwargs = {}
        
        thread_info = self.threads[tid]
        
        try:
            # Wrapper fonksiyon
            def thread_wrapper():
                try:
                    # Thread başlangıç
                    thread_info.status = ThreadStatus.RUNNING
                    thread_info.started_at = datetime.now().isoformat()
                    
                    start_time = time.time()
                    
                    # Callback tetikle
                    self._trigger_callback("thread_started", thread_info.to_dict())
                    
                    # Ana fonksiyonu çalıştır
                    result = func(*args, **kwargs)
                    
                    # Thread bitiş
                    end_time = time.time()
                    thread_info.runtime_seconds = end_time - start_time
                    thread_info.status = ThreadStatus.FINISHED
                    thread_info.finished_at = datetime.now().isoformat()
                    
                    # Profiling güncelle
                    self.profiler.update_profile(tid, execution_time=thread_info.runtime_seconds)
                    
                    # Callback tetikle
                    self._trigger_callback("thread_finished", thread_info.to_dict())
                    
                    return result
                    
                except Exception as e:
                    # Hata durumu
                    thread_info.status = ThreadStatus.CRASHED
                    thread_info.error_message = str(e)
                    thread_info.finished_at = datetime.now().isoformat()
                    
                    self.logger.error(f"Thread {tid} crashed: {e}")
                    self._trigger_callback("thread_crashed", thread_info.to_dict())
                    
                finally:
                    # Temizlik
                    self._cleanup_thread(tid)
            
            # Thread oluştur ve başlat
            thread = threading.Thread(target=thread_wrapper, name=thread_info.name)
            thread.daemon = True
            thread.start()
            
            # Referansı sakla
            self.thread_objects[tid] = thread
            
            self.logger.info(f"Thread started: {thread_info.name} ({tid})")
            return True
            
        except Exception as e:
            thread_info.status = ThreadStatus.CRASHED
            thread_info.error_message = str(e)
            self.logger.error(f"Failed to start thread {tid}: {e}")
            return False
    
    def freeze_thread(self, tid: str) -> bool:
        """Thread'i dondur (snapshot al)"""
        if tid not in self.threads:
            return False
        
        thread_info = self.threads[tid]
        
        try:
            # Snapshot oluştur
            if self.snapshots.create_snapshot(tid, thread_info):
                thread_info.status = ThreadStatus.FROZEN
                self._trigger_callback("thread_frozen", thread_info.to_dict())
                self.logger.info(f"Thread frozen: {tid}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to freeze thread {tid}: {e}")
            return False
    
    def kill_thread(self, tid: str) -> bool:
        """Thread'i öldür"""
        if tid not in self.threads:
            return False
        
        thread_info = self.threads[tid]
        
        try:
            # Thread objesini al
            thread = self.thread_objects.get(tid)
            if thread and thread.is_alive():
                # Python'da thread'i zorla öldürmenin güvenli yolu yok
                # Sadece durumu güncelle
                thread_info.status = ThreadStatus.CANCELLED
                thread_info.finished_at = datetime.now().isoformat()
                
                self.logger.warning(f"Thread marked as cancelled: {tid} (Python threads cannot be forcefully killed)")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to kill thread {tid}: {e}")
            return False
    
    def get_thread_info(self, tid: str) -> Optional[ThreadInfo]:
        """Thread bilgisi al"""
        return self.threads.get(tid)
    
    def get_all_threads(self) -> List[ThreadInfo]:
        """Tüm thread'leri al"""
        return list(self.threads.values())
    
    def get_running_threads(self) -> List[ThreadInfo]:
        """Çalışan thread'leri al"""
        return [t for t in self.threads.values() if t.status == ThreadStatus.RUNNING]
    
    def get_app_threads(self, app_id: str) -> List[ThreadInfo]:
        """Uygulama thread'lerini al"""
        return [t for t in self.threads.values() if t.app_id == app_id]
    
    def send_message(self, from_tid: str, to_tid: str, message_type: str, payload: Any) -> bool:
        """Thread'ler arası mesaj gönder"""
        return self.messaging.send_message(from_tid, to_tid, message_type, payload)
    
    def receive_message(self, tid: str, timeout: float = 0.1) -> Optional[ThreadMessage]:
        """Thread mesajı al"""
        return self.messaging.receive_message(tid, timeout)
    
    def start_watchdog(self):
        """Watchdog başlat"""
        if self.watchdog_running:
            return
        
        self.watchdog_running = True
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.watchdog_thread.start()
        self.logger.info("Thread watchdog started")
    
    def stop_watchdog(self):
        """Watchdog durdur"""
        self.watchdog_running = False
        if self.watchdog_thread and self.watchdog_thread.is_alive():
            self.watchdog_thread.join(timeout=2.0)
        self.logger.info("Thread watchdog stopped")
    
    def _watchdog_loop(self):
        """Watchdog döngüsü"""
        while self.watchdog_running:
            try:
                self._check_threads()
                time.sleep(self.watchdog_interval)
            except Exception as e:
                self.logger.error(f"Thread watchdog error: {e}")
                time.sleep(10.0)
    
    def _check_threads(self):
        """Thread'leri kontrol et"""
        for tid, thread_info in self.threads.items():
            try:
                # Thread objesi kontrolü
                thread = self.thread_objects.get(tid)
                
                if thread_info.status == ThreadStatus.RUNNING:
                    if not thread or not thread.is_alive():
                        # Thread öldü ama durumu güncellenmemiş
                        thread_info.status = ThreadStatus.CRASHED
                        thread_info.error_message = "Thread died unexpectedly"
                        thread_info.finished_at = datetime.now().isoformat()
                        
                        self.logger.warning(f"Dead thread detected: {tid}")
                        self._trigger_callback("thread_crashed", thread_info.to_dict())
                
                # Çok uzun süre çalışan thread'ler
                if (thread_info.status == ThreadStatus.RUNNING and 
                    thread_info.started_at):
                    
                    try:
                        started = datetime.fromisoformat(thread_info.started_at)
                        runtime = (datetime.now() - started).total_seconds()
                        
                        if runtime > 3600:  # 1 saat
                            self.logger.warning(f"Long running thread detected: {tid} ({runtime:.1f}s)")
                    except Exception:
                        pass
                        
            except Exception as e:
                self.logger.error(f"Error checking thread {tid}: {e}")
    
    def _cleanup_thread(self, tid: str):
        """Thread temizliği"""
        try:
            # Mesajlaşmadan çıkar
            self.messaging.unregister_thread(tid)
            
            # Profiling bitir
            profile = self.profiler.finish_profiling(tid)
            if profile:
                self.logger.debug(f"Thread profile: {tid} - {profile.execution_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Thread cleanup error for {tid}: {e}")
    
    def _trigger_callback(self, event_type: str, data: Dict):
        """Callback tetikle"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Thread callback error for {event_type}: {e}")
    
    def add_callback(self, event_type: str, callback: Callable):
        """Callback ekle"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def get_thread_stats(self) -> Dict:
        """Thread istatistikleri"""
        try:
            status_counts = {}
            for thread_info in self.threads.values():
                status = thread_info.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            type_counts = {}
            for thread_info in self.threads.values():
                ttype = thread_info.thread_type.value
                type_counts[ttype] = type_counts.get(ttype, 0) + 1
            
            return {
                "total_threads": len(self.threads),
                "status_counts": status_counts,
                "type_counts": type_counts,
                "queue_stats": self.queue.get_stats(),
                "pool_stats": self.pool.get_stats(),
                "active_snapshots": len(self.snapshots.snapshots),
                "active_profiles": len(self.profiler.profiles)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate thread stats: {e}")
            return {}
    
    def shutdown(self):
        """Modül kapatma"""
        self.logger.info("Shutting down thread manager...")
        
        # Watchdog durdur
        self.stop_watchdog()
        
        # Thread pool kapat
        self.pool.shutdown(wait=True)
        
        # Aktif thread'leri iptal et
        for tid in list(self.threads.keys()):
            if self.threads[tid].status == ThreadStatus.RUNNING:
                self.kill_thread(tid)
        
        self.logger.info("Thread manager shutdown completed")

# Kolaylık fonksiyonları
_thread_manager = None

def init_thread_manager(kernel=None):
    """Thread manager'ı başlat"""
    global _thread_manager
    _thread_manager = ThreadManager(kernel)
    return _thread_manager

def create_thread(func: Callable, *args, **kwargs) -> str:
    """Hızlı thread oluştur"""
    if _thread_manager:
        return _thread_manager.create_thread(func, args, kwargs)
    return ""

def start_thread(tid: str, func: Callable, *args, **kwargs) -> bool:
    """Thread başlat"""
    if _thread_manager:
        return _thread_manager.start_thread(tid, func, args, kwargs)
    return False

def get_thread_manager() -> Optional[ThreadManager]:
    """Thread manager'ı al"""
    return _thread_manager 