# R143 V2.1 — pontosítások, hibajavítások és döntési kapuk

**Dátum:** 2026-10-31. **Műveleti státusz:** nincs Codex CLI indítás, nincs játékbeli művelet, nincs bejelentkezés. Ez az R143 V2 javítása, nem új RE-projekt.

## Amit már tényszerűen tudunk

- 18/18 azonosított EcoSim JS-csomag, 2026-10-30-i tesztkártya-katalógus 35 projekttel, 6 korábban futóval, SmartCity kézikönyv, R142A statikus bizonyítékok.
- A SmartCity index a hat, különböző súlyú részindexből számolható. A 2026-10-30/31-i összefoglaló `p1 terv = 52,48` a megjelenített részindexekkel visszaellenőrizhető. Ez történeti **alapállapot**, nem egy jelöltkombináció megfigyelése.
- Az R142A klienskód szerint `A = market.maxProjectPerTurn + (előző periódus project1 numerikus állapota == 1 ? 1 : 0)`, majd a kiválasztott új projektek darabszáma korlátoz. A konkrét `market.maxProjectPerTurn` NEM került ki a statikus kódból.
- A 2026-10-29-i megnyitó videó 21:08-nál 4 projekt/évet, 21:57-nél 12%-os kamatot említ. **Erős szóbeli szabálytájékoztatás**, de nem bizonyítja a csapat éles numerikus market mezőit, illetve a konkrét hitelfajtát.
- A p1 tervben régebben látott **865 588 ECU** pénzügyi eredmény NEM igazoltan szabadon elkölthető költségvetés; a partneri támogatás külön bevételi ág és nem előfinanszírozás.
- A projektkártyák feltételmechanizmusa nyers aktuális döntési állapotot néz, ezért az azonos évben történő együttindítás **lehetséges kliensoldali forgatókönyv**, nem általánosan tiltott és nem is minden esetben bizonyítottan engedélyezett.
- A megnyitó szerint az 5. virtuális év végi **ligabeli helyezés** fontos; a középdöntő top-2 és esetleges „közeli harmadik” szabály még végleges szervezői megerősítésre szorul.

## A ténylegesen javított hibák

1. **Dupla projektlimit-számlálás:** `len(already_selected)+len(plan_starts)` helyett `len(set(already_selected_new) | set(plan_starts))`, és a korábbi már futó projektek nem számítanak automatikusan új helynek. A korábbi `project1==1` bónusz csak hivatalos csapatállapot esetén alkalmazható.
2. **Azonos évi projektek hibás kizárása:** az UI-ban kijelzett `Bicikliútfejlesztés — Fut` és `Vasútfejlesztés — Fut` függőségeket a modell kategorizálja: már aktív / azonos évi, sorrendfüggő lehetőség / nem teljesített / ismeretlen címke. A megjelenített feltétel nem a belső JS-nyelvi kifejezés hiteles másolata.
3. **Félreérthető pénzügyi PASS:** a korábbi `PASS_CONDITIONAL` helyett `WITHIN_USER_INPUT_ENVELOPE_NOT_SERVER_APPROVAL`; csak a bevitt, forrással igazolt pénzkerethez viszonyít, nem ismeri a szerverhitelplafont vagy támogatások tényleges rendelkezésre állását.
4. **Tesztadat örökítése az éles modellbe:** a mintaterv most külön, expliciten hordozza a 6 futó kártyát mint történeti 2026-10-30-i baseline-t; `verified_current_market:false`. A valódi új versenyfutás induló állapotának felvitele nélkül a naptár nem éles terv.
5. **Hamis ligahelyezés/kiesési becslés:** a ranglista „teljes” mezőt, liga- és időbélyegazonosítást, tény/terv típust igényel. Részleges adat esetén csak mintabeli helyezést ad. Holtverseny esetén két külön másodikpont-mértéket és „tie” jelzőt szolgáltat; NEM állít hivatalos kvalifikációs formulát.
6. **11 mező egyetlen blokkoló listában:** a készültségi állapot már `passive_identification`, `cap_calibration`, `finance_validation`, `optional_approved_candidate_validation` csoportokat ad. A játékállapotot változtató előnézet nem szükséges a modellcsontváz pontosításához; külön tulajdonosi döntési kapu.
7. **Automatikus Codex-futtatás:** a futtató alapértelmezésben már nem indít semmit; csak kifejezett későbbi engedélyezéssel aktiválható.

## Még nyitott — konkrét, minimális adat és bizonyítás

| Kérdés | Ma ismert | Minimálisan még kell | Kapu |
|---|---|---|---|
| Projektlimit | 4/év videóban; `maxProjectPerTurn` + esetleges `project1` bónusz kódban | aktuális hivatalos `market.maxProjectPerTurn` + előző periódus `project1==1` + már kiválasztott új projektek | valódi darabszám- és jogosultsági kapu |
| Költhető pénz | projektkártya ECU, p1 tervezett egyenleg, klienshitel-mechanika | aktuális pénzügyi inputok, kötelezettségek, hiteltípus/ráta/plafon és támogatási szabály | nem pusztán egyetlen „budget” szám |
| Projektfüggőségek | 2 kijelzett előfeltétel a 35 kártyán | az éles aktuális állapot, az együttindítás/sorrend szerveroldali elfogadása, ha releváns | feltételes GO, nem automatikus kizárás |
| Indexmodell | indexsúlyok, több faktorfüggvény, R142 proxy | konkrét aktuális súlyok és hatáskulcsok, nemlineáris részek, hiteles megfigyelések | a pontbecslések nem bizonyítottak |
| Terv kontra tény | a videó különbséget és liga-migrációt említ | adott év terv/tény, piaci peer inputok/tényleges hatások a forduló után | ex ante bizonytalanság megőrzése |
| Liga és továbbjutás | ötödik év vége és top2 (előzetesen) | aktuális ligatagok, azonos periódus indexe, végleges holtverseny/középdöntő szabály | relatív célfüggvény / rangsor csak bizonyítékkal |
| Külső CLI optimalizáló megengedettsége | forrásokból itt nem igazolt | írásos szabályzat vagy szervezői megerősítés | éles versenyeszköz-használat ellenőrzése |

## Következő értékes lépés, **futtatás nélkül**

- Használjuk az ismert adatokat a sémák és az invariánsok tisztítására; ne készítsünk szimulátort a hiányzó piacdinamika helyére.
- A *passzív* hivatalos állapotexport a projektlimit, valódi pénzügyi mezők és a jelenlegi liga megkülönböztetésére szolgál; az előnézet-kísérlet külön engedélyhez kötött.
- Nem állítható, hogy a 4/év = 20 garantáltan indítható, mert a bónusz, feltételek és a jövőbeli állapotok ezt módosíthatják.
- A projektköltség-naptár öt évre becsüli a **kártya szerinti** költségeket; nem hiteles pénzügyi kimutatás, adósság-visszafizetés, migráció vagy SmartCity-index előrejelzés.

**Végeredmény:** a V2.1 pontosabb és kevésbé félrevezető döntéselőkészítő; a megengedett játékbeli projektindítás és a nyerő ötéves terv továbbra sem bizonyított. `GO` nem adható.
