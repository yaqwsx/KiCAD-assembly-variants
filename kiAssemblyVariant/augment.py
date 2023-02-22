from typing import Iterable, Dict
from pathlib import Path
from .sexpr import parseSexprF, Atom, SExpr, isElement
from .eeschema import extractComponents, Symbol
from pcbnewTransition import pcbnew

class AugmentationError(RuntimeError):
    pass

def augmentProject(project: Path, variantPrefix: str, fields: Iterable[str]) -> None:
    projectFile = locateProject(project)
    for f in project.iterdir():
        if f.suffix == ".kicad_sch":
            augmentSchematic(f, variantPrefix, fields)
    schFile = projectFile.with_suffix(".kicad_sch")
    brdFile = projectFile.with_suffix(".kicad_pcb")
    if not schFile.exists():
        raise AugmentationError(f"No schematics for project {projectFile}")
    if not brdFile.exists():
        raise AugmentationError(f"No board for project {projectFile}")
    symbols = extractComponents(schFile)
    board = pcbnew.LoadBoard(str(brdFile))
    updateBoard(board, symbols)
    board.Save(board.GetFileName())


def locateProject(project: Path) -> Path:
    projectFile = None
    for f in project.iterdir():
        if f.suffix == ".kicad_pro":
            projectFile = f
            break
    if projectFile is None:
        raise AugmentationError(f"No project in {project}")
    return projectFile

def augmentSchematic(schfile: Path, variantPrefix: str, fields: Iterable[str]) -> None:
    with open(schfile, encoding="utf-8") as f:
        sheetAst = parseSexprF(f)
    for node in sheetAst:
        if not isElement("symbol")(node):
            continue
        assert isinstance(node, SExpr)
        augmentSymbol(node, variantPrefix, fields)
    with open(schfile, "w", encoding="utf-8") as f:
        f.write(str(sheetAst))


def augmentSymbol(symbol: SExpr, variantPrefix: str, fields: Iterable[str]) -> None:
    attributes = {}
    # Collect attributes
    for node in symbol.items:
        if not isElement("property")(node):
            continue
        name = node.items[1].value
        splitName = name.split(" ")
        if len(splitName) != 2:
            continue
        if splitName[0] == variantPrefix and splitName[1] in fields:
            value = node.items[2].value
            attributes[splitName[1]] = value
    # Apply attributes
    for node in symbol.items:
        if not isElement("property")(node):
            continue
        name = node.items[1].value
        if name in attributes:
            node.items[2].value = attributes[name]


def updateBoard(board: pcbnew.BOARD, symbols: Iterable[Symbol]) -> None:
    symbolDict = {s.properties["Reference"]: s for s in symbols}
    for f in board.GetFootprints():
        symbol = symbolDict.get(f.GetReference(), None)
        if symbol is None:
            continue
        f.SetValue(symbol.properties.get("Value", ""))
