import unittest
from datetime import date

from app.licenses.summary import aggregate_licence_summary
from app.licenses.summary import is_current_licence
from app.licenses.summary import parse_product_licence_rights
from app.licenses.summary import summarise_licence_text


CADENCE_SAMPLE = """\
# Product Id  : 95800,  [Version: 25.1]
# Product Name: Virtuoso Layout Suite EXL
# Licensed Rights:
#   Start Date: 23-jul-2026 Exp Date: 06-sep-2026   Product Qty: 2 Type: Floating
# Licensed Rights:
#   Start Date: 23-jul-2026 Exp Date: 25-aug-2026   Product Qty: 1 Type: Floating
# Licensed Rights:
#   Start Date: 23-jul-2026 Exp Date: 23-oct-2026   Product Qty: 2 Type: Floating
# Licensed Rights:
#   Start Date: 23-jul-2026 Exp Date: 27-sep-2026   Product Qty: 3 Type: Floating
"""


class LicenceSummaryTests(unittest.TestCase):
    def test_parses_cadence_product_rights(self):
        self.assertEqual(
            [
                {
                    "feature": "Virtuoso Layout Suite EXL",
                    "count": 2,
                    "expiry_date": "2026-09-06",
                },
                {
                    "feature": "Virtuoso Layout Suite EXL",
                    "count": 1,
                    "expiry_date": "2026-08-25",
                },
                {
                    "feature": "Virtuoso Layout Suite EXL",
                    "count": 2,
                    "expiry_date": "2026-10-23",
                },
                {
                    "feature": "Virtuoso Layout Suite EXL",
                    "count": 3,
                    "expiry_date": "2026-09-27",
                },
            ],
            parse_product_licence_rights(CADENCE_SAMPLE),
        )

    def test_uses_product_rights_instead_of_duplicate_feature_lines(self):
        text = CADENCE_SAMPLE + (
            "\nFEATURE Virtuoso_Layout_Suite_EXL cdslmd "
            "25.1 06-sep-2026 8 SIGN=example\n"
        )

        self.assertEqual(4, len(summarise_licence_text(text)))

    def test_falls_back_to_standard_flexlm_features(self):
        self.assertEqual(
            [
                {
                    "feature": "compiler",
                    "count": 5,
                    "expiry_date": None,
                }
            ],
            summarise_licence_text(
                "FEATURE compiler vendor 1.0 permanent 5 SIGN=example"
            ),
        )

    def test_aggregates_matching_server_feature_and_expiry(self):
        rows = aggregate_licence_summary(
            [
                {
                    "license_server": "Cadence",
                    "feature": "Virtuoso Layout Suite EXL",
                    "count": 1,
                    "expiry_date": "2026-08-25",
                },
                {
                    "license_server": "Cadence",
                    "feature": "Virtuoso Layout Suite EXL",
                    "count": 2,
                    "expiry_date": "2026-08-25",
                },
            ]
        )

        self.assertEqual(3, rows[0]["count"])

    def test_expiry_date_remains_current_through_that_date(self):
        entry = {
            "feature": "compiler",
            "count": 1,
            "expiry_date": "2026-07-30",
        }

        self.assertTrue(
            is_current_licence(entry, today=date(2026, 7, 30))
        )
        self.assertFalse(
            is_current_licence(entry, today=date(2026, 7, 31))
        )


if __name__ == "__main__":
    unittest.main()
