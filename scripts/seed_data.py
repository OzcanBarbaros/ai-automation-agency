"""
Demo veri olusturma scripti.
Calistirmadan once .env dosyasinda Airtable ve Groq API key'lerini ayarlayin.
Airtable'da su tablolarin olusturulmus olmasi gerekir:
  - Businesses (alanlar: BusinessID, Name, Category, City, District, Address,
    Keywords, Tone, Language, CustomPrompt, Active, CreatedAt)
  - Reviews (alanlar: ReviewID, BusinessID, ReviewerName, Rating, ReviewText,
    ResponseText, Sentiment, Status, Source, CreatedAt, RespondedAt)
  - ResponseLogs (alanlar: LogID, ReviewID, BusinessID, PromptTokens,
    CompletionTokens, LatencyMs, SEOScore, KeywordsUsed, LocationMentioned, CreatedAt)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.airtable_service import AirtableService
from backend.modules.gmb_reviews.mock import MockGMB
from backend.modules.gmb_reviews.processor import ReviewProcessor
from backend.models import BusinessCreate

airtable = AirtableService()
mock = MockGMB(airtable)
processor = ReviewProcessor()

# ── Demo Isletmeler ────────────────────────────────────────

demo_businesses = [
    BusinessCreate(
        name="Gebze Kebap Sarayi",
        category="Restoran",
        city="Gebze",
        district="Merkez",
        address="Cumhuriyet Mah. Ataturk Cad. No:45, Gebze/Kocaeli",
        keywords="Gebze kebap, en iyi kebap Gebze, Gebze restoran, aile restorani Gebze, ocakbasi",
        tone="Samimi",
        language="tr",
        custom_prompt="Aile restorani oldugumuzu vurgula. Aksam 22:00'ye kadar acik oldugumuzu belirt.",
    ),
    BusinessCreate(
        name="Kafe Mola",
        category="Kafe",
        city="Gebze",
        district="Darica",
        address="Sahil Yolu Bulvari No:12, Darica/Gebze",
        keywords="Gebze kafe, Darica kafe, kahvalti mekani Gebze, sahil kafe Gebze",
        tone="Esprili",
        language="tr",
        custom_prompt="Serpme kahvalti ve deniz manzarasi vurgusu yap. Haftasonu rezervasyon oner.",
    ),
    BusinessCreate(
        name="Berber Murat",
        category="Berber",
        city="Gebze",
        district="Beylikbagi",
        address="Beylikbagi Mah. Inonu Cad. No:8, Gebze/Kocaeli",
        keywords="Gebze berber, Beylikbagi berber, erkek kuaforu Gebze, sac kesimi Gebze",
        tone="Profesyonel",
        language="tr",
    ),
    BusinessCreate(
        name="Otel Sahil Palas",
        category="Otel",
        city="Gebze",
        district="Bayramoglu",
        address="Bayramoglu Sahil Yolu No:22, Gebze/Kocaeli",
        keywords="Gebze otel, Bayramoglu otel, denize yakin otel Gebze, konaklama Gebze",
        tone="Profesyonel",
        language="tr",
    ),
]

print("Isletmeler olusturuluyor...")
for b in demo_businesses:
    existing = airtable.list_businesses()
    if not any(e.name == b.name for e in existing):
        airtable.create_business(b)
        print(f"  ✅ {b.name}")
    else:
        print(f"  ⏭️  {b.name} (zaten var)")

# ── Demo Yorumlar ──────────────────────────────────────────

print("\nRastgele yorumlar olusturuluyor...")
mock.generate_batch(count=12)
print("  ✅ 12 yorum olusturuldu")

# ── Yorumlari Isle (batch halinde, free tier 5 RPM limitine uygun) ─

import time

print("\nYorumlar isleniyor (Groq/Llama yanit uretiyor)...")
print("  Free tier limiti: 5 istek/dakika. 4'erli batch'ler halinde isleniyor...")

all_results = []
batches = [4, 4, 4]  # 3 batch x 4 = 12 yorum

for batch_num, batch_size in enumerate(batches):
    if batch_num > 0:
        wait = 65
        print(f"  Rate limit reset bekleniyor ({wait}s)...")
        time.sleep(wait)

    results = processor.process_pending(max_count=batch_size)
    all_results.extend(results)
    print(f"  Batch {batch_num+1}: {len(results)} yorum yanitlandi")
    for review, log in results:
        print(f"    - {review.reviewer_name} ({review.rating}★) → SEO: {log.seo_score}% | {log.latency_ms}ms")

# Retry failed ones at the end
failed = [r for r in processor.airtable.list_reviews(status="Failed", limit=50) if r.review_id not in {rv.review_id for rv, _ in all_results}]
if failed:
    print(f"\n  {len(failed)} basarisiz yorum tekrar deneniyor...")
    retry_results = processor.retry_failed()
    print(f"  {len(retry_results)} tanesi kurtarildi")

print(f"\n  ✅ Toplam {len(all_results)} yorum yanitlandi")
print("\n🎉 Demo veriler hazir! Dashboard'u baslatin: streamlit run dashboard/app.py")
