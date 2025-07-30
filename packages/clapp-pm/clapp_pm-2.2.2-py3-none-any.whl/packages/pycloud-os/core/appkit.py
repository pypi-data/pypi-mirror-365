"""
PyCloud OS AppKit
.app uzantılı uygulama paketlerini kuran, doğrulayan, geri alan ve sisteme entegre eden modül
"""

import os
import json
import shutil
import hashlib
import zipfile
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class AppStatus(Enum):
    """Uygulama durumları"""
    NOT_INSTALLED = "not_installed"
    INSTALLING = "installing"
    INSTALLED = "installed"
    UPDATING = "updating"
    UNINSTALLING = "uninstalling"
    FAILED = "failed"
    CORRUPTED = "corrupted"

class InstallResult(Enum):
    """Kurulum sonuç türleri"""
    SUCCESS = "success"
    FAILED = "failed"
    ALREADY_INSTALLED = "already_installed"
    INVALID_PACKAGE = "invalid_package"
    PERMISSION_DENIED = "permission_denied"
    DEPENDENCY_ERROR = "dependency_error"
    SIGNATURE_ERROR = "signature_error"
    MODULE_ADAPTATION_ERROR = "module_adaptation_error"  # Yeni cursorrules özelliği

@dataclass
class AppMetadata:
    """Uygulama metadata sınıfı"""
    id: str
    name: str
    version: str
    description: str
    entry: str
    exec: str
    icon: str
    category: str
    developer: str
    license: str = ""
    homepage: str = ""
    tags: List[str] = None
    screenshots: List[str] = None
    
    # Yeni cursorrules alanları
    requires: List[str] = None  # Gerekli modüller
    permissions: Dict[str, bool] = None  # İzin gereksinimleri
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.screenshots is None:
            self.screenshots = []
        if self.requires is None:
            self.requires = []
        if self.permissions is None:
            self.permissions = {}
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AppMetadata':
        """Dict'ten oluştur"""
        return cls(**data)

class ModuleAdapter:
    """Uygulama modül adaptasyon sistemi - cursorrules genişletmesi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("ModuleAdapter")
        
        # Desteklenen çekirdek modülleri
        self.supported_modules = {
            "core.fs": "Dosya sistemi erişimi",
            "core.audio": "Ses sistemi erişimi", 
            "core.network": "Ağ erişimi",
            "core.security": "Güvenlik sistemi",
            "core.events": "Olay sistemi",
            "core.notify": "Bildirim sistemi",
            "core.config": "Yapılandırma sistemi",
            "core.users": "Kullanıcı sistemi",
            "core.process": "İşlem yönetimi",
            "core.thread": "Thread yönetimi"
        }
        
        # Modül bağlantıları cache
        self.module_connections: Dict[str, Dict] = {}
    
    def validate_requirements(self, app_metadata: AppMetadata) -> tuple[bool, List[str]]:
        """Uygulama gereksinimlerini doğrula"""
        errors = []
        
        try:
            for requirement in app_metadata.requires:
                if requirement.startswith("core."):
                    # Çekirdek modül kontrolü
                    if requirement not in self.supported_modules:
                        errors.append(f"Unsupported core module: {requirement}")
                    elif self.kernel:
                        module = self.kernel.get_module(requirement.replace("core.", ""))
                        if not module:
                            errors.append(f"Core module not available: {requirement}")
                
                elif requirement.startswith("python:"):
                    # Python paketi kontrolü
                    package_name = requirement.replace("python:", "")
                    if not self._check_python_package(package_name):
                        errors.append(f"Python package not available: {package_name}")
                
                else:
                    errors.append(f"Unknown requirement format: {requirement}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Requirement validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    def create_module_bridge(self, app_id: str, app_metadata: AppMetadata) -> bool:
        """Uygulama için modül köprüsü oluştur"""
        try:
            bridge_config = {
                "app_id": app_id,
                "app_name": app_metadata.name,
                "connected_modules": {},
                "permissions": app_metadata.permissions.copy(),
                "created_at": datetime.now().isoformat()
            }
            
            # Her gerekli modül için bağlantı oluştur
            for requirement in app_metadata.requires:
                if requirement.startswith("core."):
                    module_name = requirement.replace("core.", "")
                    
                    if self.kernel:
                        module = self.kernel.get_module(module_name)
                        if module:
                            bridge_config["connected_modules"][requirement] = {
                                "module_name": module_name,
                                "connection_status": "connected",
                                "connected_at": datetime.now().isoformat()
                            }
                            self.logger.info(f"Connected {app_id} to {requirement}")
                        else:
                            bridge_config["connected_modules"][requirement] = {
                                "module_name": module_name,
                                "connection_status": "failed",
                                "error": "Module not available"
                            }
                            self.logger.warning(f"Failed to connect {app_id} to {requirement}")
            
            # Bridge config'i kaydet
            self.module_connections[app_id] = bridge_config
            self._save_bridge_config(app_id, bridge_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create module bridge for {app_id}: {e}")
            return False
    
    def remove_module_bridge(self, app_id: str) -> bool:
        """Uygulama modül köprüsünü kaldır"""
        try:
            if app_id in self.module_connections:
                del self.module_connections[app_id]
            
            # Bridge config dosyasını sil
            bridge_file = Path(f"system/config/bridges/{app_id}.json")
            if bridge_file.exists():
                bridge_file.unlink()
            
            self.logger.info(f"Removed module bridge for {app_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove module bridge for {app_id}: {e}")
            return False
    
    def get_app_bridge_info(self, app_id: str) -> Optional[Dict]:
        """Uygulama köprü bilgisini al"""
        return self.module_connections.get(app_id)
    
    def _check_python_package(self, package_name: str) -> bool:
        """Python paketinin varlığını kontrol et"""
        try:
            import importlib
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False
    
    def _save_bridge_config(self, app_id: str, config: Dict):
        """Bridge config'ini kaydet"""
        try:
            bridge_dir = Path("system/config/bridges")
            bridge_dir.mkdir(parents=True, exist_ok=True)
            
            bridge_file = bridge_dir / f"{app_id}.json"
            with open(bridge_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save bridge config for {app_id}: {e}")

class PermissionManager:
    """Uygulama izin yöneticisi - cursorrules genişletmesi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("PermissionManager")
        
        # Desteklenen izin türleri
        self.supported_permissions = {
            "fs.read": "Dosya okuma izni",
            "fs.write": "Dosya yazma izni", 
            "network": "Ağ erişim izni",
            "audio": "Ses sistemi izni",
            "camera": "Kamera erişim izni",
            "microphone": "Mikrofon erişim izni",
            "location": "Konum erişim izni",
            "notifications": "Bildirim gönderme izni",
            "system": "Sistem seviyesi erişim izni"
        }
        
        # Uygulama izinleri cache
        self.app_permissions: Dict[str, Dict] = {}
        self._load_permissions()
    
    def validate_permissions(self, app_metadata: AppMetadata) -> tuple[bool, List[str]]:
        """Uygulama izinlerini doğrula"""
        errors = []
        warnings = []
        
        try:
            for permission, granted in app_metadata.permissions.items():
                if permission not in self.supported_permissions:
                    warnings.append(f"Unknown permission: {permission}")
                
                if not isinstance(granted, bool):
                    errors.append(f"Permission value must be boolean: {permission}")
                
                # Kritik izinler için ek kontrol
                if permission == "system" and granted:
                    warnings.append("System permission requested - requires admin approval")
                
                if permission in ["fs.write", "network"] and granted:
                    self.logger.info(f"High-risk permission requested: {permission}")
            
            if warnings:
                self.logger.warning(f"Permission warnings: {warnings}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Permission validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    def grant_permissions(self, app_id: str, app_metadata: AppMetadata) -> bool:
        """Uygulamaya izinleri ver"""
        try:
            # İzinleri kaydet
            permission_record = {
                "app_id": app_id,
                "app_name": app_metadata.name,
                "permissions": app_metadata.permissions.copy(),
                "granted_at": datetime.now().isoformat(),
                "granted_by": "system"  # Gelecekte kullanıcı onayı eklenebilir
            }
            
            self.app_permissions[app_id] = permission_record
            self._save_permissions()
            
            # Security modülüne bildir
            if self.kernel:
                security = self.kernel.get_module("security")
                if security and hasattr(security, 'register_app_permissions'):
                    security.register_app_permissions(app_id, app_metadata.permissions)
            
            self.logger.info(f"Granted permissions to {app_id}: {list(app_metadata.permissions.keys())}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to grant permissions to {app_id}: {e}")
            return False
    
    def revoke_permissions(self, app_id: str) -> bool:
        """Uygulama izinlerini iptal et"""
        try:
            if app_id in self.app_permissions:
                del self.app_permissions[app_id]
                self._save_permissions()
            
            # Security modülüne bildir
            if self.kernel:
                security = self.kernel.get_module("security")
                if security and hasattr(security, 'revoke_app_permissions'):
                    security.revoke_app_permissions(app_id)
            
            self.logger.info(f"Revoked permissions for {app_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke permissions for {app_id}: {e}")
            return False
    
    def check_permission(self, app_id: str, permission: str) -> bool:
        """Uygulama iznini kontrol et"""
        try:
            if app_id not in self.app_permissions:
                return False
            
            permissions = self.app_permissions[app_id]["permissions"]
            return permissions.get(permission, False)
            
        except Exception as e:
            self.logger.error(f"Permission check failed for {app_id}.{permission}: {e}")
            return False
    
    def get_app_permissions(self, app_id: str) -> Dict:
        """Uygulama izinlerini al"""
        return self.app_permissions.get(app_id, {})
    
    def _load_permissions(self):
        """İzinleri yükle"""
        try:
            permissions_file = Path("system/config/app_permissions.json")
            if permissions_file.exists():
                with open(permissions_file, 'r', encoding='utf-8') as f:
                    self.app_permissions = json.load(f)
                
                self.logger.info(f"Loaded permissions for {len(self.app_permissions)} apps")
                
        except Exception as e:
            self.logger.error(f"Failed to load permissions: {e}")
    
    def _save_permissions(self):
        """İzinleri kaydet"""
        try:
            permissions_file = Path("system/config/app_permissions.json")
            permissions_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(permissions_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_permissions, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save permissions: {e}")

class SandboxManager:
    """Uygulama sandbox yöneticisi - cursorrules genişletmesi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("SandboxManager")
        
        # Sandbox dizini
        self.sandbox_dir = Path("sandbox")
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Aktif sandbox'lar
        self.active_sandboxes: Dict[str, Dict] = {}
    
    def create_sandbox(self, app_id: str, app_metadata: AppMetadata) -> bool:
        """Uygulama için sandbox oluştur"""
        try:
            sandbox_path = self.sandbox_dir / app_id
            sandbox_path.mkdir(parents=True, exist_ok=True)
            
            # Sandbox config
            sandbox_config = {
                "app_id": app_id,
                "app_name": app_metadata.name,
                "sandbox_path": str(sandbox_path),
                "permissions": app_metadata.permissions.copy(),
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Sandbox alt dizinleri oluştur
            (sandbox_path / "temp").mkdir(exist_ok=True)
            (sandbox_path / "data").mkdir(exist_ok=True)
            (sandbox_path / "logs").mkdir(exist_ok=True)
            
            self.active_sandboxes[app_id] = sandbox_config
            self.logger.info(f"Created sandbox for {app_id} at {sandbox_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sandbox for {app_id}: {e}")
            return False
    
    def remove_sandbox(self, app_id: str) -> bool:
        """Uygulama sandbox'ını kaldır"""
        try:
            if app_id in self.active_sandboxes:
                sandbox_config = self.active_sandboxes[app_id]
                sandbox_path = Path(sandbox_config["sandbox_path"])
                
                if sandbox_path.exists():
                    shutil.rmtree(sandbox_path)
                
                del self.active_sandboxes[app_id]
                self.logger.info(f"Removed sandbox for {app_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove sandbox for {app_id}: {e}")
            return False
    
    def get_sandbox_path(self, app_id: str) -> Optional[str]:
        """Uygulama sandbox yolunu al"""
        if app_id in self.active_sandboxes:
            return self.active_sandboxes[app_id]["sandbox_path"]
        return None

class AppValidator:
    """Uygulama paketi doğrulayıcı"""
    
    def __init__(self):
        self.logger = logging.getLogger("AppValidator")
        self.required_files = ["app.json", "main.py", "icon.png"]
        self.optional_files = ["postinstall.py", "uninstall.py", "postupdate.py", "readme.md"]
    
    def validate_app_directory(self, app_path: Path) -> tuple[bool, List[str]]:
        """Uygulama dizinini doğrula"""
        errors = []
        
        try:
            # Gerekli dosyaları kontrol et
            for required_file in self.required_files:
                file_path = app_path / required_file
                if not file_path.exists():
                    errors.append(f"Required file missing: {required_file}")
                elif required_file == "app.json":
                    # app.json formatını kontrol et
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            app_data = json.load(f)
                        
                        # Gerekli alanları kontrol et
                        required_fields = ["id", "name", "version", "entry", "exec"]
                        for field in required_fields:
                            if field not in app_data:
                                errors.append(f"Required field missing in app.json: {field}")
                        
                        # Entry dosyasının varlığını kontrol et
                        entry_file = app_path / app_data.get("entry", "main.py")
                        if not entry_file.exists():
                            errors.append(f"Entry file not found: {app_data.get('entry', 'main.py')}")
                            
                    except json.JSONDecodeError as e:
                        errors.append(f"Invalid JSON in app.json: {e}")
                    except Exception as e:
                        errors.append(f"Error reading app.json: {e}")
            
            # Dizin yapısını kontrol et
            if not app_path.is_dir():
                errors.append("App path is not a directory")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False, [f"Validation failed: {e}"]
    
    def validate_app_zip(self, zip_path: Path) -> tuple[bool, List[str]]:
        """Zip paketini doğrula"""
        errors = []
        
        try:
            if not zip_path.exists() or not zip_path.suffix == '.zip':
                return False, ["Invalid zip file"]
            
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Gerekli dosyaları kontrol et
                for required_file in self.required_files:
                    if required_file not in file_list:
                        errors.append(f"Required file missing in zip: {required_file}")
                
                # app.json'ı kontrol et
                if "app.json" in file_list:
                    try:
                        app_json_data = zip_file.read("app.json")
                        app_data = json.loads(app_json_data.decode('utf-8'))
                        
                        # Gerekli alanları kontrol et
                        required_fields = ["id", "name", "version", "entry", "exec"]
                        for field in required_fields:
                            if field not in app_data:
                                errors.append(f"Required field missing in app.json: {field}")
                        
                        # Entry dosyasının zip içinde olduğunu kontrol et
                        entry_file = app_data.get("entry", "main.py")
                        if entry_file not in file_list:
                            errors.append(f"Entry file not found in zip: {entry_file}")
                            
                    except json.JSONDecodeError as e:
                        errors.append(f"Invalid JSON in app.json: {e}")
                    except Exception as e:
                        errors.append(f"Error reading app.json from zip: {e}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Zip validation error: {e}")
            return False, [f"Zip validation failed: {e}"]
    
    def verify_signature(self, app_path: Path, expected_signature: str) -> bool:
        """Uygulama imzasını doğrula"""
        try:
            # Basit SHA256 hash kontrolü
            hasher = hashlib.sha256()
            
            # Ana dosyaları hash'le
            for file_name in sorted(os.listdir(app_path)):
                file_path = app_path / file_name
                if file_path.is_file() and not file_name.startswith('.'):
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
            
            calculated_signature = hasher.hexdigest()
            return calculated_signature == expected_signature
            
        except Exception as e:
            self.logger.error(f"Signature verification error: {e}")
            return False

class AppInstaller:
    """Uygulama kurulum yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("AppInstaller")
        self.validator = AppValidator()
        self.apps_dir = Path("apps")
        self.backup_dir = Path("apps/.backup")
        self.trash_dir = Path("apps/.trash")
        
        # Dizinleri oluştur
        self.apps_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.trash_dir.mkdir(exist_ok=True)
    
    def install_from_directory(self, source_path: Path, force: bool = False) -> tuple[InstallResult, str]:
        """Dizinden uygulama kur"""
        try:
            # Doğrulama
            is_valid, errors = self.validator.validate_app_directory(source_path)
            if not is_valid:
                error_msg = "; ".join(errors)
                self.logger.error(f"Invalid app directory: {error_msg}")
                return InstallResult.INVALID_PACKAGE, error_msg
            
            # app.json oku
            app_json_path = source_path / "app.json"
            with open(app_json_path, 'r', encoding='utf-8') as f:
                app_data = json.load(f)
            
            metadata = AppMetadata.from_dict(app_data)
            
            # Hedef dizin
            target_path = self.apps_dir / metadata.id
            
            # Zaten kurulu mu kontrol et
            if target_path.exists() and not force:
                return InstallResult.ALREADY_INSTALLED, f"App {metadata.id} already installed"
            
            # Bağımlılık kontrolü
            if not self._check_dependencies(metadata.requires):
                return InstallResult.DEPENDENCY_ERROR, "Dependencies not satisfied"
            
            # Yedekleme (güncelleme durumunda)
            if target_path.exists():
                self._backup_app(metadata.id)
            
            # Kurulum
            if target_path.exists():
                shutil.rmtree(target_path)
            
            shutil.copytree(source_path, target_path)
            
            # İzinleri ayarla
            self._set_permissions(target_path)
            
            # Post-install script çalıştır
            if metadata.postinstall:
                self._run_script(target_path / metadata.postinstall, "postinstall")
            
            # Kurulum bilgisini kaydet
            self._save_app_info(metadata, target_path)
            
            # Event yayınla
            self._publish_event("APP_INSTALLED", {
                "app_id": metadata.id,
                "name": metadata.name,
                "version": metadata.version
            })
            
            self.logger.info(f"App installed successfully: {metadata.name} ({metadata.id})")
            return InstallResult.SUCCESS, f"App {metadata.name} installed successfully"
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            return InstallResult.FAILED, str(e)
    
    def install_from_zip(self, zip_path: Path, force: bool = False) -> tuple[InstallResult, str]:
        """Zip dosyasından uygulama kur"""
        try:
            # Doğrulama
            is_valid, errors = self.validator.validate_app_zip(zip_path)
            if not is_valid:
                error_msg = "; ".join(errors)
                self.logger.error(f"Invalid app zip: {error_msg}")
                return InstallResult.INVALID_PACKAGE, error_msg
            
            # Geçici dizine çıkart
            temp_dir = Path("temp") / f"app_install_{int(datetime.now().timestamp())}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_file:
                    zip_file.extractall(temp_dir)
                
                # Dizinden kurulum yap
                result, message = self.install_from_directory(temp_dir, force)
                
                return result, message
                
            finally:
                # Geçici dizini temizle
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"Zip installation failed: {e}")
            return InstallResult.FAILED, str(e)
    
    def uninstall_app(self, app_id: str, keep_data: bool = False) -> tuple[bool, str]:
        """Uygulamayı kaldır"""
        try:
            app_path = self.apps_dir / app_id
            
            if not app_path.exists():
                return False, f"App {app_id} not found"
            
            # app.json oku
            app_json_path = app_path / "app.json"
            if app_json_path.exists():
                with open(app_json_path, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)
                
                metadata = AppMetadata.from_dict(app_data)
                
                # Uninstall script çalıştır
                if metadata.uninstall:
                    self._run_script(app_path / metadata.uninstall, "uninstall")
            
            # Çöp kutusuna taşı
            if not keep_data:
                trash_path = self.trash_dir / f"{app_id}_{int(datetime.now().timestamp())}"
                shutil.move(str(app_path), str(trash_path))
            else:
                shutil.rmtree(app_path)
            
            # Kurulum bilgisini sil
            self._remove_app_info(app_id)
            
            # Event yayınla
            self._publish_event("APP_UNINSTALLED", {
                "app_id": app_id
            })
            
            self.logger.info(f"App uninstalled: {app_id}")
            return True, f"App {app_id} uninstalled successfully"
            
        except Exception as e:
            self.logger.error(f"Uninstall failed: {e}")
            return False, str(e)
    
    def update_app(self, app_id: str, source_path: Path) -> tuple[InstallResult, str]:
        """Uygulamayı güncelle"""
        try:
            # Mevcut sürümü yedekle
            current_path = self.apps_dir / app_id
            if current_path.exists():
                backup_result = self._backup_app(app_id)
                if not backup_result:
                    return InstallResult.FAILED, "Failed to backup current version"
            
            # Yeni sürümü kur
            result, message = self.install_from_directory(source_path, force=True)
            
            if result == InstallResult.SUCCESS:
                # Post-update script çalıştır
                app_json_path = current_path / "app.json"
                if app_json_path.exists():
                    with open(app_json_path, 'r', encoding='utf-8') as f:
                        app_data = json.load(f)
                    
                    metadata = AppMetadata.from_dict(app_data)
                    if metadata.postupdate:
                        self._run_script(current_path / metadata.postupdate, "postupdate")
                
                # Event yayınla
                self._publish_event("APP_UPDATED", {
                    "app_id": app_id
                })
            
            return result, message
            
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            return InstallResult.FAILED, str(e)
    
    def _check_dependencies(self, requires: List[str]) -> bool:
        """Bağımlılıkları kontrol et"""
        try:
            for requirement in requires:
                if requirement == "python3":
                    # Python kontrolü
                    try:
                        result = subprocess.run(["python3", "--version"], 
                                              capture_output=True, text=True)
                        if result.returncode != 0:
                            self.logger.warning("Python3 not found")
                            return False
                    except FileNotFoundError:
                        self.logger.warning("Python3 not found")
                        return False
                
                elif requirement.startswith("app:"):
                    # Başka uygulama bağımlılığı
                    dep_app_id = requirement[4:]
                    dep_path = self.apps_dir / dep_app_id
                    if not dep_path.exists():
                        self.logger.warning(f"Dependency app not found: {dep_app_id}")
                        return False
                
                # Diğer bağımlılık türleri buraya eklenebilir
            
            return True
            
        except Exception as e:
            self.logger.error(f"Dependency check failed: {e}")
            return False
    
    def _backup_app(self, app_id: str) -> bool:
        """Uygulamayı yedekle"""
        try:
            app_path = self.apps_dir / app_id
            if not app_path.exists():
                return False
            
            # Sürüm bilgisini al
            version = "unknown"
            app_json_path = app_path / "app.json"
            if app_json_path.exists():
                with open(app_json_path, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)
                version = app_data.get("version", "unknown")
            
            # Yedek dizini
            backup_name = f"{app_id}_{version}_{int(datetime.now().timestamp())}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copytree(app_path, backup_path)
            
            self.logger.info(f"App backed up: {app_id} -> {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def _set_permissions(self, app_path: Path):
        """Uygulama izinlerini ayarla"""
        try:
            # Unix sistemlerde executable izni ver
            if os.name == 'posix':
                for file_path in app_path.rglob("*.py"):
                    os.chmod(file_path, 0o755)
                
                for file_path in app_path.rglob("*.sh"):
                    os.chmod(file_path, 0o755)
                    
        except Exception as e:
            self.logger.warning(f"Failed to set permissions: {e}")
    
    def _run_script(self, script_path: Path, script_type: str):
        """Script çalıştır"""
        try:
            if not script_path.exists():
                return
            
            self.logger.info(f"Running {script_type} script: {script_path}")
            
            if script_path.suffix == '.py':
                result = subprocess.run([
                    "python3", str(script_path)
                ], capture_output=True, text=True, timeout=60)
            elif script_path.suffix == '.sh':
                result = subprocess.run([
                    "bash", str(script_path)
                ], capture_output=True, text=True, timeout=60)
            else:
                self.logger.warning(f"Unknown script type: {script_path}")
                return
            
            if result.returncode != 0:
                self.logger.error(f"Script failed: {result.stderr}")
            else:
                self.logger.info(f"Script completed successfully")
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Script timeout: {script_path}")
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
    
    def _save_app_info(self, metadata: AppMetadata, install_path: Path):
        """Kurulum bilgisini kaydet"""
        try:
            # Kurulum boyutunu hesapla
            install_size = 0
            for file_path in install_path.rglob("*"):
                if file_path.is_file():
                    install_size += file_path.stat().st_size
            
            install_size_mb = install_size / 1024 / 1024
            
            app_info = AppInfo(
                metadata=metadata,
                status=AppStatus.INSTALLED,
                install_path=str(install_path),
                installed_at=datetime.now().isoformat(),
                install_size_mb=install_size_mb
            )
            
            # Sistem kayıt dosyasına yaz
            registry_file = Path("system/config/app_registry.json")
            registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            registry = {}
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            
            registry[metadata.id] = app_info.to_dict()
            
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save app info: {e}")
    
    def _remove_app_info(self, app_id: str):
        """Kurulum bilgisini sil"""
        try:
            registry_file = Path("system/config/app_registry.json")
            if not registry_file.exists():
                return
            
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            if app_id in registry:
                del registry[app_id]
                
                with open(registry_file, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            self.logger.error(f"Failed to remove app info: {e}")
    
    def _publish_event(self, event_type: str, data: Dict):
        """Event yayınla"""
        try:
            if self.kernel:
                events = self.kernel.get_module("events")
                if events:
                    from core.events import Event, EventPriority
                    event = Event(event_type, data, source="AppInstaller", 
                                priority=EventPriority.NORMAL)
                    events.publish(event)
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")

@dataclass
class AppInfo:
    """Kurulu uygulama bilgi sınıfı"""
    metadata: AppMetadata
    status: AppStatus
    install_path: str
    installed_at: str
    updated_at: str = ""
    install_size_mb: float = 0.0
    last_error: str = ""
    backup_path: str = ""
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['metadata'] = self.metadata.to_dict()
        data['status'] = self.status.value
        return data

class AppKit:
    """Ana AppKit sınıfı"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("AppKit")
        self.installer = AppInstaller(kernel)
        self.validator = AppValidator()
        
        # Yeni genişletme sistemleri - cursorrules
        self.module_adapter = ModuleAdapter(kernel)
        self.permission_manager = PermissionManager(kernel)
        self.sandbox_manager = SandboxManager(kernel)
        
        # Kurulu uygulamalar cache
        self._installed_apps_cache: Dict[str, AppInfo] = {}
        self._cache_valid = False
        
        # Genişletme ayarları
        self.enable_module_adaptation = True
        self.enable_permission_system = True
        self.enable_sandbox_mode = True
        self.log_adaptations = True
        
        self._load_installed_apps()
    
    def _load_installed_apps(self):
        """Kurulu uygulamaları yükle"""
        try:
            registry_file = Path("system/config/app_registry.json")
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                
                for app_id, app_data in registry.items():
                    try:
                        # Metadata'yı yeniden oluştur
                        metadata = AppMetadata.from_dict(app_data['metadata'])
                        
                        app_info = AppInfo(
                            metadata=metadata,
                            status=AppStatus(app_data['status']),
                            install_path=app_data['install_path'],
                            installed_at=app_data['installed_at'],
                            updated_at=app_data.get('updated_at', ''),
                            install_size_mb=app_data.get('install_size_mb', 0.0),
                            last_error=app_data.get('last_error', ''),
                            backup_path=app_data.get('backup_path', '')
                        )
                        
                        self._installed_apps_cache[app_id] = app_info
                        
                    except Exception as e:
                        self.logger.error(f"Failed to load app info for {app_id}: {e}")
                
                self._cache_valid = True
                self.logger.info(f"Loaded {len(self._installed_apps_cache)} installed apps")
                
        except Exception as e:
            self.logger.error(f"Failed to load installed apps: {e}")
    
    def install_app(self, source: Union[str, Path], force: bool = False) -> tuple[InstallResult, str]:
        """Uygulama kur - genişletilmiş versiyon"""
        source_path = Path(source)
        
        try:
            # Temel kurulum
            if source_path.is_dir():
                result, message = self.installer.install_from_directory(source_path, force)
            elif source_path.suffix == '.zip':
                result, message = self.installer.install_from_zip(source_path, force)
            else:
                return InstallResult.INVALID_PACKAGE, "Invalid source format"
            
            # Kurulum başarılıysa genişletme işlemlerini yap
            if result == InstallResult.SUCCESS:
                # app.json'dan metadata al
                app_json_path = None
                if source_path.is_dir():
                    app_json_path = source_path / "app.json"
                else:
                    # Zip'ten çıkarılan dizini bul
                    temp_dir = Path("temp")
                    for item in temp_dir.iterdir():
                        if item.is_dir() and (item / "app.json").exists():
                            app_json_path = item / "app.json"
                            break
                
                if app_json_path and app_json_path.exists():
                    with open(app_json_path, 'r', encoding='utf-8') as f:
                        app_data = json.load(f)
                    
                    metadata = AppMetadata.from_dict(app_data)
                    
                    # Modül adaptasyonu (cursorrules özelliği)
                    if self.enable_module_adaptation and metadata.requires:
                        adaptation_success = self._perform_module_adaptation(metadata)
                        if not adaptation_success:
                            self.logger.warning(f"Module adaptation failed for {metadata.id}")
                            if self.log_adaptations:
                                self.logger.error(f"App {metadata.id} may not work properly due to module adaptation failure")
                    
                    # İzin sistemi (cursorrules özelliği)
                    if self.enable_permission_system and metadata.permissions:
                        permission_success = self._setup_permissions(metadata)
                        if not permission_success:
                            self.logger.warning(f"Permission setup failed for {metadata.id}")
                    
                    # Sandbox oluşturma (cursorrules özelliği)
                    if self.enable_sandbox_mode:
                        sandbox_success = self._create_app_sandbox(metadata)
                        if not sandbox_success:
                            self.logger.warning(f"Sandbox creation failed for {metadata.id}")
            
            # Cache'i güncelle
            if result == InstallResult.SUCCESS:
                self._cache_valid = False
                self._load_installed_apps()
            
            return result, message
            
        except Exception as e:
            self.logger.error(f"Enhanced install failed: {e}")
            return InstallResult.FAILED, str(e)
    
    def uninstall_app(self, app_id: str, keep_data: bool = False) -> tuple[bool, str]:
        """Uygulamayı kaldır - genişletilmiş versiyon"""
        try:
            # Genişletme temizliği
            if self.enable_module_adaptation:
                self.module_adapter.remove_module_bridge(app_id)
            
            if self.enable_permission_system:
                self.permission_manager.revoke_permissions(app_id)
            
            if self.enable_sandbox_mode:
                self.sandbox_manager.remove_sandbox(app_id)
            
            # Temel kaldırma
            result, message = self.installer.uninstall_app(app_id, keep_data)
            
            # Cache'i güncelle
            if result:
                self._installed_apps_cache.pop(app_id, None)
            
            return result, message
            
        except Exception as e:
            self.logger.error(f"Enhanced uninstall failed: {e}")
            return False, str(e)
    
    def update_app(self, app_id: str, source: Union[str, Path]) -> tuple[InstallResult, str]:
        """Uygulamayı güncelle"""
        source_path = Path(source)
        result, message = self.installer.update_app(app_id, source_path)
        
        # Cache'i güncelle
        if result == InstallResult.SUCCESS:
            self._cache_valid = False
            self._load_installed_apps()
        
        return result, message
    
    def _perform_module_adaptation(self, metadata: AppMetadata) -> bool:
        """Uygulama modül adaptasyonunu gerçekleştir - cursorrules entegrasyonu"""
        try:
            # Modül adaptörü ile gereksinim doğrulama
            is_valid, errors = self.module_adapter.validate_requirements(metadata)
            if not is_valid:
                self.logger.error(f"Module adaptation failed for {metadata.id}: {errors}")
                return False
            
            # Bridge bağlantıları oluştur
            if not self.module_adapter.create_module_bridge(metadata.id, metadata):
                self.logger.error(f"Failed to create module bridge for {metadata.id}")
                return False
            
            # Bridge manager ile entegrasyon
            if self.kernel and hasattr(self.kernel, 'bridge') and self.kernel.bridge:
                from core.bridge import PermissionLevel
                
                # Her gerekli modül için bridge bağlantısı kur
                for requirement in metadata.requires:
                    if requirement.startswith("core."):
                        module_name = requirement.replace("core.", "")
                        
                        # İzin seviyesini belirle
                        permission_level = PermissionLevel.READ
                        if metadata.permissions.get(f"{requirement}.write", False):
                            permission_level = PermissionLevel.WRITE
                        elif metadata.permissions.get(f"{requirement}.full", False):
                            permission_level = PermissionLevel.FULL
                        
                        # Bridge bağlantısı kur
                        success = self.kernel.bridge.connect_app_to_module(
                            metadata.id, metadata.name, module_name, permission_level
                        )
                        
                        if success:
                            self.logger.info(f"Bridge connection established: {metadata.id} -> {module_name}")
                        else:
                            self.logger.warning(f"Bridge connection failed: {metadata.id} -> {module_name}")
            
            self.logger.info(f"Module adaptation completed for {metadata.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Module adaptation error for {metadata.id}: {e}")
            return False
    
    def _setup_permissions(self, metadata: AppMetadata) -> bool:
        """İzin sistemi kurulumu"""
        try:
            # İzinleri doğrula
            is_valid, errors = self.permission_manager.validate_permissions(metadata)
            if not is_valid:
                self.logger.error(f"Permission validation failed for {metadata.id}: {errors}")
                return False
            
            # İzinleri ver
            permission_success = self.permission_manager.grant_permissions(metadata.id, metadata)
            if not permission_success:
                self.logger.error(f"Permission granting failed for {metadata.id}")
                return False
            
            self.logger.info(f"Permissions setup completed for {metadata.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Permission setup error for {metadata.id}: {e}")
            return False
    
    def _create_app_sandbox(self, metadata: AppMetadata) -> bool:
        """Uygulama sandbox'ı oluştur"""
        try:
            sandbox_success = self.sandbox_manager.create_sandbox(metadata.id, metadata)
            if not sandbox_success:
                self.logger.error(f"Sandbox creation failed for {metadata.id}")
                return False
            
            self.logger.info(f"Sandbox created for {metadata.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Sandbox creation error for {metadata.id}: {e}")
            return False
    
    # Yeni API metodları - cursorrules genişletmeleri
    
    def get_app_bridge_info(self, app_id: str) -> Optional[Dict]:
        """Uygulama modül köprü bilgisini al"""
        if not self.enable_module_adaptation:
            return None
        return self.module_adapter.get_app_bridge_info(app_id)
    
    def get_app_permissions(self, app_id: str) -> Dict:
        """Uygulama izinlerini al"""
        if not self.enable_permission_system:
            return {}
        return self.permission_manager.get_app_permissions(app_id)
    
    def check_app_permission(self, app_id: str, permission: str) -> bool:
        """Uygulama iznini kontrol et"""
        if not self.enable_permission_system:
            return False
        return self.permission_manager.check_permission(app_id, permission)
    
    def get_app_sandbox_path(self, app_id: str) -> Optional[str]:
        """Uygulama sandbox yolunu al"""
        if not self.enable_sandbox_mode:
            return None
        return self.sandbox_manager.get_sandbox_path(app_id)
    
    def validate_app_manifest(self, source: Union[str, Path]) -> tuple[bool, List[str]]:
        """Uygulama manifest'ini doğrula"""
        try:
            source_path = Path(source)
            
            if source_path.is_dir():
                app_json_path = source_path / "app.json"
            else:
                return False, ["Source must be a directory"]
            
            if not app_json_path.exists():
                return False, ["app.json not found"]
            
            with open(app_json_path, 'r', encoding='utf-8') as f:
                app_data = json.load(f)
            
            metadata = AppMetadata.from_dict(app_data)
            
            # Temel doğrulama
            basic_valid, basic_errors = self.validator.validate_app_directory(source_path)
            if not basic_valid:
                return False, basic_errors
            
            # Genişletme doğrulamaları
            all_errors = []
            
            if self.enable_module_adaptation and metadata.requires:
                req_valid, req_errors = self.module_adapter.validate_requirements(metadata)
                if not req_valid:
                    all_errors.extend(req_errors)
            
            if self.enable_permission_system and metadata.permissions:
                perm_valid, perm_errors = self.permission_manager.validate_permissions(metadata)
                if not perm_valid:
                    all_errors.extend(perm_errors)
            
            return len(all_errors) == 0, all_errors
            
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def get_adaptation_stats(self) -> Dict:
        """Adaptasyon istatistiklerini al"""
        try:
            stats = {
                "module_adaptation_enabled": self.enable_module_adaptation,
                "permission_system_enabled": self.enable_permission_system,
                "sandbox_mode_enabled": self.enable_sandbox_mode,
                "total_apps": len(self._installed_apps_cache),
                "apps_with_requirements": 0,
                "apps_with_permissions": 0,
                "apps_with_sandbox": 0
            }
            
            for app_info in self._installed_apps_cache.values():
                if app_info.metadata.requires:
                    stats["apps_with_requirements"] += 1
                if app_info.metadata.permissions:
                    stats["apps_with_permissions"] += 1
                if self.sandbox_manager.get_sandbox_path(app_info.metadata.id):
                    stats["apps_with_sandbox"] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to generate adaptation stats: {e}")
            return {}
    
    def get_installed_apps(self) -> List[AppInfo]:
        """Kurulu uygulamaları al"""
        if not self._cache_valid:
            self._load_installed_apps()
        
        return list(self._installed_apps_cache.values())
    
    def get_app_info(self, app_id: str) -> Optional[AppInfo]:
        """Uygulama bilgisi al"""
        if not self._cache_valid:
            self._load_installed_apps()
        
        return self._installed_apps_cache.get(app_id)
    
    def is_app_installed(self, app_id: str) -> bool:
        """Uygulama kurulu mu?"""
        return app_id in self._installed_apps_cache
    
    def validate_app_package(self, source: Union[str, Path]) -> tuple[bool, List[str]]:
        """Uygulama paketini doğrula"""
        source_path = Path(source)
        
        if source_path.is_dir():
            return self.validator.validate_app_directory(source_path)
        elif source_path.suffix == '.zip':
            return self.validator.validate_app_zip(source_path)
        else:
            return False, ["Invalid package format"]
    
    def get_app_stats(self) -> Dict:
        """Uygulama istatistikleri"""
        try:
            if not self._cache_valid:
                self._load_installed_apps()
            
            total_apps = len(self._installed_apps_cache)
            total_size_mb = sum(app.install_size_mb for app in self._installed_apps_cache.values())
            
            # Kategoriye göre sayım
            category_counts = {}
            for app in self._installed_apps_cache.values():
                category = app.metadata.category
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Duruma göre sayım
            status_counts = {}
            for app in self._installed_apps_cache.values():
                status = app.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total_apps": total_apps,
                "total_size_mb": total_size_mb,
                "category_counts": category_counts,
                "status_counts": status_counts,
                "apps_directory": str(self.installer.apps_dir),
                "backup_directory": str(self.installer.backup_dir),
                "trash_directory": str(self.installer.trash_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate app stats: {e}")
            return {}
    
    def cleanup_trash(self, older_than_days: int = 7) -> int:
        """Çöp kutusunu temizle"""
        try:
            cleaned_count = 0
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (older_than_days * 24 * 3600)
            
            for item in self.installer.trash_dir.iterdir():
                if item.is_dir():
                    # Dizin adından timestamp çıkar
                    try:
                        parts = item.name.split('_')
                        if len(parts) >= 2:
                            timestamp = float(parts[-1])
                            if timestamp < cutoff_time:
                                shutil.rmtree(item)
                                cleaned_count += 1
                                self.logger.info(f"Cleaned trash item: {item.name}")
                    except (ValueError, IndexError):
                        # Timestamp parse edilemezse, dosya tarihine bak
                        if item.stat().st_mtime < cutoff_time:
                            shutil.rmtree(item)
                            cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Trash cleanup failed: {e}")
            return 0
    
    def shutdown(self):
        """Modül kapatma"""
        self.logger.info("AppKit shutdown completed")

# Kolaylık fonksiyonları
_appkit = None

def init_appkit(kernel=None):
    """AppKit'i başlat"""
    global _appkit
    _appkit = AppKit(kernel)
    return _appkit

def get_appkit() -> Optional[AppKit]:
    """AppKit'i al"""
    return _appkit 