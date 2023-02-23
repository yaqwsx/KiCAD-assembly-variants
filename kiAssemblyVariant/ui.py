import click
import shutil
from pathlib import Path
from . import __version__

def copyKiCADProject(srcPath: Path, dstPath: Path) -> None:
    for f in srcPath.iterdir():
        if f.suffix.startswith(".kicad_") or f.name in ["fp-lib-table", "sym-lib-table"]:
            shutil.copy2(f, dstPath)

@click.command()
@click.argument("projectdir", type=click.Path(dir_okay=True, file_okay=False, exists=True))
@click.option("-p", "--prefix", type=str,
    help="Assembly variant prefix")
def switch(projectdir, prefix):
    """
    Change assembly variant of a project in place
    """
    from .augment import augmentProject
    augmentProject(Path(projectdir), prefix)


@click.command()
@click.argument("projectdir", type=click.Path(dir_okay=True, file_okay=False, exists=True))
@click.argument("destdir", type=click.Path(dir_okay=True, file_okay=False))
@click.option("-p", "--prefix", type=str, multiple=True,
    help="Assembly variant prefix")
def export(projectdir, destdir, prefix):
    """
    Export project in multiple assembly variants into a dedicated directory
    """
    from .augment import augmentProject
    for p in prefix:
        dest = Path(destdir) / p
        dest.mkdir(parents=True, exist_ok=True)
        copyKiCADProject(Path(projectdir), dest)
        augmentProject(dest, p)


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
