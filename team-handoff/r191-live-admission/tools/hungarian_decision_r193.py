#!/usr/bin/env python3
"""R193. Offline, deterministic Hungarian team-facing explanation of R191/R192 model receipts.

Never generates gameplay actions. Project-card claims are always attributed to
source cards, not to a true EcoSim outcome or to marginal project causality.
"""
from __future__ import annotations

import math
import re
from collections import Counter

SCHEMA = 'ECOSIM_R193_HUMAN_DECISION_EXPLANATION_V1'
NEGATIVE_IS_BETTER = {'Munkanélküliség', 'Munkanélküli arány',
                      'Rossz szoc. helyzetben lévők aránya', 'Autók száma / 100 fő'}

class ExplanationHold(ValueError):
    pass


def _money(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ExplanationHold('NONFINITE_MONEY')
    return f'{value:,.0f}'.replace(',', ' ')


def _decimal(value, digits=6):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ExplanationHold('NONFINITE_SCORE')
    return f'{value:.{digits}f}'.replace('.', ',')


def _percent(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ExplanationHold('INVALID_EFFECT_PERCENT')
    return f'{value:+g}'.replace('.', ',') + '%'


def _escape(text):
    if not isinstance(text, str) or not text.strip() or len(text) > 400:
        raise ExplanationHold('INVALID_CARD_TEXT')
    return re.sub(r'([\\`*_{}\[\]()#+.!<>|])', r'\\\1', text.strip())


def _effect_explanation(card, *, modeled_metrics=None):
    effects = card.get('effects')
    if not isinstance(effects, list):
        raise ExplanationHold('MISSING_CARD_EFFECTS')
    positive, unfavorable, unmapped = [], [], []
    seen = set()
    for e in effects:
        if not isinstance(e, dict) or not isinstance(e.get('metric'), str):
            raise ExplanationHold('MALFORMED_CARD_EFFECT')
        metric = e['metric'].strip()
        val = e.get('value_percent')
        if not metric or metric in seen or type(val) not in (int, float) or not math.isfinite(val):
            raise ExplanationHold('MALFORMED_CARD_EFFECT')
        seen.add(metric)
        if not val:
            continue
        is_mapped = modeled_metrics is None or metric in modeled_metrics or (
            metric == 'Munkanélküliség' and 'Munkanélküli arány' in modeled_metrics)
        sign = -1 if metric in NEGATIVE_IS_BETTER else 1
        item = (abs(val), metric, val)
        if not is_mapped:
            unmapped.append(item)
        elif sign * val > 0:
            positive.append(item)
        else:
            unfavorable.append(item)
    positive.sort(key=lambda t: (-t[0], t[1])); unfavorable.sort(key=lambda t: (-t[0], t[1]))
    unmapped.sort(key=lambda t: (-t[0], t[1]))
    def format_effect(x):
        _, metric, val = x
        polarity = ' (a csökkenés kedvező)' if metric in NEGATIVE_IS_BETTER and val < 0 else ''
        return f'{_escape(metric)} {_percent(val)}{polarity}'
    gain = '; '.join(format_effect(x) for x in positive[:2])
    risk = '; '.join(format_effect(x) for x in unfavorable[:2])
    unknown = '; '.join(format_effect(x) for x in unmapped[:2])
    return gain, risk, unknown


def explain(receipt, catalog, *, modeled_metrics=None):
    """Return machine-readable per-year calendar and printable Hungarian Markdown.

    Inputs must come from a completed R191/R192 admission/audit. The renderer
    validates the receipt independently, and cannot turn a HOLD into a recommendation.
    """
    if not isinstance(receipt, dict) or receipt.get('schema') != 'ECOSIM_R191_HARDENED_PINNED_SHADOW_V1':
        raise ExplanationHold('R191_RECEIPT_REQUIRED')
    if receipt.get('status') != 'PASS_CONDITIONAL_MODEL_SHADOW_ONLY':
        raise ExplanationHold('RECEIPT_NOT_PASSED')
    if receipt.get('gameplay_gate') != 'STOP' or receipt.get('actual_gameplay_approved') is not False:
        raise ExplanationHold('MISSING_GAMEPLAY_STOP')
    if receipt.get('r162_result_game_action') != 'STOP':
        raise ExplanationHold('SOURCE_SEARCH_NOT_STOP')
    audit = receipt.get('independent_replay')
    if not isinstance(audit, dict) or audit.get('status') != 'PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL' or audit.get('hard_violations') != 0 or audit.get('conditional_items') != 0:
        raise ExplanationHold('INDEPENDENT_AUDIT_NOT_CLEAN')
    mode = receipt.get('mode')
    if mode not in ('historical-test', 'current-readonly'):
        raise ExplanationHold('UNKNOWN_MODE')
    admission = receipt.get('admission')
    if not isinstance(admission, dict) or admission.get('gameplay_gate') != 'STOP':
        raise ExplanationHold('MISSING_ADMISSION')
    if admission.get('mode') != ('historical' if mode == 'historical-test' else 'current'):
        raise ExplanationHold('MODE_CONTRADICTION')
    start = admission.get('current_period')
    if type(start) is not int or not 1 <= start <= 5:
        raise ExplanationHold('INVALID_PERIOD')
    if mode == 'current-readonly':
        if (admission.get('r156_capture', {}).get('status') != 'PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY'
                or admission.get('year1_finance', {}).get('status') != 'PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY'
                or admission.get('catalog_parity', {}).get('status') != 'PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY'):
            raise ExplanationHold('CURRENT_ADMISSION_NOT_COMPLETE')
    rows = receipt.get('years')
    if not isinstance(rows, list) or len(rows) != 6-start or any(not isinstance(r, list) for r in rows):
        raise ExplanationHold('WRONG_PLAN_HORIZON')
    if not isinstance(catalog, dict):
        raise ExplanationHold('CARD_CATALOG_REQUIRED')
    initial_active, fixed = admission.get('active'), admission.get('fixed')
    if not isinstance(initial_active, list) or not isinstance(fixed, list):
        raise ExplanationHold('BASELINE_NOT_DECLARED')
    if any(type(x) is not int for row in rows for x in row) or any(type(x) is not int for x in initial_active + fixed):
        raise ExplanationHold('INVALID_PROJECT_ID')
    used = [x for row in rows for x in row]
    if len(used) != len(set(used)) or len(set(initial_active)) != len(initial_active) or len(set(fixed)) != len(fixed):
        raise ExplanationHold('DUPLICATE_PROJECT_ID')
    if set(used) & set(initial_active) or not set(fixed) <= set(rows[0]) or set(fixed) & set(initial_active):
        raise ExplanationHold('PLAN_VS_BASELINE_INCONSISTENCY')
    for p in set(initial_active + used):
        if p not in catalog or not isinstance(catalog[p], dict):
            raise ExplanationHold('MISSING_PROJECT_CARD')
    # Fail on unknown or contradictory dependencies; never improvise sequencing.
    names = {v.get('name'): k for k,v in catalog.items() if isinstance(v, dict)}
    if any(not isinstance(n,str) or not n.strip() for n in names):
        raise ExplanationHold('INVALID_CATALOG_NAMES')
    if len(names) != len(catalog):
        raise ExplanationHold('NON_UNIQUE_CATALOG_NAMES')
    carried = set(initial_active)
    financial_rows = []
    for offset, ids in enumerate(rows):
        year = start + offset
        if len(set(ids)) != len(ids):
            raise ExplanationHold('DUPLICATE_YEAR_PROJECT')
        current = set(ids)
        for pid in current:
            conditions = catalog[pid].get('project_conditions', [])
            if not isinstance(conditions, list):
                raise ExplanationHold('UNKNOWN_PROJECT_CONDITION')
            for raw in conditions:
                if not isinstance(raw,str):
                    raise ExplanationHold('UNKNOWN_PROJECT_CONDITION')
                lab = raw.split(' — ',1)[0].strip()
                neg = lab.startswith('not ')
                dep = names.get(lab[4:].strip() if neg else lab)
                if dep is None:
                    raise ExplanationHold('UNRESOLVED_PROJECT_DEPENDENCY')
                if (neg and dep in (current | carried)) or (not neg and dep not in carried):
                    raise ExplanationHold('UNMET_PROJECT_DEPENDENCY')
        running = current | carried
        for x in running:
            c = catalog[x]
            for k in ('startup_cost','investment','maintenance_cost','partner_support'):
                v = c.get(k)
                if type(v) not in (int,float) or not math.isfinite(v):
                    raise ExplanationHold('INVALID_CARD_MONEY')
            if c['startup_cost'] < 0 or c['investment'] < 0 or c['partner_support'] < 0:
                raise ExplanationHold('INVALID_CARD_MONEY')
        first = sum(catalog[x]['startup_cost'] + catalog[x]['investment'] for x in ids)
        maint = sum(max(0, catalog[x]['maintenance_cost']) for x in running)
        grants = sum(catalog[x]['partner_support'] for x in ids)
        total = first+maint
        envelope = receipt.get('annual_envelopes')
        if not isinstance(envelope,list) or len(envelope)!=len(rows):
            raise ExplanationHold('MISSING_ANNUAL_BUDGET')
        boundary = envelope[offset]
        if not isinstance(boundary,dict) or boundary.get('year')!=year:
            raise ExplanationHold('ANNUAL_BUDGET_MISMATCH')
        ceiling = boundary.get('scenario_ceiling_ecu')
        if type(ceiling) not in (int,float) or not math.isfinite(ceiling) or ceiling<0:
            raise ExplanationHold('INVALID_SCENARIO_CEILING')
        if total > ceiling+1e-7:
            raise ExplanationHold('PLAN_EXCEEDS_SCENARIO_CEILING')
        # No overclaim: money treated as conservative only, grants are not deducted.
        projects = []
        for pid in sorted(ids):
            c = catalog[pid]
            gain, risk, unmapped = _effect_explanation(c, modeled_metrics=modeled_metrics)
            projects.append({
                'id':pid, 'name':c['name'], 'already_selected':offset==0 and pid in fixed,
                'startup_and_investment':c['startup_cost']+c['investment'],
                'maintenance_per_year':c['maintenance_cost'],
                'source_label_partner_support':c['partner_support'],
                'positive_card_effects':gain, 'unfavorable_card_effects':risk,
                'unmapped_card_effects':unmapped,
            })
        financial_rows.append(dict(year=year, projects=projects, once=first,
                                   annual_positive_maintenance=maint, total=total,
                                   partner_support_label=grants, scenario_ceiling=ceiling,
                                   remaining_scenario_ceiling=ceiling-total))
        carried |= current
    baseline_score, final_score = receipt.get('initial_score'),receipt.get('final_score')
    if type(baseline_score) not in (int,float) or type(final_score) not in (int,float) or not math.isfinite(baseline_score) or not math.isfinite(final_score):
        raise ExplanationHold('INVALID_MODEL_SCORE')
    if final_score < baseline_score-1e-9:
        raise ExplanationHold('MODEL_SCORE_DETERIORATED')
    lines = []
    if mode == 'historical-test':
        lines.extend(['# Ötéves projektjavaslat – TÖRTÉNETI TESZT, NEM ÉLES UTASÍTÁS','',
                      '**Ezt a csomagot csak a tesztfordulós adatokra számoltuk. Az éles játékban ebből még ne indítsatok projekteket.**',''])
    else:
        lines.extend(['# Ötéves projektjavaslat – aktuális, ellenőrzendő modelljavaslat','',
                      '**Ez döntéstámogatás, nem végrehajtási engedély. A projektindítást csak az aktuális játékfelületen és a csapattal jóváhagyva végezzétek.**',''])
    first_year = financial_rows[0]
    existing = [p for p in first_year['projects'] if p['already_selected']]
    new = [p for p in first_year['projects'] if not p['already_selected']]
    lines.append(f'## Mit válasszunk most, a {start}. évben?')
    if new:
        names_new = ', '.join('**'+_escape(p['name'])+'** (#'+str(p['id'])+')' for p in new)
        lines.append('A modell szerint ezt a '+str(len(new))+' projektet érdemes közösen megfontolni: '+names_new+'.')
    else:
        lines.append('Az első évre nincs újonnan indítandó projekt a tervben.')
    if existing:
        lines.append('Már kiválasztott (ne indítsátok újra): '+', '.join(_escape(p['name'])+' (#'+str(p['id'])+')' for p in existing)+'.')
    lines.append(f'**Elsőéves konzervatív projektigény: {_money(first_year["total"])} ECU**, ebből '
                 f'{_money(first_year["once"])} ECU indulás és beruházás, '
                 f'{_money(first_year["annual_positive_maintenance"])} ECU az összes ekkor futó projekt pozitív fenntartása.')
    lines.append(f'A megadott **{_money(first_year["scenario_ceiling"])} ECU-s vizsgálati keretből** '
                 f'{_money(first_year["remaining_scenario_ceiling"])} ECU maradna. '
                 'A partnertámogatást nem vontuk le, mert folyósításának ideje és feltétele nem igazolt.')
    if mode == 'historical-test':
        lines.append('**Fontos:** a keret feltételezés, nem igazoltan elkölthető városi pénz.')
    else:
        lines.append('**Fontos:** az elsőéves pénzügyi adat operátor által rögzített, nem szerver által jóváhagyott finanszírozás.')
    lines.append('')
    lines.append('### Miért pont ezek?')
    lines.append('Az indokok a megjelenített projektkártyák hatásai, **nem** bizonyított különálló indexpont-hozzájárulások.')
    for p in first_year['projects']:
        title = f'- **#{p["id"]} {_escape(p["name"])}**'
        if p['already_selected']:title+=' (már kiválasztva)'
        lines.append(title)
        lines.append('  - Indítás és beruházás: '+_money(p['startup_and_investment'])+' ECU; éves kártya szerinti fenntartás: '+_money(p['maintenance_per_year'])+' ECU.')
        if p['positive_card_effects']:lines.append('  - Kedvezőként modellezett kártyahatások: '+p['positive_card_effects']+'.')
        else:lines.append('  - Közvetlenül kedvező indexfaktor-hatás a megadott kártyából nem különíthető el.')
        if p['unfavorable_card_effects']:lines.append('  - Figyelni kell a kedvezőtlen kártyahatásokra is: '+p['unfavorable_card_effects']+'.')
        if p['unmapped_card_effects']:lines.append('  - A modellben nem közvetlenül leképezett kártyahatás: '+p['unmapped_card_effects']+'.')
    lines.extend(['','## Mi legyen a következő években?'])
    for row in financial_rows[1:]:
        if not row['projects']:
            message='ne indítsunk új projektet; a már futók fenntartási terhe megmarad.'
        else:
            message='; '.join(f'**{_escape(p["name"])}** (#{p["id"]})' for p in row['projects'])+'.'
        lines.append(f'- **{row["year"]}. év:** {message} '
                     f'Éves konzervatív projektigény: **{_money(row["total"])} ECU** '
                     f'({_money(row["once"])} indulás/beruházás + {_money(row["annual_positive_maintenance"])} pozitív fenntartás).')
        for p in row['projects']:
            why = p['positive_card_effects'] or 'külön kedvező, közvetlenül modellezett kártyahatás nem azonosítható'
            line = f'  - **#{p["id"]} – Miért?** {why}.'
            source = catalog[p['id']]
            deps = source.get('project_conditions', [])
            if deps:
                line += ' Feltétel: ' + '; '.join(_escape(x) for x in deps) + ' (a modellben már korábban teljesül).'
            if p['unfavorable_card_effects']:
                line += ' Kockázat a kártyán: ' + p['unfavorable_card_effects'] + '.'
            lines.append(line)
    orig_first = receipt.get('initial_first_year_ids')
    if isinstance(orig_first,list) and all(type(x) is int for x in orig_first):
        now_first = set(rows[0]); was = set(orig_first)
        lines.extend(['','## Mi változott a kiinduló tervhez képest?'])
        if now_first == was:
            lines.append('Az első éves projektcsomag **változatlan**; a kereső a későbbi évek időzítését javította.')
        else:
            added = sorted(now_first-was); removed = sorted(was-now_first)
            chunks=[]
            if added:chunks.append('előrébb került: '+', '.join(_escape(catalog[x]['name'])+' (#'+str(x)+')' for x in added))
            if removed:chunks.append('későbbi évre került: '+', '.join(_escape(catalog[x]['name'])+' (#'+str(x)+')' for x in removed))
            lines.append('Az első évben '+ '; '.join(chunks) + '. Ez **átütemezés**, nem a projekt teljes törlése.')
        delta = final_score-baseline_score
        lines.append('A **teljes ötéves modellcsomag** leggyengébb feltételezett forgatókönyvének pontszáma '
                     f'{_decimal(baseline_score)}-ról {_decimal(final_score)}-ra változott '
                     f'(**+{_decimal(delta)} modell-indexpont**). Ez nem egyetlen projekt hatása és nem valódi ötödik éves előrejelzés.')
    lines.extend(['','## Mit ellenőrizzetek a döntés előtt?',
                  'A jogosultságot, a ténylegesen elérhető pénzt, a projektkártyák friss adatait, '
                  'a függőségeket és a csapat jóváhagyását. A kártyán szereplő százalékok **nem** SmartCity-indexpontok. '
                  'A projektfelsorolás nem jelent kötelező kattintási sorrendet.',
                  '', '**Játékbeli művelet: nincs. `GAME_ACTION_GATE=STOP`.**'])
    return {'schema':SCHEMA, 'mode':mode, 'current_period':start,
            'first_year_new_ids':[p['id'] for p in new],
            'first_year_preselected_ids':[p['id'] for p in existing],
            'years':financial_rows, 'model_delta':round(final_score-baseline_score,9),
            'global_optimum_claimed':False,'live_financing_approved':False,
            'gameplay_gate':'STOP', 'markdown':'\n'.join(lines)+'\n'}
