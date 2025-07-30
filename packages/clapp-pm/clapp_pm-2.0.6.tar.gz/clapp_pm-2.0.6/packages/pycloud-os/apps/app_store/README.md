# App Store - Modern Uygulama Mağazası

PyCloud OS için modern, kullanıcı dostu uygulama mağazası. Kategori bazlı gezinme, arama, kurulum/kaldırma, kullanıcı puanları ve yorum sistemi ile birlikte gelir. **Clapp altyapısıyla tam entegre çalışır.**

## 🌟 Özellikler

### 📱 Modern UI/UX
- **3 Görünüm Modu**: Izgara, Liste, Detaylı
- **Responsive Tasarım**: Pencere boyutuna göre otomatik uyum
- **Koyu/Açık Tema**: Sistem temasıyla otomatik senkronizasyon
- **Smooth Animasyonlar**: Hover efektleri ve geçişler

### 🔍 Gelişmiş Arama ve Filtreleme
- **Gerçek Zamanlı Arama**: 300ms debounce ile hızlı arama
- **Kategori Filtresi**: 13 farklı kategori desteği
- **Sıralama Seçenekleri**: Ad, kategori, geliştirici, puan, indirme sayısı
- **Akıllı Arama**: Ad, açıklama, geliştirici ve etiketlerde arama

### 📦 Uygulama Yönetimi
- **Clapp Entegrasyonu**: Gerçek kurulum/kaldırma işlemleri
- **Repository Desteği**: Clapp repository'lerinden uygulama yükleme
- **Güncelleme Kontrolü**: Otomatik güncelleme tespiti
- **Durum Takibi**: Gerçek zamanlı işlem durumu
- **AppExplorer Entegrasyonu**: Yüklü uygulamaları otomatik keşif

### ⭐ Kullanıcı Etkileşimi
- **5 Yıldızlı Puanlama**: Etkileşimli yıldız widget'ı
- **Kullanıcı Yorumları**: Yorum okuma ve yazma
- **Uygulama Detayları**: Kapsamlı bilgi sayfası
- **Ekran Görüntüleri**: Uygulama önizlemeleri

## 🔌 Clapp Entegrasyonu

### Gerçek İşlemler
- **Kurulum**: `clapp install <app_id>` komutu kullanılır
- **Kaldırma**: `clapp remove <app_id>` komutu kullanılır
- **Güncelleme**: `clapp update <app_id>` komutu kullanılır
- **Repository**: Clapp repository'lerinden paket listesi alınır

### Fallback Sistemi
- Clapp modülleri yoksa AppKit kullanılır
- AppKit yoksa simülasyon modu devreye girer
- Hata durumunda kullanıcıya bilgi verilir

## 🏗️ Mimari

### Modüler Yapı
```
apps/app_store/
├── app.json              # Uygulama metadata
├── main.py               # Ana başlatıcı
├── icon.png              # Uygulama ikonu
├── README.md             # Bu dosya
├── core/                 # Çekirdek modüller
│   ├── __init__.py
│   ├── appstore.py       # Ana AppStore sınıfı
│   ├── widgets.py        # UI widget'ları
│   └── dialogs.py        # Dialog pencereler
└── screenshots/          # Ekran görüntüleri
```

### Sınıf Hiyerarşisi
- **CloudAppStore**: Ana pencere sınıfı
- **AppDataManager**: Veri yönetimi (Clapp entegreli)
- **ModernAppCard**: Uygulama kartı widget'ı
- **StarRatingWidget**: Yıldız puanlama widget'ı
- **CategorySidebar**: Kategori kenar çubuğu
- **SearchBar**: Arama çubuğu
- **AppDetailDialog**: Uygulama detay dialog'u

## 🚀 Kullanım

### Standalone Test
```bash
python3 test_cloud_appstore.py
```

### Widget Test
```bash
python3 test_cloud_appstore.py widgets
```

### PyCloud OS İçinde
```python
from apps.app_store.core.appstore import CloudAppStore

# Kernel ile başlat (Clapp entegrasyonu otomatik)
appstore = CloudAppStore(kernel)
appstore.show()
```

## 🔧 Kurulum

### Gereksinimler
- Python 3.8+
- PyQt6
- PyCloud OS çekirdek modülleri
- Clapp modülleri (opsiyonel)

### Kurulum Adımları
1. PyCloud OS'i kurun
2. Clapp modüllerini aktif edin
3. AppStore'u apps/ dizinine yerleştirin
4. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install PyQt6
   ```

## 📊 Performans

### Optimizasyonlar
- **Lazy Loading**: Sadece görünen kartlar yüklenir
- **Thread Safety**: Tüm I/O işlemleri thread'lerde
- **Memory Management**: Otomatik widget temizliği
- **Responsive Grid**: Pencere boyutuna göre sütun sayısı
- **Clapp Cache**: Repository verileri önbelleklenir

## 🧪 Test Kapsamı

### Unit Testler
- Widget fonksiyonalitesi
- Veri yönetimi
- Tema sistemi
- Arama ve filtreleme
- Clapp entegrasyonu

### Integration Testler
- AppExplorer entegrasyonu
- Clapp Core işlemleri
- Repository yönetimi
- Kernel modül erişimi

## 🆚 Eski Clapp Store ile Karşılaştırma

| Özellik | Eski Clapp Store | Yeni App Store |
|---------|------------------|----------------|
| UI/UX | Basit liste | Modern 3 görünüm modu |
| Arama | Basit metin | Gerçek zamanlı + filtreler |
| Kategoriler | Yok | 13 kategori |
| Puanlama | Yok | 5 yıldızlı sistem |
| Yorumlar | Yok | Kullanıcı yorumları |
| Tema | Sabit | Koyu/açık otomatik |
| Clapp Entegrasyonu | Doğrudan | API üzerinden |
| Performans | Orta | Yüksek |

## 📈 Gelecek Özellikler

### v2.1.0
- [ ] Offline mod desteği
- [ ] Uygulama kategorisi önerileri
- [ ] Gelişmiş arama filtreleri
- [ ] Toplu işlemler

### v2.2.0
- [ ] Plugin sistemi
- [ ] Özel repository'ler
- [ ] Uygulama istatistikleri
- [ ] Sosyal özellikler

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📄 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakın.

---

**App Store v2.0.0** - PyCloud OS Modern Uygulama Mağazası (Clapp Entegreli) 