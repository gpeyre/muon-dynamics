"""Audit the trusted MLP notebook's initialization; never call its training loop.

Usage: python python/mlp/validate_initialization.py [--notebook PATH]
Requires the notebook's numpy and torch dependencies. Prints JSON to stdout.
The AST extraction preserves RNG order, including the unused evaluation draw.
Only the initial gradient and hypothetical first-step arithmetic are evaluated.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import random
import sys


INITIAL_NAMES = set("""
SEED N z_train z_eval teacher_u teacher_angles teacher_v teacher y_train y_eval
n teacher_mean teacher_std init_std X_init time_horizon_inf time_horizon_p1
steps store_every dt_map time_horizon_map max_delta_x
""".split())
FUNCTIONS = {"relu", "predict_from_particles", "empirical_risk", "spectral_selector"}
SETUP_CALLS = {"torch.set_default_dtype", "random.seed", "np.random.seed", "torch.manual_seed"}


def notebook_setup(path):
    """Select setup statements in notebook order, stopping before run_flow calls."""
    raw = path.read_bytes()
    notebook = json.loads(raw)
    selected, locations, runs, setup_calls = [], {}, {}, set()
    flow = None
    for cell_index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = cell["source"]
        source = source if isinstance(source, str) else "".join(source)
        for node in ast.parse(source).body:
            if isinstance(node, ast.FunctionDef):
                if node.name == "run_flow":
                    flow = node
                elif node.name in FUNCTIONS:
                    selected.append(node)
                    locations[node.name] = [cell_index, node.lineno]
            elif isinstance(node, ast.Assign):
                names = {t.id for t in node.targets if isinstance(t, ast.Name)}
                if isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == "run_flow":
                    runs[next(iter(names))] = node.value
                elif not runs and names & INITIAL_NAMES:
                    selected.append(node)
                    for name in names:
                        locations[name] = [cell_index, node.lineno]
                elif not runs and names != {"FIG_DIR"}:
                    raise ValueError(f"Unreviewed setup assignment in cell {cell_index}: {names}")
            elif not runs and isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                name = ast.unparse(node.value.func)
                if name in SETUP_CALLS:
                    selected.append(node)
                    setup_calls.add(name)
                elif name not in {"print", "FIG_DIR.mkdir", "plt.rcParams.update"}:
                    raise ValueError(f"Unreviewed setup call in cell {cell_index}: {name}")
        if runs:
            break
    required = INITIAL_NAMES | FUNCTIONS
    if (required - locations.keys() or setup_calls != SETUP_CALLS
            or flow is None or set(runs) != {"out_p1", "out_pinf"}):
        raise ValueError("Notebook layout changed; review AST extraction before running.")
    # Use the notebook's actual update/clamp statements, not a copied clipping rule.
    loops = [n for n in flow.body if isinstance(n, ast.For)]
    updates = [n for n in loops[0].body if isinstance(n, ast.With)] if len(loops) == 1 else []
    if len(updates) != 1 or ast.unparse(updates[0].items[0].context_expr) != "torch.no_grad()":
        raise ValueError("Expected exactly one no_grad update block in run_flow.")
    update = updates[0]
    if any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(update)):
        raise ValueError("Update block unexpectedly contains a loop.")
    return raw, selected, locations, runs, update


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, default=Path(__file__).with_name("mlp_spectral_flow_relu.ipynb"))
    args = parser.parse_args()
    raw, setup, locations, runs, update = notebook_setup(args.notebook)
    try:
        import numpy as np
        import torch
    except ImportError as exc:
        parser.exit(2, f"Missing notebook dependency: {exc}. Use its torch/numpy environment.\n")

    torch.set_num_threads(1)
    ns = {"np": np, "torch": torch, "random": random}
    exec(compile(ast.Module(body=setup, type_ignores=[]), str(args.notebook), "exec"), ns)
    X = ns["X_init"].detach().clone().requires_grad_(True)
    loss = ns["empirical_risk"](X, ns["z_train"], ns["y_train"])
    G, = torch.autograd.grad(loss, X)
    if not torch.isfinite(G).all():
        raise ValueError("Nonfinite initial gradient.")
    singular = torch.linalg.svdvals(G)
    rank = int(torch.linalg.matrix_rank(G))
    d1 = float(G.square().sum())
    dinf = float(singular.sum().square())
    ratio = dinf / d1 if d1 else None
    if ratio is not None and not 1 - 1e-10 <= ratio <= rank + 1e-10:
        raise ValueError("Dissipation ratio fails the numerical rank bound.")

    diagnostics = {}
    for call in runs.values():
        kwargs = {
            kw.arg: eval(compile(ast.Expression(kw.value), str(args.notebook), "eval"), ns)
            for kw in call.keywords
        }
        p, dt = kwargs["p"], kwargs["dt"]
        velocity = ns["spectral_selector"](G, p)
        predicted_rate = d1 if p == 1 else dinf
        pairing = float(-(G * velocity).sum())
        if not np.isclose(pairing, predicted_rate, rtol=1e-9, atol=1e-14):
            raise ValueError("Notebook selector no longer matches Schatten dissipation.")
        local = dict(ns, X=X.detach().clone(), V=velocity, **kwargs)
        exec(compile(ast.Module(body=[update], type_ignores=[]), str(args.notebook), "exec"), local)
        raw_norm = float(torch.linalg.norm(dt * velocity))
        clipped_norm = float(torch.linalg.norm(local["dX"]))
        factor = clipped_norm / raw_norm if raw_norm else 1.0
        guard_change = float(torch.linalg.norm(local["X"] - (X.detach() + local["dX"])))
        diagnostics["p1" if p == 1 else "pinf"] = {
            "nominal_dt": dt,
            "nominal_horizon": dt * kwargs["steps"],
            "steps_configured_not_run": kwargs["steps"],
            "time_rescale_argument": kwargs["time_rescale"],
            "global_frobenius_step_cap": kwargs["max_delta_x"],
            "raw_initial_step_norm": raw_norm,
            "clipped_initial_step_norm": clipped_norm,
            "initial_clipping_active": raw_norm > kwargs["max_delta_x"],
            "initial_clipping_factor": factor,
            "initial_effective_dt_before_coordinate_guards": dt * factor,
            "initial_coordinate_guard_change_norm": guard_change,
            "initial_notebook_loss_rate_unclipped": pairing,
            "initial_notebook_loss_rate_after_scalar_clipping": pairing * factor,
            "initial_linearized_loss_decrease_per_step": -float((G * local["dX"]).sum()),
        }
    p1, pinf = diagnostics["p1"], diagnostics["pinf"]
    clipped_ratio = (
        pinf["initial_linearized_loss_decrease_per_step"]
        / p1["initial_linearized_loss_decrease_per_step"] if d1 else None
    )
    report = {
        "notebook": str(args.notebook.resolve()),
        "notebook_sha256": hashlib.sha256(raw).hexdigest(),
        "python": sys.version.split()[0], "torch": torch.__version__, "numpy": np.__version__,
        "seed": ns["SEED"], "dtype": str(X.dtype), "device": str(X.device),
        "particles": ns["n"], "train_samples": ns["N"], "eval_samples": len(ns["z_eval"]),
        "teacher_angles": ns["teacher_angles"].tolist(),
        "initial_loss": float(loss.detach()),
        "gradient_singular_values": singular.tolist(), "gradient_numerical_rank": rank,
        "D1_measure_force": ns["n"] * d1, "Dinf_measure_force": ns["n"] * dinf,
        "initial_unclipped_dissipation_ratio": ratio,
        "nominal_horizon_ratio_T1_over_Tinf": p1["nominal_horizon"] / pinf["nominal_horizon"],
        "initial_clipped_linearized_decrease_ratio_pinf_over_p1": clipped_ratio,
        "diagnostics": diagnostics,
        "source_locations_zero_based_cell_one_based_line": locations,
        "notebook_update_source": ast.unparse(update),
        "caveats": [
            "Initialization and hypothetical first-step arithmetic only; no training loop or plots run.",
            "The notebook gradient is G=g/n; measure-force dissipations are n times matrix rates.",
            "The ratio is an unclipped initial identity, not an observed finite-step loss decrease.",
            "Scalar clipping makes effective steps state-dependent; coordinate guards may also change direction.",
            "No clipping frequency, cumulative continuum clock, convergence, or runtime claim is inferred.",
            "Do not relabel existing plots from the initial ratio alone; report nominal times and caveats.",
        ],
    }
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
