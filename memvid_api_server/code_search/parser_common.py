"""
Common tree-sitter parsing utilities for code extraction.

This module provides shared functionality for parsing source code using tree-sitter,
handling multiple languages, and extracting code definitions with various output formats.
"""

import json
import os
from pathlib import Path

import pathspec
from tree_sitter_language_pack import get_parser

from .language_definitions import EXTENSION_LANG_MAP


def get_language_for_file(filepath):
    """
    Determine the programming language associated with a given file based on its extension.

    Args:
        filepath (str or Path): The path to the file.

    Returns:
        str or None: The language identifier if recognized; otherwise, None.
    """

    ext = Path(filepath).suffix.lower()
    return EXTENSION_LANG_MAP.get(ext)


def get_snippet(src_lines, start, end):
    """
    Extract a snippet of code lines from the source lines between two tree-sitter node positions.

    Args:
        src_lines (list of str): List of all lines in the source file.
        start (Point): The start position (with row attribute) of a node.
        end (Point): The end position (with row attribute) of a node.

    Returns:
        str: The extracted code snippet as a string.
    """
    return "\n".join(src_lines[start.row : end.row + 1])


def get_context_block(src_lines, start_line, end_line, context_lines=10):
    """
    Extract code with surrounding context for LLM comprehension.

    Args:
        src_lines (list of str): All source code lines (0-indexed).
        start_line (int): Starting line (0-indexed).
        end_line (int): Ending line (0-indexed).
        context_lines (int): Number of lines before/after to include. Defaults to 10.

    Returns:
        tuple: (actual_start_line, actual_end_line, code_block)
    """
    context_start = max(0, start_line - context_lines)
    context_end = min(len(src_lines) - 1, end_line + context_lines)

    code_block = "\n".join(src_lines[context_start : context_end + 1])

    return context_start, context_end, code_block


def load_gitignore_patterns(root_dir):
    """
    Load and parse the .gitignore file at the root directory.

    Args:
        root_dir (str or Path): The root directory path.

    Returns:
        pathspec.PathSpec or None: The compiled gitignore patterns, or None if no .gitignore exists.
    """
    gitignore_path = Path(root_dir) / ".gitignore"
    if not gitignore_path.is_file():
        return None

    with open(gitignore_path, "r") as f:
        return pathspec.PathSpec.from_lines("gitwildmatch", f)


def visit_files(root_dir, skip_node_modules=True):
    """
    Recursively walk through the directory tree, yielding files with recognized source code extensions,
    while ignoring directories/files specified in .gitignore and explicit build directories.

    Args:
        root_dir (str): The path to the root directory to start walking.
        skip_node_modules (bool): Whether to skip node_modules directory. Defaults to True.

    Yields:
        str: Full paths to files eligible for parsing.
    """
    spec = load_gitignore_patterns(root_dir)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove build directories explicitly to avoid processing build artifacts
        if "target" in dirnames:
            dirnames.remove("target")
        if ".git" in dirnames:
            dirnames.remove(".git")
        if skip_node_modules and "node_modules" in dirnames:
            dirnames.remove("node_modules")

        # Filter out ignored directories per .gitignore
        if spec:
            ignored_dirs = [
                d
                for d in dirnames
                if spec.match_file(os.path.relpath(os.path.join(dirpath, d), root_dir))
            ]
            for d in ignored_dirs:
                dirnames.remove(d)

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)

            # Skip files ignored by .gitignore
            if spec and spec.match_file(rel_path):
                continue

            if get_language_for_file(filename):
                yield filepath


def get_parser_for_language(lang):
    """
    Get a tree-sitter parser for the specified language.

    Args:
        lang (str): Language identifier (e.g., 'python', 'typescript').

    Returns:
        Parser: A tree-sitter parser instance.
    """
    return get_parser(lang)


def parse_tree(src_code):
    """
    Internal helper to parse source code into a tree-sitter syntax tree.

    Args:
        src_code (str): Full source code.
        parser: Tree-sitter parser instance.

    Returns:
        tuple: (root_node, src_lines)
    """
    src_lines = src_code.splitlines()
    return src_lines


def extract_nodes_python(node, src_lines):
    """
    Recursively extract Python function and class definitions.

    Args:
        node: Tree-sitter node.
        src_lines: Source code lines.

    Yields:
        tuple: (node, item_type, name_node, docstring)
    """
    if node.type in ["function_definition", "class_definition"]:
        name_node = node.child_by_field_name("name")
        if name_node:
            item_type = "Class" if node.type == "class_definition" else "Function"
            yield (node, item_type, name_node)

    for child in node.children:
        yield from extract_nodes_python(child, src_lines)


def extract_nodes_javascript(node, src_lines):
    """
    Recursively extract JavaScript/TypeScript function, class, interface, and enum definitions.

    Args:
        node: Tree-sitter node.
        src_lines: Source code lines.

    Yields:
        tuple: (node, item_type, name_node)
    """
    handlers = {
        "function_declaration": ("Function", "name"),
        "class_declaration": ("Class", "name"),
        "method_definition": ("Method", "name"),
        "interface_declaration": ("Interface", "name"),
        "enum_declaration": ("Enum", "name"),
    }

    if node.type in handlers:
        item_type, field = handlers[node.type]
        name_node = node.child_by_field_name(field)
        if name_node:
            yield (node, item_type, name_node)

    for child in node.children:
        yield from extract_nodes_javascript(child, src_lines)


def extract_nodes_c_family(node, src_lines):
    """
    Recursively extract C/C++/C# function, struct, enum, and class definitions.

    Args:
        node: Tree-sitter node.
        src_lines: Source code lines.

    Yields:
        tuple: (node, item_type, name_node)
    """
    if node.type == "function_definition":
        declarator = node.child_by_field_name("declarator")
        if declarator:
            yield (node, "Function", declarator)
    elif node.type == "struct_specifier":
        name_node = node.child_by_field_name("name")
        if name_node:
            yield (node, "Struct", name_node)
    elif node.type == "enum_specifier":
        name_node = node.child_by_field_name("name")
        if name_node:
            yield (node, "Enum", name_node)
    elif node.type == "class_specifier":
        name_node = node.child_by_field_name("name")
        if name_node:
            yield (node, "Class", name_node)

    for child in node.children:
        yield from extract_nodes_c_family(child, src_lines)


def get_language_extractor(lang):
    """
    Get the appropriate node extractor function for a language.

    Args:
        lang (str): Language identifier.

    Returns:
        callable: A generator function that yields (node, item_type, name_node, ...).
    """
    if lang == "python":
        return extract_nodes_python
    elif lang in ("javascript", "typescript"):
        return extract_nodes_javascript
    elif lang in ("c", "cpp", "c_sharp"):
        return extract_nodes_c_family
    else:
        return None


def write_ndjson(filepath, items):
    """
    Write a list of dict items to a file in newline-delimited JSON format (JSON Lines).

    Args:
        filepath (str): The output file path.
        items (list): List of dictionary items to serialize.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        for item in items:
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + "\n")


def write_jsonl(filepath, items):
    """
    Write a list of dict items to a file in JSONL format (alias for write_ndjson).

    Args:
        filepath (str or Path): The output file path.
        items (list): List of dictionary items to serialize.
    """
    write_ndjson(filepath, items)
