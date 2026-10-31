#!/usr/bin/env python3
"""One bounded R154 adversarial qualification, keeping older R153 gates intact."""
from __future__ import annotations
import copy,hashlib,json,math,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from tax_revenue_r154 import validate,tax_revenue,evaluate_counterfactual,build_joint_tradeoff_front
from tax_response_r153 import read_document
from decision_desk_r149 import make_report,_load_config
from decision_view_r149 import render_offline_html
from strategy_5y import read_json
checks=[]
def ok(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def rejects(name,fn):
    try:fn()
    except (ValueError,TypeError,KeyError,OverflowError,ZeroDivisionError):checks.append(name)
    else:raise AssertionError('INVALID INPUT ACCEPTED: '+name)

p=ROOT/'inputs/tax_revenue_r154.synthetic.json'
doc=validate(read_json(p));t,_=read_document(ROOT/'inputs/tax_counterfactual_r153.synthetic.json')
first=doc['annual_city_bases'][0];bases={k:v for k,v in first.items() if k!='communal_tax_amount'}
revenue=tax_revenue(doc['market'],bases,t['baseline']['decisions'],communal_tax_amount=first['communal_tax_amount'])
ok('Business tax source amount',revenue['channels_ecu']['business']==360000)
ok('Vehicle tax source exact algebra',abs(revenue['channels_ecu']['vehicle']-330*10*(1-10*.32/200)*12000/1000)<1e-6)
ok('Communal tax source exact algebra',abs(revenue['channels_ecu']['communal']-8*3100*(1-8*.22/250))<1e-6)
ok('Building tax source exact algebra',abs(revenue['channels_ecu']['building']-10*3100*(1-10*.18/250))<1e-6)
ok('Sum exactly four channels',abs(revenue['four_channel_subtotal_ecu']-sum(revenue['channels_ecu'].values()))<1e-5)
ok('No actual revenue emitted',revenue['actual_total_revenue_ecu'] is None)
ok('No spendable cash emitted',revenue['available_project_cash_ecu'] is None)
ok('Zero rates yield zero tax',tax_revenue(doc['market'],bases,{**t['baseline']['decisions'],'business_tax_percentage':0,'vehicle_tax_amount':0,'building_tax_amount':0},communal_tax_amount=0)['four_channel_subtotal_ecu']==0)
ok('Vehicle sensitivity saturates revenue at zero',tax_revenue(doc['market'],bases,t['baseline']['decisions']|{'vehicle_tax_amount':10000},communal_tax_amount=8)['channels_ecu']['vehicle']==0)
ok('Communal sensitivity saturates revenue at zero',tax_revenue(doc['market'],bases,t['baseline']['decisions'],communal_tax_amount=10000)['channels_ecu']['communal']==0)
ok('Building sensitivity saturates revenue at zero',tax_revenue(doc['market'],bases,t['baseline']['decisions']|{'building_tax_amount':10000},communal_tax_amount=8)['channels_ecu']['building']==0)
ok('Vehicle revenue is not unconditionally increasing in rate',tax_revenue(doc['market'],bases,t['baseline']['decisions']|{'vehicle_tax_amount':10000},communal_tax_amount=8)['channels_ecu']['vehicle']<revenue['channels_ecu']['vehicle'])
result=evaluate_counterfactual(doc,t['baseline']['decisions'],t['paths'][0]['decisions_by_year'],start_year=1)
ok('Five years available',len(result['yearly'])==5)
ok('Unchanged rate path zero fiscal difference',result['five_year_fixed_base_tax_delta_ecu']==0)
ok('Unknown business and household feedback retained',result['unmodeled_city_state_and_indirect_revenue']=='UNKNOWN_NOT_ZERO')
ok('Not approved budget',result['fiscal_tradeoff_not_an_authorized_budget'] is True)
ok('Year 5 source scope',result['year_5_delta_ecu']==0)
low=evaluate_counterfactual(doc,t['baseline']['decisions'],t['paths'][1]['decisions_by_year'],start_year=1)
high=evaluate_counterfactual(doc,t['baseline']['decisions'],t['paths'][2]['decisions_by_year'],start_year=1)
ok('Lower business tax reduces direct income at fixed base',low['five_year_fixed_base_tax_delta_ecu']<0)
ok('Higher business tax raises direct income at fixed base',high['five_year_fixed_base_tax_delta_ecu']>0)
ok('Business tax changes only affect business channel under fixed bases',all(x['four_tax_channel_deltas_ecu'][k]==0 for x in high['yearly'] for k in ('vehicle','communal','building')))
ok('Year 3 replan respects horizon',len(evaluate_counterfactual(doc,t['baseline']['decisions'],t['paths'][2]['decisions_by_year'],start_year=3)['yearly'])==3)
ok('Year 3 replan starts at 3',evaluate_counterfactual(doc,t['baseline']['decisions'],t['paths'][0]['decisions_by_year'],start_year=3)['yearly'][0]['year']==3)

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    def mutate(name,fn):
        c=copy.deepcopy(doc);fn(c)
        return validate(c)
    rejects('No source class rejects',lambda:mutate('src',lambda d:d.pop('source_class')))
    rejects('Synthetic declarations required',lambda:mutate('src',lambda d:d.update(source_class='VERIFIED')))
    rejects('No invented calibration from empty assumption note',lambda:mutate('note',lambda d:d.update(assumption_note='')))
    rejects('No omitted year accepted',lambda:mutate('year',lambda d:d['annual_city_bases'].pop()))
    rejects('No extra year accepted',lambda:mutate('year',lambda d:d['annual_city_bases'].append(copy.deepcopy(d['annual_city_bases'][-1]))))
    rejects('No missing market sensitivity accepted',lambda:mutate('missing',lambda d:d['market']['vehicle'].pop('revenue_sensitivity')))
    rejects('No nonpositive index divisor',lambda:mutate('zero',lambda d:d['market']['building'].update(index_divisor=0)))
    rejects('No negative sensitivity',lambda:mutate('negative',lambda d:d['market']['communal'].update(revenue_sensitivity=-1)))
    rejects('No fabricated true fixed-base flag',lambda:mutate('fixed',lambda d:d.update(fixed_bases_across_paths=False)))
    rejects('No fabricated non-overlap',lambda:mutate('overlap',lambda d:d.update(excluded_from_nonproject_cash=False)))
    rejects('No missing tax basis',lambda:mutate('basis',lambda d:d['annual_city_bases'][0].pop('housing_unit_count')))
    rejects('No negative income base',lambda:mutate('negative_base',lambda d:d['annual_city_bases'][0].update(business_taxable_base_ecu=-1)))
    rejects('No infinite population',lambda:mutate('inf',lambda d:d['annual_city_bases'][0].update(population=float('inf'))))
    rejects('No NaN tax rate',lambda:tax_revenue(doc['market'],bases,t['baseline']['decisions']|{'vehicle_tax_amount':float('nan')},communal_tax_amount=8))
    rejects('Boolean cannot substitute numeric',lambda:tax_revenue(doc['market'],bases,t['baseline']['decisions'],communal_tax_amount=True))
    rejects('No overflow source revenues',lambda:tax_revenue(doc['market'],bases|{'population':1e308,'car_count_index':1e308},t['baseline']['decisions'],communal_tax_amount=8))
    rejects('Invalid rolling year blocked',lambda:evaluate_counterfactual(doc,t['baseline']['decisions'],t['paths'][0]['decisions_by_year'],start_year=6))
    rejects('Truncated policy path rejected',lambda:evaluate_counterfactual(doc,t['baseline']['decisions'],t['paths'][0]['decisions_by_year'][:2],start_year=1))
    c=read_json(ROOT/'inputs/mvp_run.r154_synthetic.json')
    ok('Current config references both source and fiscal data',bool(c.get('tax_scenarios_path')) and bool(c.get('tax_revenue_scenarios_path')))
    c.pop('tax_scenarios_path',None)
    path=td/'bad.json';path.write_text(json.dumps(c))
    rejects('Fiscal source without tax source rejected',lambda:_load_config(path))

report=make_report(ROOT/'inputs/mvp_run.r154_synthetic.json')
f=report['r154_source_four_tax_fiscal_tradeoffs'];j=report['r154_conditional_joint_pareto']
ok('Single R153/R154 source engine report',report['r153_source_backed_tax_sensitivity'] is not None)
ok('15 inherited project candidates',len(report['candidate_comparison'])==15)
ok('Three source-backed tax-revenue paths',len(f['path_counterfactuals'])==3)
ok('Five years each fiscal path',all(len(x['fiscal_comparison']['yearly'])==5 for x in f['path_counterfactuals']))
ok('All scenario inputs SHA pinned',len(report['inputs']['tax_revenue_scenarios']['sha256'])==64)
ok('45 candidate-policy combinations evaluated',j['evaluated']==45)
ok('Nondominated front nonempty',len(j['front'])>0)
ok('No globally optimal claim',j['status']=='CONDITIONAL_SAMPLED_NONDOMINATED_NOT_GLOBAL_OPTIMUM')
ok('Joint front no real scores',all(x['real_five_year_smartcity_score'] is None for x in j['front']))
ok('Joint front no approved budget',all(x['hypothetical_budget_authorized'] is False for x in j['front']))
ok('End-to-end gameplay STOP',report['gameplay_gate']=='STOP')
ok('Fiscal revenue cannot make project budget authoritative',f['revenue_cannot_be_added_to_project_budget'] is True)
ok('Fiscal cash/net-income explicitly unknown',f['actual_five_year_cash_or_profit'] is None)
html=render_offline_html(report)
ok('Existing static HTML is script free','<script' not in html)
ok('HTML contains separate fixed-base fiscal section','négy forrásalapú adóbevételi képlet' in html)
ok('HTML contains conditional Pareto tradeoff','részleges index kontra feltételes adóbevétel' in html)
ok('No offsite assets',all(x not in html for x in ('<iframe','<img','http://','https://')))
anchors=read_json(ROOT/'evidence/R154_TAX_REVENUE_FORMULA_ANCHORS.json')['anchors']
ok('Four revenue formulas anchored',len(anchors)==4)
ok('Four distinct source labels',set(x['channel'] for x in anchors)=={'Bi','_i','Ui','Yi'})
ok('Source digest uniformly recorded',len(set(x['source_full_file_sha256'] for x in anchors))==1)
ok('No server authority claimed by source anchor',all('authoritative server settlement' in x['source_does_not_prove'] for x in anchors))
for x in anchors:
    ok(x['channel']+' distinct formula digest',len(x['source_span_sha256'])==64 and x['byte_span'][1]>x['byte_span'][0])
# Check all rows in the source read-only reference are tagged TEST round; they
# are never used as real revenue model inputs (which are separately SYNTHETIC).
import csv
with (ROOT/'data/finance_R94_test_snapshot.csv').open(encoding='utf-8-sig',newline='') as fi:
    historic=[a for a in csv.DictReader(fi) if a['view']=='cash_flow' and a['label'] in ('Iparűzési adó','Gépjárműadó','Kommunális adó','Építményadó')]
ok('Four historical R94 fiscal entries remain independent',len(historic)==4)
ok('Historical observed fiscal amounts not treated as synthetic base',all(a['competition']=='X-Challenge 2026 Tesztforduló' for a in historic))
result={'schema':'ECOSIM_R154_ADVERSARIAL_QUALIFICATION_V1','status':'PASS_OFFLINE_CODE_ONLY',
        'new_checks':len(checks),'checks':checks,'inherited_checks':467,
        'historical_source_parity':'FOUR_STATIC_FORMULAS_MATCH_SOURCE_TRANSCRIPTION_NOT_SERVER_SETTLEMENT',
        'forecast_accuracy':'UNKNOWN_0_REAL_PAIRS','gameplay_gate':'STOP'}
(ROOT/'results/R154_QUALIFICATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('R154_NEW_CHECKS='+str(len(checks))+' PASS; inherited=467 (not rerun here); GAME=STOP')
