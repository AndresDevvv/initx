from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import textwrap
import venv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="initx",
        description="Bootstrap a new app directory.",
    )
    subparsers = parser.add_subparsers(dest="platform")

    python_parser = subparsers.add_parser(
        "python",
        help="Create a starter Python app.",
    )
    python_parser.add_argument("name", help="Project directory name.")
    python_parser.add_argument(
        "--path",
        default=".",
        help="Directory where the new project folder should be created.",
    )
    python_parser.add_argument(
        "--no-venv",
        action="store_true",
        help="Skip creation of the local virtual environment.",
    )

    node_parser = subparsers.add_parser(
        "node",
        help="Create a starter Node.js app.",
    )
    node_parser.add_argument("name", help="Project directory name.")
    node_parser.add_argument(
        "--path",
        default=".",
        help="Directory where the new project folder should be created.",
    )
    return parser


def create_project_dir(name: str, base_path: str | Path = ".") -> Path:
    root = Path(base_path).expanduser().resolve()
    if name == ".":
        project_dir = root
        if project_dir.exists():
            if not project_dir.is_dir():
                raise FileExistsError(f"Refusing to overwrite existing path: {project_dir}")
            if any(project_dir.iterdir()):
                raise FileExistsError(f"Refusing to initialize non-empty directory: {project_dir}")
        else:
            project_dir.mkdir(parents=True)
        return project_dir

    project_dir = root / name
    if project_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing path: {project_dir}")

    project_dir.mkdir(parents=True)

    return project_dir


def resolve_command(*candidates: str) -> str | None:
    for candidate in candidates:
        if shutil.which(candidate):
            return candidate
    return None


def require_command(*candidates: str) -> str:
    command = resolve_command(*candidates)
    if command is None:
        joined = ", ".join(candidates)
        raise RuntimeError(f"Missing required command. Tried: {joined}")
    return command


def create_python_project(name: str, base_path: str | Path = ".", create_venv: bool = True) -> Path:
    python_cmd = require_command("python3", "python")
    project_dir = create_project_dir(name, base_path)

    write_file(
        project_dir / "main.py",
        textwrap.dedent(
            f"""\
            def main() -> None:
                print("Hello from {name}!")


            if __name__ == "__main__":
                main()
            """
        ),
    )
    write_file(project_dir / "requirements.txt", "")
    write_file(
        project_dir / ".gitignore",
        textwrap.dedent(
            """\
            venv/
            __pycache__/
            *.pyc
            """
        ),
    )
    write_file(
        project_dir / "README.md",
        textwrap.dedent(
            f"""\
            # {name}

            Generated with `initx python {name}`.

            ## Run

            ```bash
            {python_cmd} main.py
            ```
            """
        ),
    )

    if create_venv:
        venv.create(project_dir / "venv", with_pip=True)

    return project_dir


def create_node_project(name: str, base_path: str | Path = ".") -> Path:
    require_command("node")
    require_command("npm")
    project_dir = create_project_dir(name, base_path)

    write_file(
        project_dir / "package.json",
        textwrap.dedent(
            f"""\
            {{
              "name": "{name}",
              "version": "1.0.0",
              "description": "",
              "main": "index.js",
              "scripts": {{
                "start": "node index.js"
              }},
              "keywords": [],
              "author": "",
              "license": "ISC"
            }}
            """
        ),
    )
    write_file(
        project_dir / "index.js",
        textwrap.dedent(
            f"""\
            console.log("Hello from {name}!");
            """
        ),
    )
    write_file(
        project_dir / ".gitignore",
        textwrap.dedent(
            """\
            node_modules/
            npm-debug.log*
            .env
            """
        ),
    )
    write_file(
        project_dir / "README.md",
        textwrap.dedent(
            f"""\
            # {name}

            Generated with `initx node {name}`.

            ## Run

            ```bash
            npm start
            ```
            """
        ),
    )

    return project_dir


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.platform == "python":
        try:
            project_dir = create_python_project(
                name=args.name,
                base_path=args.path,
                create_venv=not args.no_venv,
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Created Python app at {project_dir}")
        return 0

    if args.platform == "node":
        try:
            project_dir = create_node_project(
                name=args.name,
                base_path=args.path,
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"Created Node.js app at {project_dir}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
