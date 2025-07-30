"""
Core FS Mount - Disk ve Sanal Alan Yöneticisi
Fiziksel disk takma, sanal alan yaratma, uygulama sandbox'lama
"""

import os
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from enum import Enum

class MountType(Enum):
    """Mount türleri"""
    PHYSICAL = "physical"
    RAMDISK = "ramdisk" 
    TEMPFS = "tempfs"
    SANDBOX = "sandbox"
    NETWORK = "network"

class MountPermission(Enum):
    """Mount izinleri"""
    READ_ONLY = "ro"
    READ_WRITE = "rw"
    NO_EXEC = "noexec"
    NO_SUID = "nosuid"

class MountManager:
    """
    Disk ve sanal dosya alanlarının yönetimi:
    - Fiziksel disk takma
    - Sanal alan yaratma  
    - Uygulama sandbox'lama
    """
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("MountManager")
        
        # Aktif mount'lar
        self.active_mounts: Dict[str, Dict[str, Any]] = {}
        
        # Sistem mount noktaları
        self.system_mounts = {
            "system": "/system",
            "apps": "/apps", 
            "users": "/users",
            "temp": "/temp",
            "logs": "/logs"
        }
        
        # Mount ayarları
        self.mount_config = {
            "max_ramdisk_size": "256MB",
            "auto_detect_usb": True,
            "sandbox_size_limit": "100MB",
            "temp_cleanup_interval": 3600  # saniye
        }
        
        self._init_system_mounts()
    
    def _init_system_mounts(self):
        """Sistem mount noktalarını başlat"""
        try:
            for mount_name, mount_path in self.system_mounts.items():
                # Dizin oluştur
                Path(mount_path.lstrip('/')).mkdir(parents=True, exist_ok=True)
                
                # Virtual mount kaydı
                self.active_mounts[mount_name] = {
                    "id": f"system_{mount_name}",
                    "type": MountType.PHYSICAL.value,
                    "source": mount_path,
                    "target": mount_path,
                    "permissions": [MountPermission.READ_WRITE.value],
                    "created": datetime.now().isoformat(),
                    "is_system": True,
                    "auto_mounted": True
                }
                
            self.logger.info("System mounts initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system mounts: {e}")
    
    def create_ramdisk(self, mount_id: str, size_mb: int = 64, mount_point: Optional[str] = None) -> bool:
        """RAMDisk oluştur"""
        try:
            if mount_id in self.active_mounts:
                self.logger.warning(f"Mount already exists: {mount_id}")
                return False
            
            # Mount noktası belirle
            if not mount_point:
                mount_point = f"temp/ramdisk_{mount_id}"
            
            mount_path = Path(mount_point)
            mount_path.mkdir(parents=True, exist_ok=True)
            
            # RAMDisk simülasyonu (gerçek RAMDisk için platform-specific kod)
            ramdisk_data = {
                "id": mount_id,
                "type": MountType.RAMDISK.value,
                "size_mb": size_mb,
                "mount_point": str(mount_path),
                "created": datetime.now().isoformat(),
                "files": {},  # Bellek içi dosya sistemi
                "usage_bytes": 0,
                "max_bytes": size_mb * 1024 * 1024
            }
            
            self.active_mounts[mount_id] = ramdisk_data
            
            self.logger.info(f"RAMDisk created: {mount_id} ({size_mb}MB) at {mount_point}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create RAMDisk {mount_id}: {e}")
            return False
    
    def create_tempfs(self, mount_id: str, mount_point: Optional[str] = None) -> bool:
        """TempFS oluştur (geçici dosya sistemi)"""
        try:
            if mount_id in self.active_mounts:
                return False
            
            if not mount_point:
                mount_point = f"temp/tempfs_{mount_id}"
            
            mount_path = Path(mount_point)
            mount_path.mkdir(parents=True, exist_ok=True)
            
            # TempFS kaydı
            tempfs_data = {
                "id": mount_id,
                "type": MountType.TEMPFS.value,
                "mount_point": str(mount_path),
                "created": datetime.now().isoformat(),
                "auto_cleanup": True,
                "permissions": [MountPermission.READ_WRITE.value],
                "temp_files": []
            }
            
            self.active_mounts[mount_id] = tempfs_data
            
            self.logger.info(f"TempFS created: {mount_id} at {mount_point}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create TempFS {mount_id}: {e}")
            return False
    
    def create_app_sandbox(self, app_id: str, size_limit_mb: int = 100) -> Optional[str]:
        """Uygulama için sandbox mount oluştur"""
        try:
            sandbox_id = f"sandbox_{app_id}_{uuid.uuid4().hex[:8]}"
            sandbox_path = f"temp/sandbox/{app_id}"
            
            mount_path = Path(sandbox_path)
            mount_path.mkdir(parents=True, exist_ok=True)
            
            # Sandbox yapılandırması
            sandbox_data = {
                "id": sandbox_id,
                "app_id": app_id,
                "type": MountType.SANDBOX.value,
                "mount_point": str(mount_path),
                "size_limit_mb": size_limit_mb,
                "created": datetime.now().isoformat(),
                "permissions": [
                    MountPermission.READ_WRITE.value,
                    MountPermission.NO_SUID.value
                ],
                "isolated": True,
                "auto_cleanup": True
            }
            
            self.active_mounts[sandbox_id] = sandbox_data
            
            self.logger.info(f"App sandbox created: {app_id} -> {sandbox_id}")
            return sandbox_id
            
        except Exception as e:
            self.logger.error(f"Failed to create app sandbox for {app_id}: {e}")
            return None
    
    def detect_external_devices(self) -> List[Dict[str, Any]]:
        """Harici aygıtları tespit et (USB, disk vb.)"""
        try:
            devices = []
            
            # Platform-specific disk tespiti
            if os.name == 'posix':  # Linux/macOS
                try:
                    # macOS için diskutil
                    if os.system('which diskutil > /dev/null 2>&1') == 0:
                        result = subprocess.run(['diskutil', 'list', '-plist'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            devices.append({
                                "name": "External Disk",
                                "device": "/dev/disk2",
                                "type": "external",
                                "size": "Unknown",
                                "filesystem": "APFS",
                                "mountable": True
                            })
                    
                    # Linux için lsblk  
                    elif os.system('which lsblk > /dev/null 2>&1') == 0:
                        result = subprocess.run(['lsblk', '-J'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            devices.append({
                                "name": "USB Drive",
                                "device": "/dev/sdb1",
                                "type": "usb",
                                "size": "8GB",
                                "filesystem": "ext4",
                                "mountable": True
                            })
                
                except subprocess.SubprocessError:
                    pass
            
            # Demo aygıt (gerçek tespit mevcut değilse)
            if not devices:
                devices.append({
                    "name": "Demo USB Drive",
                    "device": "/dev/demo_usb",
                    "type": "demo",
                    "size": "4GB",
                    "filesystem": "FAT32",
                    "mountable": True,
                    "demo": True
                })
            
            return devices
            
        except Exception as e:
            self.logger.error(f"Failed to detect external devices: {e}")
            return []
    
    def mount_external_device(self, device_path: str, mount_point: Optional[str] = None) -> Optional[str]:
        """Harici aygıtı mount et"""
        try:
            mount_id = f"external_{uuid.uuid4().hex[:8]}"
            
            if not mount_point:
                mount_point = f"temp/external/{mount_id}"
            
            mount_path = Path(mount_point)
            mount_path.mkdir(parents=True, exist_ok=True)
            
            # Mount simülasyonu (gerçek mount için platform-specific kod)
            external_data = {
                "id": mount_id,
                "type": MountType.PHYSICAL.value,
                "device": device_path,
                "mount_point": str(mount_path),
                "created": datetime.now().isoformat(),
                "permissions": [MountPermission.READ_WRITE.value],
                "external": True,
                "auto_unmount": True
            }
            
            self.active_mounts[mount_id] = external_data
            
            # Demo dosyalar oluştur
            if "demo" in device_path:
                demo_files = [
                    "README.txt",
                    "Photos/sunset.jpg",
                    "Documents/report.pdf",
                    "Music/song.mp3"
                ]
                
                for demo_file in demo_files:
                    file_path = mount_path / demo_file
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.touch()
            
            self.logger.info(f"External device mounted: {device_path} -> {mount_id}")
            return mount_id
            
        except Exception as e:
            self.logger.error(f"Failed to mount external device {device_path}: {e}")
            return None
    
    def unmount(self, mount_id: str) -> bool:
        """Mount'ı kaldır"""
        try:
            if mount_id not in self.active_mounts:
                return False
            
            mount_info = self.active_mounts[mount_id]
            
            # Sistem mount'ları korumalı
            if mount_info.get("is_system", False):
                self.logger.warning(f"Cannot unmount system mount: {mount_id}")
                return False
            
            # TempFS ve Sandbox temizliği
            if mount_info["type"] in [MountType.TEMPFS.value, MountType.SANDBOX.value]:
                mount_path = Path(mount_info["mount_point"])
                if mount_path.exists():
                    import shutil
                    shutil.rmtree(mount_path)
            
            # Mount kaydını sil
            del self.active_mounts[mount_id]
            
            self.logger.info(f"Unmounted: {mount_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unmount {mount_id}: {e}")
            return False
    
    def get_mount_info(self, mount_id: str) -> Optional[Dict[str, Any]]:
        """Mount bilgilerini al"""
        return self.active_mounts.get(mount_id)
    
    def list_mounts(self, mount_type: Optional[MountType] = None) -> List[Dict[str, Any]]:
        """Aktif mount'ları listele"""
        mounts = list(self.active_mounts.values())
        
        if mount_type:
            mounts = [m for m in mounts if m["type"] == mount_type.value]
        
        return mounts
    
    def get_mount_usage(self, mount_id: str) -> Dict[str, Any]:
        """Mount kullanım bilgilerini al"""
        try:
            if mount_id not in self.active_mounts:
                return {}
            
            mount_info = self.active_mounts[mount_id]
            mount_path = Path(mount_info["mount_point"])
            
            if not mount_path.exists():
                return {"error": "Mount point not found"}
            
            # Disk kullanımı hesapla
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(mount_path):
                file_count += len(files)
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
            
            usage_data = {
                "mount_id": mount_id,
                "type": mount_info["type"],
                "used_bytes": total_size,
                "used_human": self._format_size(total_size),
                "file_count": file_count,
                "mount_point": mount_info["mount_point"]
            }
            
            # RAMDisk için ekstra bilgi
            if mount_info["type"] == MountType.RAMDISK.value:
                max_bytes = mount_info.get("max_bytes", 0)
                usage_data.update({
                    "max_bytes": max_bytes,
                    "max_human": self._format_size(max_bytes),
                    "usage_percent": (total_size / max_bytes * 100) if max_bytes > 0 else 0
                })
            
            return usage_data
            
        except Exception as e:
            self.logger.error(f"Failed to get mount usage for {mount_id}: {e}")
            return {"error": str(e)}
    
    def _format_size(self, size_bytes: int) -> str:
        """Bytes'ı okunabilir formata çevir"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def cleanup_temp_mounts(self) -> int:
        """Geçici mount'ları temizle"""
        try:
            cleaned_count = 0
            mounts_to_remove = []
            
            for mount_id, mount_info in self.active_mounts.items():
                # Auto cleanup aktif olan mount'ları kontrol et
                if mount_info.get("auto_cleanup", False):
                    # 1 saatten eski tempfs/sandbox'ları temizle
                    created_time = datetime.fromisoformat(mount_info["created"])
                    age_hours = (datetime.now() - created_time).total_seconds() / 3600
                    
                    if age_hours > 1:  # 1 saat
                        mounts_to_remove.append(mount_id)
            
            # Cleanup işlemi
            for mount_id in mounts_to_remove:
                if self.unmount(mount_id):
                    cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} temporary mounts")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp mounts: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Mount istatistiklerini al"""
        type_counts = {}
        for mount_info in self.active_mounts.values():
            mount_type = mount_info["type"]
            type_counts[mount_type] = type_counts.get(mount_type, 0) + 1
        
        return {
            "total_mounts": len(self.active_mounts),
            "mount_types": type_counts,
            "system_mounts": len([m for m in self.active_mounts.values() if m.get("is_system", False)]),
            "external_mounts": len([m for m in self.active_mounts.values() if m.get("external", False)]),
            "module_name": "MountManager"
        } 