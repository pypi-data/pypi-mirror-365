import argparse
import asyncio
from github_oss_contributions.main import GitHubOssContributions

def main():
    parser = argparse.ArgumentParser(description="Fetch and display your GitHub OSS contributions.")
    parser.add_argument("--username", required=True, help="Your GitHub username")
    parser.add_argument("--token", help="GitHub personal access token (optional, for higher rate limits)")
    parser.add_argument("--raw", action="store_true", help="Print raw data instead of pretty output")
    args = parser.parse_args()

    client = GitHubOssContributions(username=args.username, token=args.token)
    if args.raw:
        org_data = client.get_contributions()
        print(org_data)
    else:
        # For async pretty output
        # asyncio.run(client.print_contributions())
        client.print_contributions()

if __name__ == "__main__":
    main()