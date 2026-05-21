from abc import ABC, abstractmethod


class BaseModule(ABC):
    """Tum otomasyon modullerinin uymasi gereken temel sinif."""

    MODULE_ID: str = "base"
    MODULE_NAME: str = "Base Module"
    VERSION: str = "1.0.0"
    POLL_INTERVAL: int = 90  # saniye

    @abstractmethod
    def is_active(self) -> bool:
        """Bu modul su anda aktif mi?"""
        ...

    @abstractmethod
    def start(self):
        """Modulu baslat (baglantilari ac, job'lari ekle)."""
        ...

    @abstractmethod
    def stop(self):
        """Modulu durdur (baglantilari kapat, job'lari kaldir)."""
        ...

    @abstractmethod
    def process(self):
        """Ana islem dongusu (scheduler tarafindan cagrilir)."""
        ...

    def health_check(self) -> dict:
        return {"module": self.MODULE_ID, "status": "ok"}
