# Quick Start Guide

Get the UiPath Code Reviewer Bot up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Azure OpenAI service with a deployed model
- GitHub account with repository access

## Step 1: Clone and Install (2 minutes)

```bash
git clone https://github.com/kangtamo/uipath-code-reviewer.git
cd uipath-code-reviewer
pip install -r requirements.txt
```

## Step 2: Configure Environment (2 minutes)

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
GITHUB_TOKEN=your-github-token-here
```

**Where to get these values:**
- Azure OpenAI Endpoint: Azure Portal → Your OpenAI Resource → Keys and Endpoint
- API Key: Same location as endpoint
- Deployment Name: Azure Portal → Your OpenAI Resource → Model deployments
- GitHub Token: GitHub Settings → Developer settings → Personal access tokens

## Step 3: Test Locally (1 minute)

Test the bot without posting comments:
```bash
python -m bot.main --repo owner/repo --pr-number 123 --no-post
```

## Step 4: Set Up GitHub Actions (Optional)

If you want automatic reviews on all PRs:

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add these secrets:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`

That's it! The bot will now automatically review PRs when they're opened.

## Common Commands

```bash
# Review a PR and post comments
python -m bot.main --repo owner/repo --pr-number 42

# Review without posting (dry run)
python -m bot.main --repo owner/repo --pr-number 42 --no-post

# Review all files, not just UiPath files
python -m bot.main --repo owner/repo --pr-number 42 --all-files

# Get help
python -m bot.main --help

# Run tests
pytest tests/
```

## What Files Does It Review?

By default, the bot focuses on UiPath files:
- `.xaml` - UiPath workflows
- `.json` - Configuration files
- `.config` - UiPath configs

Use `--all-files` to review everything.

## Example Output

The bot will post a comment like this:

```
## 🤖 UiPath Code Review

Reviewed 3 file(s) in this pull request.

### 📄 `Main.xaml`
*Changes: +15 -3*

The workflow shows good structure with proper error handling. Here are some suggestions:

1. Consider adding more specific exception handling instead of generic Exception catch
2. The selector for the login button could be more robust
3. Add logging before the critical transaction processing step

---

*Review powered by Azure OpenAI*
```

## Troubleshooting

**Bot doesn't comment?**
- Check GitHub token has `repo` permission
- Verify secrets are set correctly in GitHub Actions
- Check workflow logs in Actions tab

**"Missing required environment variables"?**
- Ensure all variables in `.env` are set
- No quotes needed around values in `.env`

**"Rate limit exceeded"?**
- Check Azure OpenAI quota
- Add delays between reviews
- Consider using a higher-tier Azure plan

## Next Steps

- Read the full [README.md](README.md) for detailed features
- Check [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for advanced setup
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Review [examples.py](examples.py) for programmatic usage

## Support

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/kangtamo/uipath-code-reviewer/issues)
- 💡 [Request Features](https://github.com/kangtamo/uipath-code-reviewer/issues)

Happy reviewing! 🎉
