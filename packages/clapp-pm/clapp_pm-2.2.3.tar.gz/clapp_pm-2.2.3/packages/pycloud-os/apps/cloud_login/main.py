#!/usr/bin/env python3
"""
Cloud Login App Launcher
PyCloud OS Login Uygulaması Başlatıcısı
"""

import sys
import os
from pathlib import Path

# PyCloud OS core modüllerini ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from cloud.login import create_login_screen
    
    def main():
        """Login uygulamasını başlat"""
        # Kernel referansı (gelecekte AppKit'ten alınacak)
        kernel = None
        
        # Login ekranını oluştur
        login = create_login_screen(kernel)
        
        # PyQt6 GUI varsa göster
        if hasattr(login, 'show'):
            login.show()
            
            # Event loop başlat
            if hasattr(login, 'exec'):
                return login.exec()
            else:
                # Text mode
                return 0 if login.show() else 1
        
        return 0

    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"Cloud Login başlatılamadı: {e}")
    print("Lütfen PyCloud OS bağımlılıklarının yüklü olduğundan emin olun.")
    sys.exit(1) 