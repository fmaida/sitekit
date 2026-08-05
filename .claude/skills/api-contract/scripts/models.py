"""
Modelli dati che rappresentano la superficie pubblica di un pacchetto Python.
"""

from dataclasses import dataclass, field


@dataclass
class ParameterInfo:
    """
    Descrive un singolo parametro di una funzione o di un metodo.
    """

    name: str
    annotation: str = ""
    default: str = ""
    prefix: str = ""


@dataclass
class FunctionInfo:
    """
    Descrive una funzione pubblica o un metodo pubblico di una classe.
    """

    name: str
    parameters: list[ParameterInfo] = field(default_factory=list)
    returns: str = ""
    docstring: str = ""
    is_async: bool = False
    is_property: bool = False
    is_static: bool = False
    is_classmethod: bool = False
    line: int = 0


@dataclass
class ClassInfo:
    """
    Descrive una classe pubblica e i suoi metodi pubblici.
    """

    name: str
    bases: list[str] = field(default_factory=list)
    docstring: str = ""
    methods: list[FunctionInfo] = field(default_factory=list)
    attributes: list[ParameterInfo] = field(default_factory=list)
    line: int = 0


@dataclass
class ConstantInfo:
    """
    Descrive una costante pubblica definita a livello di modulo.
    """

    name: str
    annotation: str = ""
    value: str = ""
    line: int = 0


@dataclass
class ModuleInfo:
    """
    Descrive un modulo Python e tutta la sua superficie pubblica.
    """

    dotted_name: str
    relative_path: str
    docstring: str = ""
    constants: list[ConstantInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    reexports: list[str] = field(default_factory=list)
    file_sha256: str = ""
    api_sha256: str = ""


@dataclass
class PackageInfo:
    """
    Descrive un intero pacchetto Poetry con i suoi moduli pubblici.
    """

    name: str
    version: str = ""
    description: str = ""
    root_path: str = ""
    modules: list[ModuleInfo] = field(default_factory=list)
