# R147 fejlesztési átadás — 2026-10-31

Az R146 ZIP-re épülő egyetlen **nagy, helyi fejlesztési chunk**. Nem hívott Codex CLI-t, nem vezérelt böngészőt, nem kérte a felhasználó terminálját, és nem tett játékbeli írásokat.

## Kézzelfogható változások

- Egységesített, csoportosított projekt-hatásaggregálás a teljes ötéves keresőn, faktorhídon és stresszteszteken.
- Direkt projekt-hatás megfeleltetés: `Munkanélküliség` ≡ `unemployment` megjelenített rátájának relatív szorzója; ez nem tévesztendő össze a foglalkoztatottsággal.
- A statikus klienskódra alapozott négy küszöb és telítési bizonytalanság.
- A két vállalatlétszám-hatás továbbra sincs tetszőleges indexváltozássá alakítva.
- 9 darab bytehely és SHA256 rögzítve, a felhasználótól kapott eredeti 840 chunk ellenőrzésével.
- Szabályos, passzív páros tervmegfigyelés-adapter, szigorú proveniencia- és ugyanazon-periodus-követelménnyel.
- Meglévő R146 egyetlen offline belépés R147 kimenetekre frissítve, az előző API és heurisztika megőrzése mellett.

## Kvalifikáció

Az aktuális `results/R147_QUALIFICATION.json` tartalmazza a tesztjegyzéket. Az R146-ból örökölt 131 ellenőrzés és az R147 új vizsgálatai ugyanabban az egyetlen ellenőrzési folyamatban futnak. A tesztek **nem** jelentik valós EcoSim-pontosság igazolását.

Eredményfájlok:

- `results/R147_100K_ILLUSTRATIVE_JOINT.json` és `.md`: három kifejezetten szintetikus működési forgatókönyv és feltételes projektterv.
- `results/R147_100K_ILLUSTRATIVE_PASSIVE.json`: a korábbról rendelkezésre álló p0 tény/p1 terv indexösszevetés; nem kauzális átmenet.
- `results/R147_100K_ILLUSTRATIVE_PAIRED_CALIBRATION.json`: nulla valódi, jóváhagyott összehasonlító pár → a modellpontosság ismeretlen.
- `results/R147_100K_ILLUSTRATIVE_STATUS.json`: explicit STOP és `actual_five_year_score_predictive_accuracy=null`.
- `results/R147_EFFECT_COVERAGE.json`: faktorhatások feldolgozási lefedettsége.
- `results/R147_SOURCE_VERIFICATION.json`: forráskódrészletek ellenőrzése (a forráskód nincs a ZIP-ben).

## Nyitott tényleges külső bizonyítékok

1. Hiteles aktuális piac-/csapatkonfiguráció, projektlimit, hitelek és vállalt költségek.
2. Adó-, díj-, intézményi döntések valódi válaszfüggvényei és verziózott döntéstartományai.
3. Projekteknek az indirekt vállalati létszámokra és foglalkoztatásra gyakorolt hatásmechanizmusa, esetleges késleltetés.
4. Már engedélyezett, ugyanazon periódusú PLAN–PLAN méréspár a helyi kliensfaktor-modell egyeztetéséhez; később terv–tény hosszanti adatok az éves előrejelzési hiba méréséhez.
5. Más csapatok és migráció hatása, az éles ligaadatok és versenyszabályok.

**Most nincs felhasználói teendő.** A rendszer további kutatás és megfigyelés nélkül nem állíthat igazolt nyerő stratégiát.
