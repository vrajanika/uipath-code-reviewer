"""
Main entry point for the code review bot.
"""

import argparse
import sys
import os
from dotenv import load_dotenv
from .reviewer import CodeReviewer


def main():
    """Main function to run the code review bot."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='UiPath Code Review Bot')
    parser.add_argument(
        '--repo',
        required=True,
        help='Repository full name (e.g., owner/repo)'
    )
    parser.add_argument(
        '--pr-number',
        type=int,
        required=True,
        help='Pull request number'
    )
    parser.add_argument(
        '--no-post',
        action='store_true',
        help='Do not post comments to GitHub'
    )
    parser.add_argument(
        '--all-files',
        action='store_true',
        help='Review all files, not just UiPath files'
    )
    parser.add_argument(
        '--output',
        default='review_result.txt',
        help='Output file for review results'
    )
    
    args = parser.parse_args()
    
    # Validate environment variables
    required_env_vars = [
        'BEDROCK_MODEL_ID',
        'AWS_REGION',
        'GITHUB_TOKEN',
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        print("  - BEDROCK_MODEL_ID: Claude model ID in Bedrock (e.g. anthropic.claude-3-5-sonnet-20241022-v2:0)")
        print("  - AWS_REGION: AWS region where Bedrock is enabled (e.g. us-east-1)")
        print("  - GITHUB_TOKEN: GitHub access token")
        print("\nOptional (not needed when using IAM roles):")
        print("  - AWS_ACCESS_KEY_ID: AWS access key ID")
        print("  - AWS_SECRET_ACCESS_KEY: AWS secret access key")
        print("  - AWS_SESSION_TOKEN: AWS session token for temporary credentials")
        sys.exit(1)
    
    try:
        # Create reviewer instance
        reviewer = CodeReviewer()
        
        print(f"Reviewing PR #{args.pr_number} in {args.repo}...")
        
        # Perform review
        result = reviewer.review_pull_request(
            repo_full_name=args.repo,
            pr_number=args.pr_number,
            post_comments=not args.no_post,
            focus_on_uipath=not args.all_files,
        )
        
        print(f"Review status: {result['status']}")
        print(f"Message: {result['message']}")
        
        if 'overall_review' in result:
            # Save review to file
            with open(args.output, 'w') as f:
                f.write(result['overall_review'])
            print(f"Review saved to {args.output}")
        
        # Exit with appropriate code
        if result['status'] in ['success', 'partial_success']:
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        print(f"Error during review: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
