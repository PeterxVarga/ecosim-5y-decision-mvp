#!/usr/bin/env python3
"""One consolidated R156 adversarial/offline regression (no game/network calls)."""
from __future__ import annotations
import copy,json,math,re,sys,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from readonly_intake_r156 import validate_export,create_bundle,run,IntakeError
from strategy_5y import read_json,write_json

src=read_json(ROOT/'capture/R156_HISTORICAL_TEST_EXPORT.json')
checks=[]
def ok(label,check):
    if not check:raise AssertionError(label)
    checks.append(label)
def rejected(label,mod,substr=None):
    pack=copy.deepcopy(src);mod(pack)
    try:validate_export(pack)
    except (ValueError,TypeError) as ex:
        if substr and substr.lower() not in str(ex).lower():raise AssertionError(label+': unexpected rejection '+str(ex))
        ok(label,True)
    else:raise AssertionError(label+': invalid input ACCEPTED')

meta=validate_export(src)
ok('Historical R94 operator packet structurally valid',meta['mode']=='HISTORICAL_REFERENCE')
ok('No market cap invented',not meta['market_cap_observed'])
ok('Historical client index weights explicitly supplied',meta['market_weights_observed'])
ok('Provenance source for factors retained',bool(meta['field_sources']['factors']))
ok('29 factors and displayed total retained',len(meta['factor_rows'])==30)
ok('35 project statuses retained',len(meta['project_rows'])==35)
rejected('Reject missing declared schema',lambda p:p.update(schema='OTHER'))
rejected('Reject injected unknown field',lambda p:p.update(foobar=8))
rejected('Reject Bearer token in source note',lambda p:p.update(source_note='Authorization: Bearer secret'))
rejected('Reject cookie in source note',lambda p:p.update(source_note='Cookie: auth=abc'))
rejected('Reject serialized JWT',lambda p:p.update(source_note='eyJ'+'a'*40+'.eyJ'+'b'*32+'.AbCd'+ '0'*16))
rejected('Reject missing team',lambda p:p.update(team=''))
rejected('Reject noninteger period',lambda p:p.update(period=True))
rejected('Reject invalid period range',lambda p:p.update(period=6))
rejected('Reject unclassified kind',lambda p:p.update(kind='UNKNOWN'))
rejected('Reject missing factor',lambda p:p.update(factors_csv='\n'.join(p['factors_csv'].splitlines()[:-1])+'\n'))
rejected('Reject duplicated factor',lambda p:p.update(factors_csv=p['factors_csv'].replace('Vállalkozások száma,50.45','Fizetőképes piac,50.45')))
rejected('Reject nonfinite factor',lambda p:p.update(factors_csv=p['factors_csv'].replace('Fizetőképes piac,72.5','Fizetőképes piac,NaN')))
rejected('Reject nonnumeric factor',lambda p:p.update(factors_csv=p['factors_csv'].replace('Fizetőképes piac,72.5','Fizetőképes piac,bad')))
rejected('Reject missing project',lambda p:p.update(projects_csv='\n'.join(p['projects_csv'].splitlines()[:-1])+'\n'))
rejected('Reject duplicated project',lambda p:p.update(projects_csv=p['projects_csv'].replace('2,false,false','1,false,false')))
rejected('Reject ambiguous blank flags',lambda p:p.update(projects_csv=p['projects_csv'].replace('1,false,false','1,,false')))
rejected('Reject simultaneous running/new flag',lambda p:p.update(projects_csv=p['projects_csv'].replace('1,false,false','1,true,true')))
rejected('Reject forbidden market parameter',lambda p:p['parameters']['market'].update(api_key='should-not-be-here'))
rejected('Reject wrong current weights',lambda p:p['parameters']['market'].update(smartcity_total_weights={'foo':1}))
rejected('Reject invalid project limit',lambda p:p['parameters']['market'].update(maxProjectPerTurn=300))
rejected('Reject unexpected field source',lambda p:p['field_sources'].update(extra='hidden'))
rejected('Reject inaccessible/corrupt CSV header',lambda p:p.update(factors_csv=p['factors_csv'].replace('metric,value','attribute,value')))
rejected('Reject wrong market params type',lambda p:p.update(parameters={'market':[1,2]}))
rejected('Reject oversized capture body',lambda p:p.update(source_note='T'*200000))

current=copy.deepcopy(src)
current.update(capture_mode='CURRENT_READONLY',round='X-Challenge 2026 current fixture – SYNTHETIC',captured_at_local='2026-10-31T16:00:00+01:00',source_evidence_id='OFFLINE_SYNTHETIC_CROSS_CHECK')
current['field_sources']={'factors':'R94 historical reused for rejection-path synthetic test','projects':'R94 historical reused for rejection-path synthetic test','market_index_weights':'Historical weights, synthetic current test only'}
meta_current=validate_export(current)
ok('Current synthetic fixture classified as unverified',meta_current['mode']=='CURRENT_READONLY')
ok('Current mode does not fill missing project limit',not meta_current['market_cap_observed'])
rejected('Reject current placeholder provenance',lambda p:p.update(capture_mode='CURRENT_READONLY',captured_at_local='2026-11-02T00:00:00+01:00',round='REPLACE_ROUND'), 'placeholder')
try:
    wrong=copy.deepcopy(current);wrong['captured_at_local']='2026-11-02'
    validate_export(wrong)
    raise AssertionError('Missing timezone accepted')
except ValueError:ok('Reject timezone-free current timestamp',True)
try:
    wrong=copy.deepcopy(current);wrong['field_sources'].pop('factors')
    validate_export(wrong)
    raise AssertionError('Missing factor source accepted')
except ValueError:ok('Reject current without factor source',True)
try:
    wrong=copy.deepcopy(current);wrong['parameters']['market']['maxProjectPerTurn']=4
    validate_export(wrong)
    raise AssertionError('Sourceless market cap accepted')
except ValueError:ok('Reject project cap without source',True)
try:
    wrong=copy.deepcopy(current);wrong['parameters'].setdefault('team',{})['confirmed_spendable_cash_ecu_by_year']=[100000]*5
    validate_export(wrong)
    raise AssertionError('Fake future cash accepted')
except ValueError:ok('Reject future spendable cash certification',True)

with tempfile.TemporaryDirectory(prefix='r156-qual-') as d:
    root=Path(d)
    packet_dir,receipt=create_bundle(src,root/'historical_verified')
    ok('Reusable R152 manifest materialized',(packet_dir/'manifest.json').is_file())
    ok('SHA256 evidence receipt written',(packet_dir/'R156_ACQUISITION_RECEIPT.json').is_file())
    ok('Historical index factors round back to displayed total',abs(receipt['index_residual'])<0.03)
    ok('Historical provenance remains test',receipt['capture_mode']=='HISTORICAL_REFERENCE')
    ok('No asserted live browser session',receipt['has_live_ecosim_session'] is False)
    ok('Gameplay decision remains STOP',receipt['gameplay_gate']=='STOP')
    ok('No future prediction certified',receipt['not_a_future_index_prediction'] is True)
    ok('No market cap substituted into receipt',receipt['market_cap_observed'] is False)
    ok('No independent server proof asserted',receipt['not_a_server_certification'] is True)
    for f,h in receipt['file_sha256'].items():
        ok('Hash matches '+f,hashlib.sha256((packet_dir/f).read_bytes()).hexdigest()==h)
    try:create_bundle(src,packet_dir)
    except ValueError:ok('Immutable receipt cannot be silently overwritten',True)
    else:raise AssertionError('Overwrite accepted')
    export=root/'historical.json';write_json(export,src)
    cfg=ROOT/'inputs/mvp_run.r155_synthetic.json'
    full=run(export,root/'end_to_end',cfg)
    decision=full['decision_run'];
    ok('Historical real search integration produced 15 candidates',decision['candidates']==15)
    ok('Historical decision gate STOP',decision['gameplay_gate']=='STOP')
    ok('Inherited R155 cash layer still connected',(root/'end_to_end/decision/R155_SOURCE_OPERATING_COUNTERFACTUAL.json').is_file())
    ok('Standalone HTML decision output emitted',(root/'end_to_end/decision/DECISION_DESK.html').is_file())
    ok('Source classification does not claim current',read_json(root/'end_to_end/decision/EVIDENCE_RECEIPT.json')['input_classification']=='HISTORICAL_TEST_ROUND_NOT_CURRENT')
    current_export=root/'current.json';write_json(current_export,current)
    no_cap=run(current_export,root/'current_packet')
    ok('Synthetic current capture can be recorded but not certified',no_cap['decision_run'] is None)
    ready=read_json(root/'current_packet/R156_ACQUISITION_RECEIPT.json')['readiness']
    ok('Current missing cap stays a blocker',any(x['field']=='project_cap' for x in ready['specific_missing_or_invalid_evidence']))
    ok('Current missing finance remains a blocker',any(x['field']=='confirmed_spendable_cash' for x in ready['specific_missing_or_invalid_evidence']))
    try:run(current_export,root/'current_with_bad_historical_config',cfg)
    except ValueError:ok('Current capture refuses historical R155 synthetic policy config',True)
    else:raise AssertionError('Stale policy accepted')
    ok('Rejected current configuration created no receipt',(root/'current_with_bad_historical_config').exists() is False)

html_text=(ROOT/'capture/R156_OFFLINE_CAPTURE.html').read_text(encoding='utf-8')
ok('Offline HTML is self-contained with CSP',"connect-src 'none'" in html_text)
ok('No fetch requests in HTML',not re.search(r'\bfetch\s*\(',html_text))
ok('No external scripts or external resources',not re.search(r'<script[^>]+src=|<link[^>]+href=|<iframe',html_text))
ok('HTML includes manual project input','id="projects_csv"' in html_text)
ok('HTML includes manual factor input','id="factors_csv"' in html_text)
ok('HTML asks for explicit source metadata','id="source_evidence_id"' in html_text)
ok('HTML does not use real historic values in blank current template','72.5' not in html_text)

out={'schema':'ECOSIM_R156_QUALIFICATION_V1','status':'PASS_OFFLINE_ONLY','new_checks':len(checks),
     'checks':checks,'historical_e2e_candidates':15,
     'current_market_team_server_state':'UNAVAILABLE_NOT_FABRICATED',
     'source_historical':'R94_OCT_30_TEST','real_calibration_pairs':0,
     'gameplay_gate':'STOP','game_writes':0,'codex_or_user_terminal_required':False}
write_json(ROOT/'results/R156_QUALIFICATION.json',out)
print('R156_NEW_CHECKS='+str(len(checks))+'/'+str(len(checks))+' PASS; HISTORICAL_E2E=15; GAME=STOP; LIVE_ACCESS=UNAVAILABLE')
