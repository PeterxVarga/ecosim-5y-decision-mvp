import copy
import importlib.util
import unittest
from pathlib import Path

module_file=Path(__file__).with_name("first_round.py")
spec=importlib.util.spec_from_file_location("r207",module_file)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def make_state():
    return {"provenance":{"current_period":1,"source":"operator_current_readonly","round":"Live A","market":"M","team":"T","source_evidence_id":"CAP"},
            "market":{"maxProjectPerTurn":4},
            "team":{"project1_active_previous_period":False,"already_selected_new_project_ids_current_period":[]}}

def make_gates():
    capture={"schema":"ECOSIM_R191_LIVE_CAPTURE_ADMISSION_V1","status":"PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY",
             "gameplay_gate":"STOP","current_source_is_server_authenticated":False}
    finance={"schema":"ECOSIM_R191_YEAR1_FINANCE_V1","status":"PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY",
             "actual_server_financing_approved":False,"gameplay_gate":"STOP", "current_year_budget_ceiling_ecu":100000,
             "tested_first_year_scenario_ecu":90000}
    catalog={"schema":"ECOSIM_R192_CATALOG_PARITY_V1","status":"PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY",
             "observed_card_count":35,"server_attested":False,"gameplay_gate":"STOP"}
    return capture,finance,catalog

def make_result(ids=(1,2),cost=12000,objective="nominal",envelope=90000):
    years=[{"year":i,"start_project_ids":list(ids) if i==1 else [],
            "conservative_card_cash_requirement_ecu":cost} for i in range(1,6)]
    audit={"schema":"ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1","gameplay_gate":"STOP",
           "actual_game_eligibility":None,"actual_funding_approval":None,"status":"PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL",
           "hard_rule_violations":[],"conditional_eligibility_items":[],
           "years":[{"independently_replayed_conservative_cash_need_ecu":cost, "year":y["year"], "new_project_ids":y["start_project_ids"]} for y in years]}
    audit["replayed_card_cost_total_ecu"] = cost*5
    robust = {"gameplay_gate":"STOP", "actual_five_year_score":None,
              "scenario_min_is_game_lower_bound":False,
              "unmodeled_city_dynamics_uncertainty_bounded":False,
              "scenario_min_clamp_only_mapped_delta":0.7,
              "scenario_profiles":[{"profile_id":f"test_{i}",
                                    "conditional_clamp_only_low_delta":x}
                                   for i,x in enumerate((2.1,1.05,1.3,0.7))]}
    plan={"start_by_year":years,"r160_independent_constraint_replay":audit,
          "terminal_mapped_proxy_delta":2.1,"five_year_conservative_card_cost_ecu":cost*5,
          "r157_robust_sensitivity":robust,
          "illustrative_half_effect_sensitivity":[{"mapped_proxy_delta":1.05}],
          "excluded_unknown_effects":[{"metric":"x"}]}
    return {"schema":"ECOSIM_R148_SOURCE_BOUNDED_OFFLINE_STRATEGY_V1", "final_gameplay_decision":"STOP",
            "game_write_actions":0,"network_actions":0,"actual_five_year_score_forecast_validated":False,
            "start_year":1,"r157_search_objective":objective,
            "assumptions":{"annual_project_limit":4,"annual_limit_source":"USER_MARKET_INPUT_OPERATOR_DECLARED_NOT_SERVER_VERIFIED",
                           "budget_source":"EXPLICIT_ILLUSTRATIVE_CLI_SCENARIO_NOT_SPENDABLE_CASH",
                           "official_cash_envelopes_or_illustrative_scenario":[envelope]*5},
            "top_plans":[plan]}

class TestR207(unittest.TestCase):
    def setUp(self):
        self.state=make_state()
        self.capture,self.finance,self.catalog=make_gates()
        self.searches=[("scenario", "nominal",90000,make_result())]
    def run_it(self):
        return r.first_year_options(self.state,self.capture,self.finance,self.catalog,self.searches,requested_budget=90000)
    def reject(self,reason):
        with self.assertRaisesRegex(ValueError,"HOLD_"+reason):self.run_it()
    def test_one_safe_option(self):
        out=self.run_it()
        self.assertEqual(out['selected_count'],1)
        self.assertEqual(out['selected_options'][0]['first_year_new_project_ids'],[1,2])
        self.assertEqual(out['selected_options'][0]['sampled_r157_worst_direct_effect_delta'],0.7)
        self.assertEqual(out['selected_options'][0]['alternative_future_completion_count'],1)
        self.assertFalse(out['finance_server_approved'])
        self.assertEqual(out['game_writes'],0)
        self.assertIn('STOP',r.explain(out))
    def test_three_unique_first_actions(self):
        res=make_result()
        res['top_plans']=[copy.deepcopy(res['top_plans'][0]) for _ in range(4)]
        for ids,p in zip(((1,2),(3,4),(5,), (1,2)),res['top_plans']):
            p['start_by_year'][0]['start_project_ids']=list(ids)
            p['r160_independent_constraint_replay']['years'][0]['new_project_ids']=list(ids)
        self.searches=[('one','nominal',90000,res)]
        out=self.run_it()
        self.assertEqual(out['selected_count'],3)
        self.assertEqual(out['distinct_possible_first_actions'],3)
    def test_reject_old_test_round(self):
        self.state['provenance']['round']='2026 Tesztforduló'
        self.reject('HISTORICAL_NOT_LIVE')
    def test_reject_fake_capture(self):
        self.capture['current_source_is_server_authenticated']=True
        self.reject('R156_R191_CAPTURE')
    def test_reject_unapproved_finance(self):
        self.finance['actual_server_financing_approved']=True
        self.reject('YEAR1_FINANCE_GATE')
    def test_reject_missing_catalog_parity(self):
        self.catalog['status']='UNKNOWN'
        self.reject('R192_CATALOG_GATE')
    def test_reject_fake_budget(self):
        self.searches[0][3]['assumptions']['budget_source']='CONFIRMED_SERVER_FUNDS'
        self.reject('SEARCH_ASSUMPTIONS')
    def test_reject_game_action(self):
        self.searches[0][3]['game_write_actions']=1
        self.reject('R162_OUTPUT_IDENTITY')
    def test_reject_cost_drift(self):
        self.searches[0][3]['top_plans'][0]['r160_independent_constraint_replay']['years'][2]['independently_replayed_conservative_cash_need_ecu']=100
        self.reject('R160_FULL_COST_REPLAY')
    def test_conditional_candidate_ignored(self):
        self.searches[0][3]['top_plans'][0]['r160_independent_constraint_replay']['conditional_eligibility_items']=['condition unknown']
        out=self.run_it()
        self.assertEqual(out['selected_count'],0)
        self.assertEqual(out['audit_rejections']['conditional_eligibility'],1)
    def test_reject_unverified_budget(self):
        self.finance['current_year_budget_ceiling_ecu']=50000
        self.reject('BUDGET_EVIDENCE_MISMATCH')
    def test_reject_missing_selected(self):
        self.state['team']['already_selected_new_project_ids_current_period']=[9]
        self.reject('FIRST_ACTION_IDS')
    def test_reject_partial_years(self):
        self.searches[0][3]['top_plans'][0]['start_by_year'].pop()
        self.reject('YEAR_SEQUENCE')
    def test_same_first_action_different_futures_not_silently_collapsed(self):
        one=make_result()
        a=copy.deepcopy(one['top_plans'][0]);b=copy.deepcopy(a)
        b['start_by_year'][1]['start_project_ids']=[5]
        b['r160_independent_constraint_replay']['years'][1]['new_project_ids']=[5]
        b['terminal_mapped_proxy_delta']=0.25
        b['illustrative_half_effect_sensitivity']=[{'mapped_proxy_delta':0.15}]
        b['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta']=0.09
        b['r157_robust_sensitivity']['scenario_profiles'][3]['conditional_clamp_only_low_delta']=0.09
        one['top_plans']=[a,b]
        self.searches=[('one','nominal',90000,one)]
        out=self.run_it()
        x=out['selected_options'][0]
        self.assertEqual(len(x['sources']),2)
        self.assertEqual(x['scenarios_observed'],['one'])
        self.assertEqual(x['alternative_future_completion_count'],2)
        self.assertEqual(x['sampled_nominal_proxy_range'],[0.25,2.1])
        self.assertEqual(x['sampled_r157_worst_direct_effect_delta'],0.09)
        self.assertEqual(x['example_future_project_starts'][0],[5])
        self.assertEqual(out['scenario_coverage'],1)

    def test_same_first_action_two_scenarios_sourced_separately(self):
        a=make_result();b=make_result(envelope=80000)
        self.searches=[('one','nominal',90000,a),('two','nominal',80000,b)]
        out=self.run_it();x=out['selected_options'][0]
        self.assertEqual(out['scenario_coverage'],2)
        self.assertEqual(x['scenarios_observed'],['one','two'])
        self.assertEqual(x['alternative_future_completion_count'],1)

    def test_budget_tiers_survive_when_high_proxy_dominates(self):
        low=make_result(ids=(3,), cost=20000, envelope=45000)
        middle=make_result(ids=(4,), cost=30000, envelope=72000)
        high=make_result(ids=(5,), cost=40000, envelope=90000)
        for result,worst in ((low,0.15),(middle,0.45),(high,0.95)):
            p=result['top_plans'][0]
            p['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta']=worst
            p['r157_robust_sensitivity']['scenario_profiles'][3]['conditional_clamp_only_low_delta']=worst
        self.searches=[('LOW','nominal',45000,low),('MID','nominal',72000,middle),('HIGH','nominal',90000,high)]
        out=self.run_it()
        self.assertEqual(out['selected_count'],3)
        self.assertEqual([x['first_year_new_project_ids'] for x in out['selected_options']],[[3],[4],[5]])
        self.assertEqual(out['represented_scenarios_in_selected_options'],['HIGH','LOW','MID'])

    def test_reject_duplicate_scenario_label(self):
        self.searches=[self.searches[0],self.searches[0]]
        self.reject('DUPLICATE_SEARCH_SCENARIO')

    def test_reject_future_year_finance_breach(self):
        self.searches[0][3]['top_plans'][0]['start_by_year'][4]['conservative_card_cash_requirement_ecu']=100000
        self.reject('FIVE_YEAR_ILLUSTRATIVE_COST_ENVELOPE')

    def test_reject_total_cost_identity_drift(self):
        self.searches[0][3]['top_plans'][0]['five_year_conservative_card_cost_ecu']=999
        self.reject('R160_FIVE_YEAR_COST_IDENTITY')

    def test_reject_unverified_city_dynamics(self):
        self.searches[0][3]['top_plans'][0]['r157_robust_sensitivity']['unmodeled_city_dynamics_uncertainty_bounded']=True
        self.reject('R157_UNCERTAINTY_GATE')

    def test_reject_r157_stress_mismatch(self):
        self.searches[0][3]['top_plans'][0]['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta']=3
        self.reject('R157_STRESS_REPLAY')

    def test_reject_mislabeled_objective(self):
        self.searches[0]=('one','scenario_min',90000,self.searches[0][3])
        self.reject('R162_OUTPUT_IDENTITY')

if __name__=='__main__':unittest.main()
