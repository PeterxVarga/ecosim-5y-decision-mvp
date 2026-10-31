# EcoSim R151 — Evidence-gated forecast calibration (R150 extension)

## Cél és határ

A létező `tools/strategy_5y.py` az **egyetlen** ötéves optimalizáló. R151 nem épít második modellt és nem módosít EcoSim-adatot. A korábbi döntési MVP kiegészül egy időben rögzített **PLAN → későbbi, végleges FACT** visszamérési sávval.

**Aktuális állapot:** a korábbi R94 p0 tény / p1 terv nem valós éves visszamérés. A csomagban **0 valódi, véglegesített PLAN–FACT pár**, ezért az előrejelzési pontosság továbbra is `null`, a játékbeli döntési kapu `STOP`.

## Új részek

- `tools/forecast_audit_r151.py`: szigorú, időzónaérzékeny, előre rögzített modellbecslés–későbbi tény összevetés. Kiszűri a rossz évhez/csapathoz/fordulóhoz tartozó adatot, a tervként megadott tényt, a nem végleges tényt, az indexkeverést és az időbeli adatszivárgást.
- `tools/decision_desk_r149.py`: a korábbi R150 döntési eredményhez kapcsolja a visszamérési státuszt, a külön bizonyíték-SHA256-ot, de **nem** engedélyez játékbeli műveletet.
- `tools/decision_view_r149.py`: a statikus, JavaScript-mentes HTML új R151 táblát mutat.
- `inputs/forecast_audit.template.json`: a ténylegesen hiányzó bizonyítékoknak üres sémája. A felhasználói adatok **operátori állítások**, automatikusan nem hitelesített szerveradatok.
- `tools/qualify_r151.py`: 47 új negatív/pozitív és integrációs ellenőrzés; a 330 korábbi ellenőrzés bizonyítéka megőrzött, nem futtatott újra.

## Visszamérés helyes szemantikája

Egy mérési párhoz a **ugyanazon csapat/piac/forduló/periódus** korábban megfigyelt `PLAN` értéke és **annak a periódusnak a lezárását követően** megjelenő `FACT` szükséges. `after_fact.finalized_period_confirmed_by_operator=true` kötelező, de ez operátori nyilatkozat, nem független hitelesítés. Az eredeti befagyasztott modellbecslés `created_at` dátumának legkésőbb a `before_plan.captured_at` időpontjára kell esnie.

Minden méréspárhoz kötelező mind a 29 kijelzett faktor, a 6 indexsúly, az előző terv és a későbbi tény kijelzett indexe; a faktorokból visszaszámolt indexnek egyeznie kell a kijelzettel (±0,04, a kerekítés miatt). `FULL_CITY_INDEX` esetén csak egy valódi, a tény előtt rögzített, teljes városindexre vonatkozó becsléssel mérhető hiba; `PARTIAL_PROJECT_PROXY` **nem** használható teljes indexhibaként.

A mért MAE csak **az operátor által hivatalosnak nyilatkozott, összekapcsolt adatpárok** matematikai hibája. Az önmagában nem függetlenül hitelesített modellpontosság és nem globális győzelmi valószínűség. Az adatok hitelességét, a tényleges véglegesítést és a modell üzemi érvényességét nem állapíthatja meg az offline Python-kód.

## Használat később, csak ha megfelelő export már rendelkezésre áll

```bash
python3 -I -B tools/forecast_audit_r151.py \
  --input inputs/forecast_audit.template.json \
  --out results/my_forecast_audit.json
```

A R150 futtató továbbra is működik (`run_mvp.sh`). A JSON bemenetben opcionálisan `forecast_audit_path` hivatkozhat az auditadatokra. Az aktuális éles játékállapotot a `inputs/capture_current.template.json`/`inputs/official_state.template.json` fogadja, és a korábban hiányzó `market/team` konfigurációt **nem** pótolja a történeti mintával. A csomag nem használ böngészőt, hálózatot, Codexet és nem tesz EcoSim-írási műveletet.

## Fennmaradó külső P0 információk

- Valódi, időbélyegzett `market.maxProjectPerTurn`, aktív/kiválasztott projektek és aktuális hat indexsúly.
- Hiteles aktuális pénzügy, kötelezettségek, hitelek, kamatok, támogatási feltételek.
- A teljes adó-, díj-, intézmény- és migrációs átmeneti egyenletek/hatások.
- Előzetesen rögzített, **teljes városindexre** vonatkozó modelljóslat + a később lezárult forduló tényszámai.

**Végső játékbeli kapu: STOP.** Nem született validált ötéves nyerő stratégia.
