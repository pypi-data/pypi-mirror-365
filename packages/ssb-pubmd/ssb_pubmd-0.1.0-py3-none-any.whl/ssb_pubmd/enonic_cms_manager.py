from dataclasses import dataclass
from pathlib import Path

from ssb_pubmd.config import Config
from ssb_pubmd.ports import CmsClient
from ssb_pubmd.ports import ContentFileHandler
from ssb_pubmd.ports import SecretManagerClient


@dataclass
class EnonicCmsManager:
    """A CMS Mananager tailored to the Enonic CMS."""

    config: Config
    cms_client: CmsClient
    secret_manager_client: SecretManagerClient
    content_file_handler: ContentFileHandler

    def sync(self, content_file_path: str) -> str:
        """Requests that Enonic stores/updates the given contant file and gives back a rendered preview.

        The details of the communication are handled by the CmsClient implementation, which in turn depends on the services that are exposed by the Enonic XP application. The only thing this class cares is that it receives a CmsResponse object, which contains an id and preview url of the content.
        """
        content = self.content_file_handler.get_content(Path(content_file_path))
        response = self.cms_client.send(
            token=self.secret_manager_client.generate_token(),
            content=content,
        )
        self.content_file_handler.set_file_id(content.file_path, response.id)
        return response.preview_url
