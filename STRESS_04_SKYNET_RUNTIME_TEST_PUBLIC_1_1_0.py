#!/usr/bin/env python3
"""
STRESS 04 — SKYNET 1_1_0
PAIR-OPERATION THROUGHPUT — PUBLICATION COPY

Public benchmark disclosure.

This file exposes only the measurement protocol and generic runtime interface.
Private implementation names, internal operations, state names, integration
bindings, and reconstruction-sensitive details are not included.

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
    """
    Private runtime adapter intentionally excluded from public disclosure.
    """
    raise RuntimeError("Private runtime adapter is not included.")


def measure(runtime) -> dict:
    rows = []
    stop_reason = "MAX_CYCLES"

    for cycle in range(1, MAX_CYCLES + 1):
        population_before = runtime.population_size()
        expected_operations = (
            population_before * (population_before - 1) // 2
        )

        t0 = time.perf_counter_ns()
        measurement = runtime.execute_cycle(initial_input=(cycle == 1))
        t1 = time.perf_counter_ns()

        latency_s = (t1 - t0) / 1_000_000_000.0
        population_after = runtime.population_size()
        operations = measurement.operation_count

        rows.append(
            {
                "cycle": cycle,
                "population_before": population_before,
                "population_after": population_after,
                "new_units": population_after - population_before,
                "expected_operations": expected_operations,
                "operations": operations,
                "operation_count_ok": operations == expected_operations,
                "latency_s": latency_s,
                "operations_per_s": (
                    operations / latency_s if latency_s else 0.0
                ),
                "microseconds_per_operation": (
                    latency_s * 1_000_000.0 / operations
                    if operations else None
                ),
            }
        )

        if population_after >= POPULATION_LIMIT:
            stop_reason = "TEST_POPULATION_LIMIT"
            break

    latencies = [row["latency_s"] for row in rows]
    rates = [
        row["operations_per_s"]
        for row in rows
        if row["operations"] > 0
    ]
    costs = [
        row["microseconds_per_operation"]
        for row in rows
        if row["operations"] > 0
    ]
    measured_s = sum(latencies)
    total_operations = sum(row["operations"] for row in rows)

    return {
        "stop_reason": stop_reason,
        "execution_cycles": len(rows),
        "final_population": rows[-1]["population_after"],
        "measured_runtime_s": measured_s,
        "total_operations": total_operations,
        "operation_count_failures": sum(
            1 for row in rows if not row["operation_count_ok"]
        ),
        "aggregate_operations_per_s": (
            total_operations / measured_s if measured_s else 0.0
        ),
        "latency_min_s": min(latencies),
        "latency_mean_s": statistics.fmean(latencies),
        "latency_median_s": statistics.median(latencies),
        "latency_p95_s": percentile(latencies, 0.95),
        "latency_p99_s": percentile(latencies, 0.99),
        "latency_max_s": max(latencies),
        "throughput_min_operations_per_s": min(rates),
        "throughput_mean_operations_per_s": statistics.fmean(rates),
        "throughput_median_operations_per_s": statistics.median(rates),
        "throughput_p95_operations_per_s": percentile(rates, 0.95),
        "throughput_p99_operations_per_s": percentile(rates, 0.99),
        "throughput_max_operations_per_s": max(rates),
        "cost_mean_microseconds_per_operation": statistics.fmean(costs),
        "cost_median_microseconds_per_operation": statistics.median(costs),
    }


if __name__ == "__main__":
    runtime = load_private_runtime()
    print(measure(runtime))
