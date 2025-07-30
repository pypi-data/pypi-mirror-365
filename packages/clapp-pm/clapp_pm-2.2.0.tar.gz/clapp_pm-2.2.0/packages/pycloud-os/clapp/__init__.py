"""
Clapp - PyCloud OS Paket Yöneticisi
.app tabanlı uygulamaları yükleyen, kaldıran, güncelleyen ve listeleyen sistem
"""

# Clapp modülleri
from . import core
from . import repo
try:
    from . import ui
except ImportError:
    ui = None  # PyQt6 yoksa UI modülü yok

# Ana fonksiyonlar
__all__ = [
    'core',
    'repo'
]

if ui:
    __all__.append('ui')

# Version info
__version__ = "1.0.0"
__author__ = "PyCloud OS Team" 