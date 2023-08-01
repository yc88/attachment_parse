from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "attachment parse"
    tesseract_cmd_path: str = ''
    tesseract_languages: str = ''

    class Config:
        env_file = '.env'
