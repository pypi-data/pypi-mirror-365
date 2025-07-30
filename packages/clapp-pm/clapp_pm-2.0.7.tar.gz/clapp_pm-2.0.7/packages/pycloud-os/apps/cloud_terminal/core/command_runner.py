"""
Cloud Terminal - Komut Çalıştırıcı
Sistem komutları, PyCloud entegrasyonu ve komut işleme
"""

import os
import sys
import json
import subprocess
import shutil
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class CommandResult:
    """Komut sonucu"""
    
    def __init__(self, output: str = "", error: str = "", return_code: int = 0, **kwargs):
        self.output = output
        self.error = error
        self.return_code = return_code
        self.extra = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict'e çevir"""
        result = {
            'output': self.output,
            'error': self.error,
            'return_code': self.return_code
        }
        result.update(self.extra)
        return result

class CommandRunner:
    """Modern komut çalıştırıcı"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        
        # Komut kategorileri (.cursorrules uyumlu)
        self.system_commands = {
            'help': self.cmd_help,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'version': self.cmd_version,
            'uptime': self.cmd_uptime,
            'date': self.cmd_date,
            'whoami': self.cmd_whoami,
        }
        
        self.file_commands = {
            'pwd': self.cmd_pwd,
            'cd': self.cmd_cd,
            'ls': self.cmd_ls,
            'dir': self.cmd_ls,  # Windows alias
            'cat': self.cmd_cat,
            'head': self.cmd_head,
            'tail': self.cmd_tail,
            'find': self.cmd_find,
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'rm': self.cmd_rm,
            'cp': self.cmd_cp,
            'mv': self.cmd_mv,
            'touch': self.cmd_touch,
        }
        
        self.process_commands = {
            'ps': self.cmd_ps,
            'kill': self.cmd_kill,
            'killall': self.cmd_killall,
            'top': self.cmd_top,
            'mem': self.cmd_mem,
            'thread': self.cmd_thread,
        }
        
        self.user_commands = {
            'users': self.cmd_users,
            'su': self.cmd_su,
            'profile': self.cmd_profile,
        }
        
        self.developer_commands = {
            'clapp': self.cmd_clapp,
            'pycloud': self.cmd_pycloud,
            'python': self.cmd_python,
            'python3': self.cmd_python,
            'pip': self.cmd_pip,
            'git': self.cmd_git,
            'notify': self.cmd_notify,
            'fs': self.cmd_fs,
        }
        
        # Tüm komutları birleştir
        self.all_commands = {}
        self.all_commands.update(self.system_commands)
        self.all_commands.update(self.file_commands)
        self.all_commands.update(self.process_commands)
        self.all_commands.update(self.user_commands)
        self.all_commands.update(self.developer_commands)
    
    def execute_command(self, command: str, current_dir: str) -> Dict[str, Any]:
        """Ana komut çalıştırıcı"""
        try:
            parts = command.strip().split()
            if not parts:
                return CommandResult().to_dict()
            
            cmd_name = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Dizin değiştir
            original_dir = os.getcwd()
            try:
                os.chdir(current_dir)
                
                # Yerleşik komutlar
                if cmd_name in self.all_commands:
                    result = self.all_commands[cmd_name](args, current_dir)
                    if isinstance(result, CommandResult):
                        return result.to_dict()
                    return result
                
                # Harici komutlar
                return self._execute_external(parts, current_dir)
                
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            return CommandResult(
                error=f"Command execution error: {e}",
                return_code=1
            ).to_dict()
    
    def get_command_categories(self) -> Dict[str, List[str]]:
        """Komut kategorilerini al (.cursorrules uyumlu)"""
        return {
            'sistem': list(self.system_commands.keys()),
            'dosya': list(self.file_commands.keys()),
            'kullanıcı': list(self.user_commands.keys()),
            'geliştirici': list(self.developer_commands.keys())
        }
    
    def get_all_commands(self) -> List[str]:
        """Tüm komutları al"""
        return list(self.all_commands.keys())
    
    # Sistem komutları
    def cmd_help(self, args: List[str], current_dir: str) -> CommandResult:
        """Yardım komutu"""
        if args:
            # Belirli komut hakkında yardım
            cmd = args[0].lower()
            if cmd in self.all_commands:
                help_text = self._get_command_help(cmd)
            else:
                help_text = f"Unknown command: {cmd}"
        else:
            # Genel yardım
            help_text = self._get_general_help()
        
        return CommandResult(output=help_text)
    
    def cmd_clear(self, args: List[str], current_dir: str) -> CommandResult:
        """Ekranı temizle"""
        return CommandResult(clear=True)
    
    def cmd_exit(self, args: List[str], current_dir: str) -> CommandResult:
        """Terminal'den çık"""
        return CommandResult(output="Goodbye!", exit=True)
    
    def cmd_version(self, args: List[str], current_dir: str) -> CommandResult:
        """Sürüm bilgisi"""
        version_info = """
Cloud Terminal v2.0.0
PyCloud OS Terminal Application

Built with:
- Python 3.x
- PyQt6
- Modern UI Framework

© 2024 PyCloud OS Team
"""
        return CommandResult(output=version_info)
    
    def cmd_uptime(self, args: List[str], current_dir: str) -> CommandResult:
        """Sistem çalışma süresi"""
        if PSUTIL_AVAILABLE:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_str = self._format_uptime(uptime_seconds)
        else:
            uptime_str = "Uptime information not available"
        
        return CommandResult(output=f"System uptime: {uptime_str}")
    
    def cmd_date(self, args: List[str], current_dir: str) -> CommandResult:
        """Tarih ve saat"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S %A")
        return CommandResult(output=date_str)
    
    def cmd_whoami(self, args: List[str], current_dir: str) -> CommandResult:
        """Mevcut kullanıcı"""
        try:
            import getpass
            username = getpass.getuser()
        except:
            username = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        
        return CommandResult(output=username)
    
    # Dosya komutları
    def cmd_pwd(self, args: List[str], current_dir: str) -> CommandResult:
        """Mevcut dizin"""
        return CommandResult(output=current_dir)
    
    def cmd_cd(self, args: List[str], current_dir: str) -> CommandResult:
        """Dizin değiştir"""
        if not args:
            target_dir = str(Path.home())
        else:
            target_dir = args[0]
        
        try:
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(current_dir, target_dir)
            
            target_dir = os.path.abspath(target_dir)
            
            if os.path.exists(target_dir) and os.path.isdir(target_dir):
                return CommandResult(new_directory=target_dir)
            else:
                return CommandResult(
                    error=f"Directory not found: {target_dir}",
                    return_code=1
                )
                
        except Exception as e:
            return CommandResult(
                error=f"Failed to change directory: {e}",
                return_code=1
            )
    
    def cmd_ls(self, args: List[str], current_dir: str) -> CommandResult:
        """Dosyaları listele"""
        try:
            target_dir = args[0] if args else current_dir
            
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(current_dir, target_dir)
            
            if not os.path.exists(target_dir):
                return CommandResult(
                    error=f"Directory not found: {target_dir}",
                    return_code=1
                )
            
            # Detaylı listeleme seçeneği
            detailed = '-l' in args or '--long' in args
            show_hidden = '-a' in args or '--all' in args
            
            items = []
            for item in sorted(os.listdir(target_dir)):
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(target_dir, item)
                
                if detailed:
                    # Detaylı bilgi
                    stat = os.stat(item_path)
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    
                    if os.path.isdir(item_path):
                        items.append(f"drwxr-xr-x  {size:>8}  {mtime}  📁 {item}/")
                    else:
                        size_str = self._format_size(size)
                        items.append(f"-rw-r--r--  {size_str:>8}  {mtime}  📄 {item}")
                else:
                    # Basit listeleme
                    if os.path.isdir(item_path):
                        items.append(f"📁 {item}/")
                    else:
                        items.append(f"📄 {item}")
            
            return CommandResult(output="\n".join(items))
            
        except Exception as e:
            return CommandResult(
                error=f"Failed to list directory: {e}",
                return_code=1
            )
    
    def cmd_cat(self, args: List[str], current_dir: str) -> CommandResult:
        """Dosya içeriğini göster"""
        if not args:
            return CommandResult(
                error="Usage: cat <file>",
                return_code=1
            )
        
        try:
            file_path = args[0]
            if not os.path.isabs(file_path):
                file_path = os.path.join(current_dir, file_path)
            
            if not os.path.exists(file_path):
                return CommandResult(
                    error=f"File not found: {file_path}",
                    return_code=1
                )
            
            if os.path.isdir(file_path):
                return CommandResult(
                    error=f"Is a directory: {file_path}",
                    return_code=1
                )
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return CommandResult(output=content)
            
        except Exception as e:
            return CommandResult(
                error=f"Failed to read file: {e}",
                return_code=1
            )
    
    def cmd_mkdir(self, args: List[str], current_dir: str) -> CommandResult:
        """Dizin oluştur"""
        if not args:
            return CommandResult(
                error="Usage: mkdir <directory>",
                return_code=1
            )
        
        try:
            for dir_name in args:
                if not os.path.isabs(dir_name):
                    dir_path = os.path.join(current_dir, dir_name)
                else:
                    dir_path = dir_name
                
                os.makedirs(dir_path, exist_ok=True)
            
            return CommandResult(output=f"Created {len(args)} director{'y' if len(args) == 1 else 'ies'}")
            
        except Exception as e:
            return CommandResult(
                error=f"Failed to create directory: {e}",
                return_code=1
            )
    
    def cmd_touch(self, args: List[str], current_dir: str) -> CommandResult:
        """Dosya oluştur/güncelle"""
        if not args:
            return CommandResult(
                error="Usage: touch <file>",
                return_code=1
            )
        
        try:
            for file_name in args:
                if not os.path.isabs(file_name):
                    file_path = os.path.join(current_dir, file_name)
                else:
                    file_path = file_name
                
                # Dosya yoksa oluştur
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        pass
                else:
                    # Zaman damgasını güncelle
                    os.utime(file_path, None)
            
            return CommandResult(output=f"Touched {len(args)} file{'s' if len(args) != 1 else ''}")
            
        except Exception as e:
            return CommandResult(
                error=f"Failed to touch file: {e}",
                return_code=1
            )
    
    # İşlem komutları
    def cmd_ps(self, args: List[str], current_dir: str) -> CommandResult:
        """Çalışan işlemleri göster"""
        if not PSUTIL_AVAILABLE:
            return CommandResult(
                error="Process information not available (psutil required)",
                return_code=1
            )
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'] or 'Unknown',
                        'cpu': info['cpu_percent'] or 0.0,
                        'memory': info['memory_percent'] or 0.0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # CPU kullanımına göre sırala
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            
            # Başlık
            output = f"{'PID':>8} {'NAME':<20} {'CPU%':>8} {'MEM%':>8}\n"
            output += "-" * 50 + "\n"
            
            # İlk 20 işlem
            for proc in processes[:20]:
                output += f"{proc['pid']:>8} {proc['name']:<20} {proc['cpu']:>7.1f} {proc['memory']:>7.1f}\n"
            
            return CommandResult(output=output)
            
        except Exception as e:
            return CommandResult(
                error=f"Failed to get process list: {e}",
                return_code=1
            )
    
    def cmd_mem(self, args: List[str], current_dir: str) -> CommandResult:
        """Bellek kullanımı"""
        if not PSUTIL_AVAILABLE:
            return CommandResult(
                error="Memory information not available (psutil required)",
                return_code=1
            )
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            output = f"""Memory Usage:
Total:     {self._format_size(memory.total)}
Available: {self._format_size(memory.available)}
Used:      {self._format_size(memory.used)} ({memory.percent:.1f}%)
Free:      {self._format_size(memory.free)}

Swap Usage:
Total:     {self._format_size(swap.total)}
Used:      {self._format_size(swap.used)} ({swap.percent:.1f}%)
Free:      {self._format_size(swap.free)}
"""
            return CommandResult(output=output)
            
        except Exception as e:
            return CommandResult(
                error=f"Failed to get memory info: {e}",
                return_code=1
            )
    
    # PyCloud komutları
    def cmd_clapp(self, args: List[str], current_dir: str) -> CommandResult:
        """Clapp paket yöneticisi - Gerçek Clapp Core entegrasyonu"""
        try:
            # Clapp Core modülünü import et
            import sys
            import os
            
            # PyOS root dizinini sys.path'e ekle
            pyos_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            if pyos_root not in sys.path:
                sys.path.insert(0, pyos_root)
            
            from clapp.core import ClappCore
            
            # Clapp Core instance oluştur
            clapp_core = ClappCore(self.kernel)
            
            if not args:
                return CommandResult(
                    error="Usage: clapp <list|install|remove|update|search|info|doctor|help> [args]",
                    return_code=1
                )
            
            # Komut satırını oluştur
            command_line = " ".join(args)
            
            # Clapp Core ile komutu çalıştır
            result = clapp_core.execute_command(command_line)
            
            # Sonucu CommandResult formatına çevir
            if result.result.value == "success":
                return CommandResult(output=result.output, return_code=0)
            elif result.result.value in ["warning", "info"]:
                return CommandResult(output=result.output, return_code=0)
            else:
                return CommandResult(error=result.output, return_code=1)
                
        except ImportError as e:
            # Fallback: Clapp Core mevcut değilse basit implementasyon
            return self._clapp_fallback(args)
        except Exception as e:
            return CommandResult(error=f"Clapp error: {e}", return_code=1)
    
    def _clapp_fallback(self, args: List[str]) -> CommandResult:
        """Clapp Core mevcut değilse fallback implementasyon"""
        if not args:
            return CommandResult(
                error="Usage: clapp <list|help>",
                return_code=1
            )
        
        action = args[0].lower()
        
        if action == "list":
            return self._clapp_list()
        elif action == "help":
            help_text = """
Clapp Package Manager - Fallback Mode

Available commands:
  list                    - List installed apps
  
Note: Install Clapp Core module for full functionality.
"""
            return CommandResult(output=help_text.strip())
        else:
            return CommandResult(
                error=f"Clapp Core not available. Only 'list' and 'help' commands available. Command: {action}",
                return_code=1
            )
    
    def cmd_pycloud(self, args: List[str], current_dir: str) -> CommandResult:
        """PyCloud sistem komutları"""
        if not args:
            return CommandResult(
                error="Usage: pycloud <status|restart|shutdown|modules>",
                return_code=1
            )
        
        action = args[0].lower()
        
        if action == "status":
            return self._pycloud_status()
        elif action == "modules":
            return self._pycloud_modules()
        elif action == "restart":
            return CommandResult(output="System restart command received...")
        elif action == "shutdown":
            return CommandResult(output="System shutdown command received...")
        else:
            return CommandResult(
                error=f"Unknown action: {action}",
                return_code=1
            )
    
    def cmd_notify(self, args: List[str], current_dir: str) -> CommandResult:
        """Bildirim gönder"""
        if not args:
            return CommandResult(
                error="Usage: notify <message>",
                return_code=1
            )
        
        message = " ".join(args)
        
        # Kernel üzerinden bildirim gönder
        if self.kernel:
            try:
                notify_module = self.kernel.get_module("notify")
                if notify_module:
                    notify_module.send_notification("Terminal", message)
                    return CommandResult(output="Notification sent")
            except:
                pass
        
        return CommandResult(output=f"Notification: {message}")
    
    # Yardımcı metodlar
    def _execute_external(self, parts: List[str], current_dir: str) -> CommandResult:
        """Harici komut çalıştır"""
        try:
            result = subprocess.run(
                parts,
                cwd=current_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return CommandResult(
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return CommandResult(
                error="Command timed out",
                return_code=124
            )
        except FileNotFoundError:
            return CommandResult(
                error=f"Command not found: {parts[0]}",
                return_code=127
            )
        except Exception as e:
            return CommandResult(
                error=f"Failed to execute command: {e}",
                return_code=1
            )
    
    def _format_size(self, size_bytes: int) -> str:
        """Boyutu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"
    
    def _format_uptime(self, seconds: float) -> str:
        """Uptime formatla"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days} days, {hours} hours, {minutes} minutes"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes"
    
    def _get_general_help(self) -> str:
        """Genel yardım metni"""
        categories = self.get_command_categories()
        
        help_text = """
🌩️  Cloud Terminal v2.0.0 - Command Help

📋 Available Commands by Category:

🔧 System Commands:
  """ + ", ".join(categories['sistem']) + """

📁 File Commands:
  """ + ", ".join(categories['dosya']) + """

👥 User Commands:
  """ + ", ".join(categories['kullanıcı']) + """

💻 Developer Commands:
  """ + ", ".join(categories['geliştirici']) + """

💡 Tips:
  - Use Tab for autocomplete
  - Use ↑↓ arrows for command history
  - Type 'help <command>' for specific help
  - Use Ctrl+C to copy, Ctrl+V to paste
  - Use Ctrl+L to clear terminal

Examples:
  ls -la          # List files with details
  cd /path        # Change directory
  cat file.txt    # Show file content
  ps              # Show running processes
  clapp list      # List installed apps
  pycloud status  # Show system status
"""
        return help_text
    
    def _get_command_help(self, command: str) -> str:
        """Belirli komut yardımı"""
        help_texts = {
            'ls': "ls [options] [directory] - List directory contents\n  -l: detailed listing\n  -a: show hidden files",
            'cd': "cd [directory] - Change current directory\n  cd: go to home directory\n  cd ..: go to parent directory",
            'cat': "cat <file> - Display file contents",
            'ps': "ps - Show running processes",
            'clapp': "clapp <action> [args] - Package manager\n  list: show installed apps\n  install <app>: install app\n  remove <app>: remove app",
            'pycloud': "pycloud <action> - System commands\n  status: show system status\n  modules: list loaded modules"
        }
        
        return help_texts.get(command, f"No help available for '{command}'")
    
    def _clapp_list(self) -> CommandResult:
        """Clapp list komutu"""
        try:
            apps_dir = Path("../../apps")
            if not apps_dir.exists():
                apps_dir = Path("../../../apps")
            
            if not apps_dir.exists():
                return CommandResult(output="No apps directory found")
            
            apps = []
            for app_dir in apps_dir.iterdir():
                if app_dir.is_dir():
                    app_json = app_dir / "app.json"
                    if app_json.exists():
                        try:
                            with open(app_json, 'r') as f:
                                app_data = json.load(f)
                            apps.append(f"{app_data.get('id', app_dir.name)} - {app_data.get('name', 'Unknown')} v{app_data.get('version', '1.0.0')}")
                        except:
                            apps.append(f"{app_dir.name} - (Invalid app.json)")
            
            if apps:
                return CommandResult(output="Installed Apps:\n" + "\n".join(apps))
            else:
                return CommandResult(output="No apps installed")
                
        except Exception as e:
            return CommandResult(
                error=f"Failed to list apps: {e}",
                return_code=1
            )
    
    def _pycloud_status(self) -> CommandResult:
        """PyCloud durum bilgisi"""
        status_info = f"""
PyCloud OS System Status:
========================

Terminal: Cloud Terminal v2.0.0
Kernel: {'Available' if self.kernel else 'Not available'}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if self.kernel:
            try:
                modules = len(self.kernel.modules) if hasattr(self.kernel, 'modules') else 0
                status_info += f"Loaded modules: {modules}\n"
                
                if hasattr(self.kernel, 'start_time'):
                    uptime = datetime.now() - self.kernel.start_time
                    status_info += f"Uptime: {uptime}\n"
            except:
                pass
        
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                status_info += f"CPU Usage: {cpu_percent}%\n"
                status_info += f"Memory Usage: {memory.percent}%\n"
            except:
                pass
        
        return CommandResult(output=status_info)
    
    def _pycloud_modules(self) -> CommandResult:
        """PyCloud modülleri"""
        if not self.kernel:
            return CommandResult(output="Kernel not available")
        
        try:
            if hasattr(self.kernel, 'modules'):
                modules = list(self.kernel.modules.keys())
                if modules:
                    return CommandResult(output="Loaded modules:\n" + "\n".join(f"  - {mod}" for mod in modules))
                else:
                    return CommandResult(output="No modules loaded")
            else:
                return CommandResult(output="Module information not available")
        except Exception as e:
            return CommandResult(
                error=f"Failed to get modules: {e}",
                return_code=1
            )
    
    # Eksik komutlar için placeholder'lar
    def cmd_head(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="head command not implemented yet", return_code=1)
    
    def cmd_tail(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="tail command not implemented yet", return_code=1)
    
    def cmd_find(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="find command not implemented yet", return_code=1)
    
    def cmd_rmdir(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="rmdir command not implemented yet", return_code=1)
    
    def cmd_rm(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="rm command not implemented yet", return_code=1)
    
    def cmd_cp(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="cp command not implemented yet", return_code=1)
    
    def cmd_mv(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="mv command not implemented yet", return_code=1)
    
    def cmd_kill(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="kill command not implemented yet", return_code=1)
    
    def cmd_killall(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="killall command not implemented yet", return_code=1)
    
    def cmd_top(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="top command not implemented yet", return_code=1)
    
    def cmd_thread(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="thread command not implemented yet", return_code=1)
    
    def cmd_users(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="users command not implemented yet", return_code=1)
    
    def cmd_su(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="su command not implemented yet", return_code=1)
    
    def cmd_profile(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="profile command not implemented yet", return_code=1)
    
    def cmd_python(self, args: List[str], current_dir: str) -> CommandResult:
        return self._execute_external(['python3'] + args, current_dir)
    
    def cmd_pip(self, args: List[str], current_dir: str) -> CommandResult:
        return self._execute_external(['pip3'] + args, current_dir)
    
    def cmd_git(self, args: List[str], current_dir: str) -> CommandResult:
        return self._execute_external(['git'] + args, current_dir)
    
    def cmd_fs(self, args: List[str], current_dir: str) -> CommandResult:
        return CommandResult(error="fs command not implemented yet", return_code=1) 