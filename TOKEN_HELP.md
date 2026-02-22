# 🚀 Getting Started with Token Permissions

**Having trouble posting review comments?** You're in the right place!

## The Issue

You can generate reviews but they're not being posted to your PRs. This is almost always a **GitHub token permission issue**.

## Quick Fix (Choose Your Scenario)

### 🔵 Scenario 1: Using GitHub Actions

**Good news!** You don't need to create any token manually.

1. ✅ The workflow already uses the built-in `GITHUB_TOKEN`
2. ✅ Permissions are already set correctly
3. ⚙️ Just ensure your repository settings allow it:
   - Go to: **Settings** → **Actions** → **General**
   - Under "Workflow permissions", select:
     - ✅ "Read and write permissions"
   - Click **Save**

**That's it!** The bot should now work automatically on PRs.

📚 More details: [docs/TOKEN_SETUP.md#for-github-actions](docs/TOKEN_SETUP.md#for-github-actions)

---

### 🟢 Scenario 2: Local Testing

You need to create a **Personal Access Token** with the right permissions.

#### Quick Steps:

1. **Create Token**
   - Go to: https://github.com/settings/tokens
   - Click: **Generate new token** → **Generate new token (classic)**
   - Note: "UiPath Code Reviewer - Local Testing"
   - Expiration: Choose (e.g., 90 days)
   - **Select scope:**
     - For private repos: ✅ `repo`
     - For public repos only: ✅ `public_repo`
   - Click: **Generate token**
   - **COPY THE TOKEN NOW** (you won't see it again!)

2. **Add to .env file**
   ```bash
   # Create .env file if it doesn't exist
   cp .env.example .env
   
   # Edit .env and add:
   GITHUB_TOKEN=ghp_your_token_here
   ```

3. **Verify it works**
   ```bash
   python verify_token.py
   ```

📚 Detailed guide: [docs/TOKEN_SETUP.md](docs/TOKEN_SETUP.md)

---

## ✅ Verify Your Setup

Run this to check if your token is configured correctly:

```bash
python verify_token.py
```

**Expected output if working:**
```
✅ GITHUB_TOKEN found in environment
✅ Authentication successful
✅ Has 'repo' scope - can access private repositories
✅ Your token appears to be configured correctly!
```

**To test with a specific repository:**
```bash
python verify_token.py owner/repo
```

---

## 🐛 Troubleshooting

### Error: "GitHub access token is required"

**Fix:** Set the GITHUB_TOKEN environment variable
```bash
export GITHUB_TOKEN=ghp_your_token_here
# Or add to .env file
```

### Error: "403 Forbidden" or "Resource not accessible"

**Fix:** Your token needs more permissions

1. **For local testing:**
   - Create new token with `repo` scope
   - See: [docs/TOKEN_SETUP.md#creating-a-personal-access-token](docs/TOKEN_SETUP.md#creating-a-personal-access-token)

2. **For GitHub Actions:**
   - Check repository settings
   - See: [docs/TOKEN_SETUP.md#repository-settings-blocking-actions](docs/TOKEN_SETUP.md#repository-settings-blocking-actions)

### Error: "404 Not Found"

**Fix:** Token doesn't have access to the repository
- For private repos, you need `repo` scope (not just `public_repo`)
- Verify the repository name is correct

---

## 📚 Full Documentation

- **Complete Token Guide:** [docs/TOKEN_SETUP.md](docs/TOKEN_SETUP.md)
- **Configuration Guide:** [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Main README:** [README.md](README.md)

---

## 💡 Quick Reference

### Required Token Scopes

For **Personal Access Token** (local testing):
- Private repos: `repo` ✅
- Public repos: `public_repo` ✅

For **GitHub Actions** (automatic):
- No manual token needed! ✅
- Uses built-in `GITHUB_TOKEN` ✅

### Test Commands

```bash
# Verify token
python verify_token.py

# Test without posting
python -m bot.main --repo owner/repo --pr-number 123 --no-post

# Test with posting
python -m bot.main --repo owner/repo --pr-number 123
```

---

## Still Having Issues?

1. Run the verification script:
   ```bash
   python verify_token.py owner/repo
   ```

2. Check the detailed troubleshooting:
   - [docs/TOKEN_SETUP.md#troubleshooting](docs/TOKEN_SETUP.md#troubleshooting)

3. Review common issues in README:
   - [README.md#troubleshooting](README.md#troubleshooting)

4. If still stuck, open an issue with:
   - The error message (remove any tokens!)
   - Output from `python verify_token.py`
   - Whether using GitHub Actions or local testing

---

**Ready to get started?** 🚀

- Using GitHub Actions? → Check repository settings
- Testing locally? → Create token at https://github.com/settings/tokens
- Verify setup → Run `python verify_token.py`
