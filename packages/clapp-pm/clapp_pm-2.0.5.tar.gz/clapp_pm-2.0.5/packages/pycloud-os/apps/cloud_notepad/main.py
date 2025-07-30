#!/usr/bin/env python3
"""
Cloud Notepad v2.0.0 - Modern Metin Düzenleyici
PyCloud OS için geliştirilmiş sekmeli metin düzenleyici
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# PyQt6 import ve gerekli ayarlar
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QCoreApplication
    from PyQt6.QtGui import QIcon
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyQt6 import hatası: {e}")
    print("💡 Çözüm: pip install PyQt6")
    PYQT_AVAILABLE = False

# PyCloud OS core modüllerini ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Logging sistemini kur"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("CloudNotepad")

def main():
    """Ana fonksiyon"""
    logger = setup_logging()
    logger.info("📝 Cloud Notepad v2.0.0 starting...")
    
    if not PYQT_AVAILABLE:
        logger.error("❌ PyQt6 not available")
        return 1
    
    # Komut satırı parametrelerini parse et
    parser = argparse.ArgumentParser(description='PyCloud OS Cloud Notepad v2.0.0')
    parser.add_argument('--open-file', type=str, help='Açılacak dosya yolu')
    parser.add_argument('--open-path', type=str, help='Açılacak dizin yolu (dosya için)')
    args, unknown = parser.parse_known_args()
    
    # QApplication oluştur veya var olanı kullan
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setApplicationName("Cloud Notepad")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("PyCloud OS")
        
        # High DPI desteği
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            pass  # PyQt6'da varsayılan olarak aktif
    
    # Kernel referansı - Bridge sistemi üzerinden al
    kernel = None
    try:
        # Bridge sistemi üzerinden kernel'e erişim
        from core.bridge import get_bridge_manager
        bridge_manager = get_bridge_manager()
        if bridge_manager:
            kernel = bridge_manager.get_kernel_reference()
            print("✅ Kernel referansı bridge üzerinden alındı")
            
            # Bridge bağlantısını test et
            if hasattr(bridge_manager, 'call_module_method'):
                # IPC client kullanılıyor
                print("🔗 Bridge IPC client kullanılıyor")
            else:
                # Direkt bridge manager kullanılıyor
                print("🔗 Bridge manager direkt kullanılıyor")
                
        else:
            print("⚠️ Bridge manager bulunamadı, standalone modda çalışılıyor")
    except Exception as e:
        print(f"⚠️ Bridge bağlantısı kurulamadı: {e}")
        print("Standalone modda çalışılıyor...")
    
    try:
        # Notepad'ı oluştur
        logger.info("Creating Cloud Notepad instance...")
        from cloud.notepad import create_notepad_app
        
        notepad = create_notepad_app(kernel)
        
        # Icon ayarla (varsa)
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            notepad.setWindowIcon(QIcon(str(icon_path)))
        
        # Dosya açma parametresi varsa dosyayı aç
        if args.open_file:
            # PyCloud OS sanal dosya sistemi yollarını destekle
            file_path_str = args.open_file
            
            # Gerçek dosya sistemi yolu mu kontrol et
            file_path = Path(file_path_str)
            file_exists = file_path.exists()
            
            # PyCloud OS sanal dosya sistemi yolu da olabilir
            if not file_exists and not file_path_str.startswith('/'):
                # Sanal dosya sistemi yolu olarak kabul et
                logger.info(f"PyCloud OS sanal dosya sistemi yolu olarak açılıyor: {file_path_str}")
                notepad.open_specific_file(file_path_str)
                logger.info(f"Opened file: {args.open_file}")
            elif file_exists:
                # Gerçek dosya sistemi yolu
                logger.info(f"Gerçek dosya sistemi yolu olarak açılıyor: {file_path_str}")
                notepad.open_specific_file(str(file_path))
                logger.info(f"Opened file: {args.open_file}")
            else:
                logger.warning(f"File not found: {args.open_file}")
        
        logger.info("Showing notepad window...")
        notepad.show()
        
        logger.info("✅ Cloud Notepad v2.0.0 started successfully")
        logger.info("Starting event loop...")
        
        # Event loop başlat
        exit_code = app.exec()
        
        logger.info(f"🔚 Cloud Notepad exited with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        logger.info("🧹 Cleaning up...")

if __name__ == "__main__":
    sys.exit(main()) 