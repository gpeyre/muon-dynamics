"""Independently resolve Gaussian rank-loss and zero-error events.

The reference integrates powers of the variances, detects events, and keeps
extinct eigenvalues and solved modes fixed. Compare two reference tolerances
and the actual notebook RK4 step under step-size refinement around each event.
No plots or training runs are executed.
"""

import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from validate_gaussians import load_functions


def event_reference(a0, b0, beta, p, horizon, tolerance):
    q = 1.0 if np.isinf(p) else 2 * p / (2 * p - 1)
    eta = 1 - q / 2 if p > 1 else 1.0
    size = len(beta)
    extinct = np.zeros(2 * size, dtype=bool)
    solved = np.isclose((a0 - b0) / 2, beta, rtol=0, atol=1e-14)
    signs = np.sign((a0 - b0) / 2 - beta)
    state = np.concatenate((a0, b0)) ** eta
    start = 0.0
    segments, records = [], []

    def variances(y):
        return np.maximum(y, 0) ** (1 / eta)

    for _ in range(4 * size + 2):
        active_coordinates = ~extinct.copy()
        active_modes = ~solved.copy()

        def rhs(time, y):
            ab = variances(y)
            a, b = ab[:size], ab[size:]
            error = (a - b) / 2 - beta
            error[~active_modes] = 0
            nq = np.sum(np.abs(error) ** q * (a ** (q / 2) + b ** (q / 2)))
            prefactor = nq ** ((2 - q) / q) if nq > 0 else 0.0
            # Each mode approaches its target from its initial side; stop there.
            response_signs = signs if np.count_nonzero(active_modes) > 1 else np.sign(error)
            psi = response_signs * np.abs(error) ** (q - 1)
            psi[~active_modes] = 0
            rate = 2 * prefactor * psi
            if p == 1:
                result = np.concatenate((-rate * a, rate * b))
            else:
                result = eta * np.concatenate((-rate, rate))
            result[~active_coordinates] = 0
            return result

        events, descriptors = [], []
        if p > 1:
            for index in np.flatnonzero(active_coordinates):
                mode = index % size
                if not active_modes[mode]:
                    continue
                shrinking = (index < size and signs[mode] > 0) or (index >= size and signs[mode] < 0)
                if shrinking:
                    def extinction(time, y, index=index):
                        return y[index]
                    extinction.terminal, extinction.direction = True, -1
                    events.append(extinction)
                    descriptors.append(("rank_loss", int(index)))
            # With only one residual left, its final approach is asymptotic.
            target_modes = np.flatnonzero(active_modes) if np.count_nonzero(active_modes) > 1 else []
            for mode in target_modes:
                def target(time, y, mode=mode):
                    ab = variances(y)
                    return signs[mode] * ((ab[mode] - ab[size + mode]) / 2 - beta[mode])
                target.terminal, target.direction = True, -1
                events.append(target)
                descriptors.append(("target", int(mode)))

        solution = solve_ivp(rhs, (start, horizon), state, rtol=tolerance,
                             atol=tolerance * 0.02, events=events or None,
                             dense_output=True, max_step=0.05)
        assert solution.success, solution.message
        segments.append((start, solution.t[-1], solution.sol))
        if solution.status == 0:
            break
        hit = next(i for i, times in enumerate(solution.t_events) if len(times))
        kind, index = descriptors[hit]
        start, state = float(solution.t[-1]), solution.y[:, -1].copy()
        records.append({"time": start, "kind": kind, "index": index})
        if kind == "rank_loss":
            state[index] = 0.0
            extinct[index] = True
        else:
            solved[index] = True
    else:
        raise AssertionError("Too many event restarts")

    def evaluate(times):
        times = np.atleast_1d(times)
        out = np.empty((2 * size, len(times)))
        for first, last, interpolant in segments:
            selected = (times >= first - 1e-13) & (times <= last + 1e-13)
            if selected.any():
                out[:, selected] = variances(interpolant(times[selected]))
        return out

    return evaluate, records


def check_case(ns, name, a0, b0, beta, p, horizon):
    coarse, coarse_events = event_reference(a0, b0, beta, p, horizon, 2e-9)
    reference, events = event_reference(a0, b0, beta, p, horizon, 2e-11)
    assert [(e["kind"], e["index"]) for e in events] == [
        (e["kind"], e["index"]) for e in coarse_events
    ]
    sample = np.linspace(0, horizon, 501)
    path = reference(sample)
    size = len(beta)
    predictor = (path[:size] - path[size:]) / 2
    losses = 0.5 * np.sum((predictor - beta[:, None]) ** 2, axis=0)
    assert np.all(path >= 0)
    assert np.max(np.diff(losses)) < 1e-10, (name, p, "energy increase")
    for event in events:
        if event["kind"] == "rank_loss":
            after = np.linspace(event["time"] + 1e-7, horizon, 50)
            np.testing.assert_array_equal(reference(after)[event["index"]], 0.0)
    reference_error = float(np.max(np.abs(path - coarse(sample))))
    event_error = max((abs(a["time"] - b["time"]) for a, b in zip(events, coarse_events)), default=0.0)
    rank_error = max((abs(a["time"] - b["time"]) for a, b in zip(events, coarse_events)
                      if a["kind"] == "rank_loss"), default=0.0)
    assert reference_error < 2e-6, (name, p, reference_error)
    assert rank_error < 2e-7, (name, p, rank_error)
    # For finite p>1 the target event is nontransverse: its speed tends to zero.
    assert event_error < 1e-3, (name, p, event_error)
    windows = []
    # Refine the real notebook step locally across every detected event.
    for event in events:
        start = max(0, event["time"] - 0.02)
        duration = min(0.04, horizon - start)
        errors = []
        for dt in (2e-4, 1e-4, 5e-5):
            steps = int(round(duration / dt))
            dt = duration / steps
            ab = reference([start])[:, 0]
            a, b = ab[:size].copy(), ab[size:].copy()
            worst = 0.0
            times = start + dt * np.arange(1, steps + 1)
            expected = reference(times)
            for index in range(steps):
                a, b = ns["rk4_step_2d"](a, b, dt, p, beta)
                worst = max(worst, float(np.max(np.abs(np.concatenate((a, b)) - expected[:, index]))))
            errors.append(worst)
        assert errors[-1] < 1e-3, (name, p, event, errors)
        assert errors[-1] <= errors[0] * 1.1 + 1e-8, (name, p, event, errors)
        windows.append({**event, "rk4_errors_dt_2e4_1e4_5e5": errors})
    return {"case": name, "p": "inf" if np.isinf(p) else p,
            "reference_refinement_error": reference_error,
            "event_time_refinement_error": event_error,
            "rank_time_refinement_error": rank_error, "events": windows}


def main():
    ns = load_functions(Path(__file__).with_name("gaussian_closed_form.ipynb"))
    reports = []
    for p in ns["p_values"]:
        for i, (r, s) in enumerate(ns["initial_points"]):
            reports.append(check_case(ns, f"one-mode-{i}", np.array([s + r]),
                                      np.array([s - r]), np.array([ns["TARGET"]]), p, 18.0))
        for i, beta in enumerate(ns["beta_list"]):
            reports.append(check_case(ns, f"two-mode-{i}", ns["s_init_2d"] + ns["r_init_2d"],
                                      ns["s_init_2d"] - ns["r_init_2d"], np.asarray(beta), p, 18.0))
    print(json.dumps(reports, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
