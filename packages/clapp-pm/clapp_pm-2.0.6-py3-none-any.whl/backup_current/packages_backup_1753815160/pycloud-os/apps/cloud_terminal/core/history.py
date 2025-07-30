"""
Cloud Terminal - Komut Geçmişi Yöneticisi
Komut geçmişi kaydetme, gezinme ve arama
"""

import os
import json
from typing import List, Optional
from pathlib import Path

class CommandHistory:
    """Komut geçmişi yöneticisi"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.history: List[str] = []
        self.current_index = -1
        
        # Geçmiş dosyası
        self.history_file = Path.home() / ".cloud_terminal_history"
        
        # Geçmişi yükle
        self.load_history()
    
    def add_command(self, command: str):
        """Komut ekle"""
        command = command.strip()
        if not command:
            return
        
        # Aynı komut art arda gelirse ekleme
        if self.history and self.history[-1] == command:
            return
        
        # Geçmişe ekle
        self.history.append(command)
        
        # Maksimum boyutu kontrol et
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Index'i sıfırla
        self.current_index = len(self.history)
        
        # Kaydet
        self.save_history()
    
    def get_previous(self) -> Optional[str]:
        """Önceki komut"""
        if not self.history:
            return None
        
        if self.current_index > 0:
            self.current_index -= 1
        
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        
        return None
    
    def get_next(self) -> Optional[str]:
        """Sonraki komut"""
        if not self.history:
            return None
        
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        else:
            self.current_index = len(self.history)
            return None
    
    def get_history(self) -> List[str]:
        """Tüm geçmişi al"""
        return self.history.copy()
    
    def search_history(self, term: str) -> List[str]:
        """Geçmişte ara"""
        term = term.lower()
        return [cmd for cmd in self.history if term in cmd.lower()]
    
    def clear_history(self):
        """Geçmişi temizle"""
        self.history.clear()
        self.current_index = -1
        self.save_history()
    
    def load_history(self):
        """Geçmişi dosyadan yükle"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.current_index = len(self.history)
        except Exception:
            # Hata durumunda boş geçmiş
            self.history = []
            self.current_index = -1
    
    def save_history(self):
        """Geçmişi dosyaya kaydet"""
        try:
            data = {
                'history': self.history,
                'max_history': self.max_history
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            # Kaydetme hatası - sessizce geç
            pass 