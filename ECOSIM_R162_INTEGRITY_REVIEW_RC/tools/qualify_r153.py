#!/usr/bin/env python3
"""One bounded adversarial R153 regression, reusing the previously created E2E demo.

No search is launched here: previous E2E run used the inherited strategy_5y.
"""
import copy,hashlib,io,json,math,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from tax_response_r153 import tax_formula,read_document,evaluate,SOURCE_EXPRESSION_SHA256
from strategy_5y import read_json
from decision_desk_r149 import _load_config,make_report,validate_tax_context
ROOT=Path(__file__).resolve().parent.parent
checks=[]
def ok(desc,cond):
    if not cond:raise AssertionError(desc)
    checks.append(desc)
def rejects(desc,method):
    try:method()
    except (ValueError,TypeError,KeyError,OverflowError):checks.append(desc)
    else:raise AssertionError('Invalid input was accepted: '+desc)

old=read_json(ROOT/'results/R152_QUALIFICATION.json')
ok('R152 inherited source status is PASS',old['status']=='PASS_OFFLINE_CODE_ONLY')
ok('R152 documented checked count retained',old['total_documented_checks']==421)
p=ROOT/'inputs/tax_counterfactual_r153.synthetic.json'
doc,b=read_document(p)
ok('Source checksum is pinned',len(SOURCE_EXPRESSION_SHA256)==64)
ok('Original formula upper bound is 100',tax_formula(doc['market'],doc['baseline']['decisions'],100)['factor_percent']==100)
negative_tax={**doc['baseline']['decisions'],'vehicle_tax_amount':5000}
ok('Source does not introduce a zero lower clamp',tax_formula(doc['market'],negative_tax,1)['factor_percent']<0)
ok('Exact baseline reconciles observed factor',abs(b['factor_percent']-28.33)<1e-8)
for key in ('services_fee_percentage','business_tax_percentage','vehicle_tax_amount','building_tax_amount'):
    target={**doc['baseline']['decisions'],key:doc['baseline']['decisions'][key]+1}
    ok('Larger '+key+' never increases friendliness',tax_formula(doc['market'],target,1)['factor_percent']<=b['factor_percent'])
neutral=evaluate(doc,[{'candidate_id':'test','project_ids_by_year':[[],[],[],[],[]], 'mapped_terminal_proxy_delta':0}],1,{'Gazdaság':.25,'Környezet':.2,'Kormányzás':.15,'Életkörülmények':.15,'Mobilitás':.1,'Emberek':.15})
ok('Three paths evaluated',len(neutral['paths'])==3)
ok('Unchanged tax path has zero delta',neutral['paths'][0]['conditional_candidate_comparison'][0]['tax_delta_in_terminal_partial_index']==0)
ok('Lower business tax is conditionally positive',neutral['paths'][1]['conditional_candidate_comparison'][0]['tax_delta_in_terminal_partial_index']>0)
ok('Higher business tax is conditionally negative',neutral['paths'][2]['conditional_candidate_comparison'][0]['tax_delta_in_terminal_partial_index']<0)
ok('No tax revenue forecast fabricated',neutral['paths'][1]['conditional_candidate_comparison'][0]['yearly_factor_counterfactual'][0]['tax_income_effect'] is None)
ok('Source path never authorizes game mutations',neutral['gameplay_gate']=='STOP')
ok('No real five year score fabricated',neutral['paths'][1]['conditional_candidate_comparison'][0]['real_five_year_score'] is None)

j=read_json(ROOT/'results/R153_EVIDENCE_TO_TAX_AND_DECISION/DECISION_DESK.json')
t=j['r153_source_backed_tax_sensitivity']
ok('Integrated historical evidence remains historical',j['r152_offline_evidence_packet']['source_classification']=='HISTORICAL_TEST_ROUND_NOT_CURRENT')
ok('Integrated desk is STOP',j['gameplay_gate']=='STOP')
ok('Integrated source input tracked by SHA',len(j['inputs']['tax_scenarios']['sha256'])==64)
ok('All 15 inherited candidates preserved',len(j['candidate_comparison'])==15)
ok('All candidate trajectories evaluated for all three policy paths',all(len(x['conditional_candidate_comparison'])==15 for x in t['paths']))
ok('Exactly five years for every candidate',all(len(c['yearly_factor_counterfactual'])==5 for x in t['paths'] for c in x['conditional_candidate_comparison']))
ok('Tax changes do not become spendable cash',all(c['real_budget_impact'] is None for x in t['paths'] for c in x['conditional_candidate_comparison']))
html=(ROOT/'results/R153_EVIDENCE_TO_TAX_AND_DECISION/DECISION_DESK.html').read_text(encoding='utf-8')
ok('R153 appears in script-free HTML','R153 · eredeti EcoSim-képlethez kötött' in html and '<script' not in html)
ok('No network HTML assets',all(x not in html for x in ('http://','https://','<iframe','<img')))
ok('R153 structured output persisted',(ROOT/'results/R153_EVIDENCE_TO_TAX_AND_DECISION/R153_SOURCE_TAX_COUNTERFACTUAL.json').is_file())

with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    def mutated(name,modifier):
        clone=copy.deepcopy(doc);modifier(clone)
        target=tmp/(name+'.json');target.write_text(json.dumps(clone,ensure_ascii=False,allow_nan=True))
        return read_document(target)
    rejects('Missing source class rejected',lambda:mutated('sclass',lambda x:x.pop('source_class')))
    rejects('Unknown extra input rejected',lambda:mutated('extra',lambda x:x.update({'auth_token':'secret'})))
    rejects('Baseline mismatch rejected',lambda:mutated('badbase',lambda x:x['baseline'].update({'observed_company_friendliness_percent':77})))
    rejects('Duplicate tax path ids rejected',lambda:mutated('dupes',lambda x:x['paths'].append(copy.deepcopy(x['paths'][0]))))
    rejects('Invalid years rejected',lambda:mutated('years',lambda x:x['paths'][0].update({'decisions_by_year':[x['paths'][0]['decisions_by_year'][0]]})))
    rejects('Invalid market divisor rejected',lambda:mutated('div',lambda x:x['market']['tax_index_divisors'].update({'vehicle':0})))
    rejects('Infinite market base multiplier rejected',lambda:mutated('nanbase',lambda x:x['market'].update({'base_multiplier':float('inf')})))
    rejects('Negative rate rejected',lambda:mutated('neg',lambda x:x['baseline']['decisions'].update({'business_tax_percentage':-1})))
    rejects('Unexpected decision field rejected',lambda:mutated('unknown',lambda x:x['baseline']['decisions'].update({'cookie':'abc'})))
    rejects('Unstated assumptions rejected',lambda:mutated('note',lambda x:x.update({'assumption_note':''})))
    rejects('Bogus source mode rejected',lambda:mutated('mode',lambda x:x.update({'source_class':'VERIFIED_BY_SERVER'})))
    rejects('Scenario with NaN rejected',lambda:mutated('nan',lambda x:x['paths'][1]['decisions_by_year'][1].update({'vehicle_tax_amount':float('nan')})))
    c=read_json(ROOT/'inputs/mvp_run.r153_synthetic.json')
    c['mode']='CURRENT_SNAPSHOT_REVIEW';c['project_cap_assumption']=None
    c['capture_path']='inputs/capture_current.template.json';c.pop('state_path',None)
    path=tmp/'fakecurrent.json';path.write_text(json.dumps(c))
    # make_report resolves input files relative to the bundle root, not temp config;
    # place the test under the actual bundle in a temporary named file.
    import os
    dest=ROOT/'inputs/__temporary_r153_current_validation.json'
    try:
        dest.write_text(json.dumps(c))
        rejects('Synthetic tax path cannot be used with current game mode',lambda:validate_tax_context({'mode':'CURRENT_SNAPSHOT_REVIEW'},{},doc))
    finally:dest.unlink(missing_ok=True)
    badweights={'Gazdaság':.26,'Környezet':.2,'Kormányzás':.15,'Életkörülmények':.15,'Mobilitás':.1,'Emberek':.15}
    rejects('Invalid total index weights rejected',lambda:evaluate(doc,[],1,badweights))
    rejects('Wrong candidate horizon rejected',lambda:evaluate(doc,[{'candidate_id':'x','project_ids_by_year':[[]],'mapped_terminal_proxy_delta':0}],1,None))

source=read_json(ROOT/'evidence/R153_TAX_FORMULA_SOURCE_ANCHOR.json')
ok('Source range nonempty',source['range_utf8_bytes'][1]-source['range_utf8_bytes'][0]>100)
ok('Source expression digest agrees with pinned formula',source['expression_sha256']==SOURCE_EXPRESSION_SHA256)
ok('Source file digest present',len(source['source_sha256'])==64)
ok('Evidence explicitly excludes tax revenue',any('Tax income' in x for x in source['does_not_prove']))

result={'schema':'ECOSIM_R153_CONSOLIDATED_QUALIFICATION_V1',
        'status':'PASS_OFFLINE_CODE_ONLY','inherited_checks_not_rerun':421,
        'new_checks':len(checks),'total_documented_checks':421+len(checks),
        'new_checks_list':checks,'source_formula_original_840_sha256':source['source_sha256'],
        'source_formula_excerpt_sha256':SOURCE_EXPRESSION_SHA256,
        'R153_historical_E2E_search_count':1,
        'actual_model_accuracy':None,'actual_market_tax_parameters_verified':False,
        'gameplay_gate':'STOP','game_writes':0}
(ROOT/'results/R153_QUALIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'R153_QUALIFICATION={result["status"]} NEW={len(checks)} LEGACY_NOT_RERUN=421 TOTAL_DOCUMENTED={421+len(checks)} GAME=STOP')
