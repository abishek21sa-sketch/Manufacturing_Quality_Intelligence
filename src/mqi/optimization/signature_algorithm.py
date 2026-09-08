"""ECON-SPC-P adaptive inspection reference contract."""

from itertools import product


def choose_inspection(prior_bad, sensitivity, specificity, inspection_cost, escape_cost, capacity):
    n = len(prior_bad)
    if not all(len(x) == n for x in (sensitivity, specificity, inspection_cost, escape_cost)):
        raise ValueError("all line inputs must have equal length")
    best = None
    for actions in product((0, 1), repeat=n):
        if sum(actions) > capacity:
            continue
        total = 0.0
        for p, se, sp, cost, escape, action in zip(prior_bad, sensitivity, specificity, inspection_cost, escape_cost, actions):
            no_inspection = p * escape
            inspected = cost + p * (1.0 - se) * escape
            total += inspected if action else no_inspection
        row = {"actions": actions, "expected_cost": total}
        if best is None or total < best["expected_cost"]:
            best = row
    return best


def ablation(prior_bad, sensitivity, specificity, inspection_cost, escape_cost, capacity):
    """Remove gage discrimination by replacing it with a non-informative test."""
    return choose_inspection(prior_bad, [0.5] * len(prior_bad), [0.5] * len(prior_bad), inspection_cost, escape_cost, capacity)


def sensitivity(prior_bad, sensitivity, specificity, inspection_cost, escape_cost, capacity, capacity_delta=0):
    return choose_inspection(prior_bad, sensitivity, specificity, inspection_cost, escape_cost, capacity + capacity_delta)
