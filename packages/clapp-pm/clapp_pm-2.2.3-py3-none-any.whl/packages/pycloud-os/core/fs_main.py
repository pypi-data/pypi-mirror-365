"""
PyCloud OS File System
Kalıcı dosya sistemi mimarisi - Python-dostu, klasör yapılı
"""

import os
import json
import shutil
import uuid
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict

# Alt modül import'ları
try:
    from .fs.userfs import UserFS
    from .fs.mount import MountManager
    from .fs.search import FileSearchEngine
    from .fs.vfs import PyCloudVFS
    FS_MODULES_AVAILABLE = True
except ImportError:
    FS_MODULES_AVAILABLE = False

try:
    from core.fs.vfs import VFSPermission  # VFSPermission enum'ını import et
except ImportError:
    # Fallback: VFS olmadan çalış
    class VFSPermission:
        READ = "read"
        WRITE = "write"
        DELETE = "delete"

@dataclass
class FileMetadata:
    """Dosya metadata bilgileri"""
    file_id: str
    name: str
    path: str
    size: int
    created_at: str
    modified_at: str
    accessed_at: str
    file_type: str
    permissions: str = "rw-r--r--"
    owner: str = "system"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class FileSystem:
    """PyCloud OS dosya sistemi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("FileSystem")
        self.base_path = Path.cwd()
        self.metadata_file = self.base_path / "system" / "fs_metadata.json"
        
        # Dosya metadata cache
        self.metadata_cache: Dict[str, FileMetadata] = {}
        
        # Sistem mount noktaları
        self.mount_points = {
            "system": self.base_path / "system",
            "apps": self.base_path / "apps", 
            "users": self.base_path / "users",
            "temp": self.base_path / "temp"
        }
        
        # Alt modüller
        self.userfs = None
        self.mount_manager = None
        self.search_engine = None
        self.vfs = None
        
        self.initialize()
        self._init_sub_modules()
    
    def _init_sub_modules(self):
        """Alt modülleri başlat"""
        try:
            if FS_MODULES_AVAILABLE:
                # VFS modülü - önce başlat (diğerleri buna bağımlı olabilir)
                self.vfs = PyCloudVFS(self.kernel)
                self.logger.info("PyCloudVFS module initialized")
                
                # UserFS modülü
                self.userfs = UserFS(self.kernel)
                self.logger.info("UserFS module initialized")
                
                # Mount Manager modülü  
                self.mount_manager = MountManager(self.kernel)
                self.logger.info("MountManager module initialized")
                
                # Search Engine modülü
                self.search_engine = FileSearchEngine(self.kernel)
                self.logger.info("FileSearchEngine module initialized")
            else:
                self.logger.warning("FS sub-modules not available")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize FS sub-modules: {e}")
            # VFS kritik önem taşıyorsa, en azından onu başlatmaya çalış
            try:
                if not self.vfs:
                    from .fs.vfs import PyCloudVFS
                    self.vfs = PyCloudVFS(self.kernel)
                    self.logger.info("VFS module loaded as fallback")
            except Exception as vfs_error:
                self.logger.error(f"Critical: VFS module failed to load: {vfs_error}")
    
    def initialize(self):
        """Dosya sistemini başlat"""
        try:
            # Ana dizinleri oluştur
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            for mount_name, mount_path in self.mount_points.items():
                mount_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Mount point created: {mount_name} -> {mount_path}")
            
            # Metadata dosyasını yükle
            self.load_metadata()
            
            # Sistem dizinlerini oluştur
            self._create_system_directories()
            
            self.logger.info("File system initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize file system: {e}")
            raise
    
    def _create_system_directories(self):
        """Sistem dizinlerini oluştur"""
        system_dirs = [
            "system/config",
            "system/themes",
            "system/icons", 
            "system/wallpapers",
            "system/security",
            "system/users",
            "temp/cache",
            "temp/downloads"
        ]
        
        for dir_path in system_dirs:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
    
    def load_metadata(self):
        """Metadata cache'i yükle"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata_data = json.load(f)
                
                for file_id, meta_dict in metadata_data.items():
                    self.metadata_cache[file_id] = FileMetadata(**meta_dict)
                
                self.logger.info(f"Loaded metadata for {len(self.metadata_cache)} files")
            
        except Exception as e:
            self.logger.error(f"Failed to load metadata: {e}")
    
    def save_metadata(self):
        """Metadata cache'i kaydet"""
        try:
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            metadata_data = {}
            for file_id, metadata in self.metadata_cache.items():
                metadata_data[file_id] = asdict(metadata)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
    
    def _generate_file_id(self) -> str:
        """Benzersiz dosya ID oluştur"""
        return str(uuid.uuid4())
    
    def _get_file_type(self, file_path: Path) -> str:
        """Dosya türünü belirle"""
        if file_path.is_dir():
            return "directory"
        
        suffix = file_path.suffix.lower()
        
        type_mapping = {
            '.txt': 'text',
            '.md': 'markdown',
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.mp4': 'video',
            '.avi': 'video',
            '.pdf': 'pdf',
            '.zip': 'archive',
            '.tar': 'archive',
            '.gz': 'archive'
        }
        
        return type_mapping.get(suffix, 'unknown')
    
    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """Yolu çözümle ve mutlak yol döndür"""
        if isinstance(path, str):
            path = Path(path)
        
        # Eğer göreli yol ise base_path'e ekle
        if not path.is_absolute():
            path = self.base_path / path
        
        return path.resolve()
    
    def exists(self, path: Union[str, Path]) -> bool:
        """Dosya/dizin var mı?"""
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.exists()
        except Exception:
            return False
    
    def is_file(self, path: Union[str, Path]) -> bool:
        """Dosya mı?"""
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.is_file()
        except Exception:
            return False
    
    def is_directory(self, path: Union[str, Path]) -> bool:
        """Dizin mi?"""
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.is_dir()
        except Exception:
            return False
    
    def create_file(self, path: Union[str, Path], content: str = "", 
                   owner: str = "system") -> Optional[str]:
        """Dosya oluştur"""
        try:
            resolved_path = self._resolve_path(path)
            
            # Üst dizini oluştur
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Dosyayı oluştur
            with open(resolved_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Metadata oluştur
            file_id = self._generate_file_id()
            now = datetime.now().isoformat()
            
            metadata = FileMetadata(
                file_id=file_id,
                name=resolved_path.name,
                path=str(resolved_path.relative_to(self.base_path)),
                size=len(content.encode('utf-8')),
                created_at=now,
                modified_at=now,
                accessed_at=now,
                file_type=self._get_file_type(resolved_path),
                owner=owner
            )
            
            self.metadata_cache[file_id] = metadata
            self.save_metadata()
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.FILE_CREATE, {
                "file_id": file_id,
                "path": str(resolved_path),
                "owner": owner
            }, source="FileSystem")
            
            self.logger.info(f"File created: {resolved_path}")
            return file_id
            
        except Exception as e:
            self.logger.error(f"Failed to create file {path}: {e}")
            return None
    
    def create_directory(self, path: Union[str, Path], owner: str = "system") -> Optional[str]:
        """Dizin oluştur"""
        try:
            resolved_path = self._resolve_path(path)
            resolved_path.mkdir(parents=True, exist_ok=True)
            
            # Metadata oluştur
            file_id = self._generate_file_id()
            now = datetime.now().isoformat()
            
            metadata = FileMetadata(
                file_id=file_id,
                name=resolved_path.name,
                path=str(resolved_path.relative_to(self.base_path)),
                size=0,
                created_at=now,
                modified_at=now,
                accessed_at=now,
                file_type="directory",
                owner=owner
            )
            
            self.metadata_cache[file_id] = metadata
            self.save_metadata()
            
            self.logger.info(f"Directory created: {resolved_path}")
            return file_id
            
        except Exception as e:
            self.logger.error(f"Failed to create directory {path}: {e}")
            return None
    
    def read_file(self, path: Union[str, Path]) -> Optional[str]:
        """Dosya oku"""
        try:
            resolved_path = self._resolve_path(path)
            
            if not resolved_path.exists() or not resolved_path.is_file():
                return None
            
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Erişim zamanını güncelle
            self._update_access_time(resolved_path)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {path}: {e}")
            return None
    
    def write_file(self, path: Union[str, Path], content: str, 
                  owner: str = "system") -> bool:
        """Dosyaya yaz"""
        try:
            resolved_path = self._resolve_path(path)
            
            # Dosya yoksa oluştur
            if not resolved_path.exists():
                return self.create_file(path, content, owner) is not None
            
            # Dosyayı güncelle
            with open(resolved_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Metadata güncelle
            self._update_file_metadata(resolved_path, content)
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.FILE_MODIFY, {
                "path": str(resolved_path),
                "size": len(content.encode('utf-8'))
            }, source="FileSystem")
            
            self.logger.debug(f"File updated: {resolved_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write file {path}: {e}")
            return False
    
    def delete_file(self, path: Union[str, Path]) -> bool:
        """Dosya sil"""
        try:
            resolved_path = self._resolve_path(path)
            
            if not resolved_path.exists():
                return False
            
            # Metadata'dan kaldır
            file_id = self._find_file_id_by_path(resolved_path)
            if file_id and file_id in self.metadata_cache:
                del self.metadata_cache[file_id]
                self.save_metadata()
            
            # Dosyayı sil
            if resolved_path.is_file():
                resolved_path.unlink()
            elif resolved_path.is_dir():
                shutil.rmtree(resolved_path)
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.FILE_DELETE, {
                "path": str(resolved_path),
                "file_id": file_id
            }, source="FileSystem")
            
            self.logger.info(f"File deleted: {resolved_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {path}: {e}")
            return False
    
    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Dosya taşı"""
        try:
            source_path = self._resolve_path(source)
            dest_path = self._resolve_path(destination)
            
            if not source_path.exists():
                return False
            
            # Hedef dizini oluştur
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Dosyayı taşı
            shutil.move(str(source_path), str(dest_path))
            
            # Metadata güncelle
            file_id = self._find_file_id_by_path(source_path)
            if file_id and file_id in self.metadata_cache:
                metadata = self.metadata_cache[file_id]
                metadata.path = str(dest_path.relative_to(self.base_path))
                metadata.name = dest_path.name
                metadata.modified_at = datetime.now().isoformat()
                self.save_metadata()
            
            # Event yayınla
            from core.events import publish, SystemEvents
            publish(SystemEvents.FILE_MOVE, {
                "source": str(source_path),
                "destination": str(dest_path),
                "file_id": file_id
            }, source="FileSystem")
            
            self.logger.info(f"File moved: {source_path} -> {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to move file {source} -> {destination}: {e}")
            return False
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Dosya kopyala"""
        try:
            source_path = self._resolve_path(source)
            dest_path = self._resolve_path(destination)
            
            if not source_path.exists():
                return False
            
            # Hedef dizini oluştur
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Dosyayı kopyala
            if source_path.is_file():
                shutil.copy2(str(source_path), str(dest_path))
            elif source_path.is_dir():
                shutil.copytree(str(source_path), str(dest_path))
            
            # Yeni dosya için metadata oluştur
            if dest_path.is_file():
                content = self.read_file(dest_path) or ""
                self.create_file(dest_path, content)
            
            self.logger.info(f"File copied: {source_path} -> {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy file {source} -> {destination}: {e}")
            return False
    
    def list_directory(self, path: Union[str, Path]) -> List[Dict]:
        """Dizin içeriğini listele"""
        try:
            resolved_path = self._resolve_path(path)
            
            if not resolved_path.exists() or not resolved_path.is_dir():
                return []
            
            items = []
            for item_path in resolved_path.iterdir():
                try:
                    stat = item_path.stat()
                    
                    item_info = {
                        "name": item_path.name,
                        "path": str(item_path.relative_to(self.base_path)),
                        "type": "directory" if item_path.is_dir() else "file",
                        "size": stat.st_size if item_path.is_file() else 0,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "file_type": self._get_file_type(item_path)
                    }
                    
                    # Metadata varsa ekle
                    file_id = self._find_file_id_by_path(item_path)
                    if file_id and file_id in self.metadata_cache:
                        metadata = self.metadata_cache[file_id]
                        item_info.update({
                            "file_id": file_id,
                            "owner": metadata.owner,
                            "tags": metadata.tags,
                            "permissions": metadata.permissions
                        })
                    
                    items.append(item_info)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get info for {item_path}: {e}")
                    continue
            
            # Erişim zamanını güncelle
            self._update_access_time(resolved_path)
            
            return sorted(items, key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
        except Exception as e:
            self.logger.error(f"Failed to list directory {path}: {e}")
            return []
    
    def get_file_info(self, path: Union[str, Path]) -> Optional[Dict]:
        """Dosya bilgilerini al"""
        try:
            resolved_path = self._resolve_path(path)
            
            if not resolved_path.exists():
                return None
            
            stat = resolved_path.stat()
            
            info = {
                "name": resolved_path.name,
                "path": str(resolved_path.relative_to(self.base_path)),
                "absolute_path": str(resolved_path),
                "type": "directory" if resolved_path.is_dir() else "file",
                "size": stat.st_size if resolved_path.is_file() else 0,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "file_type": self._get_file_type(resolved_path)
            }
            
            # Metadata varsa ekle
            file_id = self._find_file_id_by_path(resolved_path)
            if file_id and file_id in self.metadata_cache:
                metadata = self.metadata_cache[file_id]
                info.update({
                    "file_id": file_id,
                    "owner": metadata.owner,
                    "tags": metadata.tags,
                    "permissions": metadata.permissions
                })
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get file info {path}: {e}")
            return None
    
    def _find_file_id_by_path(self, path: Path) -> Optional[str]:
        """Yol ile dosya ID'sini bul"""
        relative_path = str(path.relative_to(self.base_path))
        
        for file_id, metadata in self.metadata_cache.items():
            if metadata.path == relative_path:
                return file_id
        
        return None
    
    def _update_access_time(self, path: Path):
        """Erişim zamanını güncelle"""
        file_id = self._find_file_id_by_path(path)
        if file_id and file_id in self.metadata_cache:
            self.metadata_cache[file_id].accessed_at = datetime.now().isoformat()
    
    def _update_file_metadata(self, path: Path, content: str):
        """Dosya metadata'sını güncelle"""
        file_id = self._find_file_id_by_path(path)
        if file_id and file_id in self.metadata_cache:
            metadata = self.metadata_cache[file_id]
            metadata.size = len(content.encode('utf-8'))
            metadata.modified_at = datetime.now().isoformat()
            metadata.accessed_at = datetime.now().isoformat()
            self.save_metadata()
    
    def search_files(self, query: str, path: Union[str, Path] = None) -> List[Dict]:
        """Dosya ara"""
        try:
            search_path = self._resolve_path(path) if path else self.base_path
            results = []
            
            # Dosya adında ara
            for file_id, metadata in self.metadata_cache.items():
                if query.lower() in metadata.name.lower():
                    file_path = self.base_path / metadata.path
                    if file_path.exists() and file_path.is_relative_to(search_path):
                        results.append({
                            "file_id": file_id,
                            "name": metadata.name,
                            "path": metadata.path,
                            "type": metadata.file_type,
                            "size": metadata.size,
                            "owner": metadata.owner,
                            "tags": metadata.tags
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    def get_disk_usage(self, path: Union[str, Path] = None) -> Dict:
        """Disk kullanımı"""
        try:
            check_path = self._resolve_path(path) if path else self.base_path
            
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for item in check_path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
                elif item.is_dir():
                    dir_count += 1
            
            return {
                "path": str(check_path),
                "total_size": total_size,
                "file_count": file_count,
                "directory_count": dir_count,
                "human_size": self._format_size(total_size)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get disk usage for {path}: {e}")
            return {}
    
    def _format_size(self, size_bytes: int) -> str:
        """Boyutu okunabilir formata çevir"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def cleanup_temp(self):
        """Geçici dosyaları temizle"""
        try:
            temp_path = self.mount_points["temp"]
            
            # 24 saatten eski dosyaları sil
            cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
            
            deleted_count = 0
            for item in temp_path.rglob("*"):
                if item.is_file() and item.stat().st_mtime < cutoff_time:
                    try:
                        item.unlink()
                        deleted_count += 1
                    except Exception:
                        pass
            
            self.logger.info(f"Cleaned up {deleted_count} temporary files")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files: {e}")
    
    def shutdown(self):
        """Dosya sistemini kapat"""
        try:
            # Metadata'yı kaydet
            self.save_metadata()
            
            # Alt modülleri kapat
            if self.search_engine:
                self.search_engine.shutdown()
            
            if self.mount_manager:
                self.mount_manager.shutdown()
            
            if self.userfs:
                self.userfs.shutdown()
            
            if self.vfs:
                # VFS'in shutdown metodu yoksa sorun değil
                pass
            
            self.logger.info("File system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during file system shutdown: {e}")
    
    # VFS Entegre Metodları
    def vfs_read_file(self, virtual_path: str, app_id: str = "system") -> Optional[str]:
        """VFS üzerinden güvenli dosya okuma"""
        try:
            # VFS erişim kontrolü
            if self.vfs and not self.vfs.check_access(virtual_path, app_id, 
                                                     VFSPermission.READ):
                self.logger.warning(f"VFS denied read access: {app_id} -> {virtual_path}")
                return None
            
            # Gerçek yolu çözümle
            real_path = self.vfs.resolve_path(virtual_path) if self.vfs else virtual_path
            if not real_path:
                return None
            
            # Dosyayı oku
            return self.read_file(real_path)
            
        except Exception as e:
            self.logger.error(f"VFS read file error: {e}")
            return None
    
    def vfs_write_file(self, virtual_path: str, content: str, app_id: str = "system") -> bool:
        """VFS üzerinden güvenli dosya yazma"""
        try:
            # VFS erişim kontrolü
            if self.vfs and not self.vfs.check_access(virtual_path, app_id, 
                                                     VFSPermission.WRITE):
                self.logger.warning(f"VFS denied write access: {app_id} -> {virtual_path}")
                return False
            
            # Gerçek yolu çözümle
            real_path = self.vfs.resolve_path(virtual_path) if self.vfs else virtual_path
            if not real_path:
                return False
            
            # Dosyayı yaz
            return self.write_file(real_path, content, app_id)
            
        except Exception as e:
            self.logger.error(f"VFS write file error: {e}")
            return False
    
    def vfs_list_directory(self, virtual_path: str, app_id: str = "system") -> List[Dict]:
        """VFS üzerinden güvenli dizin listeleme"""
        try:
            # VFS erişim kontrolü
            if self.vfs and not self.vfs.check_access(virtual_path, app_id, 
                                                     VFSPermission.READ):
                self.logger.warning(f"VFS denied list access: {app_id} -> {virtual_path}")
                return []
            
            # Gerçek yolu çözümle
            real_path = self.vfs.resolve_path(virtual_path) if self.vfs else virtual_path
            if not real_path:
                return []
            
            # Dizini listele
            return self.list_directory(real_path)
            
        except Exception as e:
            self.logger.error(f"VFS list directory error: {e}")
            return []
    
    def vfs_create_directory(self, virtual_path: str, app_id: str = "system") -> Optional[str]:
        """VFS üzerinden güvenli dizin oluşturma"""
        try:
            # VFS erişim kontrolü
            if self.vfs and not self.vfs.check_access(virtual_path, app_id, 
                                                     VFSPermission.WRITE):
                self.logger.warning(f"VFS denied create access: {app_id} -> {virtual_path}")
                return None
            
            # Gerçek yolu çözümle
            real_path = self.vfs.resolve_path(virtual_path) if self.vfs else virtual_path
            if not real_path:
                return None
            
            # Dizini oluştur
            return self.create_directory(real_path, app_id)
            
        except Exception as e:
            self.logger.error(f"VFS create directory error: {e}")
            return None
    
    def vfs_delete_file(self, virtual_path: str, app_id: str = "system") -> bool:
        """VFS üzerinden güvenli dosya silme"""
        try:
            # VFS erişim kontrolü
            if self.vfs and not self.vfs.check_access(virtual_path, app_id, 
                                                     VFSPermission.DELETE):
                self.logger.warning(f"VFS denied delete access: {app_id} -> {virtual_path}")
                return False
            
            # Gerçek yolu çözümle
            real_path = self.vfs.resolve_path(virtual_path) if self.vfs else virtual_path
            if not real_path:
                return False
            
            # Dosyayı sil
            return self.delete_file(real_path)
            
        except Exception as e:
            self.logger.error(f"VFS delete file error: {e}")
            return False
    
    def get_vfs_stats(self) -> Dict:
        """VFS istatistiklerini al"""
        if self.vfs:
            return self.vfs.get_security_stats()
        return {"vfs_available": False}
    
    def get_allowed_paths_for_app(self, app_id: str) -> List[str]:
        """Uygulamanın erişebileceği yolları al"""
        if self.vfs:
            return self.vfs.list_allowed_paths(app_id)
        return ["/"]  # Fallback - tüm erişim
    
    # VFS modülüne direkt erişim
    def get_vfs(self):
        """VFS modülünü al"""
        return self.vfs

# Global file system instance
_file_system = None

def init_fs(kernel=None) -> FileSystem:
    """File system'ı başlat"""
    global _file_system
    if _file_system is None:
        _file_system = FileSystem(kernel)
        _file_system.initialize()
    return _file_system

def get_file_system() -> Optional[FileSystem]:
    """File system'ı al"""
    return _file_system 