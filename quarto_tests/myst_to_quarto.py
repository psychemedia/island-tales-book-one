#!/usr/bin/env python3
"""
MyST Markdown to Quarto Markdown Converter

Converts .md files with MyST syntax to .qmd files with Quarto syntax.
Handles admonitions, raw LaTeX blocks, YAML front matter, and other MyST-specific syntax.

Usage:
    python myst_to_quarto.py /path/to/directory
    python myst_to_quarto.py /path/to/directory --dry-run
    python myst_to_quarto.py /path/to/directory --backup
"""

import argparse
import os
import re
import shutil
from pathlib import Path
from typing import List


def convert_yaml_frontmatter(content: str) -> str:
    """Convert MyST YAML front matter to Quarto equivalents."""
    # Convert numbering: false to number: false
    content = re.sub(
        r"^numbering:\s*false", "number: false", content, flags=re.MULTILINE
    )
    # Remove exclude_patterns (Quarto handles differently or not needed)
    content = re.sub(r"^exclude_patterns:.*", "", content, flags=re.MULTILINE)
    # Clean up any double newlines created by removals
    content = re.sub(r"\n\n\n+", "\n\n", content)
    return content


def convert_admonitions(content: str) -> str:
    """Convert MyST admonitions to Quarto callouts."""
    # Admonitions with title and classes
    pattern = r"```{admonition}\s+([^\n]+)\n:class:\s+([^\n]+)\n\n(.*?)\n```"

    def replace_admonition(match):
        title = match.group(1).strip()
        classes = match.group(2).strip().split()
        body = match.group(3)
        callout_type = "note"
        attributes = [f'title="{title}"']

        if "dropdown" in classes:
            attributes.append('collapse="true"')
        if "seealso" in classes:
            attributes.append('appearance="simple"')
        if "tip" in classes:
            callout_type = "tip"
        if "warning" in classes:
            callout_type = "warning"
        if "important" in classes:
            callout_type = "important"
        if "caution" in classes:
            callout_type = "caution"

        attrs_str = " ".join(attributes)
        return f":::{{.callout-{callout_type} {attrs_str}}}\n{body}\n:::"

    content = re.sub(pattern, replace_admonition, content, flags=re.DOTALL)

    # Simple admonitions without classes
    simple_patterns = {
        r"```{note}\n(.*?)\n```": r":::{.callout-note}\n\1\n:::",
        r"```{warning}\n(.*?)\n```": r":::{.callout-warning}\n\1\n:::",
        r"```{tip}\n(.*?)\n```": r":::{.callout-tip}\n\1\n:::",
        r"```{important}\n(.*?)\n```": r":::{.callout-important}\n\1\n:::",
        r"```{caution}\n(.*?)\n```": r":::{.callout-caution}\n\1\n:::",
    }
    for pattern, repl in simple_patterns.items():
        content = re.sub(pattern, repl, content, flags=re.DOTALL)

    # Admonitions with titles but no classes
    titled_pattern = r"```{(note|warning|tip|important|caution)}\s+([^\n]+)\n(.*?)\n```"

    def replace_titled(match):
        adm_type = match.group(1)
        title = match.group(2).strip()
        body = match.group(3)
        return f':::{{.callout-{adm_type} title="{title}"}}\n{body}\n:::'

    content = re.sub(titled_pattern, replace_titled, content, flags=re.DOTALL)

    return content


def convert_raw_latex(content: str) -> str:
    """Convert MyST raw LaTeX blocks to Quarto format."""
    pattern = r"```{raw}\s+latex\n(.*?)\n```"
    return re.sub(pattern, r"```{=latex}\n\1\n```", content, flags=re.DOTALL)


def convert_myst_images(content: str) -> str:
    """Convert MyST image blocks to Quarto format."""
    pattern = r"```{image}\s+([^\n]+)\n((?::[^:]+:.*\n)*?)```"

    def replace_image(match):
        image_path = match.group(1).strip()
        options_block = match.group(2).strip()

        # Parse options
        alt_text = ""
        attributes = []

        for line in options_block.split("\n"):
            line = line.strip()
            if line.startswith(":alt:"):
                alt_text = line.replace(":alt:", "").strip()
            elif line.startswith(":align:"):
                align_value = line.replace(":align:", "").strip()
                attributes.append(f'fig-align="{align_value}"')
            elif line.startswith(":width:"):
                width_value = line.replace(":width:", "").strip()
                attributes.append(f'width="{width_value}"')
            elif line.startswith(":height:"):
                height_value = line.replace(":height:", "").strip()
                attributes.append(f'height="{height_value}"')

        # Build Quarto format
        quarto_image = f"![{alt_text}]({image_path})"
        if attributes:
            attr_string = " ".join(attributes)
            quarto_image += f"{{{attr_string}}}"

        return quarto_image

    return re.sub(pattern, replace_image, content, flags=re.DOTALL)



def convert_math_blocks(content: str) -> str:
    """Placeholder for math-specific conversions if needed."""
    return content


def convert_pagebreaks(content: str) -> str:
    """Convert MyST inline '$\\pagebreak$' into Quarto pagebreak block."""
    pattern = r"\$\s*\\pagebreak\s*\$"
    return re.sub(pattern, "::: {pagebreak}\n:::", content)


def convert_directives(content: str) -> str:
    """Convert other MyST directives to Quarto equivalents."""
    # Add more conversions here if needed
    return content


def convert_file_content(content: str) -> str:
    """Apply all MyST to Quarto conversions."""
    content = convert_yaml_frontmatter(content)
    content = convert_admonitions(content)
    content = convert_raw_latex(content)
    content = convert_myst_images(content)
    content = convert_pagebreaks(content)
    content = convert_math_blocks(content)
    content = convert_directives(content)
    return content


def find_md_files(directory: Path) -> List[Path]:
    """Find all .md files in directory and subdirectories."""
    return [
        Path(root) / file
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith(".md")
    ]


def convert_file(md_file: Path, backup: bool = False, dry_run: bool = False) -> bool:
    """Convert a single .md file to .qmd format."""
    print(f"Processing: {md_file}")
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            original_content = f.read()

        converted_content = convert_file_content(original_content)
        qmd_file = md_file.with_suffix(".qmd")

        if dry_run:
            print(f"  Would create: {qmd_file}")
            return True

        if backup:
            backup_file = md_file.with_suffix(".md.bak")
            shutil.copy2(md_file, backup_file)
            print(f"  Backup created: {backup_file}")

        with open(qmd_file, "w", encoding="utf-8") as f:
            f.write(converted_content)

        print(f"  Created: {qmd_file}")
        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert MyST Markdown files to Quarto Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python myst_to_quarto.py ./my-book-dir
    python myst_to_quarto.py ./my-book-dir --dry-run
    python myst_to_quarto.py ./my-book-dir --backup
        """,
    )
    parser.add_argument("directory", type=str, help="Directory to search for .md files")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be converted"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create .md.bak backup files before conversion",
    )
    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.exists() or not directory.is_dir():
        print(f"ERROR: '{directory}' is not a valid directory")
        return 1

    md_files = find_md_files(directory)
    if not md_files:
        print("No .md files found")
        return 0

    if args.dry_run:
        print("\n=== DRY RUN MODE - No files will be modified ===\n")

    success_count = 0
    for md_file in md_files:
        if convert_file(md_file, backup=args.backup, dry_run=args.dry_run):
            success_count += 1
        print()

    print(
        f"Conversion complete: {success_count}/{len(md_files)} files processed successfully"
    )
    if not args.dry_run:
        print("\nNext steps:")
        print("1. Review the generated .qmd files")
        print("2. Test your Quarto build: quarto render")
        print("3. If satisfied, you can remove the original .md files")
    return 0


if __name__ == "__main__":
    exit(main())
