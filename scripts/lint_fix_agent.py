#!/usr/bin/env python3
"""
CLI agent that uses OpenAI to automatically fix flake8 lint issues.

Usage:
    python scripts/lint_fix_agent.py [--model MODEL] [--dry-run] [paths ...]

Requirements:
    pip install openai flake8

Environment:
    OPENAI_API_KEY  Your OpenAI API key (required)
"""

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package is not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


SYSTEM_PROMPT = (
    "You are an expert Python developer. "
    "You will be given a Python source file and a list of flake8 lint errors. "
    "Your task is to fix ALL reported lint errors and return ONLY the corrected file content, "
    "with no explanations, no markdown code fences, and no extra commentary. "
    "Preserve the original logic and formatting as much as possible."
)


def run_flake8(paths: list[str]) -> str:
    """Run flake8 and return its output."""
    cmd = ["flake8"] + paths
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def parse_flake8_output(output: str) -> dict[str, list[str]]:
    """Group flake8 errors by file path."""
    errors_by_file: dict[str, list[str]] = defaultdict(list)
    pattern = re.compile(r"^(.+?):\d+:\d+:\s+.+$")
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            filepath = match.group(1)
            errors_by_file[filepath].append(line)
    return dict(errors_by_file)


def fix_file_with_ai(client: OpenAI, model: str, filepath: str, errors: list[str]) -> str:
    """Ask the AI to fix lint errors in a file and return the corrected content."""
    source = Path(filepath).read_text(encoding="utf-8")
    error_block = "\n".join(errors)
    user_message = (
        f"File: {filepath}\n\n"
        f"Flake8 errors to fix:\n{error_block}\n\n"
        f"Source code:\n{source}"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("AI returned an empty response; no fixes applied.")
    return content


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-powered flake8 lint fixer using OpenAI."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to lint and fix (default: current directory)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing files",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print("Running flake8...")
    flake8_output = run_flake8(args.paths)

    if not flake8_output.strip():
        print("No lint errors found. Nothing to fix.")
        return

    errors_by_file = parse_flake8_output(flake8_output)
    print(f"Found lint errors in {len(errors_by_file)} file(s).\n")

    fixed_count = 0
    written_count = 0
    for filepath, errors in errors_by_file.items():
        print(f"  Fixing {filepath} ({len(errors)} error(s))...")
        for err in errors:
            print(f"    {err}")

        try:
            fixed_content = fix_file_with_ai(client, args.model, filepath, errors)
        except Exception as exc:
            print(f"    [ERROR] AI call failed for {filepath}: {exc}", file=sys.stderr)
            continue

        if args.dry_run:
            print(f"    [dry-run] Would overwrite {filepath}")
            fixed_count += 1
        else:
            try:
                Path(filepath).write_text(fixed_content, encoding="utf-8")
                print(f"    [OK] Written {filepath}")
                fixed_count += 1
                written_count += 1
            except OSError as exc:
                print(f"    [ERROR] Could not write {filepath}: {exc}", file=sys.stderr)

    if args.dry_run:
        print(f"\nDry-run complete. {fixed_count} file(s) would be modified.")
    else:
        print(f"\nDone. Fixed {written_count} file(s).")
        # Re-run flake8 to confirm
        remaining = run_flake8(args.paths)
        if remaining.strip():
            print("\nRemaining lint errors after fix:")
            print(remaining)
        else:
            print("All lint errors resolved.")


if __name__ == "__main__":
    main()
