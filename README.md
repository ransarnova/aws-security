# aws-security

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Collection of AWS security and cleanup utilities for safer cloud operations.

## Overview

This repo highlights AWS cloud security recommendations and provides a practical utility for removing default VPCs from AWS accounts. As a best practice, it is recommended to delete default VPCs and create custom VPCs with stricter security controls. Even if a default VPC is not currently in use, removing it is often better from a security perspective because it reduces unnecessary attack surface and removes default network assumptions.

This repository contains a Python utility to identify and remove default Amazon VPCs across AWS regions where they are no longer needed. It is intentionally designed to be explicit, cautious, and safety-first because deleting VPCs and related resources is a destructive action.

The script is intentionally conservative:
- it lists all enabled AWS regions
- finds default VPCs in each region
- prints the exact VPCs before cleanup
- supports a dry-run mode
- supports region filtering and exclusion
- supports safe export options and explicit confirmation before deleting anything

The cleanup utility can be used to remove default VPCs in an AWS account in a controlled and reviewable way.

## What it does

The utility performs the following steps:

1. Lists all available AWS regions for the current account or profile.
2. Finds default VPCs in each region.
3. Displays the account ID and account alias.
4. Shows the default VPC IDs that are candidates for removal.
5. Optionally filters or excludes specific regions.
6. In dry-run mode, shows what would be deleted without making any changes.
7. If the user confirms, removes VPC dependencies such as internet gateways and subnets.
8. Deletes the default VPC itself.
9. Re-checks the account after cleanup so the user can validate the result.

## Important warning

This tool deletes AWS resources. Use it only when you understand the impact.

Always validate:
- you are connected to the correct AWS profile
- you are deleting the intended account and region set
- default VPCs are acceptable to remove in your environment
- no critical workloads depend on the default network setup

## Prerequisites

- Python 3.8+
- AWS CLI configured with a valid profile or default credentials
- boto3 installed

Install dependencies:

```bash
pip install boto3
```

## Usage

Run the script directly:

```bash
python3 default_vpc_cleanup.py
```

### Dry run

Preview what would be removed without deleting anything:

```bash
python3 default_vpc_cleanup.py --dry-run
```

### Limit cleanup to selected regions

```bash
python3 default_vpc_cleanup.py --region us-east-1 --region us-west-2
```

### Exclude specific regions

```bash
python3 default_vpc_cleanup.py --exclude-region us-west-2 --exclude-region eu-west-1
```

### Use a specific AWS profile

```bash
python3 default_vpc_cleanup.py --profile staging
```

### Skip interactive confirmation

```bash
python3 default_vpc_cleanup.py --yes
```

### Export cleanup details

```bash
python3 default_vpc_cleanup.py --dry-run --export-json cleanup-plan.json
python3 default_vpc_cleanup.py --dry-run --export-csv cleanup-plan.csv
```

### Example workflow

1. Run the script in dry-run mode.
2. Review the default VPC IDs and regions.
3. Confirm the target setup is correct.
4. Run the script again without `--dry-run`.
5. Enter `yes` when prompted, or use `--yes` for automation.

## Why this matters

Default VPCs are available by default in AWS accounts, but they are not always desirable in a hardened security posture. Custom VPCs allow teams to control:
- subnets and routing
- security groups and NACLs
- public and private exposure
- network segmentation and isolation

By deleting default VPCs and creating well-defined custom VPCs, teams can reduce ambiguity and improve their overall security baseline.

## Script behavior

The script uses the AWS SDK to:
- call `ec2.describe_regions()`
- call `ec2.describe_vpcs()` filtered by `isDefault=true`
- remove internet gateways attached to the default VPC
- delete subnets in the default VPC
- delete the VPC itself

## Reference

- https://stackoverflow.com/questions/53185119/aws-python-script-to-retrieve-list-of-resources-are-currently-in-use

## Security recommendations

Before using this utility in a real account:
- verify the AWS profile and account context
- restrict cleanup to a small set of regions first
- run in dry-run mode at least once
- ensure no critical workloads depend on default VPC behavior
- keep a rollback or recovery plan ready

## Project structure

- `default_vpc_cleanup.py` - main AWS cleanup utility
- `test_default_vpc_cleanup.py` - unit tests for CLI behavior, filtering, and safety checks

## Running tests

```bash
python3 -m unittest -q
```

## Notes

This script is intentionally focused on default VPC cleanup. It is not a general-purpose AWS resource manager, and it should stay narrow and deliberate to reduce accidental deletion risk.

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) file for details.

By contributing to this project, you agree to license your contributions under the same license.

