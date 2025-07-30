"""
Core FS UserFS - Kullanıcı Dosya Sistemi
Her kullanıcıya özel izole dosya sistemi alanı
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class UserFS:
    """
    Her kullanıcıya özel izole dosya sistemi alanı.
    Desktop, Documents, Downloads gibi klasörler içerir.
    """
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("UserFS")
        
        # Kullanıcı dizin yapısı
        self.user_dirs = {
            "Desktop": "Masaüstü",
            "Documents": "Belgeler", 
            "Downloads": "İndirilenler",
            "Pictures": "Resimler",
            "Music": "Müzik",
            "Projects": "Projeler",
            "Templates": "Şablonlar",
            ".apps": "Uygulama Ayarları",
            ".themes": "Kullanıcı Temaları",
            ".widgets": "Widget Ayarları",
            ".trash": "Geri Dönüşüm Kutusu"
        }
        
        # Aktif kullanıcı dizinleri
        self.user_directories: Dict[str, Dict[str, str]] = {}
        
    def init_user_directory(self, username: str) -> bool:
        """Kullanıcı için dizin yapısını başlat"""
        try:
            user_path = Path("users") / username
            user_path.mkdir(parents=True, exist_ok=True)
            
            # Standart klasörleri oluştur
            for dir_name, display_name in self.user_dirs.items():
                dir_path = user_path / dir_name
                dir_path.mkdir(exist_ok=True)
                
                # Metadata dosyası oluştur
                metadata = {
                    "display_name": display_name,
                    "created": datetime.now().isoformat(),
                    "type": "system_folder",
                    "permissions": "user_only"
                }
                
                metadata_path = dir_path / ".metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Kullanıcı profil dosyası
            profile_data = {
                "username": username,
                "created": datetime.now().isoformat(),
                "last_login": None,
                "preferences": {
                    "theme": "default",
                    "language": "tr_TR",
                    "desktop_layout": "grid"
                },
                "quotas": {
                    "max_storage": "1GB",
                    "max_files": 10000
                }
            }
            
            profile_path = user_path / ".profile.json"
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            # Başlangıç dosyaları
            self._create_welcome_files(user_path)
            
            # Cache'e ekle
            self.user_directories[username] = {
                "path": str(user_path),
                "initialized": True,
                "last_access": datetime.now().isoformat()
            }
            
            self.logger.info(f"User directory initialized: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize user directory for {username}: {e}")
            return False
    
    def _create_welcome_files(self, user_path: Path):
        """Kullanıcı için başlangıç dosyaları oluştur"""
        try:
            # Desktop'ta hoş geldin dosyası
            desktop_path = user_path / "Desktop"
            welcome_file = desktop_path / "PyCloud OS'e Hoş Geldiniz.md"
            
            welcome_content = """# PyCloud OS'e Hoş Geldiniz! 🎉

Bu dosya sizin kişisel masaüstünüzde yer almaktadır.

## Hızlı Başlangıç

- 📁 **Dosyalar**: Dock'taki Dosyalar simgesine tıklayarak dosya yöneticinizi açabilirsiniz
- 💻 **Terminal**: Sistem komutları için terminal uygulamasını kullanın
- 🐍 **Python IDE**: Python geliştirme için IDE'yi açın
- ⚙️ **Ayarlar**: Sistem ayarlarını topbar'daki bulut menüsünden erişebilirsiniz

## Klasörleriniz

- **Belgeler**: Dokümanlarınız için
- **İndirilenler**: İndirilen dosyalar
- **Projeler**: Geliştirme projeleri
- **Resimler**: Görseller ve fotoğraflar

Keyifli kullanımlar! 😊
"""
            
            with open(welcome_file, 'w', encoding='utf-8') as f:
                f.write(welcome_content)
            
            # Projeler klasöründe örnek proje
            projects_path = user_path / "Projects"
            sample_project = projects_path / "İlk Python Projem"
            sample_project.mkdir(exist_ok=True)
            
            sample_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Merhaba PyCloud OS! 🎉")
print("Bu benim ilk Python programım!")

# Basit hesaplama
sayı1 = 10
sayı2 = 20
sonuç = sayı1 + sayı2

print(f"{sayı1} + {sayı2} = {sonuç}")
"""
            
            with open(sample_project / "main.py", 'w', encoding='utf-8') as f:
                f.write(sample_code)
                
        except Exception as e:
            self.logger.error(f"Failed to create welcome files: {e}")
    
    def get_user_path(self, username: str, subdir: str = "") -> Optional[str]:
        """Kullanıcı dizin yolunu al"""
        try:
            if username not in self.user_directories:
                if not self.init_user_directory(username):
                    return None
            
            base_path = Path(self.user_directories[username]["path"])
            if subdir:
                return str(base_path / subdir)
            return str(base_path)
            
        except Exception as e:
            self.logger.error(f"Failed to get user path for {username}: {e}")
            return None
    
    def list_user_files(self, username: str, directory: str = "Desktop") -> List[Dict[str, Any]]:
        """Kullanıcı dizinindeki dosyaları listele"""
        try:
            user_path = self.get_user_path(username, directory)
            if not user_path:
                return []
            
            files = []
            dir_path = Path(user_path)
            
            if not dir_path.exists():
                return []
            
            for item in dir_path.iterdir():
                if item.name.startswith('.'):
                    continue  # Gizli dosyaları atla
                
                file_info = {
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "extension": item.suffix if item.is_file() else "",
                    "icon": self._get_file_icon(item)
                }
                files.append(file_info)
            
            return sorted(files, key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
        except Exception as e:
            self.logger.error(f"Failed to list user files for {username}/{directory}: {e}")
            return []
    
    def _get_file_icon(self, path: Path) -> str:
        """Dosya türüne göre ikon belirle"""
        if path.is_dir():
            return "📁"
        
        extension = path.suffix.lower()
        icon_map = {
            '.py': '🐍',
            '.md': '📝',
            '.txt': '📄',
            '.json': '⚙️',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
            '.mp3': '🎵',
            '.mp4': '🎬'
        }
        
        return icon_map.get(extension, '📄')
    
    def create_user_file(self, username: str, directory: str, filename: str, content: str = "") -> bool:
        """Kullanıcı dizininde dosya oluştur"""
        try:
            user_path = self.get_user_path(username, directory)
            if not user_path:
                return False
            
            file_path = Path(user_path) / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Created user file: {username}/{directory}/{filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create user file {filename}: {e}")
            return False
    
    def delete_user_file(self, username: str, file_path: str) -> bool:
        """Kullanıcı dosyasını geri dönüşüm kutusuna taşı"""
        try:
            source = Path(file_path)
            if not source.exists():
                return False
            
            # Geri dönüşüm kutusu yolu
            trash_path = self.get_user_path(username, ".trash")
            if not trash_path:
                return False
            
            trash_dir = Path(trash_path)
            trash_dir.mkdir(exist_ok=True)
            
            # Benzersiz dosya adı oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trash_file = trash_dir / f"{timestamp}_{source.name}"
            
            # Dosyayı taşı
            shutil.move(str(source), str(trash_file))
            
            # Metadata oluştur
            metadata = {
                "original_path": str(source),
                "deleted_date": datetime.now().isoformat(),
                "original_name": source.name,
                "type": "directory" if source.is_dir() else "file"
            }
            
            metadata_file = trash_dir / f"{timestamp}_{source.name}.metadata"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Moved to trash: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete user file {file_path}: {e}")
            return False
    
    def get_user_storage_usage(self, username: str) -> Dict[str, Any]:
        """Kullanıcı depolama kullanımını hesapla"""
        try:
            user_path = self.get_user_path(username)
            if not user_path:
                return {}
            
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for root, dirs, files in os.walk(user_path):
                dir_count += len(dirs)
                file_count += len(files)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
            
            return {
                "total_size_bytes": total_size,
                "total_size_human": self._format_size(total_size),
                "file_count": file_count,
                "directory_count": dir_count,
                "username": username
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate storage usage for {username}: {e}")
            return {}
    
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
    
    def cleanup_old_trash(self, username: str, days_old: int = 30) -> bool:
        """Eski geri dönüşüm kutusu dosyalarını temizle"""
        try:
            trash_path = self.get_user_path(username, ".trash")
            if not trash_path:
                return False
            
            trash_dir = Path(trash_path)
            if not trash_dir.exists():
                return True
            
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            for item in trash_dir.iterdir():
                if item.stat().st_mtime < cutoff_date:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                    cleaned_count += 1
            
            self.logger.info(f"Cleaned {cleaned_count} old trash items for {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup trash for {username}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """UserFS istatistiklerini al"""
        return {
            "active_users": len(self.user_directories),
            "user_list": list(self.user_directories.keys()),
            "system_folders": list(self.user_dirs.keys()),
            "module_name": "UserFS"
        } 