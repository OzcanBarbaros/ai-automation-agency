# Merkezi Mimari Rehberi

> AI Otomasyon Ajansı — Çok modüllü, sıfır kod onboarding, Airtable merkezli platform mimarisi.
> Son güncelleme: 2026-05-21

---

## 1. Büyük Resim

Bu platformun amacı: **birden fazla AI otomasyon hizmetini, kod yazmadan, Airtable üzerinden yönetmek**.

Bir müşteri geldiğinde yapılacak tek şey Airtable'da bir satır açmak. Hangi modülleri istediğini işaretlemek. Sistem otomatik olarak o müşteri için ilgili modülleri çalıştırmaya başlar.

```
┌──────────────────────────────────────────────────────────────────┐
│                      AI OTOMASYON AJANSI PLATFORMU                │
│                                                                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐                    │
│   │ MODÜL 1  │   │ MODÜL 2  │   │ MODÜL N  │   ... her müşteri  │
│   │   GMB    │   │ (Gelecek)│   │ (Gelecek)│       seçtiği kadar │
│   │  Yorum   │   │          │   │          │       modül alır    │
│   └────┬─────┘   └────┬─────┘   └────┬─────┘                    │
│        │              │              │                            │
│   ┌────┴──────────────┴──────────────┴────────┐                   │
│   │            MODULE MANAGER                  │                   │
│   │  • Airtable'dan müşteri config'ini okur    │                   │
│   │  • Aktif modülleri belirler                │                   │
│   │  • Her müşteri için doğru modülleri çalıştırır │               │
│   │  • Scheduler'ı yönetir                     │                   │
│   └────────────────────┬───────────────────────┘                   │
│                        │                                          │
│   ┌────────────────────┴───────────────────────┐                   │
│   │                AIRTABLE                     │                   │
│   │                                            │                   │
│   │  ┌─────────────────────────────────────┐   │                   │
│   │  │ Businesses (Müşteri Konfigürasyonu) │   │                   │
│   │  │  - İşletme bilgileri                │   │                   │
│   │  │  - API anahtarları                  │   │                   │
│   │  │  - Prompt / Tone / Keywords         │   │                   │
│   │  │  - Modül toggle'ları:               │   │                   │
│   │  │    GMB_Active ☑ / Instagram_Active ☐ │   │                   │
│   │  └─────────────────────────────────────┘   │                   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐   │                   │
│   │  │ Reviews  │ │Resp.Logs │ │ (Modül X │   │                   │
│   │  │ (GMB)    │ │ (GMB)    │ │  Verisi) │   │                   │
│   │  └──────────┘ └──────────┘ └──────────┘   │                   │
│   └───────────────────────────────────────────┘                   │
│                                                                    │
│   ┌─────────────────┐              ┌─────────────────┐             │
│   │   ADMIN PANEL    │              │  MÜŞTERİ PANELİ  │             │
│   │   (Airtable)     │              │  (Softr)         │             │
│   │                  │              │                  │             │
│   │  • Müşteri ekle  │              │  • Sadece kendi  │             │
│   │  • Modül toggle  │              │    verilerini    │             │
│   │  • Prompt yaz    │              │    görür         │             │
│   │  • API key gir   │              │  • Ödemediği     │             │
│   │  • Tüm verileri  │              │    modüller      │             │
│   │    görebilir     │              │    kilitli       │             │
│   └─────────────────┘              └─────────────────┘             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Temel Prensipler

### 2.1 Sıfır Kod Onboarding
Yeni bir müşteri geldiğinde **hiçbir kod satırı değişmez**. Tüm konfigürasyon Airtable üzerinden yapılır:
1. Businesses tablosuna yeni satır eklenir
2. İşletme bilgileri girilir
3. Aktif edilecek modüller checkbox ile işaretlenir
4. Varsa API anahtarları girilir
5. Prompt özelleştirilir
6. Sistem otomatik olarak yeni müşteriyi işlemeye başlar

### 2.2 Modül Bağımsızlığı
Her modül birbirinden bağımsızdır:
- Kendi dizini vardır: `backend/modules/{modul_adi}/`
- Kendi Airtable tabloları olabilir
- Kendi scheduler job'ları vardır
- Bir modülün çökmesi diğerlerini etkilemez

### 2.3 Ortak Katman (Shared Services)
Modüllerin ortak kullandığı servisler `backend/services/` altındadır:
- `airtable_service.py` — Veritabanı işlemleri
- `llm_service.py` — LLM çağrıları
- `seo_service.py` — SEO skorlama (GMB modülü için)

### 2.4 Müşteri İzolasyonu
Her müşteri sadece kendi verilerini görür. Softr veya Streamlit dashboard, Airtable'daki `BusinessID` filtresi ile müşteriye özel veri gösterir. Ödenmemiş modüllerin verileri ve grafikleri müşteri panelinde gizlenir.

---

## 3. Airtable Veri Modeli

### 3.1 Businesses Tablosu (Merkezi Konfigürasyon)

| Alan Adı | Tip | Zorunlu | Açıklama |
|----------|-----|---------|----------|
| `BusinessID` | Single line text | Evet | Benzersiz ID (auto-generate) |
| `Name` | Single line text | Evet | İşletme adı |
| `Category` | Single select | Hayır | Restoran / Kafe / Otel / Berber / Market / Eczane / Diş Hekimi / Avukat / Dükkan / Diğer |
| `City` | Single line text | Hayır | Şehir (SEO-GEO için) |
| `District` | Single line text | Hayır | İlçe (SEO-GEO için) |
| `Address` | Long text | Hayır | Tam adres |
| `Keywords` | Single line text | Hayır | Hedef anahtar kelimeler (virgülle ayrılmış) |
| `Tone` | Single select | Hayır | Samimi / Profesyonel / Esprili |
| `Language` | Single line text | Hayır | tr / en (varsayılan: tr) |
| `CustomPrompt` | Long text | Hayır | İşletmeye özel LLM prompt'u |
| `Active` | Checkbox | Hayır | Genel aktif/pasif durumu |
| `GMB_Active` | Checkbox | Hayır | **Modül 1**: GMB yorum modülü aktif mi? |
| `GMB_API_Key` | Single line text | Hayır | Google Business API anahtarı (veya OAuth token) |
| `CreatedAt` | DateTime | Hayır | Oluşturma tarihi (auto) |

**Genişleme Kuralı**: Yeni bir modül eklendiğinde bu tabloya 1-2 alan eklenir:
- `{ModulAdi}_Active` (Checkbox) — her zaman
- `{ModulAdi}_API_Key` (Text) — API anahtarı gerekiyorsa

### 3.2 Modül Veri Tabloları

Her modülün kendi Airtable tabloları olur. Örneğin GMB modülü için:

**Reviews Tablosu** (GMB modülü)
| Alan | Tip | Açıklama |
|------|-----|----------|
| `ReviewID` | Text | Benzersiz yorum ID |
| `BusinessID` | Text | Hangi işletmeye ait |
| `ReviewerName` | Text | Yorumu yapan kişi |
| `Rating` | Number | 1-5 puan |
| `ReviewText` | LongText | Yorum metni |
| `ResponseText` | LongText | AI yanıtı |
| `Sentiment` | Select | Pozitif / Negatif / Nötr |
| `Status` | Select | Pending / Responded / Failed |
| `Source` | Select | Auto / Manual |
| `CreatedAt` | DateTime | Yorum tarihi |
| `RespondedAt` | DateTime | Yanıt tarihi |

**ResponseLogs Tablosu** (GMB modülü)
| Alan | Tip | Açıklama |
|------|-----|----------|
| `LogID` | Text | Benzersiz log ID |
| `ReviewID` | Text | Hangi yoruma ait |
| `BusinessID` | Text | Hangi işletmeye ait |
| `PromptTokens` | Number | LLM prompt token |
| `CompletionTokens` | Number | LLM yanıt token |
| `LatencyMs` | Number | Yanıt süresi (ms) |
| `SEOScore` | Number | SEO puanı (0-100) |
| `KeywordsUsed` | Text | Kullanılan anahtar kelimeler |
| `LocationMentioned` | Checkbox | Konum geçti mi? |
| `CreatedAt` | DateTime | Log tarihi |

### 3.3 Müşteri Dashboard'u için Airtable View'ları

Softr'un belirli bir müşterinin verilerini gösterebilmesi için Airtable'da **filtrelenmiş view'lar** oluşturulur. Softr, URL parametresi veya kullanıcı eşleştirmesi ile doğru view'ı gösterir.

Alternatif olarak, her müşteri için Softr'da ayrı bir sayfa oluşturulup Airtable'daki `BusinessID` filtresi ile o müşterinin verileri gösterilir. Modül grafikleri sadece o modülün `_Active` checkbox'ı işaretliyse görünür.

---

## 4. Backend Modül Mimarisi

### 4.1 BaseModule Arayüzü

Tüm modüllerin uyması gereken standart arayüz:

```python
# backend/modules/base.py

from abc import ABC, abstractmethod
from typing import Optional

class BaseModule(ABC):
    """Tüm otomasyon modüllerinin temel sınıfı."""

    # Modül metadata
    MODULE_ID: str = "base"           # Benzersiz modül kimliği
    MODULE_NAME: str = "Base Module"  # İnsan okunur isim
    VERSION: str = "1.0.0"

    def __init__(self, business_config: dict):
        """
        business_config: Airtable'dan gelen işletme ayarları
        (Name, Category, City, CustomPrompt, API key'ler vs.)
        """
        self.config = business_config
        self.business_id = business_config.get("BusinessID")

    @abstractmethod
    def is_active(self) -> bool:
        """Bu modül bu işletme için aktif mi? Airtable'daki checkbox'ı kontrol eder."""
        ...

    @abstractmethod
    def start(self):
        """Modülü başlat (scheduler job'larını ekle, listener'ları aç vs.)"""
        ...

    @abstractmethod
    def stop(self):
        """Modülü durdur (job'ları kaldır, bağlantıları kapat vs.)"""
        ...

    @abstractmethod
    def process(self):
        """Ana işlem döngüsü (scheduler tarafından çağrılır)."""
        ...

    def health_check(self) -> dict:
        """Modül sağlık durumu. Opsiyonel, her modül override edebilir."""
        return {"module": self.MODULE_ID, "status": "ok"}
```

### 4.2 ModuleManager

Tüm modülleri yöneten merkezi sınıf:

```python
# backend/module_manager.py

class ModuleManager:
    """
    Airtable'dan tüm işletmeleri okur.
    Her işletme için aktif modülleri belirler.
    Scheduler'ı yapılandırır.
    """

    def __init__(self):
        self.airtable = AirtableService()
        self.modules: dict[str, list[BaseModule]] = {}  # business_id -> [modül, modül, ...]
        self.scheduler = BackgroundScheduler()

    def load_all_businesses(self):
        """Airtable'dan tüm aktif işletmeleri çek, modüllerini yükle."""
        businesses = self.airtable.list_businesses(active_only=True)
        for business in businesses:
            self.load_modules_for_business(business)

    def load_modules_for_business(self, business_config: dict):
        """Bir işletme için hangi modüller aktifse onları yükle."""
        # Örnek: GMB modülü
        if business_config.get("GMB_Active"):
            module = GMBModule(business_config)
            self._register_module(business_config["BusinessID"], module)
        # Gelecek: Instagram modülü
        # if business_config.get("Instagram_Active"):
        #     module = InstagramModule(business_config)
        #     self._register_module(...)

    def _register_module(self, business_id: str, module: BaseModule):
        """Modülü kaydet ve scheduler job'unu ekle."""
        if business_id not in self.modules:
            self.modules[business_id] = []
        self.modules[business_id].append(module)
        module.start()
        # Scheduler'a bu modülün process job'unu ekle
        self.scheduler.add_job(
            module.process,
            'interval',
            seconds=module.POLL_INTERVAL,  # Her modül kendi interval'ini belirler
            id=f"{business_id}_{module.MODULE_ID}",
        )

    def add_business(self, business_config: dict):
        """Yeni bir işletme eklendiğinde çağrılır (Airtable webhook veya polling ile)."""
        self.load_modules_for_business(business_config)

    def remove_business(self, business_id: str):
        """İşletme pasif yapıldığında tüm modüllerini durdur."""
        if business_id in self.modules:
            for module in self.modules[business_id]:
                module.stop()
                self.scheduler.remove_job(f"{business_id}_{module.MODULE_ID}")
            del self.modules[business_id]

    def start(self):
        """Tüm sistemi başlat."""
        self.load_all_businesses()
        self.scheduler.start()

    def stop(self):
        """Tüm sistemi durdur."""
        for modules in self.modules.values():
            for m in modules:
                m.stop()
        self.scheduler.shutdown(wait=False)
```

### 4.3 Örnek Modül Implementasyonu (GMB)

```python
# backend/modules/gmb_reviews/__init__.py

from backend.modules.base import BaseModule

class GMBModule(BaseModule):
    MODULE_ID = "gmb_reviews"
    MODULE_NAME = "GMB Yorum Yanıtlama"
    VERSION = "1.0.0"
    POLL_INTERVAL = 90  # saniyede bir kontrol

    def is_active(self) -> bool:
        return self.config.get("GMB_Active", False)

    def start(self):
        # Gerçek GMB API bağlantısını kur
        # Mock veri üreticiyi başlat
        pass

    def stop(self):
        # Bağlantıları kapat
        pass

    def process(self):
        # 1. GMB'den yeni yorumları çek
        # 2. Sentiment analizi yap
        # 3. LLM ile yanıt üret
        # 4. Airtable'a kaydet
        pass
```

---

## 5. Dashboard Mimarisi

İki ayrı dashboard vardır:

### 5.1 Geliştirme Dashboard'u (Streamlit — şu anki)

Amaç: Sistemi geliştirirken test etmek ve debug etmek için.
- Tüm işletmeleri ve tüm verileri gösterir
- Admin yetkileriyle çalışır
- `dashboard/app.py` ile başlatılır

Modül farkındalığı:
- Dashboard, Airtable'dan işletmenin hangi modüllerinin aktif olduğunu okur
- Pasif modüllere ait sayfalar/sekmeler gri renkte veya "(Pasif)" etiketiyle gösterilir
- Modül ekleme/çıkarma işlemleri için UI sunar

### 5.2 Müşteri Dashboard'u (Softr — üretimde)

Amaç: Müşterinin kendi verilerini görmesi için no-code arayüz.
- Softr doğrudan Airtable'a bağlanır
- Her müşteri sadece kendi `BusinessID`'sine ait verileri görür
- Hangi modüller aktifse onların grafikleri/metrikleri görünür
- Pasif modüller kilitli veya gizli olur

**Softr-Airtable Entegrasyonu:**
1. Softr'da her müşteri için bir kullanıcı hesabı oluşturulur
2. Kullanıcının email'i Airtable'daki Businesses tablosunda bir alana kaydedilir
3. Softr, kullanıcının email'i ile Airtable'daki `BusinessID`'yi eşleştirir
4. Tüm veri görüntülemeleri bu `BusinessID` filtresi ile çalışır
5. Modül grafikleri, Airtable'daki `{Modul}_Active` checkbox'ına göre koşullu gösterilir

---

## 6. Veri Akışı

### 6.1 Yeni Müşteri Onboarding Akışı

```
1. Admin Airtable'da "New Record" oluşturur
2. İşletme bilgilerini girer (isim, şehir, kategori...)
3. Prompt'u yazar: "Sen X kafesisin..."
4. GMB_Active checkbox'ını işaretler
5. GMB_API_Key alanına API anahtarını girer
6. Airtable kaydı oluşur
7. ModuleManager (polling veya webhook ile) yeni kaydı algılar
8. GMBModule instance'ı oluşturulur
9. Scheduler'a job eklenir
10. Sistem çalışmaya başlar
```

### 6.2 GMB Yorum Yanıtlama Akışı (Modül 1 Örneği)

```
Scheduler tetikler (her 90 sn)
  │
  ▼
GMBModule.process()
  │
  ├─→ [Gerçek API] GMB'den yeni yorumları çek
  │   veya [Mock] Rastgele yorum üret
  │
  ├─→ Airtable: Reviews tablosuna ekle (Status: Pending)
  │
  ├─→ SentimentService: Rating + keyword analizi
  │
  ├─→ LLMService: Prompt oluştur → Groq API → Yanıt üret
  │   (Prompt içinde: business config, SEO-GEO keywords, tone, custom_prompt)
  │
  ├─→ SEOService: Yanıtı skorla (keyword kullanımı, konum geçiyor mu?)
  │
  ├─→ Airtable: Reviews güncelle (Status: Responded, ResponseText: ...)
  │
  └─→ Airtable: ResponseLogs ekle (SEOScore, LatencyMs, KeywordsUsed...)
```

### 6.3 Müşteri Dashboard Veri Akışı

```
Müşteri → Softr'a giriş yapar (email ile)
  │
  ▼
Softr → Airtable'a bağlanır
  │
  ├─→ Businesses tablosu: Email eşleşmesi → BusinessID bulunur
  │
  ├─→ BusinessID filtresi ile:
  │   ├─ Reviews tablosundan yorumlar
  │   ├─ ResponseLogs tablosundan metrikler
  │   └─ (Diğer modül tablolarından ilgili veriler)
  │
  └─→ Koşullu gösterim:
      ├─ GMB_Active = ✅ → Yorum paneli, SEO grafikleri GÖSTER
      ├─ Instagram_Active = ❌ → Instagram paneli GİZLE/KİLİTLE
      └─ (Her modül için aynı mantık)
```

---

## 7. Güvenlik ve İzolasyon

| Katman | Yöntem | Açıklama |
|--------|--------|----------|
| **Müşteri verisi** | BusinessID filtresi | Her Airtable sorgusu BusinessID ile filtrelenir |
| **API anahtarları** | Airtable'da saklanır | .env'de DEĞİL, müşteri bazında Airtable'da |
| **LLM prompt'ları** | İşletme bazlı izole | Her işletmenin kendi prompt'u, kendi API key'i |
| **Modül izolasyonu** | try/catch sarmalı | Bir modüldeki hata diğer modülü etkilemez |
| **Rate limit** | İşletme bazlı kuyruk | Her işletme için ayrı rate limit sayacı |

---

## 8. Yeni Modül Ekleme Checklist'i

Yeni bir `{MODUL}` modülü eklerken yapılacaklar:

```
☐ 1. backend/modules/{modul_adi}/ dizinini oluştur
☐ 2. BaseModule'den kalıtım alan sınıfı yaz (__init__.py, service.py, processor.py)
☐ 3. Airtable Businesses tablosuna {ModulAdi}_Active checkbox'ı ekle
☐ 4. Gerekirse {ModulAdi}_API_Key alanı ekle
☐ 5. Gerekirse yeni Airtable tablosu oluştur (örn: InstagramPosts)
☐ 6. module_manager.py'de load_modules_for_business() metoduna ekle
☐ 7. Dashboard'da modüle özel sayfa/sekme ekle
☐ 8. Dashboard'da {ModulAdi}_Active kontrolü ile göster/gizle
☐ 9. Softr'da müşteri dashboard'una modül panelini ekle (koşullu gösterim)
☐ 10. Test: Airtable'dan checkbox'ı işaretle, modülün çalıştığını doğrula
☐ 11. Test: Checkbox'ı kaldır, modülün durduğunu doğrula
☐ 12. Bu rehberi güncelle (mevcut modüller listesi)
```

---

## 9. Deployment Mimarisi (Gelecek)

```
┌─────────────────────────────────────────┐
│              RAILWAY / RENDER            │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  FastAPI Backend (Tek instance)  │   │
│  │  - ModuleManager                 │   │
│  │  - APScheduler                   │   │
│  │  - Tüm aktif modüller            │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  Streamlit Dashboard (Opsiyonel) │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   ┌──────────┐      ┌──────────┐
   │ AIRTABLE │      │  GROQ    │
   │ (Veri +  │      │  (LLM)   │
   │  Config) │      └──────────┘
   └──────────┘
         │
         ▼
   ┌──────────┐
   │  SOFTR   │
   │ (Müşteri │
   │  Paneli) │
   └──────────┘
```

---

## 10. Önemli Kararlar ve Gerekçeleri

| Karar | Gerekçe |
|-------|---------|
| **Airtable merkezi config** | Kod değiştirmeden müşteri eklemek için. UI'ı hazır, API'si var, Softr ile entegre. |
| **Softr müşteri dashboard'u** | Sıfır kod. Airtable'a doğrudan bağlanır. Müşteriye özel dashboard geliştirmeye gerek kalmaz. |
| **Groq / Llama 3.3 70B** | Ücretsiz katman, yüksek limit. Gemini'nin 20 istek/gün limiti üretim için yetersiz. |
| **Her modül ayrı dizin** | Bağımsız geliştirme, bağımsız hata yönetimi, kolay ekleme/çıkarma. |
| **Modül başına POLL_INTERVAL** | Her modülün kontrol sıklığı farklıdır (GMB: 90sn, Instagram DM: 30sn, vs.). |
| **Streamlit geliştirme dashboard'u** | Admin için hızlı debug ve test imkanı. Üretimde asıl dashboard Softr. |

---

## 11. Mevcut Modüller

| # | Modül ID | İsim | Versiyon | Durum |
|---|----------|------|----------|-------|
| 1 | `gmb_reviews` | GMB Yorum Yanıtlama | 1.0.0 | ✅ Tamamlandı (gerçek API hariç) |

---

*Bu doküman, sistem büyüdükçe güncellenecektir. Her yeni modül eklendiğinde "Mevcut Modüller" tablosu ve Airtable şeması güncellenmelidir.*
