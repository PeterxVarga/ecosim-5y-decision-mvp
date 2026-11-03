# EcoSim R258 – A és B tényleges P1-próbája egymás után

2026. november 3. · I. piac · Jutalom a nap végén · periódus 1/5

A felhasználó kizárólag ideiglenes Start/Cancel összehasonlítást engedélyezett.
**Sem Save, sem Next Period, sem külső játék-API írás nem történt.**

| Friss játékteszt | A: #4, #13, #27, #33 | B: #4, #13, #21, #27 |
|---|---:|---:|
| SmartCity-index | **53,28** | 53,16 |
| Projektek kijelzett költsége | 305 200 ECU | **139 200 ECU** |
| P1 perióduseredmény | 768 280 ECU | **929 332 ECU** |
| Rövid lejáratú hitel | 0 ECU | 0 ECU |

Az A-t a mostani R258-körben frissen, négy ideiglenes Starttal
a Summary és Finance oldalakon ismét megmértük. Az eredmény
egyezik a korábbi R249 autentikált A-próbaértékekkel.
A különböző DOM-azonosítók miatt a visszavonásnál átmeneti
technikai hiba történt, de a helyreállító Cancel sikeres lett:
a kliens szerint új P1-projektből nulla maradt.

Csak ezután indult a B újabb, külön elszigetelt böngészőben.
A B-próba teljes négyes projektindítását, Summary/Finance értékeit
és négy Cancel akcióját a R258_B_FINAL_SUCCESS_PRIVATE.json
külön forrásbizonyíték őrzi. A B után az eredeti 52,48-as
SmartCity-index, 0 ECU projektkiadás, 1 051 111 ECU
perióduseredmény, 0 ECU rövid lejáratú hitel tért vissza.
A 35 projektből az eredeti hat maradt futó állapotban.

## Döntési különbség

A +0,12 azonnali P1-indexpontot ad B-hez képest,
de 166 000 ECU-val többe kerül és 161 052 ECU-val
kisebb tervezett perióduseredményt hagy.
Az A pénzügyileg rosszabb, de indexben jobb; egyik
sem Pareto-dominálja a másikat.

A 15%-os bevételkiesési hipotetikus stresszteszt nem játékbeli
előrejelzés: A -66 070,25, B +94 981,75 ECU perióduseredményt
adna változatlan többi tétel esetén. Ez önmagában
nem bizonyítja, hogy B nyerhet nagyobb eséllyel az ötödik évben.

A +1 éves irodai dolgozó felvételi mezőt érintetlenül hagytuk,
ugyanazzal a beállítással készült mindkét próba.

## Biztonsági bizonyíték

A B-próba operátornaplója és a React-projektstátuszok egyeznek:
Start 4,13,21,27; Cancel 27,21,13,4. A végén
a P1 projektbeállítások eltérése a P0 alaptól nulla.
A saját csapat egyéb numerikus/logikai döntései a próba során
nem változtak, az izolált böngészőt leállítottuk.
Az aktuális szerveren történt külön Save nem igazolt, de
a teszt egyetlen mentési műveletet sem végzett.

## Státusz és következő döntés

R258 jelen körben végzett A/B UI-összehasonlítás: COMPLETED.
Teljes 5 éves nyerő stratégia: PARTIAL, mert a P2–P5
gazdasági reakciók és a többi csapat döntései nem ismertek.
Funkcionális, integrált 5 éves E2E és éles használati
készültség %-a és mindhárom Delta százalékpontja UNKNOWN:
nincs reprodukálható teljesprojekt mérési nevező.

A következő lépés az A/B tulajdonosi kiválasztás.
A végleges projektindításhoz és Save-hez külön, kifejezett
jóváhagyás kell. GAMEPLAY_GATE=STOP.
