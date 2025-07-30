#!/usr/bin/env python3
"""
setup.py - clapp PyPI Packaging Konfigürasyonu

Bu dosya clapp'i PyPI'da yayınlamak için gerekli
packaging konfigürasyonunu içerir.
"""

from setuptools import setup, find_packages
import json
from pathlib import Path

# Version bilgisini version.json'dan oku
version_file = Path("version.json")
if version_file.exists():
    with open(version_file, 'r', encoding='utf-8') as f:
        version_data = json.load(f)
    VERSION = version_data.get("version", "1.0.0")
    AUTHOR = version_data.get("author", "Melih Burak Memiş")
else:
    VERSION = "1.0.0"
    AUTHOR = "Melih Burak Memiş"

# PyPI için özel README dosyasını kullan
pypi_readme_file = Path("PYPI_README.md")
if pypi_readme_file.exists():
    with open(pypi_readme_file, 'r', encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    # Fallback olarak normal README.md'yi kullan
    readme_file = Path("README.md")
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            LONG_DESCRIPTION = f.read()
    else:
        LONG_DESCRIPTION = "Universal multi-language application manager with 30+ programming language support"

setup(
    name="clapp-pm",
    version=VERSION,
    author=AUTHOR,
    author_email="mburakmemiscy@gmail.com",
    description="Universal multi-language application manager with 30+ programming language support",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/mburakmmm/clapp",
    project_urls={
        "Bug Tracker": "https://github.com/mburakmmm/clapp/issues",
        "Documentation": "https://github.com/mburakmmm/clapp/blob/main/README.md",
        "Source Code": "https://github.com/mburakmmm/clapp",
        "Package Repository": "https://github.com/mburakmmm/clapp-packages",
        "Changelog": "https://github.com/mburakmmm/clapp/blob/main/CHANGELOG.md",
    },
    
    # Paket bilgileri
    packages=find_packages(exclude=["tests*", "apps*", "packages-repo-files*"]),
    py_modules=[
        "main",
        "clapp_core",
        "package_registry",
        "package_runner",
        "manifest_schema",
        "manifest_validator",
        "dependency_resolver",
        "installer",
        "remote_registry",
        "cli_commands",
        "publish_command",
        "install_command",
        "list_command",
        "uninstall_command",
        "check_env",
        "post_install_hint",
        "info_command",
        "validate_command",
        "doctor_command",
        "clean_command",
        "where_command",
        "version_command",
        "version",
        "package_signing",
        "version_manager",
        "cache_manager",
        "smart_search",
        "progress_utils",
        "new_command",
        "update_command",
        "platform_utils",
    ],
    
    # Paket verileri
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
    
    # Gereksinimler
    install_requires=[
        "requests>=2.31.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
        "tqdm>=4.0.0",
        "packaging>=23.0",
    ],
    
    # Ek gereksinimler
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.20.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coverage>=6.0.0",
        ],
    },
    
    # Python sürümü gereksinimleri
    python_requires=">=3.8",
    
    # Cross-platform uyumluluk
    platforms=["Windows", "Linux", "macOS"],
    
    # Konsol komutları
    entry_points={
        "console_scripts": [
            "clapp=main:main",
        ],
    },
    
    # Sınıflandırma
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Installation/Setup",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
        "Environment :: Console",
        "Natural Language :: Turkish",
        "Natural Language :: English",
    ],
    
    # Anahtar kelimeler
    keywords=[
        "package-manager",
        "app-manager",
        "universal",
        "multi-language",
        "cross-language",
        "python",
        "javascript",
        "go",
        "rust",
        "c",
        "java",
        "php",
        "ruby",
        "perl",
        "bash",
        "lua",
        "cli",
        "lightweight",
        "desktop",
        "applications",
        "manifest",
        "dependency",
        "template",
        "runner",
    ],
    
    # Lisans
    license="MIT",
    
    # Proje durumu
    zip_safe=False,
    
    # Manifest dosyası
    data_files=[
        ("", ["version.json"]),
    ],
) 