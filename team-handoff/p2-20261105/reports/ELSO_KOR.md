# Az első selejtezőkör mentett döntési csomagja

**2026. november 3. · Selejtező · I piac · Jutalom a nap végén · 1/5. periódus**

A teljes elsőéves döntési csomag mentve. A sikeres mentési visszajelzést rögzítettem; újratöltés után az összes 55 megfigyelt döntési mező változatlanul visszaolvasható. A végső projektcsomagot a kontrollált alternatívapróbák után külön ismét visszaállítottam, mentettem és újratöltve ellenőriztem.

| Mutató | Kiinduló P1-terv | Mentett P1-terv |
|---|---:|---:|
| SmartCity index | 52,48 | **55,49** |
| Tervezett tartalék | 1 051 111 ECU | **379 862 ECU** |
| Bevétel | 5 562 335 ECU | **5 445 496 ECU** |
| Kiadás hitel/tartalék nélkül | 4 511 224 ECU | **5 065 634 ECU** |
| Hitelfelvétel | 0 | **0** |

A PLAN-javulás **+3,01 indexpont**. A P0 tényleges indexe külön adat: 51,96. A P1-érték még előnézet, nem lezárt elsőéves eredmény.

## A négy indított projekt

| ID | Projekt | Indítás + beruházás | Előjeles éves fenntartás |
|---:|---|---:|---:|
| 12 | Lakás- és helyiséggazdálkodás | 83 000 | -12 000 |
| 13 | Informatikai fejlesztés | 55 000 | -8 800 |
| 27 | Vasútfejlesztés | 15 000 | 0 |
| 32 | Megújuló energia park | 235 000 | -45 000 |

Az indítás és beruházás összesen **388 000 ECU**, az előjeles éves fenntartás **−65 800 ECU**. A játék P1 projektkiadási sora így **322 200 ECU**, ami az eredeti repó külön kártyaköltség-újrajátszásával is egyezik. A 15 000 ECU kijelzett új partnertámogatást külön bevételként kezeltem, nem vontam le a konzervatív modellkeretből.

A #12 lakhatási és szociális mutatókat javít és a kártyán bérleti bevételt mutat; a #13 az adminisztráció és digitalizáció mellett működési megtakarítást ad; a #27 javítja az elérhetőséget és később megnyitja a P+R előfeltételét; a #32 fenntarthatóságot és energiatermelési bevételt ad. A kártyák százalékos hatásai nem azonosak indexpontokkal.

## Miért ezt választottam?

Az aktuális felületen mindhárom csomagot azonos intézményi, közlekedési, adó- és díjbeállítások mellett mértem.

| Jelölt | Projektek | P1-index | P1 tartalék | Előjeles éves projektfenntartás |
|---|---|---:|---:|---:|
| A – kisebb elsőéves ráfordítás | 12, 13, 27, 29 | 55,44 | 508 129 | −18 300 |
| B – magasabb P1-index | 1, 13, 27, 33 | 55,52 | 405 798 | −3 400 |
| **C – mentett pénzügyi alap** | **12, 13, 27, 32** | **55,49** | **379 862** | **−65 800** |

A B terv P1-ben valóban 0,03 ponttal magasabb és 25 936 ECU-val több tartalékot ad. A C tervnél viszont a kártyák szerinti éves működési megtakarítás 62 400 ECU-val nagyobb. Ez az ötéves folytatáshoz kedvezőbb alap lehet; a tényleges ismétlődő hatást a következő FACT-adatokkal ellenőrizni kell.

A friss repó eredeti Python-motorját kilenc feltételes futásban használtam: hat szabad keresés (100/250/400 ezer ECU-s, egyenletes éves feltételezett keretek, nominal/scenario_min cél), majd három rögzített elsőéves alternatíva összehasonlítása. Az utóbbiaknál mindhárom terv ugyanazt a 400/250/250/250/250 ezer ECU-s hipotetikus projektkeretet kapta. Az eredeti R160 audit a kiválasztott terveknél nulla kemény szabálysértést és nulla feltételes jogosultsági tételt jelzett; az R232 korlát minden évben legfeljebb négy indítást engedett.

| Rögzített elsőéves csomag | Feltételes ötéves nominális nyereség | Feltételes robusztus modellnyereség |
|---|---:|---:|
| A | 1,844111 | 0,625352 |
| B | 1,850637 | 0,614522 |
| **C** | **1,893659** | **0,645112** |

Ezek projektmodell-értékek, nem teljes városi vagy szerveres P5-előrejelzések. A robusztus érzékenység sem valószínűségi garancia. A C a három azonos későbbi keretű összevetésben lett a legjobb vizsgált modelljelölt; globális optimumot vagy győzelmet nem állítok.

## A 35 módosított periodikus mező

A tábla a játék által ténylegesen elfogadott értékeket mutatja, a saját kijelzett mértékegységeikben. A 550-es oktatási és 415-ös városi szolgáltatói bért megtartottam; a terjedelmes bértömeg tartós emelése helyett a kapacitásra, képzésre és fejlesztésre jutott forrás.

| Döntés | Kiinduló | Mentett |
|---|---:|---:|
| Oktatás – képzés | 12 000 | 14 400 |
| Oktatás – fejlesztés | 50 000 | 60 000 |
| Középiskolák változása | 0 | 1 |
| Sport és kultúra – bér | 425 | 510 |
| Sport és kultúra – képzés | 10 000 | 11 000 |
| Sport és kultúra – fejlesztés | 43 000 | 47 300 |
| Sportlétesítmények változása | 0 | 1 |
| Kulturális intézmények változása | 0 | 1 |
| Egészségügy – bér | 550 | 660 |
| Egészségügy – képzés | 10 000 | 13 000 |
| Egészségügy – fejlesztés | 40 000 | 48 000 |
| Orvosi rendelők változása | 0 | 1 |
| Városi szolgáltatók – képzés | 33 000 | 39 600 |
| Városháza – bér | 445 | 534 |
| Városháza – képzés | 5 000 | 6 000 |
| Környezeti fejlesztés | 25 000 | 30 000 |
| Civil támogatás | 17 000 | 20 400 |
| Szociális ellátás – bér | 385 | 462 |
| Szociális ellátás – képzés | 10 000 | 12 000 |
| Lakásfelújítási támogatás | 35 000 | 42 000 |
| Szociális fejlesztés | 45 000 | 54 000 |
| Szociális otthonok változása | 0 | 1 |
| Buszvezetők felvétele/elbocsátása | 0 | 35 |
| Buszvezetők képzése/fő | 30 | 39 |
| Szerelők felvétele/elbocsátása | 0 | 10 |
| Közlekedési irodai létszámváltozás | 1 | -50 |
| Közlekedési irodai képzés/fő | 25 | 32 |
| Dízelbuszok vásárlása/eladása | 0 | -5 |
| Közlekedési díj/fő | 12,4 | 11 |
| Temetkezési díj/fő | 32,2 | 29 |
| Bérlakás díja/fő | 45 | 40,5 |
| Vállalkozási adó (%) | 2 | 1,6 |
| Gépjárműadó (%) | 1,9 | 2,1 |
| Kommunális adó (%) | 1,1 | 0,9 |
| Építményadó (%) | 0,5 | 0,4 |

## Működési és forrásellenőrzés

- Középiskola +1, rendelő +1, sportlétesítmény +1, kulturális intézmény +1, szociális otthon +1. Oktatási intézménybezárás nincs.
- 290 buszvezető: 96,55% terhelés; 34 szerelő: 97,48%; közlekedési iroda: 79,43%. A járműállomány 65 dízel és 5 elektromos busz, megmaradó kapacitási tartalékkal.
- Mind a 35 aktuális kártya négy pénzügyi adata és minden kijelzett százalékos hatáscímke/érték egyezik a katalógussal. A 30-as és 31-es projekt előfeltétele jelenleg nem teljesül; ezeket nem indítottam.
- Mind a tíz fő fület és az összes hozzáférhető döntési alnézetet átnéztem. A népesség, vállalkozások és elemzés nézetei nem tartalmaztak külön szerkeszthető mezőt.
- A kiinduló tényezőket és projektstátuszokat a meglévő R156→R152 beolvasó normalizálta. A tényleges szerverkonfiguráció számszerű maximumát nem állítottam ismertnek; a négyes indítási korlátot a repó R232 szervezői forrása és a sikeresen mentett négy indítás támasztja alá.
- A hat súlyozott kategória külön újraszámolt összege és a pénzügyi bevétel–kiadás azonosság is egyezik a kijelzett végeredménnyel.

## Következő évi pénzügyi érzékenység – csak feltételezés

Ha a jelenlegi működési sorokat változatlannak tekintjük, az egyszeri nyitópénz, osztalék, két fejlesztési támogatási sor és eszközeladás nélkül számított bevétel 5 035 752 ECU. Az egyszeri 388 000 ECU projektindítást/beruházást elhagyva a kiadás 4 677 634 ECU. Így a feltételes működési különbözet 358 118 ECU, újabb projektek előtt. Az így számolt bevétel 5%-os csökkenésénél 106330 ECU maradna új projektek előtt.

Ez nem tényleges P2-keret: a lakosság, riválisok, intézményi költségek, támogatások és szabályok változhatnak. A P2–P5 keretek végig hipotetikusak. A következő döntéshez a lezárt P1 FACT-ot, a tényleges cash-t, új korlátokat és friss kártyákat kell beolvasni; a feltételes öt éves projektlistát nem szabad automatikusan végrehajtani.

## Reprodukálhatóság

- Friss repóforrás: `main@26316dd9e39f2f4f23a559d399330e05001780fc`.
- Modell: eredeti `strategy_5y.search`, R157 érzékenység, R160 audit, R232 abszolút négyes limit. Nem új optimalizáló vagy JavaScript-indexátirat.
- `catalog-parity.json`, `capture.json`, `r156-bundle/`, `normalized-state.json`: aktuális forrás és meglévő beolvasók.
- `model-comparison.json`, `first-action-comparison.json` és a teljes `*-model.json` állományok: feltételes natív futások.
- `measures.json`: tényleges felületi A/B/C mérések; `changes.json`: változtatási napló.
- `persisted-inputs.json`: az 55 mező újratöltés utáni egyezése; `final-save-receipt.txt`: sikeres utolsó mentés.
- `summary-final.json`, `finance-final.json`, `FINAL_VERIFICATION.json` és a két PNG: végállapot és ellenőrzés.
- A friss játékadatokat és döntési dossziét kizárólag helyben tároltam, a nyilvános GitHub-repóba nem kerültek.
