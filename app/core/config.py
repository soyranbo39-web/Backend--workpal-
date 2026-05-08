
import os
class settings:
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY","change-me-in-pod")
    JWT_ALGORITHM: str = "HS256"     
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))

    