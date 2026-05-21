from pyairtable import Api
from pyairtable.formulas import match, AND
from typing import Optional
from backend.config import settings
from backend.models import (
    Business, BusinessCreate, Review, ReviewCreate, ReviewStatus,
    ResponseLog, SummaryResponse, Sentiment
)
from datetime import datetime


class AirtableService:
    def __init__(self):
        self.api = Api(settings.AIRTABLE_API_KEY)
        self.base_id = settings.AIRTABLE_BASE_ID
        self.businesses = self.api.table(self.base_id, "Businesses")
        self.reviews = self.api.table(self.base_id, "Reviews")
        self.logs = self.api.table(self.base_id, "ResponseLogs")

    # ── Businesses ──────────────────────────────────────────

    def _business_to_record(self, b: Business) -> dict:
        return {
            "BusinessID": b.business_id,
            "Name": b.name,
            "Category": b.category.value,
            "City": b.city,
            "District": b.district,
            "Address": b.address,
            "Keywords": b.keywords,
            "Tone": b.tone.value,
            "Language": b.language,
            "CustomPrompt": b.custom_prompt,
            "Active": b.active,
            "GMB_Active": b.gmb_active,
            "CreatedAt": b.created_at,
        }

    def _record_to_business(self, record: dict) -> Business:
        fields = record.get("fields", record)
        return Business(
            business_id=fields.get("BusinessID", ""),
            name=fields.get("Name", ""),
            category=fields.get("Category", "Diger"),
            city=fields.get("City", ""),
            district=fields.get("District", ""),
            address=fields.get("Address", ""),
            keywords=fields.get("Keywords", ""),
            tone=fields.get("Tone", "Samimi"),
            language=fields.get("Language", "tr"),
            custom_prompt=fields.get("CustomPrompt", ""),
            active=fields.get("Active", True),
            gmb_active=fields.get("GMB_Active", True),
            created_at=fields.get("CreatedAt", ""),
        )

    def list_businesses(self, active_only: bool = False) -> list[Business]:
        records = self.businesses.all()
        result = [self._record_to_business(r) for r in records]
        if active_only:
            result = [b for b in result if b.active]
        return result

    def get_business(self, business_id: str) -> Optional[Business]:
        records = self.businesses.all(formula=match({"BusinessID": business_id}))
        if records:
            return self._record_to_business(records[0])
        return None

    def create_business(self, data: BusinessCreate) -> Business:
        b = Business(**data.model_dump())
        self.businesses.create(self._business_to_record(b))
        return b

    def update_business(self, business_id: str, data: dict) -> Optional[Business]:
        records = self.businesses.all(formula=match({"BusinessID": business_id}))
        if not records:
            return None
        record_id = records[0]["id"]
        update_fields = {}
        field_map = {
            "name": "Name", "category": "Category", "city": "City",
            "district": "District", "address": "Address", "keywords": "Keywords",
            "tone": "Tone", "language": "Language", "custom_prompt": "CustomPrompt",
            "active": "Active", "gmb_active": "GMB_Active",
        }
        for py_field, at_field in field_map.items():
            if py_field in data:
                val = data[py_field]
                if hasattr(val, "value"):
                    val = val.value
                update_fields[at_field] = val
        self.businesses.update(record_id, update_fields)
        return self.get_business(business_id)

    # ── Reviews ─────────────────────────────────────────────

    def _review_to_record(self, r: Review) -> dict:
        return {
            "ReviewID": r.review_id,
            "BusinessID": r.business_id,
            "ReviewerName": r.reviewer_name,
            "Rating": r.rating,
            "ReviewText": r.review_text,
            "ResponseText": r.response_text,
            "Sentiment": r.sentiment.value if isinstance(r.sentiment, Sentiment) else r.sentiment,
            "Status": r.status.value if isinstance(r.status, ReviewStatus) else r.status,
            "Source": r.source.value if hasattr(r, 'source') else "Manual",
            "CreatedAt": r.created_at,
            "RespondedAt": r.responded_at or "",
        }

    def _record_to_review(self, record: dict) -> Review:
        fields = record.get("fields", record)
        bid = fields.get("BusinessID", "")
        return Review(
            review_id=fields.get("ReviewID", ""),
            business_id=bid,
            reviewer_name=fields.get("ReviewerName", ""),
            rating=int(fields.get("Rating", 3)),
            review_text=fields.get("ReviewText", ""),
            response_text=fields.get("ResponseText", ""),
            sentiment=fields.get("Sentiment", "Notr"),
            status=fields.get("Status", "Pending"),
            source=fields.get("Source", "Manual"),
            created_at=fields.get("CreatedAt", ""),
            responded_at=fields.get("RespondedAt", None),
        )

    def list_reviews(self, business_id: Optional[str] = None,
                     status: Optional[str] = None,
                     limit: int = 50) -> list[Review]:
        conditions = []
        if business_id:
            conditions.append(match({"BusinessID": business_id}))
        if status:
            conditions.append(match({"Status": status}))
        if conditions:
            formula = AND(*conditions) if len(conditions) > 1 else conditions[0]
            records = self.reviews.all(formula=formula, max_records=limit)
        else:
            records = self.reviews.all(max_records=limit)
        return [self._record_to_review(r) for r in records]

    def get_pending_reviews(self) -> list[Review]:
        return self.list_reviews(status="Pending", limit=100)

    def create_review(self, data: ReviewCreate) -> Review:
        r = Review(**data.model_dump(exclude_none=True))
        record = self._review_to_record(r)
        # Remove RespondedAt for creation to avoid empty string issues
        record.pop("RespondedAt", None)
        self.reviews.create(record)
        return r

    def update_review_response(self, review_id: str, response_text: str,
                               status: str = "Responded") -> Optional[Review]:
        records = self.reviews.all(formula=match({"ReviewID": review_id}))
        if not records:
            return None
        record_id = records[0]["id"]
        self.reviews.update(record_id, {
            "ResponseText": response_text,
            "Status": status,
            "RespondedAt": datetime.now().isoformat(),
        })
        return self._record_to_review(self.reviews.get(record_id))

    # ── ResponseLogs ────────────────────────────────────────

    def create_log(self, log: ResponseLog) -> ResponseLog:
        record = {
            "LogID": log.log_id,
            "ReviewID": log.review_id,
            "BusinessID": log.business_id,
            "PromptTokens": log.prompt_tokens,
            "CompletionTokens": log.completion_tokens,
            "LatencyMs": log.latency_ms,
            "SEOScore": log.seo_score,
            "KeywordsUsed": log.keywords_used,
            "LocationMentioned": log.location_mentioned,
            "CreatedAt": log.created_at,
        }
        self.logs.create(record)
        return log

    # ── Dashboard Aggregates ────────────────────────────────

    def get_summary(self, business_id: Optional[str] = None) -> SummaryResponse:
        reviews = self.list_reviews(business_id=business_id, limit=500) if business_id else []
        if not reviews and not business_id:
            # Fetch all reviews for global summary
            all_records = self.reviews.all(max_records=500)
            reviews = [self._record_to_review(r) for r in all_records]

        total = len(reviews)
        responded = sum(1 for r in reviews if r.status == ReviewStatus.RESPONDED)
        ratings = [r.rating for r in reviews if r.rating > 0]

        today = datetime.now().strftime("%Y-%m-%d")
        today_reviews = sum(1 for r in reviews if r.created_at.startswith(today))
        today_responded = sum(
            1 for r in reviews
            if r.responded_at and r.responded_at.startswith(today)
        )

        # SEO average from logs
        seo_scores = []
        all_logs = self.logs.all(max_records=500)
        for log_record in all_logs:
            f = log_record.get("fields", log_record)
            score = f.get("SEOScore", 0)
            if score:
                try:
                    seo_scores.append(int(score))
                except (ValueError, TypeError):
                    pass

        return SummaryResponse(
            total_reviews=total,
            responded=responded,
            response_rate=round(responded / total * 100, 1) if total > 0 else 0,
            avg_rating=round(sum(ratings) / len(ratings), 1) if ratings else 0,
            avg_seo_score=round(sum(seo_scores) / len(seo_scores), 1) if seo_scores else 0,
            today_reviews=today_reviews,
            today_responded=today_responded,
        )

    def get_reviews_for_chart(self, business_id: Optional[str] = None, days: int = 7) -> list[dict]:
        """Returns raw review records for dashboard charts."""
        records = self.reviews.all(max_records=500)
        result = []
        for rec in records:
            f = rec.get("fields", rec)
            bid = f.get("BusinessID", "")
            if isinstance(bid, list):
                bid = bid[0] if bid else ""
            if business_id and bid != business_id:
                continue
            result.append({
                "created_at": f.get("CreatedAt", ""),
                "status": f.get("Status", "Pending"),
                "rating": int(f.get("Rating", 0)),
                "sentiment": f.get("Sentiment", "Notr"),
                "business_id": bid,
            })
        return result

    def get_logs_for_seo_chart(self, business_id: Optional[str] = None) -> list[dict]:
        """Returns log records for SEO performance charts."""
        records = self.logs.all(max_records=500)
        result = []
        for rec in records:
            f = rec.get("fields", rec)
            bid = f.get("BusinessID", "")
            if isinstance(bid, list):
                bid = bid[0] if bid else ""
            if business_id and bid != business_id:
                continue
            result.append({
                "created_at": f.get("CreatedAt", ""),
                "seo_score": int(f.get("SEOScore", 0)),
                "keywords_used": f.get("KeywordsUsed", ""),
                "location_mentioned": f.get("LocationMentioned", False),
                "business_id": bid,
            })
        return result
