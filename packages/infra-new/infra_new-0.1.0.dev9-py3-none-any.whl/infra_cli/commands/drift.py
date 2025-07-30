import asyncio
import base64
import datetime
import difflib
import io
import json
import os
from typing import Any
from typing_extensions import override
import zipfile
from pathlib import Path

import typer
from rich import print
from infra_cli.api import BaseApiService
from infra_cli.commands.base import BaseCommand
from infra_cli.terraform.base import BaseTerraformCommandRunner


class DriftCommand(BaseCommand):
    """Command to check for drift between local and remote state"""

    def __init__(
        self,
        *,
        api: BaseApiService,
        terraform_runner: BaseTerraformCommandRunner,
        source_dir: str | None,
        backend_dir: str | None,
        plan_file_path: str | None,
        output_dir: str | None,
        github_repo_id: int | None,
        github_ref: str | None,
    ) -> None:
        if not github_repo_id and not source_dir:
            typer.echo("Please provide either a GitHub repo ID or a source directory.")
            raise typer.Exit(1)
        if github_repo_id and source_dir:
            typer.echo("Please provide only one of github_repo_id and source_dir.")
            raise typer.Exit(1)
        if github_repo_id and not github_ref:
            typer.echo("Please provide a GitHub repo ref when providing a GitHub repo.")
            raise typer.Exit(1)
        if github_repo_id and github_ref and not plan_file_path:
            typer.echo("Please provide a plan file path when providing a GitHub repo.")
            raise typer.Exit(1)

        self.api: BaseApiService = api
        self.terraform_runner: BaseTerraformCommandRunner = terraform_runner
        self.source_dir: str | None = source_dir
        self.backend_dir: str | None = (
            os.path.join(source_dir, backend_dir)
            if backend_dir and source_dir
            else source_dir
        )
        self.plan_file_path: str | None = plan_file_path
        self.output_dir: str | None = output_dir
        self.github_repo_id: int | None = github_repo_id
        self.github_ref: str | None = github_ref

    @override
    async def run(self) -> None:
        # First run terraform plan
        if self.plan_file_path is not None:
            with open(self.plan_file_path, "r") as f:
                plan_json = json.loads(f.read())  # pyright: ignore[reportAny]
        elif self.source_dir:
            typer.echo("=== Detecting drift ===")
            plan_path = self._run_terraform_plan()
            if not plan_path:
                typer.echo("No planned changed.")
                return
            plan_json = self._run_terraform_show(plan_path)
        else:
            typer.echo("No source directory provided.")
            return

        typer.echo("\n=== Creating background task ===")
        zip = self._create_zip_from_directory()
        try:
            if zip:
                task = await self.api.schedule_drift_task_from_zip(zip, plan_json)
            elif self.github_repo_id and self.github_ref:
                task = await self.api.schedule_drift_task_for_github(
                    self.github_repo_id, self.github_ref, plan_json
                )
            else:
                raise ValueError("No valid source provided.")

        except Exception as e:
            typer.echo(f"Failed to schedule drift task: {e}")
            raise typer.Exit(1)

        start_time = datetime.datetime.now()

        while True:
            task_response = await self.api.poll_background_task(task.task_id)

            if task_response.status in ["complete", "errored", "terminated"]:
                break
            else:
                typer.echo(
                    f"Drift task is {task_response.status}... [{_format_timedelta(datetime.datetime.now() - start_time)}]"
                )
                await asyncio.sleep(5)

        if task_response.status != "complete":
            typer.echo(f"Drift task failed with status: {task_response.status}")
            raise typer.Exit(1)

        if not task_response.code_result_path:
            return

        zip_results: zipfile.ZipFile | None = None

        if self.source_dir:
            zip_results = await self.api.download_code_result(
                task_response.code_result_path
            )

            self._report_diff(zip_results)

        if self.output_dir and zip_results:
            zip_results.extractall(self.output_dir)
        elif task_response.github_export_path:
            typer.echo("\n=== Exporting to GitHub ===")
            export_result = await self.api.export_code_to_github(
                task_response.github_export_path
            )
            typer.echo(f"Created PR for drift fix: {export_result.pr_url}")

        if task_response.chat_path:
            typer.echo(
                f"\n\nContinue the chat at: {self.api.backend_url}{task_response.chat_path}"
            )

    def _create_zip_from_directory(self) -> str | None:
        """Create a base64-encoded zip file from a directory."""
        if not self.source_dir:
            return None
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(self.source_dir):
                for file in files:
                    # TODO: we should probably just respect the .gitignore file in the source dir
                    if file.startswith(".terraform.lock"):
                        continue
                    file_path = Path(root, file)

                    if ".terraform" in file_path.parts or ".git" in file_path.parts:
                        continue

                    # Get relative path from source_dir
                    arcname = os.path.relpath(file_path, self.source_dir)
                    zip_file.write(file_path, arcname)

        _ = zip_buffer.seek(0)
        return base64.b64encode(zip_buffer.read()).decode("utf-8")

    def _run_terraform_plan(self) -> str | None:
        if not self.backend_dir:
            return None
        """Run terraform init, plan, and show to get plan JSON."""

        # Initialize terraform
        typer.echo("Running terraform init...")
        self.terraform_runner.init(self.backend_dir)

        typer.echo("Running terraform plan...")
        return self.terraform_runner.plan(self.backend_dir)

    def _run_terraform_show(self, plan_path: str) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        typer.echo("Running terraform show...")
        return self.terraform_runner.show(self.backend_dir or ".", plan_path)

    def _report_diff(self, new_zip: zipfile.ZipFile):
        if not self.source_dir:
            return None
        for file_info in new_zip.filelist:
            with new_zip.open(file_info) as new_file:
                new_file_contents = new_file.read().decode("utf-8")
                old_file_path = os.path.join(self.source_dir, file_info.filename)
                if os.path.exists(old_file_path) and os.path.isfile(old_file_path):
                    with open(old_file_path, "r") as old_file:
                        old_file_contents = old_file.read()

                        diff = difflib.unified_diff(
                            old_file_contents.splitlines(),
                            new_file_contents.splitlines(),
                            fromfile=old_file_path,
                            tofile=file_info.filename,
                        )
                        for d in diff:
                            if d.startswith("---") or d.startswith("+++"):
                                print(f"[yellow]{d}", end="")
                            elif d.startswith("+"):
                                print(f"[green]{d}")
                            elif d.startswith("-"):
                                print(f"[red]{d}")
                            elif d.startswith("@@"):
                                print(f"[bright_magenta]{d}", end="")
                            else:
                                typer.echo(d)
                        if diff:
                            print("\n".join(diff))
                elif os.path.isfile(old_file_path):
                    typer.echo(f"New file: {file_info.filename}")


def _format_timedelta(td: datetime.timedelta) -> str:
    """Pretty print a timedelta object."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"
