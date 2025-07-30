"""
PyCloud OS Clapp Core
.app tabanlı uygulamaları yükleyen, kaldıran, güncelleyen ve listeleyen komut satırı araç seti
"""

import os
import sys
import json
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class CommandResult(Enum):
    """Komut sonuç türleri"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    ALREADY_EXISTS = "already_exists"

class OutputFormat(Enum):
    """Çıktı formatları"""
    TABLE = "table"
    JSON = "json"
    COMPACT = "compact"
    VERBOSE = "verbose"

@dataclass
class ClappCommand:
    """Clapp komut sınıfı"""
    name: str
    description: str
    args: List[str]
    result: CommandResult
    output: str
    timestamp: str
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['result'] = self.result.value
        return data

class ClappCore:
    """Ana Clapp komut işleyici"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("ClappCore")
        
        # Komut geçmişi
        self.command_history: List[ClappCommand] = []
        self.max_history = 100
        
        # Çıktı formatı
        self.output_format = OutputFormat.TABLE
        self.interactive_mode = False
        
        # Komut kayıtları
        self.commands = {
            "install": self._cmd_install,
            "remove": self._cmd_remove,
            "update": self._cmd_update,
            "list": self._cmd_list,
            "search": self._cmd_search,
            "info": self._cmd_info,
            "doctor": self._cmd_doctor,
            "upgrade": self._cmd_upgrade,
            "history": self._cmd_history,
            "help": self._cmd_help
        }
        
        # Alias'lar
        self.aliases = {
            "i": "install",
            "rm": "remove",
            "up": "update",
            "ls": "list",
            "find": "search"
        }
    
    def execute_command(self, command_line: str) -> ClappCommand:
        """Komut satırını çalıştır"""
        start_time = datetime.now()
        
        try:
            # Komut satırını parse et
            args = self._parse_command_line(command_line)
            if not args:
                return self._create_command_result("", CommandResult.ERROR, "Empty command")
            
            command_name = args[0].lower()
            command_args = args[1:]
            
            # Alias kontrolü
            if command_name in self.aliases:
                command_name = self.aliases[command_name]
            
            # Komut var mı?
            if command_name not in self.commands:
                return self._create_command_result(
                    command_name, CommandResult.ERROR, 
                    f"Unknown command: {command_name}. Type 'clapp help' for available commands."
                )
            
            # Komutu çalıştır
            result, output = self.commands[command_name](command_args)
            
            # Komut kaydı oluştur
            execution_time = (datetime.now() - start_time).total_seconds()
            command_record = ClappCommand(
                name=command_name,
                description=f"clapp {command_line}",
                args=command_args,
                result=result,
                output=output,
                timestamp=start_time.isoformat(),
                execution_time=execution_time
            )
            
            # Geçmişe ekle
            self._add_to_history(command_record)
            
            return command_record
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return self._create_command_result(
                command_line, CommandResult.ERROR, f"Command failed: {e}"
            )
    
    def _parse_command_line(self, command_line: str) -> List[str]:
        """Komut satırını parse et"""
        try:
            # Basit split (gelişmiş parsing için shlex kullanılabilir)
            return command_line.strip().split()
        except Exception:
            return []
    
    def _create_command_result(self, command: str, result: CommandResult, output: str) -> ClappCommand:
        """Komut sonucu oluştur"""
        return ClappCommand(
            name=command,
            description=f"clapp {command}",
            args=[],
            result=result,
            output=output,
            timestamp=datetime.now().isoformat()
        )
    
    def _add_to_history(self, command: ClappCommand):
        """Komut geçmişine ekle"""
        self.command_history.append(command)
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def _get_appkit(self):
        """AppKit modülünü al"""
        if self.kernel:
            return self.kernel.get_module("appkit")
        return None
    
    def _get_app_explorer(self):
        """App Explorer modülünü al"""
        if self.kernel:
            return self.kernel.get_module("appexplorer")
        return None
    
    def _get_repo_manager(self):
        """Repository Manager'ı al"""
        try:
            from .repo import get_repository_manager
            return get_repository_manager()
        except ImportError:
            return None
    
    # Komut implementasyonları
    
    def _cmd_install(self, args: List[str]) -> tuple[CommandResult, str]:
        """Uygulama kurulum komutu"""
        try:
            if not args:
                return CommandResult.ERROR, "Usage: clapp install <app_id_or_path>"
            
            target = args[0]
            force = "--force" in args or "-f" in args
            
            appkit = self._get_appkit()
            if not appkit:
                return CommandResult.ERROR, "AppKit not available"
            
            # Yerel dosya/dizin mi yoksa repo'dan mı?
            target_path = Path(target)
            if target_path.exists():
                # Yerel kurulum
                result, message = appkit.install_app(target_path, force=force)
                
                if result.name == "SUCCESS":
                    return CommandResult.SUCCESS, f"✓ {message}"
                else:
                    return CommandResult.ERROR, f"✗ {message}"
            
            else:
                # Repo'dan kurulum
                repo_manager = self._get_repo_manager()
                if not repo_manager:
                    return CommandResult.ERROR, "Repository manager not available"
                
                # Paketi bul
                package = repo_manager.find_package(target)
                if not package:
                    return CommandResult.NOT_FOUND, f"Package not found: {target}"
                
                # İndir ve kur
                download_result = repo_manager.download_package(package)
                if not download_result:
                    return CommandResult.ERROR, f"Failed to download package: {target}"
                
                result, message = appkit.install_app(download_result, force=force)
                
                if result.name == "SUCCESS":
                    return CommandResult.SUCCESS, f"✓ {message}"
                else:
                    return CommandResult.ERROR, f"✗ {message}"
                    
        except Exception as e:
            self.logger.error(f"Install command failed: {e}")
            return CommandResult.ERROR, f"Install failed: {e}"
    
    def _cmd_remove(self, args: List[str]) -> tuple[CommandResult, str]:
        """Uygulama kaldırma komutu"""
        try:
            if not args:
                return CommandResult.ERROR, "Usage: clapp remove <app_id>"
            
            app_id = args[0]
            keep_data = "--keep-data" in args
            
            appkit = self._get_appkit()
            if not appkit:
                return CommandResult.ERROR, "AppKit not available"
            
            # Uygulama kurulu mu?
            if not appkit.is_app_installed(app_id):
                return CommandResult.NOT_FOUND, f"App not installed: {app_id}"
            
            # Kaldır
            result, message = appkit.uninstall_app(app_id, keep_data=keep_data)
            
            if result:
                return CommandResult.SUCCESS, f"✓ {message}"
            else:
                return CommandResult.ERROR, f"✗ {message}"
                
        except Exception as e:
            self.logger.error(f"Remove command failed: {e}")
            return CommandResult.ERROR, f"Remove failed: {e}"
    
    def _cmd_update(self, args: List[str]) -> tuple[CommandResult, str]:
        """Uygulama güncelleme komutu"""
        try:
            if not args:
                return CommandResult.ERROR, "Usage: clapp update <app_id> [source] or clapp update --all"
            
            if args[0] == "--all":
                return self._update_all_apps()
            
            app_id = args[0]
            source = args[1] if len(args) > 1 else None
            
            appkit = self._get_appkit()
            if not appkit:
                return CommandResult.ERROR, "AppKit not available"
            
            # Uygulama kurulu mu?
            if not appkit.is_app_installed(app_id):
                return CommandResult.NOT_FOUND, f"App not installed: {app_id}"
            
            if source:
                # Belirli kaynaktan güncelle
                source_path = Path(source)
                result, message = appkit.update_app(app_id, source_path)
                
                if result.name == "SUCCESS":
                    return CommandResult.SUCCESS, f"✓ {message}"
                else:
                    return CommandResult.ERROR, f"✗ {message}"
            
            else:
                # Repo'dan güncelle
                repo_manager = self._get_repo_manager()
                if not repo_manager:
                    return CommandResult.ERROR, "Repository manager not available"
                
                # Güncel sürümü kontrol et
                package = repo_manager.find_package(app_id)
                if not package:
                    return CommandResult.NOT_FOUND, f"Package not found in repositories: {app_id}"
                
                # Sürüm karşılaştır
                current_app = appkit.get_app_info(app_id)
                if current_app and current_app.metadata.version >= package.version:
                    return CommandResult.INFO, f"App {app_id} is already up to date (v{current_app.metadata.version})"
                
                # İndir ve güncelle
                download_result = repo_manager.download_package(package)
                if not download_result:
                    return CommandResult.ERROR, f"Failed to download update for: {app_id}"
                
                result, message = appkit.update_app(app_id, download_result)
                
                if result.name == "SUCCESS":
                    return CommandResult.SUCCESS, f"✓ {message}"
                else:
                    return CommandResult.ERROR, f"✗ {message}"
                    
        except Exception as e:
            self.logger.error(f"Update command failed: {e}")
            return CommandResult.ERROR, f"Update failed: {e}"
    
    def _update_all_apps(self) -> tuple[CommandResult, str]:
        """Tüm uygulamaları güncelle"""
        try:
            appkit = self._get_appkit()
            repo_manager = self._get_repo_manager()
            
            if not appkit or not repo_manager:
                return CommandResult.ERROR, "Required modules not available"
            
            installed_apps = appkit.get_installed_apps()
            if not installed_apps:
                return CommandResult.INFO, "No apps installed"
            
            updates_available = []
            updated_apps = []
            failed_updates = []
            
            # Güncellemeleri kontrol et
            for app_info in installed_apps:
                package = repo_manager.find_package(app_info.metadata.id)
                if package and package.version > app_info.metadata.version:
                    updates_available.append((app_info, package))
            
            if not updates_available:
                return CommandResult.INFO, "All apps are up to date"
            
            # Güncellemeleri uygula
            for app_info, package in updates_available:
                try:
                    download_result = repo_manager.download_package(package)
                    if download_result:
                        result, message = appkit.update_app(app_info.metadata.id, download_result)
                        if result.name == "SUCCESS":
                            updated_apps.append(app_info.metadata.name)
                        else:
                            failed_updates.append(f"{app_info.metadata.name}: {message}")
                    else:
                        failed_updates.append(f"{app_info.metadata.name}: Download failed")
                        
                except Exception as e:
                    failed_updates.append(f"{app_info.metadata.name}: {e}")
            
            # Sonuç raporu
            output_lines = []
            if updated_apps:
                output_lines.append(f"✓ Updated {len(updated_apps)} apps:")
                for app_name in updated_apps:
                    output_lines.append(f"  - {app_name}")
            
            if failed_updates:
                output_lines.append(f"✗ Failed to update {len(failed_updates)} apps:")
                for failure in failed_updates:
                    output_lines.append(f"  - {failure}")
            
            result_type = CommandResult.SUCCESS if updated_apps else CommandResult.WARNING
            return result_type, "\n".join(output_lines)
            
        except Exception as e:
            self.logger.error(f"Update all failed: {e}")
            return CommandResult.ERROR, f"Update all failed: {e}"
    
    def _cmd_list(self, args: List[str]) -> tuple[CommandResult, str]:
        """Kurulu uygulamaları listele"""
        try:
            appkit = self._get_appkit()
            if not appkit:
                return CommandResult.ERROR, "AppKit not available"
            
            installed_apps = appkit.get_installed_apps()
            if not installed_apps:
                return CommandResult.INFO, "No apps installed"
            
            # Filtreleme
            category_filter = None
            for arg in args:
                if arg.startswith("--category="):
                    category_filter = arg.split("=", 1)[1]
            
            if category_filter:
                installed_apps = [app for app in installed_apps 
                                if app.metadata.category.lower() == category_filter.lower()]
            
            # Format'a göre çıktı
            if self.output_format == OutputFormat.JSON:
                return self._format_apps_json(installed_apps)
            elif self.output_format == OutputFormat.COMPACT:
                return self._format_apps_compact(installed_apps)
            else:
                return self._format_apps_table(installed_apps)
                
        except Exception as e:
            self.logger.error(f"List command failed: {e}")
            return CommandResult.ERROR, f"List failed: {e}"
    
    def _cmd_search(self, args: List[str]) -> tuple[CommandResult, str]:
        """Uygulama ara"""
        try:
            if not args:
                return CommandResult.ERROR, "Usage: clapp search <query>"
            
            query = " ".join(args)
            
            # Hem kurulu uygulamalarda hem repo'da ara
            results = []
            
            # Kurulu uygulamalarda ara
            app_explorer = self._get_app_explorer()
            if app_explorer:
                local_results = app_explorer.search_apps(query)
                for app in local_results:
                    results.append({
                        "id": app.app_id,
                        "name": app.name,
                        "version": app.version,
                        "description": app.description,
                        "category": app.category,
                        "developer": app.developer,
                        "source": "installed"
                    })
            
            # Repo'da ara
            repo_manager = self._get_repo_manager()
            if repo_manager:
                repo_results = repo_manager.search_packages(query)
                for package in repo_results:
                    results.append({
                        "id": package.id,
                        "name": package.name,
                        "version": package.version,
                        "description": package.description,
                        "category": package.category,
                        "developer": package.developer,
                        "source": package.repository_name
                    })
            
            if not results:
                return CommandResult.NOT_FOUND, f"No apps found for query: {query}"
            
            # Sonuçları formatla
            if self.output_format == OutputFormat.JSON:
                return CommandResult.SUCCESS, json.dumps(results, indent=2, ensure_ascii=False)
            else:
                return self._format_search_results(results)
                
        except Exception as e:
            self.logger.error(f"Search command failed: {e}")
            return CommandResult.ERROR, f"Search failed: {e}"
    
    def _cmd_info(self, args: List[str]) -> tuple[CommandResult, str]:
        """Uygulama bilgisi göster"""
        try:
            if not args:
                return CommandResult.ERROR, "Usage: clapp info <app_id>"
            
            app_id = args[0]
            
            # Önce kurulu uygulamalarda ara
            appkit = self._get_appkit()
            if appkit:
                app_info = appkit.get_app_info(app_id)
                if app_info:
                    return self._format_app_info(app_info, installed=True)
            
            # Repo'da ara
            repo_manager = self._get_repo_manager()
            if repo_manager:
                package = repo_manager.find_package(app_id)
                if package:
                    return self._format_package_info(package)
            
            return CommandResult.NOT_FOUND, f"App not found: {app_id}"
            
        except Exception as e:
            self.logger.error(f"Info command failed: {e}")
            return CommandResult.ERROR, f"Info failed: {e}"
    
    def _cmd_doctor(self, args: List[str]) -> tuple[CommandResult, str]:
        """Sistem sağlık kontrolü"""
        try:
            issues = []
            warnings = []
            
            # AppKit kontrolü
            appkit = self._get_appkit()
            if not appkit:
                issues.append("AppKit module not available")
            else:
                # Kurulu uygulamaları kontrol et
                installed_apps = appkit.get_installed_apps()
                for app_info in installed_apps:
                    app_path = Path(app_info.install_path)
                    
                    # Uygulama dizini var mı?
                    if not app_path.exists():
                        issues.append(f"App directory missing: {app_info.metadata.name} ({app_info.metadata.id})")
                    
                    # app.json var mı?
                    elif not (app_path / "app.json").exists():
                        issues.append(f"app.json missing: {app_info.metadata.name}")
                    
                    # Entry dosyası var mı?
                    elif not (app_path / app_info.metadata.entry).exists():
                        issues.append(f"Entry file missing: {app_info.metadata.name}")
                    
                    # İkon var mı?
                    elif not (app_path / app_info.metadata.icon).exists():
                        warnings.append(f"Icon missing: {app_info.metadata.name}")
            
            # Repository kontrolü
            repo_manager = self._get_repo_manager()
            if not repo_manager:
                warnings.append("Repository manager not available")
            else:
                # Repo bağlantılarını kontrol et
                repos = repo_manager.get_repositories()
                for repo in repos:
                    if not repo_manager.test_repository_connection(repo):
                        warnings.append(f"Repository unreachable: {repo.name}")
            
            # Python kontrolü
            try:
                result = subprocess.run(["python3", "--version"], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    issues.append("Python3 not found or not working")
            except FileNotFoundError:
                issues.append("Python3 not found in PATH")
            
            # Sonuç raporu
            output_lines = []
            
            if not issues and not warnings:
                output_lines.append("✓ System health check passed - no issues found")
                return CommandResult.SUCCESS, "\n".join(output_lines)
            
            if issues:
                output_lines.append(f"✗ Found {len(issues)} critical issues:")
                for issue in issues:
                    output_lines.append(f"  - {issue}")
            
            if warnings:
                output_lines.append(f"⚠ Found {len(warnings)} warnings:")
                for warning in warnings:
                    output_lines.append(f"  - {warning}")
            
            result_type = CommandResult.ERROR if issues else CommandResult.WARNING
            return result_type, "\n".join(output_lines)
            
        except Exception as e:
            self.logger.error(f"Doctor command failed: {e}")
            return CommandResult.ERROR, f"Doctor failed: {e}"
    
    def _cmd_upgrade(self, args: List[str]) -> tuple[CommandResult, str]:
        """Sistem genelinde güncelleme denetimi"""
        try:
            # Repository listelerini güncelle
            repo_manager = self._get_repo_manager()
            if repo_manager:
                repo_manager.refresh_repositories()
            
            # Güncellemeleri kontrol et
            return self._update_all_apps()
            
        except Exception as e:
            self.logger.error(f"Upgrade command failed: {e}")
            return CommandResult.ERROR, f"Upgrade failed: {e}"
    
    def _cmd_history(self, args: List[str]) -> tuple[CommandResult, str]:
        """Komut geçmişini göster"""
        try:
            limit = 10
            
            # Limit parametresi
            for arg in args:
                if arg.startswith("--limit="):
                    try:
                        limit = int(arg.split("=", 1)[1])
                    except ValueError:
                        pass
            
            if not self.command_history:
                return CommandResult.INFO, "No command history"
            
            recent_commands = self.command_history[-limit:]
            
            output_lines = [f"Recent {len(recent_commands)} commands:"]
            for i, cmd in enumerate(recent_commands, 1):
                status_icon = "✓" if cmd.result == CommandResult.SUCCESS else "✗"
                timestamp = datetime.fromisoformat(cmd.timestamp).strftime("%H:%M:%S")
                output_lines.append(f"{i:2d}. {status_icon} [{timestamp}] {cmd.description}")
            
            return CommandResult.SUCCESS, "\n".join(output_lines)
            
        except Exception as e:
            self.logger.error(f"History command failed: {e}")
            return CommandResult.ERROR, f"History failed: {e}"
    
    def _cmd_help(self, args: List[str]) -> tuple[CommandResult, str]:
        """Yardım göster"""
        help_text = """
PyCloud OS Clapp - Application Package Manager

USAGE:
    clapp <command> [options] [arguments]

COMMANDS:
    install <app_id_or_path>    Install an application
    remove <app_id>             Remove an application  
    update <app_id>             Update an application
    update --all                Update all applications
    list                        List installed applications
    search <query>              Search for applications
    info <app_id>               Show application information
    doctor                      Check system health
    upgrade                     System-wide update check
    history                     Show command history
    help                        Show this help

OPTIONS:
    --force, -f                 Force operation
    --keep-data                 Keep user data when removing
    --category=<name>           Filter by category
    --limit=<number>            Limit number of results
    --json                      Output in JSON format
    --compact                   Compact output format
    --interactive               Interactive mode

EXAMPLES:
    clapp install textpad
    clapp install /path/to/app.zip
    clapp remove textpad --keep-data
    clapp update --all
    clapp list --category=Development
    clapp search "text editor"
    clapp info textpad
    clapp doctor

For more information, visit: https://pycloudos.dev/docs/clapp
        """
        
        return CommandResult.SUCCESS, help_text.strip()
    
    # Formatters
    
    def _format_apps_table(self, apps) -> tuple[CommandResult, str]:
        """Uygulamaları tablo formatında göster"""
        if not apps:
            return CommandResult.INFO, "No apps to display"
        
        # Başlık
        lines = []
        lines.append("ID".ljust(20) + "NAME".ljust(25) + "VERSION".ljust(10) + "CATEGORY".ljust(15) + "SIZE")
        lines.append("-" * 80)
        
        # Uygulamalar
        for app in apps:
            size_str = f"{app.install_size_mb:.1f}MB" if hasattr(app, 'install_size_mb') else "N/A"
            lines.append(
                app.metadata.id[:19].ljust(20) +
                app.metadata.name[:24].ljust(25) +
                app.metadata.version[:9].ljust(10) +
                app.metadata.category[:14].ljust(15) +
                size_str
            )
        
        lines.append(f"\nTotal: {len(apps)} apps")
        
        return CommandResult.SUCCESS, "\n".join(lines)
    
    def _format_apps_compact(self, apps) -> tuple[CommandResult, str]:
        """Uygulamaları kompakt formatında göster"""
        if not apps:
            return CommandResult.INFO, "No apps to display"
        
        lines = []
        for app in apps:
            lines.append(f"{app.metadata.id} ({app.metadata.version}) - {app.metadata.name}")
        
        return CommandResult.SUCCESS, "\n".join(lines)
    
    def _format_apps_json(self, apps) -> tuple[CommandResult, str]:
        """Uygulamaları JSON formatında göster"""
        app_data = []
        for app in apps:
            app_data.append({
                "id": app.metadata.id,
                "name": app.metadata.name,
                "version": app.metadata.version,
                "description": app.metadata.description,
                "category": app.metadata.category,
                "developer": app.metadata.developer,
                "install_size_mb": getattr(app, 'install_size_mb', 0),
                "installed_at": getattr(app, 'installed_at', ''),
                "status": app.status.value if hasattr(app, 'status') else 'installed'
            })
        
        return CommandResult.SUCCESS, json.dumps(app_data, indent=2, ensure_ascii=False)
    
    def _format_search_results(self, results) -> tuple[CommandResult, str]:
        """Arama sonuçlarını formatla"""
        lines = []
        lines.append("ID".ljust(20) + "NAME".ljust(25) + "VERSION".ljust(10) + "SOURCE".ljust(15) + "DESCRIPTION")
        lines.append("-" * 90)
        
        for result in results:
            lines.append(
                result["id"][:19].ljust(20) +
                result["name"][:24].ljust(25) +
                result["version"][:9].ljust(10) +
                result["source"][:14].ljust(15) +
                result["description"][:40]
            )
        
        lines.append(f"\nFound: {len(results)} results")
        
        return CommandResult.SUCCESS, "\n".join(lines)
    
    def _format_app_info(self, app_info, installed=True) -> tuple[CommandResult, str]:
        """Uygulama bilgisini formatla"""
        lines = []
        lines.append(f"Application: {app_info.metadata.name}")
        lines.append(f"ID: {app_info.metadata.id}")
        lines.append(f"Version: {app_info.metadata.version}")
        lines.append(f"Description: {app_info.metadata.description}")
        lines.append(f"Category: {app_info.metadata.category}")
        lines.append(f"Developer: {app_info.metadata.developer}")
        lines.append(f"License: {app_info.metadata.license}")
        
        if installed:
            lines.append(f"Status: Installed")
            lines.append(f"Install Path: {app_info.install_path}")
            lines.append(f"Install Size: {app_info.install_size_mb:.1f}MB")
            lines.append(f"Installed At: {app_info.installed_at}")
            if app_info.updated_at:
                lines.append(f"Updated At: {app_info.updated_at}")
        
        if app_info.metadata.tags:
            lines.append(f"Tags: {', '.join(app_info.metadata.tags)}")
        
        if app_info.metadata.homepage:
            lines.append(f"Homepage: {app_info.metadata.homepage}")
        
        return CommandResult.SUCCESS, "\n".join(lines)
    
    def _format_package_info(self, package) -> tuple[CommandResult, str]:
        """Paket bilgisini formatla"""
        lines = []
        lines.append(f"Package: {package.name}")
        lines.append(f"ID: {package.id}")
        lines.append(f"Version: {package.version}")
        lines.append(f"Description: {package.description}")
        lines.append(f"Category: {package.category}")
        lines.append(f"Developer: {package.developer}")
        lines.append(f"Repository: {package.repository_name}")
        lines.append(f"Status: Available for install")
        
        if hasattr(package, 'tags') and package.tags:
            lines.append(f"Tags: {', '.join(package.tags)}")
        
        if hasattr(package, 'homepage') and package.homepage:
            lines.append(f"Homepage: {package.homepage}")
        
        return CommandResult.SUCCESS, "\n".join(lines)
    
    def set_output_format(self, format_type: OutputFormat):
        """Çıktı formatını ayarla"""
        self.output_format = format_type
    
    def set_interactive_mode(self, enabled: bool):
        """Etkileşimli modu ayarla"""
        self.interactive_mode = enabled
    
    def get_command_history(self) -> List[ClappCommand]:
        """Komut geçmişini al"""
        return self.command_history.copy()
    
    def clear_history(self):
        """Komut geçmişini temizle"""
        self.command_history.clear()

# CLI Interface
def main():
    """Ana CLI fonksiyonu"""
    parser = argparse.ArgumentParser(
        prog="clapp",
        description="PyCloud OS Application Package Manager"
    )
    
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--compact", action="store_true", help="Compact output")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Logging ayarla
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    
    # Clapp Core oluştur
    clapp = ClappCore()
    
    # Çıktı formatını ayarla
    if args.json:
        clapp.set_output_format(OutputFormat.JSON)
    elif args.compact:
        clapp.set_output_format(OutputFormat.COMPACT)
    
    # Etkileşimli mod
    if args.interactive:
        clapp.set_interactive_mode(True)
        interactive_mode(clapp)
        return
    
    # Tek komut çalıştır
    if not args.command:
        args.command = "help"
    
    command_line = " ".join([args.command] + args.args)
    result = clapp.execute_command(command_line)
    
    # Sonucu yazdır
    print(result.output)
    
    # Exit code
    if result.result == CommandResult.SUCCESS:
        sys.exit(0)
    elif result.result == CommandResult.WARNING:
        sys.exit(1)
    else:
        sys.exit(2)

def interactive_mode(clapp: ClappCore):
    """Etkileşimli mod"""
    print("PyCloud OS Clapp Interactive Mode")
    print("Type 'help' for commands, 'exit' to quit")
    
    while True:
        try:
            command_line = input("clapp> ").strip()
            
            if command_line.lower() in ["exit", "quit"]:
                break
            
            if not command_line:
                continue
            
            result = clapp.execute_command(command_line)
            print(result.output)
            
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            break

if __name__ == "__main__":
    main() 