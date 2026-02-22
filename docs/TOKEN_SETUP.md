# GitHub Token Setup Guide

This guide explains how to create and configure a GitHub token with the correct permissions for the UiPath Code Reviewer Bot.

## Table of Contents

- [Understanding Token Types](#understanding-token-types)
- [Required Permissions](#required-permissions)
- [Creating a Personal Access Token](#creating-a-personal-access-token)
- [For GitHub Actions](#for-github-actions)
- [For Local Testing](#for-local-testing)
- [Verifying Token Permissions](#verifying-token-permissions)
- [Troubleshooting](#troubleshooting)

## Understanding Token Types

There are two scenarios for using the bot:

### 1. **GitHub Actions** (Automatic Reviews)
- Uses the built-in `GITHUB_TOKEN` provided by GitHub Actions
- No manual token creation needed
- Permissions are set in the workflow file
- **Recommended for most users**

### 2. **Local Testing** (Manual Reviews)
- Requires a Personal Access Token (PAT)
- Must be created manually
- Used for testing locally before deploying

## Required Permissions

The bot needs the following permissions to function:

| Permission | Scope | Why Needed |
|------------|-------|------------|
| **Repository Contents** | `contents: read` | To read file changes in PRs |
| **Pull Requests** | `pull-requests: write` | To post review comments on PRs |
| **Issues** | `issues: write` | To post comments (PRs are issues in GitHub API) |

### For Personal Access Tokens (Local Testing)

When creating a PAT, you need these scopes:
- ✅ `repo` - Full control of private repositories (includes all the above)
  - OR for public repos only: `public_repo`

## Creating a Personal Access Token

### Step-by-Step Instructions

#### 1. Navigate to Token Settings

Go to: **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**

Or use this direct link: https://github.com/settings/tokens

#### 2. Click "Generate new token" → "Generate new token (classic)"

#### 3. Configure the Token

**Note/Description:** Give it a descriptive name, e.g., "UiPath Code Reviewer - Local Testing"

**Expiration:** Choose an appropriate expiration (e.g., 90 days). You'll need to regenerate when it expires.

**Select scopes:**

For **private repositories**, select:
```
✅ repo (Full control of private repositories)
   ✅ repo:status
   ✅ repo_deployment
   ✅ public_repo
   ✅ repo:invite
   ✅ security_events
```

For **public repositories only**, you can select just:
```
✅ public_repo (Access public repositories)
```

#### 4. Generate and Copy the Token

1. Click **"Generate token"** at the bottom
2. **IMPORTANT:** Copy the token immediately - you won't be able to see it again!
3. Store it securely (e.g., in a password manager)

#### 5. Configure the Token

Add the token to your `.env` file:

```bash
# In /path/to/uipath-code-reviewer/.env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Security Note:** Never commit the `.env` file to git! It's already in `.gitignore`.

## For GitHub Actions

### Using the Built-in GITHUB_TOKEN

The workflow already uses the built-in `GITHUB_TOKEN`:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

**No manual token creation needed!** GitHub Actions automatically provides a token with these permissions.

### What You Need to Do

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add **ONLY** these secrets (NOT `GITHUB_TOKEN`):
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`

**Do NOT add `GITHUB_TOKEN` as a secret** - it's provided automatically!

### Workflow Permissions

The permissions are already set in `.github/workflows/code-review.yml`:

```yaml
permissions:
  contents: read        # Read repository files
  pull-requests: write  # Post PR comments
  issues: write         # Post issue comments
```

If you modify the workflow, ensure these permissions remain set.

## For Local Testing

### Quick Setup

1. Create a Personal Access Token (see above)
2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your token:
   ```bash
   GITHUB_TOKEN=ghp_your_token_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
   ```
4. Test it:
   ```bash
   python -m bot.main --repo owner/repo --pr-number 123 --no-post
   ```

### Environment Variable

You can also set the token as an environment variable:

```bash
export GITHUB_TOKEN=ghp_your_token_here
python -m bot.main --repo owner/repo --pr-number 123 --no-post
```

## Verifying Token Permissions

### Method 1: Use the Verification Script (Recommended)

We provide a script that checks your token automatically:

```bash
python verify_token.py
```

**Example output:**
```
============================================================
GitHub Token Verification for UiPath Code Reviewer Bot
============================================================

✅ GITHUB_TOKEN found in environment
   Token starts with: ghp_xxx...

✅ Authentication successful
   Logged in as: your-username
   User type: User

✅ Token scopes found:
   - repo
   - user

✅ Has 'repo' scope - can access private repositories

============================================================
Summary
============================================================
✅ Your token appears to be configured correctly!
```

**To test with a specific repository:**
```bash
python verify_token.py owner/repo
```

This will also verify that you can access the repository and have write permissions.

### Method 2: Test with --no-post

Run the bot without posting to verify it can read PR data:

```bash
python -m bot.main --repo owner/repo --pr-number 123 --no-post
```

**Expected output:**
```
Reviewing PR #123 in owner/repo...
Review status: success
Message: Review completed
Review saved to review_result.txt
```

**If you see errors:**
- "GitHub access token is required" → Token not set
- "404 Not Found" → Token doesn't have `repo` access
- "403 Forbidden" → Token doesn't have required permissions

### Method 3: Check Token Scopes via API

You can verify your token's scopes:

```bash
curl -H "Authorization: token ghp_your_token_here" \
     https://api.github.com/user \
     -I | grep x-oauth-scopes
```

**Expected output:**
```
x-oauth-scopes: repo, user
```

### Method 4: Try Posting a Test Comment

Test if the token can post comments:

```bash
python -m bot.main --repo owner/repo --pr-number 123
```

**Success:** You'll see "Review completed and posted"

**Failure:** You'll see an error explaining what permission is missing

## Troubleshooting

### "GitHub access token is required"

**Problem:** The token is not set in the environment.

**Solution:**
1. Check your `.env` file exists and contains `GITHUB_TOKEN=...`
2. Or set it as an environment variable: `export GITHUB_TOKEN=...`
3. Verify the file is in the correct directory

### "404 Not Found"

**Problem:** Token doesn't have access to the repository.

**Solution:**
1. For private repos, ensure you selected the `repo` scope
2. Verify the repository name is correct
3. Check that your GitHub account has access to the repository

### "403 Forbidden" or "Resource not accessible by integration"

**Problem:** Token doesn't have permission to post comments.

**Solution:**
1. **For GitHub Actions:** Verify the workflow has the correct permissions:
   ```yaml
   permissions:
     contents: read
     pull-requests: write
     issues: write
   ```
2. **For local testing:** Regenerate your token with the `repo` scope
3. The bot now uses issue comments (more compatible), but still needs write access

### "Review completed but failed to post"

**Problem:** Token can read but not write.

**Solution:**
1. Check that you selected `repo` or `public_repo` scope (not just `repo:status`)
2. Regenerate the token with the correct scopes
3. Update your `.env` file with the new token

### Token Expired

**Problem:** "Bad credentials" or "401 Unauthorized"

**Solution:**
1. Go to GitHub Settings → Personal access tokens
2. Check if your token is expired
3. Generate a new token with the same scopes
4. Update your `.env` file

### Repository Settings Blocking Actions

**Problem:** Bot works locally but not in GitHub Actions

**Solution:**
1. Go to repository **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select:
   - ✅ "Read and write permissions"
   OR
   - ✅ "Read repository contents and packages permissions" + individual permissions
3. ✅ Check "Allow GitHub Actions to create and approve pull requests"
4. Click **Save**

## Security Best Practices

1. **Never commit tokens to git**
   - Always use `.env` files (which are in `.gitignore`)
   - Never hardcode tokens in code

2. **Use minimal permissions**
   - Only grant `public_repo` if you only work with public repositories
   - Use `repo` only when necessary for private repositories

3. **Rotate tokens regularly**
   - Set expiration dates (e.g., 90 days)
   - Regenerate and update before expiration

4. **Use GitHub Actions when possible**
   - The built-in `GITHUB_TOKEN` is more secure
   - It's automatically rotated and scoped per job

5. **Store tokens securely**
   - Use a password manager
   - Don't share tokens via email or chat
   - Revoke tokens you're not using

6. **Monitor token usage**
   - Check your token activity in GitHub settings
   - Revoke any suspicious activity

## Quick Reference

### For GitHub Actions
```yaml
# Already configured in .github/workflows/code-review.yml
permissions:
  contents: read
  pull-requests: write
  issues: write
```
✅ No manual token creation needed

### For Local Testing
```bash
# Create token at: https://github.com/settings/tokens
# Scopes needed: repo (or public_repo for public repos only)

# Add to .env:
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Test:
python -m bot.main --repo owner/repo --pr-number 123 --no-post
```

## Still Having Issues?

1. Check the [Troubleshooting section in CONFIGURATION.md](CONFIGURATION.md#troubleshooting)
2. Review the [main README](../README.md#troubleshooting)
3. Open an issue with:
   - The error message (sanitize any tokens!)
   - Whether you're using GitHub Actions or local testing
   - What you've already tried

## Next Steps

After setting up your token:
- ✅ Test locally with `--no-post` first
- ✅ Then test posting with a real PR
- ✅ Set up GitHub Actions for automatic reviews
- ✅ See [QUICKSTART.md](../QUICKSTART.md) for usage examples
