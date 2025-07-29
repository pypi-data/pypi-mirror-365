import requests

class GitHubOssContributions:
    def __init__(self, username, token=None):
        self.username = username
        self.token = token
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _fetch(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _search(self, query):
        url = f"https://api.github.com/search/issues?q={query}&per_page=100"
        return self._fetch(url).get('items', [])

    def _is_org(self, owner):
        data = self._fetch(f"https://api.github.com/users/{owner}")
        return data['type'] == "Organization", data

    def get_contributions(self):
        issues = self._search(f"author:{self.username}+type:issue")
        prs = self._search(f"author:{self.username}+type:pr")

        org_data = {}
        for item, typ in [(issues, "issues"), (prs, "prs")]:
            for obj in item:
                repo_owner = obj['repository_url'].split("/")[-2]
                is_org, user_data = self._is_org(repo_owner)
                if is_org:
                    if repo_owner not in org_data:
                        org_data[repo_owner] = {
                            "avatar_url": user_data['avatar_url'],
                            "profile_url": user_data['html_url'],
                            "issues": [],
                            "prs": []
                        }
                    org_data[repo_owner][typ].append({
                        "title": obj['title'],
                        "url": obj['html_url']
                    })
        return org_data
