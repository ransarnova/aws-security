# Copyright 2024 Randhir Kumar
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# See LICENSE file for details.

import unittest
from unittest.mock import patch

import default_vpc_cleanup


class DefaultVpcCleanupTests(unittest.TestCase):
    def test_get_account_alias_returns_none_when_no_aliases(self):
        class FakeIAM:
            @staticmethod
            def list_account_aliases():
                return {"AccountAliases": []}

        with patch("default_vpc_cleanup.boto3.client", return_value=FakeIAM()):
            self.assertIsNone(default_vpc_cleanup.get_account_alias())

    def test_normalize_user_choice(self):
        self.assertEqual(
            default_vpc_cleanup.normalize_user_choice(" YES "), "yes")
        self.assertEqual(default_vpc_cleanup.normalize_user_choice("no"), "no")
        self.assertEqual(default_vpc_cleanup.normalize_user_choice("y"), "yes")

    def test_default_vpc_cleanup_class_normalizes_choices(self):
        cleanup = default_vpc_cleanup.DefaultVpcCleanup()
        self.assertEqual(cleanup.normalize_user_choice(" YES "), "yes")
        self.assertEqual(cleanup.normalize_user_choice("n"), "no")

    def test_default_vpc_cleanup_filters_regions(self):
        cleanup = default_vpc_cleanup.DefaultVpcCleanup()
        self.assertEqual(
            cleanup.filter_regions(
                ["us-east-1", "us-west-2", "eu-west-1"],
                ["us-east-1", "eu-west-1"],
            ),
            ["us-east-1", "eu-west-1"],
        )

    def test_parse_args_supports_dry_run_and_region_filters(self):
        args = default_vpc_cleanup.parse_args(
            ["--dry-run", "--region", "us-east-1", "--region", "eu-west-1"]
        )
        self.assertTrue(args.dry_run)
        self.assertEqual(args.region, ["us-east-1", "eu-west-1"])

    def test_parse_args_supports_profile_and_yes_flags(self):
        args = default_vpc_cleanup.parse_args([
            "--profile", "staging",
            "--yes",
        ])
        self.assertEqual(args.profile, "staging")
        self.assertTrue(args.yes)

    def test_parse_args_supports_log_level_and_csv_export(self):
        args = default_vpc_cleanup.parse_args([
            "--log-level", "DEBUG",
            "--export-csv", "cleanup-report.csv",
        ])
        self.assertEqual(args.log_level, "DEBUG")
        self.assertEqual(args.export_csv, "cleanup-report.csv")

    def test_parse_args_supports_json_export_and_exclude_regions(self):
        args = default_vpc_cleanup.parse_args([
            "--export-json", "cleanup-report.json",
            "--exclude-region", "us-west-2",
            "--exclude-region", "eu-west-1",
        ])
        self.assertEqual(args.export_json, "cleanup-report.json")
        self.assertEqual(args.exclude_region, ["us-west-2", "eu-west-1"])

    def test_cleanup_default_vpcs_handles_region_exclusion(self):
        cleanup = default_vpc_cleanup.DefaultVpcCleanup(
            regions=["us-east-1", "us-west-2"])
        self.assertEqual(
            cleanup.filter_regions(
                ["us-east-1", "us-west-2", "eu-west-1"], ["us-east-1", "us-west-2"]),
            ["us-east-1", "us-west-2"],
        )


if __name__ == "__main__":
    unittest.main()
