# R152 — forráshoz kötött döntési dosszié

**Játékbeli döntés: STOP; nem hitelesített, ötéves nyerő stratégia.**

- Bemenet: `HISTORICAL_TEST_ROUND_NOT_CURRENT`
- Megjelenített index: **52.48**
- Faktorokból számolt index: **52.483733**
- Tényleges EcoSim-mérés / előrejelzési pontosság: **nem igazolt**

## Fennmaradó fő adatkapuk

- `project_cap`: MISSING_OR_UNVERIFIED
- `baseline_index_factors`: OPERATOR_SUPPLIED_NOT_SERVER_VERIFIED
- `current_index_weights`: OPERATOR_SUPPLIED_NOT_SERVER_VERIFIED
- `active_projects`: OPERATOR_SUPPLIED_NOT_SERVER_VERIFIED
- `current_selections`: OPERATOR_SUPPLIED_NOT_SERVER_VERIFIED
- `prior_project1`: OPERATOR_SUPPLIED_NOT_SERVER_VERIFIED
- `confirmed_spendable_cash`: MISSING_OR_UNVERIFIED
- `committed_costs`: MISSING_OR_UNVERIFIED
- `loan_rates`: MISSING_OR_UNVERIFIED
- `official_preview`: MISSING_OR_UNVERIFIED

# EcoSim R149 — belső, offline döntési MVP

**Kizárólag döntéselőkészítés. Játékbeli művelet: 0. Véglegesítés: STOP.**

Mód: `HISTORICAL_ILLUSTRATION`; kezdőév: **1**. Aktuális állapothoz kapcsolható: **nem**.

## Forrásintegritás

- `run_config`: `R152_DECISION_RUN_CONFIG.json` — SHA-256 `e2169e86f2d831ad541921bcf9765f139d860f911c7815b8beef5c223a2e3521`
- `read_only_capture`: `NORMALIZED_CAPTURE.json` — SHA-256 `e075cb7453b239915f78bce323db729d469b0529d31d24ecf7561a1ccd76c169`
- `historical_passive_summary`: `historical_passive_summary_20261030.json` — SHA-256 `7f044cb25e8770fa768d1435d9403ec82e89196284c604765317a9f6839914b0`
- `tax_scenarios`: `tax_counterfactual_r153.synthetic.json` — SHA-256 `998b038c9f715da70ba2a76c2822c39d712863baa23467ff57309e84da722495`
- `tax_revenue_scenarios`: `tax_revenue_r154.synthetic.json` — SHA-256 `237d25e68c6d20f77290e902bc59fc4821acc266cdab175e4b85dd4008efc011`
- `operating_scenarios`: `operating_r155.synthetic.json` — SHA-256 `84394c0cd3986c9886115f22d4da420fa9bd2109efd7b1214dcba8909e28a477`
- `policy_tracks`: `policy_tracks.synthetic.example.json` — SHA-256 `6d068513340c60a2e23ddcd2615812b978dca5c156c8a82b8d016cf6cd9e93b2`
- `league_readonly`: `league_observations.template.json` — SHA-256 `d5f91f52108f682e4ce5ebffb086b486c19d491e96a5458b7ce40ef763fdfefa`
- `paired_plan_observations`: `paired_plan.template.json` — SHA-256 `44c73ebc284596ab3b16d562e2ff930fd8318cf7bdd0230201c613afab10bf13`
- `frozen_forecast_fact_audit`: `forecast_audit.template.json` — SHA-256 `a813e3758912b6885a3181789da432d3407931088190461e329325795295d96e`

## Ötéves, feltételezett projektkeretek

| Keret | Éves összegek (ECU) | Jelleg |
|---|---|---|
| narrow_50k | 50,000, 50,000, 50,000, 50,000, 50,000 | EXPLICIT_HYPOTHESIS |
| middle_100k | 100,000, 100,000, 100,000, 100,000, 100,000 | EXPLICIT_HYPOTHESIS |
| wide_150k | 150,000, 150,000, 150,000, 150,000, 150,000 | EXPLICIT_HYPOTHESIS |

## Többkeretes jelöltösszehasonlítás

A *fedettség* az itt megadott, feltételezett keretekre vonatkozik, **nem valószínűség** és nem valódi pénzügyi jóváhagyás.

| Jelölt | Évenként indított projektek | Keretfedettség | 5. évi részleges proxy Δ | Stresszelt részleges proxy Δ (minimum) |
|---|---|---|---:|---:|
| `P-68be1bc65a7b` | 26,27,28; 8,9,17; 5,21; 4; 6,20 | 3/3 | +0.8120 | +0.4038 |
| `P-aa61047c535c` | 26,27,28; 8,9,17; 4; 5,21; 6,20 | 3/3 | +0.8120 | +0.4038 |
| `P-efee28562fae` | 8,27,28; 9,21; 5,17,26; 4; 6,20 | 3/3 | +0.8120 | +0.4038 |
| `P-7af7b223be3a` | 26,27,28; 8,9,17; 5,21; 4; 20,25 | 3/3 | +0.8061 | +0.4009 |
| `P-61ce97c60a3b` | 8,27,28; 9,21; 5,17,26; 4; 20,25 | 3/3 | +0.8061 | +0.4009 |
| `P-5751d0c900aa` | 13,17,20,27; 8,21,26,28; 3,4,5,9; 1,6,16; 7,10 | 2/3 | +1.3444 | +0.6649 |
| `P-027954559c67` | 13,17,20,27; 8,21,26,28; 1,4,5,9; 6,16,25; 3,7 | 2/3 | +1.3267 | +0.6564 |
| `P-f8621e760ebd` | 13,17,20,27; 8,21,26,28; 3,4,5,9; 1,6,16; 7,25 | 2/3 | +1.3267 | +0.6564 |

## R150 – mintán belüli Pareto-szűrés és szcenáriós veszteségek

A Pareto-szűrés **csak a heurisztika által talált tervekre és részleges, nem kalibrált mutatókra** vonatkozik; nem bizonyít valódi dominanciát vagy globális optimumot.

| Feltételezett keret | Mintában beleférő tervek | Mintabeli nem dominált jelöltek |
|---|---:|---|
| narrow_50k | 5 | P-68be1bc65a7b, P-aa61047c535c, P-efee28562fae |
| middle_100k | 10 | P-68be1bc65a7b, P-aa61047c535c, P-efee28562fae, P-5751d0c900aa, P-027954559c67, P-f8621e760ebd, P-ec40afec9ed4, P-38dcd54304ff |
| wide_150k | 15 | P-68be1bc65a7b, P-aa61047c535c, P-efee28562fae, P-5751d0c900aa, P-027954559c67, P-f8621e760ebd, P-ec40afec9ed4, P-38dcd54304ff, P-9ffda18c4ae7, P-f7360b35019c, P-a2f6bade1bf2, P-e333150e7648 |

Az „elszalasztott részleges indexnyereség” csak **a megvizsgált, feltételes tervekhez képest** értelmezhető, nem játékbeli regret vagy győzelmi esély.

## Működési döntési szcenáriók

- `test_no_new_policy` (SYNTHETIC_TEST_ONLY): első ismert részleges proxy Δ: +1.3267; **nem kalibrált EcoSim-válasz**.
- `synthetic_training_capacity` (SYNTHETIC_TEST_ONLY): első ismert részleges proxy Δ: +1.3254; **nem kalibrált EcoSim-válasz**.
- `synthetic_unknown_tax` (SYNTHETIC_TEST_ONLY): első ismert részleges proxy Δ: +1.3267; **nem kalibrált EcoSim-válasz**.

## R153 – forrásképlettel számított adó-/díjérzékenység

Forrásosztály: `SYNTHETIC_TEST_ONLY`. A kliens `Re(e,t)` képletének SHA-256 hivatkozása: `cd4c23b0e57a2019ca3fe69151e19fb9c314e94e8cf5e0920f258e370eb3abf0`.
A vállalkozóbarátság közvetlen részindex-hozzájárulása **feltételesen** számolható. Nem számoljuk a megváltozó adóbevételeket, vállalatmozgást és az évenkénti gazdasági visszacsatolást.

| Adó/díj forgatókönyv | Kandidátus | Ötödik évi közvetlen adóhatás (részleges indexpont) | Projektproxy + adóhatás |
|---|---|---:|---:|
| unchanged_synthetic | `P-9ffda18c4ae7` | +0.00000 | +1.61361 |
| unchanged_synthetic | `P-f7360b35019c` | +0.00000 | +1.61361 |
| unchanged_synthetic | `P-678df6e638a7` | +0.00000 | +1.61361 |
| business_tax_reduced_synthetic | `P-9ffda18c4ae7` | +0.00510 | +1.61871 |
| business_tax_reduced_synthetic | `P-f7360b35019c` | +0.00510 | +1.61871 |
| business_tax_reduced_synthetic | `P-678df6e638a7` | +0.00510 | +1.61871 |
| business_tax_increased_synthetic | `P-9ffda18c4ae7` | -0.00510 | +1.60851 |
| business_tax_increased_synthetic | `P-f7360b35019c` | -0.00510 | +1.60851 |
| business_tax_increased_synthetic | `P-678df6e638a7` | -0.00510 | +1.60851 |
**Nincs igazolt adóbevétel, hitelkeret vagy játékbeli nyerő eredmény.**

## R155 – hat szolgáltatási bevétel, intézményi bér és anyag részkiadás

**KIZÁRÓLAG szintetikus/feltételes működési pályák; nem teljes városmérleg vagy engedélyezett költségvetés.**
| Forgatókönyv | Ötéves díjbevétel Δ ECU | Ötéves lefedett intézményi kiadás Δ ECU | Részleges nettó Δ ECU |
|---|---:|---:|---:|
| `unchanged_synthetic` | +0 | +0 | +0 |
| `business_tax_reduced_synthetic` | -102,235 | +16,800 | -119,035 |
| `business_tax_increased_synthetic` | +100,814 | +28,815 | +71,999 |
A 3 tengelyes Pareto-front kizárólag a megtalált jelöltek részleges, változatlan külső állapotú összehasonlítása; a vállalati és lakossági dinamika ismeretlen.
Mintabeli összevetés: **45**, nem dominált: **21**.

## Azonos periódusú PLAN-párok (nem éves ténykalibráció)

Megadott pár: **0**; saját nyilatkozatú kontrollokkal: **0**; valódi ötéves predikciós pontosság: **ismeretlen**.

## R151 – előre rögzített becslés és későbbi tény egyeztetése

Tényleges, operátor által hivatalosnak jelölt PLAN–FACT pár: **0**; teljes indexre szóló modelljóslattal párosítható: **0**.
Operátor által megadott, teljes modellre számolt MAE: **ismeretlen**; függetlenül hitelesített pontosság: **ismeretlen**.
A tesztfordulós p0 tény és p1 terv **nem** egy megfigyelt PLAN–FACT mérési pár.

## Liga pillanatkép

Állapot: `UNKNOWN_NO_OFFICIAL_LEAGUE_SNAPSHOT`. Teljes ligaadat és szervezői helyezési szabály hiányában továbbjutás nem állapítható meg.

## Történeti, passzív egyeztetés

- `R94_P0_UI_FACT` (FACT p0): megjelenített 51.96; visszaszámolt 51.9655; ez **nem** megfigyelt állapotátmenet.
- `R94_P1_UI_PLAN` (PLAN p1): megjelenített 52.48; visszaszámolt 52.4837; ez **nem** megfigyelt állapotátmenet.

## A következő legkisebb biztonságos bizonyítékok

- **PROJECT_CAP_AND_STATE**: Official market cap plus previous project1 and already-selected/currently-running IDs. (A 4/year spoken statement does not establish the effective current allowance)
- **FINANCE_PROOF**: Official available cash, obligations, lending terms and support settlement by period. (Net operating result and hypothetical envelopes are not spendable money)
- **PAIRED_PREVIEW**: Only an approved, preverified reversible same-period comparison or official preview export. (Without matched before/after model residuals predictive accuracy remains unknown)
- **POLICY_CAUSAL_RESPONSES**: Official rules, passive observations and independently matched safe measurement pairs. (Tax, fees and institutions are still user assumptions, not calibrated controls)
- **COMPETITION_DYNAMICS**: Read-only league snapshots after each finalized period, with contemporaneous ranks and decisions. (Competitor moves and migration can alter realized terminal rankings)
- **COMPETITION_PERMISSION**: Current written competition rules or organizer confirmation. (The competition may regulate third-party automation/optimization)

## Végső kapu

**STOP.** A projektlimit, a hitel/likviditás, a teljes várospolitikai hatásfüggvények és a terv–tény kalibráció nem igazoltak teljes körűen. A kereső heurisztikus, a stresszértékek nem megbízhatósági intervallumok. Az EcoSimben semmilyen műveletet nem hajtunk végre.
