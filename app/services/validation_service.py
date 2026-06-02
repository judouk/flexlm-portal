from datetime import datetime

def parse_expiry(value):
    if not value:
        return None

    if value.lower() == "permanent":
        return None

    for fmt in [
        "%d-%b-%Y",
        "%d-%b-%y",
    ]:
        try:
            return datetime.strptime(
                value,
                fmt,
            )
        except ValueError:
            pass

    return None

def validate_deployment(
    deployment,
    server,
    license_text,
):

    results = []

    def add(
        severity,
        code,
        message,
    ):
        results.append(
            {
                "severity": severity,
                "code": code,
                "message": message,
            }
        )

    lines = license_text.splitlines()

    daemon_names = {
        daemon.name
        for daemon in server.daemons
    }

    #
    # SERVER check
    #

    if not any(
        line.startswith("SERVER ")
        for line in lines
    ):
        add(
            "error",
            "missing_server",
            "Deployment contains no SERVER line",
        )

    #
    # Configured daemon checks
    #

    if not daemon_names:
        add(
            "error",
            "missing_daemons",
            "License server has no configured vendor daemons",
        )


    for daemon in server.daemons:
        if not daemon.daemon_path:
            add(
                "warning",
                "missing_daemon_path",
                f"{daemon.name} has no daemon binary configured",
            )

        if not daemon.options_file_path:
            add(
                "warning",
                "missing_options_file",
                f"{daemon.name} has no options file configured",
            )


    #
    # FEATURE checks
    #

    feature_daemons = set()

    for line in lines:
        parts = line.split()

        if not parts:
            continue

        if parts[0] not in [
            "FEATURE",
            "INCREMENT",
        ]:
            continue

        if len(parts) > 2:
            feature_daemons.add(
                parts[2]
            )

        if len(parts) > 4:
            expiry = parse_expiry(
                parts[4]
            )

            if expiry:
                if expiry < datetime.utcnow():
                    add(
                        "warning",
                        "expired_feature",
                        (
                            f"{parts[1]} "
                            f"expired on {parts[4]}"
                        ),
                    )


    #
    # FEATURE daemon ownership
    #

    for daemon in feature_daemons:
        if daemon not in daemon_names:
            add(
                "error",
                "unknown_daemon",
                (
                    "Feature references "
                    f"unconfigured daemon {daemon}"
                ),
            )

    return results
