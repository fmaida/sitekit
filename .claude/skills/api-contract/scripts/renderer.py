"""
Trasforma la descrizione di un pacchetto nel documento markdown finale.
"""

import json
from datetime import date

from models import ClassInfo, FunctionInfo, ModuleInfo, PackageInfo


HEADER_NOTE = (
    "> **Documento generato automaticamente. Non modificarlo a mano.**\n"
    "> Descrive la sola superficie pubblica del pacchetto: firme, tipi e\n"
    "> docstring. Serve a un agente IA che lavora su un progetto *consumatore*\n"
    "> di questa libreria e ha bisogno di conoscerne il contratto attuale.\n"
    ">\n"
    "> Per le convenzioni di sviluppo interne al pacchetto vedi `CLAUDE.md`.\n"
)


def _format_signature(function: FunctionInfo) -> str:
    """
    Ricompone la firma testuale di una funzione o di un metodo.

    Args:
        function: Descrizione della funzione da formattare.

    Returns:
        La firma completa, comprensiva di annotazioni e valori di default.
    """
    parts: list[str] = []
    for parameter in function.parameters:
        text = f"{parameter.prefix}{parameter.name}"
        if parameter.annotation:
            text = f"{text}: {parameter.annotation}"
        if parameter.default:
            text = f"{text} = {parameter.default}"
        parts.append(text)

    prefix = ""
    if function.is_async:
        prefix = "async "

    returns = ""
    if function.returns:
        returns = f" -> {function.returns}"

    return f"{prefix}def {function.name}({', '.join(parts)}){returns}"


def _render_docstring(docstring: str, indent: str = "") -> list[str]:
    """
    Prepara la docstring per l'inserimento nel documento markdown.

    Args:
        docstring: Testo grezzo della docstring.
        indent: Prefisso di indentazione da applicare a ogni riga.

    Returns:
        Le righe markdown corrispondenti, vuote se la docstring manca.
    """
    if not docstring.strip():
        return []

    lines: list[str] = []
    for line in docstring.strip().splitlines():
        lines.append(f"{indent}{line}".rstrip())

    return lines


def _render_function(function: FunctionInfo, indent: str = "") -> list[str]:
    """
    Rende una funzione pubblica come blocco markdown.

    Args:
        function: Descrizione della funzione da rendere.
        indent: Prefisso di indentazione per i blocchi annidati.

    Returns:
        Le righe markdown che descrivono la funzione.
    """
    markers: list[str] = []
    if function.is_property:
        markers.append("property")
    if function.is_static:
        markers.append("staticmethod")
    if function.is_classmethod:
        markers.append("classmethod")

    suffix = ""
    if markers:
        suffix = f" *({', '.join(markers)})*"

    lines = [f"{indent}```python", f"{indent}{_format_signature(function)}"]
    lines.append(f"{indent}```")
    if suffix:
        lines.append(f"{indent}{suffix.strip()}")

    body = _render_docstring(function.docstring, indent)
    if body:
        lines.append("")
        lines.extend(body)
    lines.append("")

    return lines


def _render_class(klass: ClassInfo) -> list[str]:
    """
    Rende una classe pubblica e i suoi membri come blocco markdown.

    Args:
        klass: Descrizione della classe da rendere.

    Returns:
        Le righe markdown che descrivono la classe.
    """
    bases = ""
    if klass.bases:
        bases = f"({', '.join(klass.bases)})"

    lines = [f"### `class {klass.name}{bases}`", ""]
    body = _render_docstring(klass.docstring)
    if body:
        lines.extend(body)
        lines.append("")

    if klass.attributes:
        lines.append("**Attributi**")
        lines.append("")
        for attribute in klass.attributes:
            text = f"- `{attribute.name}: {attribute.annotation}`"
            if attribute.default:
                text = f"{text} = `{attribute.default}`"
            lines.append(text)
        lines.append("")

    if klass.methods:
        lines.append("**Metodi**")
        lines.append("")
        for method in klass.methods:
            lines.extend(_render_function(method))

    return lines


def _render_module(module: ModuleInfo) -> list[str]:
    """
    Rende un modulo completo come sezione markdown.

    Args:
        module: Descrizione del modulo da rendere.

    Returns:
        Le righe markdown che descrivono il modulo.
    """
    lines = [f"## `{module.dotted_name}`", ""]
    lines.append(f"File: `{module.relative_path}`")
    lines.append("")
    lines.append(f"- `api_sha256`: `{module.api_sha256}`")
    lines.append(f"- `file_sha256`: `{module.file_sha256}`")
    lines.append("")

    body = _render_docstring(module.docstring)
    if body:
        lines.extend(body)
        lines.append("")

    if module.exports:
        exported = ", ".join(f"`{name}`" for name in module.exports)
        lines.append(f"`__all__`: {exported}")
        lines.append("")

    if module.reexports:
        lines.append("**Nomi riesposti da questo package**")
        lines.append("")
        for name in module.reexports:
            lines.append(f"- `{name}`")
        lines.append("")

    if module.constants:
        lines.append("**Costanti**")
        lines.append("")
        for constant in module.constants:
            declaration = constant.name
            if constant.annotation:
                declaration = f"{declaration}: {constant.annotation}"
            lines.append(f"- `{declaration}` = `{constant.value}`")
        lines.append("")

    if module.functions:
        lines.append("**Funzioni**")
        lines.append("")
        for function in module.functions:
            lines.extend(_render_function(function))

    for klass in module.classes:
        lines.extend(_render_class(klass))

    return lines


def build_manifest(package: PackageInfo) -> dict:
    """
    Costruisce il manifesto delle impronte in forma leggibile da macchina.

    Args:
        package: Descrizione del pacchetto analizzato.

    Returns:
        Un dizionario con le impronte di ogni modulo, pronto per il JSON.
    """
    modules = {}
    for module in package.modules:
        modules[module.dotted_name] = {
            "path": module.relative_path,
            "file_sha256": module.file_sha256,
            "api_sha256": module.api_sha256,
        }

    return {
        "package": package.name,
        "version": package.version,
        "generated": date.today().isoformat(),
        "modules": modules,
    }


def render(package: PackageInfo, model_name: str) -> str:
    """
    Produce il documento markdown completo del contratto pubblico.

    Args:
        package: Descrizione del pacchetto analizzato.
        model_name: Nome del modello che sta generando il documento.

    Returns:
        Il testo markdown pronto per essere scritto su file.
    """
    lines = [f"# API Contract — `{package.name}`", ""]
    lines.append(HEADER_NOTE)
    lines.append("")

    if package.description:
        lines.append(package.description)
        lines.append("")

    if package.version:
        lines.append(f"Versione documentata: **{package.version}**")
        lines.append("")

    lines.append("## Verifica di validita'")
    lines.append("")
    lines.append(
        "Prima di fidarti di questo documento, esegui il controllo di deriva:"
    )
    lines.append("")
    lines.append("```bash")
    lines.append('python3 "${CLAUDE_SKILL_DIR}/scripts/generate_contract.py" \\')
    lines.append("    . --check")
    lines.append("```")
    lines.append("")
    lines.append(
        "Se un modulo risulta *disallineato*, il documento non descrive piu' il "
        "codice: leggi il sorgente di quel modulo e rigenera il contratto."
    )
    lines.append(
        "Un `api_sha256` invariato con `file_sha256` diverso significa che sono "
        "cambiati solo dettagli interni: il contratto pubblico regge."
    )
    lines.append("")

    lines.append("## Indice dei moduli")
    lines.append("")
    lines.append("| Modulo | api_sha256 | file_sha256 |")
    lines.append("| --- | --- | --- |")
    for module in package.modules:
        lines.append(
            f"| `{module.dotted_name}` | `{module.api_sha256[:16]}` "
            f"| `{module.file_sha256[:16]}` |"
        )
    lines.append("")

    for module in package.modules:
        lines.extend(_render_module(module))

    lines.append("## Manifesto impronte")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(build_manifest(package), indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")

    lines.append("## Metadata")
    lines.append(f"- Ultima modifica: {date.today().isoformat()}")
    lines.append(f"- Modello: {model_name}")
    lines.append("")

    return "\n".join(lines)
