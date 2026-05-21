from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


class Sentiment(str, Enum):
    POSITIVE = "Pozitif"
    NEGATIVE = "Negatif"
    NEUTRAL = "Notr"


class ReviewStatus(str, Enum):
    PENDING = "Pending"
    RESPONDED = "Responded"
    FAILED = "Failed"


class ReviewSource(str, Enum):
    AUTO = "Auto"
    MANUAL = "Manual"


class Tone(str, Enum):
    SAMIMI = "Samimi"
    PROFESYONEL = "Profesyonel"
    ESPRILI = "Esprili"


class BusinessCategory(str, Enum):
    RESTORAN = "Restoran"
    KAFE = "Kafe"
    OTEL = "Otel"
    BERBER = "Berber"
    MARKET = "Market"
    ECZANE = "Eczane"
    DIS_HEKIMI = "Dis Hekimi"
    AVUKAT = "Avukat"
    DUNKKAN = "Dukkan"
    DIGER = "Diger"


# --- Business ---
class BusinessBase(BaseModel):
    name: str
    category: BusinessCategory = BusinessCategory.DIGER
    city: str = ""
    district: str = ""
    address: str = ""
    keywords: str = ""
    tone: Tone = Tone.SAMIMI
    language: str = "tr"
    custom_prompt: str = ""
    active: bool = True
    gmb_active: bool = True


class BusinessCreate(BusinessBase):
    pass


class Business(BusinessBase):
    business_id: str = Field(default_factory=gen_id)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    class Config:
        from_attributes = True


# --- Review ---
class ReviewBase(BaseModel):
    business_id: str
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    review_text: str
    source: ReviewSource = ReviewSource.MANUAL


class ReviewCreate(ReviewBase):
    sentiment: Optional[Sentiment] = None


class Review(ReviewBase):
    review_id: str = Field(default_factory=gen_id)
    response_text: str = ""
    sentiment: Sentiment = Sentiment.NEUTRAL
    status: ReviewStatus = ReviewStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    responded_at: Optional[str] = None

    class Config:
        from_attributes = True


# --- ResponseLog ---
class ResponseLog(BaseModel):
    log_id: str = Field(default_factory=gen_id)
    review_id: str
    business_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    seo_score: int = 0
    keywords_used: str = ""
    location_mentioned: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    class Config:
        from_attributes = True


# --- Summary ---
class SummaryResponse(BaseModel):
    total_reviews: int = 0
    responded: int = 0
    response_rate: float = 0.0
    avg_rating: float = 0.0
    avg_seo_score: float = 0.0
    today_reviews: int = 0
    today_responded: int = 0
