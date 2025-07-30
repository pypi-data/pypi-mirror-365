import asyncio
import os
import shutil
import tempfile
from zipfile import ZipFile
from typing_extensions import override
import unittest

import pytest

from infra_cli.api.testing.fake_api import FakeApiService
from infra_cli.api.types import (
    CreateTaskResponse,
    ExportToGitHubResponse,
    GetTaskResponse,
)
from infra_cli.commands.drift import DriftCommand
from infra_cli.terraform.testing.fake_command_runner import FakeTerraformCommandRunner


class TestDriftCommand(unittest.TestCase):
    @override
    def setUp(self) -> None:
        self.fake_api: FakeApiService = FakeApiService()  # pyright: ignore[reportUninitializedInstanceVariable]
        self.fake_tf_runner: FakeTerraformCommandRunner = FakeTerraformCommandRunner()  # pyright: ignore[reportUninitializedInstanceVariable]
        self.source_dir: str = tempfile.mkdtemp()  # pyright: ignore[reportUninitializedInstanceVariable]
        self.backend_dir: str = os.path.join(self.source_dir, "backend")  # pyright: ignore[reportUninitializedInstanceVariable]
        os.mkdir(self.backend_dir)
        with open(os.path.join(self.backend_dir, "temp.tf"), "w") as f:
            _ = f.write("# this is a comment")

        self.base_new_zip_dir: str = tempfile.mkdtemp()  # pyright: ignore[reportUninitializedInstanceVariable]
        new_zip_backend_dir = os.path.join(self.base_new_zip_dir, "backend")
        new_zip_file: str = os.path.join(self.base_new_zip_dir, "backend", "temp.tf")
        os.mkdir(new_zip_backend_dir)
        with open(os.path.join(new_zip_backend_dir, "temp.tf"), "w") as f:
            _ = f.write("# this is a new comment")

        self.new_zip_file: tuple[int, str] = tempfile.mkstemp(suffix=".zip")  # pyright: ignore[reportUninitializedInstanceVariable]

        with open(self.new_zip_file[1], "wb") as f:
            with ZipFile(f, "w") as zip_file:
                zip_file.write(new_zip_file, arcname="backend/temp.tf")

    @pytest.fixture(autouse=True)
    def capsys(self, capsys: pytest.CaptureFixture[str]) -> None:  # pyright: ignore[reportUninitializedInstanceVariable,reportRedeclaration]
        self.capsys: pytest.CaptureFixture[str] = capsys

    @override
    def tearDown(self) -> None:
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.base_new_zip_dir)
        os.remove(self.new_zip_file[1])

    def test_with_provided_plan_file(self):
        plan_file = os.path.join(self.base_new_zip_dir, "plan.json")
        with open(plan_file, "w") as f:
            _ = f.write("{}")

        self.fake_api.schedule_drift_task_from_zip_result = [
            CreateTaskResponse(task_id="task-id")
        ]
        self.fake_api.poll_background_task_result = [
            GetTaskResponse(status="complete", code_result_path="/code/path")
        ]

        with ZipFile(self.new_zip_file[1]) as f:
            self.fake_api.download_code_result_result = [f]

            drift = DriftCommand(
                api=self.fake_api,
                terraform_runner=self.fake_tf_runner,
                source_dir=self.source_dir,
                backend_dir=self.backend_dir,
                plan_file_path=plan_file,
                output_dir=None,
                github_ref=None,
                github_repo_id=None,
            )
            asyncio.run(drift.run())

        self.assertEqual(self.fake_api.schedule_drift_task_from_zip_call_count, 1)
        self.assertEqual(self.fake_api.poll_background_task_call_count, 1)
        self.assertEqual(self.fake_api.download_code_result_call_count, 1)

        out, _ = self.capsys.readouterr()

        self.assertIn("-# this is a comment", out)
        self.assertIn("+# this is a new comment", out)

    def test_without_provided_plan_file(self):
        self.fake_api.schedule_drift_task_from_zip_result = [
            CreateTaskResponse(task_id="task-id")
        ]
        self.fake_api.poll_background_task_result = [
            GetTaskResponse(status="complete", code_result_path="/code/path")
        ]

        with ZipFile(self.new_zip_file[1]) as f:
            self.fake_api.download_code_result_result = [f]

            drift = DriftCommand(
                api=self.fake_api,
                terraform_runner=self.fake_tf_runner,
                source_dir=self.source_dir,
                backend_dir=self.backend_dir,
                plan_file_path=None,
                output_dir=None,
                github_ref=None,
                github_repo_id=None,
            )
            asyncio.run(drift.run())

        self.assertEqual(self.fake_api.schedule_drift_task_from_zip_call_count, 1)
        self.assertEqual(self.fake_api.poll_background_task_call_count, 1)
        self.assertEqual(self.fake_api.download_code_result_call_count, 1)

    def test_with_output_dir(self):
        self.fake_api.schedule_drift_task_from_zip_result = [
            CreateTaskResponse(task_id="task-id")
        ]
        self.fake_api.poll_background_task_result = [
            GetTaskResponse(status="complete", code_result_path="/code/path")
        ]

        with ZipFile(self.new_zip_file[1]) as f:
            with tempfile.TemporaryDirectory() as output_dir:
                self.fake_api.download_code_result_result = [f]

                drift = DriftCommand(
                    api=self.fake_api,
                    terraform_runner=self.fake_tf_runner,
                    source_dir=self.source_dir,
                    backend_dir=self.backend_dir,
                    plan_file_path=None,
                    output_dir=output_dir,
                    github_ref=None,
                    github_repo_id=None,
                )
                asyncio.run(drift.run())

                with open(os.path.join(output_dir, "backend", "temp.tf")) as f:
                    contents = f.read()
                    self.assertEqual(contents, "# this is a new comment")

    def test_with_git(self):
        plan_file = os.path.join(self.base_new_zip_dir, "plan.json")
        with open(plan_file, "w") as f:
            _ = f.write("{}")
        self.fake_api.schedule_drift_task_for_github_result = [
            CreateTaskResponse(task_id="task-id")
        ]
        self.fake_api.poll_background_task_result = [
            GetTaskResponse(
                status="complete",
                code_result_path="/code/path",
                github_export_path="/github/export",
            )
        ]
        self.fake_api.export_code_to_github_result = [
            ExportToGitHubResponse(pr_url="url")
        ]

        drift = DriftCommand(
            api=self.fake_api,
            terraform_runner=self.fake_tf_runner,
            source_dir=None,
            backend_dir=None,
            plan_file_path=plan_file,
            output_dir=None,
            github_ref="main",
            github_repo_id=12345,
        )
        asyncio.run(drift.run())

        self.assertEqual(self.fake_api.schedule_drift_task_for_github_call_count, 1)
        self.assertEqual(self.fake_api.schedule_drift_task_from_zip_call_count, 0)
        self.assertEqual(self.fake_api.export_code_to_github_call_count, 1)
