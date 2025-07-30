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
            repo_data = await response.json()
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
