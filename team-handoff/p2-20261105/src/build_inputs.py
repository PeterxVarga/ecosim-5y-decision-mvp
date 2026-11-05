import csv,hashlib,json,re,sys
from pathlib import Path
ROOT=Path('/mnt/data/ecosim_p2_joint_work')
sys.path.insert(0,str(ROOT))
from r142_proxy_reference import COEFF,proxy_value
from effect_replay_r147 import normalize_metric
src_b=Path('/mnt/data/EcoSim_P2_Brave_Codex_elo_ellenorzes_20261105.md')
src_s=Path('/mnt/data/Pasted text(20261105-122441).txt')
s1=src_b.read_text(); s2=src_s.read_text()
archive=json.loads((ROOT/'ecosim_projects_20261030.json').read_text())
projects=archive['projects']
assert len(projects)==35 and sum(len(p['effects']) for p in projects)==272
s=s1.split('## SmartCity: hitelesített P1 és P2 értékek',1)[1].split('## Projektek',1)[0]
alias={'Rossz szociális helyzetben lévők aránya':'Rossz szoc. helyzetben lévők aránya','Lakossági viszonyok / elégedettség':'Lakossági viszonyok/elégedettség'}
factors={};prev={};components={};prevcomps={}
for line in s.splitlines():
 if not line.startswith('|'):continue
 c=[v.strip().strip('*') for v in line.strip().strip('|').split('|')]
 if len(c)!=3:continue
 name,x,y=c; name=alias.get(name,name)
 try:x,y=float(x.replace(',','.')),float(y.replace(',','.'))
 except ValueError:continue
 if name in COEFF:factors[name]=y;prev[name]=x
 if name in ('Gazdaság','Környezet','Kormányzás','Életkörülmények','Mobilitás','Emberek'):
  components[name]=y;prevcomps[name]=x
assert len(factors)==29,(len(factors),set(COEFF)-set(factors))
assert abs(proxy_value(factors)-60.52)<.005
assert abs(proxy_value(prev)-58.87)<.005
base=json.loads(Path('/mnt/data/EcoSim_P2_9_muvelet_dontesi_guard_20261105.json').read_text())
assert base['baseline']['running_projects']==10
# historical export status is stale test round; live 10 running IDs from P2 snapshot
running={12,13,14,22,23,24,27,32,34,35}
assert len(running)==10
# Parse P2 subview project's 15-35 as live source, including free 0 cases
section=s2.split('## Projektlefedettség: 35/35',1)[1].split('### Fontosabb projekt',1)[0]
rows={}
for line in section.splitlines():
 if not line.startswith('|') or line.startswith('|---'):continue
 cols=[v.strip() for v in line.strip('|').split('|')]
 if len(cols)<5:continue
 try:pid=int(cols[0])
 except ValueError:continue
 vals=[int(v.replace(' ','').replace('−','-')) for v in cols[-1].split('/')]
 if len(vals)!=4:continue
 rows[pid]=vals
assert set(rows)==set(range(15,36)), sorted(set(range(15,36))-set(rows))
# Parse 1-14 costs from first audit; shared source actually full table, avoid discrepancies
section2=s1.split('## Projektek',1)[1].split('## Pénzügyek',1)[0]
rows_old={}
for line in section2.splitlines():
 if not line.startswith('|') or line.startswith('|---'):continue
 cols=[v.strip() for v in line.strip('|').split('|')]
 if len(cols)!=5:continue
 name=cols[0]
 p=next((p for p in projects if p['name']==name),None)
 if not p:continue
 try:vals=[int(v.replace(' ','').replace('−','-')) for v in cols[1:]]
 except ValueError:continue
 rows_old[p['id']]=[vals[0],vals[2],vals[1],vals[3]]
assert set(rows_old)==set(range(1,15)),sorted(set(range(1,15))-set(rows_old))
rows.update(rows_old)
assert len(rows)==35
live=[];mismatches=[];unmapped_labels=set();unmapped_effects=0
for p in projects:
 id=p['id'];l=dict(p)
 live_vals=rows[id]
 current=(l['startup_cost'],l['investment'],l['maintenance_cost'],l['partner_support'])
 if tuple(live_vals)!=current:mismatches.append((id,current,live_vals))
 l['startup_cost'],l['investment'],l['maintenance_cost'],l['partner_support']=live_vals
 l['status_p2']='Fut' if id in running else 'Nem fut';l['status_p1_fact']=l['status_p2']
 l['live_cost_status_verified']=True
 l['effect_source']='HISTORICAL_TEST_2026-10-30_NOT_P2_REVALIDATED'
 l['effect_count']=len(l['effects'])
 l['source_page']='https://edu.ecosim.hu/simulation/projects'
 l['conservative_incremental_p2_cost']=l['startup_cost']+l['investment']+max(0,l['maintenance_cost'])
 for effect in l['effects']:
  if normalize_metric(effect['metric']) not in COEFF:
   unmapped_effects+=1;unmapped_labels.add(effect['metric'])
 live.append(l)
assert len(live)==35
# Direct model cash reconciliation: previous ongoing signed annual project cost equals finance row negative.
signed_existing=sum(p['maintenance_cost'] for p in live if p['id'] in running)
assert signed_existing==-65800, signed_existing
srcs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [src_b,src_s,ROOT/'ecosim_projects_20261030.json']}
input_state={'schema_version':'ecosim.p2.joined_live_status_finance_historical_effects.v1','sources_sha256':srcs,'game_mutations':0,'market':'I','team':'Jutalom a nap végén','period':'2/5','as_of':'2026-11-05','baseline':{'p1_fact_index':58.87,'p2_plan_index':60.52,'p2_reconstructed_index':round(proxy_value(factors),9),'p2_plan_reserve_ecu':868143,'p2_plan_total_revenue_ecu':5693381,'p2_plan_nonreserve_cost_ecu':4825239,'opening_cash_ecu':309280,'p2_signed_running_maintenance_ecu':signed_existing,'p2_projects_running_count':len(running),'p2_projects_new_started':0,'loan_plan_ecu':0,'p1_fact_factors':prev,'p2_plan_factors':factors,'p2_plan_components':components},'assumptions':{'project_max_starts_scenario':4,'project_max_starts_live_verification':None,'project_effects_live_verified':False,'baseline_plan_saved_proof':None,'unknown_cash_settlement':True,'partner_support_counted_in_cash':False,'negative_new_maintenance_counted_as_funding':False,'projection_scope':'P2 hypothetical marginal project direct factor impacts only; no P3–P5 forecasts'},'projects':live,'quality':{'p2_live_project_cost_status_count':35,'effect_count_historical':sum(p['effect_count'] for p in live),'effect_unmapped_count_historical':unmapped_effects,'unmapped_labels':sorted(unmapped_labels),'historical_live_cost_conflicts':mismatches,'finance_running_maintenance_reconciles':signed_existing==-65800}}
(ROOT/'P2_joined_input.json').write_text(json.dumps(input_state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'total_project_cost_matches':35-len(mismatches),'cost_mismatches':mismatches,'baseline_proxy_p2':proxy_value(factors),'baseline_proxy_p1':proxy_value(prev),'running_signed_maintenance':signed_existing,'project_card_effects':sum(p['effect_count'] for p in live),'unmapped_effect_count':unmapped_effects,'unmapped_labels':sorted(unmapped_labels)},ensure_ascii=False,indent=2))
