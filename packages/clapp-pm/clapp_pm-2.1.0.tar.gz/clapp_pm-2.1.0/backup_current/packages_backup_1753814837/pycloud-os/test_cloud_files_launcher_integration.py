#!/usr/bin/env python3
"""
Cloud Files Launcher Entegrasyon Testi
"""

import sys
import os
import time
import signal
import logging
from pathlib import Path

# PyOS modül yolunu ekle
pyos_root = Path(__file__).parent
sys.path.insert(0, str(pyos_root))

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cloud_files_launcher_integration():
    """Cloud Files Launcher entegrasyonunu test et"""
    
    print("🔥 Cloud Files Launcher Entegrasyon Testi")
    print("=" * 50)
    
    try:
        # 1. Test dosyaları oluştur
        test_dir = Path("pycloud_fs/home/default/Desktop/test_files")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_files = {
            "launcher_test.txt": "Cloud Files artık Launcher API kullanıyor!\n\nBu dosya Cloud Notepad ile açılmalı.",
            "readme.md": "# Launcher Entegrasyonu\n\nCloud Files artık PyOS Launcher ile entegre çalışıyor.",
            "test_script.py": "# PyOS Test Script\nprint('Cloud Files Launcher entegrasyonu başarılı!')",
            "sample.json": '{"message": "Cloud Files Launcher testi", "status": "success"}',
            "config.yml": "app:\n  name: Cloud Files\n  launcher: enabled\n  version: 2.1.0"
        }
        
        print(f"📁 Test dizini oluşturuluyor: {test_dir}")
        
        for filename, content in test_files.items():
            test_file = test_dir / filename
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ {filename} oluşturuldu")
        
        print(f"\n📂 Test dosyaları hazır: {len(test_files)} dosya")
        print(f"📍 Konum: {test_dir}")
        
        # 2. Bridge bağlantısını test et
        print("\n🌉 Bridge bağlantısını test ediliyor...")
        
        try:
            from core.bridge import BridgeIPCClient
            
            bridge_client = BridgeIPCClient()
            if bridge_client.connect():
                print("   ✅ Bridge IPC bağlantısı başarılı")
                
                # Launcher modülünü test et
                launcher_success, launcher_ref = bridge_client.call_module_method(
                    'launcher', 'get_launcher'
                )
                
                if launcher_success:
                    print("   ✅ Launcher modülü erişilebilir")
                    
                    # Mevcut uygulamaları listele
                    apps_success, available_apps = bridge_client.call_module_method(
                        'launcher', 'get_available_apps'
                    )
                    
                    if apps_success and available_apps:
                        print(f"   📱 {len(available_apps)} uygulama mevcut:")
                        for app in available_apps:
                            print(f"      • {app.get('name', 'Unknown')} ({app.get('id', 'no-id')})")
                    else:
                        print("   ⚠️ Mevcut uygulamalar listelenemedi")
                        
                else:
                    print(f"   ❌ Launcher modülü erişilemez: {launcher_ref}")
                    
            else:
                print("   ❌ Bridge IPC bağlantısı başarısız")
                
        except ImportError:
            print("   ⚠️ Bridge modülü yüklenemedi")
        except Exception as e:
            print(f"   ❌ Bridge test hatası: {e}")
        
        # 3. Cloud Files manuel test bilgileri
        print("\n📋 Manuel Test Adımları:")
        print("=" * 30)
        print("1. Cloud Files uygulamasını başlatın:")
        print("   python3 apps/cloud_files/main.py")
        print()
        print("2. Şu klasöre gidin:")
        print(f"   {test_dir}")
        print()
        print("3. Test dosyalarını çift tıklayarak açın:")
        for filename in test_files.keys():
            print(f"   • {filename}")
        print()
        print("4. Launcher entegrasyonunu kontrol edin:")
        print("   • Dosyalar uygun uygulamalarda açılmalı")
        print("   • Hata mesajı görmemelisiniz")
        print("   • Console'da Launcher log'ları görmelisiniz")
        
        # 4. Mevcut PyOS süreçlerini kontrol et
        print("\n🔄 Mevcut PyOS süreçleri:")
        try:
            import subprocess
            ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            pyos_processes = [line for line in ps_result.stdout.split('\n') if 'python' in line and 'pyos' in line.lower()]
            
            if pyos_processes:
                print(f"   🔍 {len(pyos_processes)} PyOS süreci bulundu:")
                for proc in pyos_processes[:5]:  # İlk 5 tanesini göster
                    parts = proc.split()
                    if len(parts) >= 11:
                        pid = parts[1]
                        cmd = ' '.join(parts[10:])
                        print(f"      PID {pid}: {cmd[:60]}...")
            else:
                print("   ⚠️ Aktif PyOS süreci bulunamadı")
                
        except Exception as e:
            print(f"   ❌ Süreç kontrolü hatası: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Test hazırlığı tamamlandı!")
        print("📝 Test dosyalarını Cloud Files ile açmayı deneyin")
        print("🎯 Beklenen sonuç: Launcher API ile dosyalar açılacak")
        
        return True
        
    except Exception as e:
        print(f"❌ Test hazırlığı başarısız: {e}")
        logger.error(f"Test error: {e}")
        return False

def cleanup_test_files():
    """Test dosyalarını temizle"""
    try:
        test_dir = Path("pycloud_fs/home/default/Desktop/test_files")
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
            print(f"🧹 Test dosyaları temizlendi: {test_dir}")
        return True
    except Exception as e:
        print(f"❌ Temizlik hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("Cloud Files Launcher Entegrasyon Test Aracı")
    print("Ctrl+C ile çıkış yapabilirsiniz\n")
    
    def signal_handler(sig, frame):
        print("\n\n🛑 Test sonlandırılıyor...")
        cleanup_test_files()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Test çalıştır
        success = test_cloud_files_launcher_integration()
        
        if success:
            print("\n⏳ Test dosyaları hazır. Manuel testinizi yapın...")
            print("Bitirmek için Ctrl+C tuşlayın.")
            
            # Bekleme döngüsü
            while True:
                time.sleep(1)
        else:
            print("❌ Test başarısız")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Test kullanıcı tarafından sonlandırıldı")
        cleanup_test_files()
        return 0
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        cleanup_test_files()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 