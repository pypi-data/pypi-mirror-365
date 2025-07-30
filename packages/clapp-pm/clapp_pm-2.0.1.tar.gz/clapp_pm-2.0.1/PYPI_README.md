# 🚀 clapp - Evrensel Çoklu Dil Uygulama Yöneticisi

[![PyPI version](https://badge.fury.io/py/clapp-pm.svg)](https://badge.fury.io/py/clapp-pm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**clapp**, herhangi bir programlama dilinde yazılmış uygulamaları tek komutla yükleyip çalıştırmanızı sağlayan, güçlü ve esnek bir CLI paket yöneticisidir.

## ✨ Özellikler

### 🌍 **Evrensel Dil Desteği**
- **30+ Programlama Dili**: Python, JavaScript, Go, Rust, C/C++, Java, PHP, Ruby, Perl, Bash ve daha fazlası
- **Otomatik Dil Tespiti**: Dosya uzantısına göre otomatik tespit
- **Shebang Desteği**: Script dosyalarını otomatik tanıma
- **Çoklu Dil Projeleri**: Tek projede birden fazla dil desteği

### 🚀 **Hızlı ve Kolay Kullanım**
- **Tek Komutla Kurulum**: `clapp install app-name`
- **Tek Komutla Çalıştırma**: `clapp run app-name`
- **Otomatik Bağımlılık Yönetimi**: Gerekli araçları otomatik tespit
- **Şablon Sistemi**: `clapp new` ile hızlı proje oluşturma

### 🛠️ **Geliştirici Araçları**
- **Manifest Doğrulama**: `clapp validate`
- **Paket Yayınlama**: `clapp publish`
- **Bağımlılık Kontrolü**: `clapp dependency`
- **Sistem Tanılaması**: `clapp doctor`
- **Akıllı Arama**: `clapp search`

## 📦 Kurulum

```bash
pip install clapp-pm
```

## 🎯 Hızlı Başlangıç

### 1. Uygulama Yükleme
```bash
# GitHub'dan uygulama yükle
clapp install hello-python

# Yerel dizinden yükle
clapp install ./my-app --local
```

### 2. Uygulama Çalıştırma
```bash
# Uygulamayı çalıştır
clapp run hello-python

# Evrensel dil desteği ile
clapp run my-c-app  # C uygulaması otomatik derlenir ve çalıştırılır
```

### 3. Yeni Proje Oluşturma
```bash
# Mevcut şablonları listele
clapp new

# Python projesi oluştur
clapp new python my-app

# Evrensel proje oluştur
clapp new universal my-multi-app
```

### 4. Uygulama Yönetimi
```bash
# Yüklü uygulamaları listele
clapp list

# Uygulama bilgilerini göster
clapp info hello-python

# Uygulamayı güncelle
clapp update-apps hello-python

# Uygulamayı kaldır
clapp uninstall hello-python
```

## 🌍 Desteklenen Diller

### Temel Diller
- **Python** (.py) - Python uygulamaları
- **JavaScript** (.js) - Node.js uygulamaları
- **TypeScript** (.ts) - TypeScript uygulamaları
- **Lua** (.lua) - Lua scriptleri
- **Go** (.go) - Go uygulamaları
- **Rust** (.rs) - Rust uygulamaları

### Sistem Dilleri
- **C** (.c) - C uygulamaları
- **C++** (.cpp) - C++ uygulamaları
- **Java** (.java) - Java uygulamaları
- **C#** (.cs) - .NET uygulamaları
- **Swift** (.swift) - Swift uygulamaları
- **Kotlin** (.kt) - Kotlin uygulamaları

### Script Dilleri
- **PHP** (.php) - PHP uygulamaları
- **Ruby** (.rb) - Ruby uygulamaları
- **Perl** (.pl) - Perl scriptleri
- **Bash** (.sh) - Shell scriptleri
- **PowerShell** (.ps1) - PowerShell scriptleri
- **R** (.r) - R scriptleri

### Özel Diller
- **Dart** (.dart) - Dart uygulamaları
- **Scala** (.scala) - Scala uygulamaları
- **Clojure** (.clj) - Clojure uygulamaları
- **Haskell** (.hs) - Haskell uygulamaları
- **OCaml** (.ml) - OCaml uygulamaları
- **Fortran** (.f90) - Fortran uygulamaları
- **Pascal** (.pas) - Pascal uygulamaları

### Oyun ve Özel
- **Love2D** - Lua tabanlı oyunlar
- **Executable** (.exe) - Windows uygulamaları
- **macOS App** (.app) - macOS uygulamaları
- **Java JAR** (.jar) - Java paketleri

## 📋 Manifest Formatı

### Temel Manifest
```json
{
    "name": "my-app",
    "version": "1.0.0",
    "language": "python",
    "entry": "main.py",
    "description": "Açıklama",
    "dependencies": ["requests", "numpy"]
}
```

### Evrensel Manifest
```json
{
    "name": "my-universal-app",
    "version": "1.0.0",
    "language": "universal",
    "entry": "main.c",
    "description": "Evrensel dil desteği ile uygulama"
}
```

### Çoklu Dil Manifest
```json
{
    "name": "multi-app",
    "version": "1.0.0",
    "language": "multi",
    "entry": "main.py",
    "description": "Çoklu dil projesi",
    "languages": {
        "python": {
            "entry": "backend/main.py",
            "dependencies": ["flask"]
        },
        "javascript": {
            "entry": "frontend/app.js",
            "dependencies": ["express"]
        }
    },
    "run_order": ["python", "javascript"]
}
```

## 🛠️ Komut Referansı

### Temel Komutlar
```bash
clapp list                    # Yüklü uygulamaları listele
clapp run <app>              # Uygulamayı çalıştır
clapp info <app>             # Uygulama bilgilerini göster
clapp new                    # Yeni uygulama oluştur
```

### Yönetim Komutları
```bash
clapp install <app>          # Uygulama yükle
clapp uninstall <app>        # Uygulamayı kaldır
clapp update-apps [app]      # Uygulamaları güncelle
clapp validate <path>        # Uygulama klasörünü doğrula
clapp publish <path>         # Uygulama yayınla
```

### Sistem Komutları
```bash
clapp doctor                 # Kapsamlı sistem tanılaması
clapp clean                  # Geçici dosyaları temizle
clapp where <app>            # Uygulama konumunu göster
clapp version                # Sürüm bilgilerini göster
```

### Bağımlılık Komutları
```bash
clapp dependency check       # Sistem geneli bağımlılık kontrolü
clapp dependency check <app> # Belirli uygulama bağımlılık kontrolü
clapp dependency install <app> # Uygulama bağımlılıklarını kur
clapp dependency tree <app>  # Bağımlılık ağacı
```

### Uzak Komutlar
```bash
clapp search <query>         # Uzak depoda ara
clapp remote list            # Uzak depo listesi
clapp health                 # Sistem sağlık kontrolü
```

## 🔧 Geliştirici Rehberi

### Yeni Uygulama Oluşturma
```bash
# Şablonları listele
clapp new

# Belirli dilde proje oluştur
clapp new python my-app
clapp new go my-go-app
clapp new rust my-rust-app

# Evrensel proje oluştur
clapp new universal my-c-app
```

### Uygulama Yayınlama
```bash
# Uygulamayı doğrula
clapp validate ./my-app

# Uygulamayı yayınla
clapp publish ./my-app

# GitHub'a otomatik push ile yayınla
clapp publish ./my-app --push
```

### Bağımlılık Yönetimi
```bash
# Python bağımlılıkları
clapp dependency check my-python-app

# Lua bağımlılıkları
clapp dependency check my-lua-app

# Engine kontrolü
clapp dependency engine my-love2d-game
```

## 🏗️ Mimari

### İki Repo Sistemi
- **clapp** (Bu repo): CLI ve yönetim araçları
- **clapp-packages**: Paket deposu ve index.json

### Runner Sistemi
- **LanguageRunner**: Temel dil çalıştırıcısı
- **UniversalRunner**: Evrensel dil desteği
- **MultiLanguageRunner**: Çoklu dil projeleri
- **Love2DRunner**: Oyun motoru desteği

### Güvenlik
- Manifest doğrulama
- Güvenli subprocess kullanımı
- Bağımlılık çözümleme
- Cache yönetimi

## 🤝 Katkıda Bulunma

### Hata Bildirimi
- 🐛 [Issues](https://github.com/mburakmmm/clapp/issues) - Hata bildirimi ve öneriler
- 💡 [Discussions](https://github.com/mburakmmm/clapp/discussions) - Tartışma ve öneriler

### Paket Eklemek
- 📦 [clapp-packages](https://github.com/mburakmmm/clapp-packages) - Paket deposu
- 📖 [Paket Rehberi](https://github.com/mburakmmm/clapp/wiki/Package-Guide) - Detaylı rehber

### Geliştirme
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📚 Dokümantasyon

- 📖 [Wiki](https://github.com/mburakmmm/clapp/wiki) - Detaylı dokümantasyon
- 🎯 [Hızlı Başlangıç](https://github.com/mburakmmm/clapp/wiki/Quick-Start) - İlk adımlar
- 🛠️ [Geliştirici Rehberi](https://github.com/mburakmmm/clapp/wiki/Developer-Guide) - Geliştirme
- 📦 [Paket Rehberi](https://github.com/mburakmmm/clapp/wiki/Package-Guide) - Paket oluşturma

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- Tüm katkıda bulunanlara
- Açık kaynak topluluğuna
- Test eden ve geri bildirim veren kullanıcılara

---

**clapp** ile herhangi bir dilde yazılmış uygulamaları kolayca yönetin! 🚀 