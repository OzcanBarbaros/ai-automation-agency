# AI Otomasyon Ajansı — Durum ve Yapılacaklar

> Son güncelleme: 2026-05-21 — Modül 1 (GMB) tamam, çok modüllü mimari planlandı

---

## Proje Özeti

Çok modüllü AI Otomasyon Ajansı platformu. Her müşteri istediği modülü seçer, Airtable üzerinden sıfır kod ile onboard edilir. Backend sadece aktif modülleri çalıştırır. Müşteri dashboard'u Softr ile Airtable'a bağlanır.

---

## Modül Durumu

| # | Modül | Durum | Açıklama |
|---|-------|-------|----------|
| 1 | **GMB Yorum Yanıtlama** | ✅ Tamamlandı | Google My Business yorumlarına Groq/Llama 3.3 ile SEO-GEO uyumlu otomatik yanıt |
| 2 | (Tanımlanmadı) | ⏳ Bekliyor | Bir sonraki modül bitiminde belirlenecek |
| N | (Tanımlanmadı) | ⏳ Bekliyor | |

---

## Modül 1 — GMB Yorum Yanıtlama ✅

### Çalışan Özellikler
- [x] Proje iskeleti (18 dosya) tamam
- [x] FastAPI tüm endpoint'ler çalışıyor
- [x] Airtable CRUD (Businesses, Reviews, ResponseLogs)
- [x] Groq / Llama 3.3 70B entegrasyonu
- [x] SEO-GEO prompt template
- [x] SEO skorlama servisi
- [x] Mock GMB yorum üreticisi
- [x] Streamlit Dashboard (4 sayfa)
- [x] APScheduler arka plan işleri
- [x] Sentiment analizi (rating + keyword hibrit)
- [x] Retry logic (exponential backoff, 429/503 handling)
- [x] CustomPrompt çalışıyor

### Bekleyen
- [ ] Gerçek GMB API entegrasyonu (`backend/modules/gmb_reviews/api.py`)
- [ ] Cloud deployment

---

## Mimari Geçiş Planı

### Kısa Vade (şu an - 1 hafta)
- [ ] `backend/modules/` dizin yapısını oluştur
- [ ] `backend/modules/base.py` — BaseModule abstract class
- [ ] Mevcut GMB kodunu `backend/modules/gmb_reviews/` altına taşı
- [ ] `backend/module_manager.py` — Airtable'dan modül durumlarını okuyan yönetici
- [ ] Airtable Businesses tablosuna `GMB_Active` checkbox'ı ekle
- [ ] Scheduler'ı module_manager'a bağla (sadece aktif modüller çalışsın)

### Orta Vade (1-4 hafta)
- [ ] Dashboard'u modül farkındalıklı hale getir (pasif modüller gizli)
- [ ] Softr müşteri dashboard'u için Airtable view'ları hazırla
- [ ] Gerçek GMB API entegrasyonu
- [ ] Her modül için ayrı loglama ve metrik takibi

### Uzun Vade (1-6 ay)
- [ ] Cloud deployment (Railway/Render)
- [ ] OAuth 2.0 — işletme GMB hesabına bağlanma
- [ ] E-posta/Slack bildirimleri (yeni olaylarda)
- [ ] Müşteri bazlı rate limit ve kota yönetimi

---

## Proje Yapısı (Güncel → Hedef)

```
GMB/
├── backend/
│   ├── main.py                     # FastAPI app + scheduler
│   ├── config.py                   # Ortam değişkenleri
│   ├── models.py                   # Pydantic modeller
│   ├── module_manager.py           # [YENİ] Modül yöneticisi
│   ├── modules/                    # [YENİ] Tüm otomasyon modülleri
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseModule abstract class
│   │   └── gmb_reviews/            # Modül 1 (mevcut kodun taşınmış hali)
│   │       ├── __init__.py
│   │       ├── service.py          # GMB modül servisi
│   │       ├── processor.py        # İş akışı (review_processor'dan)
│   │       ├── mock.py             # Mock yorum üretici (gmb_mock'tan)
│   │       └── api.py              # [YENİ] Gerçek GMB API entegrasyonu
│   └── services/                   # Ortak servisler
│       ├── airtable_service.py     # Airtable CRUD
│       ├── llm_service.py          # LLM çağrıları
│       └── seo_service.py          # SEO skorlama
├── dashboard/                      # Streamlit geliştirme dashboard'u
│   ├── app.py
│   ├── views/
│   └── components/
├── scripts/
│   └── seed_data.py
├── docs/
│   └── merkezi-mimari-rehberi.md   # [YENİ] Detaylı mimari dokümanı
├── requirements.txt
├── .env.example
├── .env
├── CLAUDE.md
└── TODO.md                         # BU DOSYA
```

---

## Hızlı Başlangıç

```powershell
# 1. Proje dizini
cd C:\Users\ozcan\Desktop\GMB

# 2. Bağımlılıklar (gerekirse)
pip install -r requirements.txt

# 3. .env kontrol (GROQ_API_KEY dolu olmalı)

# 4. API'yi başlat (1. terminal)
uvicorn backend.main:app --reload

# 5. Dashboard'u başlat (2. terminal)
$env:PYTHONIOENCODING = 'utf-8'; streamlit run dashboard/app.py

# 6. Seed data (Airtable boşsa)
$env:PYTHONIOENCODING = 'utf-8'; python scripts/seed_data.py
```

## URL'ler

| Servis | URL |
|--------|-----|
| FastAPI | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |
| Groq Console | https://console.groq.com/keys |
| Airtable | https://airtable.com |

---

## Geçmiş Session Özeti

### Session 1 — Proje Kurulumu
- 17 dosyalı proje iskeleti oluşturuldu
- FastAPI + Streamlit + Airtable + Gemini entegrasyonu
- 6 hata çözüldü

### Session 2 — Bug Fix ve Groq Geçişi
- Sentiment fix, rate limiting fix, CustomPrompt fix
- Gemini → Groq/Llama 3.3 70B geçişi
- Dashboard pages/ → views/ rename
- Test: 12/12 yorum Groq ile sorunsuz yanıtlandı

### Session 3 — Çok Modüllü Mimari Planlaması
- CLAUDE.md, TODO.md güncellendi
- Merkezi Mimari Rehberi oluşturuldu
- Modül sistemi ve Airtable-based müşteri yönetimi tasarlandı
- Sıfır kod onboarding mimarisi dokümante edildi

---

## Bilinen Sorunlar

1. **Windows konsol encoding**: Emoji/özel karakterler → `$env:PYTHONIOENCODING = 'utf-8'`
2. **Streamlit sürümü**: 1.43.0'a sabitlendi
3. **Gemini servisi hala diskte**: `backend/services/gemini_service.py` artık kullanılmıyor, silinebilir
