import click
import shutil
from pathlib import Path
from . import __version__

@click.command()
@click.argument("projectdir", type=click.Path(dir_okay=True, file_okay=False, exists=True))
@click.option("-p", "--prefix", type=str,
    help="Assembly variant prefix")
@click.option("-f", "--field", type=str, multiple=True,
    help="Fields to switch")
def switch(projectdir, prefix, field):
    """
    Change assembly variant of a project in place
    """
    from .augment import augmentProject
    augmentProject(Path(projectdir), prefix, field)


@click.command()
@click.argument("projectdir", type=click.Path(dir_okay=True, file_okay=False, exists=True))
@click.argument("destdir", type=click.Path(dir_okay=True, file_okay=False))
@click.option("-p", "--prefix", type=str, multiple=True,
    help="Assembly variant prefix")
@click.option("-f", "--field", type=str, multiple=True,
    help="Fields to switch")
def export(projectdir, destdir, prefix, field):
    """
    Export project in multiple assembly variants into a dedicated directory
    """
    from .augment import augmentProject
    for p in prefix:
        dest = Path(destdir) / p
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(projectdir, dest, dirs_exist_ok=True)
        augmentProject(dest, p, field)


@click.group()
@click.version_option(__version__)
def cli():
    """
    Manipulate assembly variants
    """
    pass


cli.add_command(switch)
cli.add_command(export)

if __name__ == "__main__":
    cli()
