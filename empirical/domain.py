from pathlib import Path
import csv,statistics,collections
ROOT=Path(__file__).resolve().parents[1]
def _rate(rr):return sum(int(float(r['defect'])) for r in rr)/max(1,len(rr))
def domain_diagnostics():
 rows=list(csv.DictReader((ROOT/'data/fixtures/process_fixture.csv').open())); byline=collections.defaultdict(list); byshift=collections.defaultdict(list)
 for r in rows:byline[r['line']].append(r);byshift[r['shift']].append(r)
 line={k:round(_rate(v),4) for k,v in byline.items()}; shift={k:round(_rate(v),4) for k,v in byshift.items()}; wear=sorted(float(r['tool_wear_pct']) for r in rows); q=wear[int(.75*(len(wear)-1))]; high=[r for r in rows if float(r['tool_wear_pct'])>=q]; low=[r for r in rows if float(r['tool_wear_pct'])<q]
 factors=['temperature_c','pressure_bar','speed_mpm','vibration_mm_s','tool_wear_pct','material_hardness','humidity_pct','operator_experience_y']; diff=[]
 defect=[r for r in rows if int(float(r['defect']))==1]; good=[r for r in rows if int(float(r['defect']))==0]
 for f in factors:
  if defect and good: diff.append({'factor':f,'defect_mean':round(statistics.fmean(float(r[f]) for r in defect),4),'good_mean':round(statistics.fmean(float(r[f]) for r in good),4),'delta':round(statistics.fmean(float(r[f]) for r in defect)-statistics.fmean(float(r[f]) for r in good),4)})
 diff.sort(key=lambda x:abs(x['delta']),reverse=True)
 return {'analysis':'quality escape stratification and inspection economics precursor','metrics':{'records':len(rows),'overall_defect_rate':round(_rate(rows),4),'high_wear_defect_rate':round(_rate(high),4),'lower_wear_defect_rate':round(_rate(low),4),'wear_q75':round(q,3)},'defect_rate_by_line':line,'defect_rate_by_shift':shift,'largest_defect_good_factor_gaps':diff[:6],'decision_signal':'Feed high-risk line/shift/factor evidence into defect prediction, then let GAGE-SHIELD and ECON-SPC-P allocate trustworthy inspection capacity.','evidence_boundary':'Repository process fixture supports method validation, not external plant performance claims.'}
