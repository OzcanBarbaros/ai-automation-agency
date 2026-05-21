from backend.models import Sentiment


class SentimentService:
    """Hybrid sentiment detection: rating-weighted + Turkish keyword matching."""

    POSITIVE_WORDS = {
        "harika", "mukemmel", "guzel", "iyi", "sagol", "tesekkur", "begendim",
        "tavsiye", "onerecegim", "kaliteli", "temiz", "guler", "hizli",
        "lezzetli", "taze", "enfes", "sik", "rahat", "profesyonel",
        "ilgili", "yardimsever", "basari", "basarili", "memnun", "kesinlikle",
    }
    NEGATIVE_WORDS = {
        "kotu", "kötü", "berbat", "pisman", "hayal", "kirikligi", "vasat",
        "yetersiz", "pis", "ilgisiz", "kaba", "yavas", "pahali", "bayat",
        "kotuydu", "kötüydü", "kalmadim", "sevmedim", "rezalet", "beceriksiz",
    }

    def detect(self, review_text: str, rating: int) -> Sentiment:
        # Rating gives a strong signal
        if rating >= 4:
            return Sentiment.POSITIVE
        if rating <= 2:
            return Sentiment.NEGATIVE

        # Rating == 3: let keywords decide
        text_lower = review_text.lower()
        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in text_lower)
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in text_lower)

        if pos_count > neg_count:
            return Sentiment.POSITIVE
        elif neg_count > pos_count:
            return Sentiment.NEGATIVE
        return Sentiment.NEUTRAL

    def analyze(self, review_text: str, rating: int) -> str:
        return self.detect(review_text, rating).value
