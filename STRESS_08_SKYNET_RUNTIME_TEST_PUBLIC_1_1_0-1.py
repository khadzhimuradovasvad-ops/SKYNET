#!/usr/bin/env python3
"""
STRESS 08 — SKYNET 1_1_0
GENERATIONAL CONTINUITY UNDER LOAD — PUBLICATION COPY

Public benchmark disclosure.

This publication exposes the measurement protocol through a generic runtime
interface. Private formulas, project-native mechanism names, internal state
names, bindings, integration paths, and reconstruction-sensitive details are
intentionally excluded.

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
    p = (len(values) - 1) * q
    lo = int(p)
    hi = min(lo + 1, len(values) - 1)
    f = p - lo
    return values[lo] * (1.0 - f) + values[hi] * f


def load_private_runtime():
    """Private runtime adapter intentionally excluded."""
    raise RuntimeError("Private runtime adapter is not included.")


def continuity_to_initial(unit, initial_unit):
    seen = set()
    current = unit

    while current is not initial_unit:
        marker = id(current)
        if marker in seen:
            return False, "PARENT_CYCLE"
        seen.add(marker)

        parent = current.parent
        if parent is None:
            return False, "MISSING_PARENT"

        if current.generation != parent.generation + 1:
            return False, "GENERATION_STEP"

        current = parent

    if initial_unit.generation != 0:
        return False, "INITIAL_GENERATION"

    return True, None


def measure(runtime):
    initial_unit = runtime.initial_unit()
    known_objects = {id(initial_unit)}
    known_ids = {initial_unit.identifier}

    rows = []
    new_unit_records = []

    pair_count_failures = 0
    duplicate_id_failures = 0
    parent_reference_failures = 0
    generation_step_failures = 0
    continuity_failures = 0
    retention_failures = 0

    run_start = time.perf_counter()

    for cycle in range(1, MAX_CYCLES + 1):
        before = list(runtime.active_units())
        before_objects = {id(x) for x in before}
        expected_pairs = len(before) * (len(before) - 1) // 2

        t0 = time.perf_counter()
        measurement = runtime.execute_cycle(initial_input=(cycle == 1))
        latency = time.perf_counter() - t0

        after = list(runtime.active_units())
        after_objects = {id(x) for x in after}
        ids = [x.identifier for x in after]
        new_units = [x for x in after if id(x) not in before_objects]

        pair_ok = measurement.operation_count == expected_pairs
        if not pair_ok:
            pair_count_failures += 1

        retained = before_objects.issubset(after_objects)
        if not retained:
            retention_failures += 1

        unique_ids = len(ids) == len(set(ids))
        if not unique_ids:
            duplicate_id_failures += 1

        cycle_parent_failures = 0
        cycle_generation_failures = 0
        cycle_continuity_failures = 0

        for unit in new_units:
            parent = unit.parent

            parent_ok = parent is not None and id(parent) in before_objects
            if not parent_ok:
                parent_reference_failures += 1
                cycle_parent_failures += 1

            generation_ok = (
                parent is not None
                and unit.generation == parent.generation + 1
            )
            if not generation_ok:
                generation_step_failures += 1
                cycle_generation_failures += 1

            continuity_ok, continuity_error = continuity_to_initial(
                unit, initial_unit
            )
            if not continuity_ok:
                continuity_failures += 1
                cycle_continuity_failures += 1

            known_objects.add(id(unit))
            known_ids.add(unit.identifier)

            new_unit_records.append({
                "cycle": cycle,
                "generation": unit.generation,
                "parent_generation": (
                    parent.generation if parent is not None else None
                ),
                "parent_existed_before_cycle": parent_ok,
                "generation_step_ok": generation_ok,
                "continuity_to_initial_unit": continuity_ok,
                "continuity_error": continuity_error,
            })

        all_active_continuity_ok = all(
            continuity_to_initial(unit, initial_unit)[0]
            for unit in after
        )

        rows.append({
            "cycle": cycle,
            "population_before": len(before),
            "population_after": len(after),
            "new_units": len(new_units),
            "expected_operations": expected_pairs,
            "operations": measurement.operation_count,
            "operation_count_ok": pair_ok,
            "secondary_events": measurement.secondary_event_count,
            "max_generation": max(x.generation for x in after),
            "retention_ok": retained,
            "unique_ids_ok": unique_ids,
            "new_unit_parent_failures": cycle_parent_failures,
            "new_unit_generation_failures": cycle_generation_failures,
            "new_unit_continuity_failures": cycle_continuity_failures,
            "all_active_continuity_ok": all_active_continuity_ok,
            "cycle_latency_s": latency,
        })

        if len(after) >= POPULATION_LIMIT:
            break

    final_units = list(runtime.active_units())
    final_continuity_failures = sum(
        not continuity_to_initial(unit, initial_unit)[0]
        for unit in final_units
    )
    latencies = [r["cycle_latency_s"] for r in rows]

    return {
        "test": "GENERATIONAL_CONTINUITY_UNDER_LOAD",
        "measured_runtime_s": time.perf_counter() - run_start,
        "execution_cycles": len(rows),
        "final_population": len(final_units),
        "max_generation": max(x.generation for x in final_units),
        "observed_new_units": len(new_unit_records),
        "known_object_count": len(known_objects),
        "known_identifier_count": len(known_ids),
        "operation_count_failures": pair_count_failures,
        "duplicate_identifier_failures": duplicate_id_failures,
        "parent_reference_failures": parent_reference_failures,
        "generation_step_failures": generation_step_failures,
        "continuity_failures": continuity_failures,
        "final_active_continuity_failures": final_continuity_failures,
        "retention_failures": retention_failures,
        "cycle_latency_s": {
            "min": min(latencies),
            "mean": statistics.fmean(latencies),
            "median": statistics.median(latencies),
            "p95": percentile(latencies, 0.95),
            "p99": percentile(latencies, 0.99),
            "max": max(latencies),
        },
        "new_unit_records": new_unit_records,
        "cycles": rows,
    }


if __name__ == "__main__":
    runtime = load_private_runtime()
    print(measure(runtime))