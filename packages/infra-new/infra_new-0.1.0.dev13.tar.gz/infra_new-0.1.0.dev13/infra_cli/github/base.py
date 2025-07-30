from abc import ABC, abstractmethod


class GithubService(ABC):
    @abstractmethod
    async def add_pr_comment(
        self, github_repo_id: int, pull_request_number: int, comment_body: str
    ) -> None:
        raise NotImplementedError
