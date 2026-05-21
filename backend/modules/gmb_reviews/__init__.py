import logging
from backend.modules.base import BaseModule
from backend.modules.gmb_reviews.processor import ReviewProcessor
from backend.modules.gmb_reviews.mock import MockGMB
from backend.services.airtable_service import AirtableService

logger = logging.getLogger(__name__)


class GMBModule(BaseModule):
    MODULE_ID = "gmb_reviews"
    MODULE_NAME = "GMB Yorum Yanitlama"
    VERSION = "1.0.0"
    POLL_INTERVAL = 90

    def __init__(self):
        self.airtable = AirtableService()
        self.processor = ReviewProcessor()
        self.mock = MockGMB(self.airtable)
        self._active = self._check_active()

    def _check_active(self) -> bool:
        businesses = self.airtable.list_businesses(active_only=True)
        return any(getattr(b, "gmb_active", True) for b in businesses)

    def is_active(self) -> bool:
        return self._active

    def start(self):
        logger.info(f"[{self.MODULE_ID}] Modul baslatildi (v{self.VERSION})")

    def stop(self):
        logger.info(f"[{self.MODULE_ID}] Modul durduruldu")

    def process(self):
        """Scheduler tick: mock yorum uret ve bekleyenleri isle."""
        try:
            self.mock.generate_batch(count=2)
            self.processor.process_pending()
        except Exception as e:
            logger.error(f"[{self.MODULE_ID}] Process error: {e}")
