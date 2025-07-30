"""
PyCloud OS Config Manager
Sistem yapılandırması ve tüm modüllerin ortak ayar altyapısı
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

class ConfigManager:
    """Sistem yapılandırma yöneticisi"""
    
    def __init__(self):
        self.logger = logging.getLogger("Config")
        self.config_dir = Path("system/config")
        self.config_file = self.config_dir / "config.json"
        self.backup_file = self.config_dir / "config.bak"
        self.history_file = self.config_dir / "config.history"
        
        # Varsayılan yapılandırma
        self.default_config = {
            "system": {
                "version": "0.9.0-dev",
                "language": "tr_TR",
                "timezone": "Europe/Istanbul",
                "theme": "auto",
                "debug_mode": False
            },
            "ui": {
                "theme": "dark",
                "language": "tr_TR",
                "font_family": "Arial",
                "font_size": 13,
                "enable_animations": True,
                "enable_transparency": True,
                "show_desktop_icons": True
            },
            "dock": {
                "position": "bottom",
                "size": "medium",
                "auto_hide": False,
                "magnification": True
            },
            "desktop": {
                "wallpaper": "system/wallpapers/default.jpg",
                "icon_size": "medium",
                "grid_snap": True
            },
            "security": {
                "require_password": True,
                "session_timeout": 3600,
                "auto_lock": False
            },
            "modules": {}
        }
        
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Yapılandırmayı yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info("Configuration loaded successfully")
            else:
                self.config = self.default_config.copy()
                self.save_config()
                self.logger.info("Default configuration created")
                
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """Yapılandırmayı kaydet"""
        try:
            # Mevcut config'i yedekle
            if self.config_file.exists():
                shutil.copy2(self.config_file, self.backup_file)
            
            # Yeni config'i kaydet
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Geçmişe ekle
            self._add_to_history()
            
            self.logger.info("Configuration saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            raise
    
    def _add_to_history(self):
        """Yapılandırma geçmişine ekle"""
        try:
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Yeni entry ekle
            history.append({
                "timestamp": datetime.now().isoformat(),
                "config": self.config.copy()
            })
            
            # Son 10 değişikliği tut
            if len(history) > 10:
                history = history[-10:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.warning(f"Failed to save config history: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Yapılandırma değeri al"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Yapılandırma değeri ayarla"""
        keys = key.split('.')
        config = self.config
        
        # İç içe dict yapısını oluştur
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
        
        self.logger.info(f"Config updated: {key} = {value}")
    
    def get_module_config(self, module_name: str) -> Dict:
        """Modül yapılandırmasını al"""
        return self.get(f"modules.{module_name}", {})
    
    def set_module_config(self, module_name: str, config: Dict):
        """Modül yapılandırmasını ayarla"""
        self.set(f"modules.{module_name}", config)
    
    def reset_to_defaults(self):
        """Varsayılan ayarlara dön"""
        self.config = self.default_config.copy()
        self.save_config()
        self.logger.info("Configuration reset to defaults")
    
    def restore_backup(self):
        """Yedekten geri yükle"""
        try:
            if self.backup_file.exists():
                shutil.copy2(self.backup_file, self.config_file)
                self.load_config()
                self.logger.info("Configuration restored from backup")
                return True
            else:
                self.logger.warning("No backup file found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False
    
    def get_history(self) -> List[Dict]:
        """Yapılandırma geçmişini al"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Failed to load config history: {e}")
            return []
    
    def restore_from_history(self, index: int) -> bool:
        """Geçmişten geri yükle"""
        try:
            history = self.get_history()
            if 0 <= index < len(history):
                self.config = history[index]["config"]
                self.save_config()
                self.logger.info(f"Configuration restored from history index {index}")
                return True
            else:
                self.logger.warning(f"Invalid history index: {index}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to restore from history: {e}")
            return False
    
    def export_config(self, file_path: str) -> bool:
        """Yapılandırmayı dışa aktar"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuration exported to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export config: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Yapılandırmayı içe aktar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Geçerli yapılandırmayı yedekle
            self.save_config()
            
            # Yeni yapılandırmayı yükle
            self.config = imported_config
            self.save_config()
            
            self.logger.info(f"Configuration imported from {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to import config: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Yapılandırmayı doğrula ve hataları döndür"""
        errors = []
        
        # Gerekli anahtarları kontrol et
        required_keys = [
            "system.version",
            "system.language", 
            "ui.theme",
            "dock.position"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                errors.append(f"Missing required key: {key}")
        
        # Değer türlerini kontrol et
        type_checks = {
            "ui.font_size": int,
            "ui.animations": bool,
            "dock.auto_hide": bool,
            "security.session_timeout": int
        }
        
        for key, expected_type in type_checks.items():
            value = self.get(key)
            if value is not None and not isinstance(value, expected_type):
                errors.append(f"Invalid type for {key}: expected {expected_type.__name__}")
        
        return errors
    
    def get_all(self) -> Dict:
        """Tüm yapılandırmayı döndür"""
        return self.config.copy()
    
    def shutdown(self):
        """Modül kapatma"""
        self.save_config()
        self.logger.info("Config manager shutdown")

# Global config instance
_config_manager = None

def init_config(kernel=None) -> ConfigManager:
    """Config manager'ı başlat"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config_manager() -> Optional[ConfigManager]:
    """Config manager'ı al"""
    return _config_manager 