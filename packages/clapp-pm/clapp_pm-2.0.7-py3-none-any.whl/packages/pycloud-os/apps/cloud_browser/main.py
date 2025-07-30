#!/usr/bin/env python3
"""
Cloud Browser v2.0.0 - Modern Web Tarayıcısı
PyCloud OS için geliştirilmiş sekmeli web tarayıcısı
"""

import sys
import os
import logging
from pathlib import Path

# PyQt6 import ve WebEngine için gerekli ayarlar
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QCoreApplication
    from PyQt6.QtGui import QIcon
    
    # WebEngine için gerekli ayar - QApplication oluşturmadan önce
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
except ImportError as e:
    print(f"❌ PyQt6 import hatası: {e}")
    print("💡 Çözüm: pip install PyQt6 PyQt6-WebEngine")
    sys.exit(1)

# Proje kök dizinini sys.path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Local core modülü için path ekle
local_core = Path(__file__).parent
sys.path.insert(0, str(local_core))

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
    return logging.getLogger("CloudBrowser")

def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        return True
    except ImportError:
        return False

def main():
    """Ana fonksiyon"""
    logger = setup_logging()
    logger.info("🌐 Cloud Browser v2.0.0 starting...")
    
    # QApplication instance kontrolü
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setApplicationName("Cloud Browser")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("PyCloud OS")
        
        # High DPI desteği (PyQt6 uyumlu)
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        except AttributeError:
            pass  # PyQt6'da bu ayar varsayılan olarak aktif
        
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            pass  # PyQt6'da bu ayar varsayılan olarak aktif
    
    # WebEngine kontrolü
    webengine_available = check_dependencies()
    if webengine_available:
        logger.info("✅ WebEngine available")
    else:
        logger.info("⚠️ WebEngine not available, using fallback mode")
    
    # Kernel bağlantısı (opsiyonel)
    kernel = None
    try:
        # PyCloud kernel'ı import etmeye çalış
        from core.kernel import PyCloudKernel
        kernel = PyCloudKernel()
        logger.info("✅ PyCloud kernel connected")
    except ImportError:
        logger.info("ℹ️ PyCloud kernel not available, running standalone")
    except Exception as e:
        logger.warning(f"⚠️ Kernel connection failed: {e}")
    
    # Browser oluştur ve göster
    try:
        logger.info("Creating CloudBrowser instance...")
        from core.browser_app import CloudBrowser
        
        browser = CloudBrowser(kernel)
        
        # Icon ayarla (varsa)
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            browser.setWindowIcon(QIcon(str(icon_path)))
        
        logger.info("Showing browser window...")
        browser.show()
        
        logger.info("✅ Cloud Browser v2.0.0 started successfully")
        logger.info("Starting event loop...")
        
        # Event loop başlat
        exit_code = app.exec()
        
        logger.info(f"🔚 Cloud Browser exited with code: {exit_code}")
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