import numpy as np
from fastapi.testclient import TestClient
from mqi.optimization.msa_pomdp import observation_model_from_msa, solve_multiline_inspection_pomdp, no_inspection_expected_cost
from mqi.service.api import app


def params():
    prior=np.array([.25,.08])
    P=np.array([[[.94,.06],[.35,.65]],[[.97,.03],[.45,.55]]],float)
    sensitivity=np.array([[0,.90,.97],[0,.88,.96]])
    specificity=np.array([[1,.92,.98],[1,.91,.98]])
    costs=np.array([[0,12,22],[0,10,20]],float)
    return dict(prior_bad=prior,transitions=P,sensitivity=sensitivity,specificity=specificity,inspection_cost=costs,capacity_use=np.array([0,1,2]),escape_cost=np.array([180,140.]),correction_cost=np.array([35,30.]),horizon=3,capacity_per_period=2)


def test_exact_policy_beats_or_matches_no_inspection():
    p=params(); r=solve_multiline_inspection_pomdp(**p)
    baseline=no_inspection_expected_cost(p['prior_bad'],p['transitions'],p['escape_cost'],p['horizon'])
    assert r.expected_cost <= baseline + 1e-8
    assert len(r.first_action)==2


def test_msa_replicates_improve_effective_measurement_precision():
    a=observation_model_from_msa(good_mean=0,bad_mean=1.2,process_sd_good=.3,process_sd_bad=.35,measurement_sd=.6,upper_spec=.7,replicates=1)
    b=observation_model_from_msa(good_mean=0,bad_mean=1.2,process_sd_good=.3,process_sd_bad=.35,measurement_sd=.6,upper_spec=.7,replicates=4)
    assert b.measurement_sd_effective < a.measurement_sd_effective
    assert b.specificity >= a.specificity


def test_api_returns_governed_policy():
    p=params(); payload={k:(v.tolist() if hasattr(v,'tolist') else v) for k,v in p.items()}
    r=TestClient(app).post('/v1/optimize-adaptive-inspection',json=payload)
    assert r.status_code==200
    body=r.json(); assert body['production_write_allowed'] is False
    assert body['expected_cost'] <= body['no_inspection_expected_cost'] + 1e-8


def test_msa_degradation_propagates_into_policy_cost_and_action():
    from mqi.optimization.policy_experiments import msa_policy_stress
    import numpy as np
    base=dict(
        prior_bad=np.array([.22,.09]),
        transitions=np.array([[[.95,.05],[.32,.68]],[[.97,.03],[.42,.58]]]),
        sensitivity=np.zeros((2,3)), specificity=np.ones((2,3)),
        inspection_cost=np.array([[0,10,22],[0,9,20.]]), capacity_use=np.array([0,1,2]),
        escape_cost=np.array([210.,150.]), correction_cost=np.array([38.,32.]), horizon=3, capacity_per_period=2,
    )
    rows=msa_policy_stress(base,dict(good_mean=0,bad_mean=1.2,process_sd_good=.3,process_sd_bad=.35,upper_spec=.7),measurement_sds=(.05,1.5))
    assert rows[1]['expected_cost'] > rows[0]['expected_cost']
    assert rows[0]['first_action'] != rows[1]['first_action']
