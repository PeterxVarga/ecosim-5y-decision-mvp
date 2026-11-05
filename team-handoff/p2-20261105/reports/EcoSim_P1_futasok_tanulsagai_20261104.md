# EcoSim P1 – november 3-i felületi próbák bizonyítékalapú tanulságai

*2026-11-04. Forrás: a felhasználó által feltöltött EcoSim_futas_2.zip ... EcoSim_futas_5.zip; az eredeti P1 FACT Excel.*

## Bizonyítékszintek

- **P1 terv / UI előnézet**: a korábbi felületi mérés; nem bizonyítja P2/P5 hatásokat.
- **P1 mentés + újratöltés**: futás 2/3/4, 55/55 döntési mező és 10 fül visszaigazolva a csomagok szerint.
- **P1 mentési visszajelzés visszaolvasás nélkül**: futás 5; az `expected-inputs.json` rekonstrukció, nem mentés utáni teljes szerveres dump.
- **P1 FACT export**: a lezárt P1 58,87 indexe és 309 280,31 ECU nettó eredménye.

## Futások sorrendje

| Futás | P1 tervindex | Tervezett tartalék (ECU) | Állapot | Forrás |
|---|---:|---:|---|---|
| 2 | 55.71 | 355,158 | 10 saves / 55/55 reload | EcoSim_futas_2.zip / review2/ELLENORZES.md |
| 3 | 56.73 | 248,098 | 10 saves / 55/55 reload | EcoSim_futas_3.zip / review3/ELLENORZES.md |
| 4 | 58.72 | 352,904 | 10 saves / 55/55 reload | EcoSim_futas_4.zip / review4/ELLENORZES.md |
| 5 | 58.87 | 309,280 | save feedback; 55/55 reload missing | EcoSim_futas_5.zip / review5/ELLENORZES.md |

- 2→3: +1,02 pont és −107 060 ECU; 14 eltérő mező a végpontok között.
- 3→4: +1,99 pont **és** +104 806 ECU; 5 eltérő mező; a 4. végpont mindkét indikátorban jobb, mint a 3.
- 4→5: +0,15 pont és −43 624 ECU; 9 eltérő mező, a végső visszaolvasás hiányzik.
- A 2.→4. változtatássor +3,01 indexpontot ért el mindössze 2 254 ECU tartalékcsökkenéssel, de ebből **nem** következik egyetlen változó tiszta hatása.

## Egymezős vagy egy lépésben dokumentált lokális P1 érzékenységek

| Csak egy változtatott, elfogadott bemenet a két egymás utáni mért állapot között | Δ index | Δ tervezett tartalék | Forrás |
|---|---:|---:|---|
| Városházi bér 445→534 | +0,25 | −33 642 ECU | futas_3 / checks.json |
| Városházi bér 534→650 | +0,33 | −43 848 ECU | futas_4 / checks.json |
| Városházi bér 650→800 | +0,42 | −56 700 ECU | futas_4 / checks.json |
| Iparűzési adó 1,0→0,9% | +0,12 | −20 182 ECU | futas_3 / checks.json |
| Iparűzési adó 0,9→0,8% | +0,11 | −20 181 ECU | futas_3 / checks.json |
| Víz/csatorna/távhő díj 40→45 | −0,08 | +137 515 ECU | futas_4 / checks.json |
| Dízelbusz fenntartás 175 000→192 500 | +0,02 | −17 156 ECU | futas_2 / checks.json |
| Elektromos busz fenntartás 15 000→18 000 | +0,01 | −2 940 ECU | futas_2 / checks.json |
| Egészségügyi intézmény bér 550→575 | +0,02 | −6 460 ECU | futas_3 / checks.json |

**Fontos:** a különbségek a felület egymást követő P1 tervmérései, nem független randomizált kísérletek. Csak akkor tulajdoníthatók az adott mezőnek, ha nem történt naplózatlan, egyidejű vagy késleltetett változás. A pénzügyi tartalék előnézet, nem a következő évi elkölthető pénz. A 0,01 pontos kerekítés bizonytalan különbségeket takarhat.

## Elfogadott UI-korlátok, nem feltétlenül univerzális P2 határok

- Vállalkozási adó 0% kérése → 0,3% elfogadva.
- Városházi bér 1200 kérése → 990 elfogadva.
- Kommunális díj 0 kérése → 5 elfogadva.
- Temetkezési díj 0 kérése → 20 elfogadva.
- Bérlakásdíj 0 kérése → 30 elfogadva.
- Szerelők +14 felvételi próbája → +10 elfogadva.
- Egyes képzési és fejlesztési emelések kérései → változatlan elfogadott érték; no-op nem keverendő új intézkedéssel.

## A korábbi 10/10 konfliktus feloldása

A review5/expected-inputs.json mind a hat szolgáltatási díja és mind a négy adókulcsa pontosan egyezik a lezárt P1 FACT Excel `1` munkalapjának C191:C196, C198:C201 celláival. Az 55,56-os terv az idők folyamán lecserélődött; az 5. futás 58,87/309280-as kijelzése megfelel a P1 tényexport 58,87/309280,31 értékének.

**Az 5. futás 55/55 teljes visszaolvasása hiányzik**, ezért nem állítható, hogy mind az 55 rekonstruált mező pontosan megegyezett az alkalmazott szerveres beállítással.

## P2-alkalmazás

1. A négyfutásos napló legyen **történeti P1 érzékenységi nyilvántartás**, ne kalibrált P2 ok-okozati modell.
2. Egy P2 intézkedés értékét először a tényleges 2/5 szerveres baseline, a menübeli elfogadott új mezőérték, a pénzügyi előnézet és a 29 tényező változása alapján mérjük.
3. P2-ben három eltérő teendő versenyez: mostani költségkeret/projektek igazolása; teljes döntési baseline megszerzése; egyetlen ígéretes P1 érzékenység célzott falszifikálása. Az első kettő a megvalósíthatóságot és integrált döntést blokkolja, ezért előrébb való, mint további P1 variációk tesztelése.
4. Nem igazolt P2/P5 optimum, projektkeret vagy versenytársi reakció. NO_GAME_WRITES, NO_SAVE, NO_NEXT_PERIOD.

## SHA-256 fájlazonosítók

- `EcoSim_futas_2.zip`: `29f7c373504d097fb0252d67f7ee5a46f14369ac77a4d483ec9d7efe68c09b28`
- `EcoSim_futas_3.zip`: `6a81078a9273582dfeeaaa3f6b209fe393a4ef6f8d1ff4a008229bd6b6af2db1`
- `EcoSim_futas_4.zip`: `8645fca20f8a7491081d3666e84b6f5e564a49405952e557ac724cf8bc9edc20`
- `EcoSim_futas_5.zip`: `e929a09b5788d318f50d7d1a6711df16006ddcfe640a8f148af5d784b884c879`
