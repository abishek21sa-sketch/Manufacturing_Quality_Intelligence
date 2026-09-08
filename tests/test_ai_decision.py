import pandas as pd
from mqi.data.synthetic import generate_process_data, FEATURES
from mqi.ai.model import train_temporal, coefficient_root_causes
from mqi.ai.anomaly import fit_anomaly_detector, anomaly_scores
from mqi.decision.engine import recommend

def test_model_metrics_are_valid():
    df=generate_process_data(2200)
    model, m, scored=train_temporal(df)
    assert 0.5 <= m.roc_auc <= 1
    assert 0 <= m.average_precision <= 1
    assert len(scored)==440

def test_root_causes_return_features():
    df=generate_process_data(1500)
    model,_,_=train_temporal(df)
    roots=coefficient_root_causes(model,df.iloc[[10]][FEATURES],3)
    assert len(roots)==3 and 'feature' in roots[0]

def test_anomaly_scores_shape():
    df=generate_process_data(1000)
    model=fit_anomaly_detector(df.iloc[:800])
    s=anomaly_scores(model,df.iloc[800:])
    assert len(s)==200

def test_decision_has_action():
    df=generate_process_data(1600)
    model,_,_=train_temporal(df)
    d=recommend(model,df.iloc[[100]][FEATURES],1000)
    assert d.action and 0 <= d.risk <= 1

def test_decision_contains_corrective_actions():
    df=generate_process_data(1600)
    model,_,_=train_temporal(df)
    d=recommend(model,df.iloc[[120]][FEATURES],500)
    assert len(d.corrective_actions)==4
