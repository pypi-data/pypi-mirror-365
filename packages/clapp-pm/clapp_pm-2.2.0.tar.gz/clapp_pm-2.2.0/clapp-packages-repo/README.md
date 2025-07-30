# 📦 clapp-packages

**Modern, Python tabanlı uygulama paket deposu**

[![GitHub](https://img.shields.io/badge/GitHub-clapp--packages-blue.svg)](https://github.com/mburakmmm/clapp-packages)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

## 🚀 Hakkında

`clapp-packages`, [clapp](https://github.com/mburakmmm/clapp) uygulama yöneticisi için resmi paket deposudur. Bu repo, Python tabanlı modern uygulamaları barındırır ve `clapp` komut satırı aracı ile kolayca kurulabilir.

## 📋 Mevcut Uygulamalar

### 🖥️ Sistem Uygulamaları

| Uygulama | Sürüm | Açıklama |
|----------|-------|----------|
| **pycloud-os** | 1.0.0 | Modern, Python tabanlı, macOS benzeri işletim sistemi |
| **cloud-system** | 1.0.0 | Modern sistem yöneticisi ve görev yöneticisi |
| **cloud-web-browser** | 1.0.0 | Modern ve hızlı web tarayıcı uygulaması |

### 🛠️ Geliştirme Araçları

| Uygulama | Sürüm | Açıklama |
|----------|-------|----------|
| **clapp-store** | 1.0.0 | Clapp paket yöneticisinin grafik arayüzü |
| **hello-python** | 1.0.0 | Basit Python merhaba dünya uygulaması |

### 🎮 Oyunlar

| Uygulama | Sürüm | Açıklama |
|----------|-------|----------|
| **luaozgur-moba** | 1.0.1 | League of Legends benzeri MOBA oyunu |

## 🛠️ Kurulum

### clapp Yükleme

```bash
# pip ile kurulum
pip install clapp

# veya geliştirme sürümü
git clone https://github.com/mburakmmm/clapp.git
cd clapp
pip install -e .
```

### Uygulama Kurma

```bash
# Tüm mevcut uygulamaları listele
clapp list

# Belirli bir uygulamayı kur
clapp install pycloud-os

# Uygulama bilgilerini görüntüle
clapp info pycloud-os

# Uygulamayı çalıştır
clapp run pycloud-os
```

## 📦 Yeni Uygulama Ekleme

### 1. Uygulama Hazırlama

Uygulamanızın bir `manifest.json` dosyası olmalı:

```json
{
    "name": "my-app",
    "version": "1.0.0",
    "language": "python",
    "description": "Uygulama açıklaması",
    "entry": "main.py",
    "dependencies": ["requests", "flask"]
}
```

### 2. Publish Etme

```bash
# Uygulamanızı publish edin
clapp publish ./my-app --push
```

### 3. Kurulum

```bash
# Yeni uygulamayı kurun
clapp install my-app
```

## 🔧 Geliştirme

### Repo Yapısı

```
clapp-packages/
├── packages/           # Uygulama klasörleri
│   ├── pycloud-os/
│   ├── cloud-system/
│   └── ...
├── index.json         # Uygulama listesi
├── build_index.py     # Index oluşturucu
└── README.md          # Bu dosya
```

### Index.json Formatı

```json
[
    {
        "name": "app-name",
        "version": "1.0.0",
        "language": "python",
        "description": "Açıklama",
        "entry": "main.py",
        "dependencies": ["package1", "package2"],
        "folder": "app-name",
        "repo_url": "https://github.com/mburakmmm/clapp-packages",
        "subdir": "app-name"
    }
]
```

## 🤝 Katkıda Bulunma

1. **Fork** yapın
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-app`)
3. **Commit** yapın (`git commit -m 'Add amazing app'`)
4. **Push** yapın (`git push origin feature/amazing-app`)
5. **Pull Request** oluşturun

### Uygulama Gereksinimleri

- ✅ Geçerli `manifest.json` dosyası
- ✅ Çalışan `entry` dosyası
- ✅ Python 3.8+ uyumluluğu
- ✅ Açık kaynak lisansı
- ✅ Dokümantasyon

## 📝 Lisans

Bu proje [MIT License](LICENSE) altında lisanslanmıştır.

## 🔗 Bağlantılar

- **clapp**: https://github.com/mburakmmm/clapp
- **Dokümantasyon**: https://github.com/mburakmmm/clapp/docs
- **Sorunlar**: https://github.com/mburakmmm/clapp-packages/issues

## 📊 İstatistikler

- **Toplam Uygulama**: 6
- **Python Uygulamaları**: 5
- **Oyun Uygulamaları**: 1
- **Sistem Uygulamaları**: 3

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! 