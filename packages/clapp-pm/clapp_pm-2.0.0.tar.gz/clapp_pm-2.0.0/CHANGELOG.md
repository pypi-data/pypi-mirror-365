# Changelog

Tüm önemli değişiklikler bu dosyada belgelenecektir.

Format [Keep a Changelog](https://keepachangelog.com/tr/1.0.0/) standardına dayanmaktadır,
ve bu proje [Semantic Versioning](https://semver.org/lang/tr/) kullanmaktadır.

## [2.0.0] - 2024-07-29

### 🚀 **MAJÖR YENİLİK - Evrensel Dil Desteği**

#### ✨ Yeni Özellikler
- **🌍 Evrensel Dil Desteği**: 30+ programlama dili otomatik tespit ve çalıştırma
- **🔍 Otomatik Dil Tespiti**: Dosya uzantısına göre otomatik tespit sistemi
- **📝 Shebang Desteği**: Script dosyalarını otomatik tanıma
- **🔄 Çoklu Dil Projeleri**: Tek projede birden fazla dil desteği
- **🎯 Şablon Sistemi**: `clapp new` ile hızlı proje oluşturma
- **🛡️ Güvenli Çalıştırma**: Sadece bilinen komutlar ile güvenli çalıştırma

#### 🌍 **Desteklenen Yeni Diller**
- **Sistem Dilleri**: C, C++, Java, C#, Swift, Kotlin
- **Script Dilleri**: JavaScript, TypeScript, PHP, Ruby, Perl, Bash, PowerShell, R
- **Modern Diller**: Go, Rust, Dart, Scala, Clojure
- **Fonksiyonel Diller**: Haskell, OCaml
- **Eski Diller**: Fortran, Pascal, Basic, VBScript, Batch
- **Özel Formatlar**: Executable, macOS App, Java JAR, Java Class

#### 🛠️ **Yeni Komutlar**
- `clapp new` - Yeni uygulama oluşturma (9 şablon)
- `clapp new --list` - Mevcut şablonları listeleme
- `clapp new universal <app>` - Evrensel proje oluşturma
- `clapp new multi <app>` - Çoklu dil projesi oluşturma

#### 🔧 **Geliştirici Araçları**
- **UniversalRunner**: Evrensel dil çalıştırıcısı
- **MultiLanguageRunner**: Çoklu dil projeleri için özel runner
- **Manifest Doğrulama**: Gelişmiş JSON şema kontrolü
- **Bağımlılık Yönetimi**: Otomatik bağımlılık tespiti ve kurulumu

#### 📋 **Yeni Manifest Formatları**
```json
// Evrensel Manifest
{
    "name": "my-app",
    "language": "universal",
    "entry": "main.c"
}

// Çoklu Dil Manifest
{
    "name": "multi-app",
    "language": "multi",
    "languages": {
        "python": {"entry": "backend/main.py"},
        "javascript": {"entry": "frontend/app.js"}
    },
    "run_order": ["python", "javascript"]
}
```

#### 🎯 **Şablon Sistemi**
- **Python**: Temel Python uygulaması
- **Lua**: Lua script uygulaması
- **Go**: Go uygulaması
- **Rust**: Rust uygulaması
- **Node.js**: JavaScript/Node.js uygulaması
- **Bash**: Shell script uygulaması
- **Dart**: Dart uygulaması
- **Multi**: Çoklu dil projesi
- **Universal**: Evrensel dil projesi

#### 🔒 **Güvenlik İyileştirmeleri**
- Güvenli subprocess kullanımı
- Manifest doğrulama sistemi
- Bağımlılık çözümleme
- Cache yönetimi

#### 🐛 **Hata Düzeltmeleri**
- Love2D oyunları için klasör bazlı çalıştırma
- Manifest validator güncellemeleri
- Install komutunda yerel kurulum düzeltmeleri
- Update-apps komutunda index.json format uyumluluğu

#### 📚 **Dokümantasyon**
- Kapsamlı README güncellemeleri
- Yeni komut referansları
- Geliştirici rehberleri
- Manifest format örnekleri

#### 🏗️ **Mimari Değişiklikler**
- Runner sistemi genişletildi
- Evrensel dil desteği eklendi
- Şablon sistemi entegrasyonu
- Güvenlik katmanları eklendi

---

## [1.0.50] - 2024-07-24

### 🔧 **İyileştirmeler**
- `clapp upgrade` komutu kaldırıldı (update-apps kullanın)
- `clapp check-env` komutu kaldırıldı (doctor kullanın)
- Help mesajları güncellendi
- Gereksiz dosyalar temizlendi

### 🐛 **Hata Düzeltmeleri**
- Install komutunda help mesajı düzeltildi
- New komutunda şablon listesi iyileştirildi

---

## [1.0.40] - 2024-07-20

### ✨ **Yeni Özellikler**
- `clapp new` komutu eklendi
- Şablon sistemi entegrasyonu
- Python, Lua, Dart şablonları

### 🔧 **İyileştirmeler**
- Komut yapısı optimize edildi
- Help mesajları güncellendi

---

## [1.0.30] - 2024-07-15

### ✨ **Yeni Özellikler**
- `clapp doctor` komutu eklendi
- Kapsamlı sistem tanılaması
- Bağımlılık kontrolü

### 🔧 **İyileştirmeler**
- Sistem sağlık kontrolü
- Hata raporlama iyileştirildi

---

## [1.0.20] - 2024-07-10

### ✨ **Yeni Özellikler**
- `clapp update-apps` komutu eklendi
- Otomatik güncelleme sistemi
- Index.json entegrasyonu

### 🐛 **Hata Düzeltmeleri**
- Update detection düzeltildi
- Index format uyumluluğu

---

## [1.0.10] - 2024-07-05

### ✨ **Yeni Özellikler**
- `clapp publish` komutu eklendi
- GitHub entegrasyonu
- Otomatik push sistemi

### 🔧 **İyileştirmeler**
- Manifest doğrulama
- Paket yayınlama sistemi

---

## [1.0.0] - 2024-07-01

### 🎉 **İlk Sürüm**
- Temel CLI paket yöneticisi
- Python ve Lua desteği
- Manifest sistemi
- Temel komutlar (install, run, list, uninstall)
- İki repo sistemi (clapp + clapp-packages)

---

## Sürüm Notları

### Semantic Versioning
- **MAJOR**: Uyumsuz API değişiklikleri
- **MINOR**: Geriye uyumlu yeni özellikler
- **PATCH**: Geriye uyumlu hata düzeltmeleri

### Desteklenen Python Sürümleri
- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+
- Python 3.12+

### Platform Desteği
- Windows
- macOS
- Linux

### Lisans
MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın. 