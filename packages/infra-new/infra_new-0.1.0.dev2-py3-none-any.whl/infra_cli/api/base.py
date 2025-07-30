from abc import abstractmethod
from typing import Any
from zipfile import ZipFile

from infra_cli.api.types import (
    CreateTaskResponse,
    ExportToGitHubResponse,
    GetTaskResponse,
)


class BaseApiService:
    """Base class for calling the infra.new API backend"""

    def __init__(
        self,
        api_key: str,
        # TODO: update this to point to prod by default
        backend_url: str = "https://dev.infra.new",
    ):
        self.api_key: str = api_key
        self.backend_url: str = backend_url

    @abstractmethod
    async def schedule_drift_task_from_zip(
        self,
        zip_data: str,
        plan_json: dict[Any, Any],  # pyright: ignore[reportExplicitAny]
    ) -> CreateTaskResponse:
        raise NotImplementedError

    @abstractmethod
    async def schedule_drift_task_for_github(
        self,
        github_repo_id: int,
        github_ref: str,
        plan_json: dict[Any, Any],  # pyright: ignore[reportExplicitAny]
    ) -> CreateTaskResponse:
        raise NotImplementedError

    @abstractmethod
    async def poll_background_task(self, task_id: str) -> GetTaskResponse:
        raise NotImplementedError

    @abstractmethod
    async def download_code_result(self, code_result_path: str) -> ZipFile:
        raise NotImplementedError

    @abstractmethod
    async def export_code_to_github(
        self, github_export_path: str
    ) -> ExportToGitHubResponse:
        raise NotImplementedError
