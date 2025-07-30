"""
Cloud PyIDE - Eklenti Sistemi
.plug formatında eklenti yönetimi
"""

import os
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class PluginInfo:
    """Eklenti bilgisi"""
    id: str
    name: str
    version: str
    description: str
    author: str
    main_file: str
    enabled: bool = True
    dependencies: List[str] = None

class PluginManager:
    """Eklenti yöneticisi"""
    
    def __init__(self, ide_instance=None):
        self.ide_instance = ide_instance
        self.logger = logging.getLogger("PluginManager")
        
        # Eklenti dizini
        self.plugins_dir = Path("plugins")
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Yüklü eklentiler
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_modules: Dict[str, Any] = {}
        
        # Yükle
        self.load_plugins()
    
    def load_plugins(self):
        """Eklentileri yükle"""
        try:
            # .plug dosyalarını tara
            for plugin_file in self.plugins_dir.glob("*.plug"):
                self.load_plugin_from_file(plugin_file)
            
            self.logger.info(f"Loaded {len(self.plugins)} plugins")
            
        except Exception as e:
            self.logger.error(f"Error loading plugins: {e}")
    
    def load_plugin_from_file(self, plugin_file: Path) -> bool:
        """Dosyadan eklenti yükle"""
        try:
            # .plug dosyası aslında bir JSON dosyası
            with open(plugin_file, 'r', encoding='utf-8') as f:
                plugin_data = json.load(f)
            
            # Plugin bilgisini oluştur
            plugin_info = PluginInfo(
                id=plugin_data.get('id', plugin_file.stem),
                name=plugin_data.get('name', plugin_file.stem),
                version=plugin_data.get('version', '1.0.0'),
                description=plugin_data.get('description', ''),
                author=plugin_data.get('author', 'Unknown'),
                main_file=plugin_data.get('main_file', 'main.py'),
                enabled=plugin_data.get('enabled', True),
                dependencies=plugin_data.get('dependencies', [])
            )
            
            # Plugin dizinini kontrol et
            plugin_dir = self.plugins_dir / plugin_info.id
            if not plugin_dir.exists():
                self.logger.warning(f"Plugin directory not found: {plugin_dir}")
                return False
            
            # Ana dosyayı kontrol et
            main_file_path = plugin_dir / plugin_info.main_file
            if not main_file_path.exists():
                self.logger.warning(f"Plugin main file not found: {main_file_path}")
                return False
            
            # Eklentiyi kaydet
            self.plugins[plugin_info.id] = plugin_info
            
            # Etkinse yükle
            if plugin_info.enabled:
                self.load_plugin_module(plugin_info)
            
            self.logger.info(f"Loaded plugin: {plugin_info.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading plugin from {plugin_file}: {e}")
            return False
    
    def load_plugin_module(self, plugin_info: PluginInfo) -> bool:
        """Eklenti modülünü yükle"""
        try:
            plugin_dir = self.plugins_dir / plugin_info.id
            main_file_path = plugin_dir / plugin_info.main_file
            
            # Modül spec oluştur
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_info.id}",
                main_file_path
            )
            
            if spec is None or spec.loader is None:
                self.logger.error(f"Cannot create spec for plugin: {plugin_info.id}")
                return False
            
            # Modülü yükle
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Plugin'i başlat
            if hasattr(module, 'initialize'):
                module.initialize(self.ide_instance)
            
            # Modülü kaydet
            self.loaded_modules[plugin_info.id] = module
            
            self.logger.info(f"Loaded plugin module: {plugin_info.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading plugin module {plugin_info.id}: {e}")
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Eklentiyi kaldır"""
        try:
            if plugin_id not in self.plugins:
                self.logger.warning(f"Plugin not found: {plugin_id}")
                return False
            
            # Modülü kaldır
            if plugin_id in self.loaded_modules:
                module = self.loaded_modules[plugin_id]
                
                # Cleanup fonksiyonu varsa çağır
                if hasattr(module, 'cleanup'):
                    module.cleanup()
                
                del self.loaded_modules[plugin_id]
            
            # Plugin bilgisini güncelle
            self.plugins[plugin_id].enabled = False
            
            self.logger.info(f"Unloaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Eklentiyi etkinleştir"""
        try:
            if plugin_id not in self.plugins:
                return False
            
            plugin_info = self.plugins[plugin_id]
            
            if plugin_info.enabled:
                return True
            
            # Modülü yükle
            if self.load_plugin_module(plugin_info):
                plugin_info.enabled = True
                self.save_plugin_config(plugin_info)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error enabling plugin {plugin_id}: {e}")
            return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Eklentiyi devre dışı bırak"""
        try:
            if plugin_id not in self.plugins:
                return False
            
            plugin_info = self.plugins[plugin_id]
            
            if not plugin_info.enabled:
                return True
            
            # Modülü kaldır
            if self.unload_plugin(plugin_id):
                plugin_info.enabled = False
                self.save_plugin_config(plugin_info)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error disabling plugin {plugin_id}: {e}")
            return False
    
    def save_plugin_config(self, plugin_info: PluginInfo):
        """Eklenti yapılandırmasını kaydet"""
        try:
            plugin_file = self.plugins_dir / f"{plugin_info.id}.plug"
            
            plugin_data = {
                'id': plugin_info.id,
                'name': plugin_info.name,
                'version': plugin_info.version,
                'description': plugin_info.description,
                'author': plugin_info.author,
                'main_file': plugin_info.main_file,
                'enabled': plugin_info.enabled,
                'dependencies': plugin_info.dependencies or []
            }
            
            with open(plugin_file, 'w', encoding='utf-8') as f:
                json.dump(plugin_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving plugin config: {e}")
    
    def install_plugin(self, plugin_path: str) -> bool:
        """Eklenti kur"""
        try:
            plugin_path = Path(plugin_path)
            
            if not plugin_path.exists():
                self.logger.error(f"Plugin path not found: {plugin_path}")
                return False
            
            if plugin_path.is_file() and plugin_path.suffix == '.zip':
                # ZIP dosyasından kur
                return self.install_from_zip(plugin_path)
            elif plugin_path.is_dir():
                # Dizinden kur
                return self.install_from_directory(plugin_path)
            else:
                self.logger.error(f"Invalid plugin format: {plugin_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing plugin: {e}")
            return False
    
    def install_from_zip(self, zip_path: Path) -> bool:
        """ZIP dosyasından eklenti kur"""
        try:
            import zipfile
            import tempfile
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # ZIP'i çıkar
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Çıkarılan dizini kur
                extracted_dir = Path(temp_dir)
                
                # Ana dizini bul
                subdirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
                if len(subdirs) == 1:
                    plugin_dir = subdirs[0]
                else:
                    plugin_dir = extracted_dir
                
                return self.install_from_directory(plugin_dir)
                
        except Exception as e:
            self.logger.error(f"Error installing from ZIP: {e}")
            return False
    
    def install_from_directory(self, source_dir: Path) -> bool:
        """Dizinden eklenti kur"""
        try:
            import shutil
            
            # Plugin.json dosyasını kontrol et
            plugin_json = source_dir / "plugin.json"
            if not plugin_json.exists():
                self.logger.error(f"plugin.json not found in {source_dir}")
                return False
            
            # Plugin bilgisini oku
            with open(plugin_json, 'r', encoding='utf-8') as f:
                plugin_data = json.load(f)
            
            plugin_id = plugin_data.get('id')
            if not plugin_id:
                self.logger.error("Plugin ID not found in plugin.json")
                return False
            
            # Hedef dizini oluştur
            target_dir = self.plugins_dir / plugin_id
            
            if target_dir.exists():
                self.logger.warning(f"Plugin already exists: {plugin_id}")
                shutil.rmtree(target_dir)
            
            # Dosyaları kopyala
            shutil.copytree(source_dir, target_dir)
            
            # .plug dosyası oluştur
            plug_file = self.plugins_dir / f"{plugin_id}.plug"
            with open(plug_file, 'w', encoding='utf-8') as f:
                json.dump(plugin_data, f, indent=2, ensure_ascii=False)
            
            # Eklentiyi yükle
            self.load_plugin_from_file(plug_file)
            
            self.logger.info(f"Installed plugin: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing from directory: {e}")
            return False
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Eklentiyi kaldır"""
        try:
            if plugin_id not in self.plugins:
                self.logger.warning(f"Plugin not found: {plugin_id}")
                return False
            
            # Önce devre dışı bırak
            self.disable_plugin(plugin_id)
            
            # Dosyaları sil
            plugin_dir = self.plugins_dir / plugin_id
            if plugin_dir.exists():
                import shutil
                shutil.rmtree(plugin_dir)
            
            # .plug dosyasını sil
            plug_file = self.plugins_dir / f"{plugin_id}.plug"
            if plug_file.exists():
                plug_file.unlink()
            
            # Listeden kaldır
            del self.plugins[plugin_id]
            
            self.logger.info(f"Uninstalled plugin: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
            return False
    
    def get_available_plugins(self) -> List[PluginInfo]:
        """Mevcut eklentileri al"""
        return list(self.plugins.values())
    
    def get_enabled_plugins(self) -> List[PluginInfo]:
        """Etkin eklentileri al"""
        return [plugin for plugin in self.plugins.values() if plugin.enabled]
    
    def get_plugin_info(self, plugin_id: str) -> Optional[PluginInfo]:
        """Eklenti bilgisini al"""
        return self.plugins.get(plugin_id)
    
    def call_plugin_method(self, plugin_id: str, method_name: str, *args, **kwargs) -> Any:
        """Eklenti metodunu çağır"""
        try:
            if plugin_id not in self.loaded_modules:
                self.logger.warning(f"Plugin not loaded: {plugin_id}")
                return None
            
            module = self.loaded_modules[plugin_id]
            
            if not hasattr(module, method_name):
                self.logger.warning(f"Method not found in plugin {plugin_id}: {method_name}")
                return None
            
            method = getattr(module, method_name)
            return method(*args, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Error calling plugin method {plugin_id}.{method_name}: {e}")
            return None 