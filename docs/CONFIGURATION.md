# Configuration Guide

This guide provides detailed instructions for configuring the UiPath Code Reviewer Bot.

## Table of Contents

- [AWS Bedrock Setup](#aws-bedrock-setup)
- [GitHub Setup](#github-setup)
- [Environment Variables](#environment-variables)
- [GitHub Actions Configuration](#github-actions-configuration)
- [Advanced Configuration](#advanced-configuration)

## AWS Bedrock Setup

For a full step-by-step guide on setting up AWS Bedrock with Claude, see **[BEDROCK_SETUP.md](BEDROCK_SETUP.md)**.

### Quick Summary

1. **Create an IAM user or role** in the [AWS IAM Console](https://console.aws.amazon.com/iam/) with the `bedrock:Converse` permission.
2. **Enable model access** for the desired Claude model in the [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/) → **Model access**.
3. **Generate an access key** for local use (not needed when using IAM roles on AWS compute or GitHub Actions OIDC).
4. **Choose a model ID** — recommended: `anthropic.claude-3-5-sonnet-20241022-v2:0`.

### Supported Regions

Bedrock Claude models are available in `us-east-1`, `us-west-2`, `eu-west-1`, `eu-central-1`, and more. See [BEDROCK_SETUP.md#supported-aws-regions](BEDROCK_SETUP.md#supported-aws-regions).

## GitHub Setup

**📚 For detailed token setup instructions, see [TOKEN_SETUP.md](TOKEN_SETUP.md)**

### Option 1: Personal Access Token (Simpler)

**Quick Steps:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with these scopes:
   - `repo` (Full control of private repositories) - **Required for private repos**
   - OR `public_repo` (Access public repositories) - **For public repos only**
3. Copy the token (you won't see it again!)

**Required Permissions:**
- ✅ Read repository contents
- ✅ Write to pull requests
- ✅ Write to issues

**See [TOKEN_SETUP.md](TOKEN_SETUP.md) for detailed step-by-step instructions with troubleshooting.**

### Option 2: GitHub App (More Secure)

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Create a new GitHub App with these permissions:
   - Repository permissions:
     - Contents: Read
     - Issues: Read & Write
     - Pull requests: Read & Write
   - Subscribe to these events:
     - Pull request
     - Issue comment
3. Install the app on your repository
4. Generate a private key and use it to generate installation access tokens

## Environment Variables

### Required Variables

Create a `.env` file in the project root:

```env
# AWS Bedrock Configuration
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# GitHub Configuration
GITHUB_TOKEN=your-github-token-here
```

### Optional Variables

```env
# AWS credentials — not required when using IAM roles / instance profiles
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key

# For temporary STS credentials only
AWS_SESSION_TOKEN=your-session-token
```

### Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore` by default
2. **Use different credentials for different environments** - Development vs Production
3. **Rotate access keys regularly** - Change them every 90 days
4. **Prefer IAM roles over access keys** - Use instance profiles or GitHub OIDC where possible
5. **Use minimal permissions** - Only grant `bedrock:Converse` on Claude model ARNs
6. **Monitor usage** - Check AWS CloudWatch for unexpected Bedrock API activity

## GitHub Actions Configuration

### Setting Up Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each of these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `AWS_REGION` | AWS region with Bedrock enabled | `us-east-1` |
| `BEDROCK_MODEL_ID` | Claude model ID | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `AWS_ACCESS_KEY_ID` | IAM access key ID (skip if using OIDC) | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | IAM secret access key (skip if using OIDC) | `wJalrXUtn...` |

**Note:** `GITHUB_TOKEN` is automatically provided by GitHub Actions and doesn't need to be added.

### Workflow Triggers

The default workflow triggers on:

1. **Pull request events**: `opened`, `synchronize`, `reopened`
2. **Issue comments**: When someone mentions `@uipath-reviewer`

You can customize these in `.github/workflows/code-review.yml`.

### Customizing the Workflow

Edit `.github/workflows/code-review.yml` to customize:

```yaml
# Change Python version
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Change this

# Add custom flags
- name: Run code review
  run: |
    python -m bot.main \
      --repo "${{ github.repository }}" \
      --pr-number "${{ github.event.pull_request.number }}" \
      --all-files  # Add this to review all files
```

## Advanced Configuration

### Custom Review Prompts

To customize review prompts, edit `bot/bedrock_client.py`:

```python
def _build_system_prompt(self, file_type: str) -> str:
    # Add your custom instructions here
    base_prompt = """Your custom instructions..."""
    # ...
```

### Custom File Filtering

To change which files are reviewed, edit `bot/reviewer.py`:

```python
def _filter_uipath_files(self, files: List[Dict]) -> List[Dict]:
    # Add your custom file extensions
    uipath_extensions = ['.xaml', '.json', '.config', '.custom']
    # ...
```

### Temperature and Token Limits

Adjust AI behavior in `bot/bedrock_client.py`:

```python
response = self.client.converse(
    modelId=self.model_id,
    system=[{"text": system_prompt}],
    messages=[...],
    inferenceConfig={
        "temperature": 0.3,   # Lower = more focused, Higher = more creative
        "maxTokens": 2000,    # Adjust response length
    },
)
```

## Troubleshooting

### Issue: "Authentication failed" / "NoCredentialsError"

**Solution:**
- Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, or attach an IAM role to your compute environment
- If using `~/.aws/credentials`, check that `AWS_PROFILE` or the `[default]` profile is configured

### Issue: "AccessDeniedException"

**Solution:**
- Verify the IAM user/role has `bedrock:Converse` permission
- Enable model access for the chosen Claude model in the Bedrock console
- See [BEDROCK_SETUP.md](BEDROCK_SETUP.md) for the full setup walkthrough

### Issue: "ValidationException: The provided model identifier is invalid"

**Solution:**
- Verify `BEDROCK_MODEL_ID` matches exactly (including version suffix, e.g. `-v2:0`)
- Check that the model is available in your selected `AWS_REGION`

### Issue: "ThrottlingException"

**Solution:**
- Check your [Bedrock service quotas](https://console.aws.amazon.com/servicequotas/home/services/bedrock/quotas)
- Add rate limiting in the code or reduce the frequency of reviews

### Issue: Bot doesn't comment on PRs

**Solution:**
- Check GitHub token permissions - see [TOKEN_SETUP.md](TOKEN_SETUP.md) for detailed guidance
- Verify the workflow is enabled
- Check workflow run logs in GitHub Actions
- Ensure secrets are set correctly

### Issue: GitHub Token Permission Issues

**Symptoms:**
- "GitHub access token is required"
- "404 Not Found" 
- "403 Forbidden"
- "Resource not accessible by integration"
- "Bad credentials"

**Solution:**
📚 **See [TOKEN_SETUP.md](TOKEN_SETUP.md) for comprehensive token troubleshooting**, including:
- How to create a token with correct permissions
- How to verify token scopes
- Repository settings that may block the bot
- Differences between local and GitHub Actions tokens

**Quick fixes:**
1. **For local testing:** Ensure your token has `repo` scope (Settings → Developer settings → Personal access tokens)
2. **For GitHub Actions:** Verify workflow permissions are set (already configured in default workflow)
3. **Repository settings:** Check Settings → Actions → General → Workflow permissions

### Issue: "Resource not accessible by integration" (403 error)

**Solution:**
This error occurs when the GitHub token doesn't have sufficient permissions to post comments. The bot has been updated to handle this gracefully by:
- Using issue comments (which require fewer permissions) as the primary method
- Falling back to review comments if needed
- Working reliably with the default `GITHUB_TOKEN` in GitHub Actions

If you still encounter this error:
1. Verify the workflow has the correct permissions:
   ```yaml
   permissions:
     contents: read
     pull-requests: write
     issues: write
   ```
2. Ensure the bot is not being run on a fork PR with restrictive settings
3. Check that Actions are enabled for the repository
4. For fork PRs, consider using `pull_request_target` event with caution
   
   **⚠️ Security Warning**: `pull_request_target` runs with write permissions and uses the workflow from the base branch, which can be risky if not properly secured. Only use this if you trust the PR authors or implement proper security measures. See [GitHub's documentation on pull_request_target](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request_target) for details.

## Testing Configuration

### Local Testing

```bash
# Set environment variables
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="anthropic.claude-3-5-sonnet-20241022-v2:0"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export GITHUB_TOKEN="..."

# Test with a PR
python -m bot.main --repo owner/repo --pr-number 1 --no-post
```

### Dry Run

Use `--no-post` flag to test without posting comments:

```bash
python -m bot.main --repo owner/repo --pr-number 1 --no-post
```

## Best Practices

1. **Start with small PRs** - Test on smaller PRs first
2. **Monitor costs** - AWS Bedrock charges per input/output token
3. **Review the reviews** - AI isn't perfect, verify suggestions
4. **Iterate on prompts** - Improve prompts based on review quality
5. **Set expectations** - Let your team know this is a tool, not a replacement for human review
6. **Use IAM roles** - Prefer roles over long-lived access keys for production deployments
