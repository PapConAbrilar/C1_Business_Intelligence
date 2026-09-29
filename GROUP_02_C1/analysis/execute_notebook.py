"""Restart, run every C1 notebook cell, and save the visible outputs."""

import json
import os
from pathlib import Path
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parents[1]
NOTEBOOK = PACKAGE / "analysis/respiratory_emergency_c1.ipynb"


def main() -> None:
    # A task-local kernelspec makes the kernel use the exact Python environment
    # chosen for this command rather than another system Jupyter installation.
    with tempfile.TemporaryDirectory(prefix="c1-kernel-") as directory:
        spec = Path(directory) / "kernels/c1-python"
        spec.mkdir(parents=True)
        (spec / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "C1 Python", "language": "python",
        }), encoding="utf-8")
        os.environ["JUPYTER_PATH"] = directory

        import nbformat
        from nbclient import NotebookClient

        notebook = nbformat.read(NOTEBOOK, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        client = NotebookClient(
            notebook, timeout=600, kernel_name="c1-python",
            resources={"metadata": {"path": str(PACKAGE)}},
        )
        client.execute()
        if any(cell.cell_type == "code" and cell.execution_count is None for cell in notebook.cells):
            raise RuntimeError("At least one code cell was not executed")
        nbformat.write(notebook, NOTEBOOK)
    print(f"Executed and saved {NOTEBOOK}")


if __name__ == "__main__":
    main()
