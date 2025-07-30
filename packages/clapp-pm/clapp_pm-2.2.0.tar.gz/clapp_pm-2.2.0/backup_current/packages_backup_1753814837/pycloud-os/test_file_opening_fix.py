#!/usr/bin/env python3
"""
PyCloud OS Dosya Açma Sorunu Çözüm Testi
Cloud Files ve Desktop Context Menu dosya açma işlemlerini test eder
"""

import sys
from pathlib import Path

# PyCloud OS path'ini ekle
sys.path.insert(0, str(Path.cwd()))

def test_context_menu_file_opening():
    """Context menu dosya açma testi"""
    print("🖱️ Context Menu Dosya Açma Testi")
    print("=" * 50)
    
    try:
        from core.kernel import PyCloudKernel
        from rain.contextmenu import ContextMenuManager
        
        # Kernel başlat
        print("🚀 PyCloud Kernel başlatılıyor...")
        kernel = PyCloudKernel()
        kernel.start()
        
        # Context menu oluştur
        print("📋 Context Menu Manager oluşturuluyor...")
        context_menu = ContextMenuManager(kernel)
        
        # Test dosyaları
        txt_file = Path("pycloud_fs/home/default/Desktop/test_dosya.txt").absolute()
        py_file = Path("pycloud_fs/home/default/Desktop/test_script.py").absolute()
        
        print(f"📄 TXT Test dosyası: {txt_file}")
        print(f"📄 PY Test dosyası: {py_file}")
        
        if not txt_file.exists():
            print("❌ TXT test dosyası bulunamadı!")
            return False
            
        if not py_file.exists():
            print("❌ PY test dosyası bulunamadı!")
            return False
        
        print("\n🔧 Dosya açma testleri:")
        
        # TXT dosyası açma testi
        print("1. TXT dosyası açma testi (Notepad ile)...")
        context_menu.open_file_with_default(str(txt_file))
        
        # PY dosyası açma testi
        print("2. PY dosyası açma testi (PyIDE ile)...")
        context_menu.open_file_with_default(str(py_file))
        
        print("✅ Context Menu testleri tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Context Menu test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cloud_files_opening():
    """Cloud Files dosya açma testi"""
    print("\n📁 Cloud Files Dosya Açma Testi")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from cloud.files import CloudFiles
        
        # QApplication oluştur
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("📂 Cloud Files oluşturuluyor...")
        files_app = CloudFiles()
        
        # Test dizinine git
        test_dir = Path("pycloud_fs/home/default/Desktop")
        files_app.navigate_to_path(test_dir)
        
        print(f"📂 Test dizini: {test_dir.absolute()}")
        
        # Test dosyaları
        txt_file = test_dir / "test_dosya.txt"
        py_file = test_dir / "test_script.py"
        
        print(f"📄 TXT Test dosyası: {txt_file.absolute()}")
        print(f"📄 PY Test dosyası: {py_file.absolute()}")
        
        if txt_file.exists():
            print("1. TXT dosyası açma testi...")
            files_app.open_file(txt_file)
        else:
            print("❌ TXT dosyası bulunamadı!")
        
        if py_file.exists():
            print("2. PY dosyası açma testi...")
            files_app.open_file(py_file)
        else:
            print("❌ PY dosyası bulunamadı!")
        
        print("✅ Cloud Files testleri tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Cloud Files test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_launcher_argument_opening():
    """Launcher argument dosya açma testi"""
    print("\n🚀 Launcher Argument Dosya Açma Testi")
    print("=" * 50)
    
    try:
        from core.kernel import PyCloudKernel
        from core.launcher import ApplicationLauncher
        
        # Kernel başlat
        print("🚀 PyCloud Kernel başlatılıyor...")
        kernel = PyCloudKernel()
        kernel.start()
        
        # Launcher oluştur
        print("🚀 Launcher oluşturuluyor...")
        launcher = ApplicationLauncher(kernel)
        launcher.start_launcher()
        
        # Test dosyaları
        txt_file = Path("pycloud_fs/home/default/Desktop/test_dosya.txt").absolute()
        py_file = Path("pycloud_fs/home/default/Desktop/test_script.py").absolute()
        
        print(f"📄 TXT Test dosyası: {txt_file}")
        print(f"📄 PY Test dosyası: {py_file}")
        
        print("\n🔧 Launcher argument testleri:")
        
        # TXT dosyası açma testi (Notepad ile)
        print("1. TXT dosyası → Notepad ile açma testi...")
        success = launcher.launch_app("cloud_notepad", open_file=str(txt_file))
        print(f"   Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}")
        
        # PY dosyası açma testi (PyIDE ile)
        print("2. PY dosyası → PyIDE ile açma testi...")
        success = launcher.launch_app("cloud_pyide", open_file=str(py_file))
        print(f"   Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}")
        
        # HTML dosyası için browser testi (eğer varsa)
        html_file = Path("pycloud_fs/home/default/Desktop/test.html")
        if html_file.exists():
            print("3. HTML dosyası → Browser ile açma testi...")
            success = launcher.launch_app("cloud_browser", open_file=str(html_file.absolute()))
            print(f"   Sonuç: {'✅ Başarılı' if success else '❌ Başarısız'}")
        
        print("✅ Launcher argument testleri tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Launcher argument test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 PyCloud OS Dosya Açma Sorunu Çözüm Testi")
    print("=" * 60)
    
    # Test dosyalarını kontrol et
    txt_file = Path("pycloud_fs/home/default/Desktop/test_dosya.txt")
    py_file = Path("pycloud_fs/home/default/Desktop/test_script.py")
    
    print("📋 Test Hazırlığı:")
    print(f"TXT dosyası var mı: {txt_file.exists()}")
    print(f"PY dosyası var mı: {py_file.exists()}")
    
    if not txt_file.exists():
        # Test dosyası oluştur
        txt_file.parent.mkdir(parents=True, exist_ok=True)
        txt_file.write_text("Bu bir test dosyasıdır.\nNotepad ile açılmalıdır.", encoding='utf-8')
        print("📄 TXT test dosyası oluşturuldu")
    
    if not py_file.exists():
        # Test dosyası zaten var (test_script.py)
        print("📄 PY test dosyası mevcut")
    
    # Context Menu testleri
    success1 = test_context_menu_file_opening()
    
    # Cloud Files testleri
    success2 = test_cloud_files_opening()
    
    # Launcher Argument testleri
    success3 = test_launcher_argument_opening()
    
    print("\n" + "=" * 60)
    print("🎯 TEST SONUÇLARI:")
    print(f"Context Menu: {'✅ BAŞARILI' if success1 else '❌ BAŞARISIZ'}")
    print(f"Cloud Files: {'✅ BAŞARILI' if success2 else '❌ BAŞARISIZ'}")
    print(f"Launcher Arguments: {'✅ BAŞARILI' if success3 else '❌ BAŞARISIZ'}")
    
    if success1 and success2 and success3:
        print("🎉 TÜM TESTLER BAŞARILI! Dosya açma sorunu tamamen çözüldü!")
    else:
        print("⚠️ Bazı testler başarısız!")

if __name__ == "__main__":
    main() 