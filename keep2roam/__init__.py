"""Convert Google Takeout Dump to Roam Daily Notes."""

from keep2roam.cli import cli as k2r
from keep2roam.version import get_version


__version__ = get_version()
del get_version
__all__ = ["k2r"]
