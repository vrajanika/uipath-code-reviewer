"""
Example script demonstrating how to use the bot programmatically.
"""

import os
from bot.reviewer import CodeReviewer
from bot.azure_openai_client import AzureOpenAIClient
from bot.github_client import GitHubClient


def example_usage():
    """Example of using the bot programmatically."""
    
    # Option 1: Using environment variables (recommended)
    # Make sure these are set in your .env file
    reviewer = CodeReviewer()
    
    # Option 2: Explicit configuration
    # azure_client = AzureOpenAIClient(
    #     azure_endpoint="https://your-resource.openai.azure.com/",
    #     api_key="your-api-key",
    #     deployment_name="your-deployment-name",
    # )
    # github_client = GitHubClient(access_token="your-github-token")
    # reviewer = CodeReviewer(
    #     github_client=github_client,
    #     azure_client=azure_client,
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
    from bot.azure_openai_client import AzureOpenAIClient
    
    client = AzureOpenAIClient()
    
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
    # Uncomment to run (requires valid Azure OpenAI credentials)
    # example_single_file_review()
    
    print("\nNote: Uncomment the function calls above and set your credentials to run the examples.")
