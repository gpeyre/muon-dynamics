#!/usr/bin/env python3
"""Execute teaching examples or paper experiments in isolated output directories."""

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import nbformat
from nbclient import NotebookClient
from jupyter_client import AsyncKernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = {
    "static": ("static/static_couplings.ipynb", "generate_static_notebook.py", 48),
    "mmd": ("mmd/mmd_flow.ipynb", "generate_mmd_notebook.py", 4),
    "gaussians": ("gaussians/gaussian_closed_form.ipynb", "generate_gaussians_notebook.py", 6),
    "gaussian-kl": ("gaussians-kl-flow/gaussian-kl-flow.ipynb", None, 4),
    "mlp": ("mlp/mlp_spectral_flow_relu.ipynb", "generate_mlp_spectral_flow_relu_notebook.py", 4),
    "attention": ("attention/attention_spectral_flow.ipynb", "generate_attention_notebook.py", 4),
}
EXAMPLES = ["01_spectral_directions", "02_particle_mmd", "03_static_transport", "04_gaussian_kl"]

# Applied to a copy through Python's syntax tree, never to the source notebook.
SMOKE_ASSIGNMENTS = {
    "mmd": {"n": 24, "m": 24, "steps": 8},
    "mlp": {"n": 32, "N": 32, "steps": 8, "time_horizon_p1": .02, "time_horizon_inf": .02},
    "attention": {"n_student": 8, "N": 4, "n_runs": 1, "steps_base": 2},
}


class SmokeParameters(ast.NodeTransformer):
    def __init__(self, name):
        self.name = name
        self.changes = []

    def visit_Assign(self, node):
        node = self.generic_visit(node)
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            key = node.targets[0].id
            if key in SMOKE_ASSIGNMENTS.get(self.name, {}):
                value = SMOKE_ASSIGNMENTS[self.name][key]
                self.changes.append({"assignment": key, "value": value})
                node.value = ast.Constant(value)
        return node

    def visit_Call(self, node):
        node = self.generic_visit(node)
        name = node.func.id if isinstance(node.func, ast.Name) else ""
        for keyword in node.keywords:
            if self.name == "static" and name == "sample_static_pair" and keyword.arg == "num_points":
                keyword.value = ast.Constant(40)
                self.changes.append({"call": name, "num_points": 40})
            elif self.name == "gaussian-kl" and name == "integrate_covariance_flow":
                if keyword.arg in ("T", "dt"):
                    value = .04 if keyword.arg == "T" else .001
                    keyword.value = ast.Constant(value)
                    self.changes.append({"call": name, keyword.arg: value})
        return node

    def visit_FunctionDef(self, node):
        node = self.generic_visit(node)
        if self.name == "gaussians" and node.name in ("integrate_flow_1d", "integrate_flow_2d"):
            args = node.args.args[-len(node.args.defaults):]
            for index, argument in enumerate(args):
                if argument.arg in ("T", "dt"):
                    value = .04 if argument.arg == "T" else .001
                    node.args.defaults[index] = ast.Constant(value)
                    self.changes.append({"function": node.name, argument.arg: value})
        return node


def check_sources():
    """Check that checked-in notebooks agree with their plain-Python generators."""
    for name, (relative, generator, _) in EXPERIMENTS.items():
        original = nbformat.read(ROOT / "python" / relative, as_version=4)
        nbformat.validate(original)
        if generator:
            with tempfile.TemporaryDirectory() as directory:
                script = Path(directory) / generator
                shutil.copy2(ROOT / "python" / Path(relative).parent / generator, script)
                subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
                rebuilt = nbformat.read(Path(directory) / Path(relative).name, as_version=4)
                cells = lambda nb: [(c.cell_type, c.source) for c in nb.cells]
                if cells(original) != cells(rebuilt):
                    raise RuntimeError(f"{name}: notebook is out of sync with {generator}")
        for cell in original.cells:
            if cell.cell_type == "code":
                ast.parse(cell.source)
        print(f"Checked {name}", flush=True)
    with tempfile.TemporaryDirectory() as directory:
        script = Path(directory) / "generate_examples.py"
        shutil.copy2(ROOT / "python" / "examples" / script.name, script)
        subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
        for name in EXAMPLES:
            original = nbformat.read(ROOT / "python" / "examples" / f"{name}.ipynb", as_version=4)
            rebuilt = nbformat.read(Path(directory) / f"{name}.ipynb", as_version=4)
            cells = lambda nb: [(c.cell_type, c.source) for c in nb.cells]
            if cells(original) != cells(rebuilt):
                raise RuntimeError(f"{name}: notebook is out of sync with generate_examples.py")
            nbformat.validate(original)
            print(f"Checked {name}", flush=True)


def versions():
    result = {"python": sys.version}
    for package in ("muon-dynamics", "numpy", "scipy", "torch", "cvxpy", "matplotlib", "nbformat", "nbclient"):
        try:
            result[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result[package] = None
    return result


def run_notebook(name, destination, *, smoke=False, timeout=3600):
    example = name in EXAMPLES
    relative, generator, count = ((f"examples/{name}.ipynb", None, 0) if example else EXPERIMENTS[name])
    destination.mkdir(parents=True, exist_ok=False)
    notebook_path = destination / "python" / relative
    notebook_path.parent.mkdir(parents=True)
    source = ROOT / "python" / relative
    shutil.copy2(source, notebook_path)
    if generator:
        script = ROOT / "python" / Path(relative).parent / generator
        shutil.copy2(script, notebook_path.parent / generator)
        subprocess.run([sys.executable, str(notebook_path.parent / generator)], check=True, capture_output=True)
    if name == "static":
        shutil.copytree(ROOT / "python" / "data", destination / "python" / "data")
    nb = nbformat.read(notebook_path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs, cell.execution_count = [], None
    transformer = SmokeParameters(name)
    if smoke and not example:
        for cell in nb.cells:
            if cell.cell_type == "code":
                tree = transformer.visit(ast.parse(cell.source))
                cell.source = ast.unparse(ast.fix_missing_locations(tree))
        nb.cells.insert(0, nbformat.v4.new_markdown_cell(
            "# Smoke test only\nReduced dimensions/horizons: not the published experiment."))
    provenance = {
        "experiment": name, "smoke": smoke and not example,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "versions": versions(), "smoke_overrides": transformer.changes,
        "kernel_environment": {"OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
        "status": "running", "artifacts": [],
    }
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True)
    provenance["git_commit"] = git.stdout.strip() if git.returncode == 0 else None
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True)
    provenance["git_dirty"] = bool(status.stdout.strip()) if status.returncode == 0 else None
    if generator:
        provenance["generator_sha256"] = hashlib.sha256(script.read_bytes()).hexdigest()
    provenance["toolbox_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((ROOT / "src" / "muon_dynamics").glob("*.py"))
    }
    provenance["input_sha256"] = {
        str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((destination / "python" / "data").glob("*")) if p.is_file()
    }
    start = time.monotonic()
    try:
        # A private kernelspec uses this exact Python environment, not a user's
        # unrelated default Jupyter kernel. No global kernel registration.
        with tempfile.TemporaryDirectory() as temporary:
            kernel_dir = Path(temporary) / "muon"
            kernel_dir.mkdir()
            (kernel_dir / "kernel.json").write_text(json.dumps({
                "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "Muon reproduction", "language": "python",
                "env": {"MPLBACKEND": "module://matplotlib_inline.backend_inline",
                        "MPLCONFIGDIR": str(Path(temporary) / "matplotlib"),
                        "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
            }))
            manager = AsyncKernelManager(kernel_name="muon", kernel_spec_manager=KernelSpecManager(kernel_dirs=[temporary]))
            client = NotebookClient(nb, km=manager, timeout=timeout,
                                    resources={"metadata": {"path": str(notebook_path.parent)}})
            # Supplying a manager normally transfers cleanup responsibility to
            # the caller. This private manager belongs exclusively to this run.
            client.owns_km = True
            client.execute()
        pdfs = sorted(destination.rglob("*.pdf"))
        if len(pdfs) < count:
            raise RuntimeError(f"Expected at least {count} PDFs, produced {len(pdfs)}")
        provenance["status"] = "success"
        provenance["artifacts"] = [str(p.relative_to(destination)) for p in pdfs]
    except Exception as error:
        provenance["status"] = "failed"
        provenance["error"] = str(error)
        raise
    finally:
        provenance["elapsed_seconds"] = time.monotonic() - start
        nbformat.write(nb, notebook_path)
        (destination / "run.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Finished {name}: {destination} ({provenance['elapsed_seconds']:.1f}s)", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiments", nargs="*", help="Names from --list")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--check", action="store_true", help="Validate notebook/generator agreement; do not execute")
    parser.add_argument("--all", action="store_true", help="Run all six paper experiments")
    parser.add_argument("--examples", action="store_true", help="Run the four small teaching notebooks")
    parser.add_argument("--smoke", action="store_true", help="Reduced paper experiments; not publication results")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "reproduction")
    parser.add_argument("--timeout", type=int, default=3600, help="Per-cell timeout in seconds")
    args = parser.parse_args()
    if args.list:
        for name, (path, _, _) in EXPERIMENTS.items():
            print(f"{name:12} python/{path}")
        return
    if args.check:
        check_sources()
        return
    names = list(EXPERIMENTS) if args.all else list(args.experiments)
    if args.examples:
        names.extend(EXAMPLES)
    if not names or any(n not in EXPERIMENTS and n not in EXAMPLES for n in names):
        parser.error("Choose names from --list, --all, or --examples")
    if len(names) != len(set(names)):
        parser.error("Each experiment can be selected only once")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    output = args.output.resolve()
    for name in names:
        if (output / name).exists():
            parser.error(f"Refusing to overwrite {output / name}; choose a fresh --output directory")
    for name in names:
        print(f"Running {name}{' (smoke)' if args.smoke else ''}...", flush=True)
        run_notebook(name, output / name, smoke=args.smoke, timeout=args.timeout)


if __name__ == "__main__":
    main()
