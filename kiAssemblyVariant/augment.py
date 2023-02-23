from typing import Iterable, Dict
from pathlib import Path
from .sexpr import parseSexprF, Atom, SExpr, isElement
from .eeschema import extractComponents, Symbol
from pcbnewTransition import pcbnew

class AugmentationError(RuntimeError):
    pass

def augmentProject(project: Path, variantPrefix: str) -> None:
    projectFile = locateProject(project)
    for f in project.iterdir():
        if f.suffix == ".kicad_sch":
            augmentSchematic(f, variantPrefix)
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

def augmentSchematic(schfile: Path, variantPrefix: str) -> None:
    with open(schfile, encoding="utf-8") as f:
        sheetAst = parseSexprF(f)
    for node in sheetAst:
        if not isElement("symbol")(node):
            continue
        assert isinstance(node, SExpr)
        augmentSymbol(node, variantPrefix)
    with open(schfile, "w", encoding="utf-8") as f:
        f.write(str(sheetAst))

def interpretAsYesNo(value: str) -> str:
    YES_VALS = set(["yes", "ano", "1", "true"])
    NO_VALS = set(["no", "ne", "0", "false"])
    lower = value.lower()
    if lower in YES_VALS:
        return "yes"
    if lower in NO_VALS:
        return "no"
    raise AugmentationError(f"Cannot interpret {value} as yes/no")


def augmentSymbol(symbol: SExpr, variantPrefix: str) -> None:
    attributes = {}
    positionNode = None
    lastPropertyIndex = None
    # Collect attributes
    for i, node in enumerate(symbol.items):
        if isElement("at")(node):
            positionNode = node
            continue
        if not isElement("property")(node):
            continue
        lastPropertyIndex = i
        name = node.items[1].value
        splitName = name.split(" ")
        if len(splitName) != 2:
            continue
        if splitName[0] == variantPrefix:
            value = node.items[2].value
            if value.strip() != "":
                attributes[splitName[1]] = value

    # Apply attributes
    applied = set()
    for node in symbol.items:
        if not isElement("property")(node):
            continue
        name = node.items[1].value
        if name in attributes:
            node.items[2].value = attributes[name]
            applied.add(name)

    # Apply special attributes
    for special in ["in_bom", "on_board", "dnp"]:
        if special not in attributes:
            continue
        for node in symbol.items:
            if not isElement(special)(node):
                continue
            node.items[1].value = interpretAsYesNo(attributes[special])
            applied.add(special)
            break

    # Place non-existent fields
    for attribute in set(attributes.keys()).difference(applied):
        newNode = SExpr([
            Atom("property"),
            Atom(attribute, leadingWhitespace=" ", quoted=True),
            Atom(attributes[attribute], leadingWhitespace=" ", quoted=True),
            positionNode,
            SExpr([
                Atom("effects"),
                SExpr([
                    Atom("font"),
                    SExpr([
                        Atom("size"),
                        Atom("1.27", leadingWhitespace=" "),
                        Atom("1.27", leadingWhitespace=" ")
                    ], leadingWhitespace=" ")
                ], leadingWhitespace=" "),
                Atom("hide", leadingWhitespace=" ")
            ], leadingWhitespace="\n      "),
        ], leadingWhitespace="\n    ",  trailingWhitespace="\n    ")
        symbol.items.insert(lastPropertyIndex + 1, newNode)


def updateBoard(board: pcbnew.BOARD, symbols: Iterable[Symbol]) -> None:
    symbolDict = {s.properties["Reference"]: s for s in symbols}
    for f in board.GetFootprints():
        symbol = symbolDict.get(f.GetReference(), None)
        if symbol is None:
            continue
        f.SetValue(symbol.properties.get("Value", ""))
