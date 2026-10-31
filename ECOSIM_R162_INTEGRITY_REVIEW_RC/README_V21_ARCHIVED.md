# EcoSim R143 V2.1 — bizonyítékpontosítás és hibajavítás

Ez a **meglévő R143 V2** módosított kiadása, **nem** R144 vagy párhuzamos optimalizáló. A feladat: feltárt problémák és következtetési hibák kijavítása, a még szükséges információk pontos definiálása. **Most ne indíts Codexet és ne módosíts EcoSim-állapotot.**

Olvasd el először:

- `R143_V21_CHANGES_AND_GATES.md`: tételes korrekciók, falszifikáció és prioritások;
- `R143_EVIDENCE_DECISION_MATRIX.json`: képletről, projektlimitről, finanszírozásról, előnézetről és rangsorról elválasztott bizonyítékok;
- `tools/portfolio_5y.py`: javított ötéves **kártyaköltség-naptár**, NEM index- vagy hitelmodell;
- `tools/readiness.py`: hiányok csoportosítása, holtverseny/hiányos liga kezelése;
- `examples/illustrative_plan.json`: 2026-10-30-i tesztfordulós induló hat projekt, nem éles állapot;
- `inputs/*.template.json`: üres, forrásmegjelölést kérő hivatalos bemeneti sémák.

Az eredeti R142A kutatási jelentések változatlanul maradtak az `evidence/` mappában. A meglévő R142 projekt-proxy ugyancsak változatlan és NEM alakul át feltételezett éles szimulátorrá.

A `results/` mappában tárolt költségnaptár és hiánylista kizárólag a csomag hipotetikus tesztadatainak **helyi számításai**. Sem Codex-futtatás, sem EcoSim-módosítás, sem felhasználói fiókhoz való hozzáférés nem történt a V2.1 javítás során. A játékmenet GO státusza **STOP**.

A korábbi futtató szándékosan **nem indít semmit alapértelmezésben**. Egy későbbi, kifejezetten kért Codex-futtatáshoz az `R143_ENABLE_CODEX=YES` változó szükséges. Ez a ZIP most nem igényel futtatást.
