# AI Otomasyon Ajansı — Çok Modüllü Platform

Sıfır kod ile müşteri onboarding. Her müşteri için seçilen otomasyon modülleri Airtable üzerinden aktifleştirilir. Backend, Airtable konfigürasyonunu okuyarak sadece aktif modülleri çalıştırır.

## Mimari Özeti

```
Müşteri (X Kafe) ──> Airtable'da bir satır
                      ├─ Google_Yorum_Aktif: ✅
                      ├─ Instagram_Aktif: ❌
                      ├─ Prompt: "Sen X kafesisin..."
                      └─ API Key: ...

Backend ──> ModuleManager ──> Airtable'dan okur
                                ├─ X Kafe için: GMB modülü çalışır
                                └─ X Kafe için: Instagram modülü pasif

Müşteri Paneli (Softr) ──> Airtable verilerini okur
                             ├─ GMB grafikleri: Açık
                             └─ Instagram grafikleri: Kilitli/Gizli
```

## Teknoloji Özeti
- Backend: FastAPI + APScheduler
- LLM: Groq (Llama 3.3 70B) — ücretsiz katman
- Veritabanı & Admin Panel: Airtable (pyairtable)
- Müşteri Dashboard: Softr (Airtable'a bağlı no-code)
- Geliştirme Dashboard: Streamlit + Plotly
- SEO-GEO: Lokal SEO için konum ve anahtar kelime bazlı optimizasyon

## Proje Yapısı

```
GMB/
├── backend/
│   ├── main.py                     # FastAPI + scheduler (modül bağımsız)
│   ├── config.py                   # Ortam değişkenleri
│   ├── models.py                   # Pydantic modeller
│   ├── module_manager.py           # Modül yöneticisi (Airtable'dan okur)
│   ├── modules/                    # Tüm otomasyon modülleri
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseModule (tüm modüllerin arayüzü)
│   │   └── gmb_reviews/            # Modül 1: GMB Yorum Yanıtlama ✅
│   │       ├── __init__.py          # GMBModule sınıfı
│   │       ├── processor.py        # İş akışı (ReviewProcessor)
│   │       └── mock.py             # Sahte yorum üretici (MockGMB)
│   └── services/                   # Ortak servisler (tüm modüller kullanır)
│       ├── airtable_service.py     # Airtable CRUD
│       ├── llm_service.py          # LLM çağrıları (Groq)
│       ├── seo_service.py          # SEO skorlama
│       └── sentiment_service.py    # Sentiment analizi
├── dashboard/                      # Streamlit geliştirme dashboard'u
│   ├── app.py
│   ├── views/
│   └── components/
├── scripts/
│   └── seed_data.py
├── docs/
│   ├── merkezi-mimari-rehberi.md   # Detaylı mimari tasarım
│   └── proje-rehberi.md            # Junior seviyesi proje rehberi
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── CLAUDE.md                       # BU DOSYA
└── TODO.md
```

## Airtable Yapısı (Müşteri Yönetimi)

### Businesses Tablosu
| Alan | Tip | Açıklama |
|------|-----|----------|
| BusinessID | Text | Benzersiz ID |
| Name | Text | İşletme adı |
| Category | Select | Restoran/Kafe/Otel... |
| City | Text | Şehir |
| District | Text | İlçe |
| Keywords | Text | Hedef anahtar kelimeler |
| Tone | Select | Samimi/Profesyonel/Esprili |
| Language | Text | tr/en |
| CustomPrompt | LongText | İşletmeye özel prompt |
| Active | Checkbox | Genel aktif/pasif |
| **GMB_Active** | Checkbox | GMB modülü açık mı? |
| **GMB_API_Key** | Text | Google Business API key |
| **(Gelecek Modül)_Active** | Checkbox | Yeni modül açık mı? |
| CreatedAt | DateTime | Oluşturma tarihi |

**Kural**: Her yeni modül için Businesses tablosuna `{ModulAdi}_Active` checkbox'ı eklenir. Müşteri sadece ödediği modüllerde bu checkbox işaretlenir.

## Mevcut Modüller

### Modül 1: GMB Yorum Yanıtlama ✅ (Tamamlandı)
- Google My Business yorumlarına SEO-GEO uyumlu otomatik yanıt
- Sentiment analizi, özelleştirilebilir prompt, retry logic
- Modüler mimariye taşındı: `modules/gmb_reviews/`
- GMB_Active checkbox ile Airtable'dan açılıp kapatılabilir
- Mock veri üretici (test için) — Gerçek GMB API: Bekliyor

### Gelecek Modüller (Planlama Aşaması)
- Modül belirtilmedi. Her modül bu listeye eklenecek.

## Başlatma

```powershell
# 1. Proje dizini
cd C:\Users\ozcan\Desktop\GMB

# 2. Bağımlılıklar
pip install -r requirements.txt

# 3. .env kontrol (GROQ_API_KEY, AIRTABLE_API_KEY dolu olmalı)

# 4. API'yi başlat
uvicorn backend.main:app --reload

# 5. Dashboard'u başlat (geliştirme için)
$env:PYTHONIOENCODING = 'utf-8'; streamlit run dashboard/app.py
```

## Yeni Müşteri Ekleme (Sıfır Kod)

1. Airtable → Businesses tablosu → New Record
2. İşletme bilgilerini doldur (isim, kategori, şehir...)
3. Prompt'u yaz: "Sen X kafesisin, samimi dille konuş..."
4. Aktif etmek istediğin modülleri işaretle (örn: GMB_Active = ✅)
5. API key'leri gir
6. Sistem otomatik olarak yeni müşteri için çalışmaya başlar

## Yeni Modül Ekleme

1. `backend/modules/{modul_adi}/` dizinini oluştur
2. `BaseModule`'den kalıtım alan servis sınıfını yaz
3. Businesses tablosuna `{ModulAdi}_Active` checkbox'ı ekle
4. `module_manager.py`'e yeni modülü kaydet
5. Dashboard'a modüle özel view ekle

Detaylar için: `docs/merkezi-mimari-rehberi.md`
