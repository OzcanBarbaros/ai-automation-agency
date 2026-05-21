import time
import logging
from typing import Optional
from backend.config import settings
from backend.models import Review, ReviewStatus, ResponseLog
from backend.services.airtable_service import AirtableService
from backend.services.llm_service import LLMService, LLMError
from backend.services.seo_service import SEOService
from backend.services.sentiment_service import SentimentService

logger = logging.getLogger(__name__)


class ReviewProcessor:
    def __init__(self):
        self.airtable = AirtableService()
        self.llm = LLMService()
        self.seo = SEOService()
        self.sentiment = SentimentService()

    def _get_airtable_record_id(self, review_id: str) -> str:
        from pyairtable.formulas import match
        records = self.airtable.reviews.all(formula=match({"ReviewID": review_id}))
        if records:
            return records[0]["id"]
        raise ValueError(f"Review not found: {review_id}")

    def process_pending(self, max_count: Optional[int] = None) -> list[tuple[Review, ResponseLog]]:
        pending = self.airtable.get_pending_reviews()
        results = []
        for i, review in enumerate(pending):
            if max_count and i >= max_count:
                break
            if i > 0:
                time.sleep(settings.LLM_RATE_LIMIT_DELAY)
            result = self.process_one(review)
            if result:
                results.append(result)
        return results

    def retry_failed(self) -> list[tuple[Review, ResponseLog]]:
        failed = self.airtable.list_reviews(status="Failed", limit=100)
        results = []
        for i, review in enumerate(failed):
            if i > 0:
                time.sleep(settings.LLM_RATE_LIMIT_DELAY)
            result = self.process_one(review)
            if result:
                results.append(result)
        return results

    def process_one(self, review: Review) -> Optional[tuple[Review, ResponseLog]]:
        business = self.airtable.get_business(review.business_id)
        if not business:
            logger.warning(f"Business not found: {review.business_id}")
            return None

        detected_sentiment = self.sentiment.detect(review.review_text, review.rating)
        self.airtable.reviews.update(
            self._get_airtable_record_id(review.review_id),
            {"Sentiment": detected_sentiment.value},
        )
        review.sentiment = detected_sentiment

        start = time.time()
        try:
            response_text, prompt_tokens, completion_tokens = self.llm.generate_response(
                business, review
            )
        except LLMError as e:
            logger.error(f"LLM API failed after retries for review {review.review_id}: {e}")
            self.airtable.update_review_response(review.review_id, str(e), status="Failed")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for review {review.review_id}: {e}")
            self.airtable.update_review_response(review.review_id, str(e), status="Failed")
            return None

        latency_ms = int((time.time() - start) * 1000)

        seo_result = self.seo.analyze(response_text, business)

        self.airtable.update_review_response(review.review_id, response_text)

        log = ResponseLog(
            review_id=review.review_id,
            business_id=review.business_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            seo_score=seo_result["seo_score"],
            keywords_used=seo_result["keywords_used"],
            location_mentioned=seo_result["location_mentioned"],
        )
        self.airtable.create_log(log)

        review.response_text = response_text
        review.status = ReviewStatus.RESPONDED
        return review, log
