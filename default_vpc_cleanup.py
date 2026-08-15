# Copyright 2024 Randhir Kumar
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# See LICENSE file for details.

import argparse
import json
import logging

import boto3


logger = logging.getLogger(__name__)


class DefaultVpcCleanup:
    def __init__(self, aws_session=None, dry_run=False, regions=None, profile=None, auto_confirm=False, log_level=logging.INFO, export_csv=None, export_json=None, exclude_regions=None):
        self.session = aws_session or boto3
        self.dry_run = dry_run
        self.regions = regions or []
        self.profile = profile
        self.auto_confirm = auto_confirm
        self.log_level = log_level
        self.export_csv = export_csv
        self.export_json = export_json
        self.exclude_regions = exclude_regions or []

        if self.profile:
            self.session = boto3.session.Session(profile_name=self.profile)

    def get_regions_list(self):
        # authentication happening using default aws profile(CLI)
        ec2_client = self.session.client('ec2')

        region_response = ec2_client.describe_regions()
        active_region_list = []
        # fetch all aws regions
        for region in region_response["Regions"]:
            region_name = region["RegionName"]
            active_region_list.append(region_name)

        return active_region_list

    def log(self, message, level=logging.INFO):
        logger.log(level, message)
        print(message)

    def normalize_user_choice(self, choice):
        if not isinstance(choice, str):
            return ""

        normalized = choice.strip().lower()
        if normalized in {"yes", "y"}:
            return "yes"
        if normalized in {"no", "n"}:
            return "no"
        return normalized

    def get_non_default_vpc_details(self, region_list):
        # Get VPC details by region
        # iterate region list and create region specific client
        vpc_id_dict = {}
        region_count = 0
        for region in region_list:
            ec2_region_client = self.session.client('ec2', region_name=region)
            vpc_response = ec2_region_client.describe_vpcs(
                Filters=[{'Name': 'isDefault', 'Values': ['false']}])
            try:
                vpc_id = vpc_response['Vpcs'][0]['VpcId']
            except IndexError:
                continue
            region_count = region_count + 1
            print(str(region_count) + " " + region + " " + vpc_id)
            vpc_id_dict[region] = vpc_id

        return vpc_id_dict

    def get_default_vpc_details(self, region_list):
        # Get VPC details by region
        # iterate region list and create region specific client
        vpc_id_dict = {}
        region_count = 0
        for region in region_list:
            ec2_region_client = self.session.client('ec2', region_name=region)
            vpc_response = ec2_region_client.describe_vpcs(
                Filters=[{'Name': 'isDefault', 'Values': ['true']}])
            try:
                vpc_id = vpc_response['Vpcs'][0]['VpcId']
            except IndexError:
                continue
            region_count = region_count + 1
            print(str(region_count) + " " + region + " " + vpc_id)
            vpc_id_dict[region] = vpc_id

        return vpc_id_dict

    # I needed to delete only below dependencies from default VPC for deleting default VPC
    def delete_vpc_dependencies(self, **region_vpc_id):
        # Get VPC details by region
        # iterate region list and create region specific client
        print("iterating the region vpc dictionary and deleting vpc dependencies")
        for region, vpc_id in region_vpc_id.items():
            print(region, vpc_id)
            ec2 = self.session.resource('ec2', region_name=region)
            vpc = ec2.Vpc(vpc_id)

            for igw in vpc.internet_gateways.all():
                print(igw)
                igw.detach_from_vpc(VpcId=vpc_id)
                igw.delete()
                print(str(igw) + " got deleted")

            for subnets in vpc.subnets.all():
                print(subnets)
                subnets.delete()
                print(str(subnets) + " got deleted")

        print("deleting vpc dependencies done!!!!")

    def delete_default_vpc(self, **region_vpc_id):
        # Get VPC details by region
        # iterate region list and create region specific client
        print("iterating the region vpc dictionary and deleting default VPC")
        for region, vpc_id in region_vpc_id.items():
            print(region, vpc_id)
            ec2_resource = self.session.resource('ec2', region_name=region)
            vpc_resource = ec2_resource.Vpc(vpc_id)
            vpc_resource.delete()
            print("vpc got deleted")

        print("deleting default VPCs done======!!!!")

    def get_account_id(self):
        sts_client = self.session.client("sts")
        return sts_client.get_caller_identity()["Account"]

    def get_account_alias(self):
        iam_client = self.session.client('iam')
        aliases = iam_client.list_account_aliases().get('AccountAliases', [])
        return aliases[0] if aliases else None

    def export_cleanup_summary(self, summary_data):
        if self.export_csv:
            import csv

            with open(self.export_csv, 'w', newline='') as csv_file:
                writer = csv.DictWriter(
                    csv_file, fieldnames=['region', 'vpc_id'])
                writer.writeheader()
                for region, vpc_id in summary_data.items():
                    writer.writerow({'region': region, 'vpc_id': vpc_id})

        if self.export_json:
            payload = [
                {'region': region, 'vpc_id': vpc_id}
                for region, vpc_id in summary_data.items()
            ]
            with open(self.export_json, 'w') as json_file:
                json.dump(payload, json_file, indent=2)

    def filter_regions(self, region_list, allowed_regions=None):
        if not allowed_regions:
            return region_list

        allowed = {region.strip()
                   for region in allowed_regions if region and region.strip()}
        return [region for region in region_list if region in allowed]

    def exclude_regions_from_list(self, region_list, excluded_regions=None):
        if not excluded_regions:
            return region_list

        excluded = {region.strip()
                    for region in excluded_regions if region and region.strip()}
        return [region for region in region_list if region not in excluded]

    def cleanup_default_vpcs(self, region_list):
        filtered_region_list = self.filter_regions(region_list, self.regions)
        filtered_region_list = self.exclude_regions_from_list(
            filtered_region_list, self.exclude_regions)

        if self.regions and not filtered_region_list:
            self.log("No matching AWS regions found for cleanup: " +
                     str(self.regions), logging.WARNING)
            return

        account_id = self.get_account_id()
        self.log("")
        self.log("AWS account id : " + account_id)
        self.log("")

        account_alias = self.get_account_alias()
        if account_alias:
            self.log("AWS account alias : " + account_alias)
        else:
            self.log("AWS account alias : not configured")
        self.log("")

        self.log("Checking all " + str(filtered_region_list.__len__()) +
                 " regions: " + str(filtered_region_list))
        self.log("")

        try:
            default_vpc_id_dict = self.get_default_vpc_details(
                filtered_region_list)
        except Exception as exc:
            self.log(f"Failed to inspect default VPCs: {exc}", logging.ERROR)
            return

        self.log("default vpc IDs before cleanup : " +
                 str(default_vpc_id_dict))
        self.log("")

        if not default_vpc_id_dict:
            self.log("=== Exiting as default VPCs dont exist in this account: " +
                     account_id + " " + (account_alias or "<no alias>"), logging.WARNING)
            return

        if self.export_csv or self.export_json:
            self.export_cleanup_summary(default_vpc_id_dict)

        if self.dry_run:
            self.log("DRY RUN: would clean up default VPCs in these regions: " +
                     str(default_vpc_id_dict), logging.INFO)
            return

        self.log(
            "Confirm once if account ID and default VPCs list printed above are correct before cleanup!")
        self.log("")

        if self.auto_confirm:
            user_input = "yes"
        else:
            user_input = input(
                "Enter yes to proceed and no to abort. Please enter your choice - yes/no : ")

        self.log("")

        if self.normalize_user_choice(user_input) == "yes":
            self.log("========= Start cleaning up ================")
            try:
                self.delete_vpc_dependencies(**default_vpc_id_dict)
                self.log("")
                self.delete_default_vpc(**default_vpc_id_dict)
                self.log("")
            except Exception as exc:
                self.log(
                    f"Cleanup failed during VPC deletion: {exc}", logging.ERROR)
                return
        else:
            self.log("========= Do not proceed and exit ====================")
            return

        self.log("checking for default VPCs post cleanup----------")
        try:
            default_vpc_id_dict = self.get_default_vpc_details(
                filtered_region_list)
        except Exception as exc:
            self.log(
                f"Failed to verify default VPC state after cleanup: {exc}", logging.ERROR)
            return
        self.log("default VPCs post cleanup : " + str(default_vpc_id_dict))
        self.log("")

        self.log("checking for non-default VPCs post cleanup")
        try:
            non_default_vpc_id_dict = self.get_non_default_vpc_details(
                filtered_region_list)
        except Exception as exc:
            self.log(
                f"Failed to review non-default VPCs after cleanup: {exc}", logging.ERROR)
            return
        self.log("non-default VPCs post cleanup : " +
                 str(non_default_vpc_id_dict))
        self.log("")


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Cleanup default AWS VPCs.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview cleanup without deleting resources.")
    parser.add_argument("--region", action="append", default=[],
                        help="Limit cleanup to a specific AWS region. Repeat for multiple regions.")
    parser.add_argument("--exclude-region", action="append", default=[],
                        help="Exclude a region from the cleanup list. Repeat for multiple regions.")
    parser.add_argument("--profile", default=None,
                        help="Use a specific AWS profile configured in your AWS CLI settings.")
    parser.add_argument("--yes", action="store_true",
                        help="Skip interactive confirmation and proceed automatically.")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO",
                                 "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging verbosity level.")
    parser.add_argument("--export-csv", default=None,
                        help="Write the VPC cleanup plan to a CSV file before deleting anything.")
    parser.add_argument("--export-json", default=None,
                        help="Write the VPC cleanup plan to a JSON file before deleting anything.")
    return parser.parse_args(args)


def get_regions_list():
    return DefaultVpcCleanup().get_regions_list()


def normalize_user_choice(choice):
    return DefaultVpcCleanup().normalize_user_choice(choice)


def get_non_default_vpc_details(region_list):
    return DefaultVpcCleanup().get_non_default_vpc_details(region_list)


def get_default_vpc_details(region_list):
    return DefaultVpcCleanup().get_default_vpc_details(region_list)


def delete_vpc_dependencies(**region_vpc_id):
    DefaultVpcCleanup().delete_vpc_dependencies(**region_vpc_id)


def delete_default_vpc(**region_vpc_id):
    DefaultVpcCleanup().delete_default_vpc(**region_vpc_id)


def get_account_id():
    return DefaultVpcCleanup().get_account_id()


def get_account_alias():
    return DefaultVpcCleanup().get_account_alias()


if __name__ == '__main__':
    cli_args = parse_args()
    log_level = getattr(logging, cli_args.log_level.upper())
    logging.basicConfig(level=log_level,
                        format='%(levelname)s: %(message)s')

    cleanup = DefaultVpcCleanup(
        dry_run=cli_args.dry_run,
        regions=cli_args.region,
        profile=cli_args.profile,
        auto_confirm=cli_args.yes,
        log_level=log_level,
        export_csv=cli_args.export_csv,
        export_json=cli_args.export_json,
        exclude_regions=cli_args.exclude_region,
    )
    region_list = cleanup.get_regions_list()
    cleanup.cleanup_default_vpcs(region_list)
