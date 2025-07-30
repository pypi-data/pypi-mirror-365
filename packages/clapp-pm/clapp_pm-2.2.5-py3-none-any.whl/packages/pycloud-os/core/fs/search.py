"""
Core FS Search - Dosya Arama Motoru
İçerik tabanlı arama motoru, anahtar kelime, tarih, dosya tipi filtreleri
"""

import os
import json
import logging
import re
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib

class SearchType(Enum):
    """Arama türleri"""
    FILENAME = "filename"
    CONTENT = "content"
    METADATA = "metadata"
    ALL = "all"

class FileType(Enum):
    """Dosya türleri"""
    TEXT = "text"
    CODE = "code" 
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    ALL = "all"

@dataclass
class SearchResult:
    """Arama sonucu"""
    file_path: str
    filename: str
    file_type: str
    size: int
    modified: datetime
    matches: List[str] = field(default_factory=list)
    score: float = 0.0
    preview: str = ""
    line_numbers: List[int] = field(default_factory=list)

@dataclass 
class SearchFilter:
    """Arama filtreleri"""
    file_types: List[FileType] = field(default_factory=list)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    extensions: List[str] = field(default_factory=list)
    exclude_dirs: List[str] = field(default_factory=list)

class FileSearchEngine:
    """
    PyCloud dosya sisteminde içerik tabanlı arama motoru.
    Anahtar kelime, tarih, dosya tipi filtreleri ile arama.
    """
    
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("FileSearchEngine")
        
        # Arama indeksi
        self.search_index: Dict[str, Dict[str, Any]] = {}
        self.last_index_update = None
        
        # Arama geçmişi
        self.search_history: List[Dict[str, Any]] = []
        self.favorite_searches: List[Dict[str, Any]] = []
        
        # İndeksleme ayarları
        self.index_config = {
            "auto_index_interval": 3600,  # 1 saat
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "index_content": True,
            "index_metadata": True
        }
        
        # Desteklenen dosya türleri
        self.file_type_map = {
            FileType.TEXT: ['.txt', '.md', '.log', '.cfg', '.ini'],
            FileType.CODE: ['.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml'],
            FileType.IMAGE: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg'],
            FileType.AUDIO: ['.mp3', '.wav', '.ogg', '.flac', '.m4a'],
            FileType.VIDEO: ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
            FileType.DOCUMENT: ['.pdf', '.doc', '.docx', '.odt', '.rtf'],
            FileType.ARCHIVE: ['.zip', '.tar', '.gz', '.rar', '.7z']
        }
        
        # İndeksleme thread'i
        self.indexing_thread = None
        self.indexing_active = False
        
        self._load_search_data()
        self._start_auto_indexing()
    
    def _load_search_data(self):
        """Arama verilerini yükle"""
        try:
            # Arama geçmişi
            history_file = Path("system/search_history.json")
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.search_history = json.load(f)
            
            # Favori aramalar
            favorites_file = Path("system/favorite_searches.json") 
            if favorites_file.exists():
                with open(favorites_file, 'r', encoding='utf-8') as f:
                    self.favorite_searches = json.load(f)
                    
        except Exception as e:
            self.logger.error(f"Failed to load search data: {e}")
    
    def _save_search_data(self):
        """Arama verilerini kaydet"""
        try:
            # Sistem dizini oluştur
            Path("system").mkdir(exist_ok=True)
            
            # Arama geçmişi (son 100)
            with open("system/search_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.search_history[-100:], f, indent=2, ensure_ascii=False, default=str)
            
            # Favori aramalar
            with open("system/favorite_searches.json", 'w', encoding='utf-8') as f:
                json.dump(self.favorite_searches, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save search data: {e}")
    
    def _start_auto_indexing(self):
        """Otomatik indekslemeyi başlat"""
        try:
            if self.indexing_thread and self.indexing_thread.is_alive():
                return
                
            self.indexing_active = True
            self.indexing_thread = threading.Thread(target=self._auto_index_worker, daemon=True)
            self.indexing_thread.start()
            
            self.logger.info("Auto indexing started")
            
        except Exception as e:
            self.logger.error(f"Failed to start auto indexing: {e}")
    
    def _auto_index_worker(self):
        """Otomatik indeksleme worker'ı"""
        while self.indexing_active:
            try:
                self.rebuild_index()
                time.sleep(self.index_config["auto_index_interval"])
                
            except Exception as e:
                self.logger.error(f"Auto indexing error: {e}")
                time.sleep(60)  # Hata durumunda 1 dakika bekle
    
    def rebuild_index(self, root_paths: Optional[List[str]] = None) -> bool:
        """Arama indeksini yeniden oluştur"""
        try:
            if not root_paths:
                root_paths = ["users", "system", "apps"]
            
            new_index = {}
            indexed_count = 0
            
            for root_path in root_paths:
                if not Path(root_path).exists():
                    continue
                    
                for file_path in self._walk_files(root_path):
                    try:
                        file_info = self._index_file(file_path)
                        if file_info:
                            new_index[str(file_path)] = file_info
                            indexed_count += 1
                            
                    except Exception as e:
                        self.logger.debug(f"Failed to index {file_path}: {e}")
            
            self.search_index = new_index
            self.last_index_update = datetime.now()
            
            self.logger.info(f"Search index rebuilt: {indexed_count} files indexed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rebuild index: {e}")
            return False
    
    def _walk_files(self, root_path: str) -> List[Path]:
        """Dosyaları gezin"""
        files = []
        try:
            root = Path(root_path)
            
            for item in root.rglob("*"):
                if item.is_file():
                    # Gizli dosyaları ve sistem dosyalarını atla
                    if any(part.startswith('.') for part in item.parts):
                        continue
                    
                    # Boyut kontrolü
                    if item.stat().st_size > self.index_config["max_file_size"]:
                        continue
                    
                    files.append(item)
                    
        except Exception as e:
            self.logger.debug(f"Failed to walk {root_path}: {e}")
        
        return files
    
    def _index_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Dosyayı indeksle"""
        try:
            stat_info = file_path.stat()
            
            file_info = {
                "path": str(file_path),
                "name": file_path.name,
                "extension": file_path.suffix.lower(),
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime),
                "type": self._get_file_type(file_path),
                "content_indexed": False,
                "content_hash": None,
                "keywords": set()
            }
            
            # İçerik indeksleme (metin dosyaları için)
            if self.index_config["index_content"] and self._is_text_file(file_path):
                content_info = self._index_file_content(file_path)
                if content_info:
                    file_info.update(content_info)
            
            return file_info
            
        except Exception as e:
            self.logger.debug(f"Failed to index file {file_path}: {e}")
            return None
    
    def _get_file_type(self, file_path: Path) -> str:
        """Dosya türünü belirle"""
        extension = file_path.suffix.lower()
        
        for file_type, extensions in self.file_type_map.items():
            if extension in extensions:
                return file_type.value
        
        return "unknown"
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Dosya metin dosyası mı kontrol et"""
        extension = file_path.suffix.lower()
        text_extensions = (
            self.file_type_map[FileType.TEXT] +
            self.file_type_map[FileType.CODE]
        )
        return extension in text_extensions
    
    def _index_file_content(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Dosya içeriğini indeksle"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # İçerik hash'i
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Anahtar kelimeler çıkar
            keywords = self._extract_keywords(content)
            
            return {
                "content_indexed": True,
                "content_hash": content_hash,
                "keywords": keywords,
                "line_count": len(content.splitlines()),
                "char_count": len(content)
            }
            
        except Exception as e:
            self.logger.debug(f"Failed to index content of {file_path}: {e}")
            return None
    
    def _extract_keywords(self, content: str) -> Set[str]:
        """İçerikten anahtar kelimeler çıkar"""
        # Basit anahtar kelime çıkarma
        words = re.findall(r'\w+', content.lower())
        
        # Kısa kelimeleri ve yaygın kelimeleri filtrele
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 've', 'bir', 'bu', 'da', 'de', 'ile', 'var', 'yok'}
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}
        
        return keywords
    
    def search(self, query: str, search_type: SearchType = SearchType.ALL, 
               filters: Optional[SearchFilter] = None, max_results: int = 100) -> List[SearchResult]:
        """Dosya arama yap"""
        try:
            # Arama geçmişine ekle
            search_entry = {
                "query": query,
                "type": search_type.value,
                "timestamp": datetime.now().isoformat(),
                "filters": filters.__dict__ if filters else None
            }
            self.search_history.append(search_entry)
            
            results = []
            query_lower = query.lower()
            
            for file_path, file_info in self.search_index.items():
                try:
                    # Filtre kontrolü
                    if filters and not self._apply_filters(file_info, filters):
                        continue
                    
                    score = 0.0
                    matches = []
                    line_numbers = []
                    
                    # Dosya adı araması
                    if search_type in [SearchType.FILENAME, SearchType.ALL]:
                        if query_lower in file_info["name"].lower():
                            score += 100
                            matches.append(f"Filename: {file_info['name']}")
                    
                    # İçerik araması
                    if (search_type in [SearchType.CONTENT, SearchType.ALL] and 
                        file_info.get("content_indexed", False)):
                        
                        if query_lower in file_info.get("keywords", set()):
                            score += 50
                            matches.append(f"Content keyword: {query}")
                        
                        # Dosya içeriğinde arama (detaylı)
                        content_matches = self._search_in_file_content(Path(file_path), query_lower)
                        if content_matches:
                            score += len(content_matches) * 10
                            matches.extend(content_matches["matches"])
                            line_numbers.extend(content_matches["line_numbers"])
                    
                    # Sonuç oluştur
                    if score > 0:
                        result = SearchResult(
                            file_path=file_path,
                            filename=file_info["name"],
                            file_type=file_info["type"],
                            size=file_info["size"],
                            modified=file_info["modified"],
                            matches=matches,
                            score=score,
                            line_numbers=line_numbers
                        )
                        
                        # Önizleme ekle
                        result.preview = self._get_file_preview(Path(file_path), query_lower)
                        
                        results.append(result)
                        
                except Exception as e:
                    self.logger.debug(f"Search error for {file_path}: {e}")
            
            # Sonuçları skora göre sırala
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Arama verilerini kaydet
            self._save_search_data()
            
            self.logger.info(f"Search completed: '{query}' -> {len(results)} results")
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Search failed for '{query}': {e}")
            return []
    
    def _apply_filters(self, file_info: Dict[str, Any], filters: SearchFilter) -> bool:
        """Filtreleri uygula"""
        try:
            # Dosya türü filtresi
            if filters.file_types and FileType.ALL not in filters.file_types:
                if not any(file_info["type"] == ft.value for ft in filters.file_types):
                    return False
            
            # Tarih filtresi
            if filters.date_from and file_info["modified"] < filters.date_from:
                return False
            if filters.date_to and file_info["modified"] > filters.date_to:
                return False
            
            # Boyut filtresi
            if filters.size_min and file_info["size"] < filters.size_min:
                return False
            if filters.size_max and file_info["size"] > filters.size_max:
                return False
            
            # Uzantı filtresi
            if filters.extensions:
                if file_info["extension"] not in filters.extensions:
                    return False
            
            # Dizin hariç tutma
            if filters.exclude_dirs:
                file_path = file_info["path"]
                if any(excluded in file_path for excluded in filters.exclude_dirs):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Filter application error: {e}")
            return False
    
    def _search_in_file_content(self, file_path: Path, query: str) -> Optional[Dict[str, Any]]:
        """Dosya içeriğinde detaylı arama"""
        try:
            if not self._is_text_file(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            matches = []
            line_numbers = []
            
            for i, line in enumerate(lines, 1):
                if query in line.lower():
                    matches.append(f"Line {i}: {line.strip()[:100]}")
                    line_numbers.append(i)
            
            if matches:
                return {
                    "matches": matches,
                    "line_numbers": line_numbers
                }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Content search error for {file_path}: {e}")
            return None
    
    def _get_file_preview(self, file_path: Path, query: str = "") -> str:
        """Dosya önizlemesi al"""
        try:
            if not self._is_text_file(file_path):
                return f"{file_path.suffix.upper()} dosyası"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)  # İlk 500 karakter
            
            if query:
                # Query'nin etrafını vurgula
                preview = content.replace(query, f"**{query}**")
            else:
                preview = content
            
            return preview.strip()
            
        except Exception as e:
            return "Önizleme alınamadı"
    
    def add_favorite_search(self, query: str, search_type: SearchType, filters: Optional[SearchFilter] = None) -> bool:
        """Favori arama ekle"""
        try:
            favorite = {
                "query": query,
                "type": search_type.value,
                "filters": filters.__dict__ if filters else None,
                "created": datetime.now().isoformat(),
                "name": f"Arama: {query}"
            }
            
            self.favorite_searches.append(favorite)
            self._save_search_data()
            
            self.logger.info(f"Added favorite search: {query}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add favorite search: {e}")
            return False
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Arama önerileri al"""
        try:
            suggestions = []
            
            # Geçmiş aramalardan öneriler
            for search in self.search_history[-20:]:
                query = search["query"]
                if partial_query.lower() in query.lower() and query not in suggestions:
                    suggestions.append(query)
            
            # İndeksteki anahtar kelimelerden öneriler
            for file_info in list(self.search_index.values())[:100]:  # İlk 100 dosya
                keywords = file_info.get("keywords", set())
                for keyword in keywords:
                    if (partial_query.lower() in keyword and 
                        len(keyword) > len(partial_query) and 
                        keyword not in suggestions):
                        suggestions.append(keyword)
            
            return suggestions[:10]  # En fazla 10 öneri
            
        except Exception as e:
            self.logger.error(f"Failed to get search suggestions: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Arama motoru istatistiklerini al"""
        return {
            "indexed_files": len(self.search_index),
            "last_index_update": self.last_index_update.isoformat() if self.last_index_update else None,
            "search_history_count": len(self.search_history),
            "favorite_searches_count": len(self.favorite_searches),
            "indexing_active": self.indexing_active,
            "module_name": "FileSearchEngine"
        }
    
    def stop_indexing(self):
        """İndekslemeyi durdur"""
        self.indexing_active = False
        if self.indexing_thread:
            self.indexing_thread.join(timeout=5) 