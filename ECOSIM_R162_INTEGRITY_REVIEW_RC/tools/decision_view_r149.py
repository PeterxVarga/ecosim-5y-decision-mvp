#!/usr/bin/env python3
"""Offline static report; NO JavaScript, external styles, browser/network, or game integration.
The summary is descriptive only; it is not a gameplay GO or validated score.
"""
from __future__ import annotations
import html
from collections import defaultdict


def esc(x):return html.escape(str(x),quote=True)


def summarize_first_actions(scenario_rows,cfg):
    """Occurrences are SEARCH OUTPUT FREQUENCIES, never probabilities."""
    counted=defaultdict(lambda:{'appearances':0,'scenario_ids':set(),'costs':[]})
    for scenario in scenario_rows:
        for plan in scenario['candidates']:
            first=plan['start_by_year'][0]
            signature=tuple(first['start_project_ids'])
            obj=counted[signature]
            obj['appearances']+=1
            obj['scenario_ids'].add(scenario['id'])
            obj['costs'].append(first['conservative_card_cash_requirement_ecu'])
    result=[]
    for action,x in counted.items():
        result.append({'first_year_project_ids':list(action),
                       'sampled_plan_occurrences_not_probability':x['appearances'],
                       'found_under_hypothetical_envelopes':sorted(x['scenario_ids']),
                       'first_year_conservative_project_need_ecu':round(max(x['costs']),2),
                       'actual_feasibility_verified':False})
    return sorted(result,key=lambda x:(-len(x['found_under_hypothetical_envelopes']),
                                      -x['sampled_plan_occurrences_not_probability'],
                                       x['first_year_conservative_project_need_ecu'],
                                       x['first_year_project_ids']))[:12]


def derived_proof_gates(cfg,state,gate,problems):
    """A triage of admissible exploration versus provable real-world feasibility."""
    missing={r['field'] for r in gate['specific_missing_or_invalid_evidence']}
    return {
      'historical_illustration_only':cfg['mode']=='HISTORICAL_ILLUSTRATION',
      'conditional_current_snapshot_usable':cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and not problems,
      'declared_source_independently_authenticated':False,
      'actual_spendable_cash_and_loan_authority_confirmed':False,
      'project_limit_client_confirmed_for_current_market':('project_cap' not in missing) and not problems,
      'all_policies_covered_by_measured_causal_equations':False,
      'paired_calibration_available':False,
      'real_terminal_game_score_validated':False,
      'permission_to_mutate_game':False,
      'gameplay_gate':'STOP',
      'reason':'Offline hypotheses, no authoritative current financing, competitor dynamics or server acceptance'
    }


def render_offline_html(report):
    """Single-file accessible static HTML; escaped user-defined fields and no remote resources."""
    title='EcoSim | Offline döntési dosszié'
    candidates=report.get('candidate_comparison') or []
    env=report.get('comparison_envelopes') or []
    statuses=report.get('next_evidence_to_collect') or []
    policy=report.get('policy_track_comparison') or []
    hist=report.get('passive_historical_reconciliation') or {}
    css="""
    :root{color-scheme:light;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#132333;background:#f5f7fa}
    body{margin:0}main{max-width:1100px;margin:0 auto;padding:18px 16px 80px}
    header{padding:36px 16px 24px;background:#142b40;color:white}
    header>div{max-width:1100px;margin:auto}h1{font-size:clamp(24px,4vw,36px);margin:0 0 10px}h2{margin:32px 0 14px;font-size:20px}
    p,li{line-height:1.55}.muted{color:#617084}.headline{font-size:15px;opacity:.88}
    .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
    .card{border:1px solid #e3e8ee;background:white;border-radius:12px;padding:16px;box-shadow:0 2px 6px #10243808}
    .kpi{font-weight:750;font-size:23px;display:block}.small{font-size:12px;color:#617084}
    .warn{background:#fff5e9;border:1px solid #ead1af;padding:14px 16px;border-radius:10px;color:#70460f}
    .table-wrap{overflow:auto;border:1px solid #e3e8ee;border-radius:12px;background:white}
    table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:12px;text-align:left;border-bottom:1px solid #edf0f4;vertical-align:top}th{background:#ebf1f6;font-weight:650;white-space:nowrap}
    tr:last-child td{border-bottom:0}.flag{font-size:11px;background:#eceff2;color:#394d5d;border-radius:6px;padding:3px 6px;white-space:nowrap}
    code{font-family:ui-monospace,Consolas,monospace;font-size:.92em}.gridlist{display:grid;gap:10px}.separator{border-top:1px solid #dce3eb;margin:24px 0}
    .steps{display:flex;gap:10px;flex-wrap:wrap}.steps>span{background:#eaf0f5;border-radius:9px;padding:8px 11px;font-size:12px}
    @media(prefers-color-scheme:dark){:root{color:#e9eef5;background:#101b25}header{background:#0c1620}.card,.table-wrap{background:#192937;border-color:#35506a}.muted,.small{color:#afbdc9}th{background:#243e54}td,th{border-color:#36536a}.warn{background:#3a2d1b;color:#ffdfae;border-color:#776043}.flag,.steps>span{background:#344a60;color:#e3eef8}}
    """
    def table(headers,rows):
        return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
    pieces=['<!doctype html><html lang="hu"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>'+esc(title)+'</title><style>'+css+'</style></head><body>',
      '<header><div><h1>EcoSim · ötéves döntési dosszié</h1><p class="headline">Offline, kizárólag elemzés; nincs EcoSim-kapcsolat, automatikus játékbeli művelet vagy hitelesített nyerő stratégia.</p></div></header><main>',
      '<p class="warn"><strong>Játékbeli döntési kapu: STOP.</strong> A találatok csak megadott költségkeretek és részleges, még nem kalibrált modell alapján készültek. Nem igazolt, hogy végrehajthatók vagy az ötödik évben valóban ezt az indexet adják.</p>',
      '<div class="cards">',
      '<div class="card"><span class="kpi">'+str(len(candidates))+'</span><span class="small">Összehasonlított feltételes ötéves terv</span></div>',
      '<div class="card"><span class="kpi">'+str(len(env))+'</span><span class="small">Feltételezett pénzügyi keret</span></div>',
      '<div class="card"><span class="kpi">'+str(len(report.get('first_year_action_families') or []))+'</span><span class="small">Különböző elsőéves kezdőlépés</span></div>',
      '<div class="card"><span class="kpi">0</span><span class="small">Hitelesített játékbeli eredmény</span></div></div>',
      '<h2>Adatút és bizonyítás</h2><div class="steps"><span>Engedélyezett / történeti bemenet</span><span>Normalizálás</span><span>Ötéves projektkeresés</span><span>Összehasonlítás</span><span>Bizonyítékhiányok</span></div>',
      '<p class="muted">Mód: <strong>'+esc(report['run_mode'])+'</strong>. A bemenetek SHA-256 értékeit a csomag INPUT_HASHES.json fájlja tartalmazza. A kód nem nyit weboldalt és nem módosítja a játékot.</p>',
      '<h2>Ötéves feltételes tervek</h2>']
    if candidates:
        rows=[]
        for c in candidates[:15]:
            plan=' · '.join('É'+str(report.get('start_year',1)+i)+': '+(', '.join('#'+str(n) for n in year) if year else '—') for i,year in enumerate(c['project_ids_by_year']))
            rows.append((c['candidate_id'],plan,', '.join(c['inside_explicit_hypothetical_envelopes']) or 'egyik sem',
                         f"{c['five_year_conservative_project_need_ecu']:,.0f}",
                         f"{c['mapped_terminal_proxy_delta']:+.4f}",
                         str(c['unmapped_or_uncertain_project_effect_occurrences'])))
        pieces.append(table(['Azonosító','Éves projektindítás','Melyik hipotetikus keretbe fér','Ötéves projektteher (ECU)','Részleges indexproxy Δ','Bizonytalan hatáselőfordulás'],rows))
    else:pieces.append('<p>A jelenlegi bizonyítékkapu nem engedi a feltételes keresést. Nem készül fiktív játékbeli terv.</p>')
    r160=report.get('r160_independent_plan_audits') or {}
    if r160:
        pieces.append('<h2>R160 · független projekt-, előfeltétel- és költségellenőrzés</h2>')
        pieces.append('<p class="muted">A forráskártyákból külön újraszámolt projektindítások, éves költségek, határértékek és kijelzett „Fut” feltételek ellenőrzése. A szerveroldali elfogadás és a tényleges finanszírozhatóság ismeretlen marad. Nem modellezett gazdasági hatásból nem csinálunk negatív pontszámot.</p>')
        pieces.append(table(['Mintában újraszámolt tervek','Hibás éves kártya-/projekt-korlát','Feltételes vagy bizonyítatlan szerverelfogadás','Valós eredménydominancia'],[
             (r160['plans_replayed'],r160['hard_errors'],r160['conditional_or_unknown_server_acceptance'],'ISMERETLEN')]))
        if candidates:
            pieces.append(table(['Jelölt','Független auditállapot','Feltételes előfeltételek száma','Éves újraszámolt projektteher ECU'],[
              (c['candidate_id'],c['r160_independent_constraint_replay']['status'],
               len(c['r160_independent_constraint_replay']['conditional_eligibility_items']),
               ', '.join(f"{y['independently_replayed_conservative_cash_need_ecu']:,.0f}" for y in c['r160_independent_constraint_replay']['years']))
              for c in candidates[:10]]))
    if report.get('r157_robust_search_enabled'):
        pieces.append('<h2>R157 · részleges forgatókönyv-minimum szerint keresett alternatívák</h2>')
        pieces.append('<p class="muted">A korábbi kereső két rangsorát egyesítjük; nincs új optimalizáló. Négy hipotetikus intenzitási/fennmaradási profil, a megfigyelt korlátokon rejtett telítettség és kizárólag a leképezett projekthatások. NEM valós alsó pontszámhatár vagy győzelmi valószínűség.</p>')
        pieces.append(table(['Jelölt','Részleges nominális Δ','A négy stresszprofil minimuma (telítettség mellett)','Hiányzó közvetett hatás'],[
             (c['candidate_id'],f"{c['mapped_terminal_proxy_delta']:+.5f}",
              f"{c['r157_scenario_min_clamp_only_mapped_delta']:+.5f}",
              str(c['unmapped_or_uncertain_project_effect_occurrences'])) for c in candidates[:15]]))
        for eid,p in (report.get('r157_sampled_first_year_regret_by_envelope') or {}).items():
            pieces.append('<h2>R157 · '+esc(eid)+' – elsőéves mintabeli forgatókönyvveszteség</h2>')
            pieces.append(table(['Elsőéves projektek','Legjobb mintabeli stressz-minimum','Mintabeli eltérés (nem valódi regret)'],[
                (','.join(map(str,r['first_year_project_ids'])) or '—',
                 f"{r['best_sampled_scenario_min']:+.5f}",f"{r['gap_from_best_sampled_scenario_min']:.5f}") for r in p['families'][:12]]))
    pieces.append('<h2>Elsőéves kezdőlépések – keresési gyakoriság, nem esély</h2>')
    families=report.get('first_year_action_families') or []
    if families:
        pieces.append(table(['Projektazonosítók','Mely hipotetikus keretekben fordul elő','Keresési találatok száma','Konzervatív elsőéves teher'],[
           (', '.join('#'+str(x) for x in r['first_year_project_ids']) or 'Nincs indítás',
            ', '.join(r['found_under_hypothetical_envelopes']),
            r['sampled_plan_occurrences_not_probability'],f"{r['first_year_conservative_project_need_ecu']:,.0f} ECU") for r in families]))
    else:pieces.append('<p>Nincs kellően megalapozott feltételes elsőéves jelölt.</p>')
    quality=report.get('r150_sampled_quality') or {}
    if quality:
        pieces.append('<h2>R150 · részleges Pareto-összevetés</h2>')
        pieces.append('<p class="muted">Csak a heurisztikusan talált tervek között. Az ismeretlen hatások száma bizonyítékhiány, nem bizonyított negatív hatás. A mintabeli dominancia nem jelent valós vagy globális optimumot.</p>')
        pieces.append(table(['Feltételezett keret','Mintán belül belefér','Nem dominált, vizsgált jelöltek','Mintabeli legnagyobb részleges proxy Δ'],[
            (k,v['within_hypothetical_budget_count'],', '.join(v['nondominated_in_sample_ids'][:10]) or '—',
             ('ismeretlen' if v['highest_sampled_mapped_proxy_delta'] is None else f"{v['highest_sampled_mapped_proxy_delta']:+.4f}"))
            for k,v in quality['envelope_frontiers'].items()]))
    pieces.append('<h2>Keretek és működési forgatókönyvek</h2>')
    pieces.append(table(['Keret','Éves feltételezés','Forrásosztály'],[(e['id'],', '.join(f'{x:,.0f}' for x in e['limits_ecu'])+' ECU',e['source_class']) for e in env]))
    if policy:
        pieces.append('<p class="muted">A működési változtatások itt megadott feltételezések, nem az EcoSim által igazolt válaszfüggvények.</p>')
        pieces.append(table(['Forgatókönyv','Számítási státusz','Első opció részleges indexproxy Δ'],[(r['track_id'],r['search_status'],str(r['illustrative_first_option']['mapped_terminal_delta']) if r['illustrative_first_option'] else 'ismeretlen') for r in policy]))
    tax=report.get('r153_source_backed_tax_sensitivity')
    if tax:
        pieces.append('<h2>R153 · eredeti EcoSim-képlethez kötött adó-/díjérzékenység</h2>')
        pieces.append('<p class="muted">A vállalkozóbarátság forrásképletének paraméterfüggő, feltételes eredménye. A bemenet forrásosztálya: <strong>'+esc(tax['source_class'])+'</strong>. A változtatás adóbevételi, vállalatvándorlási és következő évi hatása <strong>ISMERETLEN</strong>; ez nem nyerőstratégia-előrejelzés.</p>')
        taxrows=[]
        for path in tax['paths']:
            for candidate in path['conditional_candidate_comparison'][:8]:
                value=candidate['tax_delta_in_terminal_partial_index']
                combined=candidate['mapped_terminal_proxy_plus_tax_path_delta']
                taxrows.append((path['path_id'],candidate['candidate_id'],
                                f"{value:+.5f}" if value is not None else 'ismeretlen',
                                f"{combined:+.5f}" if combined is not None else 'ismeretlen'))
        pieces.append(table(['Adó/díj pálya','Jelölt','Közvetlen részindexhatás Δ','Projektproxy + forrásadós részΔ (feltételes)'],taxrows))
    fiscal=report.get('r154_source_four_tax_fiscal_tradeoffs')
    if fiscal:
        pieces.append('<h2>R154 · négy forrásalapú adóbevételi képlet</h2>')
        pieces.append('<p><strong>FELTÉTELES, VÁLTOZATLAN ADÓALAPOK.</strong> Az iparűzési, gépjármű-, kommunális és építményadó közvetlen kliensoldali képleteiből számolt különbség. A cégek, járművek, lakosság és ingatlanok évek közötti mozgása nem modellezett. <strong>Nem hozzáférhető készpénz, nem finanszírozási engedély, nem hivatalos játékelőrejelzés.</strong></p>')
        fiscal_rows=[]
        for record in fiscal['path_counterfactuals']:
            value=record['fiscal_comparison']
            for year in value['yearly']:
                fiscal_rows.append((record['tax_path_id'],year['year'],f"{year['baseline_four_tax_income_ecu']:,.0f}",
                                    f"{year['counterfactual_four_tax_income_ecu']:,.0f}",
                                    f"{year['fixed_base_four_tax_delta_ecu']:+,.0f}"))
        pieces.append(table(['Adópálya','Év','Alap négy adó ECU','Feltételes négy adó ECU','Fix adóalap melletti Δ ECU'],fiscal_rows))
    joint=report.get('r154_conditional_joint_pareto')
    if joint:
        pieces.append('<h2>R154 · részleges index kontra feltételes adóbevétel (Pareto)</h2>')
        pieces.append('<p>A megvizsgált tervek közül a részleges indexproxit, négy adó fix adóalapú különbségét és konzervatív projektterhet vetjük össze. Ez <strong>NEM</strong> valós pénz, ötéves előrejelzés vagy győzelmi esély.</p>')
        pieces.append(table(['Projektjelölt','Adópálya','Részindexproxy Δ','Fix bázisú 5 év adó Δ ECU','5 év projektteher ECU'], [
            (a['candidate_id'],a['tax_path_id'],f"{a['conditional_mapped_terminal_proxy_delta']:+.5f}",
             f"{a['five_year_fixed_base_four_tax_delta_ecu']:+,.0f}",f"{a['five_year_conservative_card_cost_ecu']:,.0f}")
             for a in joint['front'][:25]]))
    operating=report.get('r155_source_operating_cash_tradeoffs')
    if operating:
        pieces.append('<h2>R155 · hat szolgáltatási bevétel és intézményi részkiadás</h2>')
        pieces.append('<p><strong>SZINTETIKUS, KÖTÖTT VÁROSÁLLAPOT.</strong> Hat forrásalapú szolgáltatási bevétel, nyolc bérkomponens és hét anyagköltség-komponens közvetlen összehasonlítása. Nem számítja a következő év tényleges népességét, intézményi kapacitását, keresletét, további anyag- és működési tételeit. A részleges különbség nem szabad pénz.</p>')
        operating_rows=[]
        for path in operating['path_counterfactuals']:
            for year in path['annual_rows']:
                operating_rows.append((path['path_id'],year['year'],f"{year['six_fee_delta_ecu']:+,.0f}",
                                       f"{year['covered_institution_cost_delta_ecu']:+,.0f}",
                                       f"{year['partial_annual_operating_net_delta_ecu']:+,.0f}"))
        pieces.append(table(['Pálya','Év','Hat díjbevétele Δ ECU','Bér/anyag részkiadás Δ ECU','Részleges nettó Δ ECU'],operating_rows))
        opfront=report.get('r155_conditional_joint_operating_pareto') or {}
        if opfront.get('front'):
            pieces.append('<h2>R155 · forrásalapú részleges működési pénz–index Pareto</h2>')
            pieces.append(table(['Jelölt','Adó + díj + intézményi pálya','Részleges indexproxy Δ','Ötéves részleges nettó Δ ECU','Projektteher ECU'],[
                (r['candidate_id'],r['path_id'],f"{r['terminal_partial_index_proxy_delta']:+.5f}",
                 f"{r['five_year_conditional_net_operating_delta_ecu']:+,.0f}",
                 f"{r['five_year_project_card_need_ecu']:,.0f}") for r in opfront['front'][:25]]))
    timing=report.get('r158_annual_partial_cash_timing') or {}
    if timing.get('status')=='CONDITIONAL_PARTIAL_CASH_TIMING_NOT_GAME_SOLVENCY':
        pieces.append('<h2>R159 · korrigált, komponensenként időzített pénzügyi stressz</h2>')
        pieces.append('<p><strong>Nem igazolt, elkölthető pénz!</strong> A meglévő R154/R155 forrásképletek ötéves különbségeit a R157 éves projektkártya-teherrel, évenként igazítjuk össze. A nulláról indított kumulált egyenleg kizárólag számítási szemléltetés, nem ismert városi treasury vagy hitelkeret. A pozitív négyadó- és hatdíjcsatorna-különbségek egyéves késleltetése önálló hipotetikus érzékenység; a bér/anyagköltség-változások azonnaliak. Az egyes csatornák nem nettósíthatók az időzítés előtt.</p>')
        pieces.append(table(['Jelölt','Adó/intézmény pálya','5 év ismert résznettó mínusz kártya ECU','Legnagyobb nulla-nyitó kumulált hiány ECU','Pozitív részbevétel +1 év: legnagyobb hiány ECU'],[(r['candidate_id'],r['path_id'],f"{r['five_year_partial_net_after_card_cost_ecu']:+,.0f}",f"{r['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu']:,.0f}",f"{r['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']:,.0f}") for r in timing['combinations'][:20]]))
        pieces.append(table(['Adó/működési pálya','Mintában értékelt jelöltek','Három részleges dimenzió mentén nem dominált'],[(f['path_id'],f['evaluated_with_mapped_index'],f['nondominated_in_sample']) for f in timing['sampled_three_axis_timing_front_by_path']]))
        if timing['combinations']:
            sample=timing['combinations'][0]
            pieces.append('<h2>R159 · első kombináció éves naplója: '+esc(sample['candidate_id'])+' / '+esc(sample['path_id'])+'</h2>')
            pieces.append(table(['Év','Négy adó Δ ECU','Díj mínusz intézményi részkiadás Δ ECU','Projektkártya-teher ECU','Kumulált résznettó, nulla nyitó ECU','Késleltetett pozitív bevétellel, kumulált ECU'],[(y['year'],f"{y['four_tax_delta_ecu']:+,.0f}",f"{y['six_fee_minus_covered_institutions_delta_ecu']:+,.0f}",f"{y['project_card_need_ecu']:,.0f}",f"{y['cumulative_partial_net_zero_opening_cash_ecu']:+,.0f}",f"{y['cumulative_deferred_net_zero_opening_cash_ecu']:+,.0f}") for y in sample['annual_rows']]))
    if hist:
        pieces.append('<h2>Történeti p0 tény és p1 terv – nem ténybeli éves változás</h2>')
        pieces.append(table(['Pillanatkép','Típus','Megjelenített','Visszaszámolt'],[(r['id'],r['kind'],f"{r['displayed_total_index']:.2f}",f"{r['reconstructed_from_display_factors']:.4f}") for r in hist.get('snapshots',[])]))
    audit=report.get('r151_forecast_fact_audit')
    if audit:
        pieces.append('<h2>R151 · valós terv–tény visszamérés</h2>')
        pieces.append('<p class="muted">Csak később megfigyelt azonos periódusú FACT és korábban rögzített PLAN összevetése. Operátori adatok nem jelentenek független szerverhitelesítést. A p0 tény/p1 terv eltérés nem mérési pár.</p>')
        pieces.append(table(['Megadott hivatalos PLAN–FACT pár','Teljes indexre rögzített modellbecsléses pár','Operátori adatokból számolt MAE','Független pontosság'],[(audit['operator_declared_official_pair_count'],audit['paired_full_model_prediction_count'],audit['operator_declared_frozen_full_model_vs_fact_mae'] if audit['operator_declared_frozen_full_model_vs_fact_mae'] is not None else 'nincs adat','nem igazolt')]))
    pieces.append('<h2>Hiányzó legfontosabb bizonyítékok</h2><div class="gridlist">')
    for e in statuses:
        pieces.append('<div class="card"><strong>'+esc(e['key'])+'</strong><p>'+esc(e['smallest_safe_evidence'])+'</p><span class="small">Blokkolja: '+esc(', '.join(e['blocks']))+'</span></div>')
    pieces.extend(['</div><div class="separator"></div><p class="small">Ez a fájl önmagában offline megnyitható, nem tartalmaz külső képet, scriptet, betűtípust vagy hálózati hivatkozást. A projektoptimalizáló heurisztikus; nincs teljes szervermodell, finanszírozási jóváhagyás, jövőbeli migráció- vagy versenytárs-előrejelzés. Szerződéses és versenyszabályi megfelelés nem igazolt.</p></main></body></html>'])
    return ''.join(pieces)
