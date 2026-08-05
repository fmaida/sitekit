"""
Estrae la superficie pubblica di moduli Python analizzandone l'AST.

L'analisi e' statica: i moduli non vengono mai importati, quindi non serve
installare le loro dipendenze e non viene eseguito alcun codice.
"""

import ast
from pathlib import Path

from models import (
    ClassInfo,
    ConstantInfo,
    FunctionInfo,
    ModuleInfo,
    ParameterInfo,
)


DUNDER_KEEP = {"__init__", "__call__", "__enter__", "__exit__", "__iter__"}


def _unparse(node: ast.AST | None) -> str:
    """
    Converte un nodo AST nella sua rappresentazione testuale.

    Args:
        node: Nodo da convertire, oppure None.

    Returns:
        Il codice sorgente equivalente al nodo, stringa vuota se None.
    """
    if node is None:
        return ""

    return ast.unparse(node)


def _is_public(name: str) -> bool:
    """
    Stabilisce se un identificatore fa parte della superficie pubblica.

    Args:
        name: Nome dell'identificatore da valutare.

    Returns:
        True se il nome e' pubblico secondo le convenzioni Python.
    """
    if name in DUNDER_KEEP:
        return True

    return not name.startswith("_")


def _build_parameters(args: ast.arguments) -> list[ParameterInfo]:
    """
    Ricostruisce l'elenco ordinato dei parametri di una funzione.

    Args:
        args: Nodo `arguments` prodotto dal parser AST.

    Returns:
        Lista di ParameterInfo nell'ordine in cui compaiono nella firma.
    """
    parameters: list[ParameterInfo] = []
    positional = list(args.posonlyargs) + list(args.args)
    padding = len(positional) - len(args.defaults)

    for index, argument in enumerate(positional):
        default = ""
        if index >= padding:
            default = _unparse(args.defaults[index - padding])
        parameters.append(
            ParameterInfo(
                name=argument.arg,
                annotation=_unparse(argument.annotation),
                default=default,
            )
        )

    if args.vararg is not None:
        parameters.append(
            ParameterInfo(
                name=args.vararg.arg,
                annotation=_unparse(args.vararg.annotation),
                prefix="*",
            )
        )

    for argument, node in zip(args.kwonlyargs, args.kw_defaults):
        parameters.append(
            ParameterInfo(
                name=argument.arg,
                annotation=_unparse(argument.annotation),
                default=_unparse(node),
            )
        )

    if args.kwarg is not None:
        parameters.append(
            ParameterInfo(
                name=args.kwarg.arg,
                annotation=_unparse(args.kwarg.annotation),
                prefix="**",
            )
        )

    return parameters


def _decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """
    Raccoglie i nomi dei decoratori applicati a una funzione.

    Args:
        node: Nodo della funzione o del metodo.

    Returns:
        Insieme dei nomi dei decoratori, senza argomenti di chiamata.
    """
    names: set[str] = set()
    for decorator in node.decorator_list:
        text = _unparse(decorator)
        names.add(text.split("(")[0].split(".")[-1])

    return names


def _build_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> FunctionInfo:
    """
    Costruisce la descrizione di una funzione o di un metodo pubblico.

    Args:
        node: Nodo della funzione da descrivere.

    Returns:
        Un FunctionInfo completo di firma, tipo di ritorno e docstring.
    """
    decorators = _decorator_names(node)

    return FunctionInfo(
        name=node.name,
        parameters=_build_parameters(node.args),
        returns=_unparse(node.returns),
        docstring=ast.get_docstring(node) or "",
        is_async=isinstance(node, ast.AsyncFunctionDef),
        is_property=("property" in decorators or "cached_property" in decorators),
        is_static="staticmethod" in decorators,
        is_classmethod="classmethod" in decorators,
        line=node.lineno,
    )


def _build_class(node: ast.ClassDef) -> ClassInfo:
    """
    Costruisce la descrizione di una classe pubblica.

    Args:
        node: Nodo della classe da descrivere.

    Returns:
        Un ClassInfo con metodi pubblici e attributi annotati.
    """
    info = ClassInfo(
        name=node.name,
        bases=[_unparse(base) for base in node.bases],
        docstring=ast.get_docstring(node) or "",
        line=node.lineno,
    )

    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_public(child.name):
                info.methods.append(_build_function(child))
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            if _is_public(child.target.id):
                info.attributes.append(
                    ParameterInfo(
                        name=child.target.id,
                        annotation=_unparse(child.annotation),
                        default=_unparse(child.value),
                    )
                )

    return info


def _read_exports(tree: ast.Module) -> list[str]:
    """
    Legge il contenuto di `__all__` se il modulo lo dichiara.

    Args:
        tree: AST del modulo da ispezionare.

    Returns:
        Lista dei nomi esportati, vuota se `__all__` non e' presente.
    """
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                if isinstance(node.value, (ast.List, ast.Tuple)):
                    return [
                        element.value
                        for element in node.value.elts
                        if isinstance(element, ast.Constant)
                        and isinstance(element.value, str)
                    ]

    return []


def _collect_reexports(info: ModuleInfo, node: ast.ImportFrom) -> None:
    """
    Registra i nomi che un `__init__.py` riespone come API pubblica.

    Args:
        info: Descrizione del modulo da arricchire sul posto.
        node: Nodo `from ... import ...` incontrato a livello di modulo.
    """
    origin = node.module or ""
    for alias in node.names:
        exposed = alias.asname or alias.name
        if _is_public(exposed):
            info.reexports.append(f"{exposed} (da {origin})")


def extract_module(path: Path, root: Path, dotted_name: str) -> ModuleInfo:
    """
    Analizza un file Python e ne estrae l'intera superficie pubblica.

    Args:
        path: Percorso del file sorgente da analizzare.
        root: Radice del progetto, usata per il percorso relativo.
        dotted_name: Nome del modulo in notazione puntata.

    Returns:
        Un ModuleInfo popolato con costanti, funzioni e classi pubbliche.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    exports = _read_exports(tree)

    info = ModuleInfo(
        dotted_name=dotted_name,
        relative_path=str(path.relative_to(root)),
        docstring=ast.get_docstring(tree) or "",
        exports=exports,
    )

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if path.name == "__init__.py":
                _collect_reexports(info, node)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_public(node.name):
                info.functions.append(_build_function(node))
        elif isinstance(node, ast.ClassDef):
            if _is_public(node.name):
                info.classes.append(_build_class(node))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if _is_public(node.target.id) and node.target.id.isupper():
                info.constants.append(
                    ConstantInfo(
                        name=node.target.id,
                        annotation=_unparse(node.annotation),
                        value=_unparse(node.value),
                        line=node.lineno,
                    )
                )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                if _is_public(target.id) and target.id.isupper():
                    info.constants.append(
                        ConstantInfo(
                            name=target.id,
                            value=_unparse(node.value),
                            line=node.lineno,
                        )
                    )

    if exports:
        _filter_by_exports(info, exports)

    return info


def _filter_by_exports(info: ModuleInfo, exports: list[str]) -> None:
    """
    Restringe la superficie pubblica ai soli nomi dichiarati in `__all__`.

    Args:
        info: Descrizione del modulo da filtrare sul posto.
        exports: Nomi dichiarati esplicitamente come pubblici.
    """
    allowed = set(exports)
    info.functions = [item for item in info.functions if item.name in allowed]
    info.classes = [item for item in info.classes if item.name in allowed]
    info.constants = [item for item in info.constants if item.name in allowed]
