"""
PyCloud OS Security Manager
Dosya, kullanıcı ve sistem bazlı güvenlik işlemleri
"""

import os
import hashlib
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum

class PermissionLevel(Enum):
    """İzin seviyeleri"""
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 4
    ADMIN = 8

class SecurityEvent:
    """Güvenlik olayı"""
    
    def __init__(self, event_type: str, user: str, resource: str, 
                 action: str, success: bool, details: str = ""):
        self.timestamp = datetime.now()
        self.event_type = event_type
        self.user = user
        self.resource = resource
        self.action = action
        self.success = success
        self.details = details
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "user": self.user,
            "resource": self.resource,
            "action": self.action,
            "success": self.success,
            "details": self.details
        }

class SecurityManager:
    """Güvenlik yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("Security")
        self.security_dir = Path("system/security")
        self.security_dir.mkdir(parents=True, exist_ok=True)
        
        self.permissions_file = self.security_dir / "permissions.json"
        self.security_log = self.security_dir / "security.log"
        self.blocked_actions_file = self.security_dir / "blocked_actions.json"
        
        # İzinler ve güvenlik durumu
        self.permissions: Dict[str, Dict] = {}
        self.blocked_actions: Set[str] = set()
        self.failed_login_attempts: Dict[str, List[datetime]] = {}
        self.security_events: List[SecurityEvent] = []
        
        # Güvenlik ayarları
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.session_timeout = timedelta(hours=1)
        
        self.load_security_data()
    
    def load_security_data(self):
        """Güvenlik verilerini yükle"""
        try:
            # İzinleri yükle
            if self.permissions_file.exists():
                with open(self.permissions_file, 'r', encoding='utf-8') as f:
                    self.permissions = json.load(f)
            
            # Engellenen eylemleri yükle
            if self.blocked_actions_file.exists():
                with open(self.blocked_actions_file, 'r', encoding='utf-8') as f:
                    blocked_list = json.load(f)
                    self.blocked_actions = set(blocked_list)
            
            self.logger.info("Security data loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load security data: {e}")
    
    def save_security_data(self):
        """Güvenlik verilerini kaydet"""
        try:
            # İzinleri kaydet
            with open(self.permissions_file, 'w', encoding='utf-8') as f:
                json.dump(self.permissions, f, indent=2, ensure_ascii=False)
            
            # Engellenen eylemleri kaydet
            with open(self.blocked_actions_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.blocked_actions), f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Failed to save security data: {e}")
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Şifreyi hash'le"""
        if salt is None:
            salt = os.urandom(32).hex()
        
        # PBKDF2 ile güvenli hash
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)  # 100,000 iterasyon
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Şifreyi doğrula"""
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == stored_hash
    
    def check_permission(self, user: str, resource: str, action: str) -> bool:
        """İzin kontrolü"""
        try:
            # Root kullanıcı her şeyi yapabilir
            if user == "root":
                return True
            
            # Kullanıcı izinlerini kontrol et
            user_perms = self.permissions.get(user, {})
            resource_perms = user_perms.get(resource, {})
            
            # Eylem izni var mı?
            allowed_actions = resource_perms.get("actions", [])
            if action in allowed_actions or "all" in allowed_actions:
                return True
            
            # Grup izinlerini kontrol et
            user_groups = user_perms.get("groups", [])
            for group in user_groups:
                group_perms = self.permissions.get(f"@{group}", {})
                group_resource_perms = group_perms.get(resource, {})
                group_actions = group_resource_perms.get("actions", [])
                
                if action in group_actions or "all" in group_actions:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return False
    
    def grant_permission(self, user: str, resource: str, actions: List[str]):
        """İzin ver"""
        if user not in self.permissions:
            self.permissions[user] = {}
        
        if resource not in self.permissions[user]:
            self.permissions[user][resource] = {"actions": []}
        
        # Mevcut izinlerle birleştir
        current_actions = set(self.permissions[user][resource]["actions"])
        current_actions.update(actions)
        self.permissions[user][resource]["actions"] = list(current_actions)
        
        self.save_security_data()
        self.log_security_event("PERMISSION_GRANTED", user, resource, 
                               f"Actions: {actions}", True)
    
    def revoke_permission(self, user: str, resource: str, actions: List[str]):
        """İzin iptal et"""
        if user in self.permissions and resource in self.permissions[user]:
            current_actions = set(self.permissions[user][resource]["actions"])
            current_actions.difference_update(actions)
            self.permissions[user][resource]["actions"] = list(current_actions)
            
            # Boş kaldıysa sil
            if not self.permissions[user][resource]["actions"]:
                del self.permissions[user][resource]
            
            if not self.permissions[user]:
                del self.permissions[user]
            
            self.save_security_data()
            self.log_security_event("PERMISSION_REVOKED", user, resource,
                                   f"Actions: {actions}", True)
    
    def add_user_to_group(self, user: str, group: str):
        """Kullanıcıyı gruba ekle"""
        if user not in self.permissions:
            self.permissions[user] = {}
        
        if "groups" not in self.permissions[user]:
            self.permissions[user]["groups"] = []
        
        if group not in self.permissions[user]["groups"]:
            self.permissions[user]["groups"].append(group)
            self.save_security_data()
            self.log_security_event("GROUP_ADDED", user, group, "", True)
    
    def remove_user_from_group(self, user: str, group: str):
        """Kullanıcıyı gruptan çıkar"""
        if (user in self.permissions and 
            "groups" in self.permissions[user] and
            group in self.permissions[user]["groups"]):
            
            self.permissions[user]["groups"].remove(group)
            self.save_security_data()
            self.log_security_event("GROUP_REMOVED", user, group, "", True)
    
    def record_login_attempt(self, user: str, success: bool, ip: str = "local"):
        """Giriş denemesini kaydet"""
        if user not in self.failed_login_attempts:
            self.failed_login_attempts[user] = []
        
        now = datetime.now()
        
        if success:
            # Başarılı giriş - başarısız denemeleri temizle
            self.failed_login_attempts[user] = []
            self.log_security_event("LOGIN_SUCCESS", user, ip, "", True)
        else:
            # Başarısız giriş
            self.failed_login_attempts[user].append(now)
            
            # Eski denemeleri temizle (lockout süresi geçenler)
            cutoff = now - self.lockout_duration
            self.failed_login_attempts[user] = [
                attempt for attempt in self.failed_login_attempts[user]
                if attempt > cutoff
            ]
            
            self.log_security_event("LOGIN_FAILED", user, ip, 
                                   f"Attempts: {len(self.failed_login_attempts[user])}", 
                                   False)
    
    def is_user_locked(self, user: str) -> bool:
        """Kullanıcı kilitli mi?"""
        if user not in self.failed_login_attempts:
            return False
        
        now = datetime.now()
        cutoff = now - self.lockout_duration
        
        # Geçerli başarısız denemeleri say
        recent_attempts = [
            attempt for attempt in self.failed_login_attempts[user]
            if attempt > cutoff
        ]
        
        return len(recent_attempts) >= self.max_login_attempts
    
    def get_lockout_remaining(self, user: str) -> Optional[timedelta]:
        """Kalan kilitleme süresi"""
        if not self.is_user_locked(user):
            return None
        
        if user not in self.failed_login_attempts:
            return None
        
        # En eski başarısız deneme
        oldest_attempt = min(self.failed_login_attempts[user])
        unlock_time = oldest_attempt + self.lockout_duration
        
        remaining = unlock_time - datetime.now()
        return remaining if remaining.total_seconds() > 0 else None
    
    def block_action(self, action: str, reason: str = ""):
        """Eylemi engelle"""
        self.blocked_actions.add(action)
        self.save_security_data()
        self.log_security_event("ACTION_BLOCKED", "system", action, reason, True)
    
    def unblock_action(self, action: str):
        """Eylem engelini kaldır"""
        if action in self.blocked_actions:
            self.blocked_actions.remove(action)
            self.save_security_data()
            self.log_security_event("ACTION_UNBLOCKED", "system", action, "", True)
    
    def is_action_blocked(self, action: str) -> bool:
        """Eylem engelli mi?"""
        return action in self.blocked_actions
    
    def detect_suspicious_activity(self, user: str, action: str, resource: str) -> bool:
        """Şüpheli aktivite tespiti"""
        suspicious = False
        reasons = []
        
        # Çok fazla başarısız giriş
        if user in self.failed_login_attempts:
            recent_failures = len(self.failed_login_attempts[user])
            if recent_failures > 3:
                suspicious = True
                reasons.append(f"Multiple failed logins: {recent_failures}")
        
        # Hassas sistem dosyalarına erişim
        sensitive_paths = ["/system/", "/core/", "/security/"]
        if any(path in resource for path in sensitive_paths):
            if not self.check_permission(user, resource, action):
                suspicious = True
                reasons.append("Unauthorized access to sensitive resource")
        
        # Yüksek frekanslı işlemler (basit kontrol)
        # Bu gerçek uygulamada daha sofistike olmalı
        
        if suspicious:
            self.log_security_event("SUSPICIOUS_ACTIVITY", user, resource,
                                   f"Action: {action}, Reasons: {reasons}", False)
        
        return suspicious
    
    def log_security_event(self, event_type: str, user: str, resource: str,
                          details: str, success: bool):
        """Güvenlik olayını logla"""
        event = SecurityEvent(event_type, user, resource, "", success, details)
        self.security_events.append(event)
        
        # Log dosyasına yaz
        try:
            with open(self.security_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write security log: {e}")
        
        # Son 1000 olayı bellekte tut
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        # Kritik olayları logla
        if not success or event_type in ["SUSPICIOUS_ACTIVITY", "PERMISSION_DENIED"]:
            self.logger.warning(f"Security event: {event_type} - {user} - {resource}")
    
    def get_security_events(self, event_type: str = None, user: str = None,
                           limit: int = 100) -> List[Dict]:
        """Güvenlik olaylarını al"""
        events = self.security_events
        
        # Filtrele
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user:
            events = [e for e in events if e.user == user]
        
        # Son N olayı döndür
        events = events[-limit:]
        
        return [event.to_dict() for event in events]
    
    def get_user_permissions(self, user: str) -> Dict:
        """Kullanıcı izinlerini al"""
        return self.permissions.get(user, {})
    
    def get_security_stats(self) -> Dict:
        """Güvenlik istatistikleri"""
        total_events = len(self.security_events)
        failed_events = len([e for e in self.security_events if not e.success])
        locked_users = len([u for u in self.failed_login_attempts.keys() 
                           if self.is_user_locked(u)])
        
        return {
            "total_events": total_events,
            "failed_events": failed_events,
            "success_rate": (total_events - failed_events) / max(total_events, 1),
            "locked_users": locked_users,
            "blocked_actions": len(self.blocked_actions),
            "total_users": len(self.permissions)
        }
    
    def encrypt_data(self, data: str, key: str = None) -> tuple:
        """Veriyi şifrele (basit XOR - gerçek uygulamada AES kullanılmalı)"""
        if key is None:
            key = os.urandom(32).hex()
        
        # Basit XOR şifreleme (demo amaçlı)
        encrypted = ""
        for i, char in enumerate(data):
            key_char = key[i % len(key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        
        return encrypted.encode('latin1').hex(), key
    
    def decrypt_data(self, encrypted_hex: str, key: str) -> str:
        """Veriyi çöz"""
        try:
            encrypted = bytes.fromhex(encrypted_hex).decode('latin1')
            
            decrypted = ""
            for i, char in enumerate(encrypted):
                key_char = key[i % len(key)]
                decrypted += chr(ord(char) ^ ord(key_char))
            
            return decrypted
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return ""
    
    def shutdown(self):
        """Modül kapatma"""
        self.save_security_data()
        self.logger.info("Security manager shutdown")
    
    # VFS Güvenlik Kontrolleri
    def check_file_access(self, app_id: str, virtual_path: str, permission: str) -> bool:
        """VFS üzerinden dosya erişim kontrolü"""
        try:
            # App bazlı izin profili kontrol et
            if app_id in self.app_security_profiles:
                profile = self.app_security_profiles[app_id]
                
                # Dosya sistemi izni var mı?
                fs_permission = f"fs.{permission}"
                if not profile.get(fs_permission, False):
                    self.log_security_event("VFS_ACCESS_DENIED", app_id, virtual_path,
                                           f"Permission: {permission}", False)
                    return False
            
            # Yasaklı yolları kontrol et
            forbidden_patterns = [
                "/etc/", "/usr/", "/bin/", "/var/", "/proc/", "/sys/",
                "/Library/", "/System/", "/Applications/"
            ]
            
            for pattern in forbidden_patterns:
                if virtual_path.startswith(pattern):
                    self.log_security_event("VFS_ACCESS_DENIED", app_id, virtual_path,
                                           "Forbidden system path", False)
                    return False
            
            # İzin verildi
            self.log_security_event("VFS_ACCESS_GRANTED", app_id, virtual_path,
                                   f"Permission: {permission}", True)
            return True
            
        except Exception as e:
            self.logger.error(f"VFS access check error: {e}")
            return False
    
    def setup_app_security_profiles(self):
        """Uygulama güvenlik profillerini kur"""
        if not hasattr(self, 'app_security_profiles'):
            self.app_security_profiles = {}
        
        # Varsayılan uygulama güvenlik profilleri
        default_profiles = {
            "cloud_notepad": {
                "fs.read": True,
                "fs.write": True,
                "fs.delete": False,
                "network": False,
                "system": False
            },
            "cloud_browser": {
                "fs.read": True,
                "fs.write": True,
                "fs.delete": False,
                "network": True,
                "system": False
            },
            "cloud_pyide": {
                "fs.read": True,
                "fs.write": True,
                "fs.delete": True,
                "fs.execute": True,
                "network": False,
                "system": False
            },
            "cloud_files": {
                "fs.read": True,
                "fs.write": True,
                "fs.delete": True,
                "fs.execute": False,
                "network": False,
                "system": True
            },
            "cloud_terminal": {
                "fs.read": True,
                "fs.write": True,
                "fs.delete": True,
                "fs.execute": True,
                "network": False,
                "system": True
            }
        }
        
        # Mevcut profilleri güncelle
        for app_id, profile in default_profiles.items():
            if app_id not in self.app_security_profiles:
                self.app_security_profiles[app_id] = profile
                self.logger.info(f"Added security profile for {app_id}")
    
    def get_app_security_profile(self, app_id: str) -> Dict:
        """Uygulama güvenlik profilini al"""
        if not hasattr(self, 'app_security_profiles'):
            self.setup_app_security_profiles()
        
        return self.app_security_profiles.get(app_id, {})
    
    def update_app_security_profile(self, app_id: str, permissions: Dict):
        """Uygulama güvenlik profilini güncelle"""
        if not hasattr(self, 'app_security_profiles'):
            self.setup_app_security_profiles()
        
        if app_id not in self.app_security_profiles:
            self.app_security_profiles[app_id] = {}
        
        self.app_security_profiles[app_id].update(permissions)
        self.save_security_data()
        
        self.log_security_event("SECURITY_PROFILE_UPDATED", "system", app_id,
                               f"Permissions: {permissions}", True)
    
    def validate_app_permissions(self, app_id: str, required_permissions: List[str]) -> bool:
        """Uygulamanın gerekli izinlere sahip olup olmadığını kontrol et"""
        profile = self.get_app_security_profile(app_id)
        
        for permission in required_permissions:
            if not profile.get(permission, False):
                self.log_security_event("PERMISSION_CHECK_FAILED", app_id, permission,
                                       f"Required permissions: {required_permissions}", False)
                return False
        
        return True
    
    def log_violation_attempt(self, app_id: str, attempted_path: str, reason: str):
        """İzin ihlali denemesini logla"""
        self.log_security_event("SECURITY_VIOLATION", app_id, attempted_path, reason, False)
        
        # Kritik ihlaller için ek aksiyonlar alınabilir
        if "system" in attempted_path.lower() or "forbidden" in reason.lower():
            self.logger.critical(f"CRITICAL SECURITY VIOLATION: {app_id} attempted {attempted_path} - {reason}")

# Global security manager instance
_security_manager = None

def init_security(kernel=None) -> SecurityManager:
    """Security manager'ı başlat"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(kernel)
    return _security_manager

def get_security_manager() -> Optional[SecurityManager]:
    """Security manager'ı al"""
    return _security_manager 