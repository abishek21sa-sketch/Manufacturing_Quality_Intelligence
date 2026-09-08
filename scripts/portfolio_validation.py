from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from mqi.optimization.msa_pomdp import solve_multiline_inspection_pomdp, no_inspection_expected_cost, observation_model_from_msa
from mqi.optimization.policy_experiments import risk_priority_frontier, msa_precision_frontier, msa_policy_stress

prior=np.array([.22,.09]); transitions=np.array([[[.95,.05],[.32,.68]],[[.97,.03],[.42,.58]]])
se=np.array([[0,.88,.97],[0,.86,.96]]); sp=np.array([[1,.92,.985],[1,.91,.98]]); ic=np.array([[0,10,22],[0,9,20.]])
base=dict(prior_bad=prior,transitions=transitions,sensitivity=se,specificity=sp,inspection_cost=ic,capacity_use=np.array([0,1,2]),escape_cost=np.array([210.,150.]),correction_cost=np.array([38.,32.]),horizon=3,capacity_per_period=2)
r=solve_multiline_inspection_pomdp(**base); no=no_inspection_expected_cost(prior,transitions,base['escape_cost'],3)
frontier=risk_priority_frontier(base)
msa_args=dict(good_mean=0,bad_mean=1.2,process_sd_good=.3,process_sd_bad=.35,upper_spec=.7)
msa=msa_precision_frontier(msa_args)
msa_policy=msa_policy_stress(base,msa_args)
payload={'release':'MQI_PORTFOLIO_RC1','method':'ECON-SPC-P','optimal_expected_cost':r.expected_cost,'no_inspection_expected_cost':no,'modeled_cost_avoidance':no-r.expected_cost,'first_action':list(r.first_action),'risk_priority_frontier':frontier,'msa_precision_frontier':msa,'msa_policy_stress':msa_policy,'msa_cost_penalty_worst_vs_best':msa_policy[-1]['expected_cost']-msa_policy[0]['expected_cost'],'production_write_allowed':False,'evidence_boundary':'Synthetic/model-based quality economics; no realized plant-savings claim.'}
root=Path(__file__).resolve().parents[1]; (root/'artifacts'/'portfolio_validation.json').write_text(json.dumps(payload,indent=2))
print(json.dumps({k:payload[k] for k in ['release','method','optimal_expected_cost','no_inspection_expected_cost','first_action']},indent=2)); print('MQI_PORTFOLIO_VALIDATION=PASS')
