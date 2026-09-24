#!/usr/bin/env python3
"""
SKYNET 1_1_0 — NATIVE RUNTIME STRESS TEST 02
PUBLICATION COPY

Population-scaling and pair-throughput benchmark disclosure.

This publication copy intentionally omits private runtime identifiers,
internal mechanism names, private integration paths, and reconstruction-
sensitive bindings. The executable private benchmark used the same
measurement limits and timing rules represented here.

No performance threshold or predetermined target was used.
"""

from __future__ import annotations

import statistics
import time


POPULATION_LIMIT = 64
MAX_CYCLES = 100


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    f = pos - lo
    return ordered[lo] * (1.0 - f) + ordered[hi] * f


def population_band(n: int) -> str:
    if n <= 4:
        return "01_04"
    if n <= 8:
        return "05_08"
    if n <= 16:
        return "09_16"
    if n <= 32:
        return "17_32"
    return "33_64"


def measure_cycle(runtime, first_cycle: bool) -> dict:
    """
    Publication boundary.

    `runtime` is supplied by the private SKYNET runtime adapter.
    Private class names, method names, initialization paths, state
    transitions and mechanism bindings are intentionally not disclosed.
    """
    before = runtime.population_size()

    t0 = time.perf_counter_ns()
    measurement = runtime.execute_cycle(initial_input=first_cycle)
    t1 = time.perf_counter_ns()

    latency_s = (t1 - t0) / 1_000_000_000.0
    after = runtime.population_size()

    return {
        "population_band": population_band(before),
        "population_before": before,
        "population_after": after,
        "new_units": after - before,
        "pair_operations": measurement.pair_operations,
        "secondary_events": measurement.secondary_events,
        "new_units_reported": measurement.new_units,
        "latency_s": latency_s,
        "pair_operations_per_s": (
            measurement.pair_operations / latency_s if latency_s else 0.0
        ),
        "secondary_events_per_s": (
            measurement.secondary_events / latency_s if latency_s else 0.0
        ),
    }


def run(runtime) -> dict:
    rows = []
    stop_reason = "MAX_CYCLES"

    for cycle in range(1, MAX_CYCLES + 1):
        row = measure_cycle(runtime, first_cycle=(cycle == 1))
        row["cycle"] = cycle
        rows.append(row)

        if row["population_after"] >= POPULATION_LIMIT:
            stop_reason = "TEST_POPULATION_LIMIT"
            break

    latencies = [row["latency_s"] for row in rows]
    measured_s = sum(latencies)
    pair_total = sum(row["pair_operations"] for row in rows)
    event_total = sum(row["secondary_events"] for row in rows)

    return {
        "stop_reason": stop_reason,
        "cycles": len(rows),
        "final_population": rows[-1]["population_after"],
        "measured_runtime_s": measured_s,
        "pair_operations": pair_total,
        "secondary_events": event_total,
        "cycles_per_s": len(rows) / measured_s,
        "pair_operations_per_s": pair_total / measured_s,
        "secondary_events_per_s": event_total / measured_s,
        "latency_min_s": min(latencies),
        "latency_mean_s": statistics.fmean(latencies),
        "latency_median_s": statistics.median(latencies),
        "latency_p95_s": percentile(latencies, 0.95),
        "latency_p99_s": percentile(latencies, 0.99),
        "latency_max_s": max(latencies),
    }


if __name__ == "__main__":
    raise SystemExit(
        "PUBLICATION COPY: private SKYNET runtime adapter intentionally omitted."
    )
