import io
import os
from typing import Any
from zipfile import ZipFile
import aiohttp
from typing_extensions import override

from infra_cli.api.types import (
    CreateTaskRequest,
    CreateTaskResponse,
    ExportToGitHubResponse,
    GetTaskResponse,
)
from .base import BaseApiService


class ApiService(BaseApiService):
    """Service for calling the infra.new API backend"""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        # TODO: update this to point to prod by default
        backend_url: str = "https://dev.infra.new",
    ):
        super().__init__(api_key, backend_url)
        self.session: aiohttp.ClientSession = session
        self._cf_access_client_id: str | None = os.environ.get("CF_ACCESS_CLIENT_ID")
        self._cf_access_client_secret: str | None = os.environ.get(
            "CF_ACCESS_CLIENT_SECRET"
        )
        self._base_headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
        }
        if self._cf_access_client_id:
            self._base_headers["CF-Access-Client-Id"] = self._cf_access_client_id
        if self._cf_access_client_secret:
            self._base_headers["CF-Access-Client-Secret"] = (
                self._cf_access_client_secret
            )

    @override
    async def schedule_drift_task_from_zip(
        self,
        zip_data: str,
        plan_json: dict[Any, Any],  # pyright: ignore[reportExplicitAny]
    ) -> CreateTaskResponse:
        """Schedule a drift task for the given plan path"""

        request = CreateTaskRequest(zip=zip_data, plan_json=plan_json)

        response = await self.session.post(
            f"{self.backend_url}/api/experimental/tasks",
            headers=self._base_headers,
            json=request.to_json(),
        )

        response.raise_for_status()

        json_response: dict[str, str] = await response.json(content_type="text/plain")

        return CreateTaskResponse.from_json(json_response)

    @override
    async def schedule_drift_task_for_github(
        self,
        github_repo_id: int,
        github_ref: str,
        plan_json: dict[Any, Any],  # pyright: ignore[reportExplicitAny]
    ) -> CreateTaskResponse:
        """Schedule a drift task for the given plan path"""

        request = CreateTaskRequest(
            github_repo_id=github_repo_id,
            github_ref=github_ref,
            plan_json=plan_json,
        )

        response = await self.session.post(
            f"{self.backend_url}/api/experimental/tasks",
            headers=self._base_headers,
            json=request.to_json(),
        )

        response.raise_for_status()

        json_response: dict[str, str] = await response.json(content_type="text/plain")

        return CreateTaskResponse.from_json(json_response)

    @override
    async def poll_background_task(self, task_id: str) -> GetTaskResponse:
        response = await self.session.get(
            f"{self.backend_url}/api/experimental/tasks/{task_id}",
            headers=self._base_headers,
        )

        response.raise_for_status()

        json_response: dict[str, str] = await response.json()

        return GetTaskResponse.from_json(json_response)

    @override
    async def download_code_result(self, code_result_path: str) -> ZipFile:
        response = await self.session.get(
            f"{self.backend_url}{code_result_path}",
            headers=self._base_headers,
        )

        response.raise_for_status()

        zip_bytes = await response.read()
        return ZipFile(io.BytesIO(zip_bytes))

    @override
    async def export_code_to_github(
        self, github_export_path: str
    ) -> ExportToGitHubResponse:
        response = await self.session.post(
            f"{self.backend_url}{github_export_path}",
            headers=self._base_headers,
            json={},
        )

        response.raise_for_status()

        json_response: dict[str, str] = await response.json()

        return ExportToGitHubResponse.from_json(json_response)
