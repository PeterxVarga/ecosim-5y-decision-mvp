# EcoSim P2 — kilenc ismétlődő egyszeri művelet ROI-felülvizsgálata

**Forrás:** a 2026. november 5-i Brave–Codex alnézeti audit feltöltött beszámolója (`Pasted text(20261105-122441).txt`).
**Játék:** X-Challenge 2026 Selejtező · Jutalom a nap végén · I. piac · P2/5.
**Csak olvasható felülvizsgálat:** nem történt EcoSim-mezőmódosítás, projektindítás, hitelfelvétel vagy mentés.

A forrás szerint a P2 PLAN **60,52** SmartCity-index, **868 143 ECU** tervezett tartalék; mind a 35 projekt státusza és pénzügyi kártyája elérhető (10 futó, 25 nem futó). A P2 mentett állapota **UNKNOWN**.

## Kilenc megismételt egyszeri művelet

A kilenc érték **P1 FACT-ként és P2 PLAN-ként is megjelenik**. Ez bizonyíték az ismétlődésre, **nem bizonyíték arra, hogy P2-ben mind hibás**. Az intézménynyitások akár indokoltak is lehetnek.

| Művelet | P2 terv | Lehetséges 0-ás változat | Mostani kihasználtság | 0-ás változat proxy* |
|---|---:|---:|---:|---:|
| Dízelbusz eladás | -8 | +0 | 106,5% | 92,7% |
| Irodai dolgozók elbocsátása | -50 | +0 | 108,8% | 92,8% |
| Járművezető-felvétel | +50 | +0 | 66,5% | 77,4% |
| Szerelőfelvétel | +10 | +0 | 61,5% | 79,6% |
| Középiskola megnyitása | +1 | +0 | — | — |
| Sportintézmény megnyitása | +1 | +0 | — | — |
| Művelődési intézmény megnyitása | +1 | +0 | — | — |
| Orvosi rendelő megnyitása | +1 | +0 | — | — |
| Szociális otthon megnyitása | +1 | +0 | — | — |

* A kihasználtsági proxy **DERIVED, nem szimulációs eredmény**: azonos munkaterhelést és azonos egységkapacitást feltételezünk, majd a jelenlegi kihasználtságot megszorozzuk a P2 jelenlegi és a 0-ás változat állományának hányadosával. A tényleges EcoSim-index és ECU-hatás UNKNOWN. A 0-ás változat nem végrehajtási utasítás.

## Kritikus megfigyelések

- **−8 dízelbusz**: 54 busz és 106,46%-os tervezett járműkihasználtság; 0 eladás esetén a **62 buszos** darabszám és ~**92,7% proxy** adódna. Ugyanakkor a P2 terv 26 739 ECU járműeladási bevételt tartalmaz; a pontos marginális pénzhatás UNKNOWN.
- **−50 irodai dolgozó**: 291 fő és 108,75% kihasználtság; 0 elbocsátás esetén **341 fő** és ~**92,8% proxy**.
- **+50 járművezető**: 355 fő és 66,48% kihasználtság; 0 új felvételnél **305 fő** és ~**77,4% proxy**.
- **+10 szerelő**: 44 fő és 61,5% kihasználtság; 0 új felvételnél **34 fő** és ~**79,6% proxy**.
- **Öt intézménynyitás:** középiskola, sportintézmény, művelődési intézmény, orvosi rendelő, szociális otthon. Mindegyik +1-ről +1-re ismétlődik, de az egyedi P2 index- és ECU-hozam ismeretlen. **Nem javasolt automatikusan nullázni.**

## ROI Challenger

1. **Mind a 9 érték automatikus visszaállítása nullára:** elvetve; az intézménybővítés pontszámot javíthat.
2. **Projektcsomag azonnali kiválasztása a 35 kártya alapján:** most korai, mivel a jelenlegi kapacitáskonfliktusok és projekt–pénz elszámolás bizonytalansága torzíthatja a döntést.
3. **A négy közlekedési és személyzeti művelet kontrollált, egyváltozós P2-tervérzékenységi vizsgálata; utána az intézménynyitások:** választott következő ROI, mert a közvetlen döntési akadályt célozza.

## Következő ellenőrzési protokoll — NINCS VÉGREHAJTVA

**Jogosultsági kapu:** az eddigi tulajdonosi engedély **csak a nézetek megnyitására szólt**. A P2 mezők ideiglenes módosításához és visszaállításához külön explicit jóváhagyás kell. A jelenleg ismert UI nem igazolja a mentés nélküli visszaállíthatóságot; ennek tisztázásáig nincs kísérlet.

1. Pontosan rögzíteni az aktuális 9 döntési értéket, 60,52 pontszámot, 868 143 ECU tervtartalékot és az összes projektstátuszt. Elkülöníteni a mentett/mentetlen állapotot.
2. Ha a játék nem ment automatikusan és a pontos visszaállítás ellenőrizhető, egyenként tesztelni: **−8→0 busz**, **−50→0 iroda**, **+50→0 vezető**, **+10→0 szerelő**. Minden változatnál összes index, hat kategória, 29 tényező, tartalék, kihasználtság és költség rögzítése.
3. Minden próbát azonnal visszaállítani az eredeti értékre és teljesen ellenőrizni. Ha a visszaállítás hibás vagy a mentési szabály bizonytalan, STOP.
4. Az öt intézménynyitást külön vizsgálni. A valós marginális eredmények alapján, a négyprojekt/év korlát mellett optimalizálni a projektportfóliót.

**Tilos:** Start/Stop projekt, Mentés, Next Period, hitel, push, merge, deployment külön engedély nélkül.

## Bizonyítás és státusz

**COMPLETED, read-only felülvizsgálat:** 9/9 megismételt művelet osztályozva; négy kapacitásproxy kiszámolva; 35/35 projekt kártya és státusz beolvasva a két audit során.

**PARTIAL, teljes P2–P5 stratégia:** valódi szerveroldali margi­nális hatás, mentett/mentetlen állapot, hatások összekapcsolása, projektcsomag E2E és döntésmentés ismeretlen.

Funkcionális készültség: **UNKNOWN**; integrált E2E: **UNKNOWN**; éles használat: **UNKNOWN**; valamennyi Δ: **UNKNOWN** (a teljes stratégia nem rendelkezik reprodukálható százalékos mérési alappal).
