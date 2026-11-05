#!/usr/bin/env python3
"""Offline, conservative scenario enumeration; NOT an EcoSim server simulator.
Standard library only. No network, no browser interaction, no JavaScript execution.
"""
import argparse, json, itertools
from pathlib import Path
from collections import defaultdict
from effect_replay_r147 import replay_effects, normalize_metric

WEIGHTS = {
    "Gazdaság": (.25, ["Fizetőképes piac", "Vállalkozások száma", "Vállalkozóbarátság", "Foglalkoztatottság"], [], 4),
    "Környezet": (.20, ["Fenntarthatóság", "Vízgazdálkodás", "Levegőminőség", "Zöld területek aránya", "Hulladékgazdálkodási helyzet"], [], 5),
    "Kormányzás": (.15, ["Adminisztráció", "Lakásgazdálkodás", "Digitalizáció"], [], 3),
    "Életkörülmények": (.15, ["Közbiztonság", "Oktatási intézmények", "Egészségügy", "Szociális", "Sport", "Művelődés", "Átlagos lakásérték"], ["Rossz szoc. helyzetben lévők aránya"], 8),
    "Mobilitás": (.10, ["Településfejlettség", "Közlekedési minőség", "Tömegközlekedők aránya, %"], ["Autók száma / 100 fő"], 3),
    "Emberek": (.15, ["Lakossági viszonyok/elégedettség", "Munkakörülmények", "Lakosság képzettsége"], ["Munkanélküli arány"], 3)
}

def metric_coefficients():
    coeff={}
    for grp,(weight,pos,neg,den) in WEIGHTS.items():
        for name in pos:coeff[name]=weight/den
        for name in neg:coeff[name]=-weight/(4 if grp in ("Mobilitás", "Emberek") else den)
    coeff["Adósság / vagyon"] = .15/4
    return coeff

COEFF=metric_coefficients()
# R141 approximation includes an inverse of the negative socioeconomic share.
CONSTANT=.15 / 8 * 100

def proxy_value(v): return sum(v[m]*c for m,c in COEFF.items()) + CONSTANT

def evaluate(projects, baseline):
    factors=dict(baseline)
    pairs=[(p['id'],e) for p in sorted(projects,key=lambda p:p['id']) for e in p['effects']]
    records=replay_effects(factors,pairs,COEFF)
    unknown=[{'project_id':r.get('project_id'), 'project_ids':r.get('project_ids'),
              'metric':r.get('project_metric'), 'factor':r.get('factor'),
              'reason':r.get('reason','SATURATED_BASELINE_UNIDENTIFIED')}
             for r in records if not r['mapped'] or r.get('uncertain_due_to_saturation')]
    return proxy_value(factors)-proxy_value(baseline),unknown

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='results')
    args=parser.parse_args()
    base=Path(__file__).resolve().parent.parent
    projects=json.loads((base/'data/ecosim_projects_20261030.json').read_text())['projects']
    r141=json.loads((base/'data/ECOSIM_R141_PROJECT_PROXY.json').read_text())
    baseline=r141['baseline_from_UI']
    assert len(projects)==35 and sum(p['status_p1']=='Fut' for p in projects)==6
    assert len(baseline)>=25 and abs(proxy_value(baseline)-52.4837333)<0.02
    assert {p['id'] for p in projects} == set(range(1,36))
    # When the UI says a prerequisite is already 'Fut', do not assume launching
    # both projects in one period satisfies it. Exclude #30 & #31 in strict view.
    already_running={p['name'] for p in projects if p['status_p1']=='Fut'}
    eligible=[]; excluded=[]
    for p in projects:
        if p['status_p1']=='Fut':continue
        unknown_cond=[cond for cond in p['project_conditions'] if cond.rsplit(' — ',1)[0] not in already_running]
        if unknown_cond:
            excluded.append({'id':p['id'],'name':p['name'],'conditions':unknown_cond})
            continue
        eligible.append(p)
    assert len(eligible)+len(excluded)==29
    # No grants or negative run costs counted as usable cash in safe budget.
    def budget_cash(p):return p['startup_cost']+p['investment']+max(0,p['maintenance_cost'])
    def client_cost(p):return p['startup_cost']+p['investment']+p['maintenance_cost']
    assert all(budget_cash(p)>=client_cost(p) for p in eligible)
    for p in eligible:
        if p['startup_cost']<0 or p['investment']<0:raise ValueError('Negative startup/invest unexpectedly present')
    individual=[]
    for p in eligible:
        delta,unk=evaluate([p],baseline)
        individual.append({'id':p['id'],'name':p['name'],'proxy_delta':round(delta,6),'unknown_count':len(unk),'unknown_metrics':sorted(set(x['metric'] for x in unk)),'cash_conservative':budget_cash(p),'cash_client_signed':client_cost(p),'three_year_conservative':p['startup_cost']+p['investment']+3*max(0,p['maintenance_cost']),'annual_maintenance_signed':p['maintenance_cost'],'separate_grant_label':p['partner_support']})
    individual.sort(key=lambda x:(-x['proxy_delta'],x['cash_conservative'],x['id']))
    budgets=[30000,50000,100000,200000]
    capacities=[1,2,3,4,5]
    top={ (k,b):[] for k in capacities for b in budgets }
    evaluated=0
    for k in capacities:
        for combo in itertools.combinations(eligible,k):
            cost=sum(budget_cash(p) for p in combo)
            if cost>max(budgets): continue
            delta,unk=evaluate(combo,baseline)
            evaluated+=1
            ids=[p['id'] for p in combo]
            payload={'ids':ids, 'names':[p['name'] for p in combo], 'proxy_delta':round(delta,6), 'unknown_count':len(unk), 'unmapped_metrics':sorted(set(x['metric'] for x in unk)), 'safe_cash':cost, 'signed_client_cash':sum(client_cost(p) for p in combo), 'support_labels':sum(p['partner_support'] for p in combo), 'three_year_conservative':sum(p['startup_cost']+p['investment']+3*max(0,p['maintenance_cost']) for p in combo)}
            for b in budgets:
                if cost<=b:
                    arr=top[k,b]
                    arr.append(payload)
                    arr.sort(key=lambda x:(-x['proxy_delta'],x['unknown_count'],x['safe_cash'],x['ids']))
                    if len(arr)>5:arr.pop()
    scenarios=[]
    for k,b in top:
        scenarios.append({'exact_project_count_assumption':k,'illustrative_budget_ecu':b,'top_5':top[k,b]})
    out=Path(args.out)
    if not out.is_absolute():out=base/out
    out.mkdir(parents=True,exist_ok=True)
    result={'type':'Ecosim offline proxy NOT actual or authorized gameplay','baseline_proxy':proxy_value(baseline),'project_counts':{'all':35,'already_running':6,'eligible_in_strict_mode':len(eligible),'excluded_for_unmet_prerequisite':excluded},'assumptions':{'budgets':'30k/50k/100k/200k are illustrative, never proven spendable','capacity':'K=1..5 exact assumptions, no actual project limit proven','grants':'NEVER subtracted from required cash','negative_maintenance':'NEVER used as guaranteed free cash','effects':'Only exact display-to-metric names, multiplicative; missing effects UNKNOWN, not zero','cash':'conservative upper proxy on p1 cost under assumptions, NOT approved available cash','project_type':'assumes new non-repeatable; verify with current setup','dependencies':'requires prerequisite already running prior to same period; same-period co-start blocked'},'combinations_evaluated_within_top_budget':evaluated,'single_projects':individual,'scenarios':scenarios}
    (out/'R142_SCENARIOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# EcoSim R142 — offline scenario screening, NOT a final gameplay decision','',f"Baseline proxy: {proxy_value(baseline):.6f}; UI p1: 52.48.",'','**No grant counted toward spendable funds; no negative maintenance treated as assured cash.**','',f"Eligible strict candidates: {len(eligible)}/29; excluded dependencies: {excluded}",'','All budgets and project caps here are explicitly **hypothetical**. No EcoSim project start, save or API replay was performed.','', '## Illustrative top combinations','', '| K (exact) | Cash threshold (ECU) | IDs | Conservative cash | Mapped Δ index proxy | Unmapped effects |', '|---:|---:|---|---:|---:|---:|']
    for group in scenarios:
        winner=group['top_5'][0] if group['top_5'] else None
        if winner: lines.append(f"| {group['exact_project_count_assumption']} | {group['illustrative_budget_ecu']:,} | {','.join(map(str,winner['ids']))} | {winner['safe_cash']:,} | {winner['proxy_delta']:+.4f} | {winner['unknown_count']} |")
        else: lines.append(f"| {group['exact_project_count_assumption']} | {group['illustrative_budget_ecu']:,} | None | — | — | — |")
    lines.extend(['','## Gating facts for actual decision','', '- Verify maximum projects per period from authorized UI/setup.', '- Verify actual admissible project budget, loans, reserve and grants timing.', '- Verify current p1 state, special project type/repeatable configuration.', '- Verify candidate cost and index in actual EcoSim preview; no Start/Save without explicit operator authorization.', '- Compare exact preview to this approximation and stop if material disagreement.', '', '## Falsification warning', '', 'Unmapped effects and nonlinear market curves can reverse the ranking. Rankings are not guaranteed optimal.'])
    (out/'R142_SCENARIOS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"R142_PROXY=PASS eligible={len(eligible)} excluded={len(excluded)} combos={evaluated} baseline={proxy_value(baseline):.6f} output={out}")

if __name__=='__main__': main()
