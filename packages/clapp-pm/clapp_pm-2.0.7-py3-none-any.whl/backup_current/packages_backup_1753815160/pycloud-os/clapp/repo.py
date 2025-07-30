"""
PyCloud OS Clapp Repository Manager
Uzak ve yerel mağaza kaynaklarını yöneten yapı. Paket listelerini sağlar ve doğrulama yapar.
"""

import os
import json
import hashlib
import requests
import tempfile
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urljoin, urlparse

class RepositoryType(Enum):
    """Repository türleri"""
    OFFICIAL = "official"
    COMMUNITY = "community"
    PRIVATE = "private"
    LOCAL = "local"

class RepositoryStatus(Enum):
    """Repository durumları"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UPDATING = "updating"

@dataclass
class PackageInfo:
    """Paket bilgi sınıfı"""
    id: str
    name: str
    version: str
    description: str
    category: str
    developer: str
    license: str
    url: str
    icon_url: str = ""
    homepage: str = ""
    tags: List[str] = None
    depends: List[str] = None
    screenshots: List[str] = None
    signature: str = ""
    size_mb: float = 0.0
    repository_name: str = ""
    repository_type: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.depends is None:
            self.depends = []
        if self.screenshots is None:
            self.screenshots = []
    
    @classmethod
    def from_dict(cls, data: Dict, repo_name: str = "", repo_type: str = "") -> 'PackageInfo':
        """Dict'ten PackageInfo oluştur"""
        package = cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            category=data.get("category", "Other"),
            developer=data.get("developer", "Unknown"),
            license=data.get("license", "Unknown"),
            url=data.get("url", ""),
            icon_url=data.get("icon", ""),
            homepage=data.get("homepage", ""),
            tags=data.get("tags", []),
            depends=data.get("depends", []),
            screenshots=data.get("screenshots", []),
            signature=data.get("signature", ""),
            size_mb=data.get("size_mb", 0.0),
            repository_name=repo_name,
            repository_type=repo_type,
            last_updated=data.get("last_updated", "")
        )
        return package
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        return asdict(self)

@dataclass
class Repository:
    """Repository bilgi sınıfı"""
    id: str
    name: str
    url: str
    repo_type: RepositoryType
    status: RepositoryStatus
    description: str = ""
    priority: int = 100
    enabled: bool = True
    last_update: str = ""
    last_error: str = ""
    package_count: int = 0
    signature: str = ""
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['repo_type'] = self.repo_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Repository':
        """Dict'ten Repository oluştur"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            url=data.get("url", ""),
            repo_type=RepositoryType(data.get("repo_type", "community")),
            status=RepositoryStatus(data.get("status", "active")),
            description=data.get("description", ""),
            priority=data.get("priority", 100),
            enabled=data.get("enabled", True),
            last_update=data.get("last_update", ""),
            last_error=data.get("last_error", ""),
            package_count=data.get("package_count", 0),
            signature=data.get("signature", "")
        )

class PackageCache:
    """Paket cache yöneticisi"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("PackageCache")
        
        # Cache ayarları
        self.cache_duration = timedelta(hours=6)  # 6 saat
        self.max_cache_size_mb = 500  # 500MB
        
        # Cache indeksi
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict:
        """Cache indeksini yükle"""
        try:
            if self.cache_index_file.exists():
                with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load cache index: {e}")
        
        return {}
    
    def _save_cache_index(self):
        """Cache indeksini kaydet"""
        try:
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save cache index: {e}")
    
    def get_repository_cache(self, repo_id: str) -> Optional[Dict]:
        """Repository cache'ini al"""
        try:
            cache_entry = self.cache_index.get(repo_id)
            if not cache_entry:
                return None
            
            # Cache süresi kontrolü
            cached_time = datetime.fromisoformat(cache_entry["cached_at"])
            if datetime.now() - cached_time > self.cache_duration:
                self.invalidate_repository_cache(repo_id)
                return None
            
            # Cache dosyasını oku
            cache_file = self.cache_dir / cache_entry["filename"]
            if not cache_file.exists():
                self.invalidate_repository_cache(repo_id)
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to get repository cache for {repo_id}: {e}")
            return None
    
    def set_repository_cache(self, repo_id: str, data: Dict):
        """Repository cache'ini ayarla"""
        try:
            cache_filename = f"repo_{repo_id}_{int(datetime.now().timestamp())}.json"
            cache_file = self.cache_dir / cache_filename
            
            # Cache dosyasını yaz
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Eski cache'i temizle
            if repo_id in self.cache_index:
                old_file = self.cache_dir / self.cache_index[repo_id]["filename"]
                if old_file.exists():
                    old_file.unlink()
            
            # İndeksi güncelle
            self.cache_index[repo_id] = {
                "filename": cache_filename,
                "cached_at": datetime.now().isoformat(),
                "size_bytes": cache_file.stat().st_size
            }
            
            self._save_cache_index()
            self._cleanup_cache()
            
        except Exception as e:
            self.logger.error(f"Failed to set repository cache for {repo_id}: {e}")
    
    def invalidate_repository_cache(self, repo_id: str):
        """Repository cache'ini geçersiz kıl"""
        try:
            if repo_id in self.cache_index:
                cache_file = self.cache_dir / self.cache_index[repo_id]["filename"]
                if cache_file.exists():
                    cache_file.unlink()
                
                del self.cache_index[repo_id]
                self._save_cache_index()
                
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache for {repo_id}: {e}")
    
    def _cleanup_cache(self):
        """Cache temizliği"""
        try:
            # Toplam cache boyutunu hesapla
            total_size = sum(entry["size_bytes"] for entry in self.cache_index.values())
            max_size_bytes = self.max_cache_size_mb * 1024 * 1024
            
            if total_size > max_size_bytes:
                # En eski cache'leri sil
                sorted_entries = sorted(
                    self.cache_index.items(),
                    key=lambda x: x[1]["cached_at"]
                )
                
                for repo_id, entry in sorted_entries:
                    if total_size <= max_size_bytes:
                        break
                    
                    cache_file = self.cache_dir / entry["filename"]
                    if cache_file.exists():
                        cache_file.unlink()
                    
                    total_size -= entry["size_bytes"]
                    del self.cache_index[repo_id]
                
                self._save_cache_index()
                self.logger.info(f"Cache cleanup completed, size: {total_size / 1024 / 1024:.1f}MB")
                
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")

class RepositoryManager:
    """Ana repository yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("RepositoryManager")
        
        # Repository ayarları
        self.config_dir = Path("system/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.repositories_file = self.config_dir / "repositories.json"
        
        # Cache sistemi
        self.cache = PackageCache(Path("temp/repo_cache"))
        
        # Download dizini
        self.download_dir = Path("temp/downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Repository listesi
        self.repositories: Dict[str, Repository] = {}
        self.packages: Dict[str, List[PackageInfo]] = {}  # repo_id -> packages
        
        # HTTP ayarları
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PyCloud-OS-Clapp/1.0.0"
        })
        self.request_timeout = 30
        
        # Varsayılan repository'leri yükle
        self._load_repositories()
        self._create_default_repositories()
    
    def _load_repositories(self):
        """Repository'leri yükle"""
        try:
            if self.repositories_file.exists():
                with open(self.repositories_file, 'r', encoding='utf-8') as f:
                    repos_data = json.load(f)
                
                for repo_id, repo_data in repos_data.items():
                    try:
                        repo = Repository.from_dict(repo_data)
                        self.repositories[repo_id] = repo
                    except Exception as e:
                        self.logger.error(f"Failed to load repository {repo_id}: {e}")
                
                self.logger.info(f"Loaded {len(self.repositories)} repositories")
                
        except Exception as e:
            self.logger.error(f"Failed to load repositories: {e}")
    
    def _save_repositories(self):
        """Repository'leri kaydet"""
        try:
            repos_data = {}
            for repo_id, repo in self.repositories.items():
                repos_data[repo_id] = repo.to_dict()
            
            with open(self.repositories_file, 'w', encoding='utf-8') as f:
                json.dump(repos_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save repositories: {e}")
    
    def _create_default_repositories(self):
        """Varsayılan repository'leri oluştur"""
        if not self.repositories:
            # Resmi PyCloud repository
            official_repo = Repository(
                id="official",
                name="PyCloud Resmi Mağaza",
                url="https://repo.pycloudos.com/Repository.json",
                repo_type=RepositoryType.OFFICIAL,
                status=RepositoryStatus.ACTIVE,
                description="PyCloud OS resmi uygulama mağazası",
                priority=1,
                enabled=True
            )
            
            # Topluluk repository
            community_repo = Repository(
                id="community",
                name="PyCloud Topluluk Mağazası",
                url="https://repo.pycloudos.com/community/",
                repo_type=RepositoryType.COMMUNITY,
                status=RepositoryStatus.ACTIVE,
                description="Topluluk tarafından geliştirilen uygulamalar",
                priority=50,
                enabled=True
            )
            
            self.repositories["official"] = official_repo
            self.repositories["community"] = community_repo
            
            self._save_repositories()
            self.logger.info("Created default repositories")
    
    def add_repository(self, repo: Repository) -> bool:
        """Repository ekle"""
        try:
            # URL doğrulaması
            if not self._validate_repository_url(repo.url):
                self.logger.error(f"Invalid repository URL: {repo.url}")
                return False
            
            # Bağlantı testi
            if not self.test_repository_connection(repo):
                self.logger.warning(f"Repository connection test failed: {repo.name}")
                repo.status = RepositoryStatus.ERROR
                repo.last_error = "Connection test failed"
            
            self.repositories[repo.id] = repo
            self._save_repositories()
            
            self.logger.info(f"Repository added: {repo.name} ({repo.id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add repository: {e}")
            return False
    
    def remove_repository(self, repo_id: str) -> bool:
        """Repository kaldır"""
        try:
            if repo_id not in self.repositories:
                return False
            
            repo = self.repositories[repo_id]
            
            # Cache'i temizle
            self.cache.invalidate_repository_cache(repo_id)
            
            # Paket listesini temizle
            if repo_id in self.packages:
                del self.packages[repo_id]
            
            # Repository'yi kaldır
            del self.repositories[repo_id]
            self._save_repositories()
            
            self.logger.info(f"Repository removed: {repo.name} ({repo_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove repository {repo_id}: {e}")
            return False
    
    def update_repository(self, repo_id: str, **kwargs) -> bool:
        """Repository güncelle"""
        try:
            if repo_id not in self.repositories:
                return False
            
            repo = self.repositories[repo_id]
            
            # Alanları güncelle
            for key, value in kwargs.items():
                if hasattr(repo, key):
                    setattr(repo, key, value)
            
            # URL değiştiyse cache'i temizle
            if 'url' in kwargs:
                self.cache.invalidate_repository_cache(repo_id)
            
            self._save_repositories()
            
            self.logger.info(f"Repository updated: {repo.name} ({repo_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update repository {repo_id}: {e}")
            return False
    
    def _validate_repository_url(self, url: str) -> bool:
        """Repository URL'ini doğrula"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https', 'file'] and parsed.netloc
        except Exception:
            return False
    
    def test_repository_connection(self, repo: Repository) -> bool:
        """Repository bağlantısını test et"""
        try:
            if repo.url.startswith('file://'):
                # Yerel repository
                local_path = Path(repo.url[7:])
                return local_path.exists() and (local_path / "Repository.json").exists()
            
            else:
                # Uzak repository
                test_url = urljoin(repo.url, "Repository.json")
                response = self.session.head(test_url, timeout=self.request_timeout)
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Repository connection test failed for {repo.name}: {e}")
            return False
    
    def refresh_repository(self, repo_id: str) -> bool:
        """Repository'yi yenile"""
        try:
            if repo_id not in self.repositories:
                return False
            
            repo = self.repositories[repo_id]
            repo.status = RepositoryStatus.UPDATING
            
            # Cache'i temizle
            self.cache.invalidate_repository_cache(repo_id)
            
            # Paket listesini yükle
            packages = self._fetch_repository_packages(repo)
            if packages is not None:
                self.packages[repo_id] = packages
                repo.package_count = len(packages)
                repo.status = RepositoryStatus.ACTIVE
                repo.last_update = datetime.now().isoformat()
                repo.last_error = ""
                
                self.logger.info(f"Repository refreshed: {repo.name} ({len(packages)} packages)")
                return True
            
            else:
                repo.status = RepositoryStatus.ERROR
                repo.last_error = "Failed to fetch packages"
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to refresh repository {repo_id}: {e}")
            if repo_id in self.repositories:
                self.repositories[repo_id].status = RepositoryStatus.ERROR
                self.repositories[repo_id].last_error = str(e)
            return False
        
        finally:
            self._save_repositories()
    
    def refresh_repositories(self) -> Dict[str, bool]:
        """Tüm repository'leri yenile"""
        results = {}
        
        for repo_id, repo in self.repositories.items():
            if repo.enabled:
                results[repo_id] = self.refresh_repository(repo_id)
            else:
                results[repo_id] = True  # Disabled repos are "successful"
        
        return results
    
    def _fetch_repository_packages(self, repo: Repository) -> Optional[List[PackageInfo]]:
        """Repository paketlerini getir"""
        try:
            # Cache'den kontrol et
            cached_data = self.cache.get_repository_cache(repo.id)
            if cached_data:
                return self._parse_repository_data(cached_data, repo)
            
            # Uzaktan getir
            if repo.url.startswith('file://'):
                # Yerel repository
                local_path = Path(repo.url[7:])
                repo_file = local_path / "Repository.json"
                
                if repo_file.exists():
                    with open(repo_file, 'r', encoding='utf-8') as f:
                        repo_data = json.load(f)
                else:
                    return None
            
            else:
                # Uzak repository
                repo_url = urljoin(repo.url, "Repository.json")
                response = self.session.get(repo_url, timeout=self.request_timeout)
                response.raise_for_status()
                repo_data = response.json()
            
            # Cache'e kaydet
            self.cache.set_repository_cache(repo.id, repo_data)
            
            # Parse et
            return self._parse_repository_data(repo_data, repo)
            
        except Exception as e:
            self.logger.error(f"Failed to fetch packages from {repo.name}: {e}")
            return None
    
    def _parse_repository_data(self, repo_data: Dict, repo: Repository) -> List[PackageInfo]:
        """Repository verisini parse et"""
        packages = []
        
        try:
            # İmza kontrolü
            if repo_data.get("signature") and repo.signature:
                if not self._verify_repository_signature(repo_data, repo.signature):
                    self.logger.warning(f"Repository signature verification failed: {repo.name}")
            
            # Paketleri parse et
            for package_data in repo_data.get("packages", []):
                try:
                    package = PackageInfo.from_dict(
                        package_data, 
                        repo_name=repo.name,
                        repo_type=repo.repo_type.value
                    )
                    packages.append(package)
                    
                except Exception as e:
                    self.logger.error(f"Failed to parse package in {repo.name}: {e}")
            
            return packages
            
        except Exception as e:
            self.logger.error(f"Failed to parse repository data for {repo.name}: {e}")
            return []
    
    def _verify_repository_signature(self, repo_data: Dict, expected_signature: str) -> bool:
        """Repository imzasını doğrula"""
        try:
            # Basit SHA256 kontrolü
            data_str = json.dumps(repo_data.get("packages", []), sort_keys=True)
            calculated_signature = hashlib.sha256(data_str.encode()).hexdigest()
            return calculated_signature == expected_signature
            
        except Exception as e:
            self.logger.error(f"Signature verification failed: {e}")
            return False
    
    def get_repositories(self) -> List[Repository]:
        """Tüm repository'leri al"""
        return list(self.repositories.values())
    
    def get_repository(self, repo_id: str) -> Optional[Repository]:
        """Belirli bir repository al"""
        return self.repositories.get(repo_id)
    
    def get_all_packages(self) -> List[PackageInfo]:
        """Tüm paketleri al"""
        all_packages = []
        for packages in self.packages.values():
            all_packages.extend(packages)
        return all_packages
    
    def get_repository_packages(self, repo_id: str) -> List[PackageInfo]:
        """Repository paketlerini al"""
        if repo_id not in self.packages:
            # Lazy loading
            if repo_id in self.repositories:
                self.refresh_repository(repo_id)
        
        return self.packages.get(repo_id, [])
    
    def find_package(self, package_id: str) -> Optional[PackageInfo]:
        """Paket bul"""
        for packages in self.packages.values():
            for package in packages:
                if package.id == package_id:
                    return package
        
        # Cache'de yoksa tüm repository'leri yenile
        self.refresh_repositories()
        
        # Tekrar ara
        for packages in self.packages.values():
            for package in packages:
                if package.id == package_id:
                    return package
        
        return None
    
    def search_packages(self, query: str, category: str = None, repo_id: str = None) -> List[PackageInfo]:
        """Paket ara"""
        results = []
        query_lower = query.lower() if query else ""
        
        # Arama yapılacak paket listesi
        if repo_id and repo_id in self.packages:
            package_lists = [self.packages[repo_id]]
        else:
            package_lists = list(self.packages.values())
        
        for packages in package_lists:
            for package in packages:
                # Kategori filtresi
                if category and package.category.lower() != category.lower():
                    continue
                
                # Metin araması
                if query:
                    searchable_text = f"{package.name} {package.description} {package.developer} {' '.join(package.tags)}".lower()
                    if query_lower not in searchable_text:
                        continue
                
                results.append(package)
        
        # Relevance'a göre sırala
        if query:
            results.sort(key=lambda pkg: (
                query_lower in pkg.name.lower(),
                query_lower in pkg.description.lower(),
                pkg.name.lower()
            ), reverse=True)
        
        return results
    
    def download_package(self, package: PackageInfo) -> Optional[Path]:
        """Paketi indir"""
        try:
            if not package.url:
                self.logger.error(f"No download URL for package: {package.id}")
                return None
            
            # İndirme dosya adı
            filename = f"{package.id}_{package.version}.app.zip"
            download_path = self.download_dir / filename
            
            # Zaten indirilmiş mi?
            if download_path.exists():
                # İmza kontrolü
                if package.signature and self._verify_package_signature(download_path, package.signature):
                    return download_path
                else:
                    # İmza uyuşmuyor, yeniden indir
                    download_path.unlink()
            
            self.logger.info(f"Downloading package: {package.name} ({package.id})")
            
            # İndir
            response = self.session.get(package.url, timeout=self.request_timeout, stream=True)
            response.raise_for_status()
            
            # Dosyaya yaz
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # İmza kontrolü
            if package.signature and not self._verify_package_signature(download_path, package.signature):
                self.logger.error(f"Package signature verification failed: {package.id}")
                download_path.unlink()
                return None
            
            self.logger.info(f"Package downloaded successfully: {package.id}")
            return download_path
            
        except Exception as e:
            self.logger.error(f"Failed to download package {package.id}: {e}")
            return None
    
    def _verify_package_signature(self, package_path: Path, expected_signature: str) -> bool:
        """Paket imzasını doğrula"""
        try:
            # Dosya SHA256 hash'i
            hasher = hashlib.sha256()
            with open(package_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            calculated_signature = hasher.hexdigest()
            return calculated_signature == expected_signature
            
        except Exception as e:
            self.logger.error(f"Package signature verification failed: {e}")
            return False
    
    def get_repository_stats(self) -> Dict:
        """Repository istatistikleri"""
        try:
            total_repos = len(self.repositories)
            active_repos = sum(1 for repo in self.repositories.values() if repo.status == RepositoryStatus.ACTIVE)
            total_packages = sum(len(packages) for packages in self.packages.values())
            
            # Kategori sayımı
            category_counts = {}
            for packages in self.packages.values():
                for package in packages:
                    category = package.category
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            # Repository türü sayımı
            type_counts = {}
            for repo in self.repositories.values():
                repo_type = repo.repo_type.value
                type_counts[repo_type] = type_counts.get(repo_type, 0) + 1
            
            return {
                "total_repositories": total_repos,
                "active_repositories": active_repos,
                "total_packages": total_packages,
                "category_counts": category_counts,
                "repository_type_counts": type_counts,
                "cache_size_mb": self._get_cache_size_mb(),
                "download_dir": str(self.download_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate repository stats: {e}")
            return {}
    
    def _get_cache_size_mb(self) -> float:
        """Cache boyutunu MB olarak al"""
        try:
            total_size = sum(entry["size_bytes"] for entry in self.cache.cache_index.values())
            return total_size / 1024 / 1024
        except Exception:
            return 0.0
    
    def cleanup_downloads(self, older_than_days: int = 7) -> int:
        """Eski indirmeleri temizle"""
        try:
            cleaned_count = 0
            cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 3600)
            
            for file_path in self.download_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.zip':
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        self.logger.debug(f"Cleaned old download: {file_path.name}")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Download cleanup failed: {e}")
            return 0
    
    def export_repository_list(self, file_path: Path) -> bool:
        """Repository listesini dışa aktar"""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "repositories": [repo.to_dict() for repo in self.repositories.values()]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Repository list exported to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export repository list: {e}")
            return False
    
    def import_repository_list(self, file_path: Path) -> int:
        """Repository listesini içe aktar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            
            for repo_data in import_data.get("repositories", []):
                try:
                    repo = Repository.from_dict(repo_data)
                    
                    # Çakışma kontrolü
                    if repo.id in self.repositories:
                        self.logger.warning(f"Repository already exists, skipping: {repo.id}")
                        continue
                    
                    if self.add_repository(repo):
                        imported_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to import repository: {e}")
            
            self.logger.info(f"Imported {imported_count} repositories")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"Failed to import repository list: {e}")
            return 0

# Kolaylık fonksiyonları
_repository_manager = None

def init_repository_manager(kernel=None):
    """Repository manager'ı başlat"""
    try:
        repo_manager = RepositoryManager(kernel)
        
        # Varsayılan repository'leri ekle
        official_repo = Repository(
            id="official",
            name="PyCloud Resmi Mağaza",
            url="https://repo.pycloudos.com/Repository.json",
            repo_type=RepositoryType.OFFICIAL,
            enabled=True,
            status=RepositoryStatus.ACTIVE
        )
        
        repo_manager.add_repository(official_repo)
        
        return repo_manager
        
    except Exception as e:
        logging.getLogger("RepositoryManager").error(f"Failed to initialize: {e}")
        return None

def get_repository_manager() -> Optional[RepositoryManager]:
    """Repository Manager'ı al"""
    return _repository_manager 