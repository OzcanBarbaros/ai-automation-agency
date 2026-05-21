from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    AIRTABLE_API_KEY: str = os.getenv("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
    MOCK_INTERVAL_SECONDS: int = int(os.getenv("MOCK_INTERVAL_SECONDS", "90"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    LLM_RATE_LIMIT_DELAY: float = float(os.getenv("LLM_RATE_LIMIT_DELAY", "1.0"))


settings = Settings()
