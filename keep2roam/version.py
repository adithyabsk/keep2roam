"""Get the CLI version."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore


def get_version() -> str:
    """Get the CLI version.

    Returns:
        The package version

    """
    return importlib_metadata.version("keep2roam")  # type: ignore
