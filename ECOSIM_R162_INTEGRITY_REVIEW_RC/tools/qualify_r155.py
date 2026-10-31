#!/usr/bin/env python3
"""One-shot adversarial R155 acceptance; no browser or EcoSim actions."""
from __future__ import annotations
import sys,math,json,copy,hashlib,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'tools'))
from operating_cash_r155 import validate,service_fees,staff_expenses,evaluate,combined_front,SCHEMA,STAFF,FEES
from strategy_5y import read_json
from decision_desk_r149 import make_report,_load_config
from decision_view_r149 import render_offline_html
checks=[]
def ok(name,condition):
    if not condition:raise AssertionError('FAILED '+name)
    checks.append(name)
def reject(name,func):
    try:func()
    except (ValueError,TypeError,OverflowError,ZeroDivisionError):checks.append(name)
    else:raise AssertionError('UNSAFE ACCEPTED '+name)
def mutate(doc,func):
    d=copy.deepcopy(doc);func(d);return validate(d)
doc=validate(read_json(ROOT/'inputs/operating_r155.synthetic.json'))
ok('Exact R155 schema',doc['schema']==SCHEMA)
ok('All six source fee types',len(FEES)==6)
ok('No source provenance promoted to verified',doc['source_class']=='SYNTHETIC_TEST_ONLY')
ok('Five annual city states',len(doc['annual_city_bases'])==5)
ok('Three matching operating policy paths',len(doc['paths'])==3)
ok('All 15 staff categories',len(STAFF)==15)
base=doc['annual_city_bases'][0];mkt=doc['market'];fee=doc['baseline_fees']
res=service_fees(mkt,1,base,fee)
ok('Six fee channels precisely',set(res['channels_ecu'])==set(FEES))
ok('Burial client formula',res['channels_ecu']['burial']==35*100)
ok('Communal client formula',res['channels_ecu']['communal']==11*3100)
ok('Services client formula',res['channels_ecu']['services']==80*3100)
ok('Transport fee source formula',res['channels_ecu']['transport']==4*1400*.25)
ok('Rental cap .99 is applied',abs(res['channels_ecu']['rental']-130*120*.99)<1e-6)
r=fee['parking']/mkt['parking']['reference_fee'][0]
expected=base['population']*base['parking_car_index']/1000*fee['parking']*mkt['parking']['ratio'][0]**(r/mkt['parking']['damper'][0])*r**(-mkt['parking']['elasticity'][0])
ok('Parking price response source formula',abs(res['channels_ecu']['parking']-expected)<1e-6)
ok('All six fees sum correctly',abs(sum(res['channels_ecu'].values())-res['six_fee_subtotal_ecu'])<1e-5)
ok('Fee model not authoritative actual revenue',res['actual_service_income_ecu'] is None)
w=staff_expenses(base,base['staff'])
ok('Eight wage components',len(w['wage_components_ecu'])==8)
ok('Seven materials components',len(w['material_components_ecu'])==7)
ok('Culture wage uses sport wage per client JS',w['wage_components_ecu']['culture']==base['wage_rates']['sport']*base['staff']['culture'])
ok('Education wages four staff types',w['wage_components_ecu']['education']==base['wage_rates']['education']*sum(base['staff'][x] for x in STAFF[:4]))
ok('Services wages six staff types',w['wage_components_ecu']['services']==base['wage_rates']['services']*sum(base['staff'][x] for x in STAFF[8:14]))
ok('Transport salary declared exogenous',w['wage_components_ecu']['transport']==base['transport_wages_ecu'])
ok('Material source services project multiplier',abs(w['material_components_ecu']['services']-w['wage_components_ecu']['services']*base['material_ratios']['services']*base['service_material_multiplier'])<1e-6)
ok('Cost subtotal arithmetic',abs(w['covered_payroll_material_expense_ecu']-(w['wage_subtotal_ecu']+w['material_subtotal_ecu']))<1e-5)
ok('Unmodeled transit materials remain null',w['training_transit_material_and_other_expenses_ecu'] is None)
ok('No fake total city expenses',w['actual_total_city_expenses_ecu'] is None)
r0=evaluate(doc,doc['paths'][0]);r1=evaluate(doc,doc['paths'][1]);r2=evaluate(doc,doc['paths'][2]);
ok('Five years compared',len(r0['annual_rows'])==5)
ok('Control has no change',r0['five_year_partial_operating_net_delta_ecu']==0)
ok('Reduced service prices and extra workers reduce partial net',r1['five_year_partial_operating_net_delta_ecu']<0)
ok('Higher fees with health hires explicitly balanced',r2['five_year_covered_institution_cost_delta_ecu']>0)
ok('Rolling start year selects three years',len(evaluate(doc,doc['paths'][1],start_year=3)['annual_rows'])==3)
ok('Rolling year starts at 3',evaluate(doc,doc['paths'][1],3)['annual_rows'][0]['year']==3)
ok('Revenue cannot become project cash',r2['available_budget_from_partial_delta_ecu'] is None)
ok('No invented year-5 index',r2['actual_market_and_migration_response'] is None)
ok('Future bases explicitly not estimated',r2['full_city_expenses_and_revenues']=='UNMODELLED_NOT_ZERO')
reject('Reject missing source class',lambda:mutate(doc,lambda d:d.pop('source_class')))
reject('Reject official-looking source class',lambda:mutate(doc,lambda d:d.update(source_class='OFFICIALLY_VERIFIED')))
reject('Reject blank caveat',lambda:mutate(doc,lambda d:d.update(assumption_note='')))
reject('Reject silent budget double count',lambda:mutate(doc,lambda d:d.update(excluded_from_nonproject_cash=False)))
reject('Reject non-fixed bases',lambda:mutate(doc,lambda d:d.update(fixed_exogenous_bases_across_paths=False)))
reject('Reject missing historical year',lambda:mutate(doc,lambda d:d['annual_city_bases'].pop()))
reject('Reject missing staff group',lambda:mutate(doc,lambda d:d['annual_city_bases'][0]['staff'].pop('social')))
reject('Reject extra key in cost components',lambda:mutate(doc,lambda d:d['annual_city_bases'][0]['wage_rates'].update(unrelated=10)))
reject('Reject negative personnel cost',lambda:mutate(doc,lambda d:d['annual_city_bases'][0]['wage_rates'].update(sport=-5)))
reject('Reject missing parking yearly exogenous price',lambda:mutate(doc,lambda d:d['market']['parking']['reference_fee'].pop()))
reject('Reject zero parking reference',lambda:mutate(doc,lambda d:d['market']['parking']['reference_fee'].__setitem__(0,0)))
reject('Reject zero parking ratio',lambda:mutate(doc,lambda d:d['market']['parking']['ratio'].__setitem__(0,0)))
reject('Reject nonfinite elasticity',lambda:mutate(doc,lambda d:d['market']['parking']['elasticity'].__setitem__(0,float('inf'))))
reject('Reject negative rental multiplier',lambda:mutate(doc,lambda d:d['market'].update(rental_multiplier=-.4)))
reject('Reject bool instead of numeric',lambda:mutate(doc,lambda d:d['annual_city_bases'][0].update(population=True)))
reject('Reject 4-year fee path',lambda:mutate(doc,lambda d:d['paths'][1]['fees_by_year'].pop()))
reject('Reject missing fee channel in path',lambda:mutate(doc,lambda d:d['paths'][1]['fees_by_year'][0].pop('burial')))
reject('Reject zero parking fee in path',lambda:mutate(doc,lambda d:d['paths'][1]['fees_by_year'][0].update(parking=0)))
reject('Reject duplicate aligned path ID',lambda:mutate(doc,lambda d:d['paths'][1].update(id=d['paths'][0]['id'])))
reject('Reject negative workforce',lambda:mutate(doc,lambda d:d['paths'][1]['staff_by_year'][0].update(social=-1)))
reject('Reject invalid roll year',lambda:evaluate(doc,doc['paths'][0],0))
reject('Reject fractional roll year',lambda:evaluate(doc,doc['paths'][0],2.5))
reject('Reject extreme overflow income',lambda:service_fees(mkt,1,base|{'population':1e308,'parking_car_index':1e308},fee))
reject('Reject extreme overflow expenses',lambda:staff_expenses(base|{'transport_wages_ecu':1e308},dict.fromkeys(STAFF,1e308)))
config=ROOT/'inputs/mvp_run.r155_synthetic.json'
ok('Single existing R149 controller accepts new R155 config',_load_config(config).get('operating_scenarios_path') is not None)
with tempfile.TemporaryDirectory() as tmp:
    c=read_json(config)
    c.pop('tax_revenue_scenarios_path',None);p=Path(tmp)/'bad.json';p.write_text(json.dumps(c))
    reject('Operating path cannot exist without four-tax source model',lambda:_load_config(p))
    c=read_json(config);c['mode']='CURRENT_SNAPSHOT_REVIEW';p.write_text(json.dumps(c))
    reject('Synthetic operating scenarios never allowed in current mode',lambda:make_report(p))
report=make_report(config)
ok('End-to-end same inherited project engine',len(report['candidate_comparison'])==15)
ok('Separate 4-tax fiscal report retained',len(report['r154_source_four_tax_fiscal_tradeoffs']['path_counterfactuals'])==3)
ok('R155 partial operating in same report',len(report['r155_source_operating_cash_tradeoffs']['path_counterfactuals'])==3)
ok('R155 input hash in decision provenance',len(report['inputs']['operating_scenarios']['sha256'])==64)
ok('Matched tax plus operating tradeoffs 45',report['r155_conditional_joint_operating_pareto']['evaluated']==45)
ok('Sampled Pareto front exists',bool(report['r155_conditional_joint_operating_pareto']['front']))
ok('All partial operating candidates have no real cash',all(x['actual_available_money_ecu'] is None for x in report['r155_conditional_joint_operating_pareto']['front']))
ok('Combined R155 score is not actual year-5 index',all(x['actual_year_5_index'] is None for x in report['r155_conditional_joint_operating_pareto']['front']))
ok('Game remains STOP',report['gameplay_gate']=='STOP')
html=render_offline_html(report)
ok('Offline HTML has new operating cost section','R155 · hat szolgáltatási bevétel' in html)
ok('HTML has no scripts','<script' not in html)
ok('HTML has no network resources',all(x not in html for x in ('<iframe','https://','http://','<img')))
anchors=read_json(ROOT/'evidence/R155_OPERATING_FORMULA_ANCHORS.json')
ok('Source anchors 21 exact function spans',len(anchors['anchors'])==21)
ok('All source hash pinned',len(set(a['full_source_sha256'] for a in anchors['anchors']))==1)
ok('All source spans distinct',len(set(tuple(a['byte_span']) for a in anchors['anchors']))==21)
ok('Source does not grant server authority',all(a['not_server_authority'] for a in anchors['anchors']))
original=Path('/mnt/data/ECOSIM_R143_5Y_CODEX_V2/private_js/840.41fdc8e1.chunk.js')
if original.is_file():
    source=original.read_bytes()
    ok('Original source SHA256 matches evidence anchor',hashlib.sha256(source).hexdigest()==anchors['anchors'][0]['full_source_sha256'])
    for a in anchors['anchors']:
        lo,hi=a['byte_span'];ok('Source span '+a['name']+' hash',hashlib.sha256(source[lo:hi]).hexdigest()==a['sha256'])
else:
    checks.append('Original source unavailable; hash anchors retained, not independently rechecked')
result={'schema':'ECOSIM_R155_ADVERSARIAL_QUALIFICATION_V1','status':'PASS_OFFLINE_SOURCE_COMPONENTS',
        'new_checks':len(checks),'new_check_names':checks,'source_anchor_count':len(anchors['anchors']),
        'inherited_results_preserved_not_rerun_here':536,
        'realized_five_year_forecast_accuracy':'UNKNOWN','gameplay_gate':'STOP'}
(ROOT/'results/R155_QUALIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'R155_NEW_CHECKS={len(checks)} PASS; inherited_prior={536} (not rerun); GAME=STOP')
