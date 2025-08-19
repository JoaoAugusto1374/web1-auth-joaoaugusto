import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-super-secreta")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
