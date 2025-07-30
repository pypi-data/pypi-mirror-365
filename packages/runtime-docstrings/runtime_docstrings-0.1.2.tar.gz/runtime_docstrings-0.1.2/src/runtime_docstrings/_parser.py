from __future__ import annotations


import dataclasses
import inspect

import warnings
from textwrap import dedent
import ast
import types
from enum import Enum


def _parse_docstrings(node: ast.ClassDef) -> dict[str, str]:
    docs: dict[str, str] = {}
    body = node.body
    for index in range(len(body) - 1):
        match body[index]:
            case ast.AnnAssign(target=ast.Name(id=name)):
                pass
            case ast.Assign(targets=[ast.Name(id=name)]):
                pass
            case _:
                continue

        match body[index + 1]:
            case ast.Expr(value=ast.Constant(value=doc_str)) if isinstance(
                doc_str, str
            ):
                docs[name] = inspect.cleandoc(doc_str)
    return docs


def get_docstrings(cls: type) -> dict[str, str]:
    """Parse and return a mapping of attribute names to their docstrings for a given class.

    Args:
        cls: The class to parse attribute docstrings from.

    Returns:
        A dictionary where keys are attribute names and values are their
        corresponding docstrings.
    """
    if "__attribute_docs__" in cls.__dict__:
        return cls.__attribute_docs__
    source = dedent(inspect.getsource(cls))
    tree = ast.parse(source)
    node = tree.body[0]
    assert isinstance(node, ast.ClassDef)
    # only process top-level class definition (no NodeVisitor recursion)
    docs = _parse_docstrings(node)
    # IDE style (no MRO resolution)
    cls.__attribute_docs__ = docs
    return docs


def _attach_class(cls: type, comments: dict[str, str]) -> None:
    for name, docstring in comments.items():
        setattr(cls, f"__doc_{name}__", docstring)


def _attach_dataclass(cls: type, comments: dict[str, str]) -> None:
    for field in dataclasses.fields(cls):
        field.metadata = types.MappingProxyType(
            {"__doc__": comments.get(field.name), **field.metadata}
        )


def _attach_enum(cls: type[Enum], comments: dict[str, str]) -> None:
    # enum members (canonical)
    for member in cls:
        member.__doc__ = comments.get(member.name)

    # enum alias members
    for name, member in cls.__members__.items():
        canonical_name = member.name
        if name != canonical_name and name in comments:
            warnings.warn(
                f"Enum alias member {cls.__name__}.{name} has docstring that should be documented on {cls.__name__}.{canonical_name}"
            )
            if canonical_name not in comments:
                member.__doc__ = comments[name]


def docstrings(cls: type) -> type:
    """Decorator that attaches attribute/member docstrings to a class.

    If the class is an enum, docstrings are attached via enum members.

    If the class is a dataclass, docstrings are attached via field metadata.

    Parameters:
        cls: The class to process.
    Returns:
        The same class with attached docstrings.
    """
    assert inspect.isclass(cls), "cls must be a class"

    # Extract docstrings from the class definition
    comments = get_docstrings(cls)
    if not comments:
        return cls

    _attach_class(cls, comments)

    if issubclass(cls, Enum):
        _attach_enum(cls, comments)
    elif dataclasses.is_dataclass(cls):
        _attach_dataclass(cls, comments)

    return cls
