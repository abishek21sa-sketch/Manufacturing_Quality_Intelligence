from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
import math
import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class MSAObservationModel:
    sensitivity: float
    specificity: float
    good_measured_sd: float
    bad_measured_sd: float
    measurement_sd_effective: float


@dataclass(frozen=True)
class MultiLineInspectionPolicy:
    expected_cost: float
    first_action: tuple[int, ...]
    policy: dict[str, tuple[int, ...]]
    states_evaluated: int


def observation_model_from_msa(
    *, good_mean: float, bad_mean: float, process_sd_good: float, process_sd_bad: float,
    measurement_sd: float, upper_spec: float, replicates: int = 1,
) -> MSAObservationModel:
    """Convert Gaussian process + measurement-system uncertainty to fail/pass accuracy.

    A unit is observed FAIL when the measured CTQ exceeds `upper_spec`.
    Averaging `replicates` independent gage readings reduces the measurement
    variance component by 1/replicates. This is a compact bridge from MSA/Gage
    R&R variance evidence to the POMDP observation likelihoods.
    """
    if replicates < 1 or min(process_sd_good, process_sd_bad, measurement_sd) < 0:
        raise ValueError("standard deviations must be nonnegative and replicates >= 1")
    ms=float(measurement_sd)/math.sqrt(replicates)
    sd_g=math.sqrt(process_sd_good**2+ms**2)
    sd_b=math.sqrt(process_sd_bad**2+ms**2)
    if sd_g <= 0 or sd_b <= 0:
        raise ValueError("measured distributions must have positive variance")
    specificity=float(norm.cdf((upper_spec-good_mean)/sd_g))
    sensitivity=float(1-norm.cdf((upper_spec-bad_mean)/sd_b))
    return MSAObservationModel(sensitivity,specificity,sd_g,sd_b,ms)


def solve_multiline_inspection_pomdp(
    prior_bad: np.ndarray,
    transitions: np.ndarray,
    sensitivity: np.ndarray,
    specificity: np.ndarray,
    inspection_cost: np.ndarray,
    capacity_use: np.ndarray,
    *,
    escape_cost: np.ndarray,
    correction_cost: np.ndarray,
    horizon: int,
    capacity_per_period: int,
    belief_round: int = 5,
) -> MultiLineInspectionPolicy:
    """Exact finite-horizon small multi-line POMDP with shared inspection capacity.

    Lines evolve independently conditional on their latent GOOD/BAD state, but
    inspection resources are coupled by a per-period capacity constraint.
    Action 0 means no inspection. Positive action levels have line/action-specific
    observation accuracy and cost. A detected fail triggers containment and resets
    the line to GOOD before its Markov transition.
    """
    b0=np.asarray(prior_bad,float); P=np.asarray(transitions,float)
    se=np.asarray(sensitivity,float); sp=np.asarray(specificity,float); ic=np.asarray(inspection_cost,float)
    ku=np.asarray(capacity_use,int); ec=np.asarray(escape_cost,float); cc=np.asarray(correction_cost,float)
    if b0.ndim!=1 or np.any((b0<0)|(b0>1)): raise ValueError("invalid prior beliefs")
    L=b0.size
    if P.shape!=(L,2,2) or np.any(P<0) or not np.allclose(P.sum(axis=2),1,atol=1e-10): raise ValueError("invalid transitions")
    if se.ndim!=2 or se.shape[0]!=L or sp.shape!=se.shape or ic.shape!=se.shape: raise ValueError("action matrix mismatch")
    A=se.shape[1]
    if ku.shape!=(A,) or ku[0]!=0 or np.any(ku<0) or np.any((se<0)|(se>1)) or np.any((sp<0)|(sp>1)): raise ValueError("invalid actions")
    if ec.shape!=(L,) or cc.shape!=(L,) or np.any(ec<0) or np.any(cc<0): raise ValueError("invalid costs")
    if horizon<=0 or capacity_per_period<0: raise ValueError("invalid horizon/capacity")

    feasible_actions=[a for a in product(range(A),repeat=L) if sum(int(ku[x]) for x in a)<=capacity_per_period]
    if not feasible_actions: raise ValueError("no feasible joint action")
    policy={}

    def propagate(line,b): return float((1-b)*P[line,0,1]+b*P[line,1,1])

    def line_branches(line,b,a):
        if a==0:
            return [(1.0,ec[line]*b,round(propagate(line,b),belief_round))]
        pf=b*se[line,a]+(1-b)*(1-sp[line,a]); pp=1-pf
        out=[]
        if pf>1e-15:
            # fail -> contained/corrected; process transitions from GOOD
            out.append((float(pf),float(ic[line,a]+cc[line]),round(float(P[line,0,1]),belief_round)))
        if pp>1e-15:
            post_bad=b*(1-se[line,a])/pp
            escape=ec[line]*post_bad
            out.append((float(pp),float(ic[line,a]+escape),round(propagate(line,post_bad),belief_round)))
        return out

    @lru_cache(None)
    def dp(t:int, beliefs:tuple[float,...]):
        if t>=horizon: return 0.0
        best=float('inf'); besta=None
        for action in feasible_actions:
            branches=[line_branches(l,float(beliefs[l]),action[l]) for l in range(L)]
            val=0.0
            for combo in product(*branches):
                prob=float(np.prod([x[0] for x in combo])); immediate=sum(x[1] for x in combo)
                nxt=tuple(x[2] for x in combo)
                val += prob*(immediate+dp(t+1,nxt))
            if val<best-1e-12:
                best=float(val); besta=tuple(map(int,action))
        key=f"t={t}|b="+','.join(f'{x:.{belief_round}f}' for x in beliefs)
        policy[key]=besta
        return best

    beliefs=tuple(round(float(x),belief_round) for x in b0)
    cost=dp(0,beliefs)
    key='t=0|b='+','.join(f'{x:.{belief_round}f}' for x in beliefs)
    return MultiLineInspectionPolicy(float(cost),policy[key],policy,dp.cache_info().currsize)


def no_inspection_expected_cost(prior_bad: np.ndarray, transitions: np.ndarray, escape_cost: np.ndarray, horizon: int) -> float:
    b=np.asarray(prior_bad,float).copy(); P=np.asarray(transitions,float); ec=np.asarray(escape_cost,float)
    total=0.0
    for _ in range(horizon):
        total += float(ec@b)
        b=(1-b)*P[:,0,1]+b*P[:,1,1]
    return float(total)
