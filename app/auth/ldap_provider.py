from ldap3 import ALL
from ldap3 import Connection
from ldap3 import Server

from app.config import settings


def role_from_ad_groups(groups):
    ldap_settings = settings["auth"]["ldap"]

    admin_groups = set(
        ldap_settings.get(
            "admin_groups",
            [],
        )
    )

    manager_groups = set(
        ldap_settings.get(
            "manager_groups",
            [],
        )
    )

    user_groups = set(groups)

    if user_groups & admin_groups:
        return "admin"

    if user_groups & manager_groups:
        return "manager"

    return "user"


def authenticate_ldap(
    username,
    password,
):

    ldap_settings = settings["auth"]["ldap"]

    server = Server(
        ldap_settings["server_uri"],
        get_info=ALL,
    )

    #
    # bind using service account
    #

    service_conn = Connection(
        server,
        user=ldap_settings["bind_dn"],
        password=ldap_settings["bind_password"],
        auto_bind=True,
    )

    search_filter = (
        ldap_settings["user_filter"]
        .replace(
            "{username}",
            username,
        )
    )

    service_conn.search(
        ldap_settings["user_search_base"],
        search_filter,
        attributes=[
            "distinguishedName",
            ldap_settings.get(
                "group_attribute",
                "memberOf",
            ),
        ],
    )

    if len(service_conn.entries) != 1:
        return None

    user_entry = service_conn.entries[0]

    user_dn = str(
        user_entry.entry_dn
    )

    #
    # verify supplied password
    #

    try:
        Connection(
            server,
            user=user_dn,
            password=password,
            auto_bind=True,
        )
    except Exception:
        return None

    group_attr = ldap_settings.get(
        "group_attribute",
        "memberOf",
    )

    groups = []

    if hasattr(
        user_entry,
        group_attr,
    ):
        groups = list(
            getattr(
                user_entry,
                group_attr,
            ).values
        )

    return {
        "username": username,
        "groups": groups,
        "role": role_from_ad_groups(
            groups
        ),
    }
