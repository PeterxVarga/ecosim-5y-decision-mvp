"""Offline synthetic-gate rehearsal using SOURCE-IDENTICAL original R162 code.

NEVER authenticates or simulates a live capture. Reuses historical p1 PLAN only.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

WORK = Path(__file__).resolve().parents[2]
R162 = WORK/'ECOSIM_R162_INTEGRITY_REVIEW_RC'
TOOLS = R162/'tools'
ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(TOOLS))
from observation_bundle_r152 import compile_bundle
from readonly_intake_r156 import create_bundle
from strategy_5y import search
from portfolio_5y import project_index
from independent_audit_r160 import audit_plan

spec=importlib.util.spec_from_file_location('r207_source_rehearsal',ROOT/'first_round.py')
r207=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r207)

SOURCE_BLOBS = {
    'strategy_5y.py':'ebc0022248f3cb5cd8f6fb4123f99f52ad60f87f',
    'portfolio_5y.py':'4b81b17e28c30ef6d2026edfdeb22ea2430deee2',
    'independent_audit_r160.py':'baeb6bcc9e7e375e12a22f8f753c202325ebef8e'
}

def run():
    for filename,pinned in SOURCE_BLOBS.items():
        b=(TOOLS/filename).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        assert actual==pinned, 'HOLD_R162_UPSTREAM_SOURCE_MISMATCH_'+filename
    _, historical, _=compile_bundle(R162/'examples/R152_HISTORICAL_R94_READONLY_PACKET/manifest.json')
    assert historical['provenance']['observed_column_kind']=='PLAN'
    assert 'Tesztforduló' in historical['provenance']['round']
    # Exercise original R156 CURRENT_READONLY input materialization with explicitly
    # SYNTHETIC metadata over historical PLAN values. This is NEVER a live capture.
    source=json.loads((R162/'capture/R156_HISTORICAL_TEST_EXPORT.json').read_text())
    source.update(capture_mode='CURRENT_READONLY', kind='PLAN',
                  team='SYNTHETIC_ONLY_TEAM', market='SYNTHETIC_ONLY_MARKET',
                  round='SYNTHETIC_OFFLINE_REHEARSAL',
                  captured_at_local='2026-11-02T09:00:00+01:00',
                  source_evidence_id='SYNTHETIC_R156_READONLY_FIXTURE',
                  source_note='SYNTHETIC ONLY: historical PLAN values with fake metadata; never an observed live state')
    source['parameters']['market']['maxProjectPerTurn']=4
    source['parameters']['team']={'project1_active_previous_period':False,
                                 'already_selected_new_project_ids_current_period':[]}
    source['field_sources'].update(factors='SYNTHETIC_HISTORICAL_P1_FACTORS',
                                  projects='SYNTHETIC_HISTORICAL_P1_CARDS',
                                  market_project_cap='SYNTHETIC_4_CAP',
                                  market_index_weights='SYNTHETIC_6_WEIGHTS')
    with tempfile.TemporaryDirectory() as td:
        synthetic_bundle, receipt=create_bundle(source, Path(td)/'synthetic_readonly')
        assert receipt['schema']=='ECOSIM_R156_ACQUISITION_RECEIPT_V1'
        assert receipt['gameplay_gate']=='STOP'
        _, state, _=compile_bundle(synthetic_bundle/'manifest.json')
    assert state['provenance']['round']=='SYNTHETIC_OFFLINE_REHEARSAL'
    assert state['market']['maxProjectPerTurn']==4
    assert state['team']['initially_active_project_ids']==historical['team']['initially_active_project_ids']
    observed=[]
    scenarios=[('CONSERVATIVE_50PCT','scenario_min',75000),
               ('BALANCED_80PCT','scenario_min',120000),
               ('FULL_SYNTHETIC_CEILING','nominal',150000)]
    for name,objective,ceiling in scenarios:
        result=search(state,start_year=1,budget_override=[ceiling]*5,
                      cap_override=None,beam_width=4,shortlist=12,
                      allow_same_year=False,objective=objective)
        assert result['final_gameplay_decision']=='STOP' and result['game_write_actions']==0
        # Independent full source R160 replay, not simply trusting original search receipts.
        for p in result['top_plans']:
            starts=[y['start_project_ids'] for y in p['start_by_year']]
            audit=audit_plan(project_index(),start_year=1,
                active_ids=state['team']['initially_active_project_ids'], fixed_first_ids=[],
                previous_project1_active=False,base_project_cap=4,
                annual_budgets=[ceiling]*5,starts=starts,allow_same_year=False,
                advertised_costs=[x['conservative_card_cash_requirement_ecu'] for x in p['start_by_year']],
                advertised_total=p['five_year_conservative_card_cost_ecu'])
            assert audit==p['r160_independent_constraint_replay']
            assert not audit['hard_rule_violations']
        observed.append((name,objective,ceiling,result))
    capture={'schema':'ECOSIM_R191_LIVE_CAPTURE_ADMISSION_V1',
             'status':'PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY',
             'gameplay_gate':'STOP','current_source_is_server_authenticated':False}
    finance={'schema':'ECOSIM_R191_YEAR1_FINANCE_V1',
             'status':'PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY',
             'actual_server_financing_approved':False,'gameplay_gate':'STOP',
             'current_year_budget_ceiling_ecu':150000,
             'tested_first_year_scenario_ecu':150000}
    catalog={'schema':'ECOSIM_R192_CATALOG_PARITY_V1',
             'status':'PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY',
             'observed_card_count':35,'server_attested':False,'gameplay_gate':'STOP'}
    advisory=r207.first_year_options(state,capture,finance,catalog,observed,requested_budget=150000)
    assert advisory['gameplay_gate']=='STOP' and advisory['game_writes']==0
    assert advisory['selected_count']<=3
    assert len({tuple(x['first_year_new_project_ids']) for x in advisory['selected_options']})==advisory['selected_count']
    assert all(x['sampled_r157_worst_direct_effect_delta'] <= x['sampled_r157_stress_range'][1] for x in advisory['selected_options'])
    return {'schema':'ECOSIM_R208_R162_SOURCE_IDENTICAL_SYNTHETIC_GATE_REHEARSAL_V1',
            'status':'PASS_OFFLINE_HISTORICAL_PLAN_WITH_SYNTHETIC_ADMISSION_RECEIPTS_NOT_LIVE',
            'historical_source':'R152_HISTORICAL_R94_READONLY_PACKET_P1_PLAN',
            'operator_capture_authenticated':False,
            'synthetic_current_gate_receipts':True,
            'r156_real_local_intake_exercised':True,
            'r191_r192_native_intake_exercised':False,
            'source_git_blobs':SOURCE_BLOBS,
            'original_search_runs':len(observed),
            'original_independently_audited_plans':sum(len(x[3]['top_plans']) for x in observed),
            'distinct_first_year_actions':advisory['distinct_possible_first_actions'],
            'selected_options':advisory['selected_options'],
            'score_confidence':'DIRECT_CARD_MODEL_SAMPLED_NOT_CITY_FORECAST',
            'game_writes':0,'gameplay_gate':'STOP'}

if __name__=='__main__':
    doc=run()
    print(json.dumps({k:doc[k] for k in ('status','original_search_runs','original_independently_audited_plans','distinct_first_year_actions','game_writes')},ensure_ascii=False))
