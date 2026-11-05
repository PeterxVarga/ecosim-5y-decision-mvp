# EcoSim P2 – Vállalkozásszám → SmartCity-faktor empirikus rekonstrukció (R3)

**2026. november 5. · Csak offline elemzés · Játékírás: 0**  
**Állapot: COMPLETED az empirikus vizsgálat, PARTIAL a teljes P2–P5 optimalizálás szempontjából.**

## Vezető következtetés

A rendelkezésre álló történeti tényadatok alapján a „Vállalkozások száma” faktor **valószínűleg az adott periódus cégszámának előző periódushoz mért százalékos növekedését méri, 50-es bázissal**:

`Vállalkozásszám-faktor ≈ 50 + 100 × (N_jelenlegi / N_előző − 1)`

Ahol `N = kisvállalkozások + középvállalkozások + nagyvállalkozások száma`.

**Bizonyítékszint: ERŐS EMPIRIKUS HIPOTÉZIS – NEM bizonyított EcoSim szerveroldali képlet.** A kijelzett vállalkozásszámok egészre, a mutató két tizedesre kerekítve jelennek meg; továbbá egyéb vállalkozásdinamikai mechanizmusok sem zárhatók ki.

## 1. P1 tényadatok – 7 csapat, egyazon exportban

Forrás: `X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I (1).xlsx`, `0` és `1` munkalap; 0. periódus: `B257, B261, B265` stb., 1. periódus: `B3:H3`, `B257:H257`, `B261:H261`, `B265:H265`. A P0 minden csapatnál **4 742 kis + 90 közepes + 25 nagy = 4 857 cég**.

| Csapat | P0 cégek | P1 cégek (kijelzett) | Valós mutató | Képlet | Két tizedes egyezés |
|---|---:|---:|---:|---:|---|
| Bányász kódok | 4857 | 4882 | 50,51 | 50,515 | Igen |
| Jutalom a nap végén | 4857 | 4882 | 50,51 | 50,515 | Igen |
| Kiwi | 4857 | 4887 | 50,62 | 50,618 | Igen |
| Kőbánya Optima | 4857 | 4883 | 50,52 | 50,535 | Nem, de kerekítéssel kompatibilis |
| Midas Nonprofit | 4857 | 4882 | 50,51 | 50,515 | Igen |
| Zéró | 4857 | 4882 | 50,51 | 50,515 | Igen |
| I7 | 4857 | 4879 | 50,45 | 50,453 | Igen |

**Eredmény:** a 7 csapatból **6/7** pontosan két tizedesre egyezik, **7/7** kompatibilis azzal, hogy a kis/közép/nagy vállalkozásszám egészre kerekített. A kivétel Kőbánya Optima: kijelzett cégek 4 883, faktor 50,52, az egész számos képlet 50,5353 (két tizedesen 50,54). A maximum ±1,5 cégnyi összegzett kerekítési bizonytalanság elegendő az eltéréshez; ez **nem bizonyítja** a tényleges belső tizedesértékeket.

**Kiegészítő történeti, TEST-Z ellenőrzés:** két külön P1-snapshot is pontos két tizedes egyezést ad: 4 879 cég → 50,45 és 4 881 cég → 50,49. A számok külön nézetekről, nem egyidejű mérési nyugtából származnak, ezért az egyezés támogató, nem független oksági kísérlet.

## 2. P2 terv – alternatív képletek falszifikációja

Forrás: 2026-11-05 bejelentkezett P2 Brave–Codex Összefoglalás és Vállalkozások alnézet; **P1 FACT → P2 PLAN**, mentettség UNKNOWN.

- P1 kijelzett cégszám **4 765 + 92 + 25 = 4 882**; tényező **50,51**.
- P2 kijelzett cégszám **5 226 + 108 + 28 = 5 362**; tényező **59,85**.
- **Évenként újrabázisolt növekedés:** `50 + 100×(5362/4882−1)` = **59,832**, eltérés a P2 kijelzéséhez képest **0,018**.
- A három egészre kerekített vállalkozáskategória miatt a képlet lehetséges kijelzési tartománya kb. **59,768–59,897**; az 59,85 ezen belül van.
- **P0-hoz viszonyított kumulált növekedés** = **60,397**, a 59,85-höz képest már ~0,55 eltérés; ez az alternatíva kevésbé illeszkedik.
- **50×éves cégszám-növekedési hányados** = **54,916**; erősen ellentmond a megfigyelésnek.

A kerekítés megmagyarázhatja a P2-ben fennmaradó ~0,018-as eltérést, de a pontos rejtett cégszám **UNKNOWN**. Ezért a képlet jelenleg nem igazolt 100%-os szerverrekonstrukció.

## 3. P1-ben visszaállított, négyprojektes valós UI-próba

Forrás: `ecosim-p1-codex-audit-20261104-135151.zip`, `R258_B_FINAL_SUCCESS_PRIVATE.json`, 2026-11-03, I. piac, P1/5. Start és Cancel átmeneti próba, **Save = 0**.

- Négy projekt: **#4, #13, #21, #27**; egyenkénti hatások elkülönítése nem történt meg.
- „Vállalkozások száma” előtte **50,45**, próbában **50,51**, rollback után **50,45**.
- A TEST-Z történeti kártyák szerint együttes hatásuk: +0,04% kisvállalkozás és +1% középvállalkozás (a százalékok összeszorzása mellett).
- Becsült plusz cégek a korábbi P1 kártyakészletben: kis **1,905**, közepes **0,910**.
- Képlethipotézis szerinti faktornövekedés: **+0,058**; kijelzett faktornövekedés: **+0,06**.

**Ez kontrollált, tényleges UI-összevetés, de nem egyváltozós:** nem bizonyítja külön a kis- és középvállalati súlyt, és a kártyahatások hatásának pontos időzítését sem.

## 4. A korábbi R2 modell korrekciója

A R2 a P1/FACT és P2/PLAN különbségeiből képzett `9,34/480 = 0,019458` faktorpont/cég szelőt használta. Ez összekeveri az éves faktor újrabázisolását a két év között megfigyelt cégszámváltozással.

Az R3 képlethipotézisben a P2 marginális faktorpont/cég **100 / 4 882 = 0,020483**. A vállalkozásszám-index teljes indexproxy súlya **0,0625**. Így:

- R2: **0,001216146** indexpont/új cég (megfigyelési szelő).
- R3: **0,001280213** indexpont/új cég (éves növekedési hipotézis).
- Eltérés: **+5,27%** az R2 meredekségéhez képest.

A R3 már nem használja az R2 szelőjét elsődleges cégszámhatás-tényezőként. Az R3 sem tekinthető játékbeli oksági együtthatónak, csak jobb empirikus feltételes modellnek.

## 5. Újraellenőrzött projektcsomag-rangsor

**R3 feltételek:** max. 4 új projekt; 35 projektből 10 fut; 12 386, feltételesen megengedett kombináció a 450 000 ECU-s felső hipotetikus keret alatt; P2 szerveres projektpreview nincs; új projekt partneri támogatása nem számít garantált cashnek.

| Feltételezett projektkeret, ECU | Direkt rangelső | R2 indirekt | R3 empirikus hipotézis | R3 feltételes Δ index |
|---:|---|---|---|---:|
| 75 000 | 8,9,26,28 | 8,9,26,28 | **8,9,26,28** | 0,361959 |
| 150 000 | 4,8,16,21 | 4,8,16,21 | **4,8,16,21** | 0,523255 |
| 300 000 | 8,21,26,33 | 8,21,26,33 | **8,21,26,33** | 0,591470 |
| 450 000 | 4,8,21,33 | 4,8,16,33 | **4,8,16,33** | 0,617825 |

A 450 000 ECU-s keretnél a két szoros jelölt: **#4/#8/#16/#33** vs. **#4/#8/#21/#33**. A R3 feltételes indexelőnye az előbbinél **+0,001233**, de ez nem mért játékbeli különbség. A fordulási küszöb a R3 referencia ~**0,079×**, tisztán modellbelső paraméter.

**A másik három feltételezett keret rangelsője nem változott.** Ez a szűk képletkorrekció csak a közvetett vállalkozásszám-hatást módosította, nem a teljes városreakciót, így továbbra sem állíthatunk igazolt P2/P5 optimumot.

## 6. ROI Challenger – miért ezt és hogyan tovább?

1. **További véletlenszerű szorzórács:** nem oldja fel a képletazonosítási problémát, alacsonyabb ROI.
2. **A meglevő hét csapat és két történeti snapshot keresztellenőrzése:** elvégezve; ez érdemben korlátozza a lehetséges képleteket, és a R2 együtthatóját korrigálja.
3. **Pontos szerverforrás-képlet felkutatása:** erős bizonyítás lenne, de jelenleg nincs hiteles hozzáférhető forráskód vagy manuális képlet; nem találgatunk.
4. **Az egyedi kis-/középvállalkozás-kártyahatás hitelesítése egyetlen elkülönített UI-próbával:** akkor indokolt, ha a #16 és #21 közötti döntés valóban fennmarad, és a felhasználó kifejezetten engedélyezi az ideiglenes, mentés nélküli, bizonyítottan visszaállítható játékterv-változtatást. Most nincs ilyen engedély.

**Következő legjobb biztonságos ROI:** nem újabb modellparaméterek keresése, hanem az immár jobban alátámasztott vállalkozásszám-hatást és a versenytársak P1-döntéseit felhasználva a P2 projektcsomagok *kockázati döntéshatárait* szűkíteni, és pontosan megnevezni azt az egyetlen élő kísérletet, amely ténylegesen megfordíthatja a választást. A játékot változatlanul hagyjuk.

## Bizonyíték és korlát

**COMPLETED – jelen elemzési kör:** 7/7 P1-csapat kerekítéssel összeegyeztethető, 6/7 két tizedesen pontos; 2/2 történeti teszt Z példa pontos; egy visszaállított négyprojektes P1-próba konzisztens; P2 kerekítési tartomány konzisztens; 12 386 projektkombináció újraszámítva; 14/14 új és 17/17 korábbi célzott offline teszt PASS; Excel-képletek ellenőrizve, játékírás 0.

**PARTIAL – teljes P2–P5 stratégia:** a vállalkozásszám-faktor pontos szerveroldali implementációja UNKNOWN; a kis vs. középvállalkozások per-projekt oksági hatása UNKNOWN; P2 terv mentettsége UNKNOWN; a P3–P5 átmenet és ellenfélstratégia továbbra sem kalibrált.

**Funkcionális készültség:** UNKNOWN (a teljes ötéves döntéstámogató rendszernek nincs reprodukálható képességnevezője). **Integrált E2E:** UNKNOWN (a történeti négyprojektes P1-próba nem éles P2/P5 döntés). **Éles használati készültség:** UNKNOWN (P2 mentettség és jóváhagyott játékdöntés nincs igazolva). **Δ mindhárom:** UNKNOWN (nem áll rendelkezésre korábbi összehasonlítható teljesprojekt-mérés).

**Állapotkapu:** `NO_GAME_START / NO_SAVE / NO_NEXT_PERIOD / NO_API_WRITE / NO_MERGE / NO_DEPLOY`.
