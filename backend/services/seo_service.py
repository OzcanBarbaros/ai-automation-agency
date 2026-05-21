from backend.models import Business


class SEOService:
    def analyze(self, response_text: str, business: Business) -> dict:
        text_lower = response_text.lower()
        city = business.city.lower() if business.city else ""
        district = business.district.lower() if business.district else ""
        category = business.category.value if hasattr(business.category, 'value') else str(business.category)
        category_lower = category.lower()

        keywords_raw = business.keywords or business.name
        keywords = [k.strip().lower() for k in keywords_raw.replace(",", "\n").split("\n") if k.strip()]

        # 1. Location check (40 pts)
        location_mentioned = False
        if city and city in text_lower:
            location_mentioned = True
        if district and district in text_lower:
            location_mentioned = True

        # 2. Keyword usage (30 pts)
        used_keywords = [kw for kw in keywords if kw.lower() in text_lower]
        keyword_used = len(used_keywords) > 0

        # 3. Location + service combination (20 pts)
        combo_found = False
        location_terms = [t.lower() for t in [city, district] if t]
        category_words = category_lower.split()
        for loc in location_terms:
            for cw in category_words:
                # Check proximity: within 8 words
                words = text_lower.split()
                try:
                    loc_idx = next(i for i, w in enumerate(words) if loc in w)
                except StopIteration:
                    continue
                try:
                    cat_idx = next(i for i, w in enumerate(words) if cw in w)
                except StopIteration:
                    continue
                if abs(loc_idx - cat_idx) <= 8:
                    combo_found = True
                    break
            if combo_found:
                break

        # 4. Keyword stuffing detection
        stuffing_detected = False
        for kw in keywords:
            count = text_lower.count(kw.lower())
            if count > 2:
                stuffing_detected = True
                break

        # Calculate score
        score = 0
        if location_mentioned:
            score += 40
        if keyword_used:
            score += 30
        if combo_found:
            score += 20
        if not stuffing_detected:
            score += 10
        if stuffing_detected:
            score -= 20

        score = max(0, min(100, score))

        return {
            "seo_score": score,
            "keywords_used": ", ".join(used_keywords),
            "location_mentioned": location_mentioned,
        }
