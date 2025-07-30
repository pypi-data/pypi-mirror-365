"""
PyCloud OS Core Bridge
Uygulamalar ve çekirdek modüller arasında güvenli bağlantı arayüzü sağlar
"""

import logging
import json
import threading
import socket
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import os
import glob

class BridgeStatus(Enum):
    """Bridge bağlantı durumları"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    SUSPENDED = "suspended"

class PermissionLevel(Enum):
    """İzin seviyeleri"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    FULL = "full"

@dataclass
class BridgeConnection:
    """Bridge bağlantı bilgisi"""
    app_id: str
    app_name: str
    module_name: str
    permission_level: PermissionLevel
    status: BridgeStatus
    created_at: str
    last_used: str = ""
    usage_count: int = 0
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['permission_level'] = self.permission_level.value
        data['status'] = self.status.value
        return data

class ModuleBridge:
    """Tek bir modül için bridge arayüzü"""
    
    def __init__(self, module_name: str, module_instance: Any, kernel=None):
        self.module_name = module_name
        self.module_instance = module_instance
        self.kernel = kernel
        self.logger = logging.getLogger(f"Bridge_{module_name}")
        
        # Bağlantılar
        self.connections: Dict[str, BridgeConnection] = {}
        
        # İzin verilen metodlar
        self.allowed_methods = self._get_allowed_methods()
        
        # Thread safety
        self.lock = threading.RLock()
    
    def _get_allowed_methods(self) -> Dict[str, PermissionLevel]:
        """Modül için izin verilen metodları al"""
        # Her modül için özel izin haritası
        method_permissions = {
            "fs": {
                "read_file": PermissionLevel.READ,
                "write_file": PermissionLevel.WRITE,
                "list_directory": PermissionLevel.READ,
                "create_directory": PermissionLevel.WRITE,
                "delete_file": PermissionLevel.FULL,
                "get_file_info": PermissionLevel.READ
            },
            "config": {
                "get": PermissionLevel.READ,
                "get_config": PermissionLevel.READ,
                "set": PermissionLevel.WRITE,
                "set_config": PermissionLevel.WRITE,
                "save_config": PermissionLevel.WRITE
            },
            "events": {
                "subscribe": PermissionLevel.READ,
                "publish": PermissionLevel.WRITE,
                "unsubscribe": PermissionLevel.READ
            },
            "notify": {
                "send_notification": PermissionLevel.WRITE,
                "get_notifications": PermissionLevel.READ
            },
            "users": {
                "get_current_user": PermissionLevel.READ,
                "get_user_info": PermissionLevel.READ
            },
            "security": {
                "check_permission": PermissionLevel.READ,
                "validate_access": PermissionLevel.READ
            },
            "launcher": {
                "launch_app": PermissionLevel.WRITE,
                "get_running_apps": PermissionLevel.READ,
                "kill_app": PermissionLevel.FULL
            },
            "vfs": {
                "get_security_stats": PermissionLevel.READ,
                "get_app_profile": PermissionLevel.READ,
                "create_app_profile": PermissionLevel.WRITE,
                "update_app_profile": PermissionLevel.WRITE,
                "check_access": PermissionLevel.READ,
                "validate_path": PermissionLevel.READ,
                "resolve_path": PermissionLevel.READ,
                "get_mount_info": PermissionLevel.READ,
                "list_allowed_paths": PermissionLevel.READ,
                "check_app_access": PermissionLevel.READ,
                "set_user_context": PermissionLevel.WRITE,
                "get_user_home_path": PermissionLevel.READ,
                "create_user_app_profile": PermissionLevel.WRITE,
                "get_user_app_profile": PermissionLevel.READ,
                "check_user_access": PermissionLevel.READ
            }
        }
        
        return method_permissions.get(self.module_name, {})
    
    def connect_app(self, app_id: str, app_name: str, permission_level: PermissionLevel) -> bool:
        """Uygulamayı modüle bağla"""
        try:
            with self.lock:
                connection = BridgeConnection(
                    app_id=app_id,
                    app_name=app_name,
                    module_name=self.module_name,
                    permission_level=permission_level,
                    status=BridgeStatus.CONNECTING,
                    created_at=datetime.now().isoformat()
                )
                
                # Bağlantıyı test et
                if self._test_connection(connection):
                    connection.status = BridgeStatus.CONNECTED
                    self.connections[app_id] = connection
                    self.logger.info(f"Connected app {app_id} to {self.module_name}")
                    return True
                else:
                    connection.status = BridgeStatus.ERROR
                    connection.error_message = "Connection test failed"
                    self.logger.error(f"Failed to connect app {app_id} to {self.module_name}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error connecting app {app_id}: {e}")
            return False
    
    def disconnect_app(self, app_id: str) -> bool:
        """Uygulamayı modülden ayır"""
        try:
            with self.lock:
                if app_id in self.connections:
                    del self.connections[app_id]
                    self.logger.info(f"Disconnected app {app_id} from {self.module_name}")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error disconnecting app {app_id}: {e}")
            return False
    
    def call_method(self, app_id: str, method_name: str, *args, **kwargs) -> tuple[bool, Any]:
        """Uygulama adına modül metodunu çağır"""
        try:
            with self.lock:
                # Bağlantı kontrolü
                if app_id not in self.connections:
                    return False, "App not connected"
                
                connection = self.connections[app_id]
                
                # Durum kontrolü
                if connection.status != BridgeStatus.CONNECTED:
                    return False, f"Connection status: {connection.status.value}"
                
                # İzin kontrolü
                if method_name not in self.allowed_methods:
                    return False, f"Method {method_name} not allowed"
                
                required_permission = self.allowed_methods[method_name]
                if not self._check_permission(connection.permission_level, required_permission):
                    return False, f"Insufficient permission for {method_name}"
                
                # Metod çağrısı
                if hasattr(self.module_instance, method_name):
                    method = getattr(self.module_instance, method_name)
                    result = method(*args, **kwargs)
                    
                    # İstatistik güncelle
                    connection.last_used = datetime.now().isoformat()
                    connection.usage_count += 1
                    
                    return True, result
                else:
                    return False, f"Method {method_name} not found"
                    
        except Exception as e:
            self.logger.error(f"Error calling method {method_name} for app {app_id}: {e}")
            return False, str(e)
    
    def _test_connection(self, connection: BridgeConnection) -> bool:
        """Bağlantıyı test et"""
        try:
            # Basit test - modül instance'ının varlığını kontrol et
            return self.module_instance is not None
        except:
            return False
    
    def _check_permission(self, app_permission: PermissionLevel, required_permission: PermissionLevel) -> bool:
        """İzin seviyesini kontrol et"""
        permission_hierarchy = {
            PermissionLevel.NONE: 0,
            PermissionLevel.READ: 1,
            PermissionLevel.WRITE: 2,
            PermissionLevel.FULL: 3
        }
        
        return permission_hierarchy[app_permission] >= permission_hierarchy[required_permission]
    
    def get_connection_info(self, app_id: str) -> Optional[BridgeConnection]:
        """Bağlantı bilgisini al"""
        return self.connections.get(app_id)
    
    def get_all_connections(self) -> List[BridgeConnection]:
        """Tüm bağlantıları al"""
        return list(self.connections.values())

    def get_connection_status(self, app_id: str) -> BridgeStatus:
        """Uygulama bağlantı durumunu al"""
        if app_id in self.connections:
            return self.connections[app_id].status
        return BridgeStatus.DISCONNECTED
    
    def get_kernel_reference(self):
        """Kernel referansını al"""
        return self.kernel

class BridgeManager:
    """Ana bridge yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("BridgeManager")
        self.logger.setLevel(logging.DEBUG)  # Debug loglarını aktif et
        
        # Modül bridge'leri
        self.module_bridges: Dict[str, ModuleBridge] = {}
        
        # Yapılandırma
        self.config_file = Path("system/config/bridge_config.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self.lock = threading.RLock()
        
        self._initialize_bridges()
    
    def _initialize_bridges(self):
        """Kernel'deki modülleri bridge'lere ekle"""
        try:
            # Core modülleri bridge'e ekle
            core_modules = [
                "config", "users", "fs", "vfs", "process", "thread", 
                "memory", "security", "services", "events", "locale", 
                "notify", "appkit", "appexplorer", "appmon"
            ]
            
            for module_name in core_modules:
                module_instance = self.kernel.get_module(module_name)
                if module_instance:
                    bridge = ModuleBridge(module_name, module_instance, self.kernel)
                    self.module_bridges[module_name] = bridge
                    self.logger.info(f"Initialized bridge for {module_name}")
                else:
                    self.logger.warning(f"Module {module_name} not available during bridge initialization")
            
            # Launcher modülü özel kontrolü - runtime'da tekrar dene
            if "launcher" not in self.module_bridges:
                self.logger.info("Launcher modülü bridge başlatma sırasında bulunamadı, runtime'da tekrar denenecek")
                # Timer ile 2 saniye sonra tekrar dene
                import threading
                def delayed_launcher_check():
                    import time
                    time.sleep(2.0)
                    self._try_add_launcher()
                
                threading.Thread(target=delayed_launcher_check, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Error initializing bridges: {e}")
    
    def _try_add_launcher(self):
        """Launcher modülünü eklemeyi dene"""
        try:
            if "launcher" not in self.module_bridges and self.kernel:
                launcher_instance = self.kernel.get_module("launcher")
                if launcher_instance:
                    bridge = ModuleBridge("launcher", launcher_instance, self.kernel)
                    self.module_bridges["launcher"] = bridge
                    self.logger.info("Launcher modülü runtime'da bridge'e eklendi")
                    return True
                else:
                    self.logger.warning("Launcher modülü hala kernel'da bulunamadı")
                    return False
        except Exception as e:
            self.logger.error(f"Launcher modülü ekleme hatası: {e}")
            return False
    
    def add_module(self, module_name: str) -> bool:
        """Runtime'da yeni modül ekle"""
        try:
            with self.lock:
                if module_name in self.module_bridges:
                    self.logger.warning(f"Module {module_name} already exists in bridge")
                    return True
                
                module_instance = self.kernel.get_module(module_name)
                if module_instance:
                    bridge = ModuleBridge(module_name, module_instance, self.kernel)
                    self.module_bridges[module_name] = bridge
                    self.logger.info(f"Added module {module_name} to bridge")
                    return True
                else:
                    self.logger.error(f"Module {module_name} not found in kernel")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error adding module {module_name}: {e}")
            return False
    
    def connect_app_to_module(self, app_id: str, app_name: str, module_name: str, 
                             permission_level: PermissionLevel) -> bool:
        """Uygulamayı modüle bağla"""
        try:
            with self.lock:
                if module_name not in self.module_bridges:
                    self.logger.error(f"Module {module_name} not available")
                    return False
                
                bridge = self.module_bridges[module_name]
                return bridge.connect_app(app_id, app_name, permission_level)
                
        except Exception as e:
            self.logger.error(f"Error connecting app {app_id} to {module_name}: {e}")
            return False
    
    def disconnect_app_from_module(self, app_id: str, module_name: str) -> bool:
        """Uygulamayı modülden ayır"""
        try:
            with self.lock:
                if module_name not in self.module_bridges:
                    return False
                
                bridge = self.module_bridges[module_name]
                return bridge.disconnect_app(app_id)
                
        except Exception as e:
            self.logger.error(f"Error disconnecting app {app_id} from {module_name}: {e}")
            return False
    
    def disconnect_app_from_all(self, app_id: str) -> int:
        """Uygulamayı tüm modüllerden ayır"""
        disconnected_count = 0
        
        try:
            with self.lock:
                for module_name, bridge in self.module_bridges.items():
                    if bridge.disconnect_app(app_id):
                        disconnected_count += 1
                
                self.logger.info(f"Disconnected app {app_id} from {disconnected_count} modules")
                return disconnected_count
                
        except Exception as e:
            self.logger.error(f"Error disconnecting app {app_id} from all modules: {e}")
            return disconnected_count
    
    def call_module_method(self, app_id: str, module_name: str, method_name: str, 
                          *args, **kwargs) -> tuple[bool, Any]:
        """Uygulama adına modül metodunu çağır"""
        try:
            self.logger.debug(f"Bridge call: {app_id} -> {module_name}.{method_name}")
            
            # Launcher modülü özel kontrolü
            if module_name == "launcher" and module_name not in self.module_bridges:
                self.logger.warning("Launcher modülü bulunamadı, runtime'da eklemeyi deniyorum...")
                success = self._try_add_launcher()
                if not success:
                    self.logger.error("Launcher modülü eklenemedi")
                    return False, f"Module {module_name} not available"
            
            if module_name not in self.module_bridges:
                self.logger.error(f"Module {module_name} not available")
                return False, f"Module {module_name} not available"
            
            bridge = self.module_bridges[module_name]
            
            # Uygulama bağlantısını kontrol et
            if app_id not in bridge.connections:
                self.logger.warning(f"App {app_id} not connected to {module_name}, auto-connecting...")
                
                # Metodun gerektirdiği izin seviyesini al
                allowed_methods = bridge._get_allowed_methods()
                required_permission = allowed_methods.get(method_name, PermissionLevel.READ)
                
                # Otomatik bağlantı kur
                success = bridge.connect_app(app_id, f"App_{app_id}", required_permission)
                if not success:
                    self.logger.error(f"Failed to auto-connect app {app_id} to {module_name}")
                    return False, f"App {app_id} not connected to {module_name}"
            
            result = bridge.call_method(app_id, method_name, *args, **kwargs)
            self.logger.debug(f"Bridge call result: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calling {module_name}.{method_name} for app {app_id}: {e}")
            return False, str(e)
    
    def get_app_connections(self, app_id: str) -> Dict[str, BridgeConnection]:
        """Uygulamanın tüm bağlantılarını al"""
        connections = {}
        
        try:
            for module_name, bridge in self.module_bridges.items():
                connection = bridge.get_connection_info(app_id)
                if connection:
                    connections[module_name] = connection
            
            return connections
            
        except Exception as e:
            self.logger.error(f"Error getting connections for app {app_id}: {e}")
            return {}
    
    def get_module_connections(self, module_name: str) -> List[BridgeConnection]:
        """Modülün tüm bağlantılarını al"""
        try:
            if module_name in self.module_bridges:
                bridge = self.module_bridges[module_name]
                return bridge.get_all_connections()
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting connections for module {module_name}: {e}")
            return []
    
    def get_bridge_stats(self) -> Dict:
        """Bridge istatistiklerini al"""
        try:
            stats = {
                "total_modules": len(self.module_bridges),
                "total_connections": 0,
                "modules": {}
            }
            
            for module_name, bridge in self.module_bridges.items():
                connections = bridge.get_all_connections()
                stats["modules"][module_name] = {
                    "connection_count": len(connections),
                    "active_connections": len([c for c in connections if c.status == BridgeStatus.CONNECTED])
                }
                stats["total_connections"] += len(connections)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting bridge stats: {e}")
            return {}
    
    def shutdown(self):
        """Bridge manager'ı kapat"""
        try:
            with self.lock:
                # Tüm bağlantıları kapat
                for module_name, bridge in self.module_bridges.items():
                    for app_id in list(bridge.connections.keys()):
                        bridge.disconnect_app(app_id)
                
                self.module_bridges.clear()
                self.logger.info("Bridge manager shutdown completed")
                
        except Exception as e:
            self.logger.error(f"Error during bridge manager shutdown: {e}")

# Global bridge manager referansı
_global_bridge_manager = None
_ipc_server = None

def init_bridge_manager(kernel) -> BridgeManager:
    """Bridge manager'ı başlat"""
    global _global_bridge_manager, _ipc_server
    _global_bridge_manager = BridgeManager(kernel)
    
    # IPC server'ı başlat
    try:
        _ipc_server = BridgeIPCServer(_global_bridge_manager)
        _ipc_server.start()
    except Exception as e:
        logging.getLogger("BridgeManager").warning(f"IPC server başlatılamadı: {e}")
    
    return _global_bridge_manager

def get_bridge_manager() -> Optional[BridgeManager]:
    """Global bridge manager'ı al"""
    # Eğer aynı process'teyse direkt döndür
    if _global_bridge_manager:
        # Launcher modülünü kontrol et ve yoksa ekle
        try:
            if "launcher" not in _global_bridge_manager.module_bridges:
                success = _global_bridge_manager.add_module("launcher")
                if success:
                    logging.getLogger("BridgeManager").info("Launcher modülü runtime'da eklendi")
                else:
                    logging.getLogger("BridgeManager").warning("Launcher modülü eklenemedi")
        except Exception as e:
            logging.getLogger("BridgeManager").error(f"Launcher modülü ekleme hatası: {e}")
        return _global_bridge_manager
    
    # Farklı process'teyse IPC client kullan
    try:
        if os.environ.get('PYCLOUD_BRIDGE_AVAILABLE') == 'true':
            return BridgeIPCClient()
    except Exception:
        pass
    
    return None

def get_kernel_reference():
    """Kernel referansını al"""
    bridge_manager = get_bridge_manager()
    if bridge_manager and hasattr(bridge_manager, 'kernel'):
        return bridge_manager.kernel
    return None

class BridgeIPCServer:
    """Bridge IPC Server - Ana process'te çalışır"""
    
    def __init__(self, bridge_manager: BridgeManager):
        self.bridge_manager = bridge_manager
        self.logger = logging.getLogger("BridgeIPCServer")
        self.logger.setLevel(logging.DEBUG)  # Debug loglarını aktif et
        self.server_socket = None
        self.running = False
        self.server_thread = None
        
        # Socket dosya yolu
        import tempfile
        self.socket_path = os.path.join(tempfile.gettempdir(), f"pycloud_bridge_{os.getpid()}.sock")
    
    def start(self):
        """IPC server'ı başlat"""
        try:
            import socket
            
            # Unix domain socket oluştur
            self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            
            # Eski socket dosyasını temizle
            try:
                os.unlink(self.socket_path)
            except FileNotFoundError:
                pass
            
            self.server_socket.bind(self.socket_path)
            self.server_socket.listen(5)
            
            self.running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            self.logger.info(f"Bridge IPC server started: {self.socket_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to start IPC server: {e}")
            raise
    
    def stop(self):
        """IPC server'ı durdur"""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        try:
            os.unlink(self.socket_path)
        except:
            pass
        
        self.logger.info("Bridge IPC server stopped")
    
    def _server_loop(self):
        """Server ana döngüsü"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                
                # Client'ı ayrı thread'de işle
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Server loop error: {e}")
                break
    
    def _handle_client(self, client_socket):
        """Client isteğini işle"""
        try:
            # İstek al
            data = client_socket.recv(4096)
            if not data:
                return
            
            import json
            request = json.loads(data.decode('utf-8'))
            
            # İsteği işle
            response = self._process_request(request)
            
            # Yanıt gönder
            response_data = json.dumps(response).encode('utf-8')
            client_socket.send(response_data)
            
        except Exception as e:
            self.logger.error(f"Client handling error: {e}")
            error_response = {
                'success': False,
                'error': str(e)
            }
            try:
                response_data = json.dumps(error_response).encode('utf-8')
                client_socket.send(response_data)
            except:
                pass
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _process_request(self, request: dict) -> dict:
        """İsteği işle"""
        try:
            action = request.get('action')
            self.logger.debug(f"🔍 Processing request with action: '{action}'")
            self.logger.debug(f"🔍 Full request: {request}")
            
            if action == 'call_method':
                self.logger.debug(f"✅ Entered call_method action")
                app_id = request.get('app_id')
                module_name = request.get('module_name')
                method_name = request.get('method_name')
                args = request.get('args', [])
                kwargs = request.get('kwargs', {})
                
                self.logger.debug(f"Method call: {app_id} -> {module_name}.{method_name}({args}, {kwargs})")
                
                self.logger.debug(f"Calling bridge_manager.call_module_method...")
                try:
                    success, result = self.bridge_manager.call_module_method(
                        app_id, module_name, method_name, *args, **kwargs
                    )
                    self.logger.debug(f"Bridge manager call completed")
                except Exception as bridge_error:
                    self.logger.error(f"Bridge manager call failed: {bridge_error}")
                    import traceback
                    self.logger.error(f"Bridge traceback: {traceback.format_exc()}")
                    success, result = False, str(bridge_error)
                
                self.logger.debug(f"Method call result: success={success}, result_type={type(result)}")
                
                if not success:
                    self.logger.error(f"Method call failed: {result}")
                
                # Response formatını düzelt - başarısız durumda 'error' field'ı kullan
                if success:
                    return {
                        'success': True,
                        'result': result
                    }
                else:
                    return {
                        'success': False,
                        'error': result  # 'result' yerine 'error' field'ı kullan
                    }
            
            elif action == 'get_kernel':
                self.logger.debug(f"✅ Entered get_kernel action")
                # Kernel referansı döndür (sadece temel bilgiler)
                if self.bridge_manager.kernel:
                    return {
                        'success': True,
                        'result': {
                            'available': True,
                            'modules': list(self.bridge_manager.kernel.modules.keys())
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Kernel not available'
                    }
            
            elif action == 'debug_add_module':
                self.logger.debug(f"✅ Entered debug_add_module action")
                module_name = request.get('module_name')
                
                if module_name:
                    success = self.bridge_manager.add_module(module_name)
                    if success:
                        return {
                            'success': True,
                            'result': f"Module {module_name} added"
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"Module {module_name} failed to add"
                        }
                else:
                    return {
                        'success': False,
                        'error': 'Module name required'
                    }
            
            else:
                self.logger.warning(f"Unknown action: {action}")
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
                
        except Exception as e:
            self.logger.error(f"Request processing error: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e)
            }

class BridgeIPCClient:
    """Bridge IPC Client - Uygulama process'lerinde çalışır"""
    
    def __init__(self):
        self.logger = logging.getLogger("BridgeIPCClient")
        self.logger.setLevel(logging.DEBUG)  # Debug loglarını aktif et
        self.app_id = os.environ.get('PYCLOUD_APP_ID', 'unknown')
        
        # Socket yolu - akıllı bulma algoritması
        import tempfile
        import glob
        
        self.socket_path = None
        
        # 1. Önce PYCLOUD_KERNEL_PID ortam değişkenini dene
        kernel_pid = os.environ.get('PYCLOUD_KERNEL_PID')
        if kernel_pid:
            candidate_path = os.path.join(tempfile.gettempdir(), f"pycloud_bridge_{kernel_pid}.sock")
            if os.path.exists(candidate_path):
                self.socket_path = candidate_path
                self.logger.debug(f"Socket found via PYCLOUD_KERNEL_PID: {self.socket_path}")
        
        # 2. Eğer bulunamadıysa, mevcut tüm PyCloud bridge socket'larını ara
        if not self.socket_path:
            pattern = os.path.join(tempfile.gettempdir(), "pycloud_bridge_*.sock")
            socket_files = glob.glob(pattern)
            
            if socket_files:
                # En yeni socket dosyasını kullan (büyük ihtimalle aktif olan)
                self.socket_path = max(socket_files, key=os.path.getctime)
                self.logger.debug(f"Socket found via glob search: {self.socket_path}")
        
        # 3. Hiç bulunamadıysa hata ver
        if not self.socket_path:
            raise RuntimeError(f"PyCloud Bridge socket not found. Searched pattern: {pattern}")
        
        self.logger.info(f"BridgeIPCClient initialized with socket: {self.socket_path}")
    
    def call_module_method(self, module_name: str, method_name: str, *args, **kwargs) -> tuple[bool, Any]:
        """Modül metodunu IPC üzerinden çağır"""
        try:
            import socket
            import json
            
            self.logger.debug(f"IPC call: {module_name}.{method_name}({args}, {kwargs})")
            
            # Socket bağlantısı kur
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.logger.debug(f"Connecting to socket: {self.socket_path}")
            client_socket.connect(self.socket_path)
            
            # İstek gönder
            request = {
                'action': 'call_method',
                'app_id': self.app_id,
                'module_name': module_name,
                'method_name': method_name,
                'args': args,
                'kwargs': kwargs
            }
            
            request_data = json.dumps(request).encode('utf-8')
            self.logger.debug(f"Sending request: {len(request_data)} bytes")
            client_socket.send(request_data)
            
            # Yanıt al
            response_data = client_socket.recv(4096)
            self.logger.debug(f"Received response: {len(response_data)} bytes")
            response = json.loads(response_data.decode('utf-8'))
            
            client_socket.close()
            
            self.logger.debug(f"IPC response: success={response.get('success')}")
            self.logger.debug(f"IPC response content: {response}")
            
            if response.get('success'):
                return True, response.get('result')
            else:
                # Hem 'error' hem 'result' field'larını kontrol et
                error_msg = response.get('error') or response.get('result') or 'Unknown error'
                self.logger.error(f"IPC call failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            self.logger.error(f"IPC call failed: {e}")
            return False, str(e)
    
    def get_module(self, module_name: str):
        """Modül proxy'si al"""
        return BridgeModuleProxy(self, module_name)
    
    def get_kernel_reference(self):
        """Kernel referansı al (proxy)"""
        try:
            import socket
            import json
            
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.connect(self.socket_path)
            
            request = {
                'action': 'get_kernel'
            }
            
            request_data = json.dumps(request).encode('utf-8')
            client_socket.send(request_data)
            
            response_data = client_socket.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            client_socket.close()
            
            if response.get('success'):
                return BridgeKernelProxy(self)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Kernel reference failed: {e}")
            return None

class BridgeModuleProxy:
    """Modül proxy'si - IPC üzerinden modül metodlarını çağırır"""
    
    def __init__(self, ipc_client: BridgeIPCClient, module_name: str):
        self.ipc_client = ipc_client
        self.module_name = module_name
    
    def __getattr__(self, method_name: str):
        """Dinamik metod çağrısı"""
        def method_call(*args, **kwargs):
            success, result = self.ipc_client.call_module_method(
                self.module_name, method_name, *args, **kwargs
            )
            if success:
                return result
            else:
                raise RuntimeError(f"IPC call failed: {result}")
        
        return method_call

class BridgeKernelProxy:
    """Kernel proxy'si - IPC üzerinden kernel'e erişim"""
    
    def __init__(self, ipc_client: BridgeIPCClient):
        self.ipc_client = ipc_client
    
    def get_module(self, module_name: str):
        """Modül al"""
        return self.ipc_client.get_module(module_name) 