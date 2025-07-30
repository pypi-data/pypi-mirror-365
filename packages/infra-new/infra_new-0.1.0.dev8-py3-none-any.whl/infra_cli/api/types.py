from dataclasses import dataclass
from typing import Any


@dataclass
class CreateTaskRequest:
    plan_json: dict[Any, Any]  # pyright: ignore[reportExplicitAny]
    zip: str | None = None
    github_repo_id: int | None = None
    github_ref: str | None = None
    additionalContext: str | None = None

    def to_json(self):
        return {
            "zip": self.zip,
            "planJson": self.plan_json,
            "additionalContext": self.additionalContext,
            "githubRepoId": self.github_repo_id,
            "githubBranch": self.github_ref,
        }


@dataclass
class CreateTaskResponse:
    task_id: str

    @classmethod
    def from_json(cls, json: dict[str, str]) -> "CreateTaskResponse":
        return cls(task_id=json["taskId"])


@dataclass
class GetTaskResponse:
    status: str
    code_result_path: str | None = None
    github_export_path: str | None = None
    error: str | None = None
    chat_path: str | None = None

    @classmethod
    def from_json(cls, json: dict[str, str]) -> "GetTaskResponse":
        return cls(
            status=json["status"],
            code_result_path=json.get("codeResultPath"),
            github_export_path=json.get("githubExportPath"),
            error=json.get("error"),
            chat_path=json.get("chatPath"),
        )


@dataclass
class ExportToGitHubResponse:
    pr_url: str

    @classmethod
    def from_json(cls, json: dict[str, str]) -> "ExportToGitHubResponse":
        return cls(pr_url=json["prUrl"])
