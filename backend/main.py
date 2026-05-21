import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from apscheduler.schedulers.background import BackgroundScheduler
from backend.config import settings
from backend.models import BusinessCreate, ReviewCreate, SummaryResponse, Business, Review
from backend.services.airtable_service import AirtableService
from backend.module_manager import ModuleManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gmb")

airtable = AirtableService()
manager = ModuleManager()
scheduler = BackgroundScheduler()


def tick():
    """Scheduled job: tum aktif modulleri calistir."""
    try:
        manager.tick()
    except Exception as e:
        logger.error(f"Scheduler tick error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if manager.needs_scheduler():
        scheduler.add_job(
            tick, "interval", seconds=settings.MOCK_INTERVAL_SECONDS,
            id="tick", max_instances=1, coalesce=True,
        )
        scheduler.start()
        logger.info(f"Scheduler started (interval={settings.MOCK_INTERVAL_SECONDS}s)")
    yield
    scheduler.shutdown(wait=False)
    manager.shutdown()


app = FastAPI(title="AI Otomasyon Ajansi", version="2.0.0", lifespan=lifespan)


# ── Businesses ──────────────────────────────────────────────

@app.get("/api/businesses", response_model=list[Business])
def list_businesses(active_only: bool = Query(default=False)):
    return airtable.list_businesses(active_only=active_only)


@app.post("/api/businesses", response_model=Business)
def create_business(data: BusinessCreate):
    return airtable.create_business(data)


@app.put("/api/businesses/{business_id}", response_model=Business | dict)
def update_business(business_id: str, data: dict):
    result = airtable.update_business(business_id, data)
    if not result:
        return {"error": "Business not found"}
    return result


# ── Reviews ─────────────────────────────────────────────────

@app.get("/api/reviews", response_model=list[Review])
def list_reviews(
    business_id: str = Query(default=None),
    status: str = Query(default=None),
    limit: int = Query(default=50),
):
    return airtable.list_reviews(business_id=business_id, status=status, limit=limit)


@app.post("/api/reviews/manual", response_model=Review)
def create_manual_review(data: ReviewCreate):
    review = airtable.create_review(data)
    if manager.processor:
        manager.processor.process_one(review)
    reviews = airtable.list_reviews(business_id=review.business_id, limit=1)
    return reviews[0] if reviews else review


# ── Processing ──────────────────────────────────────────────

@app.post("/api/process")
def trigger_processing(max_count: int = Query(default=None)):
    if not manager.processor:
        return {"error": "GMB modulu aktif degil"}
    results = manager.processor.process_pending(max_count=max_count)
    return {"processed": len(results)}


@app.post("/api/retry-failed")
def retry_failed_reviews():
    if not manager.processor:
        return {"error": "GMB modulu aktif degil"}
    results = manager.processor.retry_failed()
    return {"retried": len(results)}


# ── Summary ─────────────────────────────────────────────────

@app.get("/api/summary", response_model=SummaryResponse)
def get_summary(business_id: str = Query(default=None)):
    return airtable.get_summary(business_id=business_id)


@app.get("/api/charts/reviews")
def get_review_chart_data(business_id: str = Query(default=None)):
    return airtable.get_reviews_for_chart(business_id=business_id)


@app.get("/api/charts/seo")
def get_seo_chart_data(business_id: str = Query(default=None)):
    return airtable.get_logs_for_seo_chart(business_id=business_id)


# ── Mock trigger ────────────────────────────────────────────

@app.post("/api/mock/generate")
def generate_mock_reviews(count: int = Query(default=3)):
    if not manager.mock:
        return {"error": "GMB modulu aktif degil"}
    reviews = manager.mock.generate_batch(count=count)
    return {"generated": len(reviews)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
