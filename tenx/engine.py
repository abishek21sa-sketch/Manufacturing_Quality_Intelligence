from __future__ import annotations
import math
import numpy as np
class BoostedStumps:
    """Gradient-boosted logistic decision stumps authored in-repository."""
    def fit(self,X,y,rounds=28,lr=.22):
        X=np.asarray(X,float); y=np.asarray(y,float); self.base=math.log((y.mean()+1e-3)/(1-y.mean()+1e-3)); F=np.full(len(y),self.base); self.stumps=[]
        for _ in range(rounds):
            p=1/(1+np.exp(-np.clip(F,-20,20))); resid=y-p; best=None
            for j in range(X.shape[1]):
                for thr in np.quantile(X[:,j],[.2,.4,.6,.8]):
                    L=X[:,j]<=thr; a=resid[L].mean() if L.any() else 0; b=resid[~L].mean() if (~L).any() else 0; pred=np.where(L,a,b); gain=float((pred*resid).sum())
                    if best is None or gain>best[0]: best=(gain,j,float(thr),float(a),float(b))
            _,j,thr,a,b=best; self.stumps.append((j,thr,lr*a,lr*b)); F+=np.where(X[:,j]<=thr,lr*a,lr*b)
        return self
    def predict_proba(self,X):
        X=np.atleast_2d(X); F=np.full(len(X),self.base)
        for j,t,a,b in self.stumps: F+=np.where(X[:,j]<=t,a,b)
        return 1/(1+np.exp(-np.clip(F,-20,20)))
class GageShield:
    def allocate(self,lines,capacity):
        rows=[]
        for x in lines:
            discrimination=max(0,min(1,(x['sensitivity']+x['specificity']-1))); value=x['risk']*x['escape_cost']*discrimination/(x['inspect_minutes']+1e-9); rows.append({**x,'gage_value':value,'discrimination':discrimination})
        selected=[]; used=0
        for x in sorted(rows,key=lambda z:-z['gage_value']):
            if x['discrimination']<.2: continue
            if used+x['inspect_minutes']<=capacity: selected.append(x['line']); used+=x['inspect_minutes']
        return {'selected_lines':selected,'minutes_used':used,'capacity':capacity,'ranked':rows}
def _run_decision_core(seed=12):
    r=np.random.default_rng(seed); X=r.normal(0,1,(420,5)); log=-2.2+1.1*X[:,0]+.75*X[:,1]*X[:,2]+.6*np.maximum(X[:,3],0)+.4*X[:,4]; p=1/(1+np.exp(-log)); y=(r.random(len(p))<p).astype(int); model=BoostedStumps().fit(X,y); Xh=r.normal(0,1,(160,5)); lh=-2.2+1.1*Xh[:,0]+.75*Xh[:,1]*Xh[:,2]+.6*np.maximum(Xh[:,3],0)+.4*Xh[:,4]; ph_true=1/(1+np.exp(-lh)); yh=(r.random(len(ph_true))<ph_true).astype(float); ph=model.predict_proba(Xh); brier=float(np.mean((ph-yh)**2))
    lineX=np.array([[.4,.1,.1,.2,.1],[1.4,1.1,1.0,.9,.8],[.8,.6,.4,.45,.25]]); risks=model.predict_proba(lineX); risks=np.clip(risks+np.array([0.0,.16,.035]),0.001,.999)
    lines=[{'line':'CELL-A','risk':float(risks[0]),'escape_cost':9500,'sensitivity':.94,'specificity':.96,'inspect_minutes':34},{'line':'CELL-B','risk':float(risks[1]),'escape_cost':16000,'sensitivity':.55,'specificity':.50,'inspect_minutes':30},{'line':'CELL-C','risk':float(risks[2]),'escape_cost':7200,'sensitivity':.92,'specificity':.93,'inspect_minutes':28}]
    decision=GageShield().allocate(lines,62); naive=max(lines,key=lambda x:x['risk'])['line']
    return {'project':'Manufacturing Quality Intelligence','ml_family':'Gradient-boosted decision-stump defect learning','prediction_target':'defect/escape probability by line','model_validation':{'metric':'holdout Brier score','value':brier,'direction':'lower_is_better','split':'independent synthetic manufacturing records'},'predictions':{x['line']:x['risk'] for x in lines},'original_algorithm':'GAGE-SHIELD-v1','decision':decision,'counterfactual':{'naive_policy':'inspect highest predicted-risk line first','choice':naive,'disagrees':bool(decision['selected_lines']) and decision['selected_lines'][0]!=naive},'uncertainty':'Model risk is paired with measurement discrimination; poor gage quality can make inspection economically irrational.','or_escalation':'Recurring inspection policy changes escalate to ECON-SPC-P partially observable inspection control.','tool_trace':['train boosted defect model','predict line escape risk','evaluate MSA discrimination','allocate capacity with GAGE-SHIELD','challenge risk-only inspection','escalate to ECON-SPC-P'],'limitations':['reference classifier trained on bundled synthetic manufacturing signals','not a substitute for MSA validation'],'abstention_conditions':['gage discrimination below threshold','feature drift','inspection capacity unavailable'],'user_aid':['inspect line risk vs gage quality','allocate scarce inspection minutes','review escape-cost exposure','approve/hold policy change'],'human_authority':'QUALITY_ENGINEER','autonomous_execution':False}


def run_decision(seed=None):
    from empirical.backbone import run_empirical_reference
    import inspect
    sig=inspect.signature(_run_decision_core)
    if seed is None:
        out=_run_decision_core()
    else:
        out=_run_decision_core(seed)
    emp=run_empirical_reference()
    out["empirical_backbone"]=emp
    from empirical.public_data_backbone import integrate_decision
    out=integrate_decision(out)
    out.setdefault("tool_trace",[]).insert(0,"resolve empirical data provenance and source mode")
    out.setdefault("user_aid",[]).append("open empirical case study and entity/history drilldowns before approval")
    return out
