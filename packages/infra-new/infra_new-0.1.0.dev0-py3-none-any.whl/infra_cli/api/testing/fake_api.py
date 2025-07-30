from typing import Any
from zipfile import ZipFile
from typing_extensions import override
from infra_cli.api.base import BaseApiService
from infra_cli.api.types import (
    CreateTaskResponse,
    ExportToGitHubResponse,
    GetTaskResponse,
)


class FakeApiService(BaseApiService):
    def __init__(
        self,
        api_key: str = "unused",
        backend_url: str = "https://dev.infra.new",
    ):
        super().__init__(api_key, backend_url)

        self.schedule_drift_task_from_zip_result: (
            list[CreateTaskResponse] | Exception | None
        ) = None
        self.schedule_drift_task_for_github_result: (
            list[CreateTaskResponse] | Exception | None
        ) = None
        self.poll_background_task_result: list[GetTaskResponse] | Exception | None = (
            None
        )
        self.download_code_result_result: list[ZipFile] | Exception | None = None
        self.export_code_to_github_result: (
            list[ExportToGitHubResponse] | ExceptionGroup | None
        ) = None

        self.schedule_drift_task_from_zip_call_count: int = 0
        self.schedule_drift_task_for_github_call_count: int = 0
        self.poll_background_task_call_count: int = 0
        self.download_code_result_call_count: int = 0
        self.export_code_to_github_call_count: int = 0

    @override
    async def schedule_drift_task_from_zip(
        self,
        zip_data: str,
        plan_json: dict[Any, Any],  # pyright: ignore[reportExplicitAny]
    ) -> CreateTaskResponse:
        if self.schedule_drift_task_from_zip_result is None:
            raise ValueError(
                "No response for schedule_drift_task_from_zip was provided"
            )

        self.schedule_drift_task_from_zip_call_count += 1

        if isinstance(self.schedule_drift_task_from_zip_result, Exception):
            raise self.schedule_drift_task_from_zip_result

        if len(self.schedule_drift_task_from_zip_result) == 0:
            raise ValueError("schedule_drift_task_from_zip is empty")
        return self.schedule_drift_task_from_zip_result.pop(0)

    @override
    async def schedule_drift_task_for_github(
        self,
        github_repo_id: int,
        github_ref: str,
        plan_json: dict[Any, Any],  # pyright: ignore[reportExplicitAny]
    ) -> CreateTaskResponse:
        if self.schedule_drift_task_for_github_result is None:
            raise ValueError(
                "No response for schedule_drift_task_for_github was provided"
            )

        self.schedule_drift_task_for_github_call_count += 1

        if isinstance(self.schedule_drift_task_for_github_result, Exception):
            raise self.schedule_drift_task_for_github_result

        if len(self.schedule_drift_task_for_github_result) == 0:
            raise ValueError("schedule_drift_task_for_github_result is empty")
        return self.schedule_drift_task_for_github_result.pop(0)

    @override
    async def poll_background_task(self, task_id: str) -> GetTaskResponse:
        if self.poll_background_task_result is None:
            raise ValueError("No response for poll_background_task was provided")

        self.poll_background_task_call_count += 1

        if isinstance(self.poll_background_task_result, Exception):
            raise self.poll_background_task_result

        if len(self.poll_background_task_result) == 0:
            raise ValueError("poll_background_task_result is empty")

        return self.poll_background_task_result.pop(0)

    @override
    async def download_code_result(self, code_result_path: str) -> ZipFile:
        if self.download_code_result_result is None:
            raise ValueError("No response for download_code_result_result was provided")

        self.download_code_result_call_count += 1

        if isinstance(self.download_code_result_result, Exception):
            raise self.download_code_result_result

        if len(self.download_code_result_result) == 0:
            raise ValueError("download_code_result_result is empty")

        return self.download_code_result_result.pop(0)

    @override
    async def export_code_to_github(
        self, github_export_path: str
    ) -> ExportToGitHubResponse:
        if self.export_code_to_github_result is None:
            raise ValueError(
                "No response for export_code_to_github_result was provided"
            )

        self.export_code_to_github_call_count += 1

        if isinstance(self.export_code_to_github_result, Exception):
            raise self.export_code_to_github_result

        if len(self.export_code_to_github_result) == 0:
            raise ValueError("export_code_to_github_result is empty")

        return self.export_code_to_github_result.pop(0)
