from copy import deepcopy
from mqi.governance import build_inspection_certificate, verify_inspection_certificate


def test_inspection_certificate_binds_msa_capacity_and_economics():
    req={'sensitivity':[[0,.92,.97],[0,.90,.96]],'specificity':[[1,.94,.98],[1,.91,.97]],'capacity_use':[0,1,2],'capacity_per_period':1}
    sol={'method':'ECON-SPC-P','first_action':[1,0],'expected_cost':70,'no_inspection_expected_cost':100,'modeled_cost_avoidance':30,'production_write_allowed':False}
    c=build_inspection_certificate(request=req,solution=sol)
    assert c['decision_state']=='QUALITY_ENGINEER_REVIEW'
    assert c['inspection_policy_write_allowed'] is False
    assert verify_inspection_certificate(c)['valid'] is True
    bad=deepcopy(c); bad['expected_cost_reference']=1
    assert verify_inspection_certificate(bad)['valid'] is False


def test_poor_msa_is_flagged_even_when_policy_is_reviewable():
    req={'sensitivity':[[0,.65]],'specificity':[[1,.70]],'capacity_use':[0,1],'capacity_per_period':1}
    sol={'method':'ECON-SPC-P','first_action':[0],'expected_cost':90,'no_inspection_expected_cost':90,'modeled_cost_avoidance':0,'production_write_allowed':False}
    c=build_inspection_certificate(request=req,solution=sol)
    assert c['msa_review_flag']=='MEASUREMENT_SYSTEM_CAPABILITY_REVIEW'
