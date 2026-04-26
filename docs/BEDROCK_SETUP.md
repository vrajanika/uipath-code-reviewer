# AWS Bedrock Setup Guide

This guide walks you through setting up AWS Bedrock with Claude to use it as the AI engine for the UiPath Code Reviewer Bot.

## Table of Contents

- [Overview](#overview)
- [Step 1: AWS Account & IAM Setup](#step-1-aws-account--iam-setup)
- [Step 2: Enable Bedrock Model Access](#step-2-enable-bedrock-model-access)
- [Step 3: Configure Credentials](#step-3-configure-credentials)
- [Step 4: Choose a Claude Model ID](#step-4-choose-a-claude-model-id)
- [Step 5: Set Environment Variables](#step-5-set-environment-variables)
- [Step 6: Set Up GitHub Actions Secrets](#step-6-set-up-github-actions-secrets)
- [IAM Roles vs. Access Keys](#iam-roles-vs-access-keys)
- [Supported AWS Regions](#supported-aws-regions)
- [Troubleshooting](#troubleshooting)

---

## Overview

The bot uses the [AWS Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) to call Claude models. You need:

1. An AWS account with Bedrock access
2. Model access enabled for the Claude model you want to use
3. IAM credentials (access key pair **or** an IAM role attached to your compute environment)

---

## Step 1: AWS Account & IAM Setup

### Create an IAM user or role with Bedrock permissions

**Option A — IAM user (for local development)**

1. Open the [AWS IAM Console](https://console.aws.amazon.com/iam/).
2. Go to **Users → Create user**.
3. Give the user a name (e.g. `uipath-reviewer-bot`).
4. On the **Permissions** page, attach the following policy directly or create a custom one:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "BedrockInvokeModel",
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:Converse"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude*"
       }
     ]
   }
   ```

5. Finish creating the user and go to **Security credentials → Create access key**.
6. Choose **Application running outside AWS**, copy the **Access key ID** and **Secret access key**.

**Option B — IAM role (for EC2 / ECS / GitHub Actions with OIDC)**

Attach the same policy above to the role. The boto3 SDK will automatically pick up credentials from the instance metadata or OIDC token — no explicit key/secret needed.

---

## Step 2: Enable Bedrock Model Access

Claude models on Bedrock require explicit opt-in.

1. Open the [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/).
2. In the left navigation pane, choose **Model access**.
3. Click **Manage model access** (top right).
4. Find **Anthropic** and tick the Claude model(s) you want to use (e.g. *Claude 3.5 Sonnet v2*).
5. Click **Request model access** and accept Anthropic's usage policy.
6. Wait until the status changes to **Access granted** (usually takes a few seconds to a few minutes).

> **Note:** Model access is region-specific. Enable access in every region you intend to use.

---

## Step 3: Configure Credentials

### Local development

Copy `.env.example` to `.env` and fill in your AWS credentials:

```env
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Only required when NOT using IAM roles / instance profiles
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

> **Security reminder:** Never commit `.env` to source control. It is already listed in `.gitignore`.

### Using a named AWS profile

If you manage multiple AWS accounts with `~/.aws/credentials`, you can set the profile instead of an explicit key pair:

```bash
export AWS_PROFILE=uipath-reviewer
```

The boto3 SDK respects `AWS_PROFILE` automatically.

---

## Step 4: Choose a Claude Model ID

Use one of the following Anthropic model IDs available on Bedrock.  
Always check the [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) for the current list and regional availability.

| Model | Model ID | Notes |
|-------|----------|-------|
| Claude 3.5 Sonnet v2 *(recommended)* | `anthropic.claude-3-5-sonnet-20241022-v2:0` | Best balance of speed and quality |
| Claude 3.5 Haiku | `anthropic.claude-3-5-haiku-20241022-v1:0` | Fastest, lowest cost |
| Claude 3 Opus | `anthropic.claude-3-opus-20240229-v1:0` | Highest capability, higher cost |
| Claude 3 Sonnet | `anthropic.claude-3-sonnet-20240229-v1:0` | Balanced |
| Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | Fast, economical |

Set your chosen model ID in the environment:

```env
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

---

## Step 5: Set Environment Variables

The following environment variables are read by the bot:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | ✅ Yes | `us-east-1` | AWS region with Bedrock enabled |
| `BEDROCK_MODEL_ID` | ✅ Yes | `anthropic.claude-3-5-sonnet-20241022-v2:0` | Bedrock model ID |
| `AWS_ACCESS_KEY_ID` | ⚠️ See note | — | IAM access key ID |
| `AWS_SECRET_ACCESS_KEY` | ⚠️ See note | — | IAM secret access key |
| `AWS_SESSION_TOKEN` | ❌ No | — | Required only for temporary STS credentials |
| `GITHUB_TOKEN` | ✅ Yes | — | GitHub personal access token or Actions token |

> **⚠️ Note on AWS credentials:** `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are not required when the bot runs on AWS infrastructure (EC2, ECS, Lambda, etc.) with an attached IAM role, or when using GitHub Actions with OIDC federation. In those cases, boto3 discovers credentials automatically.

---

## Step 6: Set Up GitHub Actions Secrets

For the GitHub Actions workflow to authenticate with Bedrock, add the following secrets to your repository:

1. Go to your repository → **Settings → Secrets and variables → Actions**.
2. Click **New repository secret** for each of the following:

| Secret Name | Description |
|-------------|-------------|
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |
| `BEDROCK_MODEL_ID` | Claude model ID (e.g. `anthropic.claude-3-5-sonnet-20241022-v2:0`) |
| `AWS_ACCESS_KEY_ID` | IAM access key ID (skip if using OIDC) |
| `AWS_SECRET_ACCESS_KEY` | IAM secret access key (skip if using OIDC) |

> **Tip — GitHub Actions OIDC (more secure):** Instead of storing long-lived access keys as secrets, you can configure an IAM role that trusts GitHub's OIDC provider. See [GitHub's documentation](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) for a step-by-step guide.

---

## IAM Roles vs. Access Keys

| Method | Best for | Security |
|--------|----------|----------|
| IAM access keys | Local development, CI without OIDC | ⚠️ Rotate regularly, never commit |
| IAM role on EC2/ECS | Self-hosted runners, AWS-hosted bots | ✅ No credentials to manage |
| GitHub Actions OIDC | GitHub-hosted runners | ✅ Best practice for Actions |
| AWS named profiles | Local multi-account setups | ✅ Credentials stay in `~/.aws` |

---

## Supported AWS Regions

Bedrock is not available in all regions. Claude models are currently available in (among others):

- `us-east-1` — US East (N. Virginia) *(recommended)*
- `us-west-2` — US West (Oregon)
- `eu-west-1` — Europe (Ireland)
- `eu-central-1` — Europe (Frankfurt)
- `ap-southeast-1` — Asia Pacific (Singapore)
- `ap-northeast-1` — Asia Pacific (Tokyo)

Check [AWS Bedrock regional availability](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html) for the latest list.

---

## Troubleshooting

### "An error occurred (AccessDeniedException)"

- Verify the IAM user/role has the `bedrock:Converse` permission.
- Ensure model access has been **granted** in the Bedrock console for the selected region.
- Confirm `AWS_REGION` matches the region where you enabled model access.

### "An error occurred (ValidationException): The provided model identifier is invalid"

- Check that the `BEDROCK_MODEL_ID` value matches exactly (including the version suffix, e.g. `-v2:0`).
- Confirm the model is available in your selected region.

### "botocore.exceptions.NoCredentialsError: Unable to locate credentials"

- Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, or attach an IAM role to your compute environment.
- If using `~/.aws/credentials`, check `AWS_PROFILE` or the `[default]` profile is configured.

### "An error occurred (ThrottlingException)"

- You have exceeded the Bedrock API rate limit. Consider adding retry logic or reducing review frequency.
- Check your [Bedrock service quotas](https://console.aws.amazon.com/servicequotas/home/services/bedrock/quotas) and request an increase if needed.

### Reviewing large PRs is slow

- Bedrock Claude models have a maximum input context window. Very large diffs may be truncated or cause errors.
- Consider filtering to UiPath-specific files only (the default behaviour) to reduce the amount of text sent.
