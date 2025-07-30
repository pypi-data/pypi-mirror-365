"""
PyCloud OS Notification Manager
PyCloud OS sisteminde kullanıcıya toast-style anlık bildirim sunan sistem modülü
"""

import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QFrame, QGraphicsOpacityEffect,
                                QApplication)
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
    from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class NotificationType(Enum):
    """Bildirim türleri"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"
    APP = "app"
    SECURITY = "security"
    UPDATE = "update"

class NotificationPriority(Enum):
    """Bildirim öncelikleri"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class NotificationData:
    """Bildirim veri sınıfı"""
    id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    timestamp: str
    source: str = "system"
    icon: str = "ℹ️"
    actions: List[Dict] = None
    persistent: bool = False
    sound: bool = True
    auto_dismiss: bool = True
    dismiss_delay: float = 5.0
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['notification_type'] = self.notification_type.value
        data['priority'] = self.priority.value
        return data

class NotificationToast(QWidget):
    """Toast bildirim widget'ı"""
    
    # Sinyaller
    dismissed = pyqtSignal(str)  # notification_id
    action_clicked = pyqtSignal(str, str)  # notification_id, action_id
    
    def __init__(self, notification: NotificationData):
        super().__init__()
        self.notification = notification
        self.logger = logging.getLogger("NotificationToast")
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()
        self.setup_animations()
        
        # Otomatik kapanma
        if notification.auto_dismiss and not notification.persistent:
            QTimer.singleShot(int(notification.dismiss_delay * 1000), self.dismiss)
    
    def setup_ui(self):
        """Arayüzü kur"""
        self.setFixedSize(350, 100)
        
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toast container
        self.toast_frame = QFrame()
        self.toast_frame.setStyleSheet(self._get_toast_style())
        
        # İçerik layout
        content_layout = QHBoxLayout(self.toast_frame)
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(10)
        
        # İkon
        icon_label = QLabel(self.notification.icon)
        icon_label.setFont(QFont("Arial", 20))
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(icon_label)
        
        # Metin alanı
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # Başlık
        title_label = QLabel(self.notification.title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        text_layout.addWidget(title_label)
        
        # Mesaj
        message_label = QLabel(self.notification.message)
        message_label.setFont(QFont("Arial", 10))
        message_label.setStyleSheet("color: #cccccc;")
        message_label.setWordWrap(True)
        text_layout.addWidget(message_label)
        
        content_layout.addLayout(text_layout)
        
        # Kapat butonu
        if not self.notification.persistent:
            close_btn = QPushButton("✕")
            close_btn.setFixedSize(20, 20)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #ffffff;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                }
            """)
            close_btn.clicked.connect(self.dismiss)
            content_layout.addWidget(close_btn)
        
        main_layout.addWidget(self.toast_frame)
        
        # Aksiyon butonları
        if self.notification.actions:
            self._add_action_buttons(main_layout)
    
    def _get_toast_style(self) -> str:
        """Toast stilini al"""
        # Türe göre renk
        colors = {
            NotificationType.INFO: "#2196F3",
            NotificationType.SUCCESS: "#4CAF50",
            NotificationType.WARNING: "#FF9800",
            NotificationType.ERROR: "#F44336",
            NotificationType.SYSTEM: "#9C27B0",
            NotificationType.APP: "#00BCD4",
            NotificationType.SECURITY: "#FF5722",
            NotificationType.UPDATE: "#3F51B5"
        }
        
        color = colors.get(self.notification.notification_type, "#2196F3")
        
        return f"""
            QFrame {{
                background-color: rgba(45, 45, 45, 0.95);
                border: 2px solid {color};
                border-radius: 12px;
            }}
        """
    
    def _add_action_buttons(self, layout):
        """Aksiyon butonlarını ekle"""
        if not self.notification.actions:
            return
        
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(10, 5, 10, 10)
        
        for action in self.notification.actions:
            btn = QPushButton(action.get("title", "Action"))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 6px;
                    color: #ffffff;
                    padding: 5px 15px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            
            action_id = action.get("id", "default")
            btn.clicked.connect(lambda checked, aid=action_id: self._on_action_clicked(aid))
            actions_layout.addWidget(btn)
        
        layout.addWidget(actions_frame)
    
    def _on_action_clicked(self, action_id: str):
        """Aksiyon tıklama"""
        self.action_clicked.emit(self.notification.id, action_id)
        self.dismiss()
    
    def setup_animations(self):
        """Animasyonları kur"""
        # Opacity efekti
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Fade in animasyonu
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Fade out animasyonu
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self.close)
    
    def show_animated(self):
        """Animasyonlu göster"""
        self.show()
        self.fade_in_animation.start()
    
    def dismiss(self):
        """Bildirimi kapat"""
        self.dismissed.emit(self.notification.id)
        self.fade_out_animation.start()

class NotificationManager:
    """Bildirim yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("NotificationManager")
        
        # Bildirim depolama
        self.notifications: Dict[str, NotificationData] = {}
        self.notification_history: List[NotificationData] = []
        self.active_toasts: Dict[str, NotificationToast] = {}
        
        # Ayarlar
        self.max_visible_toasts = 3
        self.max_history_size = 50
        self.toast_position = "top-right"  # top-right, top-left, bottom-right, bottom-left
        self.sounds_enabled = True
        self.animations_enabled = True
        
        # Toast kuyruğu
        self.toast_queue: List[NotificationData] = []
        self.queue_timer = None
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "notification_shown": [],
            "notification_dismissed": [],
            "action_clicked": []
        }
        
        # PyQt6 varsa timer kur
        if PYQT_AVAILABLE:
            self.queue_timer = QTimer()
            self.queue_timer.timeout.connect(self._process_queue)
            self.queue_timer.start(500)  # 500ms
    
    def show_notification(self, title: str, message: str, 
                         notification_type: NotificationType = NotificationType.INFO,
                         priority: NotificationPriority = NotificationPriority.NORMAL,
                         source: str = "system", icon: str = None,
                         actions: List[Dict] = None, persistent: bool = False,
                         sound: bool = None, auto_dismiss: bool = True,
                         dismiss_delay: float = 5.0) -> str:
        """Bildirim göster"""
        
        # Bildirim ID oluştur
        notification_id = f"notif_{int(time.time() * 1000)}"
        
        # İkon belirleme
        if icon is None:
            icon_map = {
                NotificationType.INFO: "ℹ️",
                NotificationType.SUCCESS: "✅",
                NotificationType.WARNING: "⚠️",
                NotificationType.ERROR: "❌",
                NotificationType.SYSTEM: "⚙️",
                NotificationType.APP: "📱",
                NotificationType.SECURITY: "🔒",
                NotificationType.UPDATE: "🔄"
            }
            icon = icon_map.get(notification_type, "ℹ️")
        
        # Ses ayarı
        if sound is None:
            sound = self.sounds_enabled
        
        # Bildirim oluştur
        notification = NotificationData(
            id=notification_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            timestamp=datetime.now().isoformat(),
            source=source,
            icon=icon,
            actions=actions or [],
            persistent=persistent,
            sound=sound,
            auto_dismiss=auto_dismiss,
            dismiss_delay=dismiss_delay
        )
        
        # Kaydet
        self.notifications[notification_id] = notification
        self.notification_history.append(notification)
        
        # Geçmiş boyutunu kontrol et
        if len(self.notification_history) > self.max_history_size:
            self.notification_history = self.notification_history[-self.max_history_size:]
        
        # Kuyruğa ekle
        self.toast_queue.append(notification)
        
        self.logger.info(f"Notification queued: {title}")
        return notification_id
    
    def _process_queue(self):
        """Toast kuyruğunu işle"""
        if not PYQT_AVAILABLE:
            return
        
        # Maksimum toast sayısını kontrol et
        if len(self.active_toasts) >= self.max_visible_toasts:
            return
        
        # Kuyruktan al
        if not self.toast_queue:
            return
        
        # Önceliğe göre sırala
        self.toast_queue.sort(key=lambda n: self._get_priority_value(n.priority), reverse=True)
        
        notification = self.toast_queue.pop(0)
        self._show_toast(notification)
    
    def _get_priority_value(self, priority: NotificationPriority) -> int:
        """Öncelik değeri al"""
        values = {
            NotificationPriority.LOW: 1,
            NotificationPriority.NORMAL: 2,
            NotificationPriority.HIGH: 3,
            NotificationPriority.URGENT: 4
        }
        return values.get(priority, 2)
    
    def _show_toast(self, notification: NotificationData):
        """Toast göster"""
        if not PYQT_AVAILABLE:
            self.logger.warning("PyQt6 not available, cannot show toast")
            return
        
        try:
            # Toast oluştur
            toast = NotificationToast(notification)
            
            # Sinyalleri bağla
            toast.dismissed.connect(self._on_toast_dismissed)
            toast.action_clicked.connect(self._on_action_clicked)
            
            # Pozisyon hesapla
            self._position_toast(toast)
            
            # Göster
            toast.show_animated()
            
            # Aktif toast'lara ekle
            self.active_toasts[notification.id] = toast
            
            # Ses çal
            if notification.sound and self.sounds_enabled:
                self._play_notification_sound(notification.notification_type)
            
            # Callback tetikle
            self._trigger_callback("notification_shown", notification.to_dict())
            
            self.logger.info(f"Toast shown: {notification.title}")
            
        except Exception as e:
            self.logger.error(f"Failed to show toast: {e}")
    
    def _position_toast(self, toast: NotificationToast):
        """Toast pozisyonunu ayarla"""
        if not QApplication.instance():
            return
        
        screen = QApplication.primaryScreen()
        if not screen:
            return
        
        screen_geometry = screen.availableGeometry()
        toast_size = toast.size()
        
        # Mevcut toast'ların sayısını hesapla
        toast_index = len(self.active_toasts)
        spacing = 10
        
        if self.toast_position == "top-right":
            x = screen_geometry.width() - toast_size.width() - 20
            y = 20 + (toast_index * (toast_size.height() + spacing))
        elif self.toast_position == "top-left":
            x = 20
            y = 20 + (toast_index * (toast_size.height() + spacing))
        elif self.toast_position == "bottom-right":
            x = screen_geometry.width() - toast_size.width() - 20
            y = screen_geometry.height() - toast_size.height() - 20 - (toast_index * (toast_size.height() + spacing))
        elif self.toast_position == "bottom-left":
            x = 20
            y = screen_geometry.height() - toast_size.height() - 20 - (toast_index * (toast_size.height() + spacing))
        else:
            x = screen_geometry.width() - toast_size.width() - 20
            y = 20 + (toast_index * (toast_size.height() + spacing))
        
        toast.move(x, y)
    
    def _play_notification_sound(self, notification_type: NotificationType):
        """Bildirim sesi çal"""
        # TODO: Gerçek ses çalma implementasyonu
        self.logger.debug(f"Playing sound for {notification_type.value}")
    
    def _on_toast_dismissed(self, notification_id: str):
        """Toast kapatma olayı"""
        if notification_id in self.active_toasts:
            del self.active_toasts[notification_id]
            
            # Callback tetikle
            if notification_id in self.notifications:
                notification = self.notifications[notification_id]
                self._trigger_callback("notification_dismissed", notification.to_dict())
            
            self.logger.debug(f"Toast dismissed: {notification_id}")
    
    def _on_action_clicked(self, notification_id: str, action_id: str):
        """Aksiyon tıklama olayı"""
        self.logger.info(f"Action clicked: {action_id} on notification {notification_id}")
        
        # Callback tetikle
        if notification_id in self.notifications:
            notification = self.notifications[notification_id]
            self._trigger_callback("action_clicked", {
                "notification": notification.to_dict(),
                "action_id": action_id
            })
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """Bildirimi kapat"""
        if notification_id in self.active_toasts:
            toast = self.active_toasts[notification_id]
            toast.dismiss()
            return True
        return False
    
    def dismiss_all_notifications(self):
        """Tüm bildirimleri kapat"""
        for notification_id in list(self.active_toasts.keys()):
            self.dismiss_notification(notification_id)
    
    def get_notification_history(self, limit: int = None) -> List[Dict]:
        """Bildirim geçmişini al"""
        history = self.notification_history
        if limit:
            history = history[-limit:]
        
        return [notification.to_dict() for notification in history]
    
    def clear_notification_history(self):
        """Bildirim geçmişini temizle"""
        self.notification_history.clear()
        self.logger.info("Notification history cleared")
    
    def get_active_notifications(self) -> List[Dict]:
        """Aktif bildirimleri al"""
        return [self.notifications[nid].to_dict() for nid in self.active_toasts.keys()]
    
    def set_settings(self, max_visible_toasts: int = None, sounds_enabled: bool = None,
                    animations_enabled: bool = None, toast_position: str = None):
        """Bildirim ayarlarını değiştir"""
        if max_visible_toasts is not None:
            self.max_visible_toasts = max_visible_toasts
        
        if sounds_enabled is not None:
            self.sounds_enabled = sounds_enabled
        
        if animations_enabled is not None:
            self.animations_enabled = animations_enabled
        
        if toast_position is not None:
            self.toast_position = toast_position
        
        self.logger.info("Notification settings updated")
    
    def add_callback(self, event_type: str, callback: Callable):
        """Callback ekle"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: str, callback: Callable):
        """Callback kaldır"""
        if event_type in self.callbacks:
            if callback in self.callbacks[event_type]:
                self.callbacks[event_type].remove(callback)
    
    def _trigger_callback(self, event_type: str, data: Any):
        """Callback tetikle"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Notification callback error for {event_type}: {e}")
    
    def get_notification_stats(self) -> Dict:
        """Bildirim istatistikleri"""
        try:
            # Türe göre sayım
            type_counts = {}
            for notification in self.notification_history:
                ntype = notification.notification_type.value
                type_counts[ntype] = type_counts.get(ntype, 0) + 1
            
            # Kaynak göre sayım
            source_counts = {}
            for notification in self.notification_history:
                source = notification.source
                source_counts[source] = source_counts.get(source, 0) + 1
            
            return {
                "total_notifications": len(self.notification_history),
                "active_notifications": len(self.active_toasts),
                "queued_notifications": len(self.toast_queue),
                "type_counts": type_counts,
                "source_counts": source_counts,
                "settings": {
                    "max_visible_toasts": self.max_visible_toasts,
                    "sounds_enabled": self.sounds_enabled,
                    "animations_enabled": self.animations_enabled,
                    "toast_position": self.toast_position
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate notification stats: {e}")
            return {}
    
    def shutdown(self):
        """Modül kapatma"""
        self.logger.info("Shutting down notification manager...")
        
        # Timer'ı durdur
        if self.queue_timer:
            self.queue_timer.stop()
        
        # Tüm toast'ları kapat
        self.dismiss_all_notifications()
        
        # Kuyruğu temizle
        self.toast_queue.clear()
        
        self.logger.info("Notification manager shutdown completed")

# Kolaylık fonksiyonları
_notification_manager = None

def init_notifications(kernel=None):
    """Bildirim sistemini başlat"""
    global _notification_manager
    _notification_manager = NotificationManager(kernel)
    return _notification_manager

def show_info(title: str, message: str, **kwargs) -> str:
    """Bilgi bildirimi göster"""
    if _notification_manager:
        return _notification_manager.show_notification(
            title, message, NotificationType.INFO, **kwargs
        )
    return ""

def show_success(title: str, message: str, **kwargs) -> str:
    """Başarı bildirimi göster"""
    if _notification_manager:
        return _notification_manager.show_notification(
            title, message, NotificationType.SUCCESS, **kwargs
        )
    return ""

def show_warning(title: str, message: str, **kwargs) -> str:
    """Uyarı bildirimi göster"""
    if _notification_manager:
        return _notification_manager.show_notification(
            title, message, NotificationType.WARNING, **kwargs
        )
    return ""

def show_error(title: str, message: str, **kwargs) -> str:
    """Hata bildirimi göster"""
    if _notification_manager:
        return _notification_manager.show_notification(
            title, message, NotificationType.ERROR, **kwargs
        )
    return ""

def get_notification_manager() -> Optional[NotificationManager]:
    """Bildirim yöneticisini al"""
    return _notification_manager 