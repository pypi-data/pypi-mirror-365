from typing import Any
from typing_extensions import override
from infra_cli.terraform.base import BaseTerraformCommandRunner


class FakeTerraformCommandRunner(BaseTerraformCommandRunner):
    @override
    def plan(self, backend_dir: str, refresh_only: bool = True) -> str | None:
        return "plan"

    @override
    def init(self, backend_dir: str) -> None:
        return

    @override
    def show(self, backend_dir: str, plan_path: str) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return {}
