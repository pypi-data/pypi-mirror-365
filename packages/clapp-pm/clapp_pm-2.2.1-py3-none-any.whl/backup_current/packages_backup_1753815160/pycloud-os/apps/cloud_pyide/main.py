#!/usr/bin/env python3
"""
Cloud PyIDE App Launcher
PyCloud OS Python IDE Uygulaması Başlatıcısı
"""

import sys
import os
from pathlib import Path

# PyCloud OS core modüllerini ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from PyQt6.QtWidgets import QApplication
    from cloud.pyide import create_pyide_app
    
    def main():
        """PyIDE uygulamasını başlat"""
        # QApplication oluştur veya var olanı kullan
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Kernel referansı (gelecekte AppKit'ten alınacak)
        kernel = None
        
        # PyIDE'yi oluştur
        pyide = create_pyide_app(kernel)
        
        # Event loop'u başlat
        return app.exec()

    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"Cloud PyIDE başlatılamadı: {e}")
    print("Lütfen PyCloud OS bağımlılıklarının yüklü olduğundan emin olun.")
    sys.exit(1) 