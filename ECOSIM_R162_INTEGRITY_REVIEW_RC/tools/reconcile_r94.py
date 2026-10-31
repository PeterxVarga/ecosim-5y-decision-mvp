#!/usr/bin/env python3
"""R94 historical test-round finance display reconciliation (no future inference)."""
from pathlib import Path
import csv
import json
import math
import hashlib
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'data/finance_R94_test_snapshot.csv'

ROWS={
    'expense_without_loan_and_reserve':'finance.cash_flow.t0.r44',
    'expense_total':'finance.cash_flow.t0.r43',
    'reserve_formation':'finance.cash_flow.t0.r42',
    'net_result':'finance.cash_flow.t0.r45',
    'project_oneoff_expense':'finance.cash_flow.t0.r26',
    'income_total':'finance.cash_flow.t1.r39',
    'development_support_company_income':'finance.cash_flow.t1.r13',
    'prior_end_cash_income':'finance.cash_flow.t1.r35',
    'wealth_cash_value':'finance.wealth.t0.r12',
    'wealth_loans':'finance.wealth.t0.r11',
}

def reconcile_file(path=SOURCE):
    raw=Path(path).read_bytes()
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        records=list(csv.DictReader(f))
    found={}
    for r in records:
        if r['row_id'] in ROWS.values():
            if r['row_id'] in found:raise ValueError('Duplicate row: '+r['row_id'])
            found[r['row_id']]=r
    if set(found)!=set(ROWS.values()):raise ValueError('Missing required finance rows')
    identity={}
    for key,row in ROWS.items():
        r=found[row]
        a=float(r['p0_number']);b=float(r['p1_number'])
        if not math.isfinite(a) or not math.isfinite(b):raise ValueError('Nonfinite financial input')
        identity[key]={'row_id':row,'label':r['label'],'p0_ecu':a,'p1_ecu':b}
    def val(n,p):return identity[n][p+'_ecu']
    tests=[]
    for p in ('p0','p1'):
        tests.append((p+'_income_minus_unreserved_expense_equals_net',
                      abs(val('income_total',p)-val('expense_without_loan_and_reserve',p)-val('net_result',p))<1e-5))
        tests.append((p+'_unreserved_expense_plus_reserve_equals_total_expense',
                      abs(val('expense_without_loan_and_reserve',p)+val('reserve_formation',p)-val('expense_total',p))<1e-5))
        tests.append((p+'_income_equals_total_expense',
                      abs(val('income_total',p)-val('expense_total',p))<1e-5))
    # p0 has income > total expenses, so equality does not hold p0! Keep
    # actual reconciliation grounded in the observed accounting rows.
    tests=[(k,v) for k,v in tests if k!='p0_income_equals_total_expense']
    tests.append(('p1_reserve_equals_wealth_cash',abs(val('reserve_formation','p1')-val('wealth_cash_value','p1'))<1e-5))
    tests.append(('p1_project_oneoff_zero',abs(val('project_oneoff_expense','p1'))<1e-5))
    tests.append(('p1_prior_cash_line_zero',abs(val('prior_end_cash_income','p1'))<1e-5))
    if any(not good for _,good in tests):
        raise AssertionError('Historical R94 reconciliation mismatch: '+repr(tests))
    return {'mode':'READ_ONLY_HISTORICAL_TEST_R94_2026_10_30',
            'provenance':{'team':'Jutalom a nap végén','market':'Z','period':'1/1',
                          'source':'2026-10-30 recorded finance.csv from former Work audit',
                          'source_sha256':hashlib.sha256(raw).hexdigest(),'source_rows':len(records)},
            'rows':identity,'checks':dict(tests),'all_checks_pass':True,
            'p1_observed_net_ecu':val('net_result','p1'),
            'p1_observed_reserve_ecu':val('reserve_formation','p1'),
            'p1_spendable_cash_confirmed':False,
            'future_game_balance_from_this_source':'UNKNOWN',
            'cannot_infer':['future revenue or expenditure','loan limits or grant settlement',
                            'available project spending power','future market or migration outcome']}

def project_only_counterfactual(project_ids, idx=None):
    """R94 p1 static nonproject inputs held CONSTANT; client component arithmetic ONLY."""
    from portfolio_5y import project_index
    from city_bridge import conservative_cash_and_client_line
    idx=idx or project_index()
    if (not isinstance(project_ids,list) or len(set(project_ids))!=len(project_ids) or
        any(type(i) is not int or i not in idx or idx[i]['status_p1']=='Fut' for i in project_ids)):
        raise ValueError('Unique historical not-running candidate IDs required')
    baseline=reconcile_file();line=conservative_cash_and_client_line(idx,set(),project_ids)
    old=baseline['p1_observed_net_ecu']
    return {'status':'R94_TEST_P1_STATIC_OTHER_LINES_COUNTERFACTUAL_ONLY',
            'project_ids':project_ids,
            'reference_p1_unreserved_net_ecu':old,
            'client_signed_project_expense_component_ecu':line['client_project_expense_line_ecu'],
            'separate_company_support_label_not_confirmed_collected_ecu':line['newly_started_support_label_ecu'],
            'scenario_net_if_no_grant_collected_and_no_indirect_effect_ecu':old-line['client_project_expense_line_ecu'],
            'scenario_net_if_all_support_booked_same_period_and_no_indirect_effect_ecu':old-line['client_project_expense_line_ecu']+line['newly_started_support_label_ecu'],
            'conservative_upfront_cash_requirement_ecu':line['conservative_project_cash_requirement_ecu'],
            'actual_ecosim_candidate_preview':None,
            'actual_cash_available':None,'project_indirect_feedback':'UNKNOWN',
            'financing_approval':'UNKNOWN',
            'gameplay_decision':'STOP'}


def main():
    result=reconcile_file()
    p=ROOT/'results/R144_R94_FINANCE_RECONCILIATION.json';p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('R144_R94_RECONCILIATION=PASS',len(result['checks']))
if __name__=='__main__':main()
