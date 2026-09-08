from __future__ import annotations
from tenx.engine import run_decision
from campaign.engine import run_campaign
from empirical.backbone import run_empirical_reference

def lifecycle_report():
    d=run_decision(41); v=d['model_validation']; metric=float(v.get('value', v.get('brier',0)) or 0)
    preds=d.get('predictions') or d.get('prediction') or {}; vals=[]
    if isinstance(preds,dict): vals=[float(x) for x in preds.values() if isinstance(x,(int,float))]
    spread=(max(vals)-min(vals)) if len(vals)>1 else 0.0
    state='RECALIBRATE' if metric>.24 else ('DRIFT_WATCH' if spread>.75 else 'INSPECTION_READY')
    public_data=d.get('public_data_backbone',{})
    return {'public_data_state':public_data.get('dataset_state'),'public_evidence_gate':d.get('public_evidence_gate'),'model_family':d['ml_family'],'target':d['prediction_target'],'validation':v,'risk_score_spread':round(spread,5),'model_state':state,'retrain_trigger':'retrain/recalibrate boosted defect model when Brier/log-loss exceeds release band or line/shift PSI exceeds threshold','monitoring':['calibration by line','defect recall','PSI by shift/tool wear','false-negative escape rate','prediction-to-inspection allocation lift'],'registry_state':'DEFECT_MODEL_SHADOW' if state!='INSPECTION_READY' else 'DEFECT_MODEL_ACTIVE','source_mode':run_empirical_reference().get('data_mode')}

def run_agent():
    d=run_decision(41); life=lifecycle_report(); c=run_campaign(); steps=['load SPC/MSA state','predict lot/line defect risk','check measurement-system discrimination']
    state='QUALITY_REVIEW'
    public_gate=d.get('public_evidence_gate')
    if public_gate=='REFERENCE_MODE_HOLD_FOR_REAL_DATA_CLAIM':
        steps.append('flag external public-data acquisition gap; prohibit real-data performance claim')
        state='REFERENCE_MODE_HOLD'
    if life['model_state']=='RECALIBRATE': steps += ['hold risk-led inspection reduction','recalibrate defect model','increase conservative sampling']; state='MODEL_HOLD'
    else: steps += ['allocate scarce inspection with GAGE-SHIELD','evaluate recurring policy with ECON-SPC-P','compare containment vs escape cost','build disposition queue']
    return {'agent':'Quality Decision Engineer','objective':'spend inspection capacity where it most reduces expected escape exposure','prediction':d.get('prediction') or d.get('predictions'),'decision':d['decision'],'decision_state':state,'chosen_tool_sequence':steps,'why_this_sequence':'model calibration and gage quality jointly decide whether risk predictions are actionable or containment must dominate','challenge':d['counterfactual'],'ml_lifecycle':life,'campaign_state':c.get('state'),'operator_actions':['review high-risk line/lot','inspect gage capability','approve sampling/containment policy','open CAPA if recurring signal persists'],'human_authority':d['human_authority'],'autonomous_execution':False}
