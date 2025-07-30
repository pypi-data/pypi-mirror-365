"""
PyCloud OS Python Environment
Python çalışma ortamını yöneten modül - yorumlayıcı, paket yönetimi ve uygulama uyumluluğu
"""

import os
import sys
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class PythonStatus(Enum):
    """Python durumları"""
    AVAILABLE = "available"
    NOT_FOUND = "not_found"
    VERSION_MISMATCH = "version_mismatch"
    PERMISSION_ERROR = "permission_error"

class PackageStatus(Enum):
    """Paket durumları"""
    INSTALLED = "installed"
    NOT_INSTALLED = "not_installed"
    OUTDATED = "outdated"
    UNKNOWN = "unknown"

@dataclass
class PythonInfo:
    """Python bilgileri"""
    version: str = ""
    executable: str = ""
    pip_available: bool = False
    pip_version: str = ""
    site_packages: str = ""
    status: PythonStatus = PythonStatus.NOT_FOUND
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PythonInfo':
        """Dict'ten oluştur"""
        data['status'] = PythonStatus(data.get('status', 'not_found'))
        return cls(**data)

@dataclass
class PackageInfo:
    """Paket bilgileri"""
    name: str
    version: str = ""
    latest_version: str = ""
    location: str = ""
    status: PackageStatus = PackageStatus.UNKNOWN
    required_by: List[str] = None
    
    def __post_init__(self):
        if self.required_by is None:
            self.required_by = []
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PackageInfo':
        """Dict'ten oluştur"""
        data['status'] = PackageStatus(data.get('status', 'unknown'))
        return cls(**data)

class PythonEnvironmentManager:
    """Python ortam yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("PythonEnvironmentManager")
        
        # Yapılandırma
        self.config_file = Path("system/config/python_runtime.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Python bilgileri
        self.python_info = PythonInfo()
        self.packages: Dict[str, PackageInfo] = {}
        
        # Ortam değişkenleri
        self.env_vars: Dict[str, str] = {}
        
        # Gereksinimler cache
        self.requirements_cache: Dict[str, List[str]] = {}
        
        # Thread lock
        self.lock = threading.Lock()
        
        # Başlangıç
        self.load_config()
        self.detect_python()
        self.scan_packages()
    
    def load_config(self):
        """Yapılandırmayı yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Python bilgilerini yükle
                if 'python_info' in config_data:
                    self.python_info = PythonInfo.from_dict(config_data['python_info'])
                
                # Ortam değişkenlerini yükle
                self.env_vars = config_data.get('env_vars', {})
                
                # Paket bilgilerini yükle
                packages_data = config_data.get('packages', {})
                for name, pkg_data in packages_data.items():
                    self.packages[name] = PackageInfo.from_dict(pkg_data)
            
            self.logger.info("Python environment config loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
    
    def save_config(self):
        """Yapılandırmayı kaydet"""
        try:
            config_data = {
                'python_info': self.python_info.to_dict(),
                'env_vars': self.env_vars,
                'packages': {name: pkg.to_dict() for name, pkg in self.packages.items()},
                'last_updated': self.get_current_timestamp()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def detect_python(self) -> bool:
        """Python yorumlayıcısını tespit et"""
        try:
            with self.lock:
                # Mevcut Python yorumlayıcısını kontrol et
                python_executable = sys.executable
                
                # Python sürümünü al
                version_info = sys.version_info
                version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
                
                # Site-packages dizinini bul
                import site
                site_packages = site.getsitepackages()[0] if site.getsitepackages() else ""
                
                # Pip kontrolü
                pip_available, pip_version = self.check_pip()
                
                # Python bilgilerini güncelle
                self.python_info = PythonInfo(
                    version=version_str,
                    executable=python_executable,
                    pip_available=pip_available,
                    pip_version=pip_version,
                    site_packages=site_packages,
                    status=PythonStatus.AVAILABLE
                )
                
                self.logger.info(f"Python detected: {version_str} at {python_executable}")
                self.save_config()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to detect Python: {e}")
            self.python_info.status = PythonStatus.NOT_FOUND
            return False
    
    def check_pip(self) -> Tuple[bool, str]:
        """Pip kontrolü"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # pip version output: "pip 21.0.1 from ..."
                pip_version = result.stdout.split()[1] if result.stdout.split() else ""
                return True, pip_version
            
            return False, ""
            
        except Exception as e:
            self.logger.warning(f"Pip check failed: {e}")
            return False, ""
    
    def scan_packages(self) -> bool:
        """Yüklü paketleri tara"""
        try:
            if not self.python_info.pip_available:
                self.logger.warning("Pip not available, cannot scan packages")
                return False
            
            with self.lock:
                # pip list ile yüklü paketleri al
                result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.logger.error(f"Failed to list packages: {result.stderr}")
                    return False
                
                packages_data = json.loads(result.stdout)
                
                # Paket bilgilerini güncelle
                self.packages.clear()
                for pkg_data in packages_data:
                    name = pkg_data['name']
                    version = pkg_data['version']
                    
                    package_info = PackageInfo(
                        name=name,
                        version=version,
                        status=PackageStatus.INSTALLED
                    )
                    
                    self.packages[name] = package_info
                
                self.logger.info(f"Scanned {len(self.packages)} packages")
                self.save_config()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to scan packages: {e}")
            return False
    
    def check_package(self, package_name: str) -> PackageInfo:
        """Paket durumunu kontrol et"""
        try:
            # Cache'den kontrol et
            if package_name in self.packages:
                return self.packages[package_name]
            
            # Pip ile kontrol et
            if self.python_info.pip_available:
                result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    # Paket yüklü
                    lines = result.stdout.strip().split('\n')
                    version = ""
                    location = ""
                    
                    for line in lines:
                        if line.startswith('Version:'):
                            version = line.split(':', 1)[1].strip()
                        elif line.startswith('Location:'):
                            location = line.split(':', 1)[1].strip()
                    
                    package_info = PackageInfo(
                        name=package_name,
                        version=version,
                        location=location,
                        status=PackageStatus.INSTALLED
                    )
                    
                    self.packages[package_name] = package_info
                    return package_info
                else:
                    # Paket yüklü değil
                    package_info = PackageInfo(
                        name=package_name,
                        status=PackageStatus.NOT_INSTALLED
                    )
                    return package_info
            
            # Pip yok, bilinmeyen durum
            return PackageInfo(name=package_name, status=PackageStatus.UNKNOWN)
            
        except Exception as e:
            self.logger.error(f"Failed to check package {package_name}: {e}")
            return PackageInfo(name=package_name, status=PackageStatus.UNKNOWN)
    
    def install_package(self, package_name: str, version: str = None) -> bool:
        """Paket yükle"""
        try:
            if not self.python_info.pip_available:
                self.logger.error("Pip not available for package installation")
                return False
            
            # Yükleme komutu
            install_cmd = [sys.executable, '-m', 'pip', 'install']
            
            if version:
                install_cmd.append(f"{package_name}=={version}")
            else:
                install_cmd.append(package_name)
            
            # Yükleme işlemi
            self.logger.info(f"Installing package: {package_name}")
            
            result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(f"Package installed successfully: {package_name}")
                
                # Paket bilgilerini güncelle
                package_info = self.check_package(package_name)
                self.packages[package_name] = package_info
                self.save_config()
                
                return True
            else:
                self.logger.error(f"Package installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install package {package_name}: {e}")
            return False
    
    def uninstall_package(self, package_name: str) -> bool:
        """Paket kaldır"""
        try:
            if not self.python_info.pip_available:
                self.logger.error("Pip not available for package uninstallation")
                return False
            
            # Kaldırma komutu
            uninstall_cmd = [sys.executable, '-m', 'pip', 'uninstall', '-y', package_name]
            
            self.logger.info(f"Uninstalling package: {package_name}")
            
            result = subprocess.run(uninstall_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info(f"Package uninstalled successfully: {package_name}")
                
                # Paket bilgilerini güncelle
                if package_name in self.packages:
                    del self.packages[package_name]
                
                self.save_config()
                return True
            else:
                self.logger.error(f"Package uninstallation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to uninstall package {package_name}: {e}")
            return False
    
    def check_app_requirements(self, app_id: str, requirements: List[str]) -> Dict[str, bool]:
        """Uygulama gereksinimlerini kontrol et"""
        try:
            results = {}
            
            for requirement in requirements:
                # Basit paket adı kontrolü (version specifier'lar için geliştirilmeli)
                package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].strip()
                
                package_info = self.check_package(package_name)
                results[requirement] = package_info.status == PackageStatus.INSTALLED
            
            # Cache'e kaydet
            self.requirements_cache[app_id] = requirements
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to check app requirements for {app_id}: {e}")
            return {req: False for req in requirements}
    
    def install_app_requirements(self, app_id: str, requirements: List[str]) -> bool:
        """Uygulama gereksinimlerini yükle"""
        try:
            if not requirements:
                return True
            
            self.logger.info(f"Installing requirements for {app_id}: {requirements}")
            
            success_count = 0
            for requirement in requirements:
                # Basit requirement parsing
                if '==' in requirement:
                    package_name, version = requirement.split('==', 1)
                    success = self.install_package(package_name.strip(), version.strip())
                else:
                    success = self.install_package(requirement.strip())
                
                if success:
                    success_count += 1
            
            all_success = success_count == len(requirements)
            
            if all_success:
                self.logger.info(f"All requirements installed for {app_id}")
            else:
                self.logger.warning(f"Some requirements failed for {app_id}: {success_count}/{len(requirements)}")
            
            return all_success
            
        except Exception as e:
            self.logger.error(f"Failed to install app requirements for {app_id}: {e}")
            return False
    
    def get_python_command(self, script_path: str, args: List[str] = None) -> List[str]:
        """Python komutunu oluştur"""
        try:
            if args is None:
                args = []
            
            cmd = [self.python_info.executable, script_path] + args
            return cmd
            
        except Exception as e:
            self.logger.error(f"Failed to create Python command: {e}")
            return []
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Ortam değişkenlerini al"""
        try:
            env = os.environ.copy()
            
            # Özel ortam değişkenlerini ekle
            env.update(self.env_vars)
            
            # Python path'ini ayarla
            if self.python_info.site_packages:
                pythonpath = env.get('PYTHONPATH', '')
                if pythonpath:
                    pythonpath = f"{self.python_info.site_packages}{os.pathsep}{pythonpath}"
                else:
                    pythonpath = self.python_info.site_packages
                
                env['PYTHONPATH'] = pythonpath
            
            return env
            
        except Exception as e:
            self.logger.error(f"Failed to get environment variables: {e}")
            return os.environ.copy()
    
    def run_python_script(self, script_path: str, args: List[str] = None, 
                         cwd: str = None, timeout: int = None) -> subprocess.CompletedProcess:
        """Python script çalıştır"""
        try:
            cmd = self.get_python_command(script_path, args)
            env = self.get_environment_variables()
            
            self.logger.info(f"Running Python script: {script_path}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=cwd, env=env, timeout=timeout)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to run Python script {script_path}: {e}")
            # Boş result döndür
            return subprocess.CompletedProcess([], 1, "", str(e))
    
    def validate_app_python_compatibility(self, app_id: str, app_config: Dict) -> bool:
        """Uygulama Python uyumluluğunu doğrula"""
        try:
            # Python sürüm kontrolü
            required_python = app_config.get('python_version')
            if required_python:
                current_version = tuple(map(int, self.python_info.version.split('.')))
                required_version = tuple(map(int, required_python.split('.')))
                
                if current_version < required_version:
                    self.logger.error(f"Python version mismatch for {app_id}: "
                                    f"required {required_python}, current {self.python_info.version}")
                    return False
            
            # Gerekli paketleri kontrol et
            requirements = app_config.get('requires', [])
            if requirements:
                requirement_results = self.check_app_requirements(app_id, requirements)
                missing_packages = [req for req, installed in requirement_results.items() if not installed]
                
                if missing_packages:
                    self.logger.warning(f"Missing packages for {app_id}: {missing_packages}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate Python compatibility for {app_id}: {e}")
            return False
    
    def get_package_list(self) -> List[Dict]:
        """Paket listesini al"""
        try:
            package_list = []
            
            for name, package_info in self.packages.items():
                package_list.append({
                    'name': name,
                    'version': package_info.version,
                    'status': package_info.status.value,
                    'location': package_info.location
                })
            
            return sorted(package_list, key=lambda x: x['name'])
            
        except Exception as e:
            self.logger.error(f"Failed to get package list: {e}")
            return []
    
    def get_system_info(self) -> Dict:
        """Sistem bilgilerini al"""
        try:
            return {
                'python_info': self.python_info.to_dict(),
                'package_count': len(self.packages),
                'env_vars': self.env_vars,
                'site_packages': self.python_info.site_packages
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}
    
    def repair_environment(self) -> bool:
        """Python ortamını onar"""
        try:
            self.logger.info("Repairing Python environment...")
            
            # Python'u yeniden tespit et
            if not self.detect_python():
                return False
            
            # Paketleri yeniden tara
            if not self.scan_packages():
                return False
            
            self.logger.info("Python environment repaired successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to repair environment: {e}")
            return False
    
    def get_current_timestamp(self) -> str:
        """Mevcut zaman damgası"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def shutdown(self):
        """Python environment manager'ı kapat"""
        try:
            self.save_config()
            self.packages.clear()
            self.requirements_cache.clear()
            
            self.logger.info("Python environment manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Python environment manager shutdown failed: {e}")

# Kolaylık fonksiyonları
_python_env_manager = None

def init_python_env_manager(kernel=None) -> PythonEnvironmentManager:
    """Python environment manager'ı başlat"""
    global _python_env_manager
    _python_env_manager = PythonEnvironmentManager(kernel)
    return _python_env_manager

def get_python_env_manager() -> Optional[PythonEnvironmentManager]:
    """Python environment manager'ı al"""
    return _python_env_manager

def check_package(package_name: str) -> bool:
    """Paket kontrolü (kısayol)"""
    if _python_env_manager:
        package_info = _python_env_manager.check_package(package_name)
        return package_info.status == PackageStatus.INSTALLED
    return False

def install_package(package_name: str, version: str = None) -> bool:
    """Paket yükle (kısayol)"""
    if _python_env_manager:
        return _python_env_manager.install_package(package_name, version)
    return False

def run_python_script(script_path: str, args: List[str] = None) -> subprocess.CompletedProcess:
    """Python script çalıştır (kısayol)"""
    if _python_env_manager:
        return _python_env_manager.run_python_script(script_path, args)
    return subprocess.CompletedProcess([], 1, "", "Python environment not available") 