#!/usr/bin/env python3
"""
SKYNET 1_1_0
STRESS 09 — LONG SUSTAINED STRESS
PUBLIC DISCLOSURE EDITION

Public benchmark harness for sustained runtime measurement.

The private runtime adapter and reconstruction-sensitive implementation
are intentionally not included in this disclosure file.

This harness measures:
- sustained cycle latency;
- cycles per second;
- operation throughput;
- secondary-event throughput;
- population progression;
- native event-unit production;
- depth progression;
- raw per-cycle telemetry;
- stop reason.

No performance threshold is used.
Measured values are written as observed.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RESULT = Path("STRESS_09_SKYNET_RUNTIME_RESULT_PUBLIC_1_1_0.txt")

MAX_CYCLES = 96
POPULATION_LIMIT = 256


def file_identity(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    return {
        "name": path.name,
        "lines": len(text.splitlines()),
        "characters": len(text),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def environment_info() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
    }


def load_private_runtime() -> Any:
    raise RuntimeError(
        "Private runtime adapter is not included in the public disclosure edition."
    )


def population_size(runtime: Any) -> int:
    return int(runtime.population_size())


def max_depth(runtime: Any) -> int:
    return int(runtime.max_depth())


def execute_cycle(runtime: Any, first_cycle: bool) -> Any:
    return runtime.execute_measurement_cycle(first_cycle=first_cycle)


def main() -> None:
    benchmark_identity = file_identity(Path(__file__))
    started = datetime.now(timezone.utc).isoformat()

    runtime = load_private_runtime()

    cycles: list[dict[str, Any]] = []
    latencies: list[float] = []

    total_operations = 0
    total_secondary_events = 0
    total_new_units = 0

    stop_reason = "MAX_CYCLES"
    start_ns = time.perf_counter_ns()

    try:
        for cycle in range(1, MAX_CYCLES + 1):
            before = population_size(runtime)

            cycle_start_ns = time.perf_counter_ns()
            measurement = execute_cycle(runtime, first_cycle=(cycle == 1))
            cycle_end_ns = time.perf_counter_ns()

            latency_s = (cycle_end_ns - cycle_start_ns) / 1_000_000_000.0
            latencies.append(latency_s)

            after = population_size(runtime)
            new_units = int(measurement.new_units)
            operations = int(measurement.operation_count)
            secondary_events = int(measurement.secondary_event_count)
            native_event_states = int(measurement.native_event_state_count)

            total_operations += operations
            total_secondary_events += secondary_events
            total_new_units += new_units

            row = {
                "cycle": cycle,
                "population_before": before,
                "population_after": after,
                "new_units": new_units,
                "operations": operations,
                "secondary_events": secondary_events,
                "native_event_states": native_event_states,
                "max_depth": max_depth(runtime),
                "latency_s": latency_s,
            }
            cycles.append(row)

            print(
                f"CYCLE {cycle:03d} | "
                f"POP {before}->{after} | "
                f"NEW {new_units} | "
                f"OPS {operations} | "
                f"SECONDARY {secondary_events} | "
                f"DEPTH {row['max_depth']} | "
                f"LATENCY {latency_s:.9f}s",
                flush=True,
            )

            if after >= POPULATION_LIMIT:
                stop_reason = "TEST_POPULATION_LIMIT"
                break

    except KeyboardInterrupt:
        stop_reason = "USER_INTERRUPT"

    end_ns = time.perf_counter_ns()
    runtime_s = (end_ns - start_ns) / 1_000_000_000.0
    execution_cycles = len(cycles)

    result = {
        "test": "STRESS_09_LONG_SUSTAINED_STRESS",
        "version": "SKYNET 1_1_0",
        "disclosure": "PUBLIC",
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "benchmark_identity": benchmark_identity,
        "environment": environment_info(),
        "configuration": {
            "max_cycles": MAX_CYCLES,
            "population_limit": POPULATION_LIMIT,
        },
        "stop_reason": stop_reason,
        "execution_cycles": execution_cycles,
        "final_population": population_size(runtime),
        "max_depth": max_depth(runtime),
        "runtime_s": runtime_s,
        "total_operations": total_operations,
        "total_secondary_events": total_secondary_events,
        "total_new_units": total_new_units,
        "cycles_per_second": execution_cycles / runtime_s if runtime_s else 0.0,
        "operations_per_second": total_operations / runtime_s if runtime_s else 0.0,
        "secondary_events_per_second": (
            total_secondary_events / runtime_s if runtime_s else 0.0
        ),
        "cycle_latency_s": {
            "min": min(latencies, default=0.0),
            "mean": statistics.fmean(latencies) if latencies else 0.0,
            "median": statistics.median(latencies) if latencies else 0.0,
            "p95": percentile(latencies, 0.95),
            "p99": percentile(latencies, 0.99),
            "max": max(latencies, default=0.0),
        },
        "cycles": cycles,
    }

    RESULT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("=" * 78)
    print(f"STOP_REASON = {stop_reason}")
    print(f"EXECUTION_CYCLES = {execution_cycles}")
    print(f"FINAL_POPULATION = {result['final_population']}")
    print(f"MAX_DEPTH = {result['max_depth']}")
    print(f"RUNTIME_S = {runtime_s:.9f}")
    print(f"RESULT = {RESULT}")


if __name__ == "__main__":
    main()
