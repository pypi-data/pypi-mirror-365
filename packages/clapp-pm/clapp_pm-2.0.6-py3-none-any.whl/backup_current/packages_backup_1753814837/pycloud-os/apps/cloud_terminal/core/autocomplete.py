"""
Cloud Terminal - Autocomplete Sistemi
Komut ve dosya tamamlama önerileri
"""

import os
from typing import List, Optional
from pathlib import Path

class AutoCompleter:
    """Autocomplete sistemi"""
    
    def __init__(self, command_runner=None):
        self.command_runner = command_runner
        
        # Sistem komutları
        self.system_commands = [
            'help', 'clear', 'exit', 'version', 'uptime', 'date', 'whoami'
        ]
        
        # Dosya komutları
        self.file_commands = [
            'pwd', 'cd', 'ls', 'dir', 'cat', 'head', 'tail', 'find',
            'mkdir', 'rmdir', 'rm', 'cp', 'mv', 'touch'
        ]
        
        # İşlem komutları
        self.process_commands = [
            'ps', 'kill', 'killall', 'top', 'mem', 'thread'
        ]
        
        # Kullanıcı komutları
        self.user_commands = [
            'users', 'su', 'profile'
        ]
        
        # Geliştirici komutları
        self.developer_commands = [
            'clapp', 'pycloud', 'python', 'python3', 'pip', 'git', 'notify', 'fs'
        ]
        
        # Tüm komutlar
        self.all_commands = (
            self.system_commands + 
            self.file_commands + 
            self.process_commands + 
            self.user_commands + 
            self.developer_commands
        )
        
        # Alt komutlar
        self.sub_commands = {
            'clapp': ['list', 'install', 'remove', 'update', 'search', 'info', 'doctor', 'upgrade', 'history', 'help'],
            'pycloud': ['status', 'restart', 'shutdown', 'modules'],
            'git': ['init', 'add', 'commit', 'push', 'pull', 'status', 'log'],
            'pip': ['install', 'uninstall', 'list', 'show', 'search'],
            'ls': ['-l', '-a', '-la', '--long', '--all'],
            'cd': ['..', '.', '~'],
        }
    
    def get_completions(self, partial_command: str, current_dir: str) -> List[str]:
        """Tamamlama önerilerini al"""
        if not partial_command.strip():
            return []
        
        parts = partial_command.split()
        
        if len(parts) == 1:
            # İlk kelime - komut tamamlama
            return self._complete_command(parts[0])
        else:
            # Sonraki kelimeler - bağlama göre tamamlama
            return self._complete_arguments(parts, current_dir)
    
    def _complete_command(self, partial: str) -> List[str]:
        """Komut tamamlama"""
        partial = partial.lower()
        matches = []
        
        # Komut eşleşmeleri
        for cmd in self.all_commands:
            if cmd.startswith(partial):
                matches.append(cmd)
        
        # Dosya/dizin eşleşmeleri (eğer / içeriyorsa)
        if '/' in partial or partial.startswith('.'):
            try:
                file_matches = self._complete_path(partial, os.getcwd())
                matches.extend(file_matches)
            except:
                pass
        
        return sorted(matches)
    
    def _complete_arguments(self, parts: List[str], current_dir: str) -> List[str]:
        """Argüman tamamlama"""
        command = parts[0].lower()
        current_arg = parts[-1] if len(parts) > 1 else ""
        
        # Alt komut tamamlama
        if command in self.sub_commands and len(parts) == 2:
            sub_cmds = self.sub_commands[command]
            matches = [cmd for cmd in sub_cmds if cmd.startswith(current_arg)]
            if matches:
                return matches
        
        # Dosya/dizin tamamlama
        if command in ['cd', 'ls', 'cat', 'head', 'tail', 'rm', 'cp', 'mv', 'mkdir']:
            return self._complete_path(current_arg, current_dir)
        
        # Özel tamamlamalar
        if command == 'clapp' and len(parts) == 3 and parts[1] in ['install', 'remove']:
            return self._complete_app_names()
        
        return []
    
    def _complete_path(self, partial: str, current_dir: str) -> List[str]:
        """Dosya/dizin yolu tamamlama"""
        try:
            if not partial:
                # Boş - mevcut dizindeki tüm öğeler
                target_dir = current_dir
                prefix = ""
            elif partial.startswith('/'):
                # Mutlak yol
                target_dir = os.path.dirname(partial) or '/'
                prefix = os.path.basename(partial)
            elif partial.startswith('~'):
                # Home dizini
                expanded = os.path.expanduser(partial)
                target_dir = os.path.dirname(expanded) or str(Path.home())
                prefix = os.path.basename(expanded)
            else:
                # Göreceli yol
                if '/' in partial:
                    rel_dir = os.path.dirname(partial)
                    target_dir = os.path.join(current_dir, rel_dir)
                    prefix = os.path.basename(partial)
                else:
                    target_dir = current_dir
                    prefix = partial
            
            if not os.path.exists(target_dir):
                return []
            
            matches = []
            for item in os.listdir(target_dir):
                if item.startswith(prefix):
                    item_path = os.path.join(target_dir, item)
                    
                    # Dizinlere / ekle
                    if os.path.isdir(item_path):
                        if partial.endswith('/') or not partial:
                            matches.append(item + '/')
                        else:
                            # Tam yol oluştur
                            if partial.startswith('/'):
                                matches.append(os.path.join(os.path.dirname(partial), item) + '/')
                            elif '/' in partial:
                                matches.append(os.path.join(os.path.dirname(partial), item) + '/')
                            else:
                                matches.append(item + '/')
                    else:
                        # Dosyalar
                        if partial.startswith('/'):
                            matches.append(os.path.join(os.path.dirname(partial), item))
                        elif '/' in partial:
                            matches.append(os.path.join(os.path.dirname(partial), item))
                        else:
                            matches.append(item)
            
            return sorted(matches)
            
        except Exception:
            return []
    
    def _complete_app_names(self) -> List[str]:
        """Uygulama adları tamamlama"""
        try:
            apps_dir = Path("../../apps")
            if not apps_dir.exists():
                apps_dir = Path("../../../apps")
            
            if not apps_dir.exists():
                return []
            
            app_names = []
            for app_dir in apps_dir.iterdir():
                if app_dir.is_dir() and (app_dir / "app.json").exists():
                    app_names.append(app_dir.name)
            
            return sorted(app_names)
            
        except Exception:
            return []
    
    def get_command_help(self, command: str) -> Optional[str]:
        """Komut yardımı al"""
        help_texts = {
            'help': "Show help for commands",
            'clear': "Clear the terminal screen",
            'exit': "Exit the terminal",
            'ls': "List directory contents",
            'cd': "Change directory",
            'pwd': "Print working directory",
            'cat': "Display file contents",
            'mkdir': "Create directories",
            'touch': "Create or update files",
            'ps': "Show running processes",
            'mem': "Show memory usage",
            'clapp': "Package manager for PyCloud apps - list, install, remove, update, search, info, doctor, help",
            'pycloud': "PyCloud system commands",
        }
        
        return help_texts.get(command.lower())
    
    def is_valid_command(self, command: str) -> bool:
        """Komutun geçerli olup olmadığını kontrol et"""
        return command.lower() in self.all_commands 