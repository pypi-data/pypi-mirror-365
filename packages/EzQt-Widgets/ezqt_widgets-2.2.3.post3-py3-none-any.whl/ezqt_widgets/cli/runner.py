"""
Example runner module for EzQt Widgets CLI.

Handles the execution of example files with proper error handling and feedback.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, List
import click


class ExampleRunner:
    """Handles running EzQt Widgets examples."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.examples_dir = self._find_examples_dir()

    def _find_examples_dir(self) -> Path:
        """Find the examples directory relative to the package."""
        # First priority: examples inside the package (ezqt_widgets/examples/)
        package_examples = Path(__file__).parent.parent / "examples"
        if package_examples.exists():
            return package_examples

        # Second priority: try to find examples in the project root
        package_dir = Path(__file__).parent.parent.parent
        examples_dir = package_dir / "examples"

        if examples_dir.exists():
            return examples_dir

        # Fallback: try to find examples in the current directory
        current_examples = Path.cwd() / "examples"
        if current_examples.exists():
            return current_examples

        raise FileNotFoundError("Examples directory not found")

    def get_available_examples(self) -> List[Path]:
        """Get list of available example files."""
        examples = []
        for pattern in ["*_example.py", "run_all_examples.py"]:
            examples.extend(self.examples_dir.glob(pattern))
        return sorted(examples)

    def run_example(self, example_name: str) -> bool:
        """Run a specific example by name."""
        example_path = self.examples_dir / f"{example_name}.py"

        if not example_path.exists():
            click.echo(f"❌ Example not found: {example_name}")
            return False

        return self._execute_example(example_path)

    def run_all_examples(self, use_gui_launcher: bool = True) -> bool:
        """Run all examples or use the GUI launcher."""
        if use_gui_launcher:
            launcher_path = self.examples_dir / "run_all_examples.py"
            if launcher_path.exists():
                return self._execute_example(launcher_path)
            else:
                click.echo("⚠️  GUI launcher not found, running examples sequentially")
                use_gui_launcher = False

        if not use_gui_launcher:
            # Run each example sequentially
            examples = [
                "button_example",
                "input_example",
                "label_example",
                "misc_example",
            ]
            success_count = 0

            for example in examples:
                click.echo(f"\n{'='*50}")
                click.echo(f"🚀 Running: {example}")
                click.echo(f"{'='*50}")

                if self.run_example(example):
                    success_count += 1
                else:
                    click.echo(f"❌ Failed to run: {example}")

            click.echo(
                f"\n✅ Successfully ran {success_count}/{len(examples)} examples"
            )
            return success_count == len(examples)

        return False

    def _execute_example(self, example_path: Path) -> bool:
        """Execute a specific example file."""
        if self.verbose:
            click.echo(f"🚀 Running: {example_path.name}")

        try:
            # Change to the examples directory to ensure relative imports work
            original_cwd = os.getcwd()
            os.chdir(example_path.parent)

            result = subprocess.run(
                [sys.executable, str(example_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Restore original working directory
            os.chdir(original_cwd)

            if result.returncode != 0:
                click.echo(f"❌ Error running {example_path.name}: {result.stderr}")
                return False

            return True

        except subprocess.TimeoutExpired:
            click.echo(f"⏰ Timeout running {example_path.name}")
            return False
        except Exception as e:
            click.echo(f"❌ Exception running {example_path.name}: {e}")
            return False

    def list_examples(self) -> None:
        """List all available examples."""
        examples = self.get_available_examples()

        if not examples:
            click.echo("❌ No examples found")
            return

        click.echo("📋 Available examples:")
        click.echo("=" * 40)

        for example in examples:
            status = "✅" if example.exists() else "❌"
            click.echo(f"{status} {example.stem}")

        click.echo(f"\nTotal: {len(examples)} examples found")


def run_example_by_category(category: str, verbose: bool = False) -> bool:
    """Run examples by category."""
    runner = ExampleRunner(verbose)

    category_mapping = {
        "buttons": "button_example",
        "inputs": "input_example",
        "labels": "label_example",
        "misc": "misc_example",
    }

    if category not in category_mapping:
        click.echo(f"❌ Unknown category: {category}")
        click.echo(f"Available categories: {', '.join(category_mapping.keys())}")
        return False

    return runner.run_example(category_mapping[category])


def run_all_examples(use_gui: bool = True, verbose: bool = False) -> bool:
    """Run all examples."""
    runner = ExampleRunner(verbose)
    return runner.run_all_examples(use_gui)


def list_available_examples() -> None:
    """List all available examples."""
    runner = ExampleRunner()
    runner.list_examples()
