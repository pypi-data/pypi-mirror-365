"""
PyCloud OS Event Bus
Sistem modülleri ve uygulamalar arasında olay tabanlı iletişim
"""

import logging
import threading
import queue
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from enum import Enum

class EventPriority(Enum):
    """Olay öncelik seviyeleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class Event:
    """Sistem olayı"""
    
    def __init__(self, event_type: str, data: Dict = None, 
                 priority: EventPriority = EventPriority.NORMAL,
                 source: str = None):
        self.event_type = event_type
        self.data = data or {}
        self.priority = priority
        self.source = source
        self.timestamp = datetime.now()
        self.handled = False
    
    def __str__(self):
        return f"Event({self.event_type}, {self.source}, {self.priority.name})"

class EventBus:
    """Olay yöneticisi - Pub/Sub modeli"""
    
    def __init__(self):
        self.logger = logging.getLogger("Events")
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = queue.PriorityQueue()
        self.running = False
        self.worker_thread = None
        self.event_history: List[Event] = []
        self.max_history = 1000
        self._lock = threading.Lock()
        
        # İstatistikler
        self.stats = {
            "events_published": 0,
            "events_handled": 0,
            "subscribers_count": 0
        }
    
    def start(self):
        """Event bus'ı başlat"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._event_worker, daemon=True)
        self.worker_thread.start()
        self.logger.info("Event bus started")
    
    def stop(self):
        """Event bus'ı durdur"""
        if not self.running:
            return
        
        self.running = False
        
        # Boş event ekleyerek worker thread'i uyandır
        self.event_queue.put((0, Event("__SHUTDOWN__")))
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
        
        self.logger.info("Event bus stopped")
    
    def subscribe(self, event_type: str, callback: Callable):
        """Olaya abone ol"""
        with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            if callback not in self.subscribers[event_type]:
                self.subscribers[event_type].append(callback)
                self.stats["subscribers_count"] += 1
                self.logger.debug(f"Subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Abonelikten çık"""
        with self._lock:
            if event_type in self.subscribers:
                if callback in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(callback)
                    self.stats["subscribers_count"] -= 1
                    self.logger.debug(f"Unsubscribed from {event_type}")
                
                # Boş liste ise sil
                if not self.subscribers[event_type]:
                    del self.subscribers[event_type]
    
    def publish(self, event_type: str, data: Dict = None, 
                priority: EventPriority = EventPriority.NORMAL,
                source: str = None):
        """Olay yayınla"""
        event = Event(event_type, data, priority, source)
        
        # Önceliği tersine çevir (queue düşük sayıyı öncelikli görür)
        priority_value = 5 - priority.value
        
        self.event_queue.put((priority_value, event))
        self.stats["events_published"] += 1
        
        self.logger.debug(f"Published event: {event}")
    
    def publish_sync(self, event_type: str, data: Dict = None, source: str = None):
        """Senkron olay yayınla (anında işle)"""
        event = Event(event_type, data, EventPriority.CRITICAL, source)
        self._handle_event(event)
    
    def _event_worker(self):
        """Olay işleyici worker thread"""
        while self.running:
            try:
                # Timeout ile event bekle
                priority, event = self.event_queue.get(timeout=1.0)
                
                # Shutdown eventi
                if event.event_type == "__SHUTDOWN__":
                    break
                
                self._handle_event(event)
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Event worker error: {e}")
    
    def _handle_event(self, event: Event):
        """Olayı işle"""
        try:
            # Geçmişe ekle
            self._add_to_history(event)
            
            # Aboneleri bul
            subscribers = []
            with self._lock:
                subscribers = self.subscribers.get(event.event_type, []).copy()
            
            # Aboneleri bilgilendir
            for callback in subscribers:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Event handler error: {e}")
            
            event.handled = True
            self.stats["events_handled"] += 1
            
            self.logger.debug(f"Handled event: {event} ({len(subscribers)} subscribers)")
            
        except Exception as e:
            self.logger.error(f"Failed to handle event {event}: {e}")
    
    def _add_to_history(self, event: Event):
        """Olayı geçmişe ekle"""
        self.event_history.append(event)
        
        # Geçmiş boyutunu sınırla
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
    
    def get_subscribers(self, event_type: str = None) -> Dict:
        """Aboneleri listele"""
        with self._lock:
            if event_type:
                return {event_type: len(self.subscribers.get(event_type, []))}
            else:
                return {et: len(subs) for et, subs in self.subscribers.items()}
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """Olay geçmişini al"""
        if event_type:
            filtered = [e for e in self.event_history if e.event_type == event_type]
            return filtered[-limit:]
        else:
            return self.event_history[-limit:]
    
    def get_stats(self) -> Dict:
        """İstatistikleri al"""
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "history_size": len(self.event_history),
            "event_types": list(self.subscribers.keys())
        }
    
    def clear_history(self):
        """Geçmişi temizle"""
        self.event_history.clear()
        self.logger.info("Event history cleared")
    
    def shutdown(self):
        """Modül kapatma"""
        self.stop()

# Sistem olayları için sabitler
class SystemEvents:
    """Sistem olay türleri"""
    
    # Kernel olayları
    SYSTEM_BOOT = "system.boot"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_RESTART = "system.restart"
    
    # Kullanıcı olayları
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_SWITCH = "user.switch"
    
    # Uygulama olayları
    APP_LAUNCH = "app.launch"
    APP_CLOSE = "app.close"
    APP_INSTALL = "app.install"
    APP_UNINSTALL = "app.uninstall"
    
    # UI olayları
    THEME_CHANGE = "ui.theme_change"
    WALLPAPER_CHANGE = "ui.wallpaper_change"
    DOCK_UPDATE = "ui.dock_update"
    
    # Dosya sistemi olayları
    FILE_CREATE = "fs.file_create"
    FILE_DELETE = "fs.file_delete"
    FILE_MODIFY = "fs.file_modify"
    FILE_MOVE = "fs.file_move"
    
    # Güvenlik olayları
    SECURITY_ALERT = "security.alert"
    LOGIN_ATTEMPT = "security.login_attempt"
    PERMISSION_DENIED = "security.permission_denied"
    
    # Bildirim olayları
    NOTIFICATION_SHOW = "notification.show"
    NOTIFICATION_CLICK = "notification.click"
    NOTIFICATION_DISMISS = "notification.dismiss"

# Kolaylık fonksiyonları
_global_event_bus: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    """Global event bus'ı al"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
        _global_event_bus.start()
    return _global_event_bus

def publish(event_type: str, data: Dict = None, 
           priority: EventPriority = EventPriority.NORMAL,
           source: str = None):
    """Global event bus'a olay yayınla"""
    get_event_bus().publish(event_type, data, priority, source)

def subscribe(event_type: str, callback: Callable):
    """Global event bus'a abone ol"""
    get_event_bus().subscribe(event_type, callback)

def unsubscribe(event_type: str, callback: Callable):
    """Global event bus'tan abonelikten çık"""
    get_event_bus().unsubscribe(event_type, callback)

# Global events init function
def init_events(kernel=None) -> EventBus:
    """Events system'ı başlat"""
    event_bus = get_event_bus()
    return event_bus 