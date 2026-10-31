#!/usr/bin/env python3
"""R152 integrated offline evidence -> inherited R151 decision desk pipeline.

No new optimization algorithm.  This command merely normalizes an operator-
supplied local packet, links it to an existing declarative decision run and
writes report artifacts. Always STOP for gameplay.
"""
from __future__ import annotations
import argparse,copy,html,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from observation_bundle_r152 import compile_bundle
from strategy_5y import read_json,write_json
from decision_desk_r149 import make_report,render_md
from decision_view_r149 import render_offline_html
from readiness_r148 import check_state


def execute(bundle_path,config_path,out_dir):
    dest=Path(out_dir).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    capture,state,receipt=compile_bundle(bundle_path)
    orig=read_json(config_path)
    if not isinstance(orig,dict) or orig.get('schema')!='ECOSIM_R149_OFFLINE_DECISION_MVP_V1':
        raise ValueError('Expected existing R149/R151 decision config')
    expected='CURRENT_SNAPSHOT_REVIEW' if capture['capture_mode']=='CURRENT_READONLY' else 'HISTORICAL_ILLUSTRATION'
    if orig.get('mode')!=expected:raise ValueError('Cannot mix historical packet with current search or vice versa')
    if expected=='CURRENT_SNAPSHOT_REVIEW' and capture['kind']!='PLAN':
        raise ValueError('Current search needs same-period PLAN, not finalized FACT')
    if orig.get('start_year')!=capture['period']:raise ValueError('Capture year and search year must match')
    if orig.get('project_cap_assumption') is not None and expected=='CURRENT_SNAPSHOT_REVIEW':
        raise ValueError('Current mode cannot override actual market project cap')
    # The report must read precisely the normalized packet, not a stale state/capture.
    cfg=copy.deepcopy(orig)
    cfg.pop('state_path',None)
    cfg['capture_path']=str(dest/'NORMALIZED_CAPTURE.json')
    # Resolve any original relative auxiliary files *before* relocating config.
    for key in ('historical_read_only_snapshots_path','policy_tracks_path','league_observations_path',
                'paired_plan_observations_path','forecast_audit_path','tax_scenarios_path','tax_revenue_scenarios_path','operating_scenarios_path'):
        if cfg.get(key) and not Path(cfg[key]).is_absolute():
            cfg[key]=str(ROOT/cfg[key])
    write_json(dest/'NORMALIZED_CAPTURE.json',capture)
    write_json(dest/'NORMALIZED_STATE.json',state)
    write_json(dest/'EVIDENCE_RECEIPT.json',receipt)
    write_json(dest/'R152_DECISION_RUN_CONFIG.json',cfg)
    report=make_report(dest/'R152_DECISION_RUN_CONFIG.json')
    report['r152_offline_evidence_packet']={
        'source_classification':receipt['input_classification'],
        'source_file_hashes':receipt['evidence_files'],
        'recomputed_index':receipt['recomputed_display_index'],
        'observed_display_index':receipt['original_display_index'],
        'financial_reconciliation':receipt['finance_R94_reconciliation'],
        'project_state_summary':receipt['project_states'],
        'server_verified':False,'is_actual_forecast_accuracy_evidence':False,
        'gameplay_gate':'STOP'
    }
    report['gameplay_gate']='STOP'
    if report.get('r153_source_backed_tax_sensitivity') is not None:
        write_json(dest/'R153_SOURCE_TAX_COUNTERFACTUAL.json',report['r153_source_backed_tax_sensitivity'])
    if report.get('r154_source_four_tax_fiscal_tradeoffs') is not None:
        write_json(dest/'R154_SOURCE_TAX_REVENUE_COUNTERFACTUAL.json',report['r154_source_four_tax_fiscal_tradeoffs'])
        write_json(dest/'R154_THREE_AXIS_CONDITIONAL_PARETO.json',report['r154_conditional_joint_pareto'])
    if report.get('r155_source_operating_cash_tradeoffs') is not None:
        write_json(dest/'R155_SOURCE_OPERATING_COUNTERFACTUAL.json',report['r155_source_operating_cash_tradeoffs'])
        write_json(dest/'R155_THREE_AXIS_OPERATING_PARETO.json',report['r155_conditional_joint_operating_pareto'])
    ready=check_state(state)
    missing={x['field']:x['issue'] for x in ready['specific_missing_or_invalid_evidence']}
    fields=[]
    for group,field,why in [
        ('P0','project_cap','Actual market project limit'),
        ('P0','baseline_index_factors','Observed index factors'),
        ('P0','current_index_weights','Current market weights'),
        ('P0','active_projects','Existing projects'),
        ('P0','current_selections','Already selected projects'),
        ('P0','prior_project1','Prior project1 special adjustment'),
        ('P0','confirmed_spendable_cash','Authoritative cash available by year'),
        ('P0','committed_costs','Committed cash obligations'),
        ('P0','loan_rates','Applicable loan rates'),
        ('P0','official_preview','Controlled approved game preview')]:
        fields.append({'priority':group,'name':field,'why':why,
                       'status':'MISSING_OR_UNVERIFIED' if field in missing else 'OPERATOR_SUPPLIED_NOT_SERVER_VERIFIED',
                       'details':missing.get(field)})
    gaps={'schema':'ECOSIM_R152_GAP_REPORT_V1','packet_mode':capture['capture_mode'],
          'current_operator_supplied_for_conditional_search':report['current_snapshot_usable_for_conditional_search'],
          'gameplay_gate':'STOP','independently_server_verified':False,
          'fields':fields,
          'must_not_infer':['R94 historical net as available budget','four/year spoken cap as verified market cap',
                            'p0 FACT to p1 PLAN as realized change','synthetic proxy as full-year score',
                            'operator-supplied data as independently authenticated server data']}
    write_json(dest/'R152_MISSING_EVIDENCE.json',gaps)
    write_json(dest/'DECISION_DESK.json',report)
    head=["# R152 — forráshoz kötött döntési dosszié",'',
          '**Játékbeli döntés: STOP; nem hitelesített, ötéves nyerő stratégia.**','',
          f"- Bemenet: `{receipt['input_classification']}`",f"- Megjelenített index: **{receipt['original_display_index']:.2f}**",
          f"- Faktorokból számolt index: **{receipt['recomputed_display_index'] if receipt['recomputed_display_index'] is not None else 'ismeretlen – hiányzó aktuális súly'}**",
          f"- Tényleges EcoSim-mérés / előrejelzési pontosság: **nem igazolt**",'',
          '## Fennmaradó fő adatkapuk','']
    head.extend('- `'+f['name']+'`: '+f['status'] for f in fields)
    (dest/'R152_DECISION_REPORT.md').write_text('\n'.join(head)+'\n\n'+render_md(report),encoding='utf-8')
    body=render_offline_html(report)
    section='<section><h2>R152 · olvasási forráscsomag</h2><p><strong>'+html.escape(receipt['input_classification'])+'</strong>. '
    section+='Az adatcsomag SHA-256 ellenőrzése sikeres; szerverhitelesítés és játékbeli jogosultság nem következik belőle.</p>'
    section+='<p>Megjelenített index: '+html.escape(str(receipt['original_display_index']))+', faktor-összegzés: '+html.escape(str(receipt['recomputed_display_index']))+'. '
    section+='Pénzügyi tervkeret: <strong>nem igazolt</strong>. Terv–tény pontosság: <strong>nem ismert</strong>.</p></section>'
    body=body.replace('</main>',section+'</main>')
    (dest/'DECISION_DESK.html').write_text(body,encoding='utf-8')
    return {'mode':capture['capture_mode'],'candidates':len(report['candidate_comparison']),
            'index_residual':receipt['rounding_residual'],'missing_fields':[f['name'] for f in fields if f['status']=='MISSING_OR_UNVERIFIED'],
            'output_directory':str(dest),'gameplay_gate':'STOP'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',required=True);p.add_argument('--decision-config',required=True);p.add_argument('--out-dir',required=True)
    a=p.parse_args()
    res=execute(a.bundle,a.decision_config,a.out_dir)
    print('R152_EVIDENCE_TO_DECISION=PASS; source_mode='+res['mode']+'; candidates='+str(res['candidates'])+'; GAME=STOP')

if __name__=='__main__':main()
