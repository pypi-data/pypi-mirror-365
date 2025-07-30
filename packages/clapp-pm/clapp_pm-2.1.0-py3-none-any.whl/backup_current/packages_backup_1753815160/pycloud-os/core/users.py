"""
PyCloud OS User Manager
Kullanıcı hesapları, giriş işlemleri, profil yönetimi ve oturum sistemi
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

@dataclass
class User:
    """Kullanıcı veri sınıfı"""
    username: str
    display_name: str
    email: str = ""
    avatar: str = "default.png"
    theme: str = "auto"
    language: str = "tr_TR"
    role: str = "user"  # user, admin, root
    created_at: str = ""
    last_login: str = ""
    is_active: bool = True
    password_hash: str = ""
    password_salt: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class Session:
    """Kullanıcı oturumu"""
    session_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    ip_address: str = "local"
    is_active: bool = True

class UserManager:
    """Kullanıcı yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("Users")
        self.users_dir = Path("users")
        self.system_dir = Path("system/users")
        self.system_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.system_dir / "users.json"
        self.sessions_file = self.system_dir / "sessions.json"
        
        # Kullanıcılar ve oturumlar
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.current_user: Optional[str] = None
        
        # Oturum ayarları
        self.session_timeout = timedelta(hours=8)
        self.max_sessions_per_user = 3
        
        self.load_users()
        self.load_sessions()
    
    def load_users(self):
        """Kullanıcıları yükle"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                for username, user_data in users_data.items():
                    self.users[username] = User(**user_data)
                
                self.logger.info(f"Loaded {len(self.users)} users")
            else:
                self.logger.info("No users file found, will create default user")
                
        except Exception as e:
            self.logger.error(f"Failed to load users: {e}")
    
    def save_users(self):
        """Kullanıcıları kaydet"""
        try:
            users_data = {}
            for username, user in self.users.items():
                users_data[username] = asdict(user)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Users saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save users: {e}")
    
    def load_sessions(self):
        """Oturumları yükle"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                
                for session_id, session_data in sessions_data.items():
                    # Datetime objelerini geri çevir
                    session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
                    session_data['last_activity'] = datetime.fromisoformat(session_data['last_activity'])
                    
                    self.sessions[session_id] = Session(**session_data)
                
                # Süresi dolmuş oturumları temizle
                self.cleanup_expired_sessions()
                
                self.logger.info(f"Loaded {len(self.sessions)} active sessions")
                
        except Exception as e:
            self.logger.error(f"Failed to load sessions: {e}")
    
    def save_sessions(self):
        """Oturumları kaydet"""
        try:
            sessions_data = {}
            for session_id, session in self.sessions.items():
                session_dict = asdict(session)
                # Datetime objelerini string'e çevir
                session_dict['created_at'] = session.created_at.isoformat()
                session_dict['last_activity'] = session.last_activity.isoformat()
                sessions_data[session_id] = session_dict
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Failed to save sessions: {e}")
    
    def create_user(self, username: str, password: str, display_name: str = "",
                   email: str = "", role: str = "user") -> bool:
        """Yeni kullanıcı oluştur"""
        try:
            # Kullanıcı adı kontrolü
            if username in self.users:
                self.logger.warning(f"User {username} already exists")
                return False
            
            if not username or len(username) < 3:
                self.logger.warning("Username too short")
                return False
            
            # Şifreyi hash'le
            from core.security import SecurityManager
            security = SecurityManager()
            password_hash, salt = security.hash_password(password)
            
            # Kullanıcı oluştur
            user = User(
                username=username,
                display_name=display_name or username,
                email=email,
                role=role,
                password_hash=password_hash,
                password_salt=salt
            )
            
            self.users[username] = user
            
            # Kullanıcı dizinini oluştur
            self.create_user_directory(username)
            
            self.save_users()
            
            self.logger.info(f"User {username} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create user {username}: {e}")
            return False
    
    def create_user_directory(self, username: str):
        """Kullanıcı dizinini oluştur"""
        user_dir = self.users_dir / username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Standart klasörleri oluştur
        standard_dirs = [
            "Desktop", "Documents", "Downloads", "Pictures", 
            "Music", "Projects", "trash"
        ]
        
        for dir_name in standard_dirs:
            (user_dir / dir_name).mkdir(exist_ok=True)
        
        # Kullanıcı ayarları dosyası
        settings_file = user_dir / ".settings.json"
        if not settings_file.exists():
            default_settings = {
                "theme": "auto",
                "wallpaper": "system/wallpapers/default.jpg",
                "dock_position": "bottom",
                "language": "tr_TR"
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2, ensure_ascii=False)
    
    def authenticate(self, username: str, password: str) -> bool:
        """Kullanıcı kimlik doğrulama"""
        try:
            if username not in self.users:
                self.logger.warning(f"Authentication failed: user {username} not found")
                return False
            
            user = self.users[username]
            
            if not user.is_active:
                self.logger.warning(f"Authentication failed: user {username} is inactive")
                return False
            
            # Şifre kontrolü
            from core.security import SecurityManager
            security = SecurityManager()
            
            if security.verify_password(password, user.password_hash, user.password_salt):
                # Son giriş zamanını güncelle
                user.last_login = datetime.now().isoformat()
                self.save_users()
                
                self.logger.info(f"User {username} authenticated successfully")
                return True
            else:
                self.logger.warning(f"Authentication failed: wrong password for {username}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error for {username}: {e}")
            return False
    
    def login(self, username: str, password: str, ip_address: str = "local") -> Optional[str]:
        """Kullanıcı girişi"""
        try:
            # Güvenlik kontrolü
            from core.security import SecurityManager
            security = SecurityManager()
            
            # Kullanıcı kilitli mi?
            if security.is_user_locked(username):
                remaining = security.get_lockout_remaining(username)
                self.logger.warning(f"User {username} is locked for {remaining}")
                return None
            
            # Kimlik doğrulama
            if not self.authenticate(username, password):
                security.record_login_attempt(username, False, ip_address)
                return None
            
            # Başarılı giriş
            security.record_login_attempt(username, True, ip_address)
            
            # Oturum oluştur
            session_id = self.create_session(username, ip_address)
            
            # Mevcut kullanıcıyı ayarla
            self.current_user = username
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.USER_LOGIN, {
                "username": username,
                "session_id": session_id,
                "ip_address": ip_address
            }, source="UserManager")
            
            self.logger.info(f"User {username} logged in successfully")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Login error for {username}: {e}")
            return None
    
    def logout(self, session_id: str = None, username: str = None):
        """Kullanıcı çıkışı"""
        try:
            # Session ID ile çıkış
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
                username = session.username
                del self.sessions[session_id]
            
            # Username ile tüm oturumları kapat
            elif username:
                sessions_to_remove = [
                    sid for sid, session in self.sessions.items()
                    if session.username == username
                ]
                for sid in sessions_to_remove:
                    del self.sessions[sid]
            
            # Mevcut kullanıcı çıkış yapıyorsa
            if username == self.current_user:
                self.current_user = None
            
            self.save_sessions()
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.USER_LOGOUT, {
                "username": username,
                "session_id": session_id
            }, source="UserManager")
            
            self.logger.info(f"User {username} logged out")
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
    
    def create_session(self, username: str, ip_address: str = "local") -> str:
        """Yeni oturum oluştur"""
        # Kullanıcının mevcut oturum sayısını kontrol et
        user_sessions = [s for s in self.sessions.values() if s.username == username]
        
        if len(user_sessions) >= self.max_sessions_per_user:
            # En eski oturumu kapat
            oldest_session = min(user_sessions, key=lambda s: s.last_activity)
            del self.sessions[oldest_session.session_id]
        
        # Yeni oturum oluştur
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = Session(
            session_id=session_id,
            username=username,
            created_at=now,
            last_activity=now,
            ip_address=ip_address
        )
        
        self.sessions[session_id] = session
        self.save_sessions()
        
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Oturum geçerliliğini kontrol et"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Oturum süresi dolmuş mu?
        if datetime.now() - session.last_activity > self.session_timeout:
            del self.sessions[session_id]
            self.save_sessions()
            return False
        
        # Son aktiviteyi güncelle
        session.last_activity = datetime.now()
        self.save_sessions()
        
        return True
    
    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """Oturum ID'si ile kullanıcı al"""
        if not self.validate_session(session_id):
            return None
        
        session = self.sessions[session_id]
        return self.users.get(session.username)
    
    def cleanup_expired_sessions(self):
        """Süresi dolmuş oturumları temizle"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if now - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.save_sessions()
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_user(self, username: str) -> Optional[User]:
        """Kullanıcı bilgilerini al"""
        return self.users.get(username)
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Kullanıcı bilgilerini güncelle"""
        try:
            if username not in self.users:
                return False
            
            user = self.users[username]
            
            # Güncellenebilir alanlar
            updatable_fields = [
                'display_name', 'email', 'avatar', 'theme', 
                'language', 'is_active'
            ]
            
            for field, value in kwargs.items():
                if field in updatable_fields:
                    setattr(user, field, value)
            
            self.save_users()
            self.logger.info(f"User {username} updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update user {username}: {e}")
            return False
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Şifre değiştir"""
        try:
            # Mevcut şifreyi doğrula
            if not self.authenticate(username, old_password):
                return False
            
            # Yeni şifreyi hash'le
            from core.security import SecurityManager
            security = SecurityManager()
            password_hash, salt = security.hash_password(new_password)
            
            # Kullanıcıyı güncelle
            user = self.users[username]
            user.password_hash = password_hash
            user.password_salt = salt
            
            self.save_users()
            
            self.logger.info(f"Password changed for user {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to change password for {username}: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """Kullanıcıyı sil"""
        try:
            if username not in self.users:
                return False
            
            # Root kullanıcı silinemez
            if username == "root":
                self.logger.warning("Cannot delete root user")
                return False
            
            # Kullanıcının oturumlarını kapat
            self.logout(username=username)
            
            # Kullanıcıyı sil
            del self.users[username]
            self.save_users()
            
            self.logger.info(f"User {username} deleted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete user {username}: {e}")
            return False
    
    def list_users(self) -> List[Dict]:
        """Kullanıcı listesi"""
        users_list = []
        for username, user in self.users.items():
            user_dict = asdict(user)
            # Şifre bilgilerini çıkar
            user_dict.pop('password_hash', None)
            user_dict.pop('password_salt', None)
            users_list.append(user_dict)
        
        return users_list
    
    def get_active_sessions(self) -> List[Dict]:
        """Aktif oturumlar"""
        sessions_list = []
        for session_id, session in self.sessions.items():
            session_dict = asdict(session)
            session_dict['created_at'] = session.created_at.isoformat()
            session_dict['last_activity'] = session.last_activity.isoformat()
            sessions_list.append(session_dict)
        
        return sessions_list
    
    def create_default_user(self):
        """Varsayılan kullanıcı oluştur"""
        if not self.users:
            # Root kullanıcı
            self.create_user("root", "admin123", "Administrator", role="root")
            
            # Demo kullanıcı
            self.create_user("demo", "demo123", "Demo User", role="user")
            
            self.logger.info("Default users created")
    
    def get_current_user(self) -> Optional[User]:
        """Mevcut kullanıcıyı al"""
        if self.current_user:
            return self.users.get(self.current_user)
        return None
    
    def switch_user(self, session_id: str) -> bool:
        """Kullanıcı değiştir"""
        try:
            if not self.validate_session(session_id):
                return False
            
            session = self.sessions[session_id]
            old_user = self.current_user
            self.current_user = session.username
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.USER_SWITCH, {
                "old_user": old_user,
                "new_user": self.current_user
            }, source="UserManager")
            
            self.logger.info(f"Switched from {old_user} to {self.current_user}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to switch user: {e}")
            return False
    
    def shutdown(self):
        """Modül kapatma"""
        self.save_users()
        self.save_sessions()
        self.logger.info("User manager shutdown")

# Global user manager instance
_user_manager = None

def init_users(kernel=None) -> UserManager:
    """User manager'ı başlat"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager(kernel)
    return _user_manager

def get_user_manager() -> Optional[UserManager]:
    """User manager'ı al"""
    return _user_manager 