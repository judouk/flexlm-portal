from datetime import datetime
from pathlib import Path

from app.licenses.parser import parse_license

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

def build_additive_license(server, license_files):
    selected_blocks = {}

    sorted_license_files = sorted(
        license_files,
        key=lambda lf: lf.imported_at,
    )

    for license_file in sorted_license_files:
        text = Path(license_file.storage_path).read_text(
            encoding="utf-8",
            errors="ignore",
        )

    for block in logical_blocks(text):
        block_lines = block.splitlines()

        if not block_lines:
            continue

        first_line = block_lines[0].strip()

        if not (
            first_line.startswith("FEATURE ") or
            first_line.startswith("INCREMENT ")
        ):
            continue

        parsed = parse_license(first_line)

        if not parsed["features"]:
            continue

        feature = parsed["features"][0]

        if is_feature_expired(feature):
            continue

        identity = feature_identity(feature)

        selected_blocks[identity] = block

    lines = build_server_lines(server)
    lines.append("")

    for block in sorted(selected_blocks.values()):
        lines.append(block)

    return "\n".join(lines)

def build_deployment_license(server, license_files):
    if server.merge_policy == "latest_only":
        return build_latest_only_license(
            server,
            license_files,
        )

    return build_additive_license(
        server,
        license_files,
    )

def build_latest_only_license(server, license_files):
    latest_license = sorted(
        license_files,
        key=lambda lf: lf.imported_at,
    )[-1]

    text = Path(latest_license.storage_path).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    body = strip_server_lines(text)

    lines = build_server_lines(server)
    lines.append("")
    lines.append(body)

    return "\n".join(lines)

def build_server_lines(server):
    lines = [
        f"SERVER {server.hostname} {server.hostid} {server.lmgrd_port}"
    ]

    for daemon in sorted(server.daemons, key=lambda d: d.name):
        vendor_line = f"DAEMON {daemon.name}"
        if daemon.daemon_path:
            vendor_line += f" {daemon.daemon_path}"

        if daemon.options_file_path:
            vendor_line += f" {daemon.options_file_path}"

        if daemon.port:
            vendor_line += f" PORT={daemon.port}"

        lines.append(vendor_line)

    return lines

def configured_vendor_names(server):
    names = set()

    for daemon in server.daemons:
        names.add(daemon.name)

        if daemon.served_vendors:
            for vendor in daemon.served_vendors.split(","):
                vendor = vendor.strip()

                if vendor:
                    names.add(vendor)

    return names

def feature_identity(feature):
    return (
        feature["name"],
        feature["version"],
        feature["expiry"],
        str(feature["count"]),
    )

def is_feature_expired(feature):
    expiry = parse_expiry(feature["expiry"])

    if expiry is None:
        return False

    return expiry < datetime.utcnow()

def logical_blocks(text: str):
    current = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        current.append(line)

        if line.endswith("\\"):
            continue

        yield "\n".join(current)
        current = []

    if current:
        yield "\n".join(current)


def parse_expiry(expiry: str):
    if expiry.lower() == "permanent":
        return None

    try:
        day, month, year = expiry.split("-")

        return datetime(
            int(year),
            MONTHS[month.lower()],
            int(day),
        )

    except Exception:
        return None

def strip_server_lines(text):
    kept_lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("SERVER "):
            continue

        if stripped.startswith("VENDOR "):
            continue

        if stripped.startswith("DAEMON "):
            continue

        kept_lines.append(line)

    return "\n".join(kept_lines)

