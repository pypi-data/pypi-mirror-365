import sys

from ssb_pubmd.adapters.cli import CliAdapter
from ssb_pubmd.adapters.cms_client import MimirCmsClient
from ssb_pubmd.adapters.local_storage import LocalStorageAdapter
from ssb_pubmd.adapters.secret_manager_client import GoogleSecretManagerClient
from ssb_pubmd.config import get_config
from ssb_pubmd.enonic_cms_manager import EnonicCmsManager


def main() -> None:
    config = get_config()
    cms_manager = EnonicCmsManager(
        config=config,
        cms_client=MimirCmsClient(config.cms_base_url),
        secret_manager_client=GoogleSecretManagerClient(config.gc_secret_resource_name),
        content_file_handler=LocalStorageAdapter(config.metadata_file_path),
    )
    cli_adapter = CliAdapter(cms_manager=cms_manager)
    cli_adapter.run(sys.argv)


if __name__ == "__main__":
    main()
