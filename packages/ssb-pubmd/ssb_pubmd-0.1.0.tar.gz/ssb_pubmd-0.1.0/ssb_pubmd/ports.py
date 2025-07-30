from pathlib import Path
from typing import Protocol

from ssb_pubmd.models import CmsResponse
from ssb_pubmd.models import Content


class CmsManager(Protocol):
    """An interface (primary port) for managing a CMS.

    An implementing class is tailored to a specific CMS application.
    """

    def sync(self, content_file_path: str) -> str:
        """Requests that the CMS stores and renders the given content file.

        :param content_file_path: The path to the content file to be rendered.
        :return: A URL to the rendered preview.
        """
        ...


class CmsClient(Protocol):
    """An interface (secondary port) for communicating with a CMS.

    An implementing class is tailored to a specific CMS, with its specific exposed services and token authentication flow.
    """

    def send(self, token: str, content: Content) -> CmsResponse: ...


class ContentFileHandler(Protocol):
    """An interface (secondary port) for handling content files, including extraction and handling of metadata."""

    def get_file_id(self, file_path: Path) -> str:
        """
        Returns the id of a given file path.
        If no id is registered for the given file path,
        it returns an empty string.
        """
        ...

    def set_file_id(self, file_path: Path, content_id: str) -> None:
        """Sets the id of a given file path."""
        ...

    def get_content(self, file_path: Path) -> Content:
        """
        Extracts the content of a given file.
        """
        ...


class SecretManagerClient(Protocol):
    """An interface (secondary port) for communicating with a secret manager and generating tokens."""

    def generate_token(self) -> str: ...
