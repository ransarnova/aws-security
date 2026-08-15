# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in aws-security, please report it responsibly by emailing your findings to the repository maintainers. **Do not** create a public GitHub issue for security vulnerabilities.

When reporting a security issue, please include:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if you have one)

Your report will be handled confidentially, and you will be kept informed of the remediation process.

## Security Considerations

This utility deletes AWS resources. Before using it, you must understand the following security implications:

### AWS Account Access

- **Credential Handling**: The utility uses the AWS SDK, which respects your AWS credentials (environment variables, AWS config, or instance roles).
- **Profile Support**: Use `--profile` to specify a named AWS profile if your account is not the default.
- **Credential Security**: Ensure your AWS credentials are properly secured and not exposed in logs, commits, or shell history.

### Destructive Operations

- **VPC Deletion is Irreversible**: Deleting a VPC cannot be undone. There is no rollback mechanism in this tool.
- **Resource Dependencies**: The utility removes dependencies (internet gateways, subnets) before deleting the VPC. However, if there are other resources attached to the VPC (EC2 instances, RDS databases, etc.), deletion will fail and AWS will report the error.
- **Dry-Run Mode**: Always run with `--dry-run` first to verify what will be deleted.

### Account and Region Safety

- **Region Filtering**: Use `--region` or `--exclude-region` to limit cleanup to specific regions and reduce risk.
- **Account Verification**: The utility displays your AWS account ID and alias before proceeding. Verify this is correct.
- **Confirmation Prompts**: By default, the utility asks for explicit confirmation (`yes` or `no`). Respond carefully.
- **Automation**: Use `--yes` only in controlled environments (CI/CD, automation scripts) where you have full confidence in the execution context.

### Pre-Deployment Checklist

Before running this utility in a production AWS account, verify:

- ✅ You are connected to the **correct AWS account** (check account ID and alias)
- ✅ You understand which regions will be cleaned up
- ✅ Default VPCs are acceptable to remove in your environment
- ✅ No critical workloads depend on default VPC behavior
- ✅ You have tested the utility in a **non-production account** first
- ✅ You have a **rollback or recovery plan** ready (e.g., VPC re-creation steps)
- ✅ You have reviewed the dry-run output and understand the changes
- ✅ You have appropriate AWS IAM permissions:
  - `ec2:DescribeRegions`
  - `ec2:DescribeVpcs`
  - `ec2:DescribeInternetGateways`
  - `ec2:DescribeSubnets`
  - `ec2:DetachInternetGateway`
  - `ec2:DeleteInternetGateway`
  - `ec2:DeleteSubnet`
  - `ec2:DeleteVpc`
  - `iam:GetAccountAlias` (optional, for display only)

### IAM Permissions

Ensure your AWS user or role has the minimum required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeRegions",
        "ec2:DescribeVpcs",
        "ec2:DescribeInternetGateways",
        "ec2:DescribeSubnets",
        "ec2:DetachInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:DeleteSubnet",
        "ec2:DeleteVpc"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:GetAccountAlias",
      "Resource": "*"
    }
  ]
}
```

### Logging and Audit

- Enable AWS CloudTrail to log all VPC deletion API calls for audit purposes.
- The utility supports `--log-level` to adjust verbosity for troubleshooting.
- Consider exporting cleanup details with `--export-json` or `--export-csv` for record-keeping.

## Testing in Development

Before running against production accounts:

1. **Test in a Sandbox Account**: Create a separate AWS account specifically for testing.
2. **Create Test VPCs**: Use the sandbox account's default VPCs for testing.
3. **Verify Dry-Run**: Always start with dry-run mode:
   ```bash
   python3 default_vpc_cleanup.py --dry-run
   ```
4. **Review Output**: Carefully review the VPC IDs and regions listed.
5. **Run Unit Tests**: Verify the test suite passes:
   ```bash
   python3 -m unittest -q
   ```

## Known Limitations

- This utility only handles default VPCs. It does not manage custom VPCs or other AWS resources.
- If a default VPC has resources that depend on it, deletion will fail with an AWS API error.
- The utility respects AWS API rate limits. Large-scale operations may be subject to throttling.

## Security Best Practices

- **Principle of Least Privilege**: Create an IAM role with only the permissions listed above.
- **MFA**: Require multi-factor authentication (MFA) for AWS console access.
- **Audit Logs**: Enable AWS CloudTrail and review deletion events.
- **Code Review**: Have team members review dry-run output before approving real deletion.
- **Backup and Recovery**: Keep documentation on how to recreate VPCs if needed.

## Scope and Focus

This utility is intentionally focused on default VPC cleanup only. It does not:
- Manage custom VPCs
- Delete other AWS resources
- Perform general cloud resource cleanup

This narrow scope is intentional to reduce accidental deletion risk and maintain code clarity.

## Questions or Concerns?

If you have security concerns or questions about this utility, please open an issue on GitHub or contact the maintainers.

Thank you for using aws-security responsibly! 🔒
