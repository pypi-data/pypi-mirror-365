"""
PyCloud OS Core Locale
Dil, tarih, saat ve yerel ayarlar sistemi
"""

import os
import json
import logging
import locale
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class LocaleFormat(Enum):
    """Yerel format türleri"""
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"

@dataclass
class LocaleInfo:
    """Yerel ayar bilgisi"""
    code: str
    name: str
    native_name: str
    country: str
    language: str
    direction: str = "ltr"  # ltr veya rtl
    date_format: str = "%d.%m.%Y"
    time_format: str = "%H:%M"
    datetime_format: str = "%d.%m.%Y %H:%M"
    decimal_separator: str = ","
    thousands_separator: str = "."
    currency_symbol: str = "₺"
    currency_position: str = "after"  # before veya after
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        return {
            "code": self.code,
            "name": self.name,
            "native_name": self.native_name,
            "country": self.country,
            "language": self.language,
            "direction": self.direction,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "datetime_format": self.datetime_format,
            "decimal_separator": self.decimal_separator,
            "thousands_separator": self.thousands_separator,
            "currency_symbol": self.currency_symbol,
            "currency_position": self.currency_position
        }

class TranslationManager:
    """Çeviri yöneticisi"""
    
    def __init__(self, locale_dir: Path):
        self.locale_dir = locale_dir
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language = "tr_TR"
        self.fallback_language = "en_US"
        self.logger = logging.getLogger("TranslationManager")
        
        # Çeviri değişiklik callback'leri
        self.translation_callbacks: List[Callable] = []
    
    def load_translations(self, language_code: str) -> bool:
        """Çevirileri yükle"""
        try:
            translation_file = self.locale_dir / f"{language_code}.json"
            
            if not translation_file.exists():
                self.logger.warning(f"Translation file not found: {translation_file}")
                return False
            
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            self.translations[language_code] = translations
            self.logger.info(f"Loaded translations for {language_code}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load translations for {language_code}: {e}")
            return False
    
    def get_translation(self, key: str, language: str = None, **kwargs) -> str:
        """Çeviri al"""
        if language is None:
            language = self.current_language
        
        # Ana dilde ara
        if language in self.translations:
            translation = self._get_nested_value(self.translations[language], key)
            if translation:
                return self._format_translation(translation, **kwargs)
        
        # Fallback dilde ara
        if self.fallback_language in self.translations:
            translation = self._get_nested_value(self.translations[self.fallback_language], key)
            if translation:
                return self._format_translation(translation, **kwargs)
        
        # Hiçbiri bulunamazsa key'i döndür
        return key
    
    def _get_nested_value(self, data: Dict, key: str) -> Optional[str]:
        """İç içe geçmiş değer al (örn: "menu.file.open")"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def _format_translation(self, translation: str, **kwargs) -> str:
        """Çeviriyi formatla"""
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation
    
    def set_language(self, language_code: str) -> bool:
        """Dili değiştir"""
        if language_code not in self.translations:
            if not self.load_translations(language_code):
                return False
        
        old_language = self.current_language
        self.current_language = language_code
        
        # Callback'leri çağır
        for callback in self.translation_callbacks:
            try:
                callback(old_language, language_code)
            except Exception as e:
                self.logger.error(f"Translation callback failed: {e}")
        
        self.logger.info(f"Language changed from {old_language} to {language_code}")
        return True
    
    def add_translation_callback(self, callback: Callable):
        """Çeviri değişiklik callback'i ekle"""
        self.translation_callbacks.append(callback)
    
    def remove_translation_callback(self, callback: Callable):
        """Çeviri değişiklik callback'ini kaldır"""
        if callback in self.translation_callbacks:
            self.translation_callbacks.remove(callback)
    
    def get_available_languages(self) -> List[str]:
        """Mevcut dilleri al"""
        languages = []
        
        if self.locale_dir.exists():
            for file_path in self.locale_dir.glob("*.json"):
                language_code = file_path.stem
                languages.append(language_code)
        
        return sorted(languages)

class LocaleManager:
    """Ana yerel ayar yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("LocaleManager")
        
        # Dizinler
        self.locale_dir = Path("system/locale")
        self.locale_dir.mkdir(parents=True, exist_ok=True)
        
        # Çeviri yöneticisi
        self.translation_manager = TranslationManager(self.locale_dir)
        
        # Mevcut yerel ayarlar
        self.current_locale = "tr_TR"
        self.locale_info: Dict[str, LocaleInfo] = {}
        
        # Yerel ayar değişiklik callback'leri
        self.locale_callbacks: List[Callable] = []
        
        # Başlangıç
        self._create_default_locales()
        self._create_default_translations()
        self.load_locale_info()
        self.load_current_locale()
    
    def _create_default_locales(self):
        """Varsayılan yerel ayarları oluştur"""
        default_locales = {
            "tr_TR": LocaleInfo(
                code="tr_TR",
                name="Turkish (Turkey)",
                native_name="Türkçe (Türkiye)",
                country="Turkey",
                language="Turkish",
                direction="ltr",
                date_format="%d.%m.%Y",
                time_format="%H:%M",
                datetime_format="%d.%m.%Y %H:%M",
                decimal_separator=",",
                thousands_separator=".",
                currency_symbol="₺",
                currency_position="after"
            ),
            "en_US": LocaleInfo(
                code="en_US",
                name="English (United States)",
                native_name="English (United States)",
                country="United States",
                language="English",
                direction="ltr",
                date_format="%m/%d/%Y",
                time_format="%I:%M %p",
                datetime_format="%m/%d/%Y %I:%M %p",
                decimal_separator=".",
                thousands_separator=",",
                currency_symbol="$",
                currency_position="before"
            ),
            "de_DE": LocaleInfo(
                code="de_DE",
                name="German (Germany)",
                native_name="Deutsch (Deutschland)",
                country="Germany",
                language="German",
                direction="ltr",
                date_format="%d.%m.%Y",
                time_format="%H:%M",
                datetime_format="%d.%m.%Y %H:%M",
                decimal_separator=",",
                thousands_separator=".",
                currency_symbol="€",
                currency_position="after"
            )
        }
        
        # Locale bilgilerini kaydet
        locale_info_file = self.locale_dir / "locales.json"
        try:
            with open(locale_info_file, 'w', encoding='utf-8') as f:
                locale_data = {code: info.to_dict() for code, info in default_locales.items()}
                json.dump(locale_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save locale info: {e}")
    
    def _create_default_translations(self):
        """Varsayılan çevirileri oluştur"""
        # Türkçe çeviriler
        tr_translations = {
            "system": {
                "name": "PyCloud OS",
                "version": "Sürüm",
                "loading": "Yükleniyor...",
                "ready": "Hazır",
                "error": "Hata",
                "warning": "Uyarı",
                "info": "Bilgi",
                "success": "Başarılı"
            },
            "menu": {
                "file": {
                    "title": "Dosya",
                    "new": "Yeni",
                    "open": "Aç",
                    "save": "Kaydet",
                    "save_as": "Farklı Kaydet",
                    "close": "Kapat",
                    "exit": "Çıkış"
                },
                "edit": {
                    "title": "Düzenle",
                    "undo": "Geri Al",
                    "redo": "Yinele",
                    "cut": "Kes",
                    "copy": "Kopyala",
                    "paste": "Yapıştır",
                    "select_all": "Tümünü Seç"
                },
                "view": {
                    "title": "Görünüm",
                    "zoom_in": "Yakınlaştır",
                    "zoom_out": "Uzaklaştır",
                    "fullscreen": "Tam Ekran"
                },
                "help": {
                    "title": "Yardım",
                    "about": "Hakkında",
                    "documentation": "Belgeler"
                }
            },
            "ui": {
                "buttons": {
                    "ok": "Tamam",
                    "cancel": "İptal",
                    "yes": "Evet",
                    "no": "Hayır",
                    "apply": "Uygula",
                    "reset": "Sıfırla",
                    "browse": "Gözat",
                    "search": "Ara",
                    "refresh": "Yenile"
                },
                "dock": {
                    "applications": "Uygulamalar",
                    "files": "Dosyalar",
                    "settings": "Ayarlar",
                    "terminal": "Terminal"
                },
                "topbar": {
                    "cloud_menu": "Bulut Menüsü",
                    "applications": "Uygulamalar",
                    "system_settings": "Sistem Ayarları",
                    "shutdown": "Kapat",
                    "restart": "Yeniden Başlat",
                    "logout": "Oturumu Kapat"
                }
            },
            "apps": {
                "files": {
                    "name": "Dosyalar",
                    "new_folder": "Yeni Klasör",
                    "rename": "Yeniden Adlandır",
                    "delete": "Sil",
                    "properties": "Özellikler",
                    "copy": "Kopyala",
                    "cut": "Kes",
                    "paste": "Yapıştır"
                },
                "settings": {
                    "name": "Ayarlar",
                    "appearance": "Görünüm",
                    "system": "Sistem",
                    "notifications": "Bildirimler",
                    "theme": "Tema",
                    "wallpaper": "Duvar Kağıdı"
                },
                "terminal": {
                    "name": "Terminal",
                    "new_tab": "Yeni Sekme",
                    "close_tab": "Sekmeyi Kapat",
                    "clear": "Temizle",
                    "copy": "Kopyala",
                    "paste": "Yapıştır"
                }
            },
            "time": {
                "days": {
                    "monday": "Pazartesi",
                    "tuesday": "Salı",
                    "wednesday": "Çarşamba",
                    "thursday": "Perşembe",
                    "friday": "Cuma",
                    "saturday": "Cumartesi",
                    "sunday": "Pazar"
                },
                "months": {
                    "january": "Ocak",
                    "february": "Şubat",
                    "march": "Mart",
                    "april": "Nisan",
                    "may": "Mayıs",
                    "june": "Haziran",
                    "july": "Temmuz",
                    "august": "Ağustos",
                    "september": "Eylül",
                    "october": "Ekim",
                    "november": "Kasım",
                    "december": "Aralık"
                }
            }
        }
        
        # İngilizce çeviriler
        en_translations = {
            "system": {
                "name": "PyCloud OS",
                "version": "Version",
                "loading": "Loading...",
                "ready": "Ready",
                "error": "Error",
                "warning": "Warning",
                "info": "Information",
                "success": "Success"
            },
            "menu": {
                "file": {
                    "title": "File",
                    "new": "New",
                    "open": "Open",
                    "save": "Save",
                    "save_as": "Save As",
                    "close": "Close",
                    "exit": "Exit"
                },
                "edit": {
                    "title": "Edit",
                    "undo": "Undo",
                    "redo": "Redo",
                    "cut": "Cut",
                    "copy": "Copy",
                    "paste": "Paste",
                    "select_all": "Select All"
                },
                "view": {
                    "title": "View",
                    "zoom_in": "Zoom In",
                    "zoom_out": "Zoom Out",
                    "fullscreen": "Fullscreen"
                },
                "help": {
                    "title": "Help",
                    "about": "About",
                    "documentation": "Documentation"
                }
            },
            "ui": {
                "buttons": {
                    "ok": "OK",
                    "cancel": "Cancel",
                    "yes": "Yes",
                    "no": "No",
                    "apply": "Apply",
                    "reset": "Reset",
                    "browse": "Browse",
                    "search": "Search",
                    "refresh": "Refresh"
                },
                "dock": {
                    "applications": "Applications",
                    "files": "Files",
                    "settings": "Settings",
                    "terminal": "Terminal"
                },
                "topbar": {
                    "cloud_menu": "Cloud Menu",
                    "applications": "Applications",
                    "system_settings": "System Settings",
                    "shutdown": "Shutdown",
                    "restart": "Restart",
                    "logout": "Log Out"
                }
            },
            "apps": {
                "files": {
                    "name": "Files",
                    "new_folder": "New Folder",
                    "rename": "Rename",
                    "delete": "Delete",
                    "properties": "Properties",
                    "copy": "Copy",
                    "cut": "Cut",
                    "paste": "Paste"
                },
                "settings": {
                    "name": "Settings",
                    "appearance": "Appearance",
                    "system": "System",
                    "notifications": "Notifications",
                    "theme": "Theme",
                    "wallpaper": "Wallpaper"
                },
                "terminal": {
                    "name": "Terminal",
                    "new_tab": "New Tab",
                    "close_tab": "Close Tab",
                    "clear": "Clear",
                    "copy": "Copy",
                    "paste": "Paste"
                }
            },
            "time": {
                "days": {
                    "monday": "Monday",
                    "tuesday": "Tuesday",
                    "wednesday": "Wednesday",
                    "thursday": "Thursday",
                    "friday": "Friday",
                    "saturday": "Saturday",
                    "sunday": "Sunday"
                },
                "months": {
                    "january": "January",
                    "february": "February",
                    "march": "March",
                    "april": "April",
                    "may": "May",
                    "june": "June",
                    "july": "July",
                    "august": "August",
                    "september": "September",
                    "october": "October",
                    "november": "November",
                    "december": "December"
                }
            }
        }
        
        # Çeviri dosyalarını kaydet
        try:
            with open(self.locale_dir / "tr_TR.json", 'w', encoding='utf-8') as f:
                json.dump(tr_translations, f, indent=2, ensure_ascii=False)
            
            with open(self.locale_dir / "en_US.json", 'w', encoding='utf-8') as f:
                json.dump(en_translations, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Default translations created")
            
        except Exception as e:
            self.logger.error(f"Failed to create default translations: {e}")
    
    def load_locale_info(self):
        """Yerel ayar bilgilerini yükle"""
        try:
            locale_info_file = self.locale_dir / "locales.json"
            
            if locale_info_file.exists():
                with open(locale_info_file, 'r', encoding='utf-8') as f:
                    locale_data = json.load(f)
                
                for code, data in locale_data.items():
                    self.locale_info[code] = LocaleInfo(**data)
                
                self.logger.info(f"Loaded {len(self.locale_info)} locale definitions")
            
        except Exception as e:
            self.logger.error(f"Failed to load locale info: {e}")
    
    def load_current_locale(self):
        """Mevcut yerel ayarı yükle"""
        try:
            # Config'den al
            if self.kernel:
                config_manager = self.kernel.get_module("config")
                if config_manager:
                    self.current_locale = config_manager.get("locale.current", "tr_TR")
            
            # Çevirileri yükle
            self.translation_manager.load_translations(self.current_locale)
            self.translation_manager.set_language(self.current_locale)
            
            # Sistem locale'ini ayarla
            try:
                locale.setlocale(locale.LC_ALL, self.current_locale)
            except locale.Error:
                self.logger.warning(f"System locale {self.current_locale} not available")
            
            self.logger.info(f"Current locale set to {self.current_locale}")
            
        except Exception as e:
            self.logger.error(f"Failed to load current locale: {e}")
    
    def set_locale(self, locale_code: str) -> bool:
        """Yerel ayarı değiştir"""
        try:
            if locale_code not in self.locale_info:
                self.logger.error(f"Locale {locale_code} not found")
                return False
            
            old_locale = self.current_locale
            self.current_locale = locale_code
            
            # Çevirileri değiştir
            if not self.translation_manager.set_language(locale_code):
                self.current_locale = old_locale
                return False
            
            # Config'e kaydet
            if self.kernel:
                config_manager = self.kernel.get_module("config")
                if config_manager:
                    config_manager.set("locale.current", locale_code)
            
            # Sistem locale'ini ayarla
            try:
                locale.setlocale(locale.LC_ALL, locale_code)
            except locale.Error:
                self.logger.warning(f"System locale {locale_code} not available")
            
            # Callback'leri çağır
            for callback in self.locale_callbacks:
                try:
                    callback(old_locale, locale_code)
                except Exception as e:
                    self.logger.error(f"Locale callback failed: {e}")
            
            self.logger.info(f"Locale changed from {old_locale} to {locale_code}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set locale {locale_code}: {e}")
            return False
    
    def get_current_locale(self) -> str:
        """Mevcut yerel ayarı al"""
        return self.current_locale
    
    def get_locale_info(self, locale_code: str = None) -> Optional[LocaleInfo]:
        """Yerel ayar bilgisini al"""
        if locale_code is None:
            locale_code = self.current_locale
        
        return self.locale_info.get(locale_code)
    
    def get_available_locales(self) -> List[str]:
        """Mevcut yerel ayarları al"""
        return list(self.locale_info.keys())
    
    def translate(self, key: str, **kwargs) -> str:
        """Çeviri al"""
        return self.translation_manager.get_translation(key, **kwargs)
    
    def format_date(self, date: datetime, locale_code: str = None) -> str:
        """Tarihi formatla"""
        locale_info = self.get_locale_info(locale_code)
        if locale_info:
            return date.strftime(locale_info.date_format)
        return date.strftime("%d.%m.%Y")
    
    def format_time(self, time: datetime, locale_code: str = None) -> str:
        """Saati formatla"""
        locale_info = self.get_locale_info(locale_code)
        if locale_info:
            return time.strftime(locale_info.time_format)
        return time.strftime("%H:%M")
    
    def format_datetime(self, dt: datetime, locale_code: str = None) -> str:
        """Tarih-saati formatla"""
        locale_info = self.get_locale_info(locale_code)
        if locale_info:
            return dt.strftime(locale_info.datetime_format)
        return dt.strftime("%d.%m.%Y %H:%M")
    
    def format_number(self, number: float, decimals: int = 2, locale_code: str = None) -> str:
        """Sayıyı formatla"""
        locale_info = self.get_locale_info(locale_code)
        if not locale_info:
            return f"{number:.{decimals}f}"
        
        # Sayıyı formatla
        formatted = f"{number:.{decimals}f}"
        
        # Ondalık ayırıcıyı değiştir
        if locale_info.decimal_separator != ".":
            formatted = formatted.replace(".", locale_info.decimal_separator)
        
        # Binlik ayırıcı ekle
        if abs(number) >= 1000 and locale_info.thousands_separator:
            parts = formatted.split(locale_info.decimal_separator)
            integer_part = parts[0]
            decimal_part = parts[1] if len(parts) > 1 else ""
            
            # Binlik ayırıcı ekle
            formatted_integer = ""
            for i, digit in enumerate(reversed(integer_part)):
                if i > 0 and i % 3 == 0:
                    formatted_integer = locale_info.thousands_separator + formatted_integer
                formatted_integer = digit + formatted_integer
            
            formatted = formatted_integer
            if decimal_part:
                formatted += locale_info.decimal_separator + decimal_part
        
        return formatted
    
    def format_currency(self, amount: float, locale_code: str = None) -> str:
        """Para birimini formatla"""
        locale_info = self.get_locale_info(locale_code)
        if not locale_info:
            return f"{amount:.2f}"
        
        formatted_amount = self.format_number(amount, 2, locale_code)
        
        if locale_info.currency_position == "before":
            return f"{locale_info.currency_symbol}{formatted_amount}"
        else:
            return f"{formatted_amount} {locale_info.currency_symbol}"
    
    def add_locale_callback(self, callback: Callable):
        """Yerel ayar değişiklik callback'i ekle"""
        self.locale_callbacks.append(callback)
    
    def remove_locale_callback(self, callback: Callable):
        """Yerel ayar değişiklik callback'ini kaldır"""
        if callback in self.locale_callbacks:
            self.locale_callbacks.remove(callback)
    
    def shutdown(self):
        """Locale manager'ı kapat"""
        self.logger.info("Locale manager shutdown")

# Kolaylık fonksiyonları
_locale_manager = None

def init_locale_manager(kernel=None) -> LocaleManager:
    """Locale manager'ı başlat"""
    global _locale_manager
    _locale_manager = LocaleManager(kernel)
    return _locale_manager

def get_locale_manager() -> Optional[LocaleManager]:
    """Locale manager'ı al"""
    return _locale_manager

def translate(key: str, **kwargs) -> str:
    """Çeviri al (kısayol)"""
    if _locale_manager:
        return _locale_manager.translate(key, **kwargs)
    return key

def format_date(date: datetime) -> str:
    """Tarihi formatla (kısayol)"""
    if _locale_manager:
        return _locale_manager.format_date(date)
    return date.strftime("%d.%m.%Y")

def format_time(time: datetime) -> str:
    """Saati formatla (kısayol)"""
    if _locale_manager:
        return _locale_manager.format_time(time)
    return time.strftime("%H:%M")

def format_currency(amount: float) -> str:
    """Para birimini formatla (kısayol)"""
    if _locale_manager:
        return _locale_manager.format_currency(amount)
    return f"{amount:.2f}" 