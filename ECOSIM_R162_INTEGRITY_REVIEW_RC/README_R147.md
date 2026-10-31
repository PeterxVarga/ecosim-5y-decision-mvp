# EcoSim R147 — forráskódhoz kötött faktorhatások és valódi kalibrációs adatkapu

## Cél

Az R146 meglévő ötéves motorjának **helyben történő továbbfejlesztése**, nem új optimalizáló. A csomag kizárólag offline, Python standard-library feldolgozást végez. A felhasználónak most nincs futtatási vagy ellenőrzési feladata.

## Működő új részek

1. `tools/effect_replay_r147.py`: a projektkártyák ismert direkt relatív hatásainak egységes, központi visszajátszása. A hatásokat ugyanarra a tényezőre *előbb összeszorozza*, és csak ezután alkalmazza a kód szerint indokolt faktor-korlátot. Az új `Munkanélküliség → Munkanélküli arány` leképezés nem egy önkényes pontszám, hanem az EcoSim `unemployment` hatásának direkt alága. A `Kisvállalkozások száma` és `Középvállalkozások száma` továbbra is ismeretlen indirekt hatások.
2. Négy közvetlenül azonosított faktor-korlát: vállalkozóbarátság max. 100 megjelenített pont, településfejlettség 2,1–95,6, közlekedési minőség max. 200, tömegközlekedők aránya max. 80. A már telített tényezők mögötti látens érték nem állapítható meg a kijelzett pontszámból; a rendszer ezt külön jelzi.
3. A meglévő `r142_proxy_reference.py`, `strategy_5y.py`, `city_bridge.py` és `robust_r146.py` ugyanazt az R147 faktorvisszajátszót használja. Nincs párhuzamos stratégiakereső. Az adó-, kapacitás- és egyéb működési döntések **nem** lettek „valódi EcoSim-képletként” beállítva.
4. `tools/paired_calibration_r147.py`: korábban engedélyezett, már meglévő ugyanazon évre vonatkozó PLAN–PLAN bemeneteken összehasonlíthatja a direkt faktor-predikciót a ténylegesen kijelzett terv-faktorokkal. **Nem hajt végre próbadöntést**, és a felhasználói kontrollnyilatkozatot sem tekinti független bizonyítéknak. p0 tény vs p1 terv nem elfogadható modellvalidációként.
5. `tools/verify_source_r147.py`: a hash-rögzített forrásszakaszok opcionális offline ellenőrzése. A csomag nem terjeszti újra a 18 letöltött JS-fájlt. A 840-as chunk SHA256-ja és a 9 hivatkozott bytespan a felhasználótól kapott R140B eredetiből ellenőrzött.
6. A korábbi közös offline belépési pont (`tools/run_r146_offline.py`) R147 kimeneteket készít, plusz a páros kalibráció eredményét, valós adat hiányában `forecast_accuracy_validated: false` státusszal.

## Offline használat – nem kell most futtatni

Az archívumban már megvan az `results/R147_100K_ILLUSTRATIVE_*` mintasorozat, a `results/R147_EFFECT_COVERAGE.json` és a `results/R147_QUALIFICATION.json`.

Ha később a tulajdonos futtatni szeretné a meglévő demót:

```bash
python3 -I -B tools/run_r146_offline.py --budget-per-year 100000 --out-prefix results/R147_OWN_DEMO
```

A `100000` **nem igazolt EcoSim-projektkeret**. A tesztforduló korábbi projektállapota **nem** igazolt induló állapot az éles fordulóhoz.

Külön, már rendelkezésre álló és megfelelően engedélyezett PLAN-párból:

```bash
python3 -I -B tools/paired_calibration_r147.py --input inputs/paired_plan.template.json --out results/R147_PAIRED_CALIBRATION.json
```

A minta nulla párt tartalmaz, ezért nem generál hamis „0% hiba” eredményt. A kötelező mezők a `inputs/paired_plan.schema_notes.md` fájlban szerepelnek.

A teljes offline regresszió egyetlen összesített belépése: `./qualify_once.sh`.

## Mit NEM jelent

- A megjelenített faktorokból visszaszámolt 52,48 pontos index nem a teljes döntés-/piac-/versenytárs-modell validációja.
- A projektkártyák direkt faktorhatásai nem fedik le a vállalati számdinamikát, az adók és intézmények évi visszacsatolását, hitelkorlátokat, projektkésleltetést és migrációt.
- A szintetikus 100k ECU/év minta kimenete **nem** garantált ötödik évi index, nem globális optimum, és nem végrehajtási ajánlás.
- A helyi ellenőrzések száma a kódhelyességről és konzisztenciáról szól; a valódi játékbeli előrejelzési pontosság továbbra is UNKNOWN.

**Állapot:** képes feltételes, forráskódhoz kötött ötéves projektdöntéseket kiértékelni; `gameplay_gate=STOP`, amíg a teljes modell, valós piaci adatok és hitelesített összehasonlítás hiányzik.
