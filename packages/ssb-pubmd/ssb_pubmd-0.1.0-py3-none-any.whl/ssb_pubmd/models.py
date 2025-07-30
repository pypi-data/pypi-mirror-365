from dataclasses import dataclass
from pathlib import Path


@dataclass
class CmsResponse:
    id: str
    preview_url: str


@dataclass
class Content:
    content_id: str
    file_path: Path
    markdown: str

    @property
    def display_name(self) -> str:
        """Generate a display name for the content."""
        return self.file_path.stem.replace("_", " ").title()

    def to_json(self) -> dict[str, str]:
        """Returns a json representation of the content."""
        return {
            "_id": self.content_id,
            "displayName": self.display_name,
            "markdown": self.markdown,
        }
