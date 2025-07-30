"""
Cloud Settings - Canlı Önizleme Yöneticisi
Ayar değişikliklerini anında önizleme
"""

import logging
from typing import Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class LivePreviewManager(QObject):
    """Canlı önizleme yöneticisi"""
    
    preview_updated = pyqtSignal(dict)  # preview_data
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("LivePreviewManager")
        
        self.enabled = True
        self.preview_data = {}
        
        # Debounce timer - çok sık güncellemeyi önler
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._emit_preview_update)
        
        self.logger.info("Live Preview Manager initialized")
    
    def set_enabled(self, enabled: bool):
        """Canlı önizlemeyi etkinleştir/devre dışı bırak"""
        self.enabled = enabled
        
        if not enabled:
            self.preview_data.clear()
            self.preview_updated.emit({})
        
        self.logger.info(f"Live preview {'enabled' if enabled else 'disabled'}")
    
    def update_preview(self, category: str, settings: Dict[str, Any]):
        """Önizlemeyi güncelle"""
        if not self.enabled:
            return
        
        try:
            # Kategori bazlı önizleme verisi oluştur
            if category == "appearance":
                self._update_appearance_preview(settings)
            elif category == "widgets":
                self._update_widgets_preview(settings)
            elif category == "system":
                self._update_system_preview(settings)
            elif category == "notifications":
                self._update_notifications_preview(settings)
            
            # Debounced güncelleme
            self.update_timer.start(300)  # 300ms bekle
            
        except Exception as e:
            self.logger.error(f"Preview update failed: {e}")
    
    def _update_appearance_preview(self, settings: Dict[str, Any]):
        """Görünüm önizlemesi güncelle"""
        preview_data = {}
        
        # Tema
        if "theme" in settings:
            theme_names = {
                "light": "Açık",
                "dark": "Koyu", 
                "auto": "Otomatik"
            }
            preview_data["theme"] = theme_names.get(settings["theme"], settings["theme"])
        
        # Duvar kağıdı
        if "wallpaper_path" in settings and settings["wallpaper_path"]:
            import os
            wallpaper_name = os.path.basename(settings["wallpaper_path"])
            if len(wallpaper_name) > 20:
                wallpaper_name = wallpaper_name[:17] + "..."
            preview_data["wallpaper"] = wallpaper_name
        
        # Dock konumu
        if "dock_position" in settings:
            position_names = {
                "alt": "Alt",
                "üst": "Üst",
                "sol": "Sol",
                "sağ": "Sağ"
            }
            preview_data["dock_position"] = position_names.get(settings["dock_position"], settings["dock_position"])
        
        # Dock boyutu
        if "dock_size" in settings:
            preview_data["dock_size"] = f"{settings['dock_size']}px"
        
        # Vurgu rengi
        if "accent_color" in settings:
            preview_data["accent_color"] = settings["accent_color"]
        
        self.preview_data.update(preview_data)
    
    def _update_widgets_preview(self, settings: Dict[str, Any]):
        """Widget önizlemesi güncelle"""
        preview_data = {}
        
        # Etkin widget'lar
        if "enabled_widgets" in settings:
            widget_count = len(settings["enabled_widgets"])
            preview_data["widgets_count"] = f"{widget_count} widget"
        
        # Widget şeffaflığı
        if "widget_transparency" in settings:
            transparency = int(settings["widget_transparency"] * 100)
            preview_data["widget_transparency"] = f"%{transparency} şeffaf"
        
        # Otomatik düzenleme
        if "auto_arrange" in settings:
            preview_data["auto_arrange"] = "Otomatik düzenleme" if settings["auto_arrange"] else "Manuel düzenleme"
        
        self.preview_data.update(preview_data)
    
    def _update_system_preview(self, settings: Dict[str, Any]):
        """Sistem önizlemesi güncelle"""
        preview_data = {}
        
        # Animasyonlar
        if "animations" in settings:
            preview_data["animations"] = "Animasyonlar açık" if settings["animations"] else "Animasyonlar kapalı"
        
        # Şeffaflık
        if "transparency" in settings:
            preview_data["transparency"] = "Şeffaflık açık" if settings["transparency"] else "Şeffaflık kapalı"
        
        # Bellek sınırı
        if "memory_limit" in settings:
            preview_data["memory_limit"] = f"{settings['memory_limit']} MB bellek"
        
        # Dil
        if "language" in settings:
            lang_names = {
                "tr_TR": "Türkçe",
                "en_US": "English",
                "de_DE": "Deutsch"
            }
            preview_data["language"] = lang_names.get(settings["language"], settings["language"])
        
        self.preview_data.update(preview_data)
    
    def _update_notifications_preview(self, settings: Dict[str, Any]):
        """Bildirim önizlemesi güncelle"""
        preview_data = {}
        
        # Bildirimler etkin mi
        if "enable_notifications" in settings:
            preview_data["notifications"] = "Bildirimler açık" if settings["enable_notifications"] else "Bildirimler kapalı"
        
        # Bildirim konumu
        if "notification_position" in settings:
            position_names = {
                "sağ_üst": "Sağ üst",
                "sol_üst": "Sol üst",
                "sağ_alt": "Sağ alt",
                "sol_alt": "Sol alt",
                "merkez": "Merkez"
            }
            preview_data["notification_position"] = position_names.get(settings["notification_position"], settings["notification_position"])
        
        # Bildirim süresi
        if "notification_duration" in settings:
            preview_data["notification_duration"] = f"{settings['notification_duration']} saniye"
        
        # Maksimum bildirim sayısı
        if "max_notifications" in settings:
            preview_data["max_notifications"] = f"Max {settings['max_notifications']} bildirim"
        
        self.preview_data.update(preview_data)
    
    def _emit_preview_update(self):
        """Önizleme güncellemesini gönder"""
        if self.enabled and self.preview_data:
            self.preview_updated.emit(self.preview_data.copy())
            self.logger.debug(f"Preview updated: {len(self.preview_data)} items")
    
    def get_preview_data(self) -> Dict[str, Any]:
        """Mevcut önizleme verisini al"""
        return self.preview_data.copy()
    
    def clear_preview(self):
        """Önizlemeyi temizle"""
        self.preview_data.clear()
        if self.enabled:
            self.preview_updated.emit({})
    
    def cleanup(self):
        """Temizlik işlemleri"""
        self.update_timer.stop()
        self.preview_data.clear()
        self.logger.info("Live Preview Manager cleaned up") 