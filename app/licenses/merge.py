from datetime import datetime
from pathlib import Path

from app.licenses.parser import parse_license

def build_additive_license(server, license_files):
    license_text, _ = build_additive_license_with_expired_features(
        server,
        license_files,
    )

    return license_text

def build_additive_license_with_expired_features(server, license_files):
    selected_blocks = {}
    expired_features = []

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
                expired_features.append(feature)
                continue

            identity = feature_identity(feature)

            selected_blocks[identity] = block

    lines = build_server_lines(server)
    lines.append("")

    for block in sorted(selected_blocks.values()):
        lines.append(block)

    return "\n".join(lines), unique_features(expired_features)

def build_deployment_license(server, license_files):
    license_text, _ = build_deployment_license_with_expired_features(
        server,
        license_files,
    )

    return license_text

def build_deployment_license_with_expired_features(server, license_files):
    if server.merge_policy == "latest_only":
        return build_latest_only_license_with_expired_features(
            server,
            license_files,
        )

    return build_additive_license_with_expired_features(
        server,
        license_files,
    )

def build_latest_only_license(server, license_files):
    license_text, _ = build_latest_only_license_with_expired_features(
        server,
        license_files,
    )

    return license_text

def build_latest_only_license_with_expired_features(server, license_files):
    latest_license = sorted(
        license_files,
        key=lambda lf: lf.imported_at,
    )[-1]

    text = Path(latest_license.storage_path).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    body, expired_features = remove_expired_feature_blocks(
        strip_server_lines(text)
    )

    lines = build_server_lines(server)
    lines.append("")
    lines.append(body)

    return "\n".join(lines), expired_features

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

def remove_expired_feature_blocks(text):
    kept_blocks = []
    expired_features = []

    for block in logical_blocks(text):
        block_lines = block.splitlines()

        if not block_lines:
            kept_blocks.append(block)
            continue

        parsed = parse_license(block_lines[0].strip())

        if parsed["features"]:
            feature = parsed["features"][0]

            if is_feature_expired(feature):
                expired_features.append(feature)
                continue

        kept_blocks.append(block)

    return "\n".join(kept_blocks), unique_features(expired_features)

def unique_features(features):
    unique = []
    seen = set()

    for feature in features:
        identity = feature_identity(feature)

        if identity in seen:
            continue

        seen.add(identity)
        unique.append(feature)

    return unique

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

    for fmt in [
        "%d-%b-%Y",
        "%d-%b-%y",
    ]:
        try:
            return datetime.strptime(expiry, fmt)
        except ValueError:
            pass

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
