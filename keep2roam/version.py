"""Get the CLI version."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata


def get_version():
    """Get the CLI version."""
    return importlib_metadata.version('keep2roam')
