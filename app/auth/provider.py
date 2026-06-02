from app.config import settings

def role_from_groups(groups: list[str]) -> str:
    auth_settings = settings["auth"]["header"]

    admin_groups = set(auth_settings.get("admin_groups", []))
    manager_groups = set(auth_settings.get("manager_groups", []))

    user_groups = set(groups)

    if user_groups & admin_groups:
        return "admin"

    if user_groups & manager_groups:
        return "manager"

    return "user"

def parse_groups(value: str | None) -> list[str]:
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]
