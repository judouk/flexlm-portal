"""Public UI configuration. Never return the application settings dictionary."""


def public_ui_config(settings: dict) -> dict:
    version = settings.get("ux_version", 1)
    if type(version) is not int or version not in (1, 2):
        raise ValueError("ux_version must be the integer 1 or 2")
    return {"ux_version": version}
