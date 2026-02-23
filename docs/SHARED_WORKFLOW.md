# Using UiPath Code Reviewer as a Shared Workflow

This guide explains how to use the UiPath Code Reviewer Bot as a reusable workflow in your own repositories.

## What is a Shared Workflow?

A shared workflow (also called a reusable workflow) allows you to use the UiPath Code Reviewer Bot from your own repositories without copying any code. When you create a pull request in your repository, it will automatically trigger the code review workflow hosted in the `kangtamo/uipath-code-reviewer` repository.

## Benefits

✅ **No Code Duplication**: No need to copy the bot code to your repository  
✅ **Automatic Updates**: Get improvements and bug fixes automatically  
✅ **Simple Setup**: Just add a workflow file and configure secrets  
✅ **Consistent Reviews**: Same review quality across all your repositories  

## Prerequisites

- Azure OpenAI service with a deployed model
- GitHub repository where you want to enable code reviews
- Required secrets configured in your repository

## Setup Instructions

### Step 1: Configure Secrets

In your repository, go to **Settings → Secrets and variables → Actions** and add the following secrets:

1. `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
2. `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
3. `AZURE_OPENAI_DEPLOYMENT_NAME` - Your deployment/model name (e.g., `gpt-4`)
4. `AZURE_OPENAI_API_VERSION` - API version (e.g., `2024-02-15-preview`) - Optional, defaults to `2024-02-15-preview`

**Note**: The `GITHUB_TOKEN` secret is automatically provided by GitHub Actions, so you don't need to create it manually.

### Step 2: Create Workflow File

Create a new file in your repository at `.github/workflows/uipath-code-review.yml` with the following content:

```yaml
name: UiPath Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  code-review:
    uses: kangtamo/uipath-code-reviewer/.github/workflows/code-review.yml@main
    with:
      repository: ${{ github.repository }}
      pr-number: ${{ github.event.pull_request.number }}
      all-files: false  # Set to true to review all files
    secrets:
      AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
      AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
      AZURE_OPENAI_DEPLOYMENT_NAME: ${{ secrets.AZURE_OPENAI_DEPLOYMENT_NAME }}
      AZURE_OPENAI_API_VERSION: ${{ secrets.AZURE_OPENAI_API_VERSION }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 3: Enable GitHub Actions

1. Go to your repository's **Settings → Actions → General**
2. Under **Workflow permissions**, ensure **Read and write permissions** is selected
3. Check the box for **Allow GitHub Actions to create and approve pull requests**

### Step 4: Test the Setup

1. Create a new branch in your repository
2. Make some changes to UiPath files (`.xaml`, `.json`, `.config`) or any code files if `all-files: true`
3. Open a pull request
4. The UiPath Code Review Bot will automatically run and post a review comment

## Configuration Options

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `repository` | Yes | - | Repository name in `owner/repo` format |
| `pr-number` | Yes | - | Pull request number to review |
| `all-files` | No | `false` | Review all files instead of just UiPath files |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Yes | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Yes | Azure OpenAI deployment/model name |
| `AZURE_OPENAI_API_VERSION` | No | Azure OpenAI API version (defaults to `2024-02-15-preview`) |
| `GH_TOKEN` | Yes | GitHub token for API access (use `${{ secrets.GITHUB_TOKEN }}`) |

## Advanced Usage

### Review All Files (Not Just UiPath Files)

By default, the bot only reviews UiPath-related files (`.xaml`, `.json`, `.config`). To review all files in your pull requests:

```yaml
with:
  repository: ${{ github.repository }}
  pr-number: ${{ github.event.pull_request.number }}
  all-files: true  # Enable review of all file types
```

### Use a Specific Version

Instead of using `@main`, you can pin to a specific version or tag:

```yaml
uses: kangtamo/uipath-code-reviewer/.github/workflows/code-review.yml@v1.0.0
```

### Trigger on Specific Branches

To only run reviews on pull requests targeting specific branches:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - develop
```

### Multiple Triggers

You can add multiple trigger conditions:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
  # Manual trigger
  workflow_dispatch:
    inputs:
      pr-number:
        description: 'PR number to review'
        required: true
        type: number
```

## Troubleshooting

### "Workflow does not exist" Error

**Solution**: Make sure you're using the correct repository name (`kangtamo/uipath-code-reviewer`) and the workflow exists in the `main` branch.

### "Secret not found" Error

**Solution**: Verify that all required secrets are configured in your repository's Settings → Secrets and variables → Actions.

### Review Comments Not Posted

**Solution**:
1. Check that your repository's workflow permissions are set to "Read and write permissions"
2. Verify the `GH_TOKEN` is correctly passed as `${{ secrets.GITHUB_TOKEN }}`
3. Check the workflow logs in the Actions tab for detailed error messages

### Azure OpenAI Rate Limits

**Solution**: If you hit rate limits, you may need to:
- Upgrade your Azure OpenAI tier
- Add delays between reviews
- Reduce the frequency of reviews

## Example Repositories

See the example workflow file at `.github/workflows/example-usage.yml` in this repository for a complete working example.

## Support

- 📖 [Main Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/kangtamo/uipath-code-reviewer/issues)
- 💡 [Request Features](https://github.com/kangtamo/uipath-code-reviewer/issues)

## Security Considerations

- Keep your Azure OpenAI API key secure and never commit it to code
- Use GitHub Secrets for all sensitive configuration
- Review the permissions granted to GitHub Actions in your repository settings
- The shared workflow only reads PR data and posts comments; it does not modify code

## Additional Resources

- [GitHub Reusable Workflows Documentation](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
