from starlette.config import Config

config = Config("config.env")

HOST = config("HOST", default="192.168.0.106")
PORT = int(config("PORT", default=9069))
DEBUG = config("DEBUG", cast=bool, default=False)
SSL_CERT = config("SSL_CERT", default=None)
SSL_KEY = config("SSL_KEY", default=None)
CLEAN_SCORE = config("CLEAN_SCORE", default=False)