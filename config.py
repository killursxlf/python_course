from dotenv import load_dotenv
import os

load_dotenv() 

class Settings:
    PAGES_TO_FETCH: int = int(os.getenv('PAGES_TO_FETCH', 1))
    BASE_URL: str = os.getenv('BASE_URL', '')
    GENRE_URL: str = os.getenv('GENRE_URL', '')
    TOKEN: str = os.getenv('TOKEN')

    @classmethod
    def validate(cls):
        if not cls.TOKEN:
            raise ValueError(" TOKEN not defined in .env")
        if not cls.BASE_URL or not cls.GENRE_URL:
            raise ValueError("BASE_URL or GENRE_URL not defined in .env")
Settings.validate()