# Quick Start Guide

Get the UiPath Code Reviewer Bot up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- AWS account with Bedrock access and Claude model access enabled
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
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
GITHUB_TOKEN=your-github-token-here
```

**Where to get these values:**
- AWS Region & credentials: [AWS IAM Console](https://console.aws.amazon.com/iam/) — create an IAM user with `bedrock:Converse` permission
- Bedrock Model ID: pick one from [docs/BEDROCK_SETUP.md](docs/BEDROCK_SETUP.md#step-4-choose-a-claude-model-id)
- **GitHub Token**: See [docs/TOKEN_SETUP.md](docs/TOKEN_SETUP.md) for detailed instructions
  - Quick: GitHub Settings → Developer settings → Personal access tokens → Generate with `repo` scope

**📚 Full Bedrock setup:** [docs/BEDROCK_SETUP.md](docs/BEDROCK_SETUP.md)

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
   - `AWS_REGION`
   - `BEDROCK_MODEL_ID`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

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

*Review powered by Claude on AWS Bedrock*
```

## Troubleshooting

**Bot doesn't comment?**
- Check GitHub token has `repo` permission
- Verify secrets are set correctly in GitHub Actions
- Check workflow logs in Actions tab

**"Missing required environment variables"?**
- Ensure `AWS_REGION`, `BEDROCK_MODEL_ID`, and `GITHUB_TOKEN` are set in `.env`
- No quotes needed around values in `.env`

**"AccessDeniedException" from AWS?**
- Verify IAM user has `bedrock:Converse` permission
- Enable model access in the Bedrock console for your region
- See [docs/BEDROCK_SETUP.md](docs/BEDROCK_SETUP.md) for full setup guide

**"ThrottlingException"?**
- Check Bedrock service quotas
- Add delays between reviews or review fewer files

## Next Steps

- Read the full [README.md](README.md) for detailed features
- Check [docs/BEDROCK_SETUP.md](docs/BEDROCK_SETUP.md) for Bedrock setup
- Check [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for advanced setup
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Review [examples.py](examples.py) for programmatic usage

## Support

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/kangtamo/uipath-code-reviewer/issues)
- 💡 [Request Features](https://github.com/kangtamo/uipath-code-reviewer/issues)

Happy reviewing! 🎉
