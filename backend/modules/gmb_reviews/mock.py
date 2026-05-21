import random
from datetime import datetime
from backend.models import Review, ReviewCreate, ReviewSource, Business, BusinessCategory
from backend.services.airtable_service import AirtableService


TURKISH_NAMES = [
    "Ahmet Y.", "Ayse K.", "Mehmet D.", "Fatma S.", "Mustafa C.",
    "Emine T.", "Ali R.", "Zeynep A.", "Hasan P.", "Merve B.",
    "Ibrahim O.", "Elif N.", "Osman G.", "Hacer L.", "Kemal E.",
    "Derya C.", "Canan M.", "Burak S.", "Selin T.", "Cem Y.",
]

POSITIVE_TEMPLATES = [
    "Harika bir deneyimdi! Kesinlikle tavsiye ederim.",
    "Cok memnun kaldim, personel cok ilgiliydi.",
    "Uzun zamandir boyle kaliteli hizmet almamistim.",
    "Her sey cok guzeldi, tekrar gelecegim.",
    "Fiyat performans olarak cok iyi, gonul rahatligiyla tercih edin.",
    "Mekan cok temiz ve duzenli, calisanlar guler yuzlu.",
    "Begendim, arkadaslarima da onerecegim.",
    "Hizli ve kaliteli hizmet, tesekkurler!",
    "Tam da bekledigim gibi, mukemmel!",
    "Ilk defa geldim ve cok begendim, surekli musterisi olacagim.",
    "Personelin guleryuzu ve ilgisi icin tesekkur ederim.",
    "Urunler cok taze ve lezzetliydi.",
    "Kesinlikle sehrin en iyisi!",
    "Cok memnun kaldim, herkese tavsiye ederim.",
]

NEGATIVE_TEMPLATES = [
    "Hayal kirikligina ugradim, bekledigim gibi cikmadi.",
    "Ilgi alakadan memnun kalmadim, gelistirilmeli.",
    "Fiyatlar yuksek ama hizmet vasat.",
    "Pek begendigimi soyleyemeyecegim, daha iyi olabilirdi.",
    "Uzun sure beklemek zorunda kaldim, yetersiz personel var.",
    "Temizlik konusunda daha dikkatli olunmali.",
    "Ikinci kez gelmistim ama ayni kaliteyi bulamadim.",
    "Personelin tavri hos degildi, daha profesyonel olmali.",
    "Urun kalitesi dustu, eskisi gibi degil.",
    "Gittigime pisman oldum, bir daha tercih etmem.",
]

NEUTRAL_TEMPLATES = [
    "Idare eder, cok iyi de degil cok kotu de.",
    "Ortalama bir deneyimdi, beklentimi karsiladi.",
    "Guzel ama gelistirilebilecek yonleri var.",
    "Fena degil, bir daha gelebilirim.",
    "Hizliydi ama daha ozlu olabilirdi.",
    "Standart bir hizmet, fazlasi yok eksigi yok.",
]


class MockGMB:
    def __init__(self, airtable: AirtableService):
        self.airtable = airtable

    def generate_random_review(self, business: Business | None = None) -> Review | None:
        if not business:
            businesses = self.airtable.list_businesses(active_only=True)
            if not businesses:
                return None
            business = random.choice(businesses)

        rating = random.choices([5, 4, 3, 2, 1], weights=[35, 25, 20, 12, 8], k=1)[0]

        if rating >= 4:
            templates = POSITIVE_TEMPLATES
        elif rating == 3:
            templates = NEUTRAL_TEMPLATES
        else:
            templates = NEGATIVE_TEMPLATES

        review_text = random.choice(templates)

        category_prefixes = {
            BusinessCategory.RESTORAN: ["yemek", "lezzet", "porsiyon"],
            BusinessCategory.KAFE: ["kahve", "tatli", "atmosfer"],
            BusinessCategory.BERBER: ["tras", "sac kesimi", "model"],
            BusinessCategory.OTEL: ["oda", "kahvalti", "konfor"],
            BusinessCategory.ECZANE: ["ilac", "eczaci", "recete"],
            BusinessCategory.MARKET: ["alisveris", "urun", "fiyat"],
            BusinessCategory.DIS_HEKIMI: ["tedavi", "dis", "randevu"],
            BusinessCategory.AVUKAT: ["davave", "danisma", "hukuk"],
        }

        if hasattr(business.category, 'value'):
            prefixes = category_prefixes.get(business.category, ["hizmet", "deneyim"])
        else:
            prefixes = ["hizmet", "deneyim"]

        prefix = random.choice(prefixes)
        review_text = f"{prefix.capitalize()} ile ilgili olarak: {review_text}"

        review = ReviewCreate(
            business_id=business.business_id,
            reviewer_name=random.choice(TURKISH_NAMES),
            rating=rating,
            review_text=review_text,
            source=ReviewSource.AUTO,
        )
        return self.airtable.create_review(review)

    def generate_batch(self, count: int = 3):
        businesses = self.airtable.list_businesses(active_only=True)
        if not businesses:
            return []
        results = []
        for _ in range(count):
            business = random.choice(businesses)
            review = self.generate_random_review(business)
            if review:
                results.append(review)
        return results
