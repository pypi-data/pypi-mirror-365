"""
PyCloud OS File System Package
Alt modüller: UserFS, MountManager, FileSearchEngine, PyCloudVFS
"""

from .userfs import UserFS
from .mount import MountManager
from .search import FileSearchEngine
from .vfs import PyCloudVFS, VFSPermission, VFSMount, AppProfile

# Ana fs_main.py modülünden fonksiyonları import et
import sys
from pathlib import Path

# Parent directory'yi path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

# fs_main.py'den gerekli fonksiyonları import et
from fs_main import FileSystem, init_fs, get_file_system

__all__ = [
    'UserFS',
    'MountManager',
    'FileSearchEngine',
    'PyCloudVFS',
    'VFSPermission',
    'VFSMount',
    'AppProfile',
    'FileSystem',
    'init_fs',
    'get_file_system'
] 