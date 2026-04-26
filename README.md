# UiPath Code Reviewer Bot 🤖

A GitHub bot that uses Claude on AWS Bedrock to automatically review code changes in pull requests, with a focus on UiPath automation projects.

## 🚀 Quick Start

New here? Check out the [Quick Start Guide](QUICKSTART.md) to get up and running in 5 minutes!

**Having token permission issues?** See [TOKEN_HELP.md](TOKEN_HELP.md) for quick fixes!

## Features

- 🔍 **Automated Code Review**: Automatically reviews pull requests using Claude on AWS Bedrock
- 🎯 **UiPath-Focused**: Specialized prompts for reviewing UiPath XAML workflows and configurations
- 💬 **GitHub Integration**: Posts review comments directly to your pull requests
- 🔐 **Secure**: Uses AWS Bedrock with your own AWS account — no third-party proxy
- ⚙️ **Customizable**: Configurable to review all files or focus on UiPath-specific files

## Architecture

The bot consists of three main components:

1. **Bedrock Client** (`bot/bedrock_client.py`): Handles communication with Claude via AWS Bedrock
2. **GitHub Client** (`bot/github_client.py`): Manages GitHub API interactions
3. **Code Reviewer** (`bot/reviewer.py`): Orchestrates the review process

## Prerequisites

- Python 3.8 or higher
- AWS account with Bedrock access and Claude model access enabled
- GitHub repository with Actions enabled
- GitHub Personal Access Token or GitHub App

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kangtamo/uipath-code-reviewer.git
cd uipath-code-reviewer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your AWS Bedrock and GitHub credentials:

```env
# AWS Bedrock Configuration
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# AWS Credentials (not needed when using IAM roles / instance profiles)
AWS_ACCESS_KEY_ID=your-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-secret-access-key-here

# GitHub Configuration
GITHUB_TOKEN=your-github-token-here
```

**📚 For detailed Bedrock setup instructions, see [docs/BEDROCK_SETUP.md](docs/BEDROCK_SETUP.md)**

**📚 For detailed instructions on creating a GitHub token with the correct permissions, see [docs/TOKEN_SETUP.md](docs/TOKEN_SETUP.md)**

### 4. Set Up GitHub Secrets

For GitHub Actions to work, configure the following secrets in your repository:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `AWS_REGION`: AWS region where Bedrock is enabled (e.g. `us-east-1`)
   - `BEDROCK_MODEL_ID`: Claude model ID (e.g. `anthropic.claude-3-5-sonnet-20241022-v2:0`)
   - `AWS_ACCESS_KEY_ID`: Your AWS access key ID
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
   - `GITHUB_TOKEN`: Automatically provided by GitHub Actions

## Usage

### Automatic Review via GitHub Actions

The bot automatically reviews pull requests when:
1. A new pull request is opened
2. New commits are pushed to an existing pull request
3. Someone mentions `@uipath-reviewer` in a PR comment

The workflow file is located at `.github/workflows/code-review.yml`.

### Manual Review via CLI

You can also run the bot manually from the command line:

```bash
python -m bot.main --repo owner/repo --pr-number 123
```

**Options:**
- `--repo`: Repository full name (required)
- `--pr-number`: Pull request number (required)
- `--no-post`: Don't post comments to GitHub (just generate review)
- `--all-files`: Review all files, not just UiPath files
- `--output`: Output file for review results (default: `review_result.txt`)

**Examples:**

```bash
# Review a PR and post comments
python -m bot.main --repo kangtamo/my-uipath-project --pr-number 42

# Review without posting (dry run)
python -m bot.main --repo kangtamo/my-uipath-project --pr-number 42 --no-post

# Review all files, not just UiPath files
python -m bot.main --repo kangtamo/my-uipath-project --pr-number 42 --all-files
```

## Review Focus Areas

### For UiPath XAML Workflows

The bot provides specialized reviews for UiPath workflows, focusing on:
- Proper error handling and retry logic
- Efficient selector usage and reliability
- Variable scope and naming conventions
- Workflow structure and modularity
- Best practices for UI automation
- Proper use of Try-Catch blocks
- Appropriate use of delays and timeouts
- Data type handling and conversions

### For UiPath Configuration Files

When reviewing JSON configuration files, the bot focuses on:
- Proper configuration structure
- Secure handling of credentials and sensitive data
- Environment-specific settings
- Validation of configuration values

### For Other Code Files

The bot also provides general code review for Python, C#, and VB.NET files commonly used in UiPath projects.

## File Type Support

The bot automatically identifies and appropriately reviews:
- `.xaml` - UiPath workflow files
- `.json` - Configuration files
- `.config` - UiPath configuration files
- `.py` - Python scripts
- `.cs` - C# code
- `.vb` - VB.NET code

## Development

### Project Structure

```
uipath-code-reviewer/
├── bot/
│   ├── __init__.py
│   ├── bedrock_client.py    # AWS Bedrock / Claude integration
│   ├── github_client.py     # GitHub API integration
│   ├── reviewer.py          # Main review orchestrator
│   └── main.py              # CLI entry point
├── tests/                   # Unit tests
├── docs/
│   ├── BEDROCK_SETUP.md     # AWS Bedrock setup guide
│   ├── CONFIGURATION.md     # Full configuration reference
│   └── TOKEN_SETUP.md       # GitHub token setup guide
├── .github/
│   └── workflows/
│       └── code-review.yml  # GitHub Actions workflow
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── .env.example             # Environment variables template
└── README.md                # This file
```

### Running Tests

```bash
pytest tests/
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Common Issues

**Issue: "Missing required environment variables"**
- Solution: Make sure `AWS_REGION`, `BEDROCK_MODEL_ID`, and `GITHUB_TOKEN` are set in your `.env` file or GitHub Secrets

**Issue: "Failed to post review comment"** or **"403 Forbidden"** or **"Resource not accessible"**
- **Solution:** This is a token permission issue. The bot uses issue comments by default for better compatibility.
  1. **For local testing:** Your GitHub token needs `repo` scope (or `public_repo` for public repos). See [docs/TOKEN_SETUP.md](docs/TOKEN_SETUP.md) for step-by-step token creation.
  2. **For GitHub Actions:** Ensure your workflow has the correct permissions (already set in the default workflow):
     ```yaml
     permissions:
       contents: read
       pull-requests: write
       issues: write
     ```
  3. **Repository settings:** Check Settings → Actions → General → Workflow permissions is set to "Read and write permissions"
  
  📚 **Full troubleshooting guide:** [docs/TOKEN_SETUP.md#troubleshooting](docs/TOKEN_SETUP.md#troubleshooting)

**Issue: "AccessDeniedException" from Bedrock**
- Solution: Ensure your IAM user/role has `bedrock:Converse` permission and that you have enabled model access for the chosen Claude model in the Bedrock console. See [docs/BEDROCK_SETUP.md](docs/BEDROCK_SETUP.md).

**Issue: "ThrottlingException" from Bedrock**
- Solution: You have exceeded Bedrock's rate limits. Consider adding retry logic or reviewing fewer files at once. Check your service quotas in the AWS console.

**Issue: Bot doesn't trigger on PR**
- Solution: Ensure GitHub Actions is enabled in your repository and the workflow file is in the correct location

## Security Considerations

- Never commit your `.env` file or expose your AWS credentials
- Use GitHub Secrets for sensitive configuration in Actions
- Prefer IAM roles over long-lived access keys wherever possible
- The bot only reads PR data and posts comments; it doesn't modify code
- Review the permissions granted to the GitHub token

## License

This project is licensed under the MIT License.

## Acknowledgments

- Powered by [Claude on AWS Bedrock](https://aws.amazon.com/bedrock/claude/)
- Built for [UiPath](https://www.uipath.com/) automation projects
- Uses [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration