import toml


def get_version() -> str:
    try:
        with open("pyproject.toml") as f:
            data = toml.load(f)
            return data["project"]["version"]
    except FileNotFoundError:
        return "Unknown"
