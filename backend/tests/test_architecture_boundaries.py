"""Executable guards for the architectural rules.

`lint-imports` checks these statically from pyproject.toml. These tests catch
the same violations from a plain `pytest` run, so a broken boundary fails the
normal test suite too.
"""

from __future__ import annotations

import ast
import pathlib

BACKEND = pathlib.Path(__file__).resolve().parents[1]


def _imported_modules(package: str) -> dict[pathlib.Path, set[str]]:
    """Every absolute module name imported by each file in a package."""
    result: dict[pathlib.Path, set[str]] = {}
    for path in (BACKEND / package).rglob("*.py"):
        if "migrations" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module)
        result[path.relative_to(BACKEND)] = names
    return result


def _violations(package: str, forbidden: tuple[str, ...]) -> list[str]:
    found = []
    for path, names in _imported_modules(package).items():
        for name in names:
            if any(name == f or name.startswith(f + ".") for f in forbidden):
                found.append(f"{path} imports {name}")
    return found


def test_core_imports_nothing_from_the_project():
    """core is domain-neutral: it cannot know apps, services or config exist."""
    assert _violations("core", ("apps", "services", "config")) == []


def test_apps_never_import_concrete_provider_code():
    """apps reach implementations through core.contracts, never directly."""
    assert _violations("apps", ("services",)) == []


def test_services_contain_no_business_domain_knowledge():
    """A service adapter must be meaningless outside this contract."""
    assert _violations("services", ("apps", "config")) == []


def test_no_generic_dumping_grounds_exist():
    """Every function has a named owner; utils.py is not a name."""
    banned = {"utils.py", "helpers.py", "common.py", "misc.py"}
    offenders = [
        str(path.relative_to(BACKEND))
        for package in ("core", "apps", "services", "config")
        for path in (BACKEND / package).rglob("*.py")
        if path.name in banned
    ]
    assert offenders == []
