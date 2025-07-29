"""
Storage provider entity classes.

This module defines data classes representing cloud storage entities
such as storage containers, files, folders, and permissions.
"""

from datetime import datetime

from msgspec._core import Struct


class Storage(Struct):
    """
    Represents a cloud storage container (bucket/container).

    Attributes:
        provider (str): The cloud provider identifier (e.g., 's3', 'gcp')
        storage (str): The storage name/identifier (e.g., bucket name)
        date_created (datetime): When the storage was created
    """

    provider: str
    storage: str
    date_created: datetime


class StoragePermissions(Struct):
    """
    Represents permissions for a user on a storage resource.

    Attributes:
        user (str): The user identifier or name
        permissions (List[str]): List of permission strings granted to the user
    """

    user: str
    permissions: list[str]


class Folder(Struct):
    """
    Represents a folder/directory within a storage container.

    Attributes:
        key (str): The path/key identifier for the folder
    """

    key: str
    parent_path: str


class File(Struct):
    """
    Represents a file within a storage container.

    Attributes:
        uuid (str): Unique identifier for the file
        key (str): The path/key identifier for the file
        size (str): Human-readable file size
        is_text (bool): Whether the file is textual
        date_modified (datetime | None): When the file was last modified, if available
    """

    uuid: str
    key: str
    size: int
    is_text: bool
    date_modified: datetime
    parent_path: str


class StorageContent(Struct):
    """
    Represents the contents of a storage location, including files and folders.

    Attributes:
        files (List[File]): List of files in the location
        folders (List[Folder]): List of folders in the location
    """

    files: list[File]
    folders: list[Folder]
