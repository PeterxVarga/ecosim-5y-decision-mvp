# EcoSim P2 – projekt-hatásmodell + városi pénzügyi híd (R1, 2026-11-05)

**Státusz: COMPLETED (engedélyezett offline integráció); PARTIAL (teljes P2–P5 stratégia).** Játékbeli művelet: **0**. Ez a modell csak a **2026. november 5-én kiolvasott P2-terv** és egy **2026. október 30-i tesztfordulós projekthatás-katalógus** közötti feltételes összehasonlítás. **Nem élő EcoSim-előrejelzés, nem végleges játéktanács.**

## 1. Bizonyított adat- és pénzügyi egyezések

- **P1 index:** megjelenített 58,87; 29 tényezőből újraszámított **58.865979** (kerekítésre egyezik).
- **P2 tervindex:** megjelenített 60,52; 29 tényezőből újraszámított **60.521150** (kerekítésre egyezik).
- **35/35 P2 élő projektkártya költsége** változatlan az archív projekttáblához képest; státusz **10 futó / 25 nem futó**.
- A futó 10 projekt éves **előjeles fenntartási költsége −65 800 ECU** (12: −12 000; 13: −8 800; 32: −45 000; a többi 0), **pontosan megegyezik** a P2 pénzügyek projektsorával. Ez ellenőrzi az alapállapoti fenntartás elszámolását, de nem igazolja az új projektek támogatásának és időzítésének szabályait.
- A történeti projektkatalógusban **272 hatásbejegyzés** van. **242 közvetlenül a 29 tényező valamelyikéhez rendelhető**, **30** a kis-/középvállalkozások darabszámához tartozik, közvetett hatásuk UNKNOWN. Nem vettük őket nullának.
- **Kilenc ismételt egyszeri P1-művelet** szerepel a P2 alapállapotban; azok P2-es költségei és faktorhatásai már a 60,52-es index / 868 143 ECU tartalék részei. A projektváltozatokban nem számoljuk még egyszer ezeket.

## 2. Számvitel: a 309 280 ECU áthozat nem új P2 nyereség

| Tétel | ECU | Szint |
|---|---:|---|
| Jelenlegi P2 teljes bevétel, benne az előző év végi pénzállomány | 5,693,381 | VERIFIED PLAN |
| Előző év végi pénzállomány | 309,280 | VERIFIED PLAN |
| P2 bevétel áthozat nélkül | 5,384,101 | DERIVED |
| P2 kiadások, tartalék nélkül | 4,825,239 | VERIFIED PLAN |
| Ebből futó projektek *előjeles* fenntartási sora | -65,800 | VERIFIED / RECONCILED |
| P2 egyéb városi kiadás, projektek nélkül | 4,891,039 | DERIVED |
| P2 nettó pénzügyi javulás, meglévő projektek nélkül | 493,062 | DERIVED |
| P2 éves többlet, meglévő projektekkel | 558,862 | DERIVED |
| P2 terv szerint számított záró tartalék | 868,142 | DERIVED |
| Játékban kijelzett P2-tervtartalék | 868,143 | VERIFIED PLAN |
| Egyezési eltérés a kijelzett, kerekített sorokból | 1 | DERIVED; várható kerekítés, nem bizonyított |

**Megjegyzés:** a P2-ben várható éves többlet **558 862 ECU**, és nem **868 143 ECU**. Ez kizárólag a *jelenlegi* terv visszafejtett cash-flow-ja; a projektindítások és más döntések ezt megváltoztathatják. A 868 143 ECU **nem hitelesített azonnal elkölthető keret**.

## 3. P2 projektportfóliók – csak feltételes offline direkt hatás

**Szigorú feltételek:** legfeljebb 4 új projekt/év (szervezői információ, szerveroldali limit nem bizonyított); csak a P2-ben nem futó 25 projektből; ismeretlen/azonos évi előfeltétel elutasítva (Bubi #30 az előbb nem futó #29 miatt kizárva); nincs hitel, partneri támogatást nem nettósítunk, negatív új fenntartást nem tekintünk biztos készpénzforrásnak. A projektköltség-szcenáriók 75k/150k/300k/450k **feltételes keresési burkok**, nem jóváhagyott pénzügyi keretek.

A modell a történeti kártyákból csak a leképezett *közvetlen* százalékos hatást számolja a P2 aktuális faktoraira, feltételezett egyszeri azonnali alkalmazással. **Közvetett vállalkozáshatások, piaci átmenet, versenytársi reakció, szaturáció és jövőévi változások nem jósolhatók belőle.**

| Feltételes projektkeret (ECU) | Direkt proxy szerinti jelölt IDs | Konzervatív P2 ráfordítás (ECU) | Elméleti P2 maradék tartalék támogatás nélkül (ECU) | Kizárólag leképezett Δ indexproxy | P2–P5 konzervatív újprojekt-ráfordítás (ECU)* | Nem leképezett hatásrekordok |
|---:|---|---:|---:|---:|---:|---:|
| 75 000 | 8, 9, 26, 28 | 72 500 | 795 643 | +0.357231 | 86 000 | 4 |
| 150 000 | 4, 8, 16, 21 | 150 000 | 718 143 | +0.515849 | 177 000 | 5 |
| 300 000 | 8, 21, 26, 33 | 293 000 | 575 143 | +0.586072 | 311 000 | 5 |
| 450 000 | 4, 8, 21, 33 | 308 000 | 560 143 | +0.610524 | 332 000 | 5 |

* A P2–P5 költség számítása = egyszeri indítás+beruházás **+ 4 × pozitív éves fenntartás**, változatlan fenntartás feltételezésével. **Nem négyéves pénzforgalmi prognózis.** A kártyán megjelenő partneri támogatás és negatív fenntartás nem kerül hozzáadott finanszírozásként a keretbe; a tényleges időzítés UNKNOWN.

### Kiemelt jelöltek és a rangsor falszifikációja

- **75k keretnél:** #8 Okos Gazdaság Alkalmazások, #9 Közösségi Finanszírozási Rendszer, #26 Reptér elérhetőség javítása, #28 Új trolibuszútvonal. Csak illusztratív, leképezett **+0,357231** indexhatás; a nem leképezett közvetett hatások miatt nem állítható valós P2 eredmény.
- **150k keretnél:** #4 Körforgásos gazdaság, #8 Okos Gazdaság, #16 Nyitott Alkotó és Innovációs Terek, #21 Közlekedési Múzeum; a **150 000 ECU** konzervatív ráfordítás a hipotetikus keret szélén van.
- **300k keretnél:** #8, #21, #26 és #33 Népliget. A konzervatív ráfordítás **293 000 ECU**, és a becsült P2 tartalék **575 143 ECU** lenne *minden más tervezett érték változatlansága mellett*.
- **450k keretnél:** #4, #8, #21, #33. A költség **308 000 ECU**, tehát a feltevés szerinti plusz 150 ezres felső keretet nem meríti ki. Közel azonos direkt proxy eredményt ad a **#4, #8, #16, #33** kombináció (0,610419 a 0,610524-hez képest, 316k ráfordítással). Ez a **0,000105 indexpontnyi** különbség jóval kisebb, mint a nem validált hatások bizonytalansága: **nem indokol valódi rangsorolást**.

A három kipróbált projekt-hatásamplitúdó **0,5× / 1× / 1,5×** kizárólag matematikai érzékenység, nem valós piaci forgatókönyv. Az érzékenységi minimum a 450k modellben a #4,#8,#16,#33 kombinációt enyhén előrébb helyezi, mint a nominálisan első csomagot. **Ez a rangsorcserélődés falszifikálja, hogy már ismernénk a „legjobb” négy projektet.**

## 4. ROI Challenger – miért ez a kör, és mi lehet jobb legközelebb?

| Alternatíva | Miért reális? | Miért nem választottuk most? |
|---|---|---|
| A 10 fő- és alnézet ismételt beolvasása | Frissesség | A november 5-i adatok összegyűjtve, a fő pénzügyi és 35 projektköltség összhangban; újraolvasás nagy súrlódás, kevés új információ |
| Közvetlenül beállítani a 4 projektet és menteni | Azonnali játékbeli előrelépés | Nincs jóváhagyás, a 30 közvetett hatás és az új támogatások időzítése bizonytalan; nem bizonyított valós optimum |
| **A meglévő R142–R147 hatásreplay + élő P2 cash és státusz összekapcsolása** | Meglevő OSS/saját kód újrafelhasználása, reprodukálható és read-only | **Választva és elvégezve.** |

**Következő legnagyobb ROI:** a shortlist 3–4 egymáshoz közeli projektcsomagjának **élő, visszaállítható, mentés nélküli pontszám- és pénzügyi ellenőrzése**, *de csak az automatikus mentés működésének igazolása és külön tulajdonosi felhatalmazás után*. Alternatív, teljesen offline következő körben külön a **30 közvetett vállalkozásszám-hatás** bizonyítható leképezését és a kilenc megismételt P2-művelet pontszám/ár érzékenységének P1-es egyváltozós bizonyítékát érdemes feldolgozni; ez előfeltétel hiányában biztonságosabb, mint új szintetikus ötéves előrejelzés.

## 5. Elfogadási bizonyítékok és korlátok

- Források: `EcoSim_P2_Brave_Codex_elo_ellenorzes_20261105.md` (2026-11-05, 10 főoldal), `Pasted text(20261105-122441).txt` (21 alnézeti projekt, több intézmény/közlekedés/adó), `ecosim_projects_20261030.json` (TEST Z historikus 272 hatás), `EcoSim_P2_9_muvelet_dontesi_guard_20261105.json` (9 egyszeri művelet).
- **35/35 projektköltség egyezés; 29/29 faktor; 272/272 hatásrekord megőrizve, ebből 242 közvetlen, 30 nem közvetlen.**
- **P1 és P2 indexforgatókönyv-alap képleti visszaszámítása PASS**, UI 2 tizedre egyezik.
- A futó projektek előjeles fenntartása **−65 800**, a pénzügyi híd differenciája **1 ECU**.
- **4 × feltételes keret; mindegyiknél megengedett, egy-két értelmes alternatíva; 8/8 célzott offline egységteszt PASS.**
- Nem validált: aktuális P2 projekthatás-százalékok teljes készlete, 30 közvetett hatás, elindítás tényleges kapuja, egyedi projektváltozatok élő hatása, támogatások tényleges elszámolása, P3–P5 városi átmeneti pálya, versenytársi döntések, mentési garancia.
- Nem történt `Start`, `Mentés`, hitel, API write, git push vagy változtatás más fejlesztési lane-en.

**Teljes projektstátusz:** `PARTIAL` – offline pénzügyi/projekthatás integráció `COMPLETED`; 35/35 költség, 29/29 tényező, 272/272 historikus hatás és 8/8 ellenőrzési teszt. Teljes funkcionális készültség **UNKNOWN**, integrált *élő játék* E2E készültség **UNKNOWN**, éles P2–P5 döntési készültség **UNKNOWN**, Δ százalékpont **UNKNOWN**, mert nincs a teljes ötéves projekt képességeire vonatkozó reprodukálható mérési nevező. Az offline adatutat a tesztek bizonyítják, **nem** a játékbeli végrehajtást.
