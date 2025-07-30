"""
PyCloud OS Virtual File System (VFS)
Uygulama erişimlerini sandbox içinde sınırlayan sanal dosya sistemi
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class VFSPermission(Enum):
    """VFS erişim izinleri"""
    READ = "read"
    WRITE = "write" 
    EXECUTE = "execute"
    DELETE = "delete"

@dataclass
class VFSMount:
    """VFS mount noktası"""
    virtual_path: str      # /home, /apps, /system
    real_path: str         # pycloud_fs/home/, pycloud_fs/apps/
    permissions: Set[VFSPermission]
    description: str = ""

@dataclass
class AppProfile:
    """Uygulama VFS erişim profili"""
    app_id: str
    allowed_mounts: List[str]  # ["/home", "/temp"]
    permissions: Dict[str, Set[VFSPermission]] = None  # {"/home": {READ, WRITE}}
    sandbox_mode: bool = True
    description: str = ""
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = {}
    
    def to_dict(self) -> Dict:
        """JSON serialization için dict'e çevir"""
        permissions_dict = {}
        for mount, perms in self.permissions.items():
            permissions_dict[mount] = [p.value for p in perms]
        
        return {
            "app_id": self.app_id,
            "allowed_mounts": self.allowed_mounts,
            "permissions": permissions_dict,
            "sandbox_mode": self.sandbox_mode,
            "description": self.description
        }

class PyCloudVFS:
    """PyCloud OS Virtual File System"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("PyCloudVFS")
        self.base_path = Path.cwd()
        
        # VFS root dizini
        self.vfs_root = self.base_path / "pycloud_fs"
        
        # Mount noktaları
        self.mount_points: Dict[str, VFSMount] = {}
        
        # Uygulama profilleri
        self.app_profiles: Dict[str, AppProfile] = {}
        
        # Kullanıcı bazlı profiller 
        self.user_profiles: Dict[str, Dict[str, AppProfile]] = {}
        
        # Current user context
        self.current_user = "default"
        
        # Security module referansı
        self.security = None
        
        # Yasaklı sistem dizinleri
        self.forbidden_paths = {
            "/usr", "/bin", "/sbin", "/etc", "/var", "/proc", "/sys",
            "/Library", "/System", "/Applications", "/Users"
        }
        
        self.initialize()
    
    def initialize(self):
        """VFS sistemini başlat"""
        try:
            # VFS kök dizinini oluştur
            self.vfs_root.mkdir(parents=True, exist_ok=True)
            
            # Varsayılan mount noktalarını tanımla
            self._setup_default_mounts()
            
            # Varsayılan uygulama profillerini yükle
            self._setup_default_profiles()
            
            # Security modülü referansını al
            if self.kernel:
                self.security = self.kernel.get_module("security")
            
            self.logger.info("PyCloud VFS initialized")
            
        except Exception as e:
            self.logger.error(f"VFS initialization failed: {e}")
            raise
    
    def _setup_default_mounts(self):
        """Varsayılan mount noktalarını kur"""
        default_mounts = {
            "/home": VFSMount(
                virtual_path="/home",
                real_path=str(self.vfs_root / "home"),
                permissions={VFSPermission.READ, VFSPermission.WRITE, VFSPermission.DELETE},
                description="Kullanıcı dizinleri"
            ),
            "/apps": VFSMount(
                virtual_path="/apps", 
                real_path=str(self.vfs_root / "apps"),
                permissions={VFSPermission.READ, VFSPermission.EXECUTE},
                description="Uygulama dizinleri"
            ),
            "/system": VFSMount(
                virtual_path="/system",
                real_path=str(self.vfs_root / "system"), 
                permissions={VFSPermission.READ},
                description="Sistem dosyaları"
            ),
            "/temp": VFSMount(
                virtual_path="/temp",
                real_path=str(self.vfs_root / "temp"),
                permissions={VFSPermission.READ, VFSPermission.WRITE, VFSPermission.DELETE},
                description="Geçici dosyalar"
            )
        }
        
        for virtual_path, mount in default_mounts.items():
            self.mount_points[virtual_path] = mount
            
            # Gerçek dizini oluştur
            Path(mount.real_path).mkdir(parents=True, exist_ok=True)
            
            self.logger.debug(f"VFS mount created: {virtual_path} -> {mount.real_path}")
    
    def _setup_default_profiles(self):
        """Varsayılan uygulama profillerini kur"""
        default_profiles = {
            "cloud_notepad": AppProfile(
                app_id="cloud_notepad",
                allowed_mounts=["/home", "/temp"],
                permissions={
                    "/home": {VFSPermission.READ, VFSPermission.WRITE},
                    "/temp": {VFSPermission.READ, VFSPermission.WRITE, VFSPermission.DELETE}
                },
                description="Metin düzenleyici - kullanıcı dosyalarına erişim"
            ),
            "cloud_browser": AppProfile(
                app_id="cloud_browser",
                allowed_mounts=["/home", "/temp"],
                permissions={
                    "/home": {VFSPermission.READ},
                    "/temp": {VFSPermission.READ, VFSPermission.WRITE, VFSPermission.DELETE}
                },
                description="Web tarayıcı - indirme ve önizleme"
            ),
            "cloud_pyide": AppProfile(
                app_id="cloud_pyide",
                allowed_mounts=["/home", "/apps", "/temp"],
                permissions={
                    "/home": {VFSPermission.READ, VFSPermission.WRITE},
                    "/apps": {VFSPermission.READ, VFSPermission.EXECUTE},
                    "/temp": {VFSPermission.READ, VFSPermission.WRITE, VFSPermission.DELETE}
                },
                description="Python IDE - proje geliştirme"
            ),
            "cloud_files": AppProfile(
                app_id="cloud_files",
                allowed_mounts=["/home", "/apps", "/system", "/temp"],
                permissions={
                    "/home": {VFSPermission.READ, VFSPermission.WRITE, VFSPermission.DELETE},
                    "/apps": {VFSPermission.READ},
                    "/system": {VFSPermission.READ},
                    "/temp": {VFSPermission.READ, VFSPermission.WRITE, VFSPermission.DELETE}
                },
                description="Dosya yöneticisi - tam erişim"
            )
        }
        
        for app_id, profile in default_profiles.items():
            self.app_profiles[app_id] = profile
    
    def validate_path(self, virtual_path: str, app_id: str = None) -> bool:
        """Sanal yolun geçerliliğini kontrol et"""
        try:
            # Yasaklı sistem yollarını kontrol et
            for forbidden in self.forbidden_paths:
                if virtual_path.startswith(forbidden):
                    self.logger.warning(f"Access denied to forbidden path: {virtual_path}")
                    return False
            
            # VFS mount kontrolü
            mount_root = self._get_mount_root(virtual_path)
            if not mount_root:
                self.logger.warning(f"Path not in VFS mounts: {virtual_path}")
                return False
            
            # Uygulama izin kontrolü
            if app_id:
                # Önce global profile kontrol et
                if not self._check_app_permission(app_id, virtual_path, VFSPermission.READ):
                    # Global başarısız ise user profile kontrol et
                    if not self._check_user_app_permission(app_id, virtual_path, VFSPermission.READ):
                        self.logger.warning(f"App {app_id} denied access to {virtual_path}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Path validation error: {e}")
            return False
    
    def resolve_path(self, virtual_path: str) -> Optional[str]:
        """Sanal yolu gerçek dosya sistemi yoluna çevir"""
        try:
            # / ile başlayan yolları normalize et
            if not virtual_path.startswith('/'):
                virtual_path = '/' + virtual_path
            
            # Her mount noktasını kontrol et
            for mount_id, mount in self.mount_points.items():
                if virtual_path.startswith(mount.virtual_path):
                    # Virtual path'ten mount prefix'i çıkar
                    relative_path = virtual_path[len(mount.virtual_path):].lstrip('/')
                    
                    # Real path'i oluştur - mount.real_path string olduğu için Path() kullan
                    base_real_path = Path(mount.real_path)
                    if relative_path:
                        real_path = base_real_path / relative_path
                    else:
                        real_path = base_real_path
                    
                    self.logger.debug(f"Path resolved: {virtual_path} → {real_path}")
                    return str(real_path)
            
            # Mount bulunamadı - fallback mapping
            self.logger.warning(f"No mount found for {virtual_path}, using fallback")
            
            # Fallback mapping
            fallback_mappings = {
                "/home": "pycloud_fs/home",
                "/apps": "pycloud_fs/apps", 
                "/system": "pycloud_fs/system",
                "/temp": "pycloud_fs/temp"
            }
            
            for vpath, rpath in fallback_mappings.items():
                if virtual_path.startswith(vpath):
                    relative = virtual_path[len(vpath):].lstrip('/')
                    if relative:
                        fallback_real = Path(rpath) / relative
                    else:
                        fallback_real = Path(rpath)
                    
                    self.logger.debug(f"Fallback resolve: {virtual_path} → {fallback_real}")
                    return str(fallback_real)
            
            # Son fallback
            self.logger.warning(f"Could not resolve path: {virtual_path}")
            return None
            
        except Exception as e:
            self.logger.error(f"Path resolution error: {e}")
            return None
    
    def _get_mount_root(self, virtual_path: str) -> Optional[str]:
        """Sanal yol için mount kökünü bul"""
        for mount_path in sorted(self.mount_points.keys(), key=len, reverse=True):
            if virtual_path.startswith(mount_path):
                return mount_path
        return None
    
    def _check_app_permission(self, app_id: str, virtual_path: str, permission: VFSPermission) -> bool:
        """Uygulama iznini kontrol et"""
        try:
            if app_id not in self.app_profiles:
                self.logger.warning(f"Unknown app profile: {app_id}")
                return False
            
            profile = self.app_profiles[app_id]
            mount_root = self._get_mount_root(virtual_path)
            
            if not mount_root:
                return False
            
            # Mount erişim kontrolü
            if mount_root not in profile.allowed_mounts:
                return False
            
            # İzin kontrolü
            if mount_root not in profile.permissions:
                return False
            
            return permission in profile.permissions[mount_root]
            
        except Exception as e:
            self.logger.error(f"Permission check error: {e}")
            return False
    
    def _check_user_app_permission(self, app_id: str, virtual_path: str, permission: VFSPermission) -> bool:
        """Kullanıcı bazlı uygulama izin kontrolü"""
        try:
            # Mevcut kullanıcının app profile'ını kontrol et
            if self.current_user in self.user_profiles:
                if app_id in self.user_profiles[self.current_user]:
                    profile = self.user_profiles[self.current_user][app_id]
                    mount_root = self._get_mount_root(virtual_path)
                    
                    if not mount_root:
                        return False
                    
                    # Mount erişim kontrolü
                    if mount_root not in profile.allowed_mounts:
                        return False
                    
                    # İzin kontrolü
                    if mount_root not in profile.permissions:
                        return False
                    
                    return permission in profile.permissions[mount_root]
                    
            return False
            
        except Exception as e:
            self.logger.error(f"User permission check error: {e}")
            return False
    
    def check_access(self, virtual_path: str, app_id: str, permission: VFSPermission) -> bool:
        """Uygulama erişim kontrolü (ana API)"""
        try:
            # Path validation
            if not self.validate_path(virtual_path, app_id):
                return False
            
            # Permission check
            if not self._check_app_permission(app_id, virtual_path, permission):
                return False
            
            # Security modülü kontrolü
            if self.security:
                security_result = self.security.check_file_access(app_id, virtual_path, permission.value)
                if not security_result:
                    self.logger.warning(f"Security module denied access: {app_id} -> {virtual_path}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Access check error: {e}")
            return False
    
    def list_allowed_paths(self, app_id: str) -> List[str]:
        """Uygulamanın erişebileceği yolları listele"""
        try:
            if app_id not in self.app_profiles:
                return []
            
            profile = self.app_profiles[app_id]
            return profile.allowed_mounts.copy()
            
        except Exception as e:
            self.logger.error(f"Failed to list allowed paths for {app_id}: {e}")
            return []
    
    def get_app_profile(self, app_id: str) -> Optional[Dict]:
        """Uygulama profilini al (JSON serializable)"""
        profile = self.app_profiles.get(app_id)
        if profile:
            return profile.to_dict()
        return None
    
    def add_app_profile(self, profile: AppProfile):
        """Yeni uygulama profili ekle"""
        self.app_profiles[profile.app_id] = profile
        self.logger.info(f"Added VFS profile for {profile.app_id}")
    
    def get_mount_info(self) -> Dict[str, Dict]:
        """Mount bilgilerini al"""
        return {
            path: {
                "virtual_path": mount.virtual_path,
                "real_path": mount.real_path,
                "permissions": [p.value for p in mount.permissions],
                "description": mount.description
            }
            for path, mount in self.mount_points.items()
        }
    
    def get_security_stats(self) -> Dict[str, Any]:
        """VFS güvenlik istatistiklerini al"""
        try:
            stats = {
                "total_mounts": len(self.mount_points),
                "total_app_profiles": len(self.app_profiles),
                "active_sandboxes": len([p for p in self.app_profiles.values() if p.sandbox_mode]),
                "permission_violations": getattr(self, 'violation_count', 0),
                "mount_points": [mount.virtual_path for mount in self.mount_points.values()]
            }
            
            # Uygulama izin dağılımı
            permission_distribution = {}
            for profile in self.app_profiles.values():
                count = len(profile.allowed_mounts)
                permission_distribution[profile.app_id] = count
            
            stats["app_permissions"] = permission_distribution
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting security stats: {e}")
            return {"error": str(e)}
    
    def create_app_profile(self, app_id: str, allowed_mounts: List[str] = None, 
                          sandboxed: bool = True) -> AppProfile:
        """Yeni uygulama profili oluştur"""
        try:
            if allowed_mounts is None:
                # Varsayılan izinler: home ve temp
                allowed_mounts = ["/home", "/temp"]
            
            profile = AppProfile(
                app_id=app_id,
                allowed_mounts=allowed_mounts,
                sandbox_mode=sandboxed,
                created_at=datetime.now().isoformat()
            )
            
            self.app_profiles[app_id] = profile
            self.logger.info(f"Created app profile for {app_id}: sandboxed={sandboxed}, mounts={allowed_mounts}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating app profile for {app_id}: {e}")
            raise
    
    def update_app_profile(self, app_id: str, **kwargs) -> bool:
        """Uygulama profilini güncelle"""
        try:
            if app_id not in self.app_profiles:
                return False
            
            profile = self.app_profiles[app_id]
            
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            self.logger.info(f"Updated app profile for {app_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating app profile for {app_id}: {e}")
            return False
    
    def set_user_context(self, username: str) -> bool:
        """Kullanıcı kontekstini değiştir"""
        try:
            self.current_user = username
            
            # Kullanıcı VFS dizinini oluştur
            user_home = self.vfs_root / "home" / username
            user_home.mkdir(parents=True, exist_ok=True)
            
            # Kullanıcıya özel alt dizinler
            for subdir in ["documents", "downloads", "pictures", "projects"]:
                (user_home / subdir).mkdir(exist_ok=True)
            
            self.logger.info(f"User context changed to: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set user context: {e}")
            return False
    
    def get_user_home_path(self, username: str = None) -> str:
        """Kullanıcının home dizin yolunu al"""
        if username is None:
            username = self.current_user
        return f"/home/{username}"
    
    def create_user_app_profile(self, username: str, app_id: str, allowed_mounts: List[str] = None) -> Dict:
        """Kullanıcıya özel uygulama profili oluştur (JSON serializable return)"""
        try:
            if username not in self.user_profiles:
                self.user_profiles[username] = {}
            
            if allowed_mounts is None:
                # Kullanıcının kendi home'una erişim + temp
                user_home = self.get_user_home_path(username)
                allowed_mounts = [user_home, "/temp"]
            
            profile = AppProfile(
                app_id=app_id,
                allowed_mounts=allowed_mounts,
                permissions={
                    mount: {VFSPermission.READ, VFSPermission.WRITE} 
                    for mount in allowed_mounts
                },
                sandbox_mode=True,
                description=f"User {username} profile for {app_id}"
            )
            
            self.user_profiles[username][app_id] = profile
            self.logger.info(f"Created user profile: {username}/{app_id}")
            
            # JSON serializable dict döndür
            return profile.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error creating user app profile: {e}")
            raise
    
    def get_user_app_profile(self, username: str, app_id: str) -> Optional[Dict]:
        """Kullanıcıya özel uygulama profilini al"""
        try:
            if username in self.user_profiles:
                if app_id in self.user_profiles[username]:
                    return self.user_profiles[username][app_id].to_dict()
            
            # Fallback: global profile
            return self.get_app_profile(app_id)
            
        except Exception as e:
            self.logger.error(f"Error getting user app profile: {e}")
            return None
    
    def check_user_access(self, username: str, virtual_path: str, app_id: str, permission: VFSPermission) -> bool:
        """Kullanıcı bazlı erişim kontrolü"""
        try:
            # Path validation (same for all users)
            if not self.validate_path(virtual_path):
                return False
            
            # User profile check
            if username in self.user_profiles:
                if app_id in self.user_profiles[username]:
                    profile = self.user_profiles[username][app_id]
                    mount_root = self._get_mount_root(virtual_path)
                    
                    if mount_root in profile.allowed_mounts:
                        if mount_root in profile.permissions:
                            return permission in profile.permissions[mount_root]
            
            # Fallback to global check
            return self.check_access(virtual_path, app_id, permission)
            
        except Exception as e:
            self.logger.error(f"User access check error: {e}")
            return False 