from __future__ import annotations
import json,time
from copy import deepcopy
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT/'src'):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
from mqi.optimization.msa_pomdp import solve_multiline_inspection_pomdp,no_inspection_expected_cost
from mqi.governance import build_inspection_certificate,verify_inspection_certificate

request={
 'prior_bad':[.25,.08],
 'transitions':[[[.94,.06],[.35,.65]],[[.97,.03],[.45,.55]]],
 'sensitivity':[[0,.90,.97],[0,.88,.96]],'specificity':[[1,.92,.98],[1,.91,.98]],
 'inspection_cost':[[0,12,22],[0,10,20]],'capacity_use':[0,1,2],
 'escape_cost':[180,140],'correction_cost':[35,30],'horizon':3,'capacity_per_period':2,
}
start=time.perf_counter()
r=solve_multiline_inspection_pomdp(np.array(request['prior_bad']),np.array(request['transitions']),np.array(request['sensitivity']),np.array(request['specificity']),np.array(request['inspection_cost']),np.array(request['capacity_use']),escape_cost=np.array(request['escape_cost']),correction_cost=np.array(request['correction_cost']),horizon=request['horizon'],capacity_per_period=request['capacity_per_period'])
baseline=no_inspection_expected_cost(np.array(request['prior_bad']),np.array(request['transitions']),np.array(request['escape_cost']),request['horizon'])
solution={'method':'ECON-SPC-P MSA-aware finite-horizon inspection POMDP','expected_cost':r.expected_cost,'no_inspection_expected_cost':baseline,'modeled_cost_avoidance':baseline-r.expected_cost,'first_action':list(r.first_action),'states_evaluated':r.states_evaluated,'production_write_allowed':False}
cert=build_inspection_certificate(request=request,solution=solution)
bad=deepcopy(cert); bad['inspection_policy_write_allowed']=True
tamper=verify_inspection_certificate(bad)
invalid_rejected=False
try:
    solve_multiline_inspection_pomdp(np.array([1.2]),np.array([[[1,0],[0,1]]]),np.array([[0,.9]]),np.array([[1,.9]]),np.array([[0,1.]]),np.array([0,1]),escape_cost=np.array([1.]),correction_cost=np.array([1.]),horizon=2,capacity_per_period=1)
except ValueError:
    invalid_rejected=True
elapsed=time.perf_counter()-start
checks={'policy_not_worse_than_no_inspection':r.expected_cost<=baseline+1e-8,'certificate_valid':verify_inspection_certificate(cert)['valid'] is True,'tampering_detected':tamper['valid'] is False,'invalid_belief_rejected':invalid_rejected,'inspection_write_blocked':cert['inspection_policy_write_allowed'] is False,'reference_runtime_under_30s':elapsed<30}
payload={'phase':'ENTERPRISE_OPERABILITY_V1','status':'PASS' if all(checks.values()) else 'HOLD','checks':checks,'runtime_seconds':elapsed,'expected_cost_reference':r.expected_cost,'no_inspection_expected_cost_reference':baseline,'certificate_sha256':cert['certificate_sha256'],'claim_boundary':'Model-based quality economics and MSA uncertainty only; inspection plan execution is blocked.'}
(ROOT/'artifacts'/'enterprise_operability.json').write_text(json.dumps(payload,indent=2,sort_keys=True,default=str))
print(json.dumps({'status':payload['status'],'checks':checks,'runtime_seconds':round(elapsed,3)},indent=2))
if payload['status']!='PASS': raise SystemExit('MQI_ENTERPRISE_OPERABILITY=HOLD')
print('MQI_ENTERPRISE_OPERABILITY=PASS')
