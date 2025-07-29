# github-oss-contributions Package

Fetch organizations where a user created issues or PRs for Open Source projects on GitHub.

## Features

- Retrieve organizations where a GitHub user has created issues or pull requests.
- Distinguish between organizations and individual repositories.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```
from github_oss_contributions import GitHubOssContributions

# Replace 'username' with the GitHub username, and optionally provide a GitHub token for higher rate limits
client = GitHubOssContributions('username', token='YOUR_GITHUB_TOKEN')
orgs_details = client.get_contributions()
print(orgs_details)
```

## Requirements

- Python 3.7+
- requests

## Author

Mohit Upadhyay and Anuj Kumar Upadhyay
