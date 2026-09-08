from itertools import product
from mqi.optimization.inspection import optimize_multi_station


def brute_force(risks, volumes, capacity, fractions, inspection_cost=1.0, escape_cost=200.0, effectiveness=0.95):
    stations = list(risks)
    best = None
    for combo in product(fractions, repeat=len(stations)):
        if sum(volumes[s] * f for s, f in zip(stations, combo)) > capacity + 1e-9:
            continue
        cost = sum(volumes[s] * f * inspection_cost + volumes[s] * risks[s] * (1-f*effectiveness) * escape_cost
                   for s, f in zip(stations, combo))
        if best is None or cost < best[0]:
            best = (cost, combo)
    return best


def test_milp_matches_enumeration_oracle():
    risks = {"cut": 0.04, "grind": 0.12, "finish": 0.20}
    volumes = {"cut": 100, "grind": 120, "finish": 80}
    fractions = (0.0, 0.25, 0.5, 1.0)
    result = optimize_multi_station(risks, volumes, capacity=110, fractions=fractions)
    oracle_cost, _ = brute_force(risks, volumes, 110, fractions)
    assert result.status == "OPTIMAL"
    assert result.inspected_units <= result.capacity + 1e-9
    assert abs(result.expected_total_cost - oracle_cost) < 1e-6
    assert set(result.fractions) == set(risks)


def test_milp_zero_capacity_is_feasible_with_zero_fraction():
    result = optimize_multi_station({"a": .1}, {"a": 100}, 0)
    assert result.status == "OPTIMAL"
    assert result.fractions["a"] == 0.0
