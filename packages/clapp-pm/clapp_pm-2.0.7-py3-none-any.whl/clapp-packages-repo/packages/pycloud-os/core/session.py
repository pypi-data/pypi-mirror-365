"""
PyCloud OS Core Session
Oturum yönetimi, kullanıcı oturum geçmişi ve timeout sistemi
"""

import os
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class SessionStatus(Enum):
    """Oturum durumları"""
    ACTIVE = "active"
    IDLE = "idle"
    LOCKED = "locked"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class SessionType(Enum):
    """Oturum türleri"""
    LOGIN = "login"
    GUEST = "guest"
    ADMIN = "admin"
    SYSTEM = "system"

@dataclass
class SessionInfo:
    """Oturum bilgisi"""
    session_id: str
    user_id: str
    username: str
    session_type: SessionType
    status: SessionStatus
    start_time: str
    last_activity: str
    ip_address: str = "127.0.0.1"
    user_agent: str = "PyCloud OS"
    idle_timeout: int = 0  # dakika (0 = sınırsız)
    max_duration: int = 0  # dakika (0 = sınırsız)
    auto_lock: bool = False
    lock_timeout: int = 15  # dakika
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['session_type'] = self.session_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SessionInfo':
        """Dict'ten oluştur"""
        data['session_type'] = SessionType(data.get('session_type', 'login'))
        data['status'] = SessionStatus(data.get('status', 'active'))
        return cls(**data)

@dataclass
class SessionActivity:
    """Oturum aktivitesi"""
    session_id: str
    timestamp: str
    activity_type: str
    description: str
    details: Dict = None
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        return asdict(self)

class SessionManager:
    """Ana oturum yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("SessionManager")
        
        # Oturum verileri
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.session_activities: Dict[str, List[SessionActivity]] = {}
        
        # Dosya yolları
        self.session_dir = Path("system/sessions")
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.session_dir / "active_sessions.json"
        self.history_file = self.session_dir / "session_history.json"
        
        # Timeout kontrolü
        self.timeout_thread = None
        self.timeout_interval = 60  # saniye
        self.running = False
        
        # Callback'ler
        self.session_callbacks: Dict[str, List[Callable]] = {
            'session_start': [],
            'session_end': [],
            'session_timeout': [],
            'session_lock': [],
            'session_unlock': [],
            'activity_update': []
        }
        
        # Varsayılan ayarlar
        self.default_idle_timeout = 30  # dakika
        self.default_max_duration = 480  # 8 saat
        self.max_activity_records = 1000
        
        # Başlangıç
        self.load_active_sessions()
        self.start_timeout_monitor()
    
    def generate_session_id(self) -> str:
        """Benzersiz oturum ID'si oluştur"""
        import uuid
        return str(uuid.uuid4())
    
    def create_session(self, user_id: str, username: str, 
                      session_type: SessionType = SessionType.LOGIN,
                      idle_timeout: int = None,
                      max_duration: int = None,
                      auto_lock: bool = False,
                      ip_address: str = "127.0.0.1",
                      user_agent: str = "PyCloud OS") -> str:
        """Yeni oturum oluştur"""
        try:
            session_id = self.generate_session_id()
            current_time = datetime.now().isoformat()
            
            # Varsayılan değerler
            if idle_timeout is None:
                idle_timeout = self.default_idle_timeout
            if max_duration is None:
                max_duration = self.default_max_duration
            
            # Oturum bilgisi oluştur
            session_info = SessionInfo(
                session_id=session_id,
                user_id=user_id,
                username=username,
                session_type=session_type,
                status=SessionStatus.ACTIVE,
                start_time=current_time,
                last_activity=current_time,
                ip_address=ip_address,
                user_agent=user_agent,
                idle_timeout=idle_timeout,
                max_duration=max_duration,
                auto_lock=auto_lock
            )
            
            # Aktif oturumlara ekle
            self.active_sessions[session_id] = session_info
            
            # Aktivite kaydı oluştur
            self.session_activities[session_id] = []
            self.add_activity(session_id, "session_start", f"Session started for user {username}")
            
            # Kaydet
            self.save_active_sessions()
            
            # Callback'leri çağır
            self._call_callbacks('session_start', session_info)
            
            self.logger.info(f"Session created: {session_id} for user {username}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return ""
    
    def end_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """Oturumu sonlandır"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session_info = self.active_sessions[session_id]
            session_info.status = SessionStatus.TERMINATED
            
            # Aktivite kaydı
            self.add_activity(session_id, "session_end", f"Session ended: {reason}")
            
            # Geçmişe kaydet
            self.save_session_to_history(session_info)
            
            # Aktif oturumlardan kaldır
            del self.active_sessions[session_id]
            
            # Aktivite geçmişini temizle
            if session_id in self.session_activities:
                del self.session_activities[session_id]
            
            # Kaydet
            self.save_active_sessions()
            
            # Callback'leri çağır
            self._call_callbacks('session_end', session_info, reason)
            
            self.logger.info(f"Session ended: {session_id} ({reason})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to end session {session_id}: {e}")
            return False
    
    def update_activity(self, session_id: str, activity_type: str = "user_activity") -> bool:
        """Oturum aktivitesini güncelle"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session_info = self.active_sessions[session_id]
            current_time = datetime.now().isoformat()
            
            # Son aktivite zamanını güncelle
            session_info.last_activity = current_time
            
            # Durumu aktif yap (eğer idle ise)
            if session_info.status == SessionStatus.IDLE:
                session_info.status = SessionStatus.ACTIVE
            
            # Aktivite kaydı
            self.add_activity(session_id, activity_type, "User activity detected")
            
            # Callback'leri çağır
            self._call_callbacks('activity_update', session_info)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update activity for session {session_id}: {e}")
            return False
    
    def lock_session(self, session_id: str, reason: str = "manual_lock") -> bool:
        """Oturumu kilitle"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session_info = self.active_sessions[session_id]
            session_info.status = SessionStatus.LOCKED
            
            # Aktivite kaydı
            self.add_activity(session_id, "session_lock", f"Session locked: {reason}")
            
            # Callback'leri çağır
            self._call_callbacks('session_lock', session_info, reason)
            
            self.logger.info(f"Session locked: {session_id} ({reason})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to lock session {session_id}: {e}")
            return False
    
    def unlock_session(self, session_id: str, password: str = None) -> bool:
        """Oturum kilidini aç"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session_info = self.active_sessions[session_id]
            
            # Şifre kontrolü (eğer gerekiyorsa)
            if password is not None:
                users_manager = self.kernel.get_module("users") if self.kernel else None
                if users_manager:
                    if not users_manager.verify_password(session_info.user_id, password):
                        self.add_activity(session_id, "unlock_failed", "Invalid password")
                        return False
            
            session_info.status = SessionStatus.ACTIVE
            session_info.last_activity = datetime.now().isoformat()
            
            # Aktivite kaydı
            self.add_activity(session_id, "session_unlock", "Session unlocked")
            
            # Callback'leri çağır
            self._call_callbacks('session_unlock', session_info)
            
            self.logger.info(f"Session unlocked: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unlock session {session_id}: {e}")
            return False
    
    def add_activity(self, session_id: str, activity_type: str, description: str, details: Dict = None):
        """Aktivite kaydı ekle"""
        try:
            if session_id not in self.session_activities:
                self.session_activities[session_id] = []
            
            activity = SessionActivity(
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                activity_type=activity_type,
                description=description,
                details=details or {}
            )
            
            activities = self.session_activities[session_id]
            activities.append(activity)
            
            # Maksimum kayıt sayısını kontrol et
            if len(activities) > self.max_activity_records:
                self.session_activities[session_id] = activities[-self.max_activity_records:]
            
        except Exception as e:
            self.logger.error(f"Failed to add activity for session {session_id}: {e}")
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Oturum bilgisini al"""
        return self.active_sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """Kullanıcının aktif oturumlarını al"""
        return [session for session in self.active_sessions.values() 
                if session.user_id == user_id]
    
    def get_active_sessions(self) -> List[SessionInfo]:
        """Tüm aktif oturumları al"""
        return list(self.active_sessions.values())
    
    def get_session_activities(self, session_id: str, limit: int = 100) -> List[SessionActivity]:
        """Oturum aktivitelerini al"""
        activities = self.session_activities.get(session_id, [])
        return activities[-limit:] if limit > 0 else activities
    
    def start_timeout_monitor(self):
        """Timeout izleyicisini başlat"""
        if self.timeout_thread and self.timeout_thread.is_alive():
            return
        
        self.running = True
        self.timeout_thread = threading.Thread(target=self._timeout_monitor_loop, daemon=True)
        self.timeout_thread.start()
        self.logger.info("Session timeout monitor started")
    
    def stop_timeout_monitor(self):
        """Timeout izleyicisini durdur"""
        self.running = False
        if self.timeout_thread:
            self.timeout_thread.join(timeout=5)
        self.logger.info("Session timeout monitor stopped")
    
    def _timeout_monitor_loop(self):
        """Timeout izleme döngüsü"""
        while self.running:
            try:
                current_time = datetime.now()
                sessions_to_process = list(self.active_sessions.items())
                
                for session_id, session_info in sessions_to_process:
                    if session_info.status == SessionStatus.TERMINATED:
                        continue
                    
                    # Son aktivite zamanını parse et
                    try:
                        last_activity = datetime.fromisoformat(session_info.last_activity)
                        start_time = datetime.fromisoformat(session_info.start_time)
                    except ValueError:
                        continue
                    
                    # Idle timeout kontrolü
                    if (session_info.idle_timeout > 0 and 
                        session_info.status == SessionStatus.ACTIVE):
                        
                        idle_duration = (current_time - last_activity).total_seconds() / 60
                        
                        if idle_duration >= session_info.idle_timeout:
                            if session_info.auto_lock:
                                self.lock_session(session_id, "idle_timeout")
                            else:
                                session_info.status = SessionStatus.IDLE
                                self.add_activity(session_id, "session_idle", "Session became idle")
                    
                    # Lock timeout kontrolü
                    if (session_info.status == SessionStatus.IDLE and 
                        session_info.auto_lock and session_info.lock_timeout > 0):
                        
                        idle_duration = (current_time - last_activity).total_seconds() / 60
                        
                        if idle_duration >= session_info.lock_timeout:
                            self.lock_session(session_id, "lock_timeout")
                    
                    # Maksimum süre kontrolü
                    if session_info.max_duration > 0:
                        session_duration = (current_time - start_time).total_seconds() / 60
                        
                        if session_duration >= session_info.max_duration:
                            self.end_session(session_id, "max_duration_exceeded")
                            self._call_callbacks('session_timeout', session_info, "max_duration")
                
                # Değişiklikleri kaydet
                self.save_active_sessions()
                
            except Exception as e:
                self.logger.error(f"Timeout monitor error: {e}")
            
            # Bekleme
            time.sleep(self.timeout_interval)
    
    def save_active_sessions(self):
        """Aktif oturumları kaydet"""
        try:
            sessions_data = {}
            for session_id, session_info in self.active_sessions.items():
                sessions_data[session_id] = session_info.to_dict()
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save active sessions: {e}")
    
    def load_active_sessions(self):
        """Aktif oturumları yükle"""
        try:
            if not self.sessions_file.exists():
                return
            
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            for session_id, session_data in sessions_data.items():
                try:
                    session_info = SessionInfo.from_dict(session_data)
                    self.active_sessions[session_id] = session_info
                    self.session_activities[session_id] = []
                except Exception as e:
                    self.logger.error(f"Failed to load session {session_id}: {e}")
            
            self.logger.info(f"Loaded {len(self.active_sessions)} active sessions")
            
        except Exception as e:
            self.logger.error(f"Failed to load active sessions: {e}")
    
    def save_session_to_history(self, session_info: SessionInfo):
        """Oturumu geçmişe kaydet"""
        try:
            history_data = []
            
            # Mevcut geçmişi yükle
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            
            # Yeni oturumu ekle
            session_data = session_info.to_dict()
            session_data['end_time'] = datetime.now().isoformat()
            
            # Aktiviteleri ekle
            if session_info.session_id in self.session_activities:
                session_data['activities'] = [
                    activity.to_dict() 
                    for activity in self.session_activities[session_info.session_id]
                ]
            
            history_data.append(session_data)
            
            # Maksimum geçmiş sayısını kontrol et (son 1000 oturum)
            if len(history_data) > 1000:
                history_data = history_data[-1000:]
            
            # Kaydet
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save session to history: {e}")
    
    def get_session_history(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """Oturum geçmişini al"""
        try:
            if not self.history_file.exists():
                return []
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            # Kullanıcı filtresi
            if user_id:
                history_data = [session for session in history_data 
                              if session.get('user_id') == user_id]
            
            # Sırala (en yeni önce)
            history_data.sort(key=lambda x: x.get('start_time', ''), reverse=True)
            
            # Limit uygula
            return history_data[:limit] if limit > 0 else history_data
            
        except Exception as e:
            self.logger.error(f"Failed to get session history: {e}")
            return []
    
    def add_session_callback(self, event_type: str, callback: Callable):
        """Oturum callback'i ekle"""
        if event_type in self.session_callbacks:
            self.session_callbacks[event_type].append(callback)
    
    def remove_session_callback(self, event_type: str, callback: Callable):
        """Oturum callback'ini kaldır"""
        if event_type in self.session_callbacks and callback in self.session_callbacks[event_type]:
            self.session_callbacks[event_type].remove(callback)
    
    def _call_callbacks(self, event_type: str, *args):
        """Callback'leri çağır"""
        for callback in self.session_callbacks.get(event_type, []):
            try:
                callback(*args)
            except Exception as e:
                self.logger.error(f"Session callback failed ({event_type}): {e}")
    
    def get_session_stats(self) -> Dict:
        """Oturum istatistikleri"""
        try:
            stats = {
                "active_sessions": len(self.active_sessions),
                "total_activities": sum(len(activities) for activities in self.session_activities.values()),
                "session_types": {},
                "session_statuses": {},
                "average_session_duration": 0
            }
            
            # Tip ve durum sayımları
            for session in self.active_sessions.values():
                session_type = session.session_type.value
                session_status = session.status.value
                
                stats["session_types"][session_type] = stats["session_types"].get(session_type, 0) + 1
                stats["session_statuses"][session_status] = stats["session_statuses"].get(session_status, 0) + 1
            
            # Ortalama oturum süresi (aktif oturumlar için)
            if self.active_sessions:
                current_time = datetime.now()
                total_duration = 0
                
                for session in self.active_sessions.values():
                    try:
                        start_time = datetime.fromisoformat(session.start_time)
                        duration = (current_time - start_time).total_seconds() / 60  # dakika
                        total_duration += duration
                    except ValueError:
                        continue
                
                stats["average_session_duration"] = total_duration / len(self.active_sessions)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get session stats: {e}")
            return {}
    
    def cleanup_expired_sessions(self):
        """Süresi dolmuş oturumları temizle"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session_info in self.active_sessions.items():
                try:
                    start_time = datetime.fromisoformat(session_info.start_time)
                    
                    # 24 saatten eski oturumları temizle
                    if (current_time - start_time).total_seconds() > 86400:  # 24 saat
                        expired_sessions.append(session_id)
                        
                except ValueError:
                    expired_sessions.append(session_id)
            
            # Süresi dolmuş oturumları sonlandır
            for session_id in expired_sessions:
                self.end_session(session_id, "expired")
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def shutdown(self):
        """Session manager'ı kapat"""
        try:
            # Timeout izleyicisini durdur
            self.stop_timeout_monitor()
            
            # Aktif oturumları kaydet
            self.save_active_sessions()
            
            # Tüm aktif oturumları sonlandır
            for session_id in list(self.active_sessions.keys()):
                self.end_session(session_id, "system_shutdown")
            
            self.logger.info("Session manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Session manager shutdown failed: {e}")

# Kolaylık fonksiyonları
_session_manager = None

def init_session_manager(kernel=None) -> SessionManager:
    """Session manager'ı başlat"""
    global _session_manager
    _session_manager = SessionManager(kernel)
    return _session_manager

def get_session_manager() -> Optional[SessionManager]:
    """Session manager'ı al"""
    return _session_manager

def create_session(user_id: str, username: str, **kwargs) -> str:
    """Oturum oluştur (kısayol)"""
    if _session_manager:
        return _session_manager.create_session(user_id, username, **kwargs)
    return ""

def end_session(session_id: str, reason: str = "user_logout") -> bool:
    """Oturum sonlandır (kısayol)"""
    if _session_manager:
        return _session_manager.end_session(session_id, reason)
    return False

def update_activity(session_id: str) -> bool:
    """Aktivite güncelle (kısayol)"""
    if _session_manager:
        return _session_manager.update_activity(session_id)
    return False 