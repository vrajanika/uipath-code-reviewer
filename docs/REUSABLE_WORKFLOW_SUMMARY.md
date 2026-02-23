# Reusable Workflow Implementation Summary

## Overview

This document summarizes the changes made to convert the UiPath Code Reviewer Bot into a reusable GitHub workflow that can be called from other repositories.

## What Changed

### 1. Modified `.github/workflows/code-review.yml`

**Added `workflow_call` trigger:**
- Allows other repositories to call this workflow as a reusable workflow
- Maintains backward compatibility with existing local triggers (`pull_request` and `issue_comment`)

**Defined inputs:**
- `repository` (string, required): Repository name in `owner/repo` format
- `pr-number` (number, required): Pull request number to review
- `all-files` (boolean, optional): Review all files instead of just UiPath files (default: false)

**Defined secrets:**
- `AZURE_OPENAI_ENDPOINT` (required): Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` (required): Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT_NAME` (required): Azure OpenAI deployment/model name
- `AZURE_OPENAI_API_VERSION` (optional): Azure OpenAI API version
- `GH_TOKEN` (required): GitHub token for API access

**Updated workflow logic:**
- Added conditional checkout steps based on event type
- When called as reusable workflow: checks out this repository's code
- When triggered locally: checks out the current repository
- Updated environment variables to use appropriate secrets based on event type
- Modified Python command to use inputs when called as reusable workflow
- Updated post-review step to handle both local and remote repositories

### 2. Created `.github/workflows/example-usage.yml`

Example workflow file showing how other repositories can use this as a reusable workflow. This file:
- Demonstrates the correct syntax for calling the reusable workflow
- Shows how to pass inputs and secrets
- Includes helpful comments explaining the purpose and usage
- **Important**: This is for reference only and should NOT be used in this repository

### 3. Created `docs/SHARED_WORKFLOW.md`

Comprehensive documentation covering:
- What a shared workflow is and its benefits
- Step-by-step setup instructions
- Configuration options (inputs and secrets)
- Advanced usage examples (version pinning, branch filtering, etc.)
- Troubleshooting common issues
- Security considerations

### 4. Updated `README.md`

Added sections highlighting:
- Reusable workflow as the recommended setup method
- Quick setup example for shared workflow usage
- Link to comprehensive shared workflow documentation
- Distinction between shared workflow and self-hosted setup options
- Updated features list to include "Reusable Workflow" capability

### 5. Updated `QUICKSTART.md`

Added information about:
- Two setup methods (shared workflow vs. self-hosted)
- Recommendation to use shared workflow for easiest setup
- Link to detailed shared workflow documentation

## How It Works

### For Users of This Workflow (Other Repositories)

1. Users add Azure OpenAI secrets to their repository
2. Users create a workflow file that calls `kangtamo/uipath-code-reviewer/.github/workflows/code-review.yml@main`
3. When a PR is created in their repository, GitHub Actions:
   - Triggers their workflow
   - Calls the reusable workflow in this repository
   - Checks out the code from this repository
   - Installs dependencies from this repository
   - Runs the review bot against their repository and PR
   - Posts review comments back to their PR

### For This Repository (Local Usage)

The workflow continues to work as before:
- Triggered on pull requests and issue comments
- Checks out the local repository code
- Runs reviews on this repository's PRs
- Posts comments to this repository's PRs

## Key Design Decisions

### Backward Compatibility
- Existing local triggers (`pull_request`, `issue_comment`) are maintained
- Workflow continues to function for this repository's own PRs
- No breaking changes to existing functionality

### Conditional Logic
- Uses `github.event_name` to determine if running as reusable workflow or local trigger
- Applies appropriate checkout, installation, and execution logic based on event type
- Ensures secrets and inputs are correctly mapped in both scenarios

### Token Handling
- For reusable workflow calls: uses `GH_TOKEN` secret (passed from calling repository)
- For local triggers: uses `GITHUB_TOKEN` secret (automatically provided by GitHub)
- This allows the workflow to post comments to the correct repository

### Path Management
- When called as reusable workflow: code is checked out to `uipath-code-reviewer/` subdirectory
- All paths adjusted accordingly (requirements.txt, review_result.txt, etc.)
- Ensures no conflicts with the calling repository's files

## Testing

- Workflow syntax validated with `actionlint`
- YAML syntax validated with `yamllint`
- All trailing spaces removed for cleaner formatting
- Example workflow file also validated

## Benefits for Users

1. **Zero Code Duplication**: No need to copy bot code to every repository
2. **Automatic Updates**: Bug fixes and improvements automatically available
3. **Simple Setup**: Just add secrets and a small workflow file
4. **Consistent Reviews**: Same review quality across all repositories
5. **Easy Maintenance**: Update secrets in one place, not in code
6. **Flexible Configuration**: Can customize via inputs (all-files option, etc.)

## Security Considerations

- Secrets are passed from calling repository, not exposed from this repository
- GitHub token scope limited to what calling repository provides
- Workflow only reads PR data and posts comments; does not modify code
- Users maintain control over their own secrets and permissions

## Migration Path for Existing Users

Existing users of this repository can:
1. Continue using it as before (no changes required)
2. Optionally migrate to using it as a shared workflow for easier maintenance

New users are recommended to use the shared workflow approach unless they need to customize the bot code.

## Version Pinning

Users can pin to specific versions:
- `@main` - Always use latest version (recommended for most users)
- `@v1.0.0` - Pin to specific release version
- `@commit-sha` - Pin to specific commit

## Future Enhancements

Possible future improvements:
- Add more input parameters for customization
- Support for custom review prompts
- Configurable file type filters
- Review result outputs for downstream jobs
- Support for review approvals/rejections

## Documentation

Complete documentation available at:
- Main guide: `docs/SHARED_WORKFLOW.md`
- Example: `.github/workflows/example-usage.yml`
- README: Updated with quick start and links
- QUICKSTART: Updated with setup method options
