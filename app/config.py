# from pydantic import BaseSettings
import os
from dotenv import load_dotenv
import json
import base64

load_dotenv()

class Settings:
    MONGODB_URI : str = os.getenv("MONGODB_URI")
    SECRET_KEY  = "44bdbd10be0c56ddd3df3431ae29214f1b04ad9c2c56db021c12f460004bdacc"
    ALGORITHM = "HS256"
    SWAGGER_USERNAME = "admin"
    SWAGGER_PASSWORD = "pass"
    GOOGLE_CLIENT_ID:str = os.getenv("GOOGLE_CLIENT_ID")
    ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_HOURS', 1))


settings = Settings()

title = "Social media app with FastAPI"
description = """
\nThis project provides a complete REST API using Python 3\n
"""
tags_metadata = [
    {
        "name": "Root",
        "description": "Root description",
    },
    {
        "name": "Posts",
        "description": "Posts description",
    },
    {
        "name": "Users",
        "description": "Users description",
    },
    {
        "name": "Authentication",
        "description": "Authentication description",
    },
    {
        "name": "Vote",
        "description": "Vote description",
    }
]
