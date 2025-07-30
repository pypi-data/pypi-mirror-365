"""
PyCloud OS Kernel
Sistem çekirdeği - zaman yönetimi, sistem olayları ve yaşam döngüsü kontrolü
"""

import sys
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Any
import os

class PyCloudKernel:
    """PyCloud OS ana çekirdek sınıfı"""
    
    def __init__(self, debug_mode: bool = False, safe_mode: bool = False):
        self.debug_mode = debug_mode
        self.safe_mode = safe_mode
        self.logger = logging.getLogger("Kernel")
        self.start_time = None
        self.shutdown_hooks: List[Callable] = []
        self.modules: Dict[str, Any] = {}
        self.running = False
        self.scheduler_thread = None
        self.scheduled_tasks: List[Dict] = []
        self.log_entries: List[Dict] = []  # Log kayıtları için
        
        # Debug modunda daha detaylı loglama
        if self.debug_mode:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("🐛 Debug modu aktif")
        
        # Güvenli modda sadece temel modüller yüklenir
        if self.safe_mode:
            self.logger.info("🛡️ Güvenli mod aktif")
        
        # Sistem dizinlerini oluştur
        self._create_system_directories()
        
        # Kernel journal'ı başlat
        self.journal = []
        self._log_event("KERNEL_INIT", f"PyCloud OS Kernel initialized (debug={debug_mode}, safe={safe_mode})")
    
    def _create_system_directories(self):
        """Sistem dizinlerini oluştur"""
        directories = [
            "system/config",
            "system/themes", 
            "system/icons",
            "system/wallpapers",
            "apps",
            "users",
            "temp",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _log_event(self, event_type: str, message: str, data: Dict = None):
        """Kernel journal'a olay kaydet"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "data": data or {}
        }
        self.journal.append(event)
        self.logger.info(f"[{event_type}] {message}")
    
    def start(self) -> bool:
        """Kernel'i başlat - main.py'den çağrılır"""
        try:
            self.boot()
            return True
        except Exception as e:
            self.logger.error(f"Kernel başlatma hatası: {e}")
            return False
    
    def register_module(self, name: str, module: Any):
        """Sistem modülü kaydet"""
        self.modules[name] = module
        self._log_event("MODULE_REGISTER", f"Module {name} registered")
    
    def get_module(self, name: str):
        """Sistem modülü al"""
        return self.modules.get(name)
    
    def add_shutdown_hook(self, hook: Callable):
        """Kapatma öncesi çalışacak fonksiyon ekle"""
        self.shutdown_hooks.append(hook)
    
    def schedule_task(self, func: Callable, delay: float, repeat: bool = False):
        """Zamanlanmış görev ekle"""
        task = {
            "func": func,
            "next_run": time.time() + delay,
            "delay": delay,
            "repeat": repeat
        }
        self.scheduled_tasks.append(task)
    
    def _scheduler_loop(self):
        """Zamanlayıcı döngüsü"""
        while self.running:
            current_time = time.time()
            
            # Çalışması gereken görevleri bul
            tasks_to_run = []
            for task in self.scheduled_tasks[:]:
                if current_time >= task["next_run"]:
                    tasks_to_run.append(task)
                    
                    if task["repeat"]:
                        task["next_run"] = current_time + task["delay"]
                    else:
                        self.scheduled_tasks.remove(task)
            
            # Görevleri çalıştır
            for task in tasks_to_run:
                try:
                    task["func"]()
                except Exception as e:
                    self.logger.error(f"Scheduled task error: {e}")
            
            time.sleep(0.1)  # 100ms bekle
    
    def boot(self):
        """Sistem başlatma"""
        self.start_time = datetime.now()
        self._log_event("SYSTEM_BOOT", "PyCloud OS booting...")
        
        try:
            # Core modülleri yükle
            self._load_core_modules()
            
            # Kullanıcı sistemi başlat
            self._init_user_system()
            
            # Dosya sistemi başlat
            self._init_filesystem()
            
            # Arayüz sistemi başlat
            self._init_ui_system()
            
            self.running = True
            
            # Zamanlayıcı thread'ini başlat
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            self._log_event("SYSTEM_READY", "PyCloud OS boot completed")
            
        except Exception as e:
            self._log_event("BOOT_ERROR", f"Boot failed: {e}")
            raise
    
    def _load_core_modules(self):
        """Core modülleri yükle"""
        try:
            # Config modülü
            from core.config import init_config
            self.config = init_config(self)
            self.modules['config'] = self.config
            self.log("Config modülü yüklendi", "INFO")
            
            # Users modülü
            from core.users import init_users
            self.users = init_users(self)
            self.modules['users'] = self.users
            self.log("Users modülü yüklendi", "INFO")
            
            # FS modülü
            from core.fs import init_fs
            self.fs = init_fs(self)
            self.modules['fs'] = self.fs
            self.log("FS modülü yüklendi", "INFO")
            
            # VFS modülünü FS'den al ve ayrı olarak register et
            try:
                if hasattr(self.fs, 'vfs') and self.fs.vfs:
                    self.modules['vfs'] = self.fs.vfs
                    self.log("VFS modülü FS'den alındı", "INFO")
                else:
                    self.log("VFS modülü FS'de bulunamadı", "WARNING")
                    # VFS'i manuel olarak yüklemeye çalış
                    from core.fs.vfs import PyCloudVFS
                    vfs_instance = PyCloudVFS(self)
                    self.modules['vfs'] = vfs_instance
                    # FS'e de referans ver
                    if hasattr(self.fs, 'vfs'):
                        self.fs.vfs = vfs_instance
                    self.log("VFS modülü manuel olarak yüklendi", "INFO")
            except Exception as vfs_error:
                self.log(f"VFS modülü yükleme hatası: {vfs_error}", "ERROR")
            
            # Process modülü
            from core.process import init_process
            self.process = init_process(self)
            self.modules['process'] = self.process
            self.log("Process modülü yüklendi", "INFO")
            
            # Thread modülü
            from core.thread import init_thread_manager
            self.thread = init_thread_manager(self)
            self.modules['thread'] = self.thread
            self.log("Thread modülü yüklendi", "INFO")
            
            # Memory modülü
            from core.memory import init_memory
            self.memory = init_memory(self)
            self.modules['memory'] = self.memory
            self.log("Memory modülü yüklendi", "INFO")
            
            # Security modülü
            from core.security import init_security
            self.security = init_security(self)
            self.modules['security'] = self.security
            self.log("Security modülü yüklendi", "INFO")
            
            # Security modülünde uygulama güvenlik profillerini kur
            if hasattr(self.security, 'setup_app_security_profiles'):
                self.security.setup_app_security_profiles()
                self.log("Uygulama güvenlik profilleri kuruldu", "INFO")
            
            # Services modülü
            from core.services import init_services
            self.services = init_services(self)
            self.modules['services'] = self.services
            self.log("Services modülü yüklendi", "INFO")
            
            # Events modülü
            from core.events import init_events
            self.events = init_events(self)
            self.modules['events'] = self.events
            self.log("Events modülü yüklendi", "INFO")
            
            # Locale modülü
            from core.locale import init_locale_manager
            self.locale = init_locale_manager(self)
            self.modules['locale'] = self.locale
            self.log("Locale modülü yüklendi", "INFO")
            
            # Notify modülü
            from core.notify import init_notifications
            self.notify = init_notifications(self)
            self.modules['notify'] = self.notify
            self.log("Notify modülü yüklendi", "INFO")
            
            # Bridge modülü (AppKit için gerekli)
            try:
                from core.bridge import init_bridge_manager
                self.bridge = init_bridge_manager(self)
                self.modules['bridge'] = self.bridge
                self.log("Bridge modülü yüklendi", "INFO")
            except Exception as e:
                self.log(f"Bridge modülü yüklenemedi: {e}", "WARNING")
                self.bridge = None
            
            # AppKit modülü
            from core.appkit import init_appkit
            self.appkit = init_appkit(self)
            self.modules['appkit'] = self.appkit
            self.log("AppKit modülü yüklendi", "INFO")
            
            # AppExplorer modülü
            from core.appexplorer import init_app_explorer
            self.appexplorer = init_app_explorer(self)
            self.modules['appexplorer'] = self.appexplorer
            self.log("AppExplorer modülü yüklendi", "INFO")
            
            # Python Environment Manager
            try:
                from core.pythonenv import init_python_env_manager
                # Geçici olarak devre dışı - hızlı test için
                # self.pythonenv = init_python_env_manager(self)
                self.log("PythonEnv modülü geçici olarak devre dışı", "WARNING")
            except Exception as e:
                self.log(f"PythonEnv modülü yüklenemedi: {e}", "ERROR")
            
            # AppMon modülü
            try:
                from core.appmon import init_appmon
                self.appmon = init_appmon(self)
                self.modules['appmon'] = self.appmon
                self.log("AppMon modülü yüklendi", "INFO")
            except Exception as e:
                self.log(f"AppMon modülü yüklenemedi: {e}", "WARNING")
                self.appmon = None
            
            # Launcher modülü
            try:
                from core.launcher import init_launcher
                self.launcher = init_launcher(self)
                self.modules['launcher'] = self.launcher
                self.log("Launcher modülü yüklendi", "INFO")
                
                # AppMon ile Launcher entegrasyonu
                if self.appmon and self.launcher:
                    self.launcher.set_appmon(self.appmon)
                    self.log("Launcher-AppMon entegrasyonu tamamlandı", "INFO")
                    
            except Exception as e:
                self.log(f"Launcher modülü yüklenemedi: {e}", "WARNING")
                self.launcher = None
            
            # Context Menu modülü
            try:
                from rain.contextmenu import init_context_menu_manager
                self.contextmenu = init_context_menu_manager(self)
                self.modules['contextmenu'] = self.contextmenu
                self.log("Context Menu modülü yüklendi", "INFO")
            except Exception as e:
                self.log(f"Context Menu modülü yüklenemedi: {e}", "WARNING")
                self.contextmenu = None
            
        except Exception as e:
            self.log(f"Core modül yükleme hatası: {e}", "ERROR")
            raise
    
    def _init_user_system(self):
        """Kullanıcı sistemi başlat"""
        self.logger.info("Initializing user system...")
        
        try:
            from core.users import UserManager
            user_manager = UserManager()
            self.register_module("users", user_manager)
            
            # Varsayılan kullanıcı oluştur
            user_manager.create_default_user()
            
        except ImportError:
            self.logger.warning("User system not available")
    
    def _init_filesystem(self):
        """Dosya sistemi başlat"""
        self.logger.info("Initializing filesystem...")
        
        try:
            from core.fs import FileSystem
            fs = FileSystem()
            self.register_module("fs", fs)
            fs.initialize()
            
        except ImportError:
            self.logger.warning("Filesystem not available")
    
    def _init_ui_system(self):
        """Arayüz sistemi başlat"""
        self.logger.info("Initializing UI system...")
        
        try:
            from rain.ui import RainUI
            ui = RainUI(self)
            self.register_module("ui", ui)
            
            # UI başlatıldıktan sonra wallpaper manager'ı yükle
            try:
                from rain.wallpaper import init_wallpaper_manager
                self.wallpaper = init_wallpaper_manager(self)
                self.modules['wallpaper'] = self.wallpaper
                self.log("Wallpaper modülü yüklendi", "INFO")
            except Exception as e:
                self.log(f"Wallpaper modülü yüklenemedi: {e}", "WARNING")
                self.wallpaper = None
            
        except ImportError:
            self.logger.warning("UI system not available")
    
    def run(self):
        """Ana sistem döngüsü"""
        if not self.running:
            raise RuntimeError("System not booted")
        
        self._log_event("SYSTEM_RUNNING", "PyCloud OS main loop started")
        
        try:
            # UI varsa GUI modunda çalış
            ui = self.get_module("ui")
            if ui:
                return ui.run()
            else:
                # CLI modunda çalış
                self._cli_mode()
                return 0
                
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
            self.shutdown()
            return 0
        except Exception as e:
            self.logger.error(f"System error: {e}")
            self.shutdown()
            return 1
    
    def _cli_mode(self):
        """CLI modunda çalış"""
        print("PyCloud OS CLI Mode")
        print("Type 'help' for commands, 'exit' to quit")
        
        while self.running:
            try:
                command = input("pycloud> ").strip()
                
                if command == "exit":
                    break
                elif command == "help":
                    print(self._get_help_text())
                elif command == "status":
                    uptime = datetime.now() - self.start_time
                    print(f"System uptime: {uptime}")
                    print(f"Loaded modules: {len(self.modules)}")
                elif command == "modules":
                    for name in self.modules:
                        print(f"  - {name}")
                elif command == "users":
                    user_manager = self.get_module("users")
                    if user_manager:
                        users = user_manager.list_users()
                        print(f"Users ({len(users)}):")
                        for user in users:
                            status = "active" if user.is_active else "inactive"
                            print(f"  - {user.username} ({user.display_name}) [{status}]")
                    else:
                        print("User manager not available")
                elif command == "apps":
                    app_explorer = self.get_module("appexplorer")
                    if app_explorer:
                        apps = app_explorer.get_installed_apps()
                        print(f"Installed apps ({len(apps)}):")
                        for app in apps:
                            print(f"  - {app['id']}: {app['name']} v{app['version']}")
                    else:
                        print("App explorer not available")
                elif command == "clapp":
                    try:
                        from clapp.core import get_clapp_manager
                        clapp_manager = get_clapp_manager()
                        if clapp_manager:
                            print("Clapp package manager available")
                            print("Use: clapp list, clapp install <package>, clapp remove <package>")
                        else:
                            print("Clapp manager not available")
                    except ImportError:
                        print("Clapp system not available")
                elif command == "python":
                    python_env = self.get_module("pythonenv")
                    if python_env:
                        info = python_env.get_system_info()
                        python_info = info.get('python_info', {})
                        print(f"Python version: {python_info.get('version', 'Unknown')}")
                        print(f"Python executable: {python_info.get('executable', 'Unknown')}")
                        print(f"Pip available: {python_info.get('pip_available', False)}")
                        print(f"Package count: {info.get('package_count', 0)}")
                    else:
                        print("Python environment manager not available")
                elif command == "packages":
                    python_env = self.get_module("pythonenv")
                    if python_env:
                        packages = python_env.get_package_list()
                        print(f"Python packages ({len(packages)}):")
                        for pkg in packages[:10]:  # İlk 10 paket
                            print(f"  - {pkg['name']} v{pkg['version']}")
                        if len(packages) > 10:
                            print(f"  ... and {len(packages) - 10} more")
                    else:
                        print("Python environment manager not available")
                elif command == "widgets":
                    widget_manager = self.get_module("widgets")
                    if widget_manager:
                        widgets = widget_manager.list_widgets()
                        print(f"Active widgets ({len(widgets)}):")
                        for widget in widgets:
                            print(f"  - {widget['widget_id']}: {widget['title']} ({widget['widget_type']})")
                    else:
                        print("Widget manager not available")
                elif command == "themes":
                    theme_manager = self.get_module("theme")
                    if theme_manager:
                        themes = theme_manager.get_available_themes()
                        print(f"Available themes ({len(themes)}):")
                        for theme in themes:
                            current = " (current)" if theme['is_current'] else ""
                            print(f"  - {theme['name']}: {theme['display_name']}{current}")
                    else:
                        print("Theme manager not available")
                elif command == "contextmenu":
                    context_menu = self.get_module("contextmenu")
                    if context_menu:
                        print("Context menu manager available")
                        print("Context menu system provides right-click menus for desktop, files, and apps")
                    else:
                        print("Context menu manager not available")
                elif command == "wallpaper":
                    wallpaper_manager = self.get_module("wallpaper")
                    if wallpaper_manager:
                        wallpapers = wallpaper_manager.get_available_wallpapers()
                        print(f"Available wallpapers ({len(wallpapers)}):")
                        for wp in wallpapers[:5]:  # İlk 5 duvar kağıdı
                            print(f"  - {wp['name']} ({wp['type']}) - {wp['size'][0]}x{wp['size'][1]}")
                        if len(wallpapers) > 5:
                            print(f"  ... and {len(wallpapers) - 5} more")
                    else:
                        print("Wallpaper manager not available")
                elif command == "vfs":
                    vfs = self.get_module("vfs")
                    if vfs:
                        stats = vfs.get_security_stats()
                        print(f"VFS Status:")
                        print(f"  - Active: {stats.get('active', False)}")
                        print(f"  - Mount points: {len(stats.get('mount_points', []))}")
                        print(f"  - Registered apps: {len(stats.get('app_profiles', {}))}")
                        print(f"  - Security checks: {stats.get('security_checks', 0)}")
                        print(f"  - Access denials: {stats.get('access_denials', 0)}")
                    else:
                        print("VFS not available")
                elif command == "filepicker":
                    try:
                        from cloud.filepicker import FilePickerWindow
                        print("FilePicker module available")
                        print("Features: VFS integration, security filters, app-specific permissions")
                    except ImportError:
                        print("FilePicker module not available")
                elif command:
                    print(f"Unknown command: {command}")
                    print("Available commands: status, modules, fs, memory, threads, processes, users, apps, services, events, config, logs, shutdown, restart, uptime, clapp, python, packages, widgets, themes, contextmenu, wallpaper, vfs, filepicker")
                    
            except EOFError:
                break
    
    def shutdown(self):
        """Sistemi kapat"""
        if not self.running:
            return
        
        self._log_event("SYSTEM_SHUTDOWN", "PyCloud OS shutting down...")
        self.running = False
        
        # Bridge IPC server'ı kapat
        try:
            from core.bridge import _ipc_server
            if _ipc_server:
                _ipc_server.stop()
        except Exception as e:
            self.logger.warning(f"Bridge IPC server shutdown error: {e}")
        
        # Shutdown hook'larını çalıştır
        for hook in self.shutdown_hooks:
            try:
                hook()
            except Exception as e:
                self.logger.error(f"Shutdown hook error: {e}")
        
        # Modülleri kapat
        for name, module in self.modules.items():
            try:
                if hasattr(module, 'shutdown'):
                    module.shutdown()
                    self.logger.info(f"Module {name} shutdown completed")
            except Exception as e:
                self.logger.error(f"Module {name} shutdown error: {e}")
        
        self._log_event("SYSTEM_SHUTDOWN_COMPLETE", "PyCloud OS shutdown completed")
    
    def restart(self):
        """Sistem yeniden başlatma"""
        self._log_event("SYSTEM_RESTART", "PyCloud OS restarting...")
        self.shutdown()
        # Ana process'i yeniden başlatmak için exit code 2 döndür
        sys.exit(2)
    
    def get_uptime(self) -> float:
        """Sistem çalışma süresini saniye olarak döndür"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0
    
    def get_system_info(self) -> Dict:
        """Sistem bilgilerini döndür"""
        return {
            "version": "0.9.0-dev",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime": self.get_uptime(),
            "modules": list(self.modules.keys()),
            "running": self.running
        }
    
    def _handle_cli_command(self, command: str, args: List[str]) -> str:
        """CLI komutunu işle"""
        try:
            if command == "help":
                return self._get_help_text()
            
            elif command == "status":
                return self._get_system_status()
            
            elif command == "modules":
                return self._list_modules()
            
            elif command == "logs":
                count = int(args[0]) if args and args[0].isdigit() else 10
                return self._get_recent_logs(count)
            
            elif command == "shutdown":
                self.shutdown()
                return "Sistem kapatılıyor..."
            
            elif command == "restart":
                self.restart()
                return "Sistem yeniden başlatılıyor..."
            
            elif command == "uptime":
                uptime = time.time() - self.start_time
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                seconds = int(uptime % 60)
                return f"Sistem çalışma süresi: {hours}s {minutes}d {seconds}s"
            
            elif command == "memory":
                if self.memory:
                    stats = self.memory.get_stats()
                    return f"Bellek kullanımı: {stats.get('used_percent', 0):.1f}% ({stats.get('used_mb', 0):.1f}MB / {stats.get('total_mb', 0):.1f}MB)"
                return "Memory modülü mevcut değil"
            
            elif command == "threads":
                if self.thread:
                    stats = self.thread.get_stats()
                    return f"Thread'ler: {stats.get('active_threads', 0)} aktif, {stats.get('total_threads', 0)} toplam"
                return "Thread modülü mevcut değil"
            
            elif command == "processes":
                if self.process:
                    stats = self.process.get_stats()
                    return f"Process'ler: {stats.get('active_processes', 0)} aktif"
                return "Process modülü mevcut değil"
            
            elif command == "users":
                if self.users:
                    users = self.users.get_all_users()
                    user_list = [f"- {user['username']} ({user['role']})" for user in users]
                    return f"Kullanıcılar:\n" + "\n".join(user_list)
                return "Users modülü mevcut değil"
            
            elif command == "apps":
                if self.appexplorer:
                    apps = self.appexplorer.get_all_apps()
                    app_list = [f"- {app['name']} v{app['version']} ({app['app_id']})" for app in apps]
                    return f"Kurulu uygulamalar ({len(apps)}):\n" + "\n".join(app_list)
                return "AppExplorer modülü mevcut değil"
            
            elif command == "python":
                if self.pythonenv:
                    info = self.pythonenv.get_python_info()
                    return f"Python: {info.version} ({info.executable})\nPip: {'Mevcut' if info.pip_available else 'Mevcut değil'}"
                return "PythonEnv modülü mevcut değil"
            
            elif command == "packages":
                if self.pythonenv:
                    packages = self.pythonenv.get_installed_packages()
                    if packages:
                        pkg_list = [f"- {pkg.name} {pkg.version}" for pkg in packages[:10]]
                        return f"Python paketleri ({len(packages)} toplam, ilk 10):\n" + "\n".join(pkg_list)
                    return "Hiç Python paketi bulunamadı"
                return "PythonEnv modülü mevcut değil"
            
            elif command == "appmon":
                if self.appmon:
                    stats = self.appmon.get_stats()
                    return f"AppMon: {stats['running_apps']} çalışan, {stats['monitored_apps']} izlenen uygulama"
                return "AppMon modülü mevcut değil"
            
            elif command == "launcher":
                if self.launcher:
                    stats = self.launcher.get_stats()
                    return f"Launcher: {stats['running_apps']} çalışan, {stats['queue_size']} kuyrukta"
                return "Launcher modülü mevcut değil"
            
            elif command == "widgets":
                # Widget sistemi için placeholder
                return "Widget sistemi henüz aktif değil"
            
            elif command == "themes":
                # Tema sistemi için placeholder
                return "Tema sistemi henüz aktif değil"
            
            elif command == "contextmenu":
                # Context menu sistemi için placeholder
                return "Context menu sistemi henüz aktif değil"
            
            elif command == "wallpaper":
                # Wallpaper sistemi için placeholder
                return "Wallpaper sistemi henüz aktif değil"
            
            elif command == "clapp":
                # Clapp sistemi için placeholder
                return "Clapp sistemi henüz aktif değil"
            
            elif command == "vfs":
                vfs = self.get_module("vfs")
                if vfs:
                    stats = vfs.get_security_stats()
                    return f"VFS Status:\n  - Active: {stats.get('active', False)}\n  - Mount points: {len(stats.get('mount_points', []))}\n  - Registered apps: {len(stats.get('app_profiles', {}))}\n  - Security checks: {stats.get('security_checks', 0)}\n  - Access denials: {stats.get('access_denials', 0)}"
                return "VFS not available"
            
            elif command == "filepicker":
                try:
                    from cloud.filepicker import FilePickerWindow
                    return "FilePicker module available\nFeatures: VFS integration, security filters, app-specific permissions"
                except ImportError:
                    return "FilePicker module not available"
            
            else:
                return f"Bilinmeyen komut: {command}. 'help' yazın."
                
        except Exception as e:
            return f"Komut hatası: {str(e)}"
    
    def _get_help_text(self) -> str:
        """Yardım metnini döndür"""
        return """
PyCloud OS Kernel CLI Komutları:

Sistem Komutları:
  help          - Bu yardım metnini göster
  status        - Sistem durumunu göster
  modules       - Yüklü modülleri listele
  uptime        - Sistem çalışma süresini göster
  shutdown      - Sistemi kapat
  restart       - Sistemi yeniden başlat

Kaynak İzleme:
  memory        - Bellek kullanımını göster
  threads       - Thread istatistiklerini göster
  processes     - Process istatistiklerini göster

Kullanıcı ve Uygulamalar:
  users         - Kullanıcıları listele
  apps          - Kurulu uygulamaları listele
  appmon        - Uygulama izleme durumu
  launcher      - Uygulama başlatıcı durumu

Python Ortamı:
  python        - Python bilgilerini göster
  packages      - Python paketlerini listele

UI Sistemleri:
  widgets       - Widget durumu
  themes        - Tema durumu
  contextmenu   - Context menu durumu
  wallpaper     - Wallpaper durumu

Paket Yönetimi:
  clapp         - Clapp durumu

Log Sistemi:
  logs [sayı]   - Son log kayıtlarını göster (varsayılan: 10)

Örnek: 'status' veya 'logs 20'
        """
    
    def _get_system_status(self) -> str:
        """Sistem durumunu döndür"""
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        status = f"""
PyCloud OS Sistem Durumu:
  Durum: {'Çalışıyor' if self.running else 'Durmuş'}
  Çalışma Süresi: {hours}s {minutes}d
  Başlangıç: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}
  Yüklü Modüller: {len(self.modules)}
  PID: {os.getpid()}
        """
        
        # Kaynak kullanımı
        if self.memory:
            mem_stats = self.memory.get_stats()
            status += f"  Bellek: {mem_stats.get('used_percent', 0):.1f}%\n"
        
        if self.thread:
            thread_stats = self.thread.get_stats()
            status += f"  Thread'ler: {thread_stats.get('active_threads', 0)}\n"
        
        if self.appmon:
            app_stats = self.appmon.get_stats()
            status += f"  Çalışan Uygulamalar: {app_stats.get('running_apps', 0)}\n"
        
        return status.strip()
    
    def _list_modules(self) -> str:
        """Yüklü modülleri listele"""
        if not self.modules:
            return "Hiç modül yüklü değil"
        
        module_list = []
        for name, module in self.modules.items():
            module_type = type(module).__name__
            status = "✓ Aktif" if hasattr(module, 'is_active') and module.is_active else "✓ Yüklü"
            module_list.append(f"  {name}: {module_type} - {status}")
        
        return f"Yüklü Modüller ({len(self.modules)}):\n" + "\n".join(module_list)
    
    def _get_recent_logs(self, count: int = 10) -> str:
        """Son log kayıtlarını döndür"""
        if not hasattr(self, 'log_entries') or not self.log_entries:
            return "Hiç log kaydı bulunamadı"
        
        recent_logs = self.log_entries[-count:]
        log_lines = []
        
        for entry in recent_logs:
            timestamp = time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))
            level = entry['level']
            message = entry['message']
            log_lines.append(f"[{timestamp}] {level}: {message}")
        
        return f"Son {len(recent_logs)} log kaydı:\n" + "\n".join(log_lines)
    
    def log(self, message: str, level: str = "INFO"):
        """Log mesajı kaydet"""
        timestamp = time.time()
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.log_entries.append(log_entry)
        
        # Logger'a da gönder
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "DEBUG":
            self.logger.debug(message)
        else:
            self.logger.info(message) 