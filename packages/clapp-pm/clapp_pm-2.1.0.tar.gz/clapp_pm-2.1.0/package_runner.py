import os
import json
import subprocess
import mimetypes
from typing import Dict, Callable, Optional, Tuple
from package_registry import get_manifest

class LanguageRunner:
    """Dil çalıştırıcıları için temel sınıf"""
    
    def __init__(self, name: str, command: str, file_extension: str = ""):
        self.name = name
        self.command = command
        self.file_extension = file_extension
    
    def run(self, entry_file: str, app_path: str) -> Tuple[bool, str]:
        """
        Uygulamayı çalıştırır
        
        Args:
            entry_file: Giriş dosyası
            app_path: Uygulama dizini
            
        Returns:
            (success, error_message)
        """
        try:
            result = subprocess.run([self.command, entry_file], 
                                  cwd=app_path, 
                                  capture_output=False)
            return result.returncode == 0, ""
        except FileNotFoundError:
            return False, f"{self.name} yüklü değil veya PATH'te bulunamadı."
        except Exception as e:
            return False, f"Çalıştırma hatası: {str(e)}"
    
    def check_availability(self) -> bool:
        """Dil çalıştırıcısının sistemde mevcut olup olmadığını kontrol eder"""
        try:
            result = subprocess.run([self.command, "--version"], 
                                  capture_output=True, 
                                  text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

class Love2DRunner(LanguageRunner):
    """Love2D oyunları için özel runner"""
    
    def __init__(self):
        super().__init__("Love2D", "love", ".lua")
    
    def run(self, entry_file: str, app_path: str) -> Tuple[bool, str]:
        """
        Love2D oyununu çalıştırır (klasör bazlı)
        
        Args:
            entry_file: Kullanılmaz (Love2D klasör bazlı çalışır)
            app_path: Oyun klasörü
            
        Returns:
            (success, error_message)
        """
        try:
            # Love2D için klasörü çalıştır (entry_file parametresini yok say)
            result = subprocess.run([self.command, app_path], 
                                  capture_output=False)
            return result.returncode == 0, ""
        except FileNotFoundError:
            return False, f"{self.name} yüklü değil veya PATH'te bulunamadı."
        except Exception as e:
            return False, f"Çalıştırma hatası: {str(e)}"

class UniversalRunner(LanguageRunner):
    """Evrensel dil çalıştırıcısı - herhangi bir dili çalıştırabilir"""
    
    def __init__(self):
        super().__init__("Universal", "universal", "")
    
    def run(self, entry_file: str, app_path: str) -> Tuple[bool, str]:
        """
        Dosya türüne göre uygun komutu bulur ve çalıştırır
        
        Args:
            entry_file: Giriş dosyası
            app_path: Uygulama dizini
            
        Returns:
            (success, error_message)
        """
        try:
            entry_path = os.path.join(app_path, entry_file)
            
            # Dosya türünü tespit et
            file_type = self._detect_file_type(entry_path)
            command = self._get_command_for_file_type(file_type, entry_file)
            
            if not command:
                return False, f"Dosya türü için uygun komut bulunamadı: {file_type}"
            
            print(f"🔍 Tespit edilen tür: {file_type}")
            print(f"🚀 Çalıştırılan komut: {command[0]}")
            
            # Komutu çalıştır
            result = subprocess.run(command, 
                                  cwd=app_path, 
                                  capture_output=False)
            
            # Eğer derleme komutuysa (C, C++, Fortran, Pascal), çalıştırılabilir dosyayı çalıştır
            if file_type in ['c', 'cpp', 'fortran', 'pascal'] and result.returncode == 0:
                executable_name = 'output'
                if os.path.exists(os.path.join(app_path, executable_name)):
                    print(f"🚀 Çalıştırılabilir dosya çalıştırılıyor: {executable_name}")
                    exec_result = subprocess.run([f'./{executable_name}'], 
                                               cwd=app_path, 
                                               capture_output=False)
                    return exec_result.returncode == 0, ""
            
            return result.returncode == 0, ""
            
        except Exception as e:
            return False, f"Evrensel çalıştırma hatası: {str(e)}"
    
    def _detect_file_type(self, file_path: str) -> str:
        """Dosya türünü tespit eder"""
        if not os.path.exists(file_path):
            return "unknown"
        
        # Dosya uzantısına göre tespit
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # MIME türü tespiti
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Shebang satırını kontrol et
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    return "script"
        except:
            pass
        
        # Uzantıya göre tespit
        extension_map = {
            '.py': 'python',
            '.lua': 'lua',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.dart': 'dart',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.pl': 'perl',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.r': 'r',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.hs': 'haskell',
            '.ml': 'ocaml',
            '.f90': 'fortran',
            '.pas': 'pascal',
            '.bas': 'basic',
            '.vbs': 'vbscript',
            '.bat': 'batch',
            '.exe': 'executable',
            '.app': 'macos_app',
            '.jar': 'java_jar',
            '.class': 'java_class'
        }
        
        return extension_map.get(ext, 'unknown')
    
    def _get_command_for_file_type(self, file_type: str, entry_file: str) -> Optional[list]:
        """Dosya türüne göre uygun komutu döndürür"""
        
        # Bilinen komutlar
        commands = {
            'python': ['python', entry_file],
            'lua': ['lua', entry_file],
            'javascript': ['node', entry_file],
            'typescript': ['ts-node', entry_file],
            'dart': ['dart', entry_file],
            'go': ['go', 'run', entry_file],
            'rust': ['cargo', 'run'],
            'java': ['java', entry_file],
            'c': ['gcc', entry_file, '-o', 'output'],
            'cpp': ['g++', entry_file, '-o', 'output'],
            'csharp': ['dotnet', 'run'],
            'php': ['php', entry_file],
            'ruby': ['ruby', entry_file],
            'perl': ['perl', entry_file],
            'bash': ['bash', entry_file],
            'powershell': ['powershell', '-File', entry_file],
            'r': ['Rscript', entry_file],
            'swift': ['swift', entry_file],
            'kotlin': ['kotlin', entry_file],
            'scala': ['scala', entry_file],
            'clojure': ['clojure', entry_file],
            'haskell': ['runhaskell', entry_file],
            'ocaml': ['ocaml', entry_file],
            'fortran': ['gfortran', entry_file, '-o', 'output'],
            'pascal': ['fpc', entry_file],
            'basic': ['basic', entry_file],
            'vbscript': ['cscript', entry_file],
            'batch': ['cmd', '/c', entry_file],
            'script': ['bash', entry_file],  # Shebang varsa bash ile çalıştır
            'executable': [f'./{entry_file}'],
            'macos_app': ['open', entry_file],
            'java_jar': ['java', '-jar', entry_file],
            'java_class': ['java', entry_file.replace('.class', '')]
        }
        
        return commands.get(file_type)

class MultiLanguageRunner(LanguageRunner):
    """Çoklu dil uygulamaları için özel runner"""
    
    def __init__(self):
        super().__init__("Multi-Language", "multi", "")
    
    def run(self, entry_file: str, app_path: str) -> Tuple[bool, str]:
        """
        Çoklu dil uygulamasını çalıştırır
        
        Args:
            entry_file: Ana giriş dosyası
            app_path: Uygulama dizini
            
        Returns:
            (success, error_message)
        """
        try:
            # Manifest'i oku
            manifest_path = os.path.join(app_path, "manifest.json")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            if 'languages' not in manifest:
                return False, "Çoklu dil manifest formatı geçersiz"
            
            languages = manifest['languages']
            run_order = manifest.get('run_order', list(languages.keys()))
            
            print(f"🚀 Çoklu dil uygulaması başlatılıyor...")
            print(f"📋 Çalıştırma sırası: {', '.join(run_order)}")
            
            # Her dili sırayla çalıştır
            for lang_name in run_order:
                if lang_name not in languages:
                    print(f"⚠️  {lang_name} dili bulunamadı, atlanıyor")
                    continue
                
                lang_config = languages[lang_name]
                lang_entry = lang_config['entry']
                lang_path = os.path.join(app_path, lang_entry)
                
                print(f"🔄 {lang_name} başlatılıyor: {lang_entry}")
                
                # Dile göre runner bul
                runner = get_runner_for_language(lang_name)
                if not runner:
                    print(f"⚠️  {lang_name} için runner bulunamadı, atlanıyor")
                    continue
                
                # Arka planda çalıştır
                success, error = runner.run(lang_entry, app_path)
                if not success:
                    print(f"❌ {lang_name} başlatılamadı: {error}")
                    return False, f"{lang_name} hatası: {error}"
                
                print(f"✅ {lang_name} başarıyla başlatıldı")
            
            return True, "Çoklu dil uygulaması başarıyla çalıştırıldı"
            
        except Exception as e:
            return False, f"Çoklu dil çalıştırma hatası: {str(e)}"

# Desteklenen diller için runner'lar
LANGUAGE_RUNNERS: Dict[str, LanguageRunner] = {
    'python': LanguageRunner('Python', 'python', '.py'),
    'lua': LanguageRunner('Lua', 'lua', '.lua'),
    'love2d': Love2DRunner(),  # Love2D için özel runner
    'dart': LanguageRunner('Dart', 'dart', '.dart'),
    'go': LanguageRunner('Go', 'go', '.go'),
    'rust': LanguageRunner('Rust', 'cargo', '.rs'),
    'node': LanguageRunner('Node.js', 'node', '.js'),
    'bash': LanguageRunner('Bash', 'bash', '.sh'),
    'perl': LanguageRunner('Perl', 'perl', '.pl'),
    'ruby': LanguageRunner('Ruby', 'ruby', '.rb'),
    'php': LanguageRunner('PHP', 'php', '.php'),
    'multi': MultiLanguageRunner(),  # Çoklu dil desteği
    'universal': UniversalRunner()  # Evrensel dil desteği
}

def get_runner_for_language(language: str) -> Optional[LanguageRunner]:
    """
    Dile göre runner döndürür
    
    Args:
        language: Programlama dili
        
    Returns:
        LanguageRunner veya None
    """
    return LANGUAGE_RUNNERS.get(language.lower())

def add_language_support(name: str, command: str, file_extension: str = "") -> bool:
    """
    Yeni dil desteği ekler
    
    Args:
        name: Dil adı
        command: Çalıştırma komutu
        file_extension: Dosya uzantısı
        
    Returns:
        Başarılı ise True
    """
    try:
        LANGUAGE_RUNNERS[name.lower()] = LanguageRunner(name, command, file_extension)
        return True
    except Exception:
        return False

def run_app(app_name: str) -> bool:
    """
    Belirtilen uygulamayı çalıştırır.
    
    Args:
        app_name (str): Çalıştırılacak uygulamanın adı
        
    Returns:
        bool: Uygulama başarıyla çalıştırıldıysa True, değilse False
    """
    # Manifest bilgilerini al
    manifest = get_manifest(app_name)
    
    if not manifest:
        print(f"Hata: '{app_name}' uygulaması bulunamadı veya geçersiz manifest dosyası.")
        return False
    
    # Uygulama dizini ve giriş dosyası
    from package_registry import get_apps_directory
    apps_dir = get_apps_directory()
    app_path = os.path.join(apps_dir, app_name)
    entry_file = manifest['entry']
    entry_path = os.path.join(app_path, entry_file)
    
    # Dile göre runner al
    language = manifest['language'].lower()
    runner = get_runner_for_language(language)
    
    if not runner:
        # Eğer özel runner bulunamazsa, evrensel runner'ı dene
        print(f"⚠️  '{language}' için özel runner bulunamadı, evrensel runner deneniyor...")
        runner = get_runner_for_language('universal')
        
        if not runner:
            supported = ', '.join([k for k in LANGUAGE_RUNNERS.keys() if k != 'universal'])
            print(f"Hata: Desteklenmeyen dil '{language}'. Desteklenen diller: {supported}")
            return False
    
    # Love2D için özel kontrol
    if language == 'love2d':
        # Love2D için entry dosyası kontrolü gerekmez, klasör yeterli
        if not os.path.exists(app_path):
            print(f"Hata: Uygulama klasörü bulunamadı: {app_path}")
            return False
    elif language == 'universal':
        # Evrensel runner için entry dosyası kontrolü
        if not os.path.exists(entry_path):
            print(f"Hata: Giriş dosyası bulunamadı: {entry_path}")
            return False
    else:
        # Diğer diller için entry dosyası kontrolü
        if not os.path.exists(entry_path):
            print(f"Hata: Giriş dosyası '{entry_file}' bulunamadı.")
            return False
        
    # Uygulamayı çalıştır
    success, error_msg = runner.run(entry_file, app_path)
    
    if not success and error_msg:
        print(f"Hata: {error_msg}")
    
    return success

def get_supported_languages() -> list:
    """
    Desteklenen programlama dillerinin listesini döndürür.
    
    Returns:
        list: Desteklenen diller listesi
    """
    return list(LANGUAGE_RUNNERS.keys())

def check_language_support(language: str) -> bool:
    """
    Belirtilen dilin desteklenip desteklenmediğini kontrol eder.
    
    Args:
        language (str): Kontrol edilecek dil
        
    Returns:
        bool: Dil destekleniyorsa True, değilse False
    """
    return language.lower() in LANGUAGE_RUNNERS

def check_language_availability(language: str) -> bool:
    """
    Belirtilen dilin sistemde mevcut olup olmadığını kontrol eder.
    
    Args:
        language (str): Kontrol edilecek dil
        
    Returns:
        bool: Dil mevcutsa True, değilse False
    """
    runner = get_runner_for_language(language)
    if not runner:
        return False
    return runner.check_availability()

def get_language_status_report() -> str:
    """
    Tüm desteklenen dillerin durum raporunu döndürür.
    
    Returns:
        str: Formatlanmış durum raporu
    """
    report = "🌐 Desteklenen Diller Durumu\n"
    report += "=" * 40 + "\n\n"
    
    for lang_name, runner in LANGUAGE_RUNNERS.items():
        available = runner.check_availability()
        status = "✅ Mevcut" if available else "❌ Mevcut Değil"
        report += f"{lang_name.title():<12} : {status}\n"
    
    return report 