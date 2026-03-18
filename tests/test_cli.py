from __future__ import annotations

import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from init_cli.cli import create_node_project, create_python_project, main


class CreatePythonProjectTests(unittest.TestCase):
    def test_creates_python_project_without_venv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", side_effect=lambda cmd: "/usr/bin/python3" if cmd == "python3" else None):
                project_dir = create_python_project("myapp", tmp, create_venv=False)

            self.assertEqual(project_dir, Path(tmp) / "myapp")
            self.assertTrue((project_dir / "main.py").exists())
            self.assertTrue((project_dir / "requirements.txt").exists())
            self.assertTrue((project_dir / ".gitignore").exists())
            self.assertTrue((project_dir / "README.md").exists())
            self.assertFalse((project_dir / "venv").exists())
            readme = (project_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("python3 main.py", readme)
            self.assertIn("Generated with `initx python myapp`.", readme)

    def test_rejects_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            existing_dir = Path(tmp) / "myapp"
            existing_dir.mkdir()

            with patch("init_cli.cli.shutil.which", return_value="/usr/bin/python"):
                with self.assertRaises(FileExistsError):
                    create_python_project("myapp", tmp, create_venv=False)

    def test_creates_venv_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", return_value="/usr/bin/python"):
                with patch("init_cli.cli.venv.create") as create_mock:
                    project_dir = create_python_project("myapp", tmp)

            create_mock.assert_called_once_with(project_dir / "venv", with_pip=True)

    def test_initializes_empty_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", return_value="/usr/bin/python"):
                project_dir = create_python_project(".", tmp, create_venv=False)

            self.assertEqual(project_dir, Path(tmp))
            self.assertTrue((project_dir / "main.py").exists())

    def test_rejects_non_empty_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "existing.txt").write_text("x", encoding="utf-8")

            with patch("init_cli.cli.shutil.which", return_value="/usr/bin/python"):
                with self.assertRaises(FileExistsError):
                    create_python_project(".", tmp, create_venv=False)

    def test_requires_python_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", return_value=None):
                with self.assertRaises(RuntimeError):
                    create_python_project("myapp", tmp, create_venv=False)


class CreateNodeProjectTests(unittest.TestCase):
    def test_creates_node_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", side_effect=lambda cmd: f"/usr/bin/{cmd}"):
                project_dir = create_node_project("webapp", tmp)

            self.assertEqual(project_dir, Path(tmp) / "webapp")
            self.assertTrue((project_dir / "package.json").exists())
            self.assertTrue((project_dir / "index.js").exists())
            self.assertTrue((project_dir / ".gitignore").exists())
            self.assertTrue((project_dir / "README.md").exists())
            self.assertIn("Generated with `initx node webapp`.", (project_dir / "README.md").read_text(encoding="utf-8"))

    def test_rejects_existing_node_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            existing_dir = Path(tmp) / "webapp"
            existing_dir.mkdir()

            with patch("init_cli.cli.shutil.which", side_effect=lambda cmd: f"/usr/bin/{cmd}"):
                with self.assertRaises(FileExistsError):
                    create_node_project("webapp", tmp)

    def test_initializes_empty_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", side_effect=lambda cmd: f"/usr/bin/{cmd}"):
                project_dir = create_node_project(".", tmp)

            self.assertEqual(project_dir, Path(tmp))
            self.assertTrue((project_dir / "package.json").exists())

    def test_requires_node_and_npm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", return_value=None):
                with self.assertRaises(RuntimeError):
                    create_node_project("webapp", tmp)


class MainTests(unittest.TestCase):
    def test_main_returns_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", return_value="/usr/bin/python"):
                exit_code = main(["python", "myapp", "--path", tmp, "--no-venv"])

            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(tmp) / "myapp" / "main.py").exists())

    def test_main_returns_error_when_project_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "myapp").mkdir()

            with patch("init_cli.cli.shutil.which", return_value="/usr/bin/python"):
                exit_code = main(["python", "myapp", "--path", tmp, "--no-venv"])

            self.assertEqual(exit_code, 1)

    def test_main_creates_node_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", side_effect=lambda cmd: f"/usr/bin/{cmd}"):
                exit_code = main(["node", "webapp", "--path", tmp])

            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(tmp) / "webapp" / "package.json").exists())

    def test_main_initializes_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch("init_cli.cli.shutil.which", return_value="/usr/bin/python"):
                exit_code = main(["python", ".", "--path", tmp, "--no-venv"])

            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(tmp) / "main.py").exists())

    def test_main_returns_error_when_prerequisite_is_missing(self) -> None:
        with patch("init_cli.cli.shutil.which", return_value=None):
            exit_code = main(["node", "webapp"])

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
