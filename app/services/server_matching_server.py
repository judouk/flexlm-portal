from app.licenses.merge import configured_vendor_names

def match_server(db, parsed):
    hostid = (
        parsed.get("server", {})
        .get("hostid", "")
        .lower()
    )

    feature_vendors = {
        feature["vendor"]
        for feature in parsed["features"]
    }

    candidates = []

    from app.models.license_server import LicenseServer

    servers = db.query(
        LicenseServer
    ).all()

    #
    # hostid match
    #
    for server in servers:
        if (
            server.hostid
            and server.hostid.lower() == hostid
        ):
            candidates.append(server)

    if len(candidates) == 0:
        return None, (
            f"No server found for "
            f"hostid {hostid}"
        )

    if len(candidates) == 1:
        return candidates[0], None

    #
    # Multiple servers share hostid
    #
    matches = []

    for server in candidates:
        served = configured_vendor_names(server)

        if (
            feature_vendors
            & served
        ):
            matches.append(server)

    if len(matches) == 1:
        return matches[0], None

    if len(matches) == 0:
        return (
            None,
            (
                f"No matching server found "
                f"for vendors "
                f"{sorted(feature_vendors)}"
            ),
        )

    return (
        None,
        (
            f"Multiple matching servers "
            f"found"
        ),
    )
