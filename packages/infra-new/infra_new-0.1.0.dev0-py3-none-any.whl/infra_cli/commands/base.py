class BaseCommand:
    """Base command class for all commands."""

    async def run(self) -> None:
        raise NotImplementedError("Subclasses must implement the run method")
