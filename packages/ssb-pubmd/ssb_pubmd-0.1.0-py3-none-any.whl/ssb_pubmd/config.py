import os
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "SSB_PUBMD"


@dataclass
class Config:
    metadata_file_path: Path
    cms_base_url: str
    gc_secret_resource_name: str


def get_config(metadata_file_path: Path | None = None) -> Config:
    user_data_dir = Path.home() / ".local" / "share" / APP_NAME
    if not metadata_file_path:
        user_data_dir.mkdir(parents=True, exist_ok=True)
        metadata_file_path = user_data_dir / "metadata.json"
    if not metadata_file_path.exists():
        with open(metadata_file_path, "x") as metadata_file:
            metadata_file.write("{}\n")
    return Config(
        metadata_file_path=metadata_file_path,
        cms_base_url=os.environ[f"{APP_NAME}_BASE_URL"],
        gc_secret_resource_name=os.environ[f"{APP_NAME}_GC_SECRET_RESOURCE_NAME"],
    )
