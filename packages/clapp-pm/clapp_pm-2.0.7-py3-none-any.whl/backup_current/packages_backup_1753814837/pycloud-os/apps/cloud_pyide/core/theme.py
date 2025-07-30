"""
Cloud PyIDE - Tema Uygulayıcı ve Renklendirme
Tema sistemi ve syntax highlighting
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

try:
    from PyQt6.QtGui import QColor, QFont, QPalette
    from PyQt6.QtCore import QObject, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class ThemeMode(Enum):
    """Tema modları"""
    LIGHT = "light"
    DARK = "dark"
    MONOKAI = "monokai"
    DRACULA = "dracula"

class ThemeManager(QObject if PYQT_AVAILABLE else object):
    """Tema yöneticisi"""
    
    if PYQT_AVAILABLE:
        theme_changed = pyqtSignal(str)
    
    def __init__(self):
        if PYQT_AVAILABLE:
            super().__init__()
        
        self.logger = logging.getLogger("ThemeManager")
        
        # Tema dizini
        self.themes_dir = Path("themes")
        self.themes_dir.mkdir(exist_ok=True)
        
        # Mevcut tema
        self.current_theme = ThemeMode.DARK
        
        # Tema tanımları
        self.themes = self._load_default_themes()
        
        # Kullanıcı temalarını yükle
        self.load_user_themes()
    
    def _load_default_themes(self) -> Dict[str, Dict[str, Any]]:
        """Varsayılan temaları yükle"""
        themes = {}
        
        # Dark tema
        themes["dark"] = {
            "name": "Dark",
            "type": "dark",
            "colors": {
                "background": "#1e1e1e",
                "foreground": "#d4d4d4",
                "selection": "#264f78",
                "line_highlight": "#2a2d2e",
                "line_number_bg": "#252526",
                "line_number_fg": "#858585",
                "sidebar_bg": "#252526",
                "sidebar_fg": "#cccccc",
                "sidebar_selection": "#094771",
                "toolbar_bg": "#2d2d30",
                "toolbar_fg": "#cccccc",
                "statusbar_bg": "#007acc",
                "statusbar_fg": "#ffffff",
                "border": "#3c3c3c"
            },
            "syntax": {
                "keyword": "#569cd6",
                "string": "#ce9178",
                "comment": "#6a9955",
                "number": "#b5cea8",
                "function": "#dcdcaa",
                "class": "#4ec9b0",
                "decorator": "#ffd700",
                "builtin": "#569cd6",
                "operator": "#d4d4d4",
                "variable": "#9cdcfe"
            },
            "fonts": {
                "editor": {"family": "JetBrains Mono", "size": 12},
                "ui": {"family": "Segoe UI", "size": 9}
            }
        }
        
        # Light tema
        themes["light"] = {
            "name": "Light",
            "type": "light",
            "colors": {
                "background": "#ffffff",
                "foreground": "#000000",
                "selection": "#add6ff",
                "line_highlight": "#f0f0f0",
                "line_number_bg": "#f8f8f8",
                "line_number_fg": "#237893",
                "sidebar_bg": "#f3f3f3",
                "sidebar_fg": "#000000",
                "sidebar_selection": "#0078d4",
                "toolbar_bg": "#f3f3f3",
                "toolbar_fg": "#000000",
                "statusbar_bg": "#0078d4",
                "statusbar_fg": "#ffffff",
                "border": "#cccccc"
            },
            "syntax": {
                "keyword": "#0000ff",
                "string": "#008000",
                "comment": "#808080",
                "number": "#800080",
                "function": "#000080",
                "class": "#008080",
                "decorator": "#ff8000",
                "builtin": "#0000ff",
                "operator": "#000000",
                "variable": "#000000"
            },
            "fonts": {
                "editor": {"family": "JetBrains Mono", "size": 12},
                "ui": {"family": "Segoe UI", "size": 9}
            }
        }
        
        # Monokai tema
        themes["monokai"] = {
            "name": "Monokai",
            "type": "dark",
            "colors": {
                "background": "#272822",
                "foreground": "#f8f8f2",
                "selection": "#49483e",
                "line_highlight": "#3e3d32",
                "line_number_bg": "#2f2f2f",
                "line_number_fg": "#90908a",
                "sidebar_bg": "#2f2f2f",
                "sidebar_fg": "#f8f8f2",
                "sidebar_selection": "#49483e",
                "toolbar_bg": "#2f2f2f",
                "toolbar_fg": "#f8f8f2",
                "statusbar_bg": "#a6e22e",
                "statusbar_fg": "#272822",
                "border": "#49483e"
            },
            "syntax": {
                "keyword": "#f92672",
                "string": "#e6db74",
                "comment": "#75715e",
                "number": "#ae81ff",
                "function": "#a6e22e",
                "class": "#66d9ef",
                "decorator": "#fd971f",
                "builtin": "#f92672",
                "operator": "#f92672",
                "variable": "#f8f8f2"
            },
            "fonts": {
                "editor": {"family": "Fira Code", "size": 12},
                "ui": {"family": "Segoe UI", "size": 9}
            }
        }
        
        # Dracula tema
        themes["dracula"] = {
            "name": "Dracula",
            "type": "dark",
            "colors": {
                "background": "#282a36",
                "foreground": "#f8f8f2",
                "selection": "#44475a",
                "line_highlight": "#44475a",
                "line_number_bg": "#2f3349",
                "line_number_fg": "#6272a4",
                "sidebar_bg": "#2f3349",
                "sidebar_fg": "#f8f8f2",
                "sidebar_selection": "#44475a",
                "toolbar_bg": "#2f3349",
                "toolbar_fg": "#f8f8f2",
                "statusbar_bg": "#bd93f9",
                "statusbar_fg": "#282a36",
                "border": "#44475a"
            },
            "syntax": {
                "keyword": "#ff79c6",
                "string": "#f1fa8c",
                "comment": "#6272a4",
                "number": "#bd93f9",
                "function": "#50fa7b",
                "class": "#8be9fd",
                "decorator": "#ffb86c",
                "builtin": "#ff79c6",
                "operator": "#ff79c6",
                "variable": "#f8f8f2"
            },
            "fonts": {
                "editor": {"family": "Fira Code", "size": 12},
                "ui": {"family": "Segoe UI", "size": 9}
            }
        }
        
        return themes
    
    def load_user_themes(self):
        """Kullanıcı temalarını yükle"""
        try:
            for theme_file in self.themes_dir.glob("*.json"):
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                
                theme_id = theme_file.stem
                self.themes[theme_id] = theme_data
                
                self.logger.info(f"Loaded user theme: {theme_data.get('name', theme_id)}")
                
        except Exception as e:
            self.logger.error(f"Error loading user themes: {e}")
    
    def get_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Tema al"""
        return self.themes.get(theme_id)
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Mevcut temayı al"""
        return self.themes.get(self.current_theme.value, self.themes["dark"])
    
    def set_theme(self, theme_id: str) -> bool:
        """Tema ayarla"""
        try:
            if theme_id not in self.themes:
                self.logger.warning(f"Theme not found: {theme_id}")
                return False
            
            # Enum değerini güncelle
            try:
                self.current_theme = ThemeMode(theme_id)
            except ValueError:
                # Kullanıcı teması için string olarak sakla
                self.current_theme = theme_id
            
            # Sinyal gönder
            if PYQT_AVAILABLE and hasattr(self, 'theme_changed'):
                self.theme_changed.emit(theme_id)
            
            self.logger.info(f"Theme changed to: {theme_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting theme: {e}")
            return False
    
    def get_available_themes(self) -> Dict[str, str]:
        """Mevcut temaları al"""
        return {theme_id: theme_data.get("name", theme_id) 
                for theme_id, theme_data in self.themes.items()}
    
    def create_theme(self, theme_id: str, theme_data: Dict[str, Any]) -> bool:
        """Yeni tema oluştur"""
        try:
            # Tema dosyasını kaydet
            theme_file = self.themes_dir / f"{theme_id}.json"
            
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            # Tema listesine ekle
            self.themes[theme_id] = theme_data
            
            self.logger.info(f"Created theme: {theme_data.get('name', theme_id)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating theme: {e}")
            return False
    
    def delete_theme(self, theme_id: str) -> bool:
        """Tema sil"""
        try:
            # Varsayılan temaları silmeye izin verme
            if theme_id in ["dark", "light", "monokai", "dracula"]:
                self.logger.warning(f"Cannot delete default theme: {theme_id}")
                return False
            
            if theme_id not in self.themes:
                self.logger.warning(f"Theme not found: {theme_id}")
                return False
            
            # Dosyayı sil
            theme_file = self.themes_dir / f"{theme_id}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            # Listeden kaldır
            del self.themes[theme_id]
            
            # Eğer mevcut tema siliniyorsa dark'a geç
            if self.current_theme == theme_id:
                self.set_theme("dark")
            
            self.logger.info(f"Deleted theme: {theme_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting theme: {e}")
            return False
    
    def get_color(self, color_key: str) -> str:
        """Renk al"""
        theme = self.get_current_theme()
        return theme.get("colors", {}).get(color_key, "#000000")
    
    def get_syntax_color(self, syntax_key: str) -> str:
        """Syntax rengi al"""
        theme = self.get_current_theme()
        return theme.get("syntax", {}).get(syntax_key, "#000000")
    
    def get_font(self, font_key: str) -> Dict[str, Any]:
        """Font al"""
        theme = self.get_current_theme()
        fonts = theme.get("fonts", {})
        
        if font_key in fonts:
            return fonts[font_key]
        
        # Varsayılan font
        return {"family": "Consolas", "size": 12}
    
    def is_dark_theme(self) -> bool:
        """Koyu tema mı?"""
        theme = self.get_current_theme()
        return theme.get("type", "dark") == "dark"
    
    def generate_stylesheet(self, component: str) -> str:
        """Bileşen için stylesheet oluştur"""
        theme = self.get_current_theme()
        colors = theme.get("colors", {})
        
        if component == "editor":
            return f"""
                QPlainTextEdit {{
                    background-color: {colors.get('background', '#1e1e1e')};
                    color: {colors.get('foreground', '#d4d4d4')};
                    border: none;
                    selection-background-color: {colors.get('selection', '#264f78')};
                }}
            """
        
        elif component == "sidebar":
            return f"""
                QTreeWidget {{
                    background-color: {colors.get('sidebar_bg', '#252526')};
                    color: {colors.get('sidebar_fg', '#cccccc')};
                    border: none;
                    outline: none;
                }}
                
                QTreeWidget::item:selected {{
                    background-color: {colors.get('sidebar_selection', '#094771')};
                    color: #ffffff;
                }}
                
                QTreeWidget::item:hover {{
                    background-color: {colors.get('line_highlight', '#2a2d2e')};
                }}
            """
        
        elif component == "toolbar":
            return f"""
                QToolBar {{
                    background-color: {colors.get('toolbar_bg', '#2d2d30')};
                    color: {colors.get('toolbar_fg', '#cccccc')};
                    border: none;
                }}
                
                QToolButton {{
                    background-color: transparent;
                    color: {colors.get('toolbar_fg', '#cccccc')};
                    border: none;
                    padding: 4px;
                }}
                
                QToolButton:hover {{
                    background-color: {colors.get('line_highlight', '#2a2d2e')};
                }}
            """
        
        elif component == "statusbar":
            return f"""
                QStatusBar {{
                    background-color: {colors.get('statusbar_bg', '#007acc')};
                    color: {colors.get('statusbar_fg', '#ffffff')};
                    border: none;
                }}
            """
        
        return ""
    
    def export_theme(self, theme_id: str, file_path: Path) -> bool:
        """Tema dışa aktar"""
        try:
            if theme_id not in self.themes:
                self.logger.warning(f"Theme not found: {theme_id}")
                return False
            
            theme_data = self.themes[theme_id]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported theme {theme_id} to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting theme: {e}")
            return False
    
    def import_theme(self, file_path: Path) -> bool:
        """Tema içe aktar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Tema ID'sini dosya adından al
            theme_id = file_path.stem
            
            # Tema oluştur
            return self.create_theme(theme_id, theme_data)
            
        except Exception as e:
            self.logger.error(f"Error importing theme: {e}")
            return False 