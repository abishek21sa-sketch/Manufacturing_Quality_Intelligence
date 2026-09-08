from __future__ import annotations
import numpy as np
from .msa_pomdp import solve_multiline_inspection_pomdp, observation_model_from_msa


def risk_priority_frontier(base: dict, line0_beliefs=(.02,.08,.15,.25,.4,.6)) -> list[dict]:
    rows=[]
    for b in line0_beliefs:
        p=dict(base); prior=np.asarray(base['prior_bad'],float).copy(); prior[0]=b; p['prior_bad']=prior
        r=solve_multiline_inspection_pomdp(**p)
        rows.append({'line0_bad_belief':float(b),'expected_cost':r.expected_cost,'first_action':list(r.first_action)})
    return rows


def msa_precision_frontier(model_args: dict, measurement_sds=(.05,.15,.35,.7,1.5), replicates=1) -> list[dict]:
    rows=[]
    for sd in measurement_sds:
        m=observation_model_from_msa(**model_args,measurement_sd=float(sd),replicates=replicates)
        rows.append({'measurement_sd':float(sd),'sensitivity':m.sensitivity,'specificity':m.specificity,'effective_measurement_sd':m.measurement_sd_effective})
    return rows


def msa_policy_stress(
    base: dict,
    model_args: dict,
    measurement_sds=(.05, .15, .35, .7, 1.5),
    action_replicates=(1, 3),
) -> list[dict]:
    """Propagate measurement-system degradation into the inspection policy itself.

    Each positive inspection action is mapped to a replicate count. The MSA model
    supplies action-specific sensitivity/specificity, after which ECON-SPC-P is
    re-solved. This connects Gage R&R evidence to economic policy consequences
    rather than reporting metrology metrics in isolation.
    """
    if len(action_replicates) != np.asarray(base['sensitivity']).shape[1] - 1:
        raise ValueError('action_replicates must define every positive inspection action')
    lines=np.asarray(base['prior_bad']).size
    rows=[]
    for sd in measurement_sds:
        se=np.zeros((lines, len(action_replicates)+1), float)
        sp=np.ones_like(se)
        action_models=[]
        for a,rep in enumerate(action_replicates, start=1):
            m=observation_model_from_msa(**model_args, measurement_sd=float(sd), replicates=int(rep))
            se[:,a]=m.sensitivity
            sp[:,a]=m.specificity
            action_models.append({'action':a,'replicates':int(rep),'sensitivity':m.sensitivity,'specificity':m.specificity})
        params=dict(base); params['sensitivity']=se; params['specificity']=sp
        result=solve_multiline_inspection_pomdp(**params)
        rows.append({
            'measurement_sd':float(sd),
            'expected_cost':float(result.expected_cost),
            'first_action':list(result.first_action),
            'action_models':action_models,
        })
    return rows
