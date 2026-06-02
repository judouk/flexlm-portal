import re


SERVER_RE = re.compile(
    r"^SERVER\s+(?P<hostname>\S+)\s+(?P<hostid>\S+)"
)


VENDOR_RE = re.compile(
    r"^(VENDOR|DAEMON)\s+(?P<vendor>\S+)"
)


FEATURE_RE = re.compile(
    r"^(FEATURE|INCREMENT)\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<vendor>\S+)\s+"
    r"(?P<version>\S+)\s+"
    r"(?P<expiry>\S+)\s+"
    r"(?P<count>\S+)"
)


def parse_license(text: str):
    result = {
        "server": None,
        "vendors": [],
        "features": [],
    }

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        server_match = SERVER_RE.match(line)

        if server_match:
            result["server"] = server_match.groupdict()
            continue

        vendor_match = VENDOR_RE.match(line)

        if vendor_match:
            vendor = vendor_match.group("vendor")

            if vendor not in result["vendors"]:
                result["vendors"].append(vendor)

            continue

        feature_match = FEATURE_RE.match(line)

        if feature_match:
            feature = feature_match.groupdict()

            try:
                feature["count"] = int(feature["count"])
            except ValueError:
                pass

            result["features"].append(feature)

    return result
