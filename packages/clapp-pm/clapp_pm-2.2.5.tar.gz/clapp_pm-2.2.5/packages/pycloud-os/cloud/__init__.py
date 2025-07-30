"""
PyCloud OS Cloud Applications
Cloud tabanlı temel uygulamalar
"""

__version__ = "0.9.0-dev"

# Core cloud applications
APPLICATIONS = [
    "cloud.files",       # Dosya yöneticisi
    "cloud.settings",    # Sistem ayarları
    "cloud.terminal",    # Terminal
    "cloud.browser",     # Web tarayıcısı
    "cloud.notepad",     # Not defteri
    "cloud.taskmanager", # Görev yöneticisi
    "cloud.pythonconsole", # Python konsolu
    "cloud.login",       # Giriş ekranı
    "cloud.pyide",       # Python IDE
    "cloud.filepicker"   # Dosya seçici
]

# Import modules with fallback
try:
    from . import files
    from . import settings
    from . import terminal
    from . import browser
    from . import notepad
    from . import taskmanager
    from . import pythonconsole
    from . import login
    from . import pyide
    from . import filepicker
except ImportError as e:
    import logging
    logging.getLogger("cloud").warning(f"Failed to import some cloud modules: {e}")

__all__ = [
    "files", "settings", "terminal", "browser", 
    "notepad", "taskmanager", "pythonconsole", "login", "pyide", "filepicker"
]

# Version info
__author__ = "PyCloud OS Team" 