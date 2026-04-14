import cloudinary

from backend.config.settings import settings


_definitely_initialized = False


def init_cloudinary() -> None:
    global _definitely_initialized

    if _definitely_initialized:
        return

    cloudinary.config(
        cloud_name=settings.cloud_name,
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        secure=True,
    )
    _definitely_initialized = True
