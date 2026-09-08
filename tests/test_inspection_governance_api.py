from fastapi.testclient import TestClient
from mqi.service.api import app


def test_adaptive_inspection_certificate_endpoint():
    payload={
      'prior_bad':[.25,.12],
      'transitions':[[[.96,.04],[.20,.80]],[[.97,.03],[.25,.75]]],
      'sensitivity':[[0,.90,.97],[0,.88,.96]],
      'specificity':[[1,.93,.98],[1,.92,.98]],
      'inspection_cost':[[0,2.0,4.0],[0,2.5,4.5]],
      'capacity_use':[0,1,2],
      'escape_cost':[45.0,60.0],'correction_cost':[8.0,10.0],
      'horizon':3,'capacity_per_period':1
    }
    r=TestClient(app).post('/v1/governance/adaptive-inspection-certificate',json=payload)
    assert r.status_code==200, r.text
    assert r.headers['X-Request-ID'].startswith('mqi-')
    assert float(r.headers['X-Response-Time-Ms']) >= 0
    b=r.json(); assert b['verification']['valid'] is True
    assert b['certificate']['inspection_policy_write_allowed'] is False
    assert b['certificate']['decision_state']=='QUALITY_ENGINEER_REVIEW'
