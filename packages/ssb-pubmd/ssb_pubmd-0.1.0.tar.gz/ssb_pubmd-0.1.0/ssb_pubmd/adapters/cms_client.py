from urllib.parse import urlparse

import requests

from ssb_pubmd.models import CmsResponse
from ssb_pubmd.models import Content


class CmsClientError(Exception): ...


class MimirCmsClient:
    base_url: str

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _convert_preview_url(self, url_from_response: str) -> str:
        """Convert the preview URL to a full URL if it's relative."""
        url = urlparse(url_from_response)
        if url.scheme and url.netloc:
            return url.geturl()
        else:
            return urlparse(self.base_url)._replace(path=url.path).geturl()

    def send(self, token: str, content: Content) -> CmsResponse:
        """Sends a request to the Enonic CMS, assumed to have the mimir application installed (currently this only works with the feature branch https://github.com/statisticsnorway/mimir/pull/3192)."""
        try:
            response = requests.post(
                f"{self.base_url}/_/service/mimir/postMarkdown",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=content.to_json(),
            )
            if response.status_code != 200:
                raise CmsClientError(
                    f"Request to CMS failed with status code {response.status_code}."
                )
            body = response.json()
            return CmsResponse(
                id=body["_id"],
                preview_url=self._convert_preview_url(body["previewPath"]),
            )
        except Exception as e:
            raise CmsClientError("Request to CMS failed.") from e
