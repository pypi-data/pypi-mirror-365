from msgspec._core import Struct

from sourcerer.settings import (
    DEFAULT_DOWNLOAD_CHUNK_SIZE_MB,
    DEFAULT_UPLOAD_CHUNK_SIZE_MB,
)


class Settings(Struct):
    theme: str = "github-dark"
    group_by_access_credentials: bool = False
    upload_chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE_MB
    download_chunk_size: int = DEFAULT_DOWNLOAD_CHUNK_SIZE_MB


class SettingsFields:
    theme = "theme"
    group_by_access_credentials = "group_by_access_credentials"
    upload_chunk_size = "upload_chunk_size"
    download_chunk_size = "download_chunk_size"
