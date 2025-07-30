"""
Cloud Terminal - Tema Yöneticisi
Terminal stilleri ve renk temaları
"""

from typing import Dict, Any

class TerminalThemes:
    """Terminal tema yöneticisi"""
    
    def __init__(self):
        self.themes = {
            'dark': self._dark_theme(),
            'light': self._light_theme(),
            'hacker': self._hacker_theme(),
            'glass': self._glass_theme(),
            'classic': self._classic_theme()
        }
    
    def _dark_theme(self) -> Dict[str, Any]:
        """Koyu tema"""
        return {
            'name': 'Dark',
            'background': '#1e1e1e',
            'foreground': '#ffffff',
            'accent': '#00ff88',
            'error': '#ff6b6b',
            'success': '#51cf66',
            'warning': '#ffd43b',
            'info': '#74c0fc',
            'border': '#3c3c3c',
            'secondary_bg': '#2d2d2d',
            'stylesheet': """
                /* Ana pencere */
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                
                /* Tab widget */
                QTabWidget::pane {
                    border: 1px solid #3c3c3c;
                    background-color: #1e1e1e;
                }
                
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3c3c3c;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    border-bottom-color: #1e1e1e;
                    color: #00ff88;
                }
                
                QTabBar::tab:hover {
                    background-color: #3c3c3c;
                }
                
                /* Terminal çıktısı */
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: none;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    selection-background-color: #3c3c3c;
                }
                
                /* Terminal girişi */
                QLineEdit {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 2px solid #3c3c3c;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                }
                
                QLineEdit:focus {
                    border-color: #00ff88;
                    background-color: #1e1e1e;
                }
                
                /* Butonlar */
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: 600;
                }
                
                QPushButton:hover {
                    background-color: #14a085;
                }
                
                QPushButton#primaryButton {
                    background-color: #007acc;
                }
                
                QPushButton#primaryButton:hover {
                    background-color: #1e90ff;
                }
            """
        }
    
    def _light_theme(self) -> Dict[str, Any]:
        """Açık tema"""
        return {
            'name': 'Light',
            'background': '#ffffff',
            'foreground': '#000000',
            'accent': '#007acc',
            'error': '#d63031',
            'success': '#00b894',
            'warning': '#fdcb6e',
            'info': '#0984e3',
            'border': '#e0e0e0',
            'secondary_bg': '#f5f5f5',
            'stylesheet': """
                /* Ana pencere */
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                
                /* Tab widget */
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    background-color: #ffffff;
                }
                
                QTabBar::tab {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #e0e0e0;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom-color: #ffffff;
                    color: #007acc;
                }
                
                QTabBar::tab:hover {
                    background-color: #e8e8e8;
                }
                
                /* Terminal çıktısı */
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #e0e0e0;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    selection-background-color: #b3d9ff;
                }
                
                /* Terminal girişi */
                QLineEdit {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                }
                
                QLineEdit:focus {
                    border-color: #007acc;
                    background-color: #ffffff;
                }
                
                /* Butonlar */
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: 600;
                }
                
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """
        }
    
    def _hacker_theme(self) -> Dict[str, Any]:
        """Hacker teması"""
        return {
            'name': 'Hacker',
            'background': '#000000',
            'foreground': '#00ff00',
            'accent': '#00ff00',
            'error': '#ff0000',
            'success': '#00ff00',
            'warning': '#ffff00',
            'info': '#00ffff',
            'border': '#003300',
            'secondary_bg': '#001100',
            'stylesheet': """
                /* Ana pencere */
                QMainWindow {
                    background-color: #000000;
                    color: #00ff00;
                }
                
                /* Tab widget */
                QTabWidget::pane {
                    border: 1px solid #003300;
                    background-color: #000000;
                }
                
                QTabBar::tab {
                    background-color: #001100;
                    color: #00ff00;
                    border: 1px solid #003300;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                
                QTabBar::tab:selected {
                    background-color: #000000;
                    border-bottom-color: #000000;
                    color: #00ff00;
                    font-weight: bold;
                }
                
                QTabBar::tab:hover {
                    background-color: #002200;
                }
                
                /* Terminal çıktısı */
                QTextEdit {
                    background-color: #000000;
                    color: #00ff00;
                    border: none;
                    font-family: 'Courier New', 'Monaco', monospace;
                    font-weight: bold;
                    selection-background-color: #003300;
                }
                
                /* Terminal girişi */
                QLineEdit {
                    background-color: #001100;
                    color: #00ff00;
                    border: 2px solid #003300;
                    border-radius: 0px;
                    padding: 8px 12px;
                    font-family: 'Courier New', 'Monaco', monospace;
                    font-weight: bold;
                }
                
                QLineEdit:focus {
                    border-color: #00ff00;
                    background-color: #000000;
                }
                
                /* Butonlar */
                QPushButton {
                    background-color: #003300;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    padding: 6px 12px;
                    border-radius: 0px;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #005500;
                }
            """
        }
    
    def _glass_theme(self) -> Dict[str, Any]:
        """Cam efekti teması"""
        return {
            'name': 'Glass',
            'background': 'rgba(30, 30, 30, 0.8)',
            'foreground': '#ffffff',
            'accent': '#74c0fc',
            'error': '#ff6b6b',
            'success': '#51cf66',
            'warning': '#ffd43b',
            'info': '#74c0fc',
            'border': 'rgba(255, 255, 255, 0.2)',
            'secondary_bg': 'rgba(45, 45, 45, 0.8)',
            'stylesheet': """
                /* Ana pencere */
                QMainWindow {
                    background-color: rgba(30, 30, 30, 0.9);
                    color: #ffffff;
                }
                
                /* Tab widget */
                QTabWidget::pane {
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    background-color: rgba(30, 30, 30, 0.8);
                    border-radius: 8px;
                }
                
                QTabBar::tab {
                    background-color: rgba(45, 45, 45, 0.8);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                }
                
                QTabBar::tab:selected {
                    background-color: rgba(30, 30, 30, 0.9);
                    border-bottom-color: rgba(30, 30, 30, 0.9);
                    color: #74c0fc;
                }
                
                QTabBar::tab:hover {
                    background-color: rgba(60, 60, 60, 0.8);
                }
                
                /* Terminal çıktısı */
                QTextEdit {
                    background-color: rgba(30, 30, 30, 0.7);
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    selection-background-color: rgba(116, 192, 252, 0.3);
                }
                
                /* Terminal girişi */
                QLineEdit {
                    background-color: rgba(45, 45, 45, 0.8);
                    color: #ffffff;
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                }
                
                QLineEdit:focus {
                    border-color: #74c0fc;
                    background-color: rgba(30, 30, 30, 0.9);
                }
                
                /* Butonlar */
                QPushButton {
                    background-color: rgba(116, 192, 252, 0.8);
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 8px;
                    font-weight: 600;
                }
                
                QPushButton:hover {
                    background-color: rgba(116, 192, 252, 1.0);
                }
            """
        }
    
    def _classic_theme(self) -> Dict[str, Any]:
        """Klasik terminal teması"""
        return {
            'name': 'Classic',
            'background': '#2e3440',
            'foreground': '#d8dee9',
            'accent': '#88c0d0',
            'error': '#bf616a',
            'success': '#a3be8c',
            'warning': '#ebcb8b',
            'info': '#81a1c1',
            'border': '#4c566a',
            'secondary_bg': '#3b4252',
            'stylesheet': """
                /* Ana pencere */
                QMainWindow {
                    background-color: #2e3440;
                    color: #d8dee9;
                }
                
                /* Tab widget */
                QTabWidget::pane {
                    border: 1px solid #4c566a;
                    background-color: #2e3440;
                }
                
                QTabBar::tab {
                    background-color: #3b4252;
                    color: #d8dee9;
                    border: 1px solid #4c566a;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                
                QTabBar::tab:selected {
                    background-color: #2e3440;
                    border-bottom-color: #2e3440;
                    color: #88c0d0;
                }
                
                QTabBar::tab:hover {
                    background-color: #434c5e;
                }
                
                /* Terminal çıktısı */
                QTextEdit {
                    background-color: #2e3440;
                    color: #d8dee9;
                    border: none;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    selection-background-color: #4c566a;
                }
                
                /* Terminal girişi */
                QLineEdit {
                    background-color: #3b4252;
                    color: #d8dee9;
                    border: 2px solid #4c566a;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                }
                
                QLineEdit:focus {
                    border-color: #88c0d0;
                    background-color: #2e3440;
                }
                
                /* Butonlar */
                QPushButton {
                    background-color: #5e81ac;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: 600;
                }
                
                QPushButton:hover {
                    background-color: #81a1c1;
                }
            """
        }
    
    def get_theme(self, theme_name: str) -> Dict[str, Any]:
        """Tema al"""
        return self.themes.get(theme_name.lower(), self.themes['dark'])
    
    def get_available_themes(self) -> list:
        """Mevcut temaları al"""
        return list(self.themes.keys())
    
    def apply_theme(self, widget, theme_name: str):
        """Widget'a tema uygula"""
        theme = self.get_theme(theme_name)
        if hasattr(widget, 'setStyleSheet'):
            widget.setStyleSheet(theme['stylesheet'])
    
    def apply_terminal_theme(self, terminal_widget, theme_name: str):
        """Terminal widget'ına tema uygula"""
        theme = self.get_theme(theme_name)
        
        if hasattr(terminal_widget, 'output'):
            # Terminal çıktısı renkleri güncelle
            output = terminal_widget.output
            output.default_color = theme['foreground']
            output.error_color = theme['error']
            output.success_color = theme['success']
            output.warning_color = theme['warning']
            output.info_color = theme['info']
            
            # Stil uygula
            output.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {theme['background']};
                    color: {theme['foreground']};
                    border: none;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    selection-background-color: {theme['border']};
                }}
            """)
        
        if hasattr(terminal_widget, 'input'):
            # Terminal girişi
            terminal_widget.input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme['secondary_bg']};
                    color: {theme['foreground']};
                    border: 2px solid {theme['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                }}
                
                QLineEdit:focus {{
                    border-color: {theme['accent']};
                    background-color: {theme['background']};
                }}
            """)
        
        if hasattr(terminal_widget, 'prompt_label'):
            # Prompt etiketi
            terminal_widget.prompt_label.setStyleSheet(f"color: {theme['accent']};")
    
    def get_theme_colors(self, theme_name: str) -> Dict[str, str]:
        """Tema renklerini al"""
        theme = self.get_theme(theme_name)
        return {
            'background': theme['background'],
            'foreground': theme['foreground'],
            'accent': theme['accent'],
            'error': theme['error'],
            'success': theme['success'],
            'warning': theme['warning'],
            'info': theme['info'],
            'border': theme['border'],
            'secondary_bg': theme['secondary_bg']
        } 