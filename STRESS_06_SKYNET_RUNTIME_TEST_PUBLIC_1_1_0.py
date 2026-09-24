#!/usr/bin/env python3
"""
STRESS 06 — SKYNET 1_1_0
NATIVE EVENT REACTION LATENCY — PUBLICATION COPY

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
    events = []
    stop_reason = "MAX_CYCLES"
    run_start_ns = time.perf_counter_ns()
    previous_event_cycle = None
    previous_event_end_ns = None

    for cycle in range(1, MAX_CYCLES + 1):
        population_before = runtime.population_size()

        t0 = time.perf_counter_ns()
        measurement = runtime.execute_cycle(initial_input=(cycle == 1))
        t1 = time.perf_counter_ns()

        latency_s = (t1 - t0) / 1_000_000_000.0
        population_after = runtime.population_size()
        new_units = population_after - population_before
        event_units = measurement.new_units

        rows.append({
            "cycle": cycle,
            "population_before": population_before,
            "population_after": population_after,
            "new_units": new_units,
            "operations": measurement.operation_count,
            "secondary_events": measurement.secondary_event_count,
            "native_event_states": measurement.native_event_state_count,
            "event_units": event_units,
            "max_depth": measurement.max_depth,
            "cycle_latency_s": latency_s,
        })

        if event_units > 0 or new_units > 0:
            events.append({
                "event_index": len(events) + 1,
                "cycle": cycle,
                "population_before": population_before,
                "population_after": population_after,
                "new_units": new_units,
                "event_units": event_units,
                "native_event_states": measurement.native_event_state_count,
                "max_depth": measurement.max_depth,
                "reaction_latency_s": latency_s,
                "milliseconds_per_new_unit": (
                    latency_s * 1000.0 / event_units if event_units else None
                ),
                "cycles_since_previous_event": (
                    None if previous_event_cycle is None
                    else cycle - previous_event_cycle
                ),
                "elapsed_s_since_previous_event_end": (
                    None if previous_event_end_ns is None
                    else (t0 - previous_event_end_ns) / 1_000_000_000.0
                ),
                "elapsed_s_from_run_start": (
                    t1 - run_start_ns
                ) / 1_000_000_000.0,
            })
            previous_event_cycle = cycle
            previous_event_end_ns = t1

        if population_after >= POPULATION_LIMIT:
            stop_reason = "TEST_POPULATION_LIMIT"
            break

    latencies = [row["cycle_latency_s"] for row in rows]
    reaction_latencies = [event["reaction_latency_s"] for event in events]
    per_unit = [
        event["milliseconds_per_new_unit"]
        for event in events
        if event["milliseconds_per_new_unit"] is not None
    ]

    return {
        "test": "NATIVE_EVENT_REACTION_LATENCY",
        "stop_reason": stop_reason,
        "execution_cycles": len(rows),
        "final_population": rows[-1]["population_after"],
        "max_depth": max(row["max_depth"] for row in rows),
        "native_event_count": len(events),
        "total_new_units": sum(row["event_units"] for row in rows),
        "cycle_latency_min_s": min(latencies),
        "cycle_latency_mean_s": statistics.fmean(latencies),
        "cycle_latency_median_s": statistics.median(latencies),
        "cycle_latency_p95_s": percentile(latencies, 0.95),
        "cycle_latency_p99_s": percentile(latencies, 0.99),
        "cycle_latency_max_s": max(latencies),
        "reaction_latency_min_s": min(reaction_latencies),
        "reaction_latency_mean_s": statistics.fmean(reaction_latencies),
        "reaction_latency_median_s": statistics.median(reaction_latencies),
        "reaction_latency_p95_s": percentile(reaction_latencies, 0.95),
        "reaction_latency_p99_s": percentile(reaction_latencies, 0.99),
        "reaction_latency_max_s": max(reaction_latencies),
        "milliseconds_per_new_unit_min": min(per_unit),
        "milliseconds_per_new_unit_mean": statistics.fmean(per_unit),
        "milliseconds_per_new_unit_median": statistics.median(per_unit),
        "milliseconds_per_new_unit_p95": percentile(per_unit, 0.95),
        "milliseconds_per_new_unit_p99": percentile(per_unit, 0.99),
        "milliseconds_per_new_unit_max": max(per_unit),
        "events": events,
    }


if __name__ == "__main__":
    runtime = load_private_runtime()
    print(measure(runtime))
