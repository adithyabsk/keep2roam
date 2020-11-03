"""Test the version file."""


def test_get_version():
    """Test whether get_version and pyproject.toml agree"""
    from pathlib import Path

    import toml

    from keep2roam.version import get_version

    pyproject_path = Path(__file__).parent / Path("../pyproject.toml")
    with open(pyproject_path, "r") as file:
        pyproject = toml.load(file)

    assert get_version() == pyproject["tool"]["poetry"]["version"]
