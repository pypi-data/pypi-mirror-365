from abc import ABC, abstractmethod


class GithubService(ABC):
    @abstractmethod
    async def get_repo_id(self, repo_name: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def add_pr_comment(
        self, github_repo_name: str, pull_request_number: int, comment_body: str
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search_for_pr_comment_with_drift_id(
        self, github_rep_name: str, drift_id: str
    ) -> int | None:
        raise NotImplementedError
