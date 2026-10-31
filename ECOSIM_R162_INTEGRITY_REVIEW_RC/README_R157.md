# EcoSim R157 — Forráskonzisztens stresszelt ötéves döntési MVP

**Cél:** az R156 / R155 / R150 / R143 meglévő egyetlen keresőjének nagy, offline javítása; nincs Codex, felhasználói terminál, bejelentkezett EcoSim, hálózati hívás vagy játékbeli írás.

## Research → Falsify → Reuse → Build

A korábbi `tools/robust_r146.py` által használt stresszvizsgálat a projektek hatásait külön korlátozta, majd a hipotetikus policy-szorzókat már a korlátozott faktorra tette rá. Ez téves kimenetet adhatott a forrásban meglévő felső/alsó faktorkorlátok mellett, és ellentmondott a későbbi R148 közös számító magnak. Az R157 **kijavítja**, hogy a `combined_factor_replay()` a projekt- és működési szorzókat előbb összeszorozza és **utána egyetlen korlátot** alkalmazzon. A rejtett, korlát előtti faktorállapot miatt azonosíthatatlan eredményt külön feltételes intervallumként kezeli; az intervallum csak a telítettségre vonatkozik, nem a teljes városgazdaságra.

További talált hiány: a korábbi kereső a gyenge projekthatás és csökkenő fennmaradás vizsgálatát többnyire **utólag** végezte el. Az R157 `strategy_5y.search(objective='scenario_min')` útvonala **ugyanabban a beam keresőben** már a shortlist és a beam-állapotok megtartásakor is a leggyengébb leképezett stresszértéket használja. Ez heurisztikus, nem bizonyított globális optimum.

## Új, működő funkciók

- `tools/robust_decision_r157.py`: négy kifejezetten hipotetikus modell-érzékenységi pálya. Hatásintenzitás 100% / 50%; évente fennmaradás 100% / 85%. Az utolsó év részleges faktorindexe, a forrásalapú telítettségi feltételes intervallum és a be nem kötött indirekt hatások száma külön rekord.
- `tools/strategy_5y.py`: opcionális, scenario-min-célfüggvényű **ugyanazon** bounded beam heurisztika. A nominális keresés alapértelmezetten változatlanul elérhető. A valódi játékkimenetre nem számol felső/alsó korlátot és nem társít profil-valószínűséget.
- `tools/robust_r146.py`: a régi policy-szenzitivitási ág is a központi egyszeri korlátozást használja. A korlát miatti lehetséges intervallumot külön kimeneti mezőben publikálja.
- `tools/decision_desk_r149.py`: `r157_include_scenario_min_search=true` mellett mindkét keresési célfüggvényt ugyanazon év, állapot és hipotetikus keret mellett futtatja; az eredményeket tervazonosítók alapján deduplikálja. A 15%-os további pénzügyi szűkülés tisztán hipotetikus érzékenység. **Elsőéves stratégia-regret csak kereten belül és csak a mintabeli stratégiák között** értelmezett.
- `tools/decision_view_r149.py`: a már meglévő statikus offline HTML-ben új táblák láthatók a stressz-minimumról és az elsőéves lépések mintabeli eltéréséről. Nem tartalmaz külső JavaScriptet vagy hálózati kérést.
- `tools/qualify_r157.py`: 68 korábbi R156 ellenőrzés újbóli, konszolidált futtatása, plusz 66 új, többek között korlát-sorrendi, rejtett telítettségi, hibás bemeneti és valós R152→R155→R157 munkafolyamat-ellenőrzés. Eredmény: `results/R157_QUALIFICATION.json`.

## Ténylegesen lefuttatott, történeti demonstráció

- `results/R157_HISTORICAL_ROBUST_DEMO/DECISION_DESK.html` — statikus, böngészővel offline olvasható jelentés.
- `results/R157_HISTORICAL_ROBUST_DEMO/DECISION_DESK.json` — teljes gépi jelentés, kimeneti források és bizonytalanságok.
- `results/R157_HISTORICAL_ROBUST_DEMO/DECISION_DESK.md` — szöveges változat.
- A három feltételezett keret **50 000 / 100 000 / 150 000 ECU/év**, a korábbi R94 **tesztfordulós** p1 faktorokkal és 35 történeti projektkártyával. Nem a jelenlegi éles költségvetés.
- Az első öt keresési terv összehasonlításánál a scenario-min ág 50k/100k/150k keretben rendre **2/4/5** olyan egyedi tervet adott, amely a nominális ág első öt találatában nem volt benne. Ez keresési diverzitás; nem valódi eredményjavulás.
- **Egyetlen éles játékbeli döntés sem történt.** Játékbeli kapu: `STOP`.

## Egyetlen offline végső ellenőrzés, amikor majd szeretnéd

```bash
./qualify_once.sh
sha256sum -c SHA256SUMS
```

A demo ismételt előállítása (külön, nem szükséges most):

```bash
./run_r157_offline.sh
```

## Határok és következő kritikus függőség

A négy stresszprofil **nem** bizonyított valóságos lehetséges tartomány, nem eloszlás, nem valószínűség, nem játékteljesítmény-korlát. A mögöttes kereső továbbra is bounded beam heurisztika, és az intézményi, vállalati, migrációs, szerveroldali finanszírozási és versenytársdinamika nincs teljesen modellezve. Nem igazolható a „legrosszabb ötéves valódi kimenet”. Az ismeretlen indirekt hatások nem lettek zérusnak minősítve.

A megfigyelt R94 p0 tény és p1 terv **nem** éves tény–tény visszamérés. Hivatalos aktuális `market/team`, igazolt pénzügyi keret és fagyasztott előrejelzés–későbbi tény mérési pár továbbra sincs. A következő legnagyobb hozadék a jelenlegi, jogosult és megfigyelt EcoSim-állapot átvétele, nem további mesterséges optimalizáló-réteg.

A korábbi R143–R156 kiadási fájlokat és modellkódot megtartottuk; az eredeti EcoSim-alkalmazást és a történeti ZIP-eket nem módosítottuk.
