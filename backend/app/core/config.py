from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/app.db"
    openai_api_key: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_db_path: str = "./data/chroma"

    class Config:
        env_file = ".env"

settings = Settings()
