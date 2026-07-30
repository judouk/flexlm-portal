import re
from datetime import date, datetime

from app.licenses.parser import parse_license


PRODUCT_NAME_RE = re.compile(
    r"^Product Name:\s*(?P<name>.+?)\s*$",
    re.IGNORECASE,
)

PRODUCT_ID_RE = re.compile(
    r"^Product Id\s*:",
    re.IGNORECASE,
)

LICENSED_RIGHT_RE = re.compile(
    r"^Start Date:\s*(?P<start>\S+)\s+"
    r"Exp Date:\s*(?P<expiry>\S+)\s+"
    r"Product Qty:\s*(?P<count>\d+)\b",
    re.IGNORECASE,
)


def normalise_expiry(value):
    if not value or value.lower() == "permanent":
        return None

    for fmt in ("%d-%b-%Y", "%d-%b-%y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass

    return value


def parse_product_licence_rights(text):
    rights = []
    product_name = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if line.startswith("#"):
            line = line[1:].strip()

        if PRODUCT_ID_RE.match(line):
            product_name = None
            continue

        product_match = PRODUCT_NAME_RE.match(line)
        if product_match:
            product_name = product_match.group("name").strip()
            continue

        right_match = LICENSED_RIGHT_RE.match(line)
        if right_match and product_name:
            rights.append(
                {
                    "feature": product_name,
                    "count": int(right_match.group("count")),
                    "expiry_date": normalise_expiry(
                        right_match.group("expiry")
                    ),
                }
            )

    return rights


def summarise_licence_text(text):
    product_rights = parse_product_licence_rights(text)

    if product_rights:
        return product_rights

    return [
        {
            "feature": feature["name"],
            "count": feature["count"],
            "expiry_date": normalise_expiry(feature["expiry"]),
        }
        for feature in parse_license(text)["features"]
        if isinstance(feature["count"], int)
    ]


def aggregate_licence_summary(entries):
    totals = {}

    for entry in entries:
        key = (
            entry["license_server"],
            entry["feature"],
            entry["expiry_date"],
        )
        totals[key] = totals.get(key, 0) + entry["count"]

    rows = [
        {
            "license_server": key[0],
            "feature": key[1],
            "count": count,
            "expiry_date": key[2],
        }
        for key, count in totals.items()
    ]

    return sorted(
        rows,
        key=lambda row: (
            row["license_server"].lower(),
            row["feature"].lower(),
            row["expiry_date"] is None,
            row["expiry_date"] or "",
        ),
    )


def is_current_licence(entry, today=None):
    expiry_date = entry["expiry_date"]

    if expiry_date is None:
        return True

    try:
        expiry = date.fromisoformat(expiry_date)
    except ValueError:
        return True

    return expiry >= (today or datetime.utcnow().date())
