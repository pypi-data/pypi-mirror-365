import json
from dataclasses import dataclass
from pathlib import Path

import nbformat

from ssb_pubmd.models import Content

ID_KEY = "_id"


class LocalStorageError(Exception): ...


@dataclass
class LocalStorageAdapter:
    metadata_file_path: Path

    def get_file_id(self, file_path: Path) -> str:
        """
        Returns the content id of a given file path.
        If no id is registered for the given file path,
        it returns an empty string.
        """
        with open(self.metadata_file_path) as metadata_file:
            metadata = json.load(metadata_file)
            return str(metadata.get(str(file_path.absolute()), {}).get(ID_KEY, ""))

    def set_file_id(self, file_path: Path, content_id: str) -> None:
        """Stores a given file's content id in the metadata file"""
        with open(self.metadata_file_path) as metadata_file:
            metadata = json.load(metadata_file)
        metadata[str(file_path.absolute())] = {ID_KEY: content_id}
        with open(self.metadata_file_path, "w") as metadata_file:
            json.dump(metadata, metadata_file)

    def get_content(self, file_path: Path) -> Content:
        """
        Returns the markdown content of a given file.
        If the file is neither a .md or a .ipynb file,
        this function will throw a `LocalStorageError`
        """
        return Content(
            content_id=self.get_file_id(file_path),
            file_path=file_path,
            markdown=self._get_content(file_path),
        )

    def _get_content_from_notebook_file(self, file_path: Path) -> str:
        """Extracts all markdown cells from the notebook and returns it as a string."""
        notebook = nbformat.read(file_path, as_version=nbformat.NO_CONVERT)  # type: ignore
        markdown_cells = []
        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                markdown_cells.append(cell.source)
        sep = "\n\n"
        return sep.join(markdown_cells)

    def _get_content_from_markdown_file(self, file_path: Path) -> str:
        """Returns the content of a markdown file as a string."""
        with open(file_path) as file:
            return file.read()

    def _get_content(self, file_path: Path) -> str:
        file_type = file_path.suffix
        match file_type:
            case ".md":
                return self._get_content_from_markdown_file(file_path)
            case ".ipynb":
                return self._get_content_from_notebook_file(file_path)
            case _:
                raise LocalStorageError(f"Unsupported file type: {file_type}")
