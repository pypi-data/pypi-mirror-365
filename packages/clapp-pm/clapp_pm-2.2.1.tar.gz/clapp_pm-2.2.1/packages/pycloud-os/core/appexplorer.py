"""
PyCloud OS App Explorer
Sisteme kurulmuş tüm .app uygulamalarını tanır, doğrular ve başlatıcıya görünür hale getirir
"""

import os
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class AppDiscoveryStatus(Enum):
    """Uygulama keşif durumları"""
    DISCOVERED = "discovered"
    VALIDATED = "validated"
    INDEXED = "indexed"
    FAILED = "failed"
    REMOVED = "removed"

class AppCategory(Enum):
    """Uygulama kategorileri"""
    SYSTEM = "Sistem"
    DEVELOPMENT = "Geliştirme"
    OFFICE = "Ofis"
    ENTERTAINMENT = "Eğlence"
    GRAPHICS = "Grafik"
    INTERNET = "İnternet"
    MULTIMEDIA = "Multimedya"
    UTILITIES = "Araçlar"
    GAMES = "Oyunlar"
    EDUCATION = "Eğitim"
    OTHER = "Diğer"

@dataclass
class DiscoveredApp:
    """Keşfedilen uygulama bilgisi"""
    app_id: str
    name: str
    version: str
    description: str
    category: str
    developer: str
    icon_path: str
    app_path: str
    entry_file: str
    exec_command: str
    tags: List[str]
    discovery_time: str
    last_validated: str
    status: AppDiscoveryStatus
    metadata: Dict[str, Any]
    
    # Yeni alanlar - cursorrules genişletmeleri
    requires: List[str] = None  # Gerekli modüller
    permissions: Dict[str, Any] = None  # İzin gereksinimleri
    custom_folder: str = ""  # Özel klasör yolu
    
    def __post_init__(self):
        if self.requires is None:
            self.requires = []
        if self.permissions is None:
            self.permissions = {}
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_app_json(cls, app_path: Path, app_data: Dict) -> 'DiscoveredApp':
        """app.json'dan DiscoveredApp oluştur"""
        return cls(
            app_id=app_data.get("id", ""),
            name=app_data.get("name", ""),
            version=app_data.get("version", "1.0.0"),
            description=app_data.get("description", ""),
            category=app_data.get("category", AppCategory.OTHER.value),
            developer=app_data.get("developer", "Unknown"),
            icon_path=str(app_path / app_data.get("icon", "icon.png")),
            app_path=str(app_path),
            entry_file=app_data.get("entry", "main.py"),
            exec_command=app_data.get("exec", "python3 main.py"),
            tags=app_data.get("tags", []),
            discovery_time=datetime.now().isoformat(),
            last_validated=datetime.now().isoformat(),
            status=AppDiscoveryStatus.DISCOVERED,
            metadata=app_data,
            # Yeni alanlar
            requires=app_data.get("requires", []),
            permissions=app_data.get("permissions", {}),
            custom_folder=""
        )

class AppIndexer:
    """Uygulama indeksleme sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger("AppIndexer")
        self.index_file = Path("system/config/app_index.json")
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        
        # İndeks cache
        self.app_index: Dict[str, DiscoveredApp] = {}
        self.category_index: Dict[str, List[str]] = {}
        self.tag_index: Dict[str, List[str]] = {}
        self.developer_index: Dict[str, List[str]] = {}
        
        self._load_index()
    
    def _load_index(self):
        """İndeksi yükle"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                # Ana indeks
                for app_id, app_data in index_data.get("apps", {}).items():
                    try:
                        app = DiscoveredApp(
                            app_id=app_data["app_id"],
                            name=app_data["name"],
                            version=app_data["version"],
                            description=app_data["description"],
                            category=app_data["category"],
                            developer=app_data["developer"],
                            icon_path=app_data["icon_path"],
                            app_path=app_data["app_path"],
                            entry_file=app_data["entry_file"],
                            exec_command=app_data["exec_command"],
                            tags=app_data["tags"],
                            discovery_time=app_data["discovery_time"],
                            last_validated=app_data["last_validated"],
                            status=AppDiscoveryStatus(app_data["status"]),
                            metadata=app_data["metadata"]
                        )
                        self.app_index[app_id] = app
                    except Exception as e:
                        self.logger.error(f"Failed to load app {app_id}: {e}")
                
                # Yardımcı indeksler
                self.category_index = index_data.get("category_index", {})
                self.tag_index = index_data.get("tag_index", {})
                self.developer_index = index_data.get("developer_index", {})
                
                self.logger.info(f"Loaded index with {len(self.app_index)} apps")
                
        except Exception as e:
            self.logger.error(f"Failed to load app index: {e}")
    
    def _save_index(self):
        """İndeksi kaydet"""
        try:
            index_data = {
                "apps": {app_id: app.to_dict() for app_id, app in self.app_index.items()},
                "category_index": self.category_index,
                "tag_index": self.tag_index,
                "developer_index": self.developer_index,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save app index: {e}")
    
    def add_app(self, app: DiscoveredApp):
        """Uygulamayı indekse ekle"""
        try:
            self.app_index[app.app_id] = app
            
            # Kategori indeksi
            if app.category not in self.category_index:
                self.category_index[app.category] = []
            if app.app_id not in self.category_index[app.category]:
                self.category_index[app.category].append(app.app_id)
            
            # Tag indeksi
            for tag in app.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                if app.app_id not in self.tag_index[tag]:
                    self.tag_index[tag].append(app.app_id)
            
            # Developer indeksi
            if app.developer not in self.developer_index:
                self.developer_index[app.developer] = []
            if app.app_id not in self.developer_index[app.developer]:
                self.developer_index[app.developer].append(app.app_id)
            
            app.status = AppDiscoveryStatus.INDEXED
            self._save_index()
            
            self.logger.debug(f"App indexed: {app.name} ({app.app_id})")
            
        except Exception as e:
            self.logger.error(f"Failed to index app {app.app_id}: {e}")
    
    def remove_app(self, app_id: str):
        """Uygulamayı indeksten kaldır"""
        try:
            if app_id not in self.app_index:
                return
            
            app = self.app_index[app_id]
            
            # Ana indeksten kaldır
            del self.app_index[app_id]
            
            # Kategori indeksinden kaldır
            if app.category in self.category_index:
                if app_id in self.category_index[app.category]:
                    self.category_index[app.category].remove(app_id)
                # Boş kategoriyi temizle
                if not self.category_index[app.category]:
                    del self.category_index[app.category]
            
            # Tag indeksinden kaldır
            for tag in app.tags:
                if tag in self.tag_index:
                    if app_id in self.tag_index[tag]:
                        self.tag_index[tag].remove(app_id)
                    # Boş tag'i temizle
                    if not self.tag_index[tag]:
                        del self.tag_index[tag]
            
            # Developer indeksinden kaldır
            if app.developer in self.developer_index:
                if app_id in self.developer_index[app.developer]:
                    self.developer_index[app.developer].remove(app_id)
                # Boş developer'ı temizle
                if not self.developer_index[app.developer]:
                    del self.developer_index[app.developer]
            
            self._save_index()
            
            self.logger.debug(f"App removed from index: {app.name} ({app_id})")
            
        except Exception as e:
            self.logger.error(f"Failed to remove app {app_id} from index: {e}")
    
    def search_apps(self, query: str, category: str = None, tags: List[str] = None) -> List[DiscoveredApp]:
        """Uygulama ara"""
        try:
            results = []
            query_lower = query.lower() if query else ""
            
            for app in self.app_index.values():
                # Kategori filtresi
                if category and app.category != category:
                    continue
                
                # Tag filtresi
                if tags and not any(tag in app.tags for tag in tags):
                    continue
                
                # Metin araması
                if query:
                    searchable_text = f"{app.name} {app.description} {app.developer} {' '.join(app.tags)}".lower()
                    if query_lower not in searchable_text:
                        continue
                
                results.append(app)
            
            # Relevance'a göre sırala (basit implementasyon)
            if query:
                results.sort(key=lambda app: (
                    query_lower in app.name.lower(),
                    query_lower in app.description.lower(),
                    app.name.lower()
                ), reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def get_apps_by_category(self, category: str) -> List[DiscoveredApp]:
        """Kategoriye göre uygulamaları al"""
        app_ids = self.category_index.get(category, [])
        return [self.app_index[app_id] for app_id in app_ids if app_id in self.app_index]
    
    def get_apps_by_developer(self, developer: str) -> List[DiscoveredApp]:
        """Geliştiriciye göre uygulamaları al"""
        app_ids = self.developer_index.get(developer, [])
        return [self.app_index[app_id] for app_id in app_ids if app_id in self.app_index]
    
    def get_apps_by_tag(self, tag: str) -> List[DiscoveredApp]:
        """Etikete göre uygulamaları al"""
        app_ids = self.tag_index.get(tag, [])
        return [self.app_index[app_id] for app_id in app_ids if app_id in self.app_index]
    
    def get_all_categories(self) -> List[str]:
        """Tüm kategorileri al"""
        return list(self.category_index.keys())
    
    def get_all_tags(self) -> List[str]:
        """Tüm etiketleri al"""
        return list(self.tag_index.keys())
    
    def get_all_developers(self) -> List[str]:
        """Tüm geliştiricileri al"""
        return list(self.developer_index.keys())

class ConflictResolver:
    """Uygulama çakışma çözücü"""
    
    def __init__(self):
        self.logger = logging.getLogger("ConflictResolver")
    
    def detect_conflicts(self, apps: List[DiscoveredApp]) -> Dict[str, List[DiscoveredApp]]:
        """Çakışmaları tespit et"""
        conflicts = {}
        
        # ID çakışmaları
        id_groups = {}
        for app in apps:
            if app.app_id not in id_groups:
                id_groups[app.app_id] = []
            id_groups[app.app_id].append(app)
        
        for app_id, app_list in id_groups.items():
            if len(app_list) > 1:
                conflicts[f"duplicate_id_{app_id}"] = app_list
        
        return conflicts
    
    def resolve_conflicts(self, conflicts: Dict[str, List[DiscoveredApp]]) -> Dict[str, DiscoveredApp]:
        """Çakışmaları çöz"""
        resolved = {}
        
        for conflict_type, conflicted_apps in conflicts.items():
            if conflict_type.startswith("duplicate_id_"):
                # En yeni sürümü seç
                latest_app = max(conflicted_apps, key=lambda app: app.version)
                resolved[latest_app.app_id] = latest_app
                
                self.logger.warning(f"Resolved ID conflict for {latest_app.app_id}: selected version {latest_app.version}")
        
        return resolved

class SmartTagExtractor:
    """Otomatik etiket çıkarıcı"""
    
    def __init__(self):
        self.logger = logging.getLogger("SmartTagExtractor")
        
        # Kategori bazlı otomatik etiketler
        self.category_tags = {
            AppCategory.DEVELOPMENT.value: ["code", "programming", "dev", "ide"],
            AppCategory.OFFICE.value: ["productivity", "document", "office"],
            AppCategory.ENTERTAINMENT.value: ["fun", "media", "entertainment"],
            AppCategory.GRAPHICS.value: ["image", "design", "graphics"],
            AppCategory.INTERNET.value: ["web", "browser", "network"],
            AppCategory.MULTIMEDIA.value: ["audio", "video", "media"],
            AppCategory.UTILITIES.value: ["tool", "utility", "system"],
            AppCategory.GAMES.value: ["game", "play", "entertainment"],
            AppCategory.EDUCATION.value: ["learn", "education", "study"]
        }
        
        # Anahtar kelime bazlı etiketler
        self.keyword_tags = {
            "editor": ["text", "editor"],
            "browser": ["web", "internet"],
            "terminal": ["cli", "command"],
            "ide": ["development", "programming"],
            "player": ["media", "multimedia"],
            "manager": ["utility", "system"],
            "viewer": ["view", "display"],
            "calculator": ["math", "utility"],
            "chat": ["communication", "social"],
            "email": ["communication", "mail"]
        }
    
    def extract_tags(self, app: DiscoveredApp) -> List[str]:
        """Otomatik etiket çıkar"""
        extracted_tags = set()
        
        # Kategori bazlı etiketler
        category_tags = self.category_tags.get(app.category, [])
        extracted_tags.update(category_tags)
        
        # İsim ve açıklama bazlı etiketler
        text = f"{app.name} {app.description}".lower()
        
        for keyword, tags in self.keyword_tags.items():
            if keyword in text:
                extracted_tags.update(tags)
        
        # Mevcut etiketleri koru
        extracted_tags.update(app.tags)
        
        return list(extracted_tags)

class ManifestValidator:
    """Gelişmiş manifest doğrulayıcı - cursorrules genişletmesi"""
    
    def __init__(self):
        self.logger = logging.getLogger("ManifestValidator")
        
        # Desteklenen manifest alanları
        self.supported_fields = [
            "id", "name", "version", "description", "entry", "exec",
            "icon", "category", "developer", "tags", "requires", 
            "permissions", "license", "homepage", "screenshots"
        ]
        
        # Gerekli alanlar
        self.required_fields = ["id", "name", "entry"]
        
        # İzin türleri
        self.valid_permissions = [
            "fs.read", "fs.write", "network", "audio", "camera", 
            "microphone", "location", "notifications", "system"
        ]
    
    def validate_manifest(self, app_data: Dict, app_path: Path) -> tuple[bool, List[str]]:
        """Manifest dosyasını doğrula"""
        errors = []
        warnings = []
        
        try:
            # Gerekli alanları kontrol et
            for field in self.required_fields:
                if field not in app_data:
                    errors.append(f"Required field missing: {field}")
            
            # ID formatını kontrol et
            app_id = app_data.get("id", "")
            if app_id:
                if not app_id.replace("_", "").replace("-", "").isalnum():
                    errors.append("App ID must contain only alphanumeric characters, hyphens, and underscores")
                if len(app_id) < 3:
                    errors.append("App ID must be at least 3 characters long")
            
            # Sürüm formatını kontrol et
            version = app_data.get("version", "")
            if version and not self._is_valid_version(version):
                warnings.append(f"Version format may be invalid: {version}")
            
            # Entry dosyasını kontrol et
            entry = app_data.get("entry", "")
            if entry:
                entry_path = app_path / entry
                if not entry_path.exists():
                    errors.append(f"Entry file not found: {entry}")
                elif not entry_path.suffix in [".py", ".sh", ".exe"]:
                    warnings.append(f"Unusual entry file type: {entry}")
            
            # İkon dosyasını kontrol et
            icon = app_data.get("icon", "icon.png")
            icon_path = app_path / icon
            if not icon_path.exists():
                warnings.append(f"Icon file not found: {icon}")
            elif not icon_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".svg", ".ico"]:
                warnings.append(f"Unusual icon file type: {icon}")
            
            # Requires alanını kontrol et
            requires = app_data.get("requires", [])
            if requires and isinstance(requires, list):
                for requirement in requires:
                    if not isinstance(requirement, str):
                        errors.append(f"Invalid requirement format: {requirement}")
                    elif not requirement.startswith("core.") and not requirement.startswith("python:"):
                        warnings.append(f"Unknown requirement type: {requirement}")
            
            # Permissions alanını kontrol et
            permissions = app_data.get("permissions", {})
            if permissions and isinstance(permissions, dict):
                for perm, value in permissions.items():
                    if perm not in self.valid_permissions:
                        warnings.append(f"Unknown permission: {perm}")
                    if not isinstance(value, bool):
                        errors.append(f"Permission value must be boolean: {perm}")
            
            # Kategori kontrolü
            category = app_data.get("category", "")
            if category:
                valid_categories = [cat.value for cat in AppCategory]
                if category not in valid_categories:
                    warnings.append(f"Unknown category: {category}")
            
            # Desteklenmeyen alanları kontrol et
            for field in app_data.keys():
                if field not in self.supported_fields:
                    warnings.append(f"Unsupported manifest field: {field}")
            
            # Log warnings
            if warnings:
                self.logger.warning(f"Manifest warnings for {app_id}: {warnings}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Manifest validation error: {e}")
            return False, [f"Validation failed: {e}"]
    
    def _is_valid_version(self, version: str) -> bool:
        """Sürüm formatını kontrol et"""
        try:
            # Semantic versioning kontrolü (x.y.z)
            parts = version.split(".")
            if len(parts) < 2 or len(parts) > 4:
                return False
            
            for part in parts:
                if not part.isdigit():
                    # Alpha, beta, rc gibi ekleri kabul et
                    if not any(suffix in part.lower() for suffix in ["alpha", "beta", "rc", "dev"]):
                        return False
            
            return True
        except:
            return False

class CustomFolderManager:
    """Özel uygulama klasörleri yöneticisi - cursorrules genişletmesi"""
    
    def __init__(self):
        self.logger = logging.getLogger("CustomFolderManager")
        self.custom_folders: List[Path] = []
        self.config_file = Path("system/config/custom_app_folders.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._load_custom_folders()
    
    def _load_custom_folders(self):
        """Özel klasörleri yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for folder_path in data.get("custom_folders", []):
                    path = Path(folder_path)
                    if path.exists() and path.is_dir():
                        self.custom_folders.append(path)
                        self.logger.info(f"Loaded custom app folder: {path}")
                    else:
                        self.logger.warning(f"Custom app folder not found: {path}")
                        
        except Exception as e:
            self.logger.error(f"Failed to load custom folders: {e}")
    
    def add_custom_folder(self, folder_path: str) -> bool:
        """Özel klasör ekle"""
        try:
            path = Path(folder_path)
            if not path.exists():
                self.logger.error(f"Folder does not exist: {folder_path}")
                return False
            
            if not path.is_dir():
                self.logger.error(f"Path is not a directory: {folder_path}")
                return False
            
            if path in self.custom_folders:
                self.logger.warning(f"Folder already added: {folder_path}")
                return True
            
            self.custom_folders.append(path)
            self._save_custom_folders()
            self.logger.info(f"Added custom app folder: {folder_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add custom folder: {e}")
            return False
    
    def remove_custom_folder(self, folder_path: str) -> bool:
        """Özel klasör kaldır"""
        try:
            path = Path(folder_path)
            if path in self.custom_folders:
                self.custom_folders.remove(path)
                self._save_custom_folders()
                self.logger.info(f"Removed custom app folder: {folder_path}")
                return True
            else:
                self.logger.warning(f"Custom folder not found: {folder_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove custom folder: {e}")
            return False
    
    def get_custom_folders(self) -> List[Path]:
        """Özel klasörleri al"""
        return self.custom_folders.copy()
    
    def _save_custom_folders(self):
        """Özel klasörleri kaydet"""
        try:
            data = {
                "custom_folders": [str(folder) for folder in self.custom_folders],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save custom folders: {e}")

class AppDiscoveryLogger:
    """Uygulama keşif log sistemi - cursorrules genişletmesi"""
    
    def __init__(self):
        self.logger = logging.getLogger("AppDiscoveryLogger")
        self.log_file = Path("logs/app_discovery.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Dosya handler ekle
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.discovery_stats = {
            "total_discoveries": 0,
            "successful_discoveries": 0,
            "failed_discoveries": 0,
            "last_discovery": None,
            "discovery_history": []
        }
    
    def log_discovery_start(self, folder_path: str):
        """Keşif başlangıcını logla"""
        self.logger.info(f"Starting app discovery in: {folder_path}")
    
    def log_app_discovered(self, app: DiscoveredApp):
        """Keşfedilen uygulamayı logla"""
        self.logger.info(f"App discovered: {app.name} ({app.app_id}) v{app.version} in {app.app_path}")
        self.discovery_stats["total_discoveries"] += 1
        self.discovery_stats["successful_discoveries"] += 1
        
        # Geçmişe ekle
        self.discovery_stats["discovery_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "discovered",
            "app_id": app.app_id,
            "app_name": app.name,
            "version": app.version,
            "path": app.app_path
        })
        
        # Geçmişi sınırla (son 100 kayıt)
        if len(self.discovery_stats["discovery_history"]) > 100:
            self.discovery_stats["discovery_history"] = self.discovery_stats["discovery_history"][-100:]
    
    def log_app_failed(self, app_path: str, errors: List[str]):
        """Başarısız keşfi logla"""
        self.logger.error(f"App discovery failed in {app_path}: {errors}")
        self.discovery_stats["total_discoveries"] += 1
        self.discovery_stats["failed_discoveries"] += 1
    
    def log_app_removed(self, app_id: str, app_name: str):
        """Kaldırılan uygulamayı logla"""
        self.logger.info(f"App removed: {app_name} ({app_id})")
        
        # Geçmişe ekle
        self.discovery_stats["discovery_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "removed",
            "app_id": app_id,
            "app_name": app_name
        })
    
    def log_discovery_completed(self, discovered_count: int, removed_count: int, total_apps: int):
        """Keşif tamamlandığını logla"""
        self.logger.info(f"Discovery completed: +{discovered_count}, -{removed_count} apps, total: {total_apps}")
        self.discovery_stats["last_discovery"] = datetime.now().isoformat()
    
    def get_discovery_stats(self) -> Dict:
        """Keşif istatistiklerini al"""
        return self.discovery_stats.copy()

class AppExplorer:
    """Ana uygulama keşif yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("AppExplorer")
        
        # Alt sistemler
        self.indexer = AppIndexer()
        self.conflict_resolver = ConflictResolver()
        self.tag_extractor = SmartTagExtractor()
        
        # Yeni genişletme sistemleri
        self.manifest_validator = ManifestValidator()
        self.custom_folder_manager = CustomFolderManager()
        self.discovery_logger = AppDiscoveryLogger()
        
        # Keşif ayarları
        self.apps_directory = Path("apps")
        self.discovery_interval = 10.0  # 10 saniye
        self.auto_discovery = True
        self.log_discovered_apps = True  # cursorrules özelliği
        self.support_custom_app_folders = True  # cursorrules özelliği
        
        # Keşif durumu
        self.discovery_running = False
        self.discovery_thread = None
        self.last_discovery = None
        
        # Cache
        self.discovered_apps: Dict[str, DiscoveredApp] = {}
        self.app_paths: Set[str] = set()
        
        # Callbacks
        self.callbacks = {
            "app_discovered": [],
            "app_removed": [],
            "discovery_completed": []
        }
        
        # İlk keşif
        self._initial_discovery()
        
        # Otomatik keşfi başlat
        if self.auto_discovery:
            self.start_discovery()
    
    def _initial_discovery(self):
        """İlk keşif işlemi"""
        try:
            self.logger.info("Starting initial app discovery...")
            
            # İndeksten yükle
            for app_id, app in self.indexer.app_index.items():
                self.discovered_apps[app_id] = app
                self.app_paths.add(app.app_path)
            
            # Yeni uygulamaları keşfet
            self._discover_apps()
            
            self.logger.info(f"Initial discovery completed: {len(self.discovered_apps)} apps found")
            
        except Exception as e:
            self.logger.error(f"Initial discovery failed: {e}")
    
    def start_discovery(self):
        """Otomatik keşfi başlat"""
        if self.discovery_running:
            return
        
        self.discovery_running = True
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.discovery_thread.start()
        self.logger.info("App discovery started")
    
    def stop_discovery(self):
        """Otomatik keşfi durdur"""
        self.discovery_running = False
        if self.discovery_thread and self.discovery_thread.is_alive():
            self.discovery_thread.join(timeout=2.0)
        self.logger.info("App discovery stopped")
    
    def _discovery_loop(self):
        """Keşif döngüsü"""
        while self.discovery_running:
            try:
                self._discover_apps()
                self.last_discovery = datetime.now()
                time.sleep(self.discovery_interval)
            except Exception as e:
                self.logger.error(f"Discovery loop error: {e}")
                time.sleep(30.0)
    
    def _discover_apps(self):
        """Uygulamaları keşfet - genişletilmiş versiyon"""
        try:
            discovered_count = 0
            removed_count = 0
            current_paths = set()
            
            # Keşif klasörlerini belirle
            discovery_folders = [self.apps_directory]
            
            # Özel klasörleri ekle (cursorrules özelliği)
            if self.support_custom_app_folders:
                discovery_folders.extend(self.custom_folder_manager.get_custom_folders())
            
            # Her klasörü tara
            for folder in discovery_folders:
                if not folder.exists():
                    continue
                
                # Keşif başlangıcını logla
                if self.log_discovered_apps:
                    self.discovery_logger.log_discovery_start(str(folder))
                
                discovered_in_folder, removed_in_folder = self._discover_apps_in_folder(folder, current_paths)
                discovered_count += discovered_in_folder
                removed_count += removed_in_folder
            
            # Kaldırılan uygulamaları tespit et
            removed_apps = []
            for app_id, app in self.discovered_apps.items():
                if app.app_path not in current_paths:
                    removed_apps.append(app_id)
            
            # Kaldırılan uygulamaları temizle
            for app_id in removed_apps:
                app = self.discovered_apps[app_id]
                del self.discovered_apps[app_id]
                self.indexer.remove_app(app_id)
                
                # Log ve callback
                if self.log_discovered_apps:
                    self.discovery_logger.log_app_removed(app_id, app.name)
                
                self._trigger_callback("app_removed", {"app_id": app_id, "name": app.name})
                
                removed_count += 1
                self.logger.info(f"App removed: {app.name} ({app_id})")
            
            # Çakışmaları kontrol et
            conflicts = self.conflict_resolver.detect_conflicts(list(self.discovered_apps.values()))
            if conflicts:
                resolved = self.conflict_resolver.resolve_conflicts(conflicts)
                self.logger.warning(f"Resolved {len(conflicts)} app conflicts")
            
            # Discovery tamamlandı callback'i
            self._trigger_callback("discovery_completed", {
                "discovered_count": discovered_count,
                "removed_count": removed_count,
                "total_apps": len(self.discovered_apps),
                "timestamp": datetime.now().isoformat()
            })
            
            # Log discovery completion
            if self.log_discovered_apps:
                self.discovery_logger.log_discovery_completed(discovered_count, removed_count, len(self.discovered_apps))
            
            if discovered_count > 0 or removed_count > 0:
                self.logger.info(f"Discovery completed: +{discovered_count}, -{removed_count} apps")
                
        except Exception as e:
            self.logger.error(f"App discovery failed: {e}")
    
    def _discover_apps_in_folder(self, folder: Path, current_paths: set) -> tuple[int, int]:
        """Belirli bir klasörde uygulama keşfi"""
        discovered_count = 0
        removed_count = 0
        
        try:
            for app_dir in folder.iterdir():
                if not app_dir.is_dir() or app_dir.name.startswith('.'):
                    continue
                
                app_json_path = app_dir / "app.json"
                if not app_json_path.exists():
                    continue
                
                current_paths.add(str(app_dir))
                
                try:
                    # app.json oku
                    with open(app_json_path, 'r', encoding='utf-8') as f:
                        app_data = json.load(f)
                    
                    app_id = app_data.get("id")
                    if not app_id:
                        self.logger.warning(f"App without ID: {app_dir}")
                        continue
                    
                    # Yeni uygulama mı?
                    if app_id not in self.discovered_apps:
                        # Gelişmiş doğrulama (cursorrules özelliği)
                        is_valid, validation_errors = self.manifest_validator.validate_manifest(app_data, app_dir)
                        
                        if not is_valid:
                            if self.log_discovered_apps:
                                self.discovery_logger.log_app_failed(str(app_dir), validation_errors)
                            self.logger.error(f"App validation failed for {app_dir}: {validation_errors}")
                            continue
                        
                        # Temel doğrulama
                        if self._validate_app(app_dir, app_data):
                            app = DiscoveredApp.from_app_json(app_dir, app_data)
                            
                            # Özel klasör bilgisini ekle
                            if folder != self.apps_directory:
                                app.custom_folder = str(folder)
                            
                            # Otomatik etiket çıkarımı
                            app.tags = self.tag_extractor.extract_tags(app)
                            
                            # Kaydet
                            self.discovered_apps[app_id] = app
                            self.indexer.add_app(app)
                            
                            # Log ve callback
                            if self.log_discovered_apps:
                                self.discovery_logger.log_app_discovered(app)
                            
                            self._trigger_callback("app_discovered", app.to_dict())
                            
                            discovered_count += 1
                            self.logger.info(f"New app discovered: {app.name} ({app_id})")
                    
                    else:
                        # Mevcut uygulamayı güncelle
                        existing_app = self.discovered_apps[app_id]
                        
                        # Sürüm kontrolü
                        new_version = app_data.get("version", "1.0.0")
                        if new_version != existing_app.version:
                            # Güncelle
                            updated_app = DiscoveredApp.from_app_json(app_dir, app_data)
                            updated_app.tags = self.tag_extractor.extract_tags(updated_app)
                            
                            # Özel klasör bilgisini koru
                            if existing_app.custom_folder:
                                updated_app.custom_folder = existing_app.custom_folder
                            elif folder != self.apps_directory:
                                updated_app.custom_folder = str(folder)
                            
                            self.discovered_apps[app_id] = updated_app
                            self.indexer.add_app(updated_app)
                            
                            self.logger.info(f"App updated: {updated_app.name} ({app_id}) v{new_version}")
                        
                        # Son doğrulama zamanını güncelle
                        existing_app.last_validated = datetime.now().isoformat()
                
                except Exception as e:
                    self.logger.error(f"Failed to process app {app_dir}: {e}")
                    if self.log_discovered_apps:
                        self.discovery_logger.log_app_failed(str(app_dir), [str(e)])
        
        except Exception as e:
            self.logger.error(f"Failed to discover apps in folder {folder}: {e}")
        
        return discovered_count, removed_count
    
    def _validate_app(self, app_dir: Path, app_data: Dict) -> bool:
        """Uygulamayı doğrula"""
        try:
            # Gerekli alanları kontrol et
            required_fields = ["id", "name", "version", "entry", "exec"]
            for field in required_fields:
                if field not in app_data:
                    self.logger.warning(f"Missing required field '{field}' in {app_dir}/app.json")
                    return False
            
            # Entry dosyasını kontrol et
            entry_file = app_dir / app_data["entry"]
            if not entry_file.exists():
                self.logger.warning(f"Entry file not found: {entry_file}")
                return False
            
            # İkon dosyasını kontrol et
            icon_file = app_dir / app_data.get("icon", "icon.png")
            if not icon_file.exists():
                self.logger.warning(f"Icon file not found: {icon_file}")
                # İkon yoksa da geçerli sayalım, varsayılan kullanılır
            
            return True
            
        except Exception as e:
            self.logger.error(f"App validation failed for {app_dir}: {e}")
            return False
    
    # Yeni API metodları - cursorrules genişletmeleri
    
    def add_custom_app_folder(self, folder_path: str) -> bool:
        """Özel uygulama klasörü ekle"""
        if not self.support_custom_app_folders:
            return False
        
        success = self.custom_folder_manager.add_custom_folder(folder_path)
        if success:
            # Hemen keşif yap
            self.force_discovery()
        return success
    
    def remove_custom_app_folder(self, folder_path: str) -> bool:
        """Özel uygulama klasörü kaldır"""
        if not self.support_custom_app_folders:
            return False
        
        return self.custom_folder_manager.remove_custom_folder(folder_path)
    
    def get_custom_app_folders(self) -> List[str]:
        """Özel uygulama klasörlerini al"""
        if not self.support_custom_app_folders:
            return []
        
        return [str(folder) for folder in self.custom_folder_manager.get_custom_folders()]
    
    def get_discovery_logs(self) -> Dict:
        """Keşif loglarını al"""
        if not self.log_discovered_apps:
            return {}
        
        return self.discovery_logger.get_discovery_stats()
    
    def validate_app_manifest(self, app_path: str) -> tuple[bool, List[str]]:
        """Uygulama manifest'ini doğrula"""
        try:
            app_dir = Path(app_path)
            app_json_path = app_dir / "app.json"
            
            if not app_json_path.exists():
                return False, ["app.json file not found"]
            
            with open(app_json_path, 'r', encoding='utf-8') as f:
                app_data = json.load(f)
            
            return self.manifest_validator.validate_manifest(app_data, app_dir)
            
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def get_apps_with_permissions(self, permission: str) -> List[DiscoveredApp]:
        """Belirli izne sahip uygulamaları al"""
        apps_with_permission = []
        
        for app in self.discovered_apps.values():
            if permission in app.permissions and app.permissions[permission]:
                apps_with_permission.append(app)
        
        return apps_with_permission
    
    def get_apps_with_requirements(self, requirement: str) -> List[DiscoveredApp]:
        """Belirli gereksinimi olan uygulamaları al"""
        apps_with_requirement = []
        
        for app in self.discovered_apps.values():
            if requirement in app.requires:
                apps_with_requirement.append(app)
        
        return apps_with_requirement
    
    def get_all_apps(self) -> List[DiscoveredApp]:
        """Tüm keşfedilen uygulamaları al"""
        return list(self.discovered_apps.values())
    
    def get_app(self, app_id: str) -> Optional[DiscoveredApp]:
        """Belirli bir uygulamayı al"""
        return self.discovered_apps.get(app_id)
    
    def get_app_by_id(self, app_id: str) -> Optional[DiscoveredApp]:
        """Belirli bir uygulamayı ID ile al (alias method)"""
        return self.get_app(app_id)
    
    def search_apps(self, query: str, category: str = None, tags: List[str] = None) -> List[DiscoveredApp]:
        """Uygulama ara"""
        return self.indexer.search_apps(query, category, tags)
    
    def get_apps_by_category(self, category: str) -> List[DiscoveredApp]:
        """Kategoriye göre uygulamaları al"""
        return self.indexer.get_apps_by_category(category)
    
    def get_categories(self) -> List[str]:
        """Tüm kategorileri al"""
        return self.indexer.get_all_categories()
    
    def get_developers(self) -> List[str]:
        """Tüm geliştiricileri al"""
        return self.indexer.get_all_developers()
    
    def get_tags(self) -> List[str]:
        """Tüm etiketleri al"""
        return self.indexer.get_all_tags()
    
    def force_discovery(self):
        """Zorla keşif yap"""
        self.logger.info("Forcing app discovery...")
        self._discover_apps()
    
    def add_callback(self, event_type: str, callback):
        """Callback ekle"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def _trigger_callback(self, event_type: str, data: Dict):
        """Callback tetikle"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"App explorer callback error for {event_type}: {e}")
    
    def get_discovery_stats(self) -> Dict:
        """Keşif istatistikleri"""
        try:
            category_counts = {}
            developer_counts = {}
            
            for app in self.discovered_apps.values():
                # Kategori sayımı
                category_counts[app.category] = category_counts.get(app.category, 0) + 1
                
                # Geliştirici sayımı
                developer_counts[app.developer] = developer_counts.get(app.developer, 0) + 1
            
            return {
                "total_apps": len(self.discovered_apps),
                "category_counts": category_counts,
                "developer_counts": developer_counts,
                "total_categories": len(self.indexer.get_all_categories()),
                "total_tags": len(self.indexer.get_all_tags()),
                "total_developers": len(self.indexer.get_all_developers()),
                "last_discovery": self.last_discovery.isoformat() if self.last_discovery else None,
                "discovery_running": self.discovery_running,
                "apps_directory": str(self.apps_directory)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate discovery stats: {e}")
            return {}
    
    def shutdown(self):
        """Modül kapatma"""
        self.logger.info("Shutting down app explorer...")
        
        # Keşfi durdur
        self.stop_discovery()
        
        # İndeksi kaydet
        self.indexer._save_index()
        
        self.logger.info("App explorer shutdown completed")

# Kolaylık fonksiyonları
_app_explorer = None

def init_app_explorer(kernel=None):
    """App Explorer'ı başlat"""
    global _app_explorer
    _app_explorer = AppExplorer(kernel)
    return _app_explorer

def get_app_explorer() -> Optional[AppExplorer]:
    """App Explorer'ı al"""
    return _app_explorer 