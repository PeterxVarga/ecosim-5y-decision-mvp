"""R209 offline multi-plan R153/R154/R155/R159 historical synthetic finance integration.

Calls source-identical existing fiscal models, NO new cash simulator, NO live data.
"""
from pathlib import Path
import sys,json,hashlib,copy
# Python -I omits the script directory from sys.path. Restore only this
# checked sibling fixture directory before loading the pinned-model harness.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_original_r162_integration import R162, SOURCE_BLOBS
sys.path.insert(0,str(R162/'tools'))
from observation_bundle_r152 import compile_bundle
from strategy_5y import search
from tax_response_r153 import read_document,evaluate as tax_effects
from tax_revenue_r154 import validate as validate_tax, evaluate_counterfactual
from operating_cash_r155 import validate as validate_operating, evaluate as operating_effects
from temporal_cash_r158 import build_timing_bridge

def exercise():
    for filename,pin in SOURCE_BLOBS.items():
        b=(R162/'tools'/filename).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==pin
    # Independent input catalog/control is historical p1 PLAN only.
    _,state,_=compile_bundle(R162/'examples/R152_HISTORICAL_R94_READONLY_PACKET/manifest.json')
    scenarios=[('LOW',75000),('MID',120000),('HIGH',150000)]
    candidates=[];statuses={}
    for label,limit in scenarios:
        strategy=search(state,1,[limit]*5,cap_override=4,beam_width=4,
                        shortlist=12,allow_same_year=False,objective='scenario_min')
        assert strategy['game_write_actions']==0
        for j,plan in enumerate(strategy['top_plans']):
            audit=plan['r160_independent_constraint_replay']
            assert not audit['hard_rule_violations']
            cid=f'{label}_{j}'
            candidates.append({'candidate_id':cid,
                'project_ids_by_year':[r['start_project_ids'] for r in plan['start_by_year']],
                'conservative_project_need_ecu_by_year':[r['conservative_card_cash_requirement_ecu'] for r in plan['start_by_year']],
                'five_year_conservative_project_need_ecu':plan['five_year_conservative_card_cost_ecu'],
                'mapped_terminal_proxy_delta':plan['terminal_mapped_proxy_delta']})
            statuses[cid]=audit['status']
    data=R162/'inputs'
    tax,_=read_document(data/'tax_counterfactual_r153.synthetic.json')
    fiscal=validate_tax(json.loads((data/'tax_revenue_r154.synthetic.json').read_text()))
    op=validate_operating(json.loads((data/'operating_r155.synthetic.json').read_text()))
    assert tax['source_class']==fiscal['source_class']==op['source_class']=='SYNTHETIC_TEST_ONLY'
    paths={x['id']:x for x in op['paths']}
    assert set(paths)=={x['id'] for x in tax['paths']}
    response=tax_effects(tax,candidates,1,weights=state['market']['smartcity_total_weights'])
    tax_paths={'source_class':tax['source_class'],
               'path_counterfactuals':[{'tax_path_id':x['id'],
                  'fiscal_comparison':evaluate_counterfactual(fiscal,tax['baseline']['decisions'],x['decisions_by_year'],start_year=1)}
                  for x in tax['paths']]}
    operating={'source_class':op['source_class'],
               'path_counterfactuals':[operating_effects(op,paths[x['id']],1) for x in tax['paths']]}
    joined=build_timing_bridge(candidates,tax_paths,operating,response,1)
    assert joined['status']=='CONDITIONAL_PARTIAL_CASH_TIMING_NOT_GAME_SOLVENCY'
    assert joined['gameplay_gate']=='STOP' and not joined['true_cash_availability_or_financing_proven']
    assert joined['evaluated_combinations']==len(candidates)*len(tax['paths'])
    assert len(joined['combinations'])==len(candidates)*len(tax['paths'])
    assert all(x['gameplay_gate']=='STOP' and not x['affordability_authorized'] and x['actual_spendable_cash_ecu'] is None for x in joined['combinations'])
    # Negative controls: a mismatched five-year card-cost identity and mixed
    # assumed model source classes must fail rather than silently join.
    mutated=copy.deepcopy(candidates)
    mutated[0]['five_year_conservative_project_need_ecu']+=1
    try:build_timing_bridge(mutated,tax_paths,operating,response,1)
    except ValueError:pass
    else:raise AssertionError('HOLD_COST_DRIFT_FAILED_TO_REJECT')
    corrupted=copy.deepcopy(tax_paths)
    corrupted['source_class']='OPERATOR_DECLARED_READONLY_HYPOTHESIS'
    try:build_timing_bridge(candidates,corrupted,operating,response,1)
    except ValueError:pass
    else:raise AssertionError('HOLD_MIXED_SOURCE_CLASSES_FAILED_TO_REJECT')
    for x in joined['combinations']:
        expected=next(y for y in candidates if y['candidate_id']==x['candidate_id'])
        assert [y['projects_started_ids'] for y in x['annual_rows']]==expected['project_ids_by_year']
        assert abs(x['five_year_project_card_cost_ecu']-expected['five_year_conservative_project_need_ecu']) < 1e-4
    return {'status':'PASS_HISTORICAL_SYNTHETIC_PARTIAL_POLICY_JOIN_ONLY',
        'source_class':'SYNTHETIC_TEST_ONLY','source_git_blobs':SOURCE_BLOBS,
        'five_year_project_schedules_evaluated':len(candidates),
        'tax_operating_scenarios':len(tax['paths']),
        'project_policy_timing_combinations':joined['evaluated_combinations'],
        'project_model_display_condition_statuses':statuses,
        'sampled_policy_financial_rows':[{
             'project_plan':x['candidate_id'], 'policy':x['path_id'],
             'first_year_project_ids':next(y['project_ids_by_year'][0] for y in candidates if y['candidate_id']==x['candidate_id']),
             'five_year_project_card_cost_ecu':x['five_year_project_card_cost_ecu'],
             'five_year_partial_net_after_card_cost_ecu':x['five_year_partial_net_after_card_cost_ecu'],
             'hypothetical_zero_opening_deferred_peak_shortfall_ecu':x['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu'],
             'conditional_terminal_index_proxy_plus_tax_delta':x['conditional_terminal_mapped_proxy_delta']}
             for x in joined['combinations']],
        'partial_zero_opening_financial_metrics_are_not_real_liquidity':True,
        'actual_city_forecast':False,'actual_spendable_cash':False,
        'gameplay_gate':'STOP','game_writes':0}

if __name__=='__main__':
    print(json.dumps(exercise(),ensure_ascii=False,sort_keys=True,indent=2))
