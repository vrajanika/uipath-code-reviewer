# Configuration Guide

This guide provides detailed instructions for configuring the UiPath Code Reviewer Bot.

## Table of Contents

- [Azure OpenAI Setup](#azure-openai-setup)
- [GitHub Setup](#github-setup)
- [Environment Variables](#environment-variables)
- [GitHub Actions Configuration](#github-actions-configuration)
- [Advanced Configuration](#advanced-configuration)

## Azure OpenAI Setup

### 1. Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new Azure OpenAI resource
3. Note your endpoint URL (e.g., `https://your-resource-name.openai.azure.com/`)
4. Get your API key from the resource's "Keys and Endpoint" section

### 2. Deploy a Model

1. In your Azure OpenAI resource, go to "Model deployments"
2. Deploy a model (recommended: GPT-4 or GPT-3.5-turbo)
3. Note your deployment name

### 3. Configure API Version

The bot uses API version `2024-02-15-preview` by default. You can change this in your configuration if needed.

**Note:** Check the [Azure OpenAI API versioning documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/api-version-deprecation) for the latest stable or preview API versions. Using a newer version may provide access to additional features or improvements.

## GitHub Setup

### Option 1: Personal Access Token (Simpler)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with these scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
3. Copy the token (you won't see it again!)

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
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# GitHub Configuration
GITHUB_TOKEN=your-github-token-here
```

### Optional Variables

```env
# API version (default: 2024-02-15-preview)
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore` by default
2. **Use different tokens for different environments** - Development vs Production
3. **Rotate tokens regularly** - Change them every 90 days
4. **Use minimal permissions** - Only grant what's needed
5. **Monitor usage** - Check Azure OpenAI usage for unexpected activity

## GitHub Actions Configuration

### Setting Up Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each of these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | `https://my-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Your model deployment name | `gpt-4` |
| `AZURE_OPENAI_API_VERSION` | API version (optional) | `2024-02-15-preview` |

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

To customize review prompts, edit `bot/azure_openai_client.py`:

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

Adjust AI behavior in `bot/azure_openai_client.py`:

```python
response = self.client.chat.completions.create(
    model=self.deployment_name,
    messages=[...],
    temperature=0.3,  # Lower = more focused, Higher = more creative
    max_tokens=2000,  # Adjust response length
)
```

## Troubleshooting

### Issue: "Authentication failed"

**Solution:**
- Verify your API key is correct
- Check if the key has expired
- Ensure the endpoint URL is correct

### Issue: "Model not found"

**Solution:**
- Verify the deployment name matches exactly
- Check if the deployment is active in Azure portal
- Ensure you have access to the deployment

### Issue: "Rate limit exceeded"

**Solution:**
- Check your Azure OpenAI quota
- Add rate limiting in the code
- Review fewer files at once

### Issue: Bot doesn't comment on PRs

**Solution:**
- Check GitHub token permissions
- Verify the workflow is enabled
- Check workflow run logs in GitHub Actions
- Ensure secrets are set correctly

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
4. For fork PRs, consider using `pull_request_target` event with caution (security implications)

## Testing Configuration

### Local Testing

```bash
# Set environment variables
export AZURE_OPENAI_ENDPOINT="https://..."
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_DEPLOYMENT_NAME="..."
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
2. **Monitor costs** - Azure OpenAI charges per token
3. **Review the reviews** - AI isn't perfect, verify suggestions
4. **Iterate on prompts** - Improve prompts based on review quality
5. **Set expectations** - Let your team know this is a tool, not a replacement for human review
