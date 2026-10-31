# R150 — Outcome-first delivery

**Cél:** az R149 meglévő offline Decision Desk MVP-jét ténylegesen használhatóbbá tenni az öt éven át zajló *megfigyelés → döntési alternatívák → éves újratervezés* ciklushoz.

**Research → Reuse → Build:** forrás az R149 saját kódja és a korábbi 18 JS/kézikönyv bizonyítéka; a R150 nem épít új EcoSim-adatkinyerőt vagy második optimalizálót. A legerősebb most beépíthető eredmény a kereső által már megtalált jelöltek hatékonyabb összevetése és a megfigyelések szemantikailag szigorú összehasonlítása.

**Beépítés:** `tools/decision_quality_r150.py`, `tools/compare_runs_r150.py`; meglévő `decision_desk_r149.py` és `decision_view_r149.py` bővült. **Kritikus validáció:** 1 összevont regresszió, külön falszifikációs negatív esetekkel.

**Proof Before Done:** `results/R150_QUALIFICATION.json`, `results/R150_MVP_DEMO/`, `R150_RELEASE_MANIFEST.json`, `SHA256SUMS`.

**Határ:** a viszonyítási front nem bizonyít globális optimumot, a pénzügyi keresési feltételezések nem igazolt keretek, a tervezett kontra tényleges városváltozás nincs igazolva; `STOP`.

## Végső offline eredmények

- Konszolidált ellenőrzés: **330/330 PASS** (291 megőrzött, 39 új ellenőrzés).
- Mintában vizsgált feltételes ötéves tervek: **15**; elérhetők a ``results/R150_MVP_DEMO/`` mappában.
- Feltételezett költségkeretek száma: **3**; mindegyikhez külön Pareto- és relatív veszteség-lista.
- Hivatalos éles állapot, teljes éves városváltozás, validált játékpontszám: **UNKNOWN**.
- Felhasználói Codex/terminál futtatás: **0 szükséges**; EcoSim-módosítás: **0**.
