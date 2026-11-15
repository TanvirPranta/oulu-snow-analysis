"""Execute every notebook cell with this Python environment, from any directory."""
from pathlib import Path
import os
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

root = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(root / ".matplotlib"))
os.environ.setdefault("JUPYTER_RUNTIME_DIR", str(root / ".jupyter-runtime"))

class ProjectKernel(KernelManager):
    def format_kernel_cmd(self, extra_arguments=None):
        return [sys.executable, "-m", "ipykernel_launcher", "-f", self.connection_file] + (extra_arguments or [])

path = root / "DABI_FINAL_ASSIGNEMT.ipynb"
notebook = nbformat.read(path, as_version=4)
NotebookClient(notebook, timeout=180, kernel_name="python3",
               kernel_manager_class=ProjectKernel,
               resources={"metadata": {"path": str(root)}}).execute()
# Save only after every cell has completed successfully.
nbformat.write(notebook, path)
print("Completed notebook and outputs:", root / "outputs")
