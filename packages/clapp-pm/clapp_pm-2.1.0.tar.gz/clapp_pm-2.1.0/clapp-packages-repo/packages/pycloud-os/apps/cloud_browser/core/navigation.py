"""
Cloud Browser Navigation Modülü
URL yönetimi ve geçmiş sistemi
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from urllib.parse import urlparse

try:
    from PyQt6.QtCore import QObject, pyqtSignal
except ImportError:
    raise ImportError("PyQt6 is required for Cloud Browser")

class NavigationHistory:
    """
    Tarayıcı geçmişi yöneticisi
    """
    
    def __init__(self):
        self.history_file = Path.home() / ".cloud_browser" / "history.json"
        self.history_file.parent.mkdir(exist_ok=True)
        self.history: List[Dict[str, Any]] = []
        self.max_history_items = 1000
        self.load_history()
    
    def load_history(self):
        """Geçmişi yükle"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
            else:
                self.history = []
        except Exception as e:
            print(f"Geçmiş yükleme hatası: {e}")
            self.history = []
    
    def save_history(self):
        """Geçmişi kaydet"""
        try:
            # Geçmişi sınırla
            if len(self.history) > self.max_history_items:
                self.history = self.history[-self.max_history_items:]
            
            data = {
                "version": "2.0.0",
                "created": datetime.now().isoformat(),
                "history": self.history
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Geçmiş kaydetme hatası: {e}")
    
    def add_entry(self, url: str, title: str = ""):
        """Geçmişe giriş ekle"""
        if not url or url == "about:blank":
            return
        
        # Aynı URL'yi tekrar ekleme
        if self.history and self.history[-1].get("url") == url:
            # Son ziyaret zamanını güncelle
            self.history[-1]["last_visited"] = datetime.now().isoformat()
            self.history[-1]["visit_count"] = self.history[-1].get("visit_count", 1) + 1
            self.save_history()
            return
        
        # Yeni giriş
        entry = {
            "url": url,
            "title": title or self.extract_domain(url),
            "visited": datetime.now().isoformat(),
            "last_visited": datetime.now().isoformat(),
            "visit_count": 1,
            "domain": self.extract_domain(url)
        }
        
        self.history.append(entry)
        self.save_history()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Geçmişi al"""
        history = sorted(self.history, key=lambda x: x.get("last_visited", ""), reverse=True)
        if limit:
            return history[:limit]
        return history
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """Geçmişte arama yap"""
        query = query.lower().strip()
        if not query:
            return self.get_history()
        
        results = []
        for entry in self.history:
            title = entry.get("title", "").lower()
            url = entry.get("url", "").lower()
            domain = entry.get("domain", "").lower()
            
            if query in title or query in url or query in domain:
                results.append(entry)
        
        return sorted(results, key=lambda x: x.get("last_visited", ""), reverse=True)
    
    def clear_history(self):
        """Geçmişi temizle"""
        self.history.clear()
        self.save_history()
    
    def remove_entry(self, url: str):
        """Belirli URL'yi geçmişten sil"""
        self.history = [entry for entry in self.history if entry.get("url") != url]
        self.save_history()
    
    def get_most_visited(self, limit: int = 10) -> List[Dict[str, Any]]:
        """En çok ziyaret edilen sayfalar"""
        return sorted(
            self.history,
            key=lambda x: x.get("visit_count", 0),
            reverse=True
        )[:limit]
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son ziyaret edilen sayfalar"""
        return sorted(
            self.history,
            key=lambda x: x.get("last_visited", ""),
            reverse=True
        )[:limit]
    
    def extract_domain(self, url: str) -> str:
        """URL'den domain çıkar"""
        try:
            parsed = urlparse(url)
            return parsed.netloc or "Yerel Dosya"
        except:
            return "Bilinmeyen"

class URLValidator:
    """
    URL doğrulama ve düzeltme sınıfı
    """
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """URL geçerli mi kontrol et"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    @staticmethod
    def fix_url(url: str) -> str:
        """URL'yi düzelt"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Zaten geçerli protokol var mı?
        if url.startswith(('http://', 'https://', 'file://', 'ftp://')):
            return url
        
        # Dosya yolu mu?
        if url.startswith('/') or ':\\' in url:
            return f"file://{url}"
        
        # Domain benzeri mi?
        if '.' in url and ' ' not in url and not url.startswith('www.'):
            return f"https://{url}"
        
        # www ile başlıyor mu?
        if url.startswith('www.'):
            return f"https://{url}"
        
        # Arama sorgusu olarak değerlendir
        return f"https://www.google.com/search?q={url.replace(' ', '+')}"
    
    @staticmethod
    def is_search_query(text: str) -> bool:
        """Metin arama sorgusu mu?"""
        if not text:
            return False
        
        # Boşluk varsa arama sorgusu
        if ' ' in text.strip():
            return True
        
        # Nokta yoksa arama sorgusu
        if '.' not in text:
            return True
        
        # Protokol varsa URL
        if text.startswith(('http://', 'https://', 'file://', 'ftp://')):
            return False
        
        # Domain benzeri değilse arama sorgusu
        try:
            parsed = urlparse(f"https://{text}")
            return not bool(parsed.netloc)
        except:
            return True

class NavigationManager(QObject):
    """
    Navigasyon yöneticisi
    """
    
    # Signals
    url_changed = pyqtSignal(str)
    title_changed = pyqtSignal(str)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.history = NavigationHistory()
        self.current_url = ""
        self.current_title = ""
        self.is_loading = False
    
    def navigate_to(self, url: str, title: str = ""):
        """URL'ye git"""
        if not url:
            return
        
        # URL'yi düzelt
        fixed_url = URLValidator.fix_url(url)
        
        # Geçmişe ekle
        if fixed_url != "about:blank":
            self.history.add_entry(fixed_url, title)
        
        # Durumu güncelle
        self.current_url = fixed_url
        self.current_title = title
        
        # Signal gönder
        self.url_changed.emit(fixed_url)
        if title:
            self.title_changed.emit(title)
    
    def set_loading(self, loading: bool):
        """Yükleme durumunu ayarla"""
        if self.is_loading != loading:
            self.is_loading = loading
            if loading:
                self.loading_started.emit()
            else:
                self.loading_finished.emit(True)
    
    def update_title(self, title: str):
        """Başlığı güncelle"""
        if title and title != self.current_title:
            self.current_title = title
            self.title_changed.emit(title)
            
            # Geçmişte güncelle
            if self.current_url:
                for entry in self.history.history:
                    if entry.get("url") == self.current_url:
                        entry["title"] = title
                        break
                self.history.save_history()
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Arama önerileri al"""
        if not query:
            return self.history.get_recent(limit)
        
        # Geçmişte ara
        history_results = self.history.search_history(query)[:limit//2]
        
        # Popüler siteler
        popular_sites = []
        if query.lower() in ['google', 'g']:
            popular_sites.append({
                "url": "https://www.google.com",
                "title": "Google",
                "type": "suggestion"
            })
        elif query.lower() in ['youtube', 'yt']:
            popular_sites.append({
                "url": "https://www.youtube.com",
                "title": "YouTube",
                "type": "suggestion"
            })
        elif query.lower() in ['github', 'git']:
            popular_sites.append({
                "url": "https://www.github.com",
                "title": "GitHub",
                "type": "suggestion"
            })
        
        # Arama önerisi
        if URLValidator.is_search_query(query):
            search_suggestion = {
                "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "title": f"'{query}' için arama yap",
                "type": "search"
            }
            popular_sites.append(search_suggestion)
        
        # Sonuçları birleştir
        results = popular_sites + history_results
        return results[:limit]

class TabHistory:
    """
    Sekme bazlı geçmiş yöneticisi
    """
    
    def __init__(self):
        self.back_history: List[str] = []
        self.forward_history: List[str] = []
        self.current_url = ""
    
    def navigate_to(self, url: str):
        """Yeni URL'ye git"""
        if self.current_url and self.current_url != url:
            self.back_history.append(self.current_url)
        
        self.current_url = url
        self.forward_history.clear()
    
    def can_go_back(self) -> bool:
        """Geri gidebilir mi?"""
        return len(self.back_history) > 0
    
    def can_go_forward(self) -> bool:
        """İleri gidebilir mi?"""
        return len(self.forward_history) > 0
    
    def go_back(self) -> Optional[str]:
        """Geri git"""
        if not self.can_go_back():
            return None
        
        if self.current_url:
            self.forward_history.append(self.current_url)
        
        self.current_url = self.back_history.pop()
        return self.current_url
    
    def go_forward(self) -> Optional[str]:
        """İleri git"""
        if not self.can_go_forward():
            return None
        
        if self.current_url:
            self.back_history.append(self.current_url)
        
        self.current_url = self.forward_history.pop()
        return self.current_url
    
    def clear(self):
        """Geçmişi temizle"""
        self.back_history.clear()
        self.forward_history.clear()
        self.current_url = "" 