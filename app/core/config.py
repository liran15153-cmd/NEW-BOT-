from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    service_name: str = "financial-wellness-assistant"


settings = Settings()
