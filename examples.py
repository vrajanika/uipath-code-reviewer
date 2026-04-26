"""
Example script demonstrating how to use the bot programmatically.
"""

import os
from bot.reviewer import CodeReviewer
from bot.bedrock_client import BedrockClient
from bot.github_client import GitHubClient


def example_usage():
    """Example of using the bot programmatically."""

    # Option 1: Using environment variables (recommended)
    # Make sure these are set in your .env file:
    #   AWS_REGION, BEDROCK_MODEL_ID, GITHUB_TOKEN
    reviewer = CodeReviewer()

    # Option 2: Explicit configuration
    # bedrock_client = BedrockClient(
    #     model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    #     aws_region="us-east-1",
    #     aws_access_key_id="your-access-key-id",
    #     aws_secret_access_key="your-secret-access-key",
    # )
    # github_client = GitHubClient(access_token="your-github-token")
    # reviewer = CodeReviewer(
    #     github_client=github_client,
    #     bedrock_client=bedrock_client,
    # )

    # Review a pull request
    result = reviewer.review_pull_request(
        repo_full_name="owner/repo",
        pr_number=1,
        post_comments=False,  # Set to True to post comments
        focus_on_uipath=True,  # Set to False to review all files
    )

    print(f"Review Status: {result['status']}")
    print(f"Message: {result['message']}")

    if 'overall_review' in result:
        print("\nOverall Review:")
        print(result['overall_review'])

    # Access individual file reviews
    if 'reviews' in result:
        for review in result['reviews']:
            print(f"\n{review['filename']}: {review['status']}")


def example_single_file_review():
    """Example of reviewing a single file diff."""
    from bot.bedrock_client import BedrockClient

    client = BedrockClient()

    # Example diff (would come from git)
    diff = """
    + <Sequence DisplayName="Process Transaction">
    +   <TryCatch DisplayName="Try Process">
    +     <Try>
    +       <Assign DisplayName="Get Transaction Data">
    +         <variable>[TransactionData] = TransactionQueue.Dequeue()</variable>
    +       </Assign>
    +     </Try>
    +     <Catches>
    +       <Catch x:TypeArguments="s:Exception">
    +         <ActivityAction x:TypeArguments="s:Exception">
    +           <LogMessage DisplayName="Log Error" Level="Error" Message="[exception.Message]" />
    +         </ActivityAction>
    +       </Catch>
    +     </Catches>
    +   </TryCatch>
    + </Sequence>
    """

    review = client.review_code(
        diff=diff,
        file_path="ProcessTransaction.xaml",
        context="This is a transaction processing workflow"
    )

    print("Review for ProcessTransaction.xaml:")
    print(review)


if __name__ == "__main__":
    print("Example 1: Review a pull request")
    print("=" * 50)
    # Uncomment to run (requires valid credentials)
    # example_usage()

    print("\nExample 2: Review a single file diff")
    print("=" * 50)
    # Uncomment to run (requires valid AWS Bedrock credentials)
    # example_single_file_review()

    print("\nNote: Uncomment the function calls above and set your credentials to run the examples.")
