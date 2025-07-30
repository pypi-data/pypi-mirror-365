"""
Cloud PyIDE - Kod Çalıştırıcı
Python kod çalıştırma ve subprocess yönetimi
"""

import os
import sys
import subprocess
import logging
import threading
from pathlib import Path
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass

try:
    from PyQt6.QtCore import QThread, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

@dataclass
class RunResult:
    """Çalıştırma sonucu"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float

class CodeRunner:
    """Kod çalıştırıcı"""
    
    def __init__(self, python_path: str = "python"):
        self.logger = logging.getLogger("CodeRunner")
        self.python_path = python_path
        
        # Çalışan işlemler
        self.running_processes: Dict[str, subprocess.Popen] = {}
        
        # Callback'ler
        self.output_callback: Optional[Callable[[str, str], None]] = None
        self.finished_callback: Optional[Callable[[RunResult], None]] = None
    
    def set_output_callback(self, callback: Callable[[str, str], None]):
        """Çıktı callback'i ayarla"""
        self.output_callback = callback
    
    def set_finished_callback(self, callback: Callable[[RunResult], None]):
        """Bitirme callback'i ayarla"""
        self.finished_callback = callback
    
    def run_file(self, file_path: str, working_dir: Optional[str] = None) -> bool:
        """Dosya çalıştır"""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False
            
            if working_dir is None:
                working_dir = os.path.dirname(file_path)
            
            # Thread'de çalıştır
            if PYQT_AVAILABLE:
                worker = RunWorker(file_path, working_dir, self.python_path)
                worker.output_ready.connect(self._on_output)
                worker.finished_signal.connect(self._on_finished)
                worker.start()
            else:
                # Fallback: threading kullan
                thread = threading.Thread(
                    target=self._run_in_thread,
                    args=(file_path, working_dir)
                )
                thread.daemon = True
                thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error running file: {e}")
            return False
    
    def run_code(self, code: str, working_dir: Optional[str] = None) -> bool:
        """Kod çalıştır"""
        try:
            # Geçici dosya oluştur
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            # Çalıştır
            result = self.run_file(temp_file, working_dir)
            
            # Geçici dosyayı sil
            try:
                os.unlink(temp_file)
            except:
                pass
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error running code: {e}")
            return False
    
    def _run_in_thread(self, file_path: str, working_dir: str):
        """Thread'de çalıştır"""
        import time
        start_time = time.time()
        
        try:
            # Komut oluştur
            cmd = [self.python_path, file_path]
            
            # İşlemi başlat
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # İşlemi kaydet
            process_id = f"{file_path}_{id(process)}"
            self.running_processes[process_id] = process
            
            # Çıktıları oku
            stdout_lines = []
            stderr_lines = []
            
            # Stdout okuma
            for line in iter(process.stdout.readline, ''):
                line = line.rstrip()
                stdout_lines.append(line)
                if self.output_callback:
                    self.output_callback(line, "stdout")
            
            # Stderr okuma
            for line in iter(process.stderr.readline, ''):
                line = line.rstrip()
                stderr_lines.append(line)
                if self.output_callback:
                    self.output_callback(line, "stderr")
            
            # İşlemin bitmesini bekle
            exit_code = process.wait()
            
            # Süreyi hesapla
            execution_time = time.time() - start_time
            
            # Sonuç oluştur
            result = RunResult(
                success=(exit_code == 0),
                exit_code=exit_code,
                stdout='\n'.join(stdout_lines),
                stderr='\n'.join(stderr_lines),
                execution_time=execution_time
            )
            
            # Callback çağır
            if self.finished_callback:
                self.finished_callback(result)
            
            # İşlemi temizle
            if process_id in self.running_processes:
                del self.running_processes[process_id]
                
        except Exception as e:
            self.logger.error(f"Error in run thread: {e}")
            
            # Hata sonucu
            result = RunResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time
            )
            
            if self.finished_callback:
                self.finished_callback(result)
    
    def _on_output(self, text: str, output_type: str):
        """Çıktı geldi"""
        if self.output_callback:
            self.output_callback(text, output_type)
    
    def _on_finished(self, result: RunResult):
        """Çalıştırma bitti"""
        if self.finished_callback:
            self.finished_callback(result)
    
    def stop_all(self):
        """Tüm çalışan işlemleri durdur"""
        for process_id, process in list(self.running_processes.items()):
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
            
            if process_id in self.running_processes:
                del self.running_processes[process_id]
        
        self.logger.info("All running processes stopped")
    
    def get_running_count(self) -> int:
        """Çalışan işlem sayısı"""
        return len(self.running_processes)

if PYQT_AVAILABLE:
    class RunWorker(QThread):
        """Kod çalıştırma worker'ı"""
        
        output_ready = pyqtSignal(str, str)  # text, type
        finished_signal = pyqtSignal(RunResult)
        
        def __init__(self, file_path: str, working_dir: str, python_path: str = "python"):
            super().__init__()
            self.file_path = file_path
            self.working_dir = working_dir
            self.python_path = python_path
            self.logger = logging.getLogger("RunWorker")
        
        def run(self):
            """Çalıştır"""
            import time
            start_time = time.time()
            
            try:
                # Komut oluştur
                cmd = [self.python_path, self.file_path]
                
                # İşlemi başlat
                process = subprocess.Popen(
                    cmd,
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # stderr'i stdout'a yönlendir
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Çıktıları oku
                output_lines = []
                
                for line in iter(process.stdout.readline, ''):
                    line = line.rstrip()
                    output_lines.append(line)
                    self.output_ready.emit(line, "stdout")
                
                # İşlemin bitmesini bekle
                exit_code = process.wait()
                
                # Süreyi hesapla
                execution_time = time.time() - start_time
                
                # Sonuç oluştur
                result = RunResult(
                    success=(exit_code == 0),
                    exit_code=exit_code,
                    stdout='\n'.join(output_lines),
                    stderr="",
                    execution_time=execution_time
                )
                
                self.finished_signal.emit(result)
                
            except Exception as e:
                self.logger.error(f"Error in run worker: {e}")
                
                # Hata sonucu
                result = RunResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=str(e),
                    execution_time=time.time() - start_time
                )
                
                self.finished_signal.emit(result) 