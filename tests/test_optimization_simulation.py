from mqi.optimization.inspection import optimize_inspection, optimize_multi_station
from mqi.simulation.monte_carlo import simulate_quality

def test_inspection_returns_feasible():
    p=optimize_inspection(0.2,1000,max_inspections=500)
    assert p.sample_fraction <= 0.5

def test_higher_risk_not_less_inspection():
    a=optimize_inspection(0.01,1000); b=optimize_inspection(0.4,1000)
    assert b.sample_fraction >= a.sample_fraction

def test_multi_station_capacity():
    r=optimize_multi_station({'A':.1,'B':.2},{'A':100,'B':100},100)
    assert sum(100*f for f in r.fractions.values()) <= 100

def test_simulation_reproducible():
    a=simulate_quality(.1,1000,1000,seed=5); b=simulate_quality(.1,1000,1000,seed=5)
    assert a == b
