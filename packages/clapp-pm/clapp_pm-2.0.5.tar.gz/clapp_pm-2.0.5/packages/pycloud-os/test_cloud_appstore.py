#!/usr/bin/env python3
"""
App Store Test
Modern uygulama mağazasını test eder
"""

import sys
import os
from pathlib import Path

# PyCloud modüllerini yüklemek için sistem yolunu ekle
sys.path.insert(0, str(Path(__file__).parent))

def test_appstore():
    """AppStore'u test et"""
    try:
        from PyQt6.QtWidgets import QApplication
        from apps.app_store.core.appstore import CloudAppStore
        
        print("🏪 App Store Test Başlatılıyor...")
        
        # QApplication oluştur
        app = QApplication(sys.argv)
        app.setApplicationName("App Store Test")
        
        # Mock kernel (test için)
        class MockKernel:
            def get_module(self, name):
                if name == "config":
                    return MockConfig()
                elif name == "appexplorer":
                    return MockAppExplorer()
                elif name == "appkit":
                    return MockAppKit()
                elif name == "clapp_core":
                    return MockClappCore()
                elif name == "clapp_repo":
                    return MockClappRepo()
                return None
        
        class MockConfig:
            def get(self, key, default=None):
                if key == "theme":
                    return {"dark_mode": False}
                return default
        
        class MockClappCore:
            def _cmd_install(self, args):
                from clapp.core import CommandResult
                return CommandResult.SUCCESS, f"Mock install: {args[0]}"
            
            def _cmd_remove(self, args):
                from clapp.core import CommandResult
                return CommandResult.SUCCESS, f"Mock remove: {args[0]}"
            
            def _cmd_update(self, args):
                from clapp.core import CommandResult
                return CommandResult.SUCCESS, f"Mock update: {args[0]}"
        
        class MockClappRepo:
            def refresh_repositories(self):
                pass
            
            def get_all_packages(self):
                # Mock repository paketleri
                class MockPackage:
                    def __init__(self, data):
                        self.id = data["id"]
                        self.name = data["name"]
                        self.version = data["version"]
                        self.description = data["description"]
                        self.category = data["category"]
                        self.developer = data["developer"]
                        self.tags = data.get("tags", [])
                        self.rating = data.get("rating", 4.0)
                        self.downloads = data.get("downloads", 0)
                
                mock_packages = [
                    {
                        "id": "cloud_calculator",
                        "name": "Cloud Calculator",
                        "version": "1.2.0",
                        "description": "Modern hesap makinesi uygulaması",
                        "category": "Araçlar",
                        "developer": "PyCloud Team",
                        "tags": ["calculator", "math"],
                        "rating": 4.5,
                        "downloads": 1250
                    },
                    {
                        "id": "cloud_music",
                        "name": "Cloud Music Player",
                        "version": "2.1.0",
                        "description": "Güçlü müzik çalar",
                        "category": "Multimedya",
                        "developer": "AudioSoft",
                        "tags": ["music", "player"],
                        "rating": 4.8,
                        "downloads": 3400
                    }
                ]
                
                return [MockPackage(data) for data in mock_packages]
        
        class MockAppExplorer:
            def get_all_apps(self):
                # Mock yüklü uygulamalar
                from apps.app_store.core.appstore import AppInfo
                
                mock_installed = [
                    {
                        "app_id": "cloud_files",
                        "name": "Cloud Files",
                        "version": "1.0.0",
                        "description": "Modern dosya yöneticisi",
                        "category": "Sistem",
                        "developer": "PyCloud Team",
                        "icon_path": "",
                        "app_path": "/apps/cloud_files",
                        "tags": ["files", "manager"],
                        "last_validated": "2024-01-25"
                    },
                    {
                        "app_id": "cloud_terminal",
                        "name": "Cloud Terminal",
                        "version": "1.0.0", 
                        "description": "Gelişmiş terminal uygulaması",
                        "category": "Geliştirme",
                        "developer": "PyCloud Team",
                        "icon_path": "",
                        "app_path": "/apps/cloud_terminal",
                        "tags": ["terminal", "cli"],
                        "last_validated": "2024-01-25"
                    }
                ]
                
                class MockApp:
                    def __init__(self, data):
                        self.app_id = data["app_id"]
                        self.name = data["name"]
                        self.version = data["version"]
                        self.description = data["description"]
                        self.category = data["category"]
                        self.developer = data["developer"]
                        self.icon_path = data["icon_path"]
                        self.app_path = data["app_path"]
                        self.tags = data["tags"]
                        self.last_validated = data["last_validated"]
                
                return [MockApp(data) for data in mock_installed]
            
            class indexer:
                @staticmethod
                def remove_app(app_id):
                    print(f"Mock: Removing app {app_id}")
                    return True
        
        class MockAppKit:
            def install_app(self, app_id):
                print(f"Mock: Installing app {app_id}")
                return True
            
            def remove_app(self, app_id):
                print(f"Mock: Removing app {app_id}")
                return True
        
        # Mock kernel ile AppStore oluştur
        kernel = MockKernel()
        appstore = CloudAppStore(kernel)
        
        print("✅ App Store başarıyla oluşturuldu!")
        print(f"📊 Yüklenen uygulama sayısı: {len(appstore.current_apps)}")
        
        # Kategorileri kontrol et
        counts = appstore.data_manager.get_category_counts()
        print("📂 Kategori sayıları:")
        for category, count in counts.items():
            print(f"   {category}: {count}")
        
        # Pencereyi göster
        appstore.show()
        
        print("🎯 Test tamamlandı! AppStore penceresi açıldı.")
        print("💡 Pencereyi kapatmak için X butonuna tıklayın.")
        
        # Event loop başlat
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("💡 PyQt6 yüklü olduğundan emin olun: pip install PyQt6")
        return 1
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()
        return 1

def test_widgets():
    """Widget'ları ayrı ayrı test et"""
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
        from apps.app_store.core.appstore import AppInfo, ViewMode
        from apps.app_store.core.widgets import ModernAppCard, StarRatingWidget, CategorySidebar, SearchBar
        
        print("🧩 Widget Test Başlatılıyor...")
        
        app = QApplication(sys.argv)
        
        # Test penceresi
        window = QMainWindow()
        window.setWindowTitle("AppStore Widget Test")
        window.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        window.setCentralWidget(central_widget)
        
        # Test app info
        test_app_data = {
            "app_id": "test_app",
            "name": "Test Uygulaması",
            "version": "1.0.0",
            "description": "Bu bir test uygulamasıdır. Widget'ların nasıl göründüğünü test etmek için kullanılır.",
            "category": "Test",
            "developer": "Test Developer",
            "icon_path": "",
            "app_path": "",
            "tags": ["test", "demo", "widget"],
            "rating": 4.5,
            "downloads": 1234
        }
        
        app_info = AppInfo(test_app_data)
        
        # Modern app card test
        print("📱 ModernAppCard test ediliyor...")
        card = ModernAppCard(app_info, ViewMode.GRID, False)
        layout.addWidget(card)
        
        # Star rating test
        print("⭐ StarRatingWidget test ediliyor...")
        rating_widget = StarRatingWidget(4.5, read_only=False)
        layout.addWidget(rating_widget)
        
        # Category sidebar test
        print("📂 CategorySidebar test ediliyor...")
        sidebar = CategorySidebar(False)
        layout.addWidget(sidebar)
        
        # Search bar test
        print("🔍 SearchBar test ediliyor...")
        search_bar = SearchBar(False)
        layout.addWidget(search_bar)
        
        window.show()
        
        print("✅ Tüm widget'lar başarıyla test edildi!")
        print("🎯 Widget test penceresi açıldı.")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Widget test hatası: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Ana test fonksiyonu"""
    print("🏪 App Store Test Suite")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "widgets":
        return test_widgets()
    else:
        return test_appstore()

if __name__ == "__main__":
    sys.exit(main()) 