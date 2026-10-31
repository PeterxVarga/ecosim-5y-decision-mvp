# EcoSim R152 — Evidence-ready Offline Decision MVP

## Végcél és a tényleges új képesség

Az R151 meglévő **egyetlen** ötéves keresőjéhez (`tools/strategy_5y.py`) épült egy **ténylegesen futó bemeneti integráció**, nem különálló új optimalizáló:

1. `tools/observation_bundle_r152.py` — egy helyi, csak olvasott adatokból összerakott faktor-CSV + projektállapot-CSV + opcionális market/team JSON + *szigorúan történeti* R94 pénzügyi CSV csomagot ellenőriz, normalizál, SHA-256-szal nyugtáz.
2. `tools/run_evidence_pipeline_r152.py` — a normalizált bemenetet a korábbi R151 `decision_desk_r149.make_report()` függvényébe vezeti. Ebből ugyanaz a 5Y kereső, több feltételezett pénzügyi keret, Pareto-összevetés, bizonyítékhiányok, Markdown és **offline, szkriptmentes HTML** készül.
3. `tools/qualify_r152.py` — 44 új célzott ellenőrzés, beleértve hibás, félrevezető és hiányos inputok elutasítását. A korábbi 377 PASS a **megőrzött** R151-ellenőrzés; az R152-ban nem ismételtük meg. A teljes heurisztikus keresővel egyetlen történeti végponttól végpontig példa futott.

## A meglévő, ellenőrzött történeti minta

A `examples/R152_HISTORICAL_R94_READONLY_PACKET/` az október 30-i **tesztfordulós** eredeti adatokat szétbontva tartalmazza. A kimenet a `results/R152_HISTORICAL_END_TO_END/` mappában:

- 29 faktor + összesített kijelzett index: **52,48**; kliensoldali rekonstrukció: **52,483733** (kerekítési egyezés).
- 35 projektállapot-sor: **6 korábban futó**, **0 új kiválasztás**.
- A teljes, konkrét történeti `finance_R94_test_snapshot.csv`: **113 pénzügyi sor**, nyolc elszámolási egyezés, p1 nettó **865 588 ECU**. Ez **nem** igazoltan költhető keret.
- Az örökölt ötéves kereső **15 feltételes jelöltet** hasonlított össze 50k/100k/150k ECU-s, **hipotetikus** éves korlátokkal.
- Eredmények: `DECISION_DESK.html`, `R152_DECISION_REPORT.md`, `EVIDENCE_RECEIPT.json`, `R152_MISSING_EVIDENCE.json`, `DECISION_DESK.json`. A játékbeli döntési kapu `STOP`.

Ez **nem** az éles forduló aktuális állapota, és **nem** a játék által igazolt előrejelzés.

## Mi kell majd egy valódi, megengedetten megfigyelt aktuális bemenethez?

Az `examples/R152_CURRENT_READONLY_TEMPLATE/` kizárólag kitöltetlen sablon, nem futtatható és **nem** tartalmaz a régi tesztadatból másolt aktuális faktorértékeket. A saját, jogszerűen megfigyelt állapotról készíts az ottani pontos oszlopnevekkel:

- `factors...csv`: `metric,value` — mind a 29 faktor és az `Okosváros index` együttesen, azonos periódus `PLAN` oszlopból.
- `projects...csv`: `project_id,previous_running,selected_new` — mind a 35 projekthez `true`/`false`; a korábban futó és az újonnan kiválasztott státusz nem felcserélhető. Ha az állapot nem bizonyítható, **nem** kell kitölteni helyette találgatással.
- `market_team_params...json`: a kézikönyvi/historikus default helyett **az adott market hivatalos** projektlimitje, indexsúlyai; opcionális további adatok. A forrásnak és a csapatnak meg kell egyeznie.
- `manifest.json`: market, team, round, period, időzónás ISO 8601 megfigyelési idő, forrásbizonyíték-azonosító, `CURRENT_READONLY` és `PLAN`.

**Ne** exportálj tokent, session cookie-t, jelszót vagy HAR-t. A program semmilyen hálózati kapcsolatot nem létesít, EcoSimbe nem ír. A forrásfájlok integritása önmagában **nem igazolja, hogy valóban hivatalosak**. A market konfiguráció, a hitel/belépési szabály és az ellenfélmozgás továbbra is hiányozhat. Az R151 mérési adatút továbbra is csak lezárt, utólag megfigyelt FACT esetén számol valós terv–tény eltérést.

## Futtatás csak később, ha akarsz

A csomagban a mintafuttatás **már elkészült**, nincs szükség most végrehajtásra.

```bash
cd ECOSIM_R152_EVIDENCE_READY_MVP
python3 -I -B tools/run_evidence_pipeline_r152.py \
  --bundle examples/R152_HISTORICAL_R94_READONLY_PACKET/manifest.json \
  --decision-config inputs/mvp_run.illustrative.json \
  --out-dir results/my_historical_demo
```

Valódi aktuális adatnál ugyanígy, de egy erre kitöltött `CURRENT_READONLY` bemenettel és a `inputs/mvp_run.current.template.json` **saját, tisztázott** másolatával (csak a hipotetikus budgetek változtatása megengedett, az effektív market cap felülírása nem). Hiányos inputnál a rendszer **keresés nélkül** jelzi a szükséges további bizonyítékokat. Ha egy operátor által kitöltött forrás jelenleg formailag teljes is, az **nem** független szerverhitelesítés és **nem** játékbeli jóváhagyás.

## Korlátok / falszifikáció

Az R152 **nem** módosítja az R151 keretrendszer számítási korlátait. Az adók/díjak/intézmények teljes oksági függvényei, költségvetési korlátok, szerveroldali végrehajtás, vállalatmozgás és 5. év ténybeli eredménye ismeretlen. Egyetlen mintabeli Pareto-dominancia sem bizonyít valós optimumot, és a tesztforduló jellemzői nem vihetők át észrevétlenül az éles fordulókra. **Játékbeli döntés: STOP.**
