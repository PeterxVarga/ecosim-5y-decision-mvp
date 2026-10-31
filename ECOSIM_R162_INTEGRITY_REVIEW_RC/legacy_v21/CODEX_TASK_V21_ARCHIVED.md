# R143 V2.1 — későbbi Codex-feladat, JELENLEG NEM FUTTATANDÓ

A jelenlegi megbízás tisztázás és helyesbítés, nem modellfuttatás. A V2.1 kódbeli és dokumentációs javításait már elvégeztük; tilos az R139–R142A újrakutatása, és nem szabad még egy párhuzamos szimulátort készíteni. A következő Codex-futtatás csak új, ténylegesen ellenőrizhető hivatalos inputok vagy a felhasználó kifejezett későbbi kérése esetén indokolt.

Olvasd előbb: `R143_V21_CHANGES_AND_GATES.md`, `R143_EVIDENCE_DECISION_MATRIX.json`, `evidence/R142A_*`, `evidence/R143_RULES_EVIDENCE.json`, `results/R143_READINESS.json`.

Ha később történik modellezés, kötelező korlátok:
1. Semmilyen élő game-művelet, bejelentkezés, mentés, projektindítás, hitelfelvétel vagy API-hívás. A projektkártya renderje is visszaállíthat érvénytelen kiválasztást. Felületi A/B kizárólag külön jóváhagyással, előre ellenőrzött visszaállítással.
2. A négy projekt/év és a 12%-os kamat hivatalos SZÓBELI információ, nem éles konfiguráció. A `market.maxProjectPerTurn` és a korábbi `project1==1` kombinációját az aktuális hivatalos setup alapján kell igazolni.
3. A p1 nettó eredmény (865 588 ECU) nem „szabad pénz”, az automatikus rövid hitel képlete nem hitelplafon, a támogatás címkéje nem előre folyósított készpénz.
4. Az azonos évben választható előfeltétel elvileg teljesíthető a kliens nyers állapotában, de a szerver/játék sorrendje nem igazolt. Nem kizárni automatikusan az ilyen projekteket, hanem feltételesnek jelölni.
5. A 2026-10-30-i kártya-export és a 6 futó projekt csak TESZTFORDULÓS induló állapot. Éles év1 állapota/market/ligamezők teljesen külön bemenetet igényelnek.
6. Egy részleges liga-score-lista nem hiteles ligabeli helyezés; a holtverseny és a „másodikhoz való relatív közelség” pontos kvalifikációs formulája nyitott.
7. A felületi p1 terv **becslés**, versenytársi migrációval változhat a p1 tény. Nem lehet determinisztikus 5. évre jóslást állítani.
8. Reuse az eredeti `tools/r142_proxy_reference.py` és `tools/portfolio_5y.py`; csak bizonyított kód- vagy adatillesztési hiba esetén módosíts. A kiadás egyetlen igazi célja a kalibrálható döntési kapu, nem újabb RE-eredmények felhalmozása.

Bármely későbbi `R143_STATUS.json` csak `final_gameplay_decision: STOP`, `true_game_model_validated: false` értékeket kaphat, amíg ténylegesen nincs hiteles döntési validáció.
