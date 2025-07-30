from typing_extensions import override
import aiohttp

from .base import GithubService


class GithubServiceImpl(GithubService):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        github_access_token: str,
        base_url: str = "https://api.github.com",
    ):
        self.session: aiohttp.ClientSession = session
        self.base_url: str = base_url
        self.github_access_token: str = github_access_token

    @override
    async def get_repo_id(self, repo_name: str) -> int:
        """Get repository ID from repository name in format 'owner/repo'."""
        url = f"{self.base_url}/repos/{repo_name}"

        headers = {
            "Authorization": f"Bearer {self.github_access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            repo_data: dict[str, int] = await response.json()
            return repo_data["id"]

    @override
    async def add_pr_comment(
        self,
        github_repo_name: str,
        pull_request_number: int,
        comment_body: str,
    ) -> None:
        """Add a comment to a GitHub pull request.

        Args:
            github_repo_name: Repository name in format "owner/repo"
            pull_request_number: PR number
            comment_body: Comment text to add
        """
        url = f"{self.base_url}/repos/{github_repo_name}/issues/{pull_request_number}/comments"

        headers = {
            "Authorization": f"Bearer {self.github_access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        data = {"body": comment_body}

        async with self.session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()

    @override
    async def search_for_pr_comment_with_drift_id(
        self, github_repo_name: str, drift_id: str
    ) -> int | None:
        """Search for an open PR that has a comment with the specified drift ID.

        Args:
            github_repo_name: Repository name in format "owner/repo"
            drift_id: The drift ID to search for in PR comments

        Returns:
            PR number if found, None otherwise
        """
        # Search for open pull requests
        url = f"{self.base_url}/repos/{github_repo_name}/pulls"
        headers = {
            "Authorization": f"Bearer {self.github_access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"state": "open"}

        async with self.session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            prs = await response.json()

        # Check comments on each PR for the drift ID
        for pr in prs:
            pr_number = pr["number"]
            comments_url = f"{self.base_url}/repos/{github_repo_name}/issues/{pr_number}/comments"
            
            async with self.session.get(comments_url, headers=headers) as response:
                response.raise_for_status()
                comments = await response.json()

            # Search for drift ID in comment bodies
            for comment in comments:
                if f"**Drift ID:** `{drift_id}`" in comment["body"]:
                    return pr_number

        return None
