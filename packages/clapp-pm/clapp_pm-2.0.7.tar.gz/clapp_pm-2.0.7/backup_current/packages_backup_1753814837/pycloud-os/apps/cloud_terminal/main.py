#!/usr/bin/env python3
"""
Cloud Terminal v2.0.0 - Modern PyCloud OS Terminal
Sekmeli arayüz, komut geçmişi, autocomplete ve tema desteği
"""

import sys
import os
import logging
from pathlib import Path

# PyQt6 import
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    PYQT6_AVAILABLE = True
except ImportError:
    print("❌ PyQt6 not found. Please install PyQt6:")
    print("   pip install PyQt6")
    PYQT6_AVAILABLE = False

def setup_logging():
    """Logging kurulumu"""
    log_dir = Path.home() / ".cloud_terminal"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "terminal.log"),
            logging.StreamHandler()
        ]
    )

def main():
    """Ana fonksiyon"""
    # PyQt6 kontrolü
    if not PYQT6_AVAILABLE:
        return 1
    
    # Logging kurulumu
    setup_logging()
    logger = logging.getLogger("CloudTerminal")
    
    logger.info("🌩️ Cloud Terminal v2.0.0 starting...")
    
    try:
        # QApplication oluştur - mevcut instance kontrolü
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app_created = True
        else:
            app_created = False
            logger.info("Using existing QApplication instance")
        
        app.setApplicationName("Cloud Terminal")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("PyCloud OS")
        
        # Uygulama ikonu
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # High DPI desteği
        if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Core modülleri import
        try:
            from core import CloudTerminal
        except ImportError as e:
            logger.error(f"❌ Core modules not found: {e}")
            print(f"❌ Core modules not found: {e}")
            print("Make sure all core modules are in the core/ directory")
            return 1
        
        # Kernel bağlantısı (opsiyonel)
        kernel = None
        try:
            # PyCloud kernel'ı bulmaya çalış
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from core.kernel import PyCloudKernel
            kernel = PyCloudKernel.get_instance()
            logger.info("✅ Connected to PyCloud kernel")
        except ImportError:
            logger.info("ℹ️ PyCloud kernel not available, running standalone")
        except Exception as e:
            logger.warning(f"⚠️ Kernel connection failed: {e}")
        
        # Cloud Terminal oluştur
        logger.info("Creating CloudTerminal instance...")
        terminal = CloudTerminal(kernel=kernel)
        
        # Pencereyi göster
        logger.info("Showing terminal window...")
        terminal.show()
        terminal.raise_()  # Pencereyi öne getir
        terminal.activateWindow()  # Pencereyi aktif yap
        
        # Başlangıç mesajı
        logger.info("✅ Cloud Terminal v2.0.0 started successfully")
        
        # Event loop başlat (sadece yeni app oluşturduysak)
        if app_created:
            logger.info("Starting event loop...")
            exit_code = app.exec()
            logger.info(f"🔚 Cloud Terminal exited with code: {exit_code}")
            return exit_code
        else:
            logger.info("Terminal window created in existing application")
            return 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        print(f"❌ Fatal error: {e}")
        return 1
    
    finally:
        # Temizlik
        logger.info("🧹 Cleaning up...")

if __name__ == "__main__":
    sys.exit(main()) 