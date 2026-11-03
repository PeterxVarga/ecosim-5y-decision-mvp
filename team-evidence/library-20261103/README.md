# EcoSim – megosztott forrásbizonyítékok (Library-import, 2026-11-03)

Ez a könyvtár a felhasználó kifejezett kérésére a **nyilvános** EcoSim repóba átemelt, korábban a ChatGPT-fájltárban tárolt, forrásfüggő versenyadatokat és ellenőrző jelentéseket tartalmazza. A csapattagok szabadon olvashatják, de **nem** minősülnek mentett szerveres döntésnek vagy validált ötéves előrejelzésnek.

## Selejtező / I. piac – történeti források

- `ecosim_selejtezo_I_normalizalt_forras.json`: normalizált forrás az első periódus megfigyeléseiből.
- `ecosim_R227_forraslefedettseg.json`: nagy terjedelmű Excel–UI forráskeresztwalk, a 374 számozott sor és 23 megfigyelt mező lefedettségi vizsgálatával.
- `ecosim_R227_dontesi_crosswalk.csv`: kivonat a 23 megfigyelt döntési mezőről, UNKNOWN tartományokkal.
- `ecosim_selejtezo_I_29_faktor_R156_ellenorzesre.csv`: 29 megfigyelt tényező és összesített index felülvizsgálatra.
- `ecosim_selejtezo_I_kornyezet_forrasellenorzes_20261102.json`: forrás- és környezetvizsgálat.
- `ecosim_R227_bizonyitek_es_kovetkezo_lepes.md`: a keresztwalk korlátai.
- `ecosim_r238_ellenorzes_20261103.json` és `.md`: a R238 csomag utólagos integritási és lefedettségi ellenőrzése.
- `EcoSim_R239_hianyzo_adatok_gyujtesi_manifest.json` és `EcoSim_R239_hianyzo_adatok_gyujtesi_atadas.md`: hiányzó adatforrások és feladatlista.
- `EcoSim_P1_hianyzo_informaciok_2026-11-03.md`: célzott P1 feltétel- és információhiány-audit.

## Régebbi tesztforduló / Z. piac

A `test-Z/` könyvtárban a `finance.csv`, `income.csv`, `source_index.csv` és a korábbi XLSX-ből normalizált `ecosim_r213_historical_excel_normalized_private.json` **2026-10-30-as tesztfordulós**, nem a selejtező I. piacára vonatkozó adatok. Tilos automatikusan az I. piaci P1 döntések kiindulásaként használni őket.

A `EcoSim_R195_5_eves_tervek_osszehasonlitasa.md` két feltételes historikus ötéves projektszcenáriót foglal össze; nem mentett, éles stratégia.\n\n## Adateredet és korlátok

- Az állományok a ChatGPT Library-ben tárolt, korábban a felhasználó által rendelkezésre bocsátott exportok **szöveges beolvasásából** kerültek a repóba. A CSV-kből a beolvasó által hozzáadott technikai fejlécet kihagytuk.
- Az importáláskor a JSON-ok szintaktikáját ellenőriztük, és ismert hitelesítőadat-mintákra célzott ellenőrzést végeztünk. Ez **nem** teljes biztonsági vagy forráshitelesítési audit; az eredeti állományok byte-szintű azonosságát nem bizonyítja.
- A Fedora gép helyi R238 eredeti ZIP-je, a R257/R258 teljes élő UI-próbanyugták, illetve az eredeti XLSX-fájlok **nem** szerepelnek ebben az importban. Ezek azonosítását, byte-egyezését és hiteles forrását nem szabad feltételezni. A ZIP és XLSX nem helyettesíthető ezzel a szöveges importtal.
- A bejelentkezett játék aktuális szerveres állapotát sem ezek az állományok, sem egy sikeres történeti offline teszt nem bizonyítja.
- `GAME_ACTION_GATE=STOP`: semmilyen start, cancel, Save vagy Next Period felhatalmazás nem következik az adatok publikálásából.
- A repository jelenleg **PUBLIC**; az itt közzétett csapat-/játékadatokat bárki láthatja. Ne töltsünk fel jelszót, tokent, session cookie-t vagy nem publikálható harmadik félhez tartozó személyes adatot.

A megosztott adatok az auditálhatóságot és a csapatos folytatást támogatják; a hiányzó tényleges éves FACT-adatok és a szerveroldali szabályok továbbra is UNKNOWN.
