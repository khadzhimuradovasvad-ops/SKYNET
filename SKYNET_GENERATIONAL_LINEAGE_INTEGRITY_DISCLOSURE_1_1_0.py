"""
SKYNET 1_1_0
GENERATIONAL CONTINUITY INTEGRITY TEST
PUBLIC DISCLOSURE EDITION

PURPOSE
-------
This file documents the public validation procedure used to evaluate
generational continuity during an autonomous SKYNET runtime.

Implementation-specific integration with the private SKYNET runtime is
intentionally omitted. The complete internal test stand remains private.

This disclosure edition is not a standalone executable reproduction of
the private validation harness.

PRIVATE INTEGRATION BOUNDARY
----------------------------
The following are intentionally not disclosed here:
- private runtime import/binding;
- private execution-cycle invocation;
- internal state extraction;
- internal succession bindings;
- implementation-specific Core construction;
- reconstruction-level architecture.

The published result artifact is produced by the complete internal test
stand, not by this disclosure edition.
"""

from copy import deepcopy
from typing import Any, Dict, Iterable, Optional, Tuple


TEST_POPULATION_LIMIT = 32


def state_equal_except_generation(
    parent_state: Dict[str, Any],
    child_state: Dict[str, Any],
) -> bool:
    """
    Compare transferred observable state while evaluating generation
    progression independently.
    """
    left = deepcopy(parent_state)
    right = deepcopy(child_state)

    left.pop("generation", None)
    right.pop("generation", None)

    return left == right


def expected_pair_count(core_count: int) -> int:
    """
    Expected number of unordered pair interactions for the population
    present at the beginning of an execution cycle.
    """
    if core_count < 0:
        raise ValueError("core_count must be non-negative")

    return core_count * (core_count - 1) // 2


def validate_pair_count(
    core_count_before_cycle: int,
    observed_interactions: int,
) -> bool:
    return observed_interactions == expected_pair_count(core_count_before_cycle)


def validate_descendant_edge(
    *,
    parent_exists: bool,
    parent_generation: int,
    child_generation: int,
    previous_parent_id: Optional[str],
    observed_parent_id: str,
    parent_state: Dict[str, Any],
    child_state: Dict[str, Any],
) -> Dict[str, bool]:
    """
    Public validation logic for one observed parent -> descendant event.

    No private mechanism that creates the descendant is exposed here.
    """
    generation_ok = child_generation == parent_generation + 1

    single_parent_ok = (
        previous_parent_id is None
        or previous_parent_id == observed_parent_id
    )

    state_edge_ok = state_equal_except_generation(
        parent_state,
        child_state,
    )

    return {
        "parent_exists": bool(parent_exists),
        "generation_ok": generation_ok,
        "single_parent_ok": single_parent_ok,
        "state_edge_ok": state_edge_ok,
    }


def validate_continuity_path(
    *,
    current_id: str,
    initial_core_id: str,
    parent_by_core: Dict[str, Optional[str]],
) -> Tuple[bool, bool]:
    """
    Follow recorded succession relations back toward the initial Core.

    Returns:
        (continuity_to_initial_core, cycle_detected)

    This is a continuity check only. It does not impose a binary-tree
    model or a fixed reproduction schedule on SKYNET.
    """
    seen = set()
    cursor: Optional[str] = current_id

    while cursor is not None:
        if cursor in seen:
            return False, True

        seen.add(cursor)

        if cursor == initial_core_id:
            return True, False

        cursor = parent_by_core.get(cursor)

    return False, False


def validate_population_retention(
    ids_before_cycle: Iterable[str],
    ids_after_cycle: Iterable[str],
) -> bool:
    """
    Confirm that Cores present before a cycle remain represented after it.
    """
    before = set(ids_before_cycle)
    after = set(ids_after_cycle)
    return before.issubset(after)


def validate_unique_core_ids(core_ids: Iterable[str]) -> bool:
    ids = list(core_ids)
    return len(ids) == len(set(ids))


def final_result(
    *,
    descendants_seen: int,
    duplicate_id_failures: int,
    parent_failures: int,
    generation_failures: int,
    multiple_parent_failures: int,
    continuity_failures: int,
    continuity_cycle_failures: int,
    state_transfer_failures: int,
    population_retention_failures: int,
    pair_count_failures: int,
) -> str:
    failures = (
        duplicate_id_failures
        + parent_failures
        + generation_failures
        + multiple_parent_failures
        + continuity_failures
        + continuity_cycle_failures
        + state_transfer_failures
        + population_retention_failures
        + pair_count_failures
    )

    return "PASS" if descendants_seen > 0 and failures == 0 else "FAIL"


# =============================================================================
# PUBLIC PROCEDURE
# =============================================================================
#
# The complete internal stand performs the following procedure:
#
# 1. Start the autonomous runtime from one initial Core.
#
# 2. Execute normal runtime cycles.
#
#    PRIVATE INTEGRATION BOUNDARY:
#    Exact runtime construction and execution calls are intentionally omitted.
#
# 3. Before each cycle, capture the observable population identity and the
#    state required for independent post-cycle validation.
#
#    PRIVATE INTEGRATION BOUNDARY:
#    Internal state-access paths are intentionally omitted.
#
# 4. After each cycle:
#       - verify uniqueness of Core identifiers;
#       - verify retention of the pre-cycle population;
#       - compare observed pair interactions with N * (N - 1) / 2;
#       - identify newly observed descendants.
#
# 5. For each observed descendant:
#       - verify that its recorded parent existed before the cycle;
#       - verify generation progression by exactly one;
#       - verify that one descendant is not associated with conflicting
#         parent identities;
#       - verify transferred observable state independently of generation.
#
# 6. For every observed Core, follow recorded succession relations toward
#    the initial Core and verify:
#       - continuity reaches the initial Core;
#       - no cycle occurs in the recorded parent relation.
#
#    This validation does not assume that a Core must produce a descendant
#    on every cycle and does not impose a binary-tree reproduction model.
#
# 7. Continue until the external test population ceiling is reached or the
#    input/runtime terminates normally.
#
# TEST_POPULATION_LIMIT is an external test-safety ceiling only. It is not
# a SKYNET population limit.
#
# 8. Report the observed execution totals and all validation-failure counters.
#
# =============================================================================
# PUBLISHED RESULT FORMAT
# =============================================================================
#
# STOP_REASON
# EXECUTION_CYCLES
# FINAL_CORES
# MAX_GENERATION
# DESCENDANTS_SEEN
# DUPLICATE_ID_FAILURES
# PARENT_FAILURES
# GENERATION_FAILURES
# MULTIPLE_PARENT_FAILURES
# CONTINUITY_FAILURES
# CONTINUITY_CYCLE_FAILURES
# STATE_TRANSFER_FAILURES
# POPULATION_RETENTION_FAILURES
# PAIR_COUNT_FAILURES
# RESULT
#
# The complete result is distributed separately as the corresponding
# public result artifact.
# =============================================================================
