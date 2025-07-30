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
    async def add_pr_comment(
        self,
        github_repo_id: int,
        pull_request_number: int,
        comment_body: str,
    ) -> None:
        """Add a comment to a GitHub pull request.

        Args:
            github_repo_id: Repository ID in format "owner/repo"
            pull_request_number: PR number
            comment_body: Comment text to add
        """
        url = f"{self.base_url}/repos/{github_repo_id}/issues/{pull_request_number}/comments"

        headers = {
            "Authorization": f"Bearer {self.github_access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        data = {"body": comment_body}

        async with self.session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()
