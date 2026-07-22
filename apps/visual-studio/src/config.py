from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    comfyui_url: str = "http://192.168.15.9:8188"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VISUALSTUDIO_",
    )


settings = Settings()
