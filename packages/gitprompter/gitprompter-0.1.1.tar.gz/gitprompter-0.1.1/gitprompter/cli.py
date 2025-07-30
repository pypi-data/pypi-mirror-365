import click
from .core import create_diff_prompt, create_branch_diff_prompt, create_branch_commit_message

@click.group()  # Делаем основную группу команд
def cli():
    """Генератор промтов для Git-изменений."""
    pass

@cli.command()
def diff():
    """Промт на основе git diff текущих изменений."""
    create_diff_prompt()


@cli.command()
@click.option("--since", default="master", help='Просмотр изменений с момента ответвления от указанной ветки')
def branch_diff(since: str):
    """Промт на основе git diff всей ветки."""
    create_branch_diff_prompt(since)

@cli.command()
@click.option("--since", default="master", help='Просмотр изменений с момента ответвления от указанной ветки')
def branch_comments(since: str):
    """Промт из всех комментариев коммитов ветки."""
    create_branch_commit_message(since)


if __name__ == "__main__":
    cli()