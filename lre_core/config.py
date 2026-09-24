import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings:
    PROJECT_NAME: str = "Logistics Requirements Engine (LRE)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"
    
    # Пороги активации
    REQUIREMENT_ACTIVATION_THRESHOLD: float = 0.50
    CONCEPT_ACTIVATION_THRESHOLD: float = 0.35
    HARD_RULE_BIAS: float = 10.0
    
    # Хранилище
    DB_PATH: Path = DATA_DIR / "lre_traces.sqlite"
    MAX_TRACES_HISTORY: int = 500

settings = Settings()
