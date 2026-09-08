"""Governed assurance certificate for ECON-SPC-P adaptive inspection policies."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib, json
from typing import Any


def _canonical(x: Any) -> bytes:
    return json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode('utf-8')


def build_inspection_certificate(*, request: dict[str,Any], solution: dict[str,Any]) -> dict[str,Any]:
    first_action=list(solution.get('first_action',[]))
    capacity_use=list(request.get('capacity_use',[]))
    used=sum(int(capacity_use[int(action)]) for action in first_action) if capacity_use and all(0 <= int(action) < len(capacity_use) for action in first_action) else 10**9
    cap=int(request.get('capacity_per_period',0))
    def flat(rows):
        return [float(x) for row in rows for x in (row if isinstance(row,(list,tuple)) else [row])]
    sens=flat(request.get('sensitivity',[]))
    spec=flat(request.get('specificity',[]))
    expected=float(solution.get('expected_cost',float('inf')))
    baseline=float(solution.get('no_inspection_expected_cost',float('inf')))
    checks={
        'policy_solution_finite':expected < float('inf') and baseline < float('inf'),
        'optimized_cost_not_worse_than_no_inspection':expected <= baseline + 1e-8,
        'first_action_within_shared_capacity':used <= cap,
        'measurement_probabilities_valid':bool(sens and spec) and all(0<=x<=1 for x in sens+spec),
        'production_write_blocked':solution.get('production_write_allowed') is False,
    }
    state='QUALITY_ENGINEER_REVIEW' if all(checks.values()) else 'HOLD'
    msa_min=min(sens+spec) if sens and spec else 0.0
    core={
        'certificate_type':'ECON_SPC_P_INSPECTION_ASSURANCE_V1',
        'decision_state':state,
        'method':solution.get('method'),
        'first_action':first_action,
        'shared_capacity_use':used,
        'shared_capacity_limit':cap,
        'expected_cost_reference':expected,
        'no_inspection_expected_cost_reference':baseline,
        'modeled_cost_avoidance_reference':float(solution.get('modeled_cost_avoidance',baseline-expected)),
        'msa_min_sensitivity_or_specificity':msa_min,
        'msa_review_flag':'MEASUREMENT_SYSTEM_CAPABILITY_REVIEW' if msa_min < .80 else 'WITHIN_REFERENCE_REVIEW_BAND',
        'request_sha256':hashlib.sha256(_canonical(request)).hexdigest(),
        'checks':checks,
        'approval_authority':'QUALITY_ENGINEER',
        'secondary_review':'METROLOGY_OR_PROCESS_ENGINEER',
        'inspection_policy_write_allowed':False,
        'claim_boundary':'Model-based expected quality economics and measurement uncertainty; not realized plant savings or authorization to change an inspection plan.',
    }
    return {**core,'certificate_sha256':hashlib.sha256(_canonical(core)).hexdigest(),'generated_at_utc':datetime.now(timezone.utc).isoformat()}


def verify_inspection_certificate(certificate: dict[str,Any])->dict[str,Any]:
    stored=certificate.get('certificate_sha256')
    core={k:v for k,v in certificate.items() if k not in {'certificate_sha256','generated_at_utc'}}
    expected=hashlib.sha256(_canonical(core)).hexdigest()
    return {'valid':bool(stored and stored==expected),'stored_sha256':stored,'expected_sha256':expected,'decision_state':certificate.get('decision_state')}
