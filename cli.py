import typer

from typer.core import TyperGroup
from advanced_alchemy.cli import get_alchemy_group, add_migration_commands


app = typer.Typer()


@app.callback()
def callback():
    """CLI da aplicação."""


def create_cli() -> TyperGroup:
    alchemy_group = get_alchemy_group()
    typer_clicker_object = typer.main.get_command(app)

    assert isinstance(typer_clicker_object, TyperGroup)

    typer_clicker_object.add_command(add_migration_commands(alchemy_group))  # type: ignore

    typer_clicker_object.context_settings = {
        'default_map': {
            'alchemy': {'config': 'app.infrastructure.database.sqlite.database.config'}
        }
    }

    return typer_clicker_object


if __name__ == "__main__":
    cli = create_cli()
    cli()
