import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from app.licenses.merge import (
    build_deployment_license,
    build_deployment_license_with_expired_features,
)


class DeploymentLicenseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.server = SimpleNamespace(
            hostname="licenses.example.test",
            hostid="001122334455",
            lmgrd_port=27000,
            merge_policy="additive",
            daemons=[],
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def license_file(self, name, text, imported_at):
        path = Path(self.temp_dir.name) / name
        path.write_text(text, encoding="utf-8")
        return SimpleNamespace(
            storage_path=str(path),
            imported_at=imported_at,
        )

    def test_additive_removes_expired_features_and_reports_them(self):
        older = self.license_file(
            "older.lic",
            "FEATURE old_feature vendor 1.0 01-jan-2020 5 SIGN=old\n",
            datetime(2024, 1, 1),
        )
        newer = self.license_file(
            "newer.lic",
            "FEATURE active_feature vendor 1.0 permanent 10 SIGN=new\n",
            datetime(2025, 1, 1),
        )

        text, expired = build_deployment_license_with_expired_features(
            self.server,
            [older, newer],
        )

        self.assertNotIn("old_feature", text)
        self.assertIn("active_feature", text)
        self.assertEqual(["old_feature"], [item["name"] for item in expired])

    def test_feature_expiring_today_remains_active(self):
        today = datetime.utcnow().strftime("%d-%b-%Y")
        license_file = self.license_file(
            "expires-today.lic",
            f"FEATURE expires_today vendor 1.0 {today} 5 SIGN=today\n",
            datetime(2025, 1, 1),
        )

        text, expired = build_deployment_license_with_expired_features(
            self.server,
            [license_file],
        )

        self.assertIn("expires_today", text)
        self.assertEqual([], expired)

    def test_latest_only_removes_expired_blocks_and_keeps_other_content(self):
        self.server.merge_policy = "latest_only"
        future_expiry = (datetime.utcnow() + timedelta(days=365)).strftime(
            "%d-%b-%Y"
        )
        latest = self.license_file(
            "latest.lic",
            "\n".join(
                [
                    "SERVER old-host old-id 27000",
                    "VENDOR vendor /old/vendor",
                    "# retained comment",
                    "FEATURE old_feature vendor 1.0 01-jan-20 5 \\",
                    "    SIGN=old",
                    f"FEATURE active_feature vendor 1.0 {future_expiry} 10 SIGN=new",
                ]
            ),
            datetime(2025, 1, 1),
        )

        text, expired = build_deployment_license_with_expired_features(
            self.server,
            [latest],
        )

        self.assertNotIn("old_feature", text)
        self.assertNotIn("SIGN=old", text)
        self.assertIn("active_feature", text)
        self.assertIn("# retained comment", text)
        self.assertEqual(["old_feature"], [item["name"] for item in expired])

    def test_existing_builder_still_returns_text(self):
        license_file = self.license_file(
            "license.lic",
            "FEATURE active_feature vendor 1.0 permanent 10 SIGN=new\n",
            datetime(2025, 1, 1),
        )

        result = build_deployment_license(self.server, [license_file])

        self.assertIsInstance(result, str)
        self.assertIn("active_feature", result)


if __name__ == "__main__":
    unittest.main()
