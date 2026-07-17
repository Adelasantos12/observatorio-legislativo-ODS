from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )

    # Extraction
    module_extractor: str = "spain"
    id_legislatura: int = 0
    current_legislature: bool = True
    limit_date_to_sync: str = "2000-01-01"  # str: consumer parses with strptime()
    amendments_feature: bool = False

    # México — Gaceta Parlamentaria
    gaceta_legislatura: str = "66"
    gaceta_date: str = ""  # YYYYMMDD; vacío = día de hoy

    # NormTrace — codificación estructural en el etiquetado batch (opcional).
    # Desactivada por defecto: el etiquetado no requiere LLM salvo que se active.
    normtrace_deep: bool = False

    # Alerts
    use_alerts: bool = False

    # Stats legislature window (empty-string sentinel is load-bearing)
    legislature_start_date: str = ""
    legislature_end_date: str = ""

    # Logging (field name matches env LOGLEVEL exactly)
    loglevel: str = "INFO"

    # Redis — declared for .env parity; not consumed by the engine today
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db_check: int = 0
    redis_db_denylist: int = 1


@lru_cache
def get_settings() -> Settings:
    return Settings()
