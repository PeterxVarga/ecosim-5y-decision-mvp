# EcoSim P2 – kritikus átadási őr és legnagyobb ROI-jú következő lépés

**Érvényesség:** P1 történeti forrásbizonyíték, nem P2 élő döntés. I. piac, Jutalom a nap végén.

## ROI Challenger

| Reális lehetőség | Kritikusút-hatás | Döntés |
|---|---|---|
| Régi P1/P2 offline szcenáriók újrafuttatása | Nem oldja fel az aktuális pénzügyi és döntési bizonytalanságot | Halasztás |
| P1-ben eredményes változtatások ismétlése | Két legerősebb kar P1-ben megfigyelt határértéken; tranzakciómezők ismétlése veszélyes | Elvetés élő baseline nélkül |
| **Egyidejű P2 read-only snapshot + a tranzakciómezők kontrollja** | Közvetlenül oldja a végrehajthatósági akadályt, minimalizálja a káros átvitel kockázatát | **Első** |
| Új policy-optimizer fejlesztése | A hatásmodell továbbra is kalibrálatlan | Halasztás |

## 9 nem nulla P1-műveleti mező – SOHA ne másold automatikusan új évi utasításként

| P1-bemenet | Végső P1 érték | P2 kezelés |
|---|---:|---|
| `institutions.education.middleSchool.change` | 1 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `institutions.sport.change` | 1 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `institutions.culture.change` | 1 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `institutions.healthCare.doctorsOffice.change` | 1 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `institutions.social.socialHome.change` | 1 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `publicTransport.hr.drivers.hire` | 50 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `publicTransport.hr.mechanics.hire` | 10 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `publicTransport.hr.office.hire` | -50 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |
| `publicTransport.bus.change` | -8 | Előbb olvasd vissza a jelenlegi P2 szerverállapotot és a mező jelentését |

Összes vizsgált P1-bemenet: **55**; akciójellegű `*.change` / `*.hire` mező: **14**, ebből nem nulla **9**. A P1 5. futás mentése után **nincs teljes 55/55 visszaolvasás**; a FACT export egyes végső értékeket függetlenül megerősít, nem mind az 55-öt.

## P1-ben megfigyelt határértékek (P2-re nem automatikus szabály)

| Mező | P1 utolsó érték | P1 felületi tapasztalat |
|---|---:|---|
| `institutions.bureau.wage` | 990 | max 990 |
| `income.taxes.business` | 0.3 | min 0.3 |
| `income.services.communalCost` | 5 | min 5 |
| `income.services.burialCost` | 20 | min 20 |
| `income.services.rentalCost` | 30 | min 30 |

## A P1 lokális mérésekből döntési szempontból megőrzendő bizonyíték

| P1 lokális kísérlet | Δ index | Δ tervezett tartalék | Korlát |
|---|---:|---:|---|
| Városházi bér 534→650 | +0,33 | −43 848 ECU | Végül 990-ig emelve |
| Városházi bér 650→800 | +0,42 | −56 700 ECU | Végül 990-ig emelve |
| Iparűzési adó 1,0→0,9% | +0,12 | −20 182 ECU | Végül 0,3%-ig csökkentve |
| Iparűzési adó 0,9→0,8% | +0,11 | −20 181 ECU | Végül 0,3%-ig csökkentve |
| Közműdíj 40→45 | −0,08 | +137 515 ECU | P1 végül 50; stratégiai pénzügyi trade-off |
| Dízelbusz-fenntartás 175 000→192 500 | +0,02 | −17 156 ECU | Gyenge lokális index/ECU arány |

Ezek P1 előnézeti, egymás utáni megfigyelések. Egyáltalán nem bizonyított, hogy P2-ben ugyanekkora, azonos irányú vagy ismételhető hatásuk lesz.

## P2 élő adatgyűjtési minimum, első döntés előtt

1. **Egyetlen azonosított P2 2/5 snapshot:** szerver dátum/idő, I. piac, csapat, határidő; jelölni mentett vs szerkesztett érték.
2. **Pénzügyek:** nyitó/valódi szabad pénz; P2 tervezett bevételek és kiadások; lekötött projektköltség; hitel- és törlesztési feltételek.
3. **Projektek:** mind a 35 státusza, már felhasznált P2-indítások száma, abszolút 4/év kapu; kezdeti/éves költség, előfeltétel, késleltetés.
4. **Összes szerkeszthető döntés:** legalább az 55 ismert mező, és minden további, valójában elérhető mező. A `change`/`hire` mezők P2 kezdőértéke és jelentése kiemelt.
5. **Pontozás:** 29 faktor, hat kategória, P2 PLAN index, pénzügyi előnézet egy időponthoz; ismeretlen képletek UNKNOWN.
6. **Csapatbiztonság:** csapattársak utolsó mentése/ütközés, mentett állapot igazolása; semmi megváltoztatása vagy Save.

## Első célzott P2 próbák (csak hiteles P2 baseline után, és kizárólag külön engedélyezett kísérletben)

1. **Szociális/életkörülmények új, még nem telített karjai:** 11,05 pontos P1 szociális részmutató-hátrány a vezetőhöz képest; *nem* bizonyítja, hogy olcsón növelhető. Egyetlen változó, visszamérés, rollback ellenőrzés.
2. **Mobilitás hiányzó komponensei:** Kiwi P1 mobilitás 65,17, saját 54,83. Ne másoljuk vakon a nagy elektromosbusz-vásárlást; előbb a P2 flotta, állomány, karbantartás és szabad pénz ellenőrzése.
3. **Költségvetési csere, ha P2-ben van mozgástér:** csak akkor vizsgálható, ha a P2 pénzügyi baseline és az adott díj/bér valódi változási tartománya ismert; az előző év érzékenysége nem projektköltségvetés.

## Lezárás

- A történeti P1 átadási ellenőrzés: **COMPLETED (offline)**; 55/55 bemenet felsorolva, 14 akciójellegű és 9 nem nulla kiemelve.
- A P2 teljes stratégia: **PARTIAL/BLOCKED** a hiteles élő P2 snapshot hiánya miatt.
- Teljes funkcionális / integrált E2E / éles használati készültség és Δ: **UNKNOWN**, nincs reprodukálható teljes nevező.
- Következő legjobb, jogosult művelet: a P2 autentikált felületen az egyidejű, kizárólag olvasott pénzügyi, projektes és döntési snapshot megszerzése. NO_GAME_WRITES / NO_SAVE / NO_NEXT_PERIOD.

## Forrás-hashek

- `EcoSim_futas_2.zip`: `29f7c373504d097fb0252d67f7ee5a46f14369ac77a4d483ec9d7efe68c09b28`
- `EcoSim_futas_3.zip`: `6a81078a9273582dfeeaaa3f6b209fe393a4ef6f8d1ff4a008229bd6b6af2db1`
- `EcoSim_futas_4.zip`: `8645fca20f8a7491081d3666e84b6f5e564a49405952e557ac724cf8bc9edc20`
- `EcoSim_futas_5.zip`: `e929a09b5788d318f50d7d1a6711df16006ddcfe640a8f148af5d784b884c879`
- `X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I (1).xlsx`: `23a76fd044fe698e66a18577642825eca1f058d5715cd8f85b05d0a3b9fd38ab`
