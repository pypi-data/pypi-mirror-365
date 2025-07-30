import json
import os
import subprocess
import tempfile
from typing import Any
from typing_extensions import override
from infra_cli.terraform.base import BaseTerraformCommandRunner


class TerraformCommandRunner(BaseTerraformCommandRunner):
    @override
    def plan(self, backend_dir: str, refresh_only: bool = True) -> str | None:
        temp_dir = tempfile.mkdtemp()
        plan_path = os.path.join(temp_dir, "terraform.tfplan")

        plan_cmd = [
            "terraform",
            "plan",
            "-lock=false",
            "-detailed-exitcode",
            "-out",
            plan_path,
        ]
        if refresh_only:
            plan_cmd.insert(-3, "-refresh-only")

        plan_result = subprocess.run(
            plan_cmd, cwd=backend_dir, capture_output=True, text=True
        )

        if plan_result.returncode == 0:
            return None
        elif plan_result.returncode == 1:
            raise ValueError(f"Terraform plan failed: {plan_result.stderr}")

        return plan_path

    @override
    def init(self, backend_dir: str) -> None:
        # Initialize terraform
        init_result = subprocess.run(
            ["terraform", "init"],
            cwd=backend_dir,
            capture_output=True,
            text=True,
        )
        if init_result.returncode != 0:
            raise RuntimeError(f"Terraform init failed: {init_result.stderr}")

    @override
    def show(self, backend_dir: str, plan_path: str) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        show_result = subprocess.run(
            ["terraform", "show", "-json", plan_path],
            cwd=backend_dir,
            capture_output=True,
            text=True,
        )
        if show_result.returncode != 0:
            raise RuntimeError(f"Terraform show failed: {show_result.stderr}")

        return json.loads(show_result.stdout)  # pyright: ignore[reportAny]
