import logging
from backend.modules.gmb_reviews import GMBModule

logger = logging.getLogger(__name__)


class ModuleManager:
    """Tum modulleri yoneten merkezi sinif."""

    def __init__(self):
        self.gmb_module: GMBModule | None = None
        self._load()

    def _load(self):
        """Airtable konfigurasyonuna gore aktif modulleri yukle."""
        self.gmb_module = GMBModule()
        if self.gmb_module.is_active():
            self.gmb_module.start()
            logger.info(f"ModuleManager: {self.gmb_module.MODULE_NAME} yuklendi")
        else:
            logger.info("ModuleManager: GMB modulu pasif, atlaniyor")

    @property
    def processor(self):
        """GMB review processor (endpoint'ler icin shortcut)."""
        if self.gmb_module and self.gmb_module.is_active():
            return self.gmb_module.processor
        return None

    @property
    def mock(self):
        """GMB mock yorum uretici (endpoint'ler icin shortcut)."""
        if self.gmb_module and self.gmb_module.is_active():
            return self.gmb_module.mock
        return None

    def needs_scheduler(self) -> bool:
        """Scheduler job'u eklenmeli mi?"""
        return self.gmb_module is not None and self.gmb_module.is_active()

    def tick(self):
        """Scheduler tarafindan cagrilan ana dongu."""
        if self.gmb_module and self.gmb_module.is_active():
            self.gmb_module.process()

    def shutdown(self):
        """Tum modulleri durdur."""
        if self.gmb_module:
            self.gmb_module.stop()
            logger.info("ModuleManager: Tum moduller durduruldu")
