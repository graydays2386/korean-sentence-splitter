from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env 파일 혹은 환경변수에서 자동으로 읽어옴
    ENV: str = 'server'
    URL: str
    API_KEY: str
    PROJECT_ID: str
    DEPLOYMENT_NEWWIKI_URL: str
    DEPLOYMENT_MERGEWIKI_URL: str







    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8"
    )


settings = Settings()