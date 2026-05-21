# Proje Rehberi

> Bu rehber, projeye yeni başlayan bir yazılımcının projeyi anlaması için yazıldı. Teknik terimler açıklandı, her dosyanın ne işe yaradığı sade bir dille anlatıldı.

---

## 1. Bu Proje Ne Yapıyor?

Bu bir **AI Otomasyon Ajansı** platformu. Farklı işletmelere, farklı yapay zeka otomasyon hizmetleri satıyoruz.

Şu anda tek bir hizmetimiz var: **Google My Business yorumlarına otomatik cevap verme.**

Sistem şöyle çalışıyor:
1. Bir işletmenin Google yorumlarına yapay zeka otomatik cevap yazıyor
2. Cevaplar SEO'ya uygun oluyor (işletmenin bulunduğu şehir ve anahtar kelimeler geçiyor)
3. Tüm veriler Airtable'da tutuluyor
4. Admin ve müşteri dashboard'ları üzerinden takip ediliyor

**Gelecek planı:** Bu platforma yeni otomasyon modülleri eklenecek (örnek: Instagram DM otomasyonu, Facebook yorum otomasyonu). Her müşteri sadece istediği modülü satın alacak. Sistem şimdiden bu modüler yapıya uygun şekilde tasarlandı.

---

## 2. Kullanılan Teknolojiler (Kısaca)

| Teknoloji | Ne için kullanılıyor? |
|-----------|----------------------|
| **FastAPI** | Backend API. Dış dünyayla haberleşmeyi sağlayan sunucu. |
| **Groq / Llama 3.3** | Yapay zeka. Yorumlara cevap yazan beyin. Ücretsiz katman kullanıyoruz. |
| **Airtable** | Veritabanı. Hem verileri tutuyor, hem de admin paneli olarak kullanılıyor. |
| **APScheduler** | Zamanlayıcı. "Her 90 saniyede bir yeni yorumları kontrol et" gibi görevleri yönetiyor. |
| **Streamlit** | Dashboard. Geliştirme ve demo amaçlı arayüz. |
| **Plotly** | Grafik kütüphanesi. Dashboard'daki çizgi/pasta/bar grafikleri bununla yapılıyor. |
| **Softr** | Müşteri dashboard'u (planlanan). Kod yazmadan Airtable verilerini gösteren bir arayüz. |

---

## 3. Dosya Yapısı

Projeyi açtığında göreceğin klasör ve dosyalar şöyle:

```
GMB/
│
├── backend/                        # Sunucu tarafı — asıl iş burada dönüyor
│   ├── main.py                     # Uygulamanın giriş kapısı. API burada başlıyor.
│   ├── config.py                   # Ayarlar. API anahtarları buradan okunuyor.
│   ├── models.py                   # Veri şablonları. İşletme, yorum, log gibi tiplerin tanımı.
│   ├── module_manager.py           # Modül yöneticisi. Hangi hizmet aktif, onu kontrol ediyor.
│   │
│   ├── modules/                    # OTOMASYON MODÜLLERİ (her hizmet ayrı bir klasör)
│   │   ├── base.py                 # Temel modül şablonu. Tüm modüller buna uymak zorunda.
│   │   └── gmb_reviews/           # Modül 1: Google yorumlarına cevap verme
│   │       ├── __init__.py         # Modülün kimlik kartı (adı, versiyonu, aktif mi?)
│   │       ├── processor.py        # İş akışı. Yorumu al → AI cevap yaz → kaydet
│   │       └── mock.py            # Sahte yorum üretici (test için, gerçek API yokken)
│   │
│   └── services/                  # ORTAK ARAÇLAR (tüm modüllerin kullandığı)
│       ├── airtable_service.py    # Airtable ile haberleşme. Veri okuma/yazma.
│       ├── llm_service.py         # Yapay zeka ile haberleşme. Groq'ya soru sorup cevap alma.
│       ├── seo_service.py         # SEO puanlaması. Cevap ne kadar SEO'lu, 0-100 puan.
│       └── sentiment_service.py   # Duygu analizi. Yorum pozitif mi negatif mi?
│
├── dashboard/                     # Görsel arayüz (geliştirme ve demo için)
│   ├── app.py                     # Dashboard'un ana sayfası, menü yapısı
│   ├── views/                     # Sayfalar
│   │   ├── overview.py            # Özet sayfası — genel durum, grafikler
│   │   ├── reviews.py             # Yorum listesi ve manuel yorum ekleme
│   │   ├── businesses.py          # İşletme listesi ve yeni işletme ekleme
│   │   └── reports.py             # Detaylı raporlar, SEO analizi, karşılaştırmalar
│   └── components/                # Ortak bileşenler
│       └── charts.py              # Tüm grafikler burada (7 farklı grafik tipi)
│
├── scripts/                       # Yardımcı komut dosyaları
│   └── seed_data.py               # Demo veri oluşturucu. Sistemi test etmek için.
│
├── docs/                          # Dokümantasyon
│   ├── merkezi-mimari-rehberi.md   # Mimari tasarım ve modül ekleme rehberi
│   └── proje-rehberi.md            # BU DOSYA
│
├── requirements.txt                # Gerekli Python kütüphanelerinin listesi
├── .env                            # Gizli anahtarlar (bu dosya GitHub'a GİTMEZ!)
├── .env.example                    # .env'in şablonu (bu GitHub'a gider)
├── .gitignore                      # Hangi dosyalar GitHub'a gitmesin?
├── CLAUDE.md                       # Claude Code için proje talimatları
└── TODO.md                         # Yapılacaklar listesi ve proje durumu
```

---

## 4. Sistem Nasıl Çalışıyor? (Adım Adım)

### Otomatik Çalışma (Arka Planda)

Her 90 saniyede bir şunlar oluyor:

```
1. Zamanlayıcı tetikleniyor (APScheduler)
        │
2. ModuleManager "hangi modüller aktif?" diye kontrol ediyor
        │
3. GMB modülü aktifse çalışmaya başlıyor:
        │
        ├── 2 adet sahte yorum üretiliyor (test amaçlı, gerçek API gelince değişecek)
        │
        └── Bekleyen tüm yorumlar sırayla işleniyor:
              │
              ├── Duygu analizi: Yorum pozitif mi, negatif mi?
              ├── AI cevap yazıyor (Groq/Llama)
              ├── Cevap SEO puanlamasından geçiyor (şehir geçmiş mi? anahtar kelime var mı?)
              └── Her şey Airtable'a kaydediliyor
```

### Dashboard'dan Manuel Kullanım

Dashboard açıkken bir yorumu elle ekleyip anında AI cevabı alabiliyorsun. Bu özellik demo ve test için.

---

## 5. Katman Katman Proje

Proje 4 ana katmandan oluşuyor. Her katmanın ne iş yaptığını ve neden ayrı olduğunu anlatalım:

### Katman 1: API (backend/main.py)

**Görevi:** Dış dünyayla konuşmak. Dashboard, script'ler veya başka uygulamalar bu API üzerinden sisteme bağlanır.

API'nin sunduğu temel işlemler:
- İşletme listesini getir, yeni işletme ekle, güncelle
- Yorum listesini getir (filtreli), manuel yorum ekle
- Özet istatistikleri getir (kaç yorum, kaçı yanıtlandı, SEO ortalaması)
- Grafik verilerini getir
- Manuel olarak "şimdi yorumları işle" tetiklemesi yap

### Katman 2: Modüller (backend/modules/)

**Görevi:** Asıl işi yapmak. Her otomasyon hizmeti ayrı bir modül.

Şu anda sadece `gmb_reviews` modülü var. Bu modülün içinde:
- **processor.py:** Bir yorum geldiğinde yapılacak tüm işlemlerin sırasını belirler (iş akışı/pipeline)
- **mock.py:** Gerçek Google API'si henüz bağlı olmadığı için, test amaçlı sahte yorumlar üretir

Yeni bir hizmet (mesela Instagram DM) eklendiğinde, `modules/instagram_dm/` diye yeni bir klasör açılacak. Mevcut koda dokunulmayacak.

### Katman 3: Ortak Servisler (backend/services/)

**Görevi:** Tüm modüllerin kullanabileceği ortak araçlar.

Buradaki hiçbir şey GMB'ye özel değil. Yeni bir modül eklendiğinde buradaki servisleri olduğu gibi kullanabilir.

- **airtable_service.py:** Airtable'daki tablolara veri yazıp okumak için tüm fonksiyonlar burada
- **llm_service.py:** Yapay zekaya soru sormak için. Prompt'u hazırlar, Groq API'ye gönderir, cevabı alır. Rate limit aşımında otomatik tekrar dener.
- **seo_service.py:** AI'ın yazdığı cevabı SEO açısından puanlar
- **sentiment_service.py:** Yorumun duygusunu analiz eder

### Katman 4: Dashboard (dashboard/)

**Görevi:** İnsanların görebileceği bir arayüz sunmak.

4 sayfadan oluşur:
- **Özet:** Büyük resim — kaç yorum var, kaçı yanıtlandı, ortalama puan kaç, bugün ne oldu?
- **Yorumlar:** Tüm yorumları listeler, manuel yorum eklemeye izin verir
- **İşletmeler:** İşletmeleri listeler, yeni işletme eklemeye izin verir
- **Raporlar:** Detaylı analiz — SEO trendi, işletme karşılaştırması, en çok kullanılan kelimeler

Tüm grafikler `components/charts.py` dosyasında toplanmıştır. Bir grafiği değiştirmek istersen tek bir yerden değiştirirsin.

---

## 6. Veri Nerede Duruyor?

Tüm veriler **Airtable**'da. 3 ana tablo var:

| Tablo | Ne tutuyor? |
|-------|-------------|
| **Businesses** | İşletme bilgileri + hangi modüllerin aktif olduğu + AI prompt ayarları |
| **Reviews** | Gelen yorumlar ve AI'ın yazdığı cevaplar |
| **ResponseLogs** | Her cevap için metrikler (SEO puanı, ne kadar sürdü, kaç token harcandı) |

Airtable aynı zamanda **admin paneli** olarak da kullanılıyor. Yeni bir müşteri eklemek için Airtable'da Businesses tablosuna bir satır eklemek yeterli — kod değişmiyor.

---

## 7. Önemli Kavramlar

### Modül Sistemi

Projedeki en önemli tasarım kararı. Her otomasyon hizmeti bir "modül". Modüller:
- Birbirinden bağımsız çalışır
- Airtable'dan açılıp kapatılabilir
- Kendi dosyaları vardır, diğer modüllere karışmaz

### SEO-GEO Skorlaması

AI'ın yazdığı cevap SEO açısından 0-100 arası puanlanır. Puanlama şöyle:

| Kriter | Puan |
|--------|------|
| Cevapta şehir veya ilçe adı geçiyor mu? | 40 |
| İşletmenin anahtar kelimeleri kullanılmış mı? | 30 |
| Konum ve hizmet aynı cümlede mi? | 20 |
| Anahtar kelime aşırı tekrar cezası | -20 |

Amaç: Cevap hem samimi olsun, hem de Google'da işletmenin görünürlüğünü artırsın.

### Rate Limit Yönetimi

Groq'un ücretsiz katmanı dakikada 5 istekle sınırlı. LLM servisi bu limite takılmamak için:
1. "Çok istek attın" hatası alınca bir süre bekler
2. Her bekleyişte süreyi ikiye katlar (1 sn → 2 sn → 4 sn)
3. 3 kere dener, olmazsa o yorumu "Failed" olarak işaretler
4. Failed yorumlar daha sonra `/api/retry-failed` ile tekrar denenebilir

---

## 8. Sık Kullanılan Komutlar

### Projeyi Çalıştırmak

```powershell
# 1. Proje klasörüne git
cd C:\Users\ozcan\Desktop\GMB

# 2. Kütüphaneleri yükle (ilk kez veya yenilendiyse)
pip install -r requirements.txt

# 3. API sunucusunu başlat (1. terminal penceresi)
uvicorn backend.main:app --reload

# 4. Dashboard'u başlat (2. terminal penceresi)
$env:PYTHONIOENCODING = 'utf-8'; streamlit run dashboard/app.py
```

### Demo Veri Oluşturmak

```powershell
# Airtable'da veri yoksa, 4 işletme + 12 yorum oluşturur
$env:PYTHONIOENCODING = 'utf-8'; python scripts/seed_data.py
```

### Başarısız Yorumları Tekrar Denemek

```powershell
curl -X POST http://localhost:8000/api/retry-failed
```

---

## 9. Bağlantılar

| Ne | Adres |
|----|-------|
| API Sunucusu | http://localhost:8000 |
| API Dokümantasyonu (Otomatik) | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |
| Groq (AI) Kontrol Paneli | https://console.groq.com/keys |
| Airtable | https://airtable.com |
| GitHub Repo | https://github.com/OzcanBarbaros/ai-automation-agency |

---

## 10. Dikkat Edilmesi Gerekenler

1. **`.env` dosyası gizlidir, GitHub'a gitmez.** İçinde Groq ve Airtable API anahtarları var. `.gitignore` sayesinde korunuyor.

2. **Streamlit klasör ismi `views/` olmak zorunda.** Streamlit `pages/` diye bir klasör görürse otomatik sayfa olarak algılayıp çakışma çıkarıyor. O yüzden `views/` kullanıyoruz.

3. **Windows'ta Türkçe karakter sorunu:** Dashboard'u başlatırken mutlaka `$env:PYTHONIOENCODING = 'utf-8'` yaz. Yoksa ı, ş, ç, ğ gibi harfler hata verir.

4. **GMB modülü şu anda sahte veriyle çalışıyor.** Gerçek Google Business API entegrasyonu henüz yapılmadı. `gmb_reviews/mock.py` rastgele yorum üretiyor. Gerçek API bağlandığında bu dosyanın yanına bir `api.py` eklenecek.

5. **Yeni müşteri = Airtable'da bir satır.** Kod açıp değiştirmeye gerek yok. Airtable'dan Businesses tablosuna yeni kayıt ekle, hangi modülleri istediğini checkbox'tan işaretle, sistem otomatik başlasın.
