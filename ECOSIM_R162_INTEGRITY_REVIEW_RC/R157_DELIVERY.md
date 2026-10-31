# R157 átadási nyugta

**Státusz: KÉSZ – offline, nem kalibrált, játékbeli STOP.**

Az R156 meglévő offline EcoSim döntési MVP-jében javítottuk a korábbi R146 stressz számítás eltérő projekt-policy korlátozási sorrendjét, és az **egyetlen meglévő R143→R156 beam optimalizáló** külön, hipotetikus scenario-min rangsorolását, bemeneti és kimeneti integrációját hoztuk létre.

- R156 kvalifikáció: **68/68 PASS újrafuttatva**.
- R157 új kvalifikáció: **66/66 PASS**.
- Valóban lefuttatott történeti R94 döntési összehasonlítás: 3 feltételezett keret × nominális és stresszelt keresés; 20 megjelenített (teljes mintában több) jelölt.
- A stresszelt rangsor új első ötös jelölthalmazai a három keretben: **2/4/5**, kizárólag történeti és hipotetikus összevetés.
- Teljes előrejelzési pontosság **nem igazolt**. Aktuális market/team **nincs**. EcoSim írás **0**.

Részletek: `README_R157.md`, `results/R157_QUALIFICATION.json`, `results/R157_HISTORICAL_ROBUST_DEMO/`.
