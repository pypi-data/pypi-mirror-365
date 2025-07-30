from abc import abstractmethod
from typing import Any


class BaseTerraformCommandRunner:
    @abstractmethod
    def plan(self, backend_dir: str, refresh_only: bool = True) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def init(self, backend_dir: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def show(self, backend_dir: str, plan_path: str) -> dict[str, Any]:
        raise NotImplementedError
