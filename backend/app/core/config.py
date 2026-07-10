from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/app.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_db_path: str = "./data/chroma"

    class Config:
        env_file = ".env"

settings = Settings()
