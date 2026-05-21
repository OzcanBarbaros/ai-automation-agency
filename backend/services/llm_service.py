import re
import time
import logging
from groq import Groq
from backend.config import settings
from backend.models import Business, Review, Tone

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when LLM API fails after all retries."""


class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def _parse_retry_delay(self, error_str: str) -> int:
        """Extract retry seconds from rate limit headers/body. Falls back to 0."""
        match = re.search(r"'retryAfter':\s*'?(\d+)'?", error_str)
        if match:
            return int(match.group(1))
        match = re.search(r"retry in (\d+)", error_str)
        if match:
            return int(match.group(1))
        return 0

    def generate_response(self, business: Business, review: Review) -> tuple[str, int, int]:
        messages = self._build_messages(business, review)
        last_error = None

        for attempt in range(settings.LLM_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=512,
                )
                text = response.choices[0].message.content.strip() if response.choices else ""
                prompt_tokens = response.usage.prompt_tokens if response.usage else 0
                completion_tokens = response.usage.completion_tokens if response.usage else 0
                return text, prompt_tokens, completion_tokens

            except Exception as e:
                last_error = e
                error_str = str(e)
                error_lower = error_str.lower()
                is_rate_limit = any(kw in error_lower for kw in ("429", "rate", "quota", "exhausted"))
                is_server_error = any(kw in error_lower for kw in ("500", "502", "503", "504", "internal", "unavailable"))

                if attempt < settings.LLM_MAX_RETRIES - 1 and (is_rate_limit or is_server_error):
                    if is_rate_limit:
                        api_delay = self._parse_retry_delay(error_str)
                        delay = api_delay if api_delay > 0 else settings.LLM_RATE_LIMIT_DELAY * (2 ** attempt)
                    else:
                        delay = settings.LLM_RATE_LIMIT_DELAY * (2 ** attempt)

                    logger.warning(
                        f"Groq API retryable error (attempt {attempt+1}/{settings.LLM_MAX_RETRIES}), "
                        f"waiting {delay}s: {e}"
                    )
                    time.sleep(delay)
                else:
                    break

        raise LLMError(f"Groq API failed after {settings.LLM_MAX_RETRIES} retries: {last_error}")

    def _build_messages(self, business: Business, review: Review) -> list[dict]:
        tone_map = {
            Tone.SAMIMI: "samimi ve sıcak",
            Tone.PROFESYONEL: "profesyonel ve kurumsal",
            Tone.ESPRILI: "esprili ve neşeli",
        }
        tone_desc = tone_map.get(business.tone, "samimi ve sıcak")
        location = f"{business.city}, {business.district}" if business.district else business.city
        category = business.category.value if hasattr(business.category, 'value') else business.category

        system = (
            f"Sen \"{business.name}\" işletmesinin sahibisin. "
            f"İşletme konumu: {location}. Kategori: {category}. Adres: {business.address}. "
            f"Müşteri yorumlarına {business.language} dilinde, {tone_desc} bir tonla, "
            f"2-4 cümle arasında yanıt veriyorsun."
        )

        seo_rules = (
            "SEO-GEO KURALLARI (HER YANITTA UYGULAMALISIN):\n"
            f"1. Yanıtta MUTLAKA en az 1 kez \"{business.city}\" veya \"{business.district}\" geçsin\n"
            f"2. Şu anahtar kelimelerden en az 1-2 tanesini doğal bir şekilde kullan: {business.keywords or business.name}\n"
            f"3. Konum + hizmet bir arada doğal biçimde geçsin (örn: \"{business.district or business.city}'deki {category}\" gibi)\n"
            "4. Anahtar kelimeleri zorlama yapmadan, doğal akışta yerleştir\n"
            "5. Asla aynı anahtar kelimeyi 2'den fazla tekrar etme (keyword stuffing yapma)"
        )

        custom = business.custom_prompt.strip()
        if custom:
            seo_rules += f"\n\nEk talimat: {custom}"

        user = (
            f"{seo_rules}\n\n"
            f"Müşteri yorumu ({review.rating}/5 yıldız): {review.review_text}\n\n"
            f"Yanıt:"
        )

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
