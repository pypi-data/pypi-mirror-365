"""
PyCloud OS Application Launcher
.app uygulamalarını başlatır, yönetir ve AppMon ile entegre çalışır.
"""

import os
import json
import subprocess
import threading
import time
import signal
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

class LaunchStatus(Enum):
    """Başlatma durumu"""
    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"

class LaunchMode(Enum):
    """Başlatma modu"""
    NORMAL = "normal"
    BACKGROUND = "background"
    ELEVATED = "elevated"  # Admin izni ile
    SANDBOX = "sandbox"    # İzole ortamda

@dataclass
class LaunchRequest:
    """Başlatma isteği"""
    app_id: str
    app_path: str
    mode: LaunchMode = LaunchMode.NORMAL
    args: List[str] = None
    env_vars: Dict[str, str] = None
    working_dir: Optional[str] = None
    user_id: Optional[str] = None
    priority: int = 0  # 0=normal, 1=high, -1=low

@dataclass
class LaunchResult:
    """Başlatma sonucu"""
    success: bool
    pid: Optional[int]
    status: LaunchStatus
    error_message: Optional[str]
    start_time: float
    app_info: Optional[Dict[str, Any]]

@dataclass
class RunningApp:
    """Çalışan uygulama bilgisi"""
    app_id: str
    name: str
    version: str
    pid: int
    process: subprocess.Popen
    start_time: float
    launch_mode: LaunchMode
    app_path: str
    metadata: Dict[str, Any]
    status: LaunchStatus

class ApplicationLauncher:
    """Uygulama başlatıcı sistemi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("ApplicationLauncher")
        self.running_apps: Dict[str, RunningApp] = {}
        self.launch_queue: List[LaunchRequest] = []
        self.launcher_active = False
        self.launcher_thread = None
        self.launcher_lock = threading.Lock()
        self.config_file = "system/config/launcher.json"
        self.apps_dir = "apps"
        self.python_executable = "python3"
        
        # Callbacks
        self.on_app_launched = None
        self.on_app_failed = None
        self.on_app_stopped = None
        
        # AppMon entegrasyonu
        self.appmon = None
        
        self._load_config()
        self._setup_signal_handlers()
    
    def _load_config(self):
        """Konfigürasyon yükle"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.apps_dir = config.get('apps_dir', 'apps')
                self.python_executable = config.get('python_executable', 'python3')
                
                # Python yolu kontrolü
                if not self._check_python():
                    if self.kernel:
                        self.kernel.log("Launcher: Python bulunamadı", "WARNING")
                        
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"Launcher config yükleme hatası: {e}", "ERROR")
    
    def _save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'apps_dir': self.apps_dir,
                'python_executable': self.python_executable,
                'last_updated': time.time()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"Launcher config kaydetme hatası: {e}", "ERROR")
    
    def _check_python(self) -> bool:
        """Python varlığını kontrol et"""
        try:
            result = subprocess.run([self.python_executable, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _setup_signal_handlers(self):
        """Sinyal işleyicilerini ayarla"""
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"Launcher sinyal ayarlama hatası: {e}", "WARNING")
    
    def _signal_handler(self, signum, frame):
        """Sinyal işleyici"""
        if self.kernel:
            self.kernel.log(f"Launcher sinyal alındı: {signum}", "INFO")
        self.stop_launcher()
    
    def set_appmon(self, appmon):
        """AppMon referansını ayarla"""
        self.appmon = appmon
    
    def start_launcher(self):
        """Başlatıcıyı başlat"""
        if self.launcher_active:
            return
        
        self.launcher_active = True
        self.launcher_thread = threading.Thread(target=self._launcher_loop, daemon=True)
        self.launcher_thread.start()
        
        if self.kernel:
            self.kernel.log("Launcher başlatıldı", "INFO")
    
    def stop_launcher(self):
        """Başlatıcıyı durdur"""
        self.launcher_active = False
        if self.launcher_thread:
            self.launcher_thread.join(timeout=2.0)
        
        # Çalışan uygulamaları temiz şekilde kapat
        self._shutdown_all_apps()
        
        self._save_config()
        
        if self.kernel:
            self.kernel.log("Launcher durduruldu", "INFO")
    
    def _launcher_loop(self):
        """Ana başlatıcı döngüsü"""
        while self.launcher_active:
            try:
                with self.launcher_lock:
                    self._process_launch_queue()
                    self._check_running_apps()
                
                time.sleep(1.0)
                
            except Exception as e:
                if self.kernel:
                    self.kernel.log(f"Launcher döngü hatası: {e}", "ERROR")
                time.sleep(1.0)
    
    def _process_launch_queue(self):
        """Başlatma kuyruğunu işle"""
        if not self.launch_queue:
            return
        
        # Öncelik sırasına göre sırala
        self.launch_queue.sort(key=lambda x: x.priority, reverse=True)
        
        # İlk isteği işle
        request = self.launch_queue.pop(0)
        self._launch_app_internal(request)
    
    def _check_running_apps(self):
        """Çalışan uygulamaları kontrol et"""
        to_remove = []
        
        for app_id, running_app in self.running_apps.items():
            try:
                # Process durumunu kontrol et
                poll_result = running_app.process.poll()
                
                if poll_result is not None:
                    # Process sonlandı
                    running_app.status = LaunchStatus.STOPPED
                    to_remove.append(app_id)
                    
                    if self.on_app_stopped:
                        self.on_app_stopped(app_id, running_app, poll_result)
                    
                    # AppMon'dan kaldır
                    if self.appmon:
                        self.appmon.unregister_app(app_id)
                    
                    if self.kernel:
                        self.kernel.log(f"Launcher: {running_app.name} sonlandı (kod: {poll_result})", "INFO")
                        
            except Exception as e:
                if self.kernel:
                    self.kernel.log(f"Launcher: {app_id} kontrol hatası: {e}", "WARNING")
        
        # Sonlanan uygulamaları kaldır
        for app_id in to_remove:
            del self.running_apps[app_id]
    
    def launch_app(self, app_id: str, mode: LaunchMode = LaunchMode.NORMAL, 
                   args: List[str] = None, env_vars: Dict[str, str] = None,
                   working_dir: Optional[str] = None, user_id: Optional[str] = None,
                   priority: int = 0, **kwargs) -> bool:
        """Uygulama başlat (asenkron)"""
        
        # Uygulama zaten çalışıyor mu?
        if app_id in self.running_apps:
            if self.kernel:
                self.kernel.log(f"Launcher: {app_id} zaten çalışıyor", "WARNING")
            # Var olan pencereyi öne getir
            self._focus_existing_app(app_id)
            return True
        
        # Önce AppExplorer ile uygulama keşfini yap
        app_path = self._discover_app(app_id)
        if not app_path:
            if self.kernel:
                self.kernel.log(f"Launcher: {app_id} bulunamadı veya keşfedilemedi", "ERROR")
            return False
        
        # Dosya açma parametrelerini işle
        if args is None:
            args = []
        
        # kwargs'dan dosya parametrelerini al
        if 'open_file' in kwargs:
            args.extend(['--open-file', kwargs['open_file']])
        if 'open_path' in kwargs:
            args.extend(['--open-path', kwargs['open_path']])
        
        # Başlatma isteği oluştur
        request = LaunchRequest(
            app_id=app_id,
            app_path=app_path,
            mode=mode,
            args=args,
            env_vars=env_vars or {},
            working_dir=working_dir,
            user_id=user_id,
            priority=priority
        )
        
        # Kuyruğa ekle
        with self.launcher_lock:
            self.launch_queue.append(request)
        
        if self.kernel:
            self.kernel.log(f"Launcher: {app_id} başlatma kuyruğuna eklendi (args: {args})", "INFO")
        
        return True
    
    def _discover_app(self, app_id: str) -> Optional[str]:
        """Uygulamayı keşfet ve yolunu döndür"""
        try:
            # Önce standart apps/ dizininde ara
            standard_path = os.path.join(self.apps_dir, app_id)
            if os.path.exists(standard_path) and os.path.isdir(standard_path):
                app_json_path = os.path.join(standard_path, 'app.json')
                if os.path.exists(app_json_path):
                    return standard_path
            
            # AppExplorer ile keşfet
            if self.kernel:
                app_explorer = self.kernel.get_module("appexplorer")
                if app_explorer:
                    # App Explorer'ı yenile
                    app_explorer.force_discovery()
                    
                    # Uygulamayı ara
                    app_info = app_explorer.get_app_by_id(app_id)
                    if app_info and app_info.app_path and os.path.exists(app_info.app_path):
                        return app_info.app_path
            
            # Son çare: tüm apps/ alt dizinlerinde ara
            if os.path.exists(self.apps_dir):
                for item in os.listdir(self.apps_dir):
                    item_path = os.path.join(self.apps_dir, item)
                    if os.path.isdir(item_path):
                        app_json_path = os.path.join(item_path, 'app.json')
                        if os.path.exists(app_json_path):
                            try:
                                with open(app_json_path, 'r', encoding='utf-8') as f:
                                    app_info = json.load(f)
                                    if app_info.get('id') == app_id:
                                        return item_path
                            except:
                                continue
            
            return None
            
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"Launcher: App discovery error for {app_id}: {e}", "ERROR")
            return None
    
    def _focus_existing_app(self, app_id: str):
        """Var olan uygulamanın penceresini öne getir"""
        try:
            if self.kernel:
                window_manager = self.kernel.get_module("windowmanager")
                if window_manager:
                    # Uygulamanın pencerelerini bul
                    windows = window_manager.get_windows_by_app(app_id)
                    if windows:
                        # İlk pencereyi aktif et
                        window_manager._set_active_window(windows[0].window_id)
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"Failed to focus existing app {app_id}: {e}", "WARNING")
    
    def launch_app_sync(self, app_id: str, mode: LaunchMode = LaunchMode.NORMAL,
                       args: List[str] = None, env_vars: Dict[str, str] = None,
                       timeout: float = 10.0) -> LaunchResult:
        """Uygulama başlat (senkron)"""
        
        app_path = os.path.join(self.apps_dir, app_id)
        if not os.path.exists(app_path):
            return LaunchResult(
                success=False,
                pid=None,
                status=LaunchStatus.FAILED,
                error_message=f"Uygulama bulunamadı: {app_path}",
                start_time=time.time(),
                app_info=None
            )
        
        request = LaunchRequest(
            app_id=app_id,
            app_path=app_path,
            mode=mode,
            args=args or [],
            env_vars=env_vars or {}
        )
        
        return self._launch_app_internal(request)
    
    def _launch_app_internal(self, request: LaunchRequest) -> LaunchResult:
        """İç başlatma fonksiyonu"""
        start_time = time.time()
        
        try:
            # app.json dosyasını yükle
            app_json_path = os.path.join(request.app_path, 'app.json')
            if not os.path.exists(app_json_path):
                return LaunchResult(
                    success=False,
                    pid=None,
                    status=LaunchStatus.FAILED,
                    error_message="app.json bulunamadı",
                    start_time=start_time,
                    app_info=None
                )
            
            with open(app_json_path, 'r', encoding='utf-8') as f:
                app_info = json.load(f)
            
            # Entry dosyasını kontrol et
            entry_file = app_info.get('entry', 'main.py')
            entry_path = os.path.join(request.app_path, entry_file)
            
            if not os.path.exists(entry_path):
                return LaunchResult(
                    success=False,
                    pid=None,
                    status=LaunchStatus.FAILED,
                    error_message=f"Entry dosyası bulunamadı: {entry_file}",
                    start_time=start_time,
                    app_info=app_info
                )
            
            # Çalışma dizini
            working_dir = request.working_dir or request.app_path
            
            # Ortam değişkenleri
            env = os.environ.copy()
            env.update(request.env_vars)
            env['PYCLOUD_APP_ID'] = request.app_id
            env['PYCLOUD_APP_PATH'] = request.app_path
            
            # Bridge manager bilgilerini ortam değişkenlerine ekle
            if self.kernel:
                bridge_manager = self.kernel.get_module("bridge")
                if bridge_manager:
                    # Bridge manager'ın çalıştığını belirt
                    env['PYCLOUD_BRIDGE_AVAILABLE'] = 'true'
                    env['PYCLOUD_KERNEL_PID'] = str(os.getpid())
                    
                    # Uygulama için bridge bağlantısı kur
                    try:
                        from core.bridge import PermissionLevel
                        
                        # Uygulama türüne göre izin seviyesi belirle
                        app_name = app_info.get('name', request.app_id)
                        
                        # Sistem uygulamaları için FULL, diğerleri için WRITE izni
                        if request.app_id.startswith('cloud_') or request.app_id in ['system_monitor', 'task_manager']:
                            permission_level = PermissionLevel.FULL
                        else:
                            permission_level = PermissionLevel.WRITE
                        
                        # Bridge bağlantılarını kur
                        bridge_modules = ['fs', 'config', 'events', 'notify', 'users']
                        for module_name in bridge_modules:
                            success = bridge_manager.connect_app_to_module(
                                app_id=request.app_id,
                                app_name=app_name,
                                module_name=module_name,
                                permission_level=permission_level
                            )
                            if success:
                                self.logger.debug(f"Bridge connection established: {request.app_id} -> {module_name}")
                        
                        env['PYCLOUD_BRIDGE_CONNECTED'] = 'true'
                        
                    except Exception as e:
                        self.logger.warning(f"Bridge connection setup failed for {request.app_id}: {e}")
                        env['PYCLOUD_BRIDGE_CONNECTED'] = 'false'
            
            # Komut oluştur
            if request.mode == LaunchMode.BACKGROUND:
                # Arka plan modu
                cmd = [self.python_executable, entry_file] + request.args
            elif request.mode == LaunchMode.ELEVATED:
                # Yükseltilmiş mod (sudo)
                cmd = ['sudo', self.python_executable, entry_file] + request.args
            else:
                # Normal mod
                cmd = [self.python_executable, entry_file] + request.args
            
            # Process başlat
            if request.mode == LaunchMode.BACKGROUND:
                process = subprocess.Popen(
                    cmd,
                    cwd=working_dir,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    cwd=working_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Kısa süre bekle (başlatma kontrolü)
            time.sleep(0.5)
            
            # Process hala çalışıyor mu?
            if process.poll() is not None:
                # Hemen sonlandı, hata var
                stdout, stderr = process.communicate()
                error_msg = stderr.decode('utf-8') if stderr else "Bilinmeyen hata"
                
                return LaunchResult(
                    success=False,
                    pid=None,
                    status=LaunchStatus.FAILED,
                    error_message=error_msg,
                    start_time=start_time,
                    app_info=app_info
                )
            
            # Başarılı başlatma
            running_app = RunningApp(
                app_id=request.app_id,
                name=app_info.get('name', request.app_id),
                version=app_info.get('version', '1.0.0'),
                pid=process.pid,
                process=process,
                start_time=start_time,
                launch_mode=request.mode,
                app_path=request.app_path,
                metadata=app_info,
                status=LaunchStatus.RUNNING
            )
            
            # Çalışan uygulamalar listesine ekle
            self.running_apps[request.app_id] = running_app
            
            # AppMon'a kaydet
            if self.appmon:
                self.appmon.register_app(
                    app_id=request.app_id,
                    name=running_app.name,
                    version=running_app.version,
                    pid=process.pid,
                    app_path=request.app_path,
                    metadata=app_info
                )
            
            # Window Manager'da pencere oluştur
            if self.kernel:
                window_manager = self.kernel.get_module("windowmanager")
                if window_manager:
                    try:
                        from rain.windowmanager import WindowType
                        
                        # Icon path belirle
                        icon_path = None
                        if 'icon' in app_info:
                            icon_path = os.path.join(request.app_path, app_info['icon'])
                            if not os.path.exists(icon_path):
                                icon_path = None
                        
                        # Pencere oluştur
                        window_id = window_manager.create_window(
                            app_id=request.app_id,
                            title=running_app.name,
                            window_type=WindowType.APPLICATION,
                            icon_path=icon_path,
                            metadata={
                                'pid': process.pid,
                                'version': running_app.version,
                                'app_path': request.app_path
                            }
                        )
                        
                        # Running app'e window_id ekle
                        running_app.metadata['window_id'] = window_id
                        
                        if self.kernel:
                            self.kernel.log(f"Launcher: Pencere oluşturuldu: {window_id}", "INFO")
                            
                    except Exception as e:
                        if self.kernel:
                            self.kernel.log(f"Launcher: Pencere oluşturma hatası: {e}", "WARNING")
            
            # Callback çağır
            if self.on_app_launched:
                self.on_app_launched(request.app_id, running_app)
            
            if self.kernel:
                self.kernel.log(f"Launcher: {running_app.name} başlatıldı (PID: {process.pid})", "INFO")
            
            return LaunchResult(
                success=True,
                pid=process.pid,
                status=LaunchStatus.RUNNING,
                error_message=None,
                start_time=start_time,
                app_info=app_info
            )
            
        except Exception as e:
            error_msg = f"Başlatma hatası: {str(e)}"
            
            if self.on_app_failed:
                self.on_app_failed(request.app_id, error_msg)
            
            if self.kernel:
                self.kernel.log(f"Launcher: {request.app_id} başlatma hatası: {e}", "ERROR")
            
            return LaunchResult(
                success=False,
                pid=None,
                status=LaunchStatus.FAILED,
                error_message=error_msg,
                start_time=start_time,
                app_info=None
            )
    
    def stop_app(self, app_id: str, force: bool = False) -> bool:
        """Uygulamayı durdur"""
        if app_id not in self.running_apps:
            return False
        
        running_app = self.running_apps[app_id]
        
        try:
            # Window Manager'dan pencereyi kapat
            if self.kernel:
                window_manager = self.kernel.get_module("windowmanager")
                if window_manager and 'window_id' in running_app.metadata:
                    window_id = running_app.metadata['window_id']
                    try:
                        window_manager.close_window(window_id)
                        if self.kernel:
                            self.kernel.log(f"Launcher: Pencere kapatıldı: {window_id}", "INFO")
                    except Exception as e:
                        if self.kernel:
                            self.kernel.log(f"Launcher: Pencere kapatma hatası: {e}", "WARNING")
            
            if force:
                # Zorla sonlandır
                running_app.process.kill()
                if self.kernel:
                    self.kernel.log(f"Launcher: {running_app.name} zorla sonlandırıldı", "WARNING")
            else:
                # Nazikçe sonlandır
                running_app.process.terminate()
                if self.kernel:
                    self.kernel.log(f"Launcher: {running_app.name} sonlandırılıyor", "INFO")
            
            # 5 saniye bekle, sonra zorla öldür
            if not force:
                threading.Timer(5.0, lambda: self._force_stop_app(app_id)).start()
            
            return True
            
        except Exception as e:
            if self.kernel:
                self.kernel.log(f"Launcher: {app_id} durdurma hatası: {e}", "ERROR")
            return False
    
    def _force_stop_app(self, app_id: str):
        """Uygulamayı zorla durdur"""
        if app_id in self.running_apps:
            running_app = self.running_apps[app_id]
            try:
                if running_app.process.poll() is None:
                    running_app.process.kill()
                    if self.kernel:
                        self.kernel.log(f"Launcher: {running_app.name} zorla sonlandırıldı", "WARNING")
            except Exception as e:
                if self.kernel:
                    self.kernel.log(f"Launcher: {app_id} zorla durdurma hatası: {e}", "ERROR")
    
    def _shutdown_all_apps(self):
        """Tüm uygulamaları kapat"""
        if not self.running_apps:
            return
        
        if self.kernel:
            self.kernel.log("Launcher: Tüm uygulamalar kapatılıyor", "INFO")
        
        # Önce nazikçe kapat
        for app_id in list(self.running_apps.keys()):
            self.stop_app(app_id, force=False)
        
        # 3 saniye bekle
        time.sleep(3.0)
        
        # Hala çalışanları zorla kapat
        for app_id in list(self.running_apps.keys()):
            self.stop_app(app_id, force=True)
    
    def restart_app(self, app_id: str) -> bool:
        """Uygulamayı yeniden başlat"""
        if app_id not in self.running_apps:
            return False
        
        running_app = self.running_apps[app_id]
        
        # Mevcut ayarları kaydet
        launch_mode = running_app.launch_mode
        app_path = running_app.app_path
        
        # Durdur
        if not self.stop_app(app_id):
            return False
        
        # Kısa süre bekle
        time.sleep(1.0)
        
        # Yeniden başlat
        return self.launch_app(app_id, mode=launch_mode)
    
    def get_running_app(self, app_id: str) -> Optional[RunningApp]:
        """Çalışan uygulama bilgisini al"""
        return self.running_apps.get(app_id)
    
    def get_all_running_apps(self) -> Dict[str, RunningApp]:
        """Tüm çalışan uygulamaları al"""
        return self.running_apps.copy()
    
    def is_app_running(self, app_id: str) -> bool:
        """Uygulama çalışıyor mu?"""
        return app_id in self.running_apps
    
    def get_app_pid(self, app_id: str) -> Optional[int]:
        """Uygulama PID'ini al"""
        if app_id in self.running_apps:
            return self.running_apps[app_id].pid
        return None
    
    def get_available_apps(self) -> List[Dict[str, Any]]:
        """Mevcut uygulamaları listele"""
        apps = []
        
        if not os.path.exists(self.apps_dir):
            return apps
        
        for app_dir in os.listdir(self.apps_dir):
            app_path = os.path.join(self.apps_dir, app_dir)
            app_json_path = os.path.join(app_path, 'app.json')
            
            if os.path.isdir(app_path) and os.path.exists(app_json_path):
                try:
                    with open(app_json_path, 'r', encoding='utf-8') as f:
                        app_info = json.load(f)
                        app_info['app_id'] = app_dir
                        app_info['app_path'] = app_path
                        app_info['is_running'] = app_dir in self.running_apps
                        apps.append(app_info)
                except Exception as e:
                    if self.kernel:
                        self.kernel.log(f"Launcher: {app_dir} app.json okuma hatası: {e}", "WARNING")
        
        return apps
    
    def validate_app(self, app_id: str) -> Tuple[bool, str]:
        """Uygulama geçerliliğini kontrol et"""
        app_path = os.path.join(self.apps_dir, app_id)
        
        if not os.path.exists(app_path):
            return False, "Uygulama dizini bulunamadı"
        
        app_json_path = os.path.join(app_path, 'app.json')
        if not os.path.exists(app_json_path):
            return False, "app.json dosyası bulunamadı"
        
        try:
            with open(app_json_path, 'r', encoding='utf-8') as f:
                app_info = json.load(f)
            
            # Gerekli alanları kontrol et
            required_fields = ['name', 'version', 'entry']
            for field in required_fields:
                if field not in app_info:
                    return False, f"Gerekli alan eksik: {field}"
            
            # Entry dosyasını kontrol et
            entry_file = app_info['entry']
            entry_path = os.path.join(app_path, entry_file)
            if not os.path.exists(entry_path):
                return False, f"Entry dosyası bulunamadı: {entry_file}"
            
            return True, "Geçerli"
            
        except json.JSONDecodeError:
            return False, "app.json geçersiz JSON formatı"
        except Exception as e:
            return False, f"Doğrulama hatası: {str(e)}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Launcher istatistikleri"""
        return {
            'launcher_active': self.launcher_active,
            'running_apps': len(self.running_apps),
            'queue_size': len(self.launch_queue),
            'apps_dir': self.apps_dir,
            'python_executable': self.python_executable,
            'python_available': self._check_python(),
            'apps': {app_id: {
                'name': app.name,
                'version': app.version,
                'pid': app.pid,
                'status': app.status.value,
                'launch_mode': app.launch_mode.value,
                'start_time': app.start_time,
                'uptime': time.time() - app.start_time
            } for app_id, app in self.running_apps.items()}
        }

# Global instance
launcher = None

def get_launcher():
    """Global Launcher instance'ını al"""
    global launcher
    return launcher

def init_launcher(kernel=None):
    """Launcher'ı başlat"""
    global launcher
    if launcher is None:
        launcher = ApplicationLauncher(kernel)
        launcher.start_launcher()
    return launcher 