#!/usr/bin/env python3
"""
Token Verification Script

This script helps verify that your GitHub token has the correct permissions
for the UiPath Code Reviewer Bot.

Usage:
    python verify_token.py

The script will:
1. Check if GITHUB_TOKEN is set
2. Verify the token can authenticate
3. Check token scopes/permissions
4. Test if it can access a repository (if provided)
"""

import os
import sys
from github import Github, GithubException


def check_token_env():
    """Check if GITHUB_TOKEN is set in environment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not found in environment variables")
        print("\nPlease set it:")
        print("  export GITHUB_TOKEN=your_token_here")
        print("\nOr create a .env file with:")
        print("  GITHUB_TOKEN=your_token_here")
        return None
    
    print("✅ GITHUB_TOKEN found in environment")
    print(f"   Token starts with: {token[:7]}...")
    return token


def verify_authentication(token):
    """Verify the token can authenticate."""
    try:
        client = Github(token)
        user = client.get_user()
        print(f"✅ Authentication successful")
        print(f"   Logged in as: {user.login}")
        print(f"   User type: {user.type}")
        return client, user
    except GithubException as e:
        if e.status == 401:
            print("❌ Authentication failed: Invalid token or expired")
            print(f"   Error: {e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)}")
        elif e.status == 403:
            print("⚠️  Token authenticated but has limited access")
            print("   This might be a GitHub Actions token (ghu_*) which has restricted API access")
            print("   For local testing, create a Personal Access Token (ghp_*)")
            print("   See: docs/TOKEN_SETUP.md")
            return None, None
        else:
            print(f"❌ Authentication error: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, None


def check_token_scopes(client):
    """Check what scopes the token has."""
    try:
        # Make a request and check the scopes header
        import requests
        token = client._Github__requester._Requester__auth.token
        response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}"}
        )
        
        scopes = response.headers.get('X-OAuth-Scopes', '')
        if scopes:
            scopes_list = [s.strip() for s in scopes.split(',')]
            print("✅ Token scopes found:")
            for scope in scopes_list:
                print(f"   - {scope}")
            
            # Check for required scopes
            required = False
            if 'repo' in scopes_list:
                print("\n✅ Has 'repo' scope - can access private repositories")
                required = True
            elif 'public_repo' in scopes_list:
                print("\n⚠️  Has 'public_repo' scope - can only access public repositories")
                required = True
            else:
                print("\n❌ Missing required scope!")
                print("   Need: 'repo' (for private repos) or 'public_repo' (for public repos)")
                required = False
            
            return required
        else:
            print("⚠️  Could not determine token scopes")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check scopes: {e}")
        return False


def test_repo_access(client, repo_name=None):
    """Test if token can access a repository."""
    if not repo_name:
        print("\nℹ️  No repository specified for access test")
        print("   To test repository access, run:")
        print("   python verify_token.py owner/repo")
        return
    
    try:
        print(f"\n🔍 Testing access to repository: {repo_name}")
        repo = client.get_repo(repo_name)
        print(f"✅ Can access repository: {repo.full_name}")
        print(f"   Description: {repo.description or 'No description'}")
        print(f"   Private: {repo.private}")
        
        # Test if we can read pull requests
        try:
            prs = list(repo.get_pulls(state='all'))[:1]
            print(f"✅ Can read pull requests")
        except GithubException:
            print(f"❌ Cannot read pull requests")
        
        # Check permissions
        perms = repo.permissions
        print(f"\n   Permissions:")
        print(f"   - Admin: {perms.admin}")
        print(f"   - Push: {perms.push}")
        print(f"   - Pull: {perms.pull}")
        
        if perms.push:
            print("\n✅ Has write access - can post comments!")
        else:
            print("\n❌ Does not have write access - cannot post comments!")
            print("   You need push/write access to post review comments")
        
    except GithubException as e:
        if e.status == 404:
            print(f"❌ Repository not found or no access: {repo_name}")
            print("   - Check the repository name is correct")
            print("   - Ensure your token has access to this repository")
            print("   - For private repos, you need the 'repo' scope")
        else:
            print(f"❌ Error accessing repository: {e}")


def main():
    """Main verification process."""
    print("=" * 60)
    print("GitHub Token Verification for UiPath Code Reviewer Bot")
    print("=" * 60)
    print()
    
    # Step 1: Check environment
    token = check_token_env()
    if not token:
        sys.exit(1)
    
    print()
    
    # Step 2: Verify authentication
    client, user = verify_authentication(token)
    if not client:
        sys.exit(1)
    
    print()
    
    # Step 3: Check scopes
    has_required_scope = check_token_scopes(client)
    
    # Step 4: Test repository access if provided
    repo_name = sys.argv[1] if len(sys.argv) > 1 else None
    test_repo_access(client, repo_name)
    
    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if has_required_scope:
        print("✅ Your token appears to be configured correctly!")
        if repo_name:
            print(f"✅ You should be able to use the bot with {repo_name}")
        else:
            print("\nTo test with a specific repository, run:")
            print("   python verify_token.py owner/repo")
    else:
        print("❌ Your token needs additional permissions")
        print("\nTo fix:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Create a new token or edit existing")
        print("3. Select scopes:")
        print("   - For private repos: 'repo'")
        print("   - For public repos only: 'public_repo'")
        print("4. Update your .env file with the new token")
        print("\n📚 See docs/TOKEN_SETUP.md for detailed instructions")
    
    print()


if __name__ == "__main__":
    try:
        # Try to load from .env file if python-dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        main()
    except KeyboardInterrupt:
        print("\n\nVerification cancelled.")
        sys.exit(0)
