# EcoSim R194 – egységes csapatos futtatás (R162 + R189–R193)

**Állapot:** `PASS_88_LOCAL_TESTS`, `PINNED_NATIVE_R162_E2E_NOT_EXECUTED`, `GAME_ACTION_GATE=STOP`.

## Milyen problémát javít?

A GitHub PR #2 R193-futtatója a `bounded_shadow_r189` modult ugyanabból a Python `tools/` könyvtárból importálta, de a tényleges GitHub-on a fájl a `team-handoff/r189-r190/tools/` könyvtárban volt. A régi helyi tesztcsomag másolatot tartalmazott, ami elfedte a hibát. **A GitHub könyvtárszerkezetében a korábbi `python run_r191_shadow.py --help` `ModuleNotFoundError` hibával megállt.**

Az R194 **nem másolja** a keresőmodult: a tényleges testvér-könyvtárból importálja, ellenőrzi a forrás helyét és a korábbi R189 Git blob SHA-ját (`5042d7da2d762bd393ab0e6848acee46e2bdbae8`). Hiányzó, symlinkelt, megváltozott vagy más útvonalról importált forrásnál `HOLD`.

## Egy parancs – történeti, teljes futtatási ellenőrzés

A privát `PeterxVarga/ecosim-5y-decision-mvp` fejlesztési ágának gyökerében:

```bash
bash team-handoff/r191-live-admission/run_team.sh historical
```

A program a *meglévő* `run_native_r162_r193.sh` ellenőrzőre delegál. Tiszta detached Git-worktree-t hoz létre az eredeti R162 PIN-en, ellenőrzi a forrást, teszteket futtat, megpróbálja a teljes R162→R189→R191/R192→R193 történeti modellt, ellenőrzi az R160 kimenetet és a magyar jelentést, majd R162 történeti kvalifikációt futtat. A naplók egy egyedi `/tmp/ecosim-r193-native-*` mappában maradnak. **Nem garantáljuk, hogy ez a teljes natív E2E már sikeres volt**: a natív pinned checkout ebben a ChatGPT-környezetben nem elérhető.

## Egy parancs – éles adatokon, de csak olvasva

Az éles adatok R156 adatcsomagja és 35 kártya aktuális megfigyelése esetén:

```bash
bash team-handoff/r191-live-admission/run_team.sh current \
  --state /path/current-state.json \
  --r156-bundle /path/r156-immutable-bundle \
  --year1-finance /path/observed-year1-finance.json \
  --current-card-catalog /path/observed-current-35-cards.json \
  --annual-budget 100000 --cap 4
```

A `100000` és `4` csupán **szintaktikai példák**, nem ismert éles értékek. A parancs mindkét explicit argumentumot a state-ben deklarált értékekkel veti össze; az aktuális 35 kártyának meg kell egyeznie a kereső historikus adatbázisával. Ha eltér, blokkol. Az elsőéves pénzügyeket külön ellenőrzi; a későbbi négy évre a keret hipotetikus. Nem vezérel böngészőt és semmilyen EcoSim műveletet nem hajt végre. Az eredmény JSON és magyar jelentés lokális, egyszer írható fájlokban keletkezik.

## Mi van integrálva?

- **R162:** egyetlen eredeti Python stratégiakereső, R157 robusztus érzékenység, R160 független audit – rögzített forrás; nem átalakított másolat.
- **R189/R190:** meglévő R189 körülhatárolt évátrendező, változatlan R189 Git blob, választott projekthalmaz megőrzése; nem globális optimum.
- **R191:** éles és történeti bemenetek elkülönítése, eredeti R162 szigorú JSON-beolvasó, elsőéves pénzügyi bemeneti kapu.
- **R192:** mind a 35 aktuális projektkártya egyezésének ellenőrzése a forrásprojektkatalógussal.
- **R193:** magyar öt éves döntési javaslat, `human_explanation_hu.markdown` és terminálkimenet, explicit bizonytalanságokkal.
- **R194:** helyes modul-összekötés, forrásazonosítás, historikus/éles egyparancsos csapatindítás, valódi layoutot tesztelő bootstrap és negatív tesztek.

## Futtatott bizonyíték

- 73 meglévő, R191/R192/R193 helyi szerződés-/regressziós teszt: PASS.
- 9 új R194 integritási és tényleges Python-indulási teszt: PASS.
- 6 új R194 launcher-teszt: PASS.
- **Összesen: 88/88 helyi teszt PASS**, és `bash -n` PASS.
- Az új tesztek a GitHubdal azonos mappaszerkezetből **másolat nélkül** indítják a Python CLI-t. A hiányzó vagy módosított R189 forrást blokkolják.
- **Nem történt meg** a teljes pinned R162/R160 natív E2E; az eredeti 35-kártyás aktuális kör, valós pénzügyi és szerveroldali döntés továbbra nem minősített.

## Merge feltételek

1. Futtasd a `run_team.sh historical` parancsot olyan csapatgépén, ahol az eredeti privát Git-repó teljes commit-története elérhető; a létrejött naplókból igazold `R193_NATIVE_E2E=PASS_OFFLINE_HISTORICAL_ONLY`.
2. Ha a historikus E2E PASS, függetlenül ellenőrizd a tényleges magyar döntési javaslatot, a R160 auditledgerét és a forrás PIN-t.
3. Merge csak opcionális, alapértelmezetten offline/felügyeleti funkcióként. Éles döntést kizárólag aktuális, bizonyítottan ugyanazon körű adatok alapján, emberi jóváhagyással.

**Játékbeli változtatás nincs. `GAME_ACTION_GATE=STOP`.**
