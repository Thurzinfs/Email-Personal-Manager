from dotenv import load_dotenv
import os


load_dotenv()

class EnvironmentConfig:
    def __init__(self) -> None:
        self.GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
        self.GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
        self.GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', '')
        self.ENVIRONMENT = os.getenv('ENVIRONMENT', '')
        self.SECRET_KEY = os.getenv('SECRET_KEY', '')
        self.ALGORITHM = os.getenv('ALGORITHM', '')
        self.ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '')
        self.REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '')

settings = EnvironmentConfig()
