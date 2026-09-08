from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))
from mqi.optimization.inspection import optimize_multi_station
from mqi.simulation.monte_carlo import simulate_quality
from mqi.data.synthetic import generate_process_data
from mqi.quality.spc import capability

df = generate_process_data(500, seed=42)
cap = capability(df['dimension_error_mm'], -0.20, 0.20)
assert cap.cp > 0 and cap.cpk > 0
sim1 = simulate_quality(.1, 1000, trials=2000, seed=42)
sim2 = simulate_quality(.1, 1000, trials=2000, seed=42)
assert sim1 == sim2
opt = optimize_multi_station({'S1':.04,'S2':.12,'S3':.20},{'S1':100,'S2':120,'S3':80},110)
assert opt.status == 'OPTIMAL' and opt.inspected_units <= 110
print('DIAGNOSTICS PASS')
print(f'capability_cp={cap.cp:.6f} cpk={cap.cpk:.6f}')
print(f'simulation_reproducible={sim1 == sim2}')
print(f'or_status={opt.status} objective={opt.expected_total_cost:.6f} inspected={opt.inspected_units:.1f}/{opt.capacity}')
