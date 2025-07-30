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

    async def _find_prs_with_comment_containing(
        self, github_repo_name: str, search_text: str, exclude_pr_number: int | None = None
    ) -> list[int]:
        """Find open PRs that have comments containing the specified text.

        Args:
            github_repo_name: Repository name in format "owner/repo"
            search_text: Text to search for in PR comments
            exclude_pr_number: PR number to exclude from search (optional)

        Returns:
            List of PR numbers that contain the search text in their comments
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

        matching_prs = []
        
        # Check comments on each PR for the search text
        for pr in prs:
            pr_number = pr["number"]
            
            # Skip excluded PR if specified
            if exclude_pr_number and pr_number == exclude_pr_number:
                continue
                
            comments_url = f"{self.base_url}/repos/{github_repo_name}/issues/{pr_number}/comments"
            
            async with self.session.get(comments_url, headers=headers) as response:
                response.raise_for_status()
                comments = await response.json()

            # Search for text in comment bodies
            for comment in comments:
                if search_text in comment["body"]:
                    matching_prs.append(pr_number)
                    break

        return matching_prs

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
        matching_prs = await self._find_prs_with_comment_containing(
            github_repo_name, f"**Drift ID:** `{drift_id}`"
        )
        return matching_prs[0] if matching_prs else None

    @override
    async def close_stale_drift_prs(
        self, github_repo_name: str, backend_dir: str, new_pr_number: int
    ) -> None:
        """Close stale drift PRs that contain the specified backend directory.
        
        Args:
            github_repo_name: Repository name in format "owner/repo"
            backend_dir: Backend directory path to search for in PR comments
            new_pr_number: Number of the new PR to link to in the closing comment
        """
        # Find PRs with matching backend directory, excluding the new PR
        stale_pr_numbers = await self._find_prs_with_comment_containing(
            github_repo_name, 
            f"**Backend Directory:** `{backend_dir}`",
            exclude_pr_number=new_pr_number
        )
        
        # Close each stale PR with a comment
        for pr_number in stale_pr_numbers:
            # Add closing comment with link to new PR
            closing_comment = f"""## Closing Stale Drift PR

This PR is being closed because a newer drift fix has been created for the same backend directory (`{backend_dir}`).

Please refer to the latest drift fix: #{new_pr_number}"""
            
            await self.add_pr_comment(github_repo_name, pr_number, closing_comment)
            
            # Close the PR
            close_url = f"{self.base_url}/repos/{github_repo_name}/pulls/{pr_number}"
            close_data = {"state": "closed"}
            headers = {
                "Authorization": f"Bearer {self.github_access_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            
            async with self.session.patch(close_url, headers=headers, json=close_data) as response:
                response.raise_for_status()
