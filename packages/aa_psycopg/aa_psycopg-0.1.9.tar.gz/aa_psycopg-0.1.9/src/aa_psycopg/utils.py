import yaml

from pathlib import Path


def read_yaml(yaml_path: Path) -> dict:
    """Read a YAML file and return its content.

    Args:
        yaml_path (Path): Path to the YAML file.

    Returns:
        dict: Content of the YAML file.
    """
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def read_file(file_path: Path) -> str:
    """Read a file and return its content.

    Args:
        file_path (Path): Path to the file.

    Returns:
        str: Content of the file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
