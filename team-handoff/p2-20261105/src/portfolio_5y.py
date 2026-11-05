#!/usr/bin/env python3
"""R143 V2.1 five-year *project cost calendar*; not a game simulator.
Static client logic does not establish finance approval or next-year transitions.
No game state, browser, network or external app is accessed.
"""
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def project_index():
    projects=load(ROOT/'data/ecosim_projects_20261030.json')['projects']
    if len(projects)!=35 or {p['id'] for p in projects}!=set(range(1,36)):
        raise ValueError('35-card test-round snapshot mismatch')
    return {p['id']:p for p in projects}

def unique_ids(ids,allowed,description):
    if not isinstance(ids,list) or any(type(i)!=int or i not in allowed for i in ids) or len(ids)!=len(set(ids)):
        raise ValueError('Invalid or duplicate project IDs: '+description)
    return set(ids)

def classify_conditions(p,prior,co_started,idx):
    checks=[]
    for raw in p.get('project_conditions',[]):
        # Export contains DISPLAY strings, not raw JS condition expression.
        label=raw.split(' — ',1)[0].strip()
        negative=label.startswith('not ')
        if negative:label=label[4:].strip()
        matches=[j for j,v in idx.items() if v['name']==label]
        if len(matches)!=1:status='UNKNOWN_DISPLAY_LABEL_NOT_MAPPED';pid=None
        else:
            pid=matches[0]
            available=pid in (prior|co_started)
            if negative:
                status='CONDITION_CONFLICT_IN_PLAN' if available else 'NEGATIVE_DISPLAY_CONDITION_CONSISTENT'
            elif pid in prior:status='PRIOR_ACTIVE_SATISFIES_DISPLAY_CONDITION'
            elif pid in co_started:status='SAME_YEAR_POSSIBLE_ORDER_AND_RENDER_SENSITIVE'
            else:status='UNMET_IN_PROPOSED_PLAN'
        checks.append({'condition_display':raw,'dependency_id':pid,'classification':status,
                       'verification':'DISPLAY_INTERPRETATION_ONLY_NEEDS_CURRENT_GAME_STATE'})
    return checks

def verify_inputs(plan,state):
    years=plan['years'];idx=project_index();allowed=set(idx)
    if len(years)!=5 or [row.get('year') for row in years]!=[1,2,3,4,5]:
        raise ValueError('Need 5 years labelled 1..5')
    base=plan.get('baseline')
    warnings=[]
    if base is None:
        running={i for i,p in idx.items() if p['status_p1']=='Fut'}
        baseline_source='2026-10-30_TEST_ROUND_FALLBACK_NOT_LIVE'
        warnings.append({'issue':'MISSING_BASELINE_USED_TEST_SNAPSHOT_NOT_LIVE'})
    else:
        running=unique_ids(base.get('initially_active_project_ids'),allowed,'baseline')
        baseline_source=base.get('source','UNVERIFIED')
        if not base.get('verified_current_market'):
            warnings.append({'issue':'BASELINE_NOT_VERIFIED_FOR_CURRENT_LIVE_MARKET','source':baseline_source})
    started=set();prior=set(running);annual=[]
    for row in years:
        t=row['year']; ids=unique_ids(row.get('start_project_ids'),allowed,'year '+str(t))
        if ids&(started|running):
            raise ValueError('Cannot newly start a previously started/running project in nonrepeatable scenario')
        checks=[]
        for i in sorted(ids):
            checks += [dict(x,project_id=i,year=t) for x in classify_conditions(idx[i],prior,ids,idx)]
        warnings += [x for x in checks if x['classification'] in ('SAME_YEAR_POSSIBLE_ORDER_AND_RENDER_SENSITIVE','UNMET_IN_PROPOSED_PLAN','CONDITION_CONFLICT_IN_PLAN','UNKNOWN_DISPLAY_LABEL_NOT_MAPPED')]
        started |= ids
        active=started|running
        startinvest=sum(idx[i]['startup_cost']+idx[i]['investment'] for i in ids)
        maintenance_positive=sum(max(idx[i]['maintenance_cost'],0) for i in active)
        maintenance_signed=sum(idx[i]['maintenance_cost'] for i in active)
        grant_label=sum(idx[i]['partner_support'] for i in ids)
        annual.append({'year':t,'new_project_ids':sorted(ids),'all_started_ids':sorted(started),
            'project_conditions_interpreted':checks,
            'conservative_project_cash_requirement_ecu':startinvest+maintenance_positive,
            'signed_client_project_expense_proxy_ecu':startinvest+maintenance_signed,
            'new_partner_support_label_ecu_not_available_cash':grant_label,
            'positive_maintenance_only_ecu':maintenance_positive,'signed_maintenance_ecu':maintenance_signed,
            'funding_status':'UNKNOWN_NOT_SERVER_VALIDATED'})
        prior=active.copy()
    market=state.get('market',{});team=state.get('team',{});provenance=state.get('provenance',{})
    cap=market.get('maxProjectPerTurn')
    bonus=team.get('project1_active_previous_period')
    selected=team.get('already_selected_new_project_ids_current_period')
    if cap is None or type(bonus) is not bool or selected is None:
        warnings.append({'issue':'YEAR_1_GAME_CAP_NOT_VERIFIED','requires':['official_base_cap','previous_project1_numeric_state_eq_1','already_selected_NEW_project_ids']})
    elif type(cap) is not int or cap<0:
        warnings.append({'issue':'INVALID_CAP_VALUE_NOT_EVALUATED'})
    else:
        already=unique_ids(selected,allowed,'selected new ids')
        # Prior/current selected new projects are a SET; never double count overlap.
        selected_union=already|set(annual[0]['new_project_ids'])
        count=len(selected_union)
        allowance=cap+int(bonus)
        if provenance.get('current_period')!=1:
            warnings.append({'issue':'CAP_APPLIES_TO_ANOTHER_PERIOD_NOT_YEAR_1','current_period':provenance.get('current_period')})
        else:
            annual[0]['local_project_count_assessment']={'count':count,'allowance_from_client':allowance,
                'assessment':'COUNT_EXCEEDS_CLIENT_ALLOWANCE' if count>allowance else 'COUNT_WITHIN_CLIENT_ALLOWANCE_NOT_SERVER_APPROVAL'}
        missing_in_plan=already-set(annual[0]['new_project_ids'])
        if missing_in_plan:warnings.append({'issue':'ALREADY_SELECTED_NEW_PROJECTS_OMITTED_FROM_PLAN_COSTS','ids':sorted(missing_in_plan)})
    for x in annual:
        if len(x['new_project_ids'])>4:
            warnings.append({'year':x['year'],'issue':'EXCEEDS_SPOKEN_4_PER_YEAR_SCENARIO_NOT_PROVEN_GAME_GATE'})
    cash=team.get('confirmed_spendable_cash_ecu_by_year'); committed=team.get('committed_costs_ecu_by_year')
    for n,x in enumerate(annual):
        if not (isinstance(cash,list) and len(cash)==5 and type(cash[n]) in (int,float) and cash[n]>=0 and
                isinstance(committed,list) and len(committed)==5 and type(committed[n]) in (int,float) and committed[n]>=0):
            warnings.append({'year':n+1,'issue':'CASH_AND_COMMITMENTS_NOT_CONFIRMED'});continue
        within=cash[n]>=committed[n]+x['conservative_project_cash_requirement_ecu']
        x['funding_status']='WITHIN_USER_INPUT_ENVELOPE_NOT_SERVER_APPROVAL' if within else 'OUTSIDE_USER_INPUT_ENVELOPE'
        x['cash_envelope_source']=team.get('confirmed_spendable_cash_source') or 'UNVERIFIED_SOURCE'
        if not team.get('confirmed_spendable_cash_source'):
            warnings.append({'year':n+1,'issue':'CASH_ENVELOPE_SOURCE_UNVERIFIED'})
    return annual,warnings,baseline_source

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--plan',default='examples/illustrative_plan.json')
    p.add_argument('--state',default='inputs/official_state.template.json')
    p.add_argument('--out',default='results/R143_PROJECT_CASH_CALENDAR.json');a=p.parse_args()
    root=lambda path:Path(path) if Path(path).is_absolute() else ROOT/path
    plan=load(root(a.plan));state=load(root(a.state))
    annual,warnings,baseline_source=verify_inputs(plan,state)
    total=sum(x['conservative_project_cash_requirement_ecu'] for x in annual)
    result={'type':'HISTORICAL_TEST_CARD_COST_CALENDAR_NOT_5Y_GAME_SIMULATOR','no_live_actions':True,
        'final_gameplay_decision':'STOP','score_forecast':'UNKNOWN_NOT_CALCULATED',
        'initial_state_source':baseline_source,
        'video_assumptions_not_live_params':{'reported_project_cap_per_year':4,'reported_loan_rate_example':0.12},
        'annual':annual,'five_year_conservative_project_cash_requirement_sum_ecu':total,
        'warnings':warnings,
        'limitations':['Only nonrepeatable card costs, 2026-10-30 test catalog; repeatable actions, delays and changes to active set not simulated',
            'Same-year dependencies can be possible in client selected state; exact ordering and server acceptance are not verified',
            'Signed negative maintenance is shown as a client proxy, but zeroed in funding envelope',
            'Support not netted against upfront costs; schedule and collection not known',
            'Annual loan interest, project grant settlement, other financial obligations, taxes, market migration and SmartCity index not simulated',
            'A user-input cash-envelope comparison is not credit approval or actual availability',
            'No true future game state, market cap or league qualification predicted']}
    dest=root(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('R143_COST_CALENDAR_CREATED_GAME_STOP YEARS=5 CASH_ESTIMATE='+str(total))
if __name__=='__main__':main()
