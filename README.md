# UiPath Code Reviewer Bot 🤖

A GitHub bot that uses Azure OpenAI to automatically review code changes in pull requests, with a focus on UiPath automation projects.

## 🚀 Quick Start

New here? Check out the [Quick Start Guide](QUICKSTART.md) to get up and running in 5 minutes!

## Features

- 🔍 **Automated Code Review**: Automatically reviews pull requests using Azure OpenAI
- 🎯 **UiPath-Focused**: Specialized prompts for reviewing UiPath XAML workflows and configurations
- 💬 **GitHub Integration**: Posts review comments directly to your pull requests
- 🔐 **Secure**: Uses Azure OpenAI service with your own LLM deployment
- ⚙️ **Customizable**: Configurable to review all files or focus on UiPath-specific files

## Architecture

The bot consists of three main components:

1. **Azure OpenAI Client** (`bot/azure_openai_client.py`): Handles communication with Azure OpenAI service
2. **GitHub Client** (`bot/github_client.py`): Manages GitHub API interactions
3. **Code Reviewer** (`bot/reviewer.py`): Orchestrates the review process

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI service deployment
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

Edit `.env` with your Azure OpenAI and GitHub credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# GitHub Configuration
GITHUB_TOKEN=your-github-token-here
```

### 4. Set Up GitHub Secrets

For GitHub Actions to work, configure the following secrets in your repository:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment/model name
   - `AZURE_OPENAI_API_VERSION`: API version (e.g., `2024-02-15-preview`)
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
│   ├── azure_openai_client.py  # Azure OpenAI integration
│   ├── github_client.py         # GitHub API integration
│   ├── reviewer.py              # Main review orchestrator
│   └── main.py                  # CLI entry point
├── tests/                       # Unit tests
├── .github/
│   └── workflows/
│       └── code-review.yml      # GitHub Actions workflow
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── .env.example                 # Environment variables template
└── README.md                    # This file
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
- Solution: Make sure all required environment variables are set in your `.env` file or GitHub Secrets

**Issue: "Failed to post review comment"**
- Solution: Check that your GitHub token has the necessary permissions (`repo` scope for private repos, `public_repo` for public repos)

**Issue: "Error during code review: Rate limit exceeded"**
- Solution: Azure OpenAI has rate limits. Consider adding retry logic or reducing the frequency of reviews

**Issue: Bot doesn't trigger on PR**
- Solution: Ensure GitHub Actions is enabled in your repository and the workflow file is in the correct location

## Security Considerations

- Never commit your `.env` file or expose your API keys
- Use GitHub Secrets for sensitive configuration in Actions
- The bot only reads PR data and posts comments; it doesn't modify code
- Review the permissions granted to the GitHub token

## License

This project is licensed under the MIT License.

## Acknowledgments

- Powered by [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- Built for [UiPath](https://www.uipath.com/) automation projects
- Uses [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration