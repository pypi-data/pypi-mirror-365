import requests
import asyncio
import httpx
import logging
try:
    from rich.console import Console
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class GitHubOssContributions:
    def __init__(self, username: str, token: str = None) -> None:
        self.username = username
        self.token = token
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def print_contributions(self, org_data: dict = None) -> None:
        """
        Pretty printing the contributions data using rich, with color coding for easy differentiation.
        Shows a loading spinner and fetches async/concurrent data.
        If org_data is None, it will call get_contributions().
        """
        if not RICH_AVAILABLE:
            print("If you want beautiful output, then install rich: pip install rich")
            return

        # Data Representation with rich
        console = Console()
        if org_data is None:
            with Progress(SpinnerColumn(style="bold magenta"), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task(description="[yellow]Fetching data from GitHub...", total=None)
                org_data = self.get_contributions()
            console.print("[bold green]Data fetched Successfully!\n[/bold green]")

        if not org_data:
            console.print("[bold red]Aree Bhai kya ker rha hai, Contribution bgera ker yrr!![/bold red]")
            return

        # Details Contributions -> orgs - issues, PRs and avatar URLs
        for org, data in org_data.items():
            console.print(f"[bold cyan]Org:[/bold cyan] [cyan]{org}[/cyan]")
            console.print(f"[bold yellow]Avatar:[/bold yellow] [link={data['avatar_url']}]{data['avatar_url']}[/link]")
            console.print(f"[bold blue]Profile:[/bold blue] [link={data['profile_url']}]{data['profile_url']}[/link]")
            if data['issues']:
                console.print("[green]Issues:[/green]")
                for issue in data['issues']:
                    console.print(f"  [bold green]-[/bold green] [white]{issue['title']}[/white] [blue]({issue['url']})[/blue]")
            if data['prs']:
                console.print("[magenta]Pull Requests:[/magenta]")
                for pr in data['prs']:
                    console.print(f"  [bold magenta]-[/bold magenta] [white]{pr['title']}[/white] [blue]({pr['url']})[/blue]")
            console.print()  
            console.print(f"[bold dark_red]--------------------------------[/bold dark_red]")
            console.print()  

        # Summary
        total_orgs = len(org_data)
        total_issues = sum(len(data['issues']) for data in org_data.values())
        total_prs = sum(len(data['prs']) for data in org_data.values())
        console.print(f"[bold white]Summary:[/bold white]")
        console.print(f"[bold cyan]Organizations:[/bold cyan] [cyan]{total_orgs}[/cyan]")
        console.print(f"[bold green]Issues:[/bold green] [green]{total_issues}[/green]")
        console.print(f"[bold magenta]Pull Requests:[/bold magenta] [magenta]{total_prs}[/magenta]\n")  


    def _fetch(self, url: str) -> dict:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return {}
    

    def _search(self, query: str) -> list:
        url = f"https://api.github.com/search/issues?q={query}&per_page=100"
        return self._fetch(url).get('items', [])
    

    async def _is_org_async(self, owner: str, client: httpx.AsyncClient, headers: dict) -> tuple:
        try:
            resp = await client.get(f"https://api.github.com/users/{owner}", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return owner, data['type'] == "Organization", data
        except Exception as e:
            logging.error(f"Error fetching org info for {owner}: {e}")
            return owner, False, {}

    def get_contributions(self) -> dict:
        issues = self._search(f"author:{self.username}+type:issue")
        prs = self._search(f"author:{self.username}+type:pr")

        # Collect all unique repo owners
        repo_owners = set()
        item_map = []
        for item, typ in [(issues, "issues"), (prs, "prs")]:
            for obj in item:
                repo_owner = obj['repository_url'].split("/")[-2]
                repo_owners.add(repo_owner)
                item_map.append((repo_owner, typ, obj))

        async def fetch_orgs():
            headers = self.headers.copy()
            async with httpx.AsyncClient() as client:
                tasks = [self._is_org_async(owner, client, headers) for owner in repo_owners]
                results = await asyncio.gather(*tasks)
            return {owner: (is_org, data) for owner, is_org, data in results}

        org_results = asyncio.run(fetch_orgs())

        org_data = {}
        for repo_owner, typ, obj in item_map:
            is_org, user_data = org_results[repo_owner]
            if is_org:
                if repo_owner not in org_data:
                    org_data[repo_owner] = {
                        "avatar_url": user_data.get('avatar_url', ''),
                        "profile_url": user_data.get('html_url', ''),
                        "issues": [],
                        "prs": []
                    }
                org_data[repo_owner][typ].append({
                    "title": obj['title'],
                    "url": obj['html_url']
                })
        if not org_data:
            if RICH_AVAILABLE:
                console = Console()
                console.print("[bold red]Aree Bhai kya ker rha hai, Contribution bgera ker yrr!![/bold red]")
            else:
                print("Aree Bhai kya ker rha hai, Contribution bgera ker yrr!!")
        return org_data
    
