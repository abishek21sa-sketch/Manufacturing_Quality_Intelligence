import numpy as np
from mqi.quality.spc import individuals_chart, capability, detect_rule1, p_chart, acceptance_sample_size
from mqi.quality.pfmea import FailureMode, rank_failure_modes
from mqi.quality.doe import full_factorial_two_level, estimate_main_effects
from mqi.quality.msa import crossed_gage_rr
from mqi.data.synthetic import generate_msa_data

def test_individuals_limits_center():
    x = [1,2,3,4,5]
    lim = individuals_chart(x)
    assert lim.center == 3
    assert lim.lcl < lim.center < lim.ucl

def test_capability_known():
    rng=np.random.default_rng(1); x=rng.normal(0,1,10000)
    c=capability(x,-3,3)
    assert 0.95 < c.cp < 1.05

def test_rule1_detects_outlier():
    lim=individuals_chart([0,0.1,-0.1,0.05,-0.05])
    assert detect_rule1([0,10],lim)==[1]

def test_p_chart_bounds():
    lim=p_chart([0,0,1,0,0], subgroup_size=50)
    assert 0 <= lim.lcl <= lim.ucl <= 1

def test_acceptance_sampling_positive():
    assert acceptance_sample_size(0.01) >= 1

def test_pfmea_rank():
    a=FailureMode('a',9,8,7); b=FailureMode('b',3,3,3)
    assert rank_failure_modes([b,a])[0].name=='a'

def test_doe_four_runs():
    d=full_factorial_two_level({'temp':(1,2),'pressure':(3,4)})
    assert len(d)==4
    d['y']=2*d['temp_coded']+d['pressure_coded']
    e=estimate_main_effects(d,'y',['temp_coded','pressure_coded'])
    assert e['temp_coded']==4

def test_msa_finite():
    r=crossed_gage_rr(generate_msa_data())
    assert 0 <= r.percent_study_variation <= 100

from mqi.quality.improvement import quality_kpis, defect_pareto, identify_bottleneck
from mqi.data.synthetic import generate_process_data

def test_quality_improvement_kpis():
    df=generate_process_data(500)
    k=quality_kpis(df)
    assert 0 <= k.first_pass_yield <= 1 and k.cost_of_poor_quality >= 0
    p=defect_pareto(df)
    assert p['count'].sum() == df['defect'].sum()

def test_bottleneck_identification():
    r=identify_bottleneck({'cut':1.0,'coat':1.5,'inspect':0.8}, available_time=480, demand=350)
    assert r['bottleneck']=='coat' and not r['demand_feasible']
