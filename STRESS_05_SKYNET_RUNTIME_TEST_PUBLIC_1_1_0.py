#!/usr/bin/env python3
"""
STRESS 05 — SKYNET 1_1_0
EVENT THROUGHPUT — PUBLICATION COPY

Public benchmark disclosure.

Only the measurement protocol and a generic runtime interface are exposed.
Private implementation names, internal mechanisms, state names, bindings,
integration paths, and reconstruction-sensitive details are omitted.

No performance threshold or predetermined target is used.
"""

from __future__ import annotations

import statistics
import time


POPULATION_LIMIT = 192
MAX_CYCLES = 64


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    position = (len(values) - 1) * q
    low = int(position)
    high = min(low + 1, len(values) - 1)
    fraction = position - low
    return values[low] * (1.0 - fraction) + values[high] * fraction


def load_private_runtime():
    """Private runtime adapter intentionally excluded."""
    raise RuntimeError("Private runtime adapter is not included.")


def measure(runtime) -> dict:
    rows = []
    stop_reason = "MAX_CYCLES"

    for cycle in range(1, MAX_CYCLES + 1):
        population_before = runtime.population_size()

        t0 = time.perf_counter_ns()
        measurement = runtime.execute_cycle(initial_input=(cycle == 1))
        t1 = time.perf_counter_ns()

        latency_s = (t1 - t0) / 1_000_000_000.0
        population_after = runtime.population_size()
        operations = measurement.operation_count
        events = measurement.event_count

        rows.append(
            {
                "cycle": cycle,
                "population_before": population_before,
                "population_after": population_after,
                "new_units": population_after - population_before,
                "operations": operations,
                "events": events,
                "latency_s": latency_s,
                "events_per_s": events / latency_s if latency_s else 0.0,
                "microseconds_per_event": (
                    latency_s * 1_000_000.0 / events if events else None
                ),
                "event_density": events / operations if operations else None,
            }
        )

        if population_after >= POPULATION_LIMIT:
            stop_reason = "TEST_POPULATION_LIMIT"
            break

    latencies = [row["latency_s"] for row in rows]
    rates = [row["events_per_s"] for row in rows if row["events"] > 0]
    costs = [
        row["microseconds_per_event"]
        for row in rows
        if row["events"] > 0
    ]
    densities = [
        row["event_density"]
        for row in rows
        if row["event_density"] is not None
    ]

    measured_s = sum(latencies)
    total_events = sum(row["events"] for row in rows)

    return {
        "stop_reason": stop_reason,
        "execution_cycles": len(rows),
        "final_population": rows[-1]["population_after"],
        "measured_runtime_s": measured_s,
        "total_events": total_events,
        "aggregate_events_per_s": (
            total_events / measured_s if measured_s else 0.0
        ),
        "latency_min_s": min(latencies),
        "latency_mean_s": statistics.fmean(latencies),
        "latency_median_s": statistics.median(latencies),
        "latency_p95_s": percentile(latencies, 0.95),
        "latency_p99_s": percentile(latencies, 0.99),
        "latency_max_s": max(latencies),
        "throughput_min_events_per_s": min(rates),
        "throughput_mean_events_per_s": statistics.fmean(rates),
        "throughput_median_events_per_s": statistics.median(rates),
        "throughput_p95_events_per_s": percentile(rates, 0.95),
        "throughput_p99_events_per_s": percentile(rates, 0.99),
        "throughput_max_events_per_s": max(rates),
        "cost_mean_microseconds_per_event": statistics.fmean(costs),
        "cost_median_microseconds_per_event": statistics.median(costs),
        "event_density_mean": statistics.fmean(densities),
        "event_density_median": statistics.median(densities),
    }


if __name__ == "__main__":
    runtime = load_private_runtime()
    print(measure(runtime))
