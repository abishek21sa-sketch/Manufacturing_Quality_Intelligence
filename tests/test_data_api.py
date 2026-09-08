from fastapi.testclient import TestClient
from mqi.data.synthetic import generate_process_data
from mqi.data.contracts import validate_process_frame
from mqi.service.api import app

def test_data_contract():
    r=validate_process_frame(generate_process_data(100))
    assert r.passed and r.rows==100

def test_health():
    c=TestClient(app); r=c.get('/health')
    assert r.status_code==200 and r.json()['status']=='ok'

def test_capability_endpoint():
    c=TestClient(app); r=c.post('/v1/capability',json={'values':[1,1.1,.9,1.05,.95],'lsl':0,'usl':2})
    assert r.status_code==200 and 'cpk' in r.json()

def test_simulate_endpoint():
    c=TestClient(app); r=c.post('/v1/simulate',json={'defect_probability':.05,'volume':1000,'trials':500})
    assert r.status_code==200 and r.json()['mean_defects'] > 0
