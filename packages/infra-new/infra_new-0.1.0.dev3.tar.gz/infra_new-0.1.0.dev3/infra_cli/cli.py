from functools import partial
from typing import Annotated
import aiohttp
import typer

from infra_cli.api import ApiService
from infra_cli.commands.drift import DriftCommand
from asyncer import syncify
from dotenv import load_dotenv

from infra_cli.terraform.command_runner import TerraformCommandRunner

_ = load_dotenv()

app = typer.Typer()


@app.command()
@partial(syncify, raise_sync_error=False)
async def drift(
    api_key: Annotated[str, typer.Option(help="API key")],
    github_repo_id: Annotated[int | None, typer.Option(help="GitHub repo ID")] = None,
    github_ref: Annotated[str | None, typer.Option(help="GitHub repo ref")] = None,
    source_dir: Annotated[
        str | None,
        typer.Option(help="This is the source directory that will be uploaded."),
    ] = None,
    backend_dir: Annotated[
        str | None,
        typer.Option(
            help="The directory where the backend is located. This should be a relative path from the source directory. This is only needed if you are not passing in a terraform plan file."
        ),
    ] = None,
    output_dir: Annotated[str | None, typer.Option(help="Output directory")] = None,
    plan_file_path: Annotated[
        str | None, typer.Option(help="Path to plan file")
    ] = None,
    # Hidden arguments / options
    backend_url: Annotated[
        str, typer.Option(help="Backend URL", hidden=True)
    ] = "https://dev.infra.new",
):
    tf_cmd_runner = TerraformCommandRunner()
    async with aiohttp.ClientSession() as session:
        api = ApiService(session, api_key, backend_url)
        cmd = DriftCommand(
            api=api,
            terraform_runner=tf_cmd_runner,
            source_dir=source_dir,
            backend_dir=backend_dir,
            plan_file_path=plan_file_path,
            output_dir=output_dir,
            github_repo_id=github_repo_id,
            github_ref=github_ref,
        )

        await cmd.run()


@app.command()
def version():
    typer.echo("Version action")


if __name__ == "__main__":
    app()