import sys
from dataclasses import dataclass

from ssb_pubmd.ports import CmsManager


@dataclass
class CliAdapter:
    cms_manager: CmsManager

    def run(self, system_arguments: list[str]) -> None:
        match system_arguments:
            case [_, "sync", file_path]:
                preview = self.cms_manager.sync(file_path)
                print(f"Preview URL: {preview}")
                # except Exception as e:
                #     print(f"Error during sync: {e}")
                #     sys.exit(1)
            case _:
                print("Usage: ssb-pubmd sync <content_file_path>")
                sys.exit(1)
