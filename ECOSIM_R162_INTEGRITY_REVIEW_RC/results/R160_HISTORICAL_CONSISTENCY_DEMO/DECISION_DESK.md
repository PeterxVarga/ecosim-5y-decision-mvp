# EcoSim R149 — belső, offline döntési MVP

**Kizárólag döntéselőkészítés. Játékbeli művelet: 0. Véglegesítés: STOP.**

Mód: `HISTORICAL_ILLUSTRATION`; kezdőév: **1**. Aktuális állapothoz kapcsolható: **nem**.

## Forrásintegritás

- `run_config`: `mvp_run.r157_robust_historical.json` — SHA-256 `43690da62fa1ab7f17d54a478a548fdace7b9a870495323c3d1a7a4befacf386`
- `state`: `official_state.template.json` — SHA-256 `1e9f82948d614de5fcbba68a955d1c079daaf8c9004c2101ec489fefa1a4f196`
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
| `P-780aee4394fa` | 5,26,27; 4,28; 9,21; 8,17; 6,20 | 3/3 | +0.8120 | +0.4038 |
| `P-d440783cfc88` | 5,26,27; 4,28; 9,21; 8,17; 20,25 | 3/3 | +0.8061 | +0.4009 |
| `P-aa61047c535c` | 26,27,28; 8,9,17; 4; 5,21; 6,20 | 3/3 | +0.8120 | +0.4038 |
| `P-efee28562fae` | 8,27,28; 9,21; 5,17,26; 4; 6,20 | 3/3 | +0.8120 | +0.4038 |
| `P-68be1bc65a7b` | 26,27,28; 8,9,17; 5,21; 4; 6,20 | 3/3 | +0.8120 | +0.4038 |
| `P-61ce97c60a3b` | 8,27,28; 9,21; 5,17,26; 4; 20,25 | 3/3 | +0.8061 | +0.4009 |
| `P-7af7b223be3a` | 26,27,28; 8,9,17; 5,21; 4; 20,25 | 3/3 | +0.8061 | +0.4009 |
| `P-5751d0c900aa` | 13,17,20,27; 8,21,26,28; 3,4,5,9; 1,6,16; 7,10 | 2/3 | +1.3444 | +0.6649 |

## R157 – mintabeli legrosszabb forgatókönyv szerinti elsőéves lépések

Négy, **szintetikus** hatásintenzitás és fennmaradási pálya. A számítás csak az ismert faktorokra és a telítettségi bizonytalanságra vonatkozik. Nem előrejelzés, nem valódi regret és nem győzelmi valószínűség.
| Feltételezett keret | Elsőéves projektek | Legjobb mintabeli forgatókönyv-minimum Δ | Mintabeli különbség |
|---|---|---:|---:|
| narrow_50k | 5,26,27 | +0.27651 | 0.00000 |
| narrow_50k | 26,27,28 | +0.27197 | 0.00455 |
| narrow_50k | 8,27,28 | +0.27147 | 0.00504 |
| middle_100k | 13,17,20,27 | +0.43934 | 0.00000 |
| middle_100k | 13,26,27 | +0.43376 | 0.00557 |
| middle_100k | 9,13,20,27 | +0.43365 | 0.00569 |
| wide_150k | 8,13,16,27 | +0.53008 | 0.00000 |
| wide_150k | 4,13,21,27 | +0.52769 | 0.00239 |
| wide_150k | 4,8,13,27 | +0.52763 | 0.00244 |

## R160 – független korlát- és költségellenőrzés

**26 mintaterv újraszámítva**, hard eltérés: **0**,
feltételes szerverelfogadás: **26**.
A kártya- és kijelzett előfeltétel-szabályok következetessége **nem** szerverjogosultság. A nem modellezett hatások száma nem negatív indexhatás; valódi pontszám-dominancia **ISMERETLEN**.

## R150 – mintán belüli Pareto-szűrés és szcenáriós veszteségek

A Pareto-szűrés **csak a heurisztika által talált tervekre és részleges, nem kalibrált mutatókra** vonatkozik; nem bizonyít valódi dominanciát vagy globális optimumot.

| Feltételezett keret | Mintában beleférő tervek | Mintabeli nem dominált jelöltek |
|---|---:|---|
| narrow_50k | 7 | P-780aee4394fa, P-aa61047c535c, P-efee28562fae, P-68be1bc65a7b |
| middle_100k | 16 | P-780aee4394fa, P-aa61047c535c, P-efee28562fae, P-68be1bc65a7b, P-5751d0c900aa, P-7987f0e1a89d, P-b97fc8b30724, P-027954559c67, P-ec40afec9ed4, P-f8621e760ebd, P-3e06cde819a6, P-38dcd54304ff |
| wide_150k | 26 | P-780aee4394fa, P-aa61047c535c, P-efee28562fae, P-68be1bc65a7b, P-5751d0c900aa, P-7987f0e1a89d, P-b97fc8b30724, P-027954559c67, P-ec40afec9ed4, P-f8621e760ebd, P-3e06cde819a6, P-38dcd54304ff |

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
| unchanged_synthetic | `P-9f220f6f225b` | +0.00000 | +1.61361 |
| unchanged_synthetic | `P-e10fc0617d3e` | +0.00000 | +1.61361 |
| unchanged_synthetic | `P-f7360b35019c` | +0.00000 | +1.61361 |
| business_tax_reduced_synthetic | `P-9f220f6f225b` | +0.00510 | +1.61871 |
| business_tax_reduced_synthetic | `P-e10fc0617d3e` | +0.00510 | +1.61871 |
| business_tax_reduced_synthetic | `P-f7360b35019c` | +0.00510 | +1.61871 |
| business_tax_increased_synthetic | `P-9f220f6f225b` | -0.00510 | +1.60851 |
| business_tax_increased_synthetic | `P-e10fc0617d3e` | -0.00510 | +1.60851 |
| business_tax_increased_synthetic | `P-f7360b35019c` | -0.00510 | +1.60851 |
**Nincs igazolt adóbevétel, hitelkeret vagy játékbeli nyerő eredmény.**

## R155 – hat szolgáltatási bevétel, intézményi bér és anyag részkiadás

**KIZÁRÓLAG szintetikus/feltételes működési pályák; nem teljes városmérleg vagy engedélyezett költségvetés.**
| Forgatókönyv | Ötéves díjbevétel Δ ECU | Ötéves lefedett intézményi kiadás Δ ECU | Részleges nettó Δ ECU |
|---|---:|---:|---:|
| `unchanged_synthetic` | +0 | +0 | +0 |
| `business_tax_reduced_synthetic` | -102,235 | +16,800 | -119,035 |
| `business_tax_increased_synthetic` | +100,814 | +28,815 | +71,999 |
A 3 tengelyes Pareto-front kizárólag a megtalált jelöltek részleges, változatlan külső állapotú összehasonlítása; a vállalati és lakossági dinamika ismeretlen.
Mintabeli összevetés: **78**, nem dominált: **24**.

## R159 – komponensenként korrigált éves pénzügyi időzítés

**Az ötéves adó- és működési különbség nem egyenlő az azonnal elérhető pénzzel.** Nincs igazolt nyitó készpénz, támogatási időpont, hitelkeret vagy szerveroldali elszámolás. Az alábbi nulla nyitó pénzes kísérlet NEM tényleges finanszírozási hiány.

| Projekt | Adó/díj/intézmény pálya | 5 év részleges nettó projektkártya után | Azonnali elszámolás: legnagyobb hipotetikus kumulált hiány | Pozitív pénzáram +1 év: legnagyobb hipotetikus kumulált hiány |
|---|---|---:|---:|---:|
| `P-027954559c67` | `business_tax_increased_synthetic` | +514,299 | 0 | 105,263 |
| `P-38dcd54304ff` | `business_tax_increased_synthetic` | +546,699 | 0 | 105,263 |
| `P-3e06cde819a6` | `business_tax_increased_synthetic` | +550,899 | 0 | 103,763 |
| `P-4dd0b056939c` | `business_tax_increased_synthetic` | +275,899 | 0 | 147,763 |
| `P-5751d0c900aa` | `business_tax_increased_synthetic` | +504,199 | 0 | 105,263 |
| `P-61ce97c60a3b` | `business_tax_increased_synthetic` | +747,499 | 0 | 54,763 |
| `P-678df6e638a7` | `business_tax_increased_synthetic` | +280,399 | 0 | 147,763 |
| `P-68be1bc65a7b` | `business_tax_increased_synthetic` | +754,499 | 0 | 53,763 |
| `P-7128a45f8542` | `business_tax_increased_synthetic` | +275,899 | 0 | 147,763 |
| `P-71895ba56dd7` | `business_tax_increased_synthetic` | +275,899 | 0 | 147,763 |
| `P-780aee4394fa` | `business_tax_increased_synthetic` | +753,999 | 0 | 55,763 |
| `P-7987f0e1a89d` | `business_tax_increased_synthetic` | +517,899 | 0 | 103,763 |

| Pálya | Feltételes indexszel vizsgált jelöltek | A három hipotetikus szempont szerint nem dominált jelöltek |
|---|---:|---:|
| `business_tax_increased_synthetic` | 26 | 8 |
| `business_tax_reduced_synthetic` | 26 | 8 |
| `unchanged_synthetic` | 26 | 8 |
**Döntési kapu: STOP.** Sem a pozitív részbevétel, sem az éves szintetikus cash-nyomás nem jogosít projektindításra.

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

- **CURRENT_PROVENANCE**: Authorized official export or unchanged summary screenshot with market, team, period, timestamp. (Without current team/period provenance the baseline may be stale)
- **PROJECT_CAP_AND_STATE**: Official market cap plus previous project1 and already-selected/currently-running IDs. (A 4/year spoken statement does not establish the effective current allowance)
- **BASELINE_AND_WEIGHTS**: Same-period factor table and market weight configuration. (The proxy score cannot be transferred from historical R94 without them)
- **FINANCE_PROOF**: Official available cash, obligations, lending terms and support settlement by period. (Net operating result and hypothetical envelopes are not spendable money)
- **PAIRED_PREVIEW**: Only an approved, preverified reversible same-period comparison or official preview export. (Without matched before/after model residuals predictive accuracy remains unknown)
- **POLICY_CAUSAL_RESPONSES**: Official rules, passive observations and independently matched safe measurement pairs. (Tax, fees and institutions are still user assumptions, not calibrated controls)
- **COMPETITION_DYNAMICS**: Read-only league snapshots after each finalized period, with contemporaneous ranks and decisions. (Competitor moves and migration can alter realized terminal rankings)
- **COMPETITION_PERMISSION**: Current written competition rules or organizer confirmation. (The competition may regulate third-party automation/optimization)

## Végső kapu

**STOP.** A projektlimit, a hitel/likviditás, a teljes várospolitikai hatásfüggvények és a terv–tény kalibráció nem igazoltak teljes körűen. A kereső heurisztikus, a stresszértékek nem megbízhatósági intervallumok. Az EcoSimben semmilyen műveletet nem hajtunk végre.
