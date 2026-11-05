# EcoSim P2 — élő Brave–Codex ellenőrzés (2026-11-05)

**Eredet:** a felhasználó által megosztott Codex-futás kimenetéből változtatás nélkül kiemelt auditjelentés.
**Forrás futás:** Codex v0.166.0, session `01a1ab84-b845-7a63-835b-1218f61a9e45`; élő EcoSim P2 PLAN.
**Megjegyzés:** az eredeti `P2_BRAVE_READONLY_SNAPSHOT.md` csatolmány egy korábbi, blokkolt próbálkozás, NEM a sikeres audit; a sikeres futás helyi kimenete `P2_LIVE_READONLY_SNAPSHOT.md` néven készült.

---

**Státusz: PARTIAL.** A csapat, a piac és a periódus egyezett, ezért a tíz megadott főoldalt ugyanazon EcoSim-lapon végigolvastam. A P2-tervben továbbra is **60,52** az Okosváros-index és **868 143 ECU** a tartalékképzésre tervezett összeg. A projekttáblázatban **10 futó és 25 nem futó** projekt látható.

A teljes gyűjtéshez szükséges több alnézetet csak gombbal lehetne megnyitni, amit a megadott korlátok tiltanak. A teljes szöveges pillanatképek külön fájlba mentése sem történt meg: a környezet fájlrendszere csak olvasható. Az alábbi beszámoló ezért nem helyettesíti a kért teljes pillanatkép-archívumot.

**Ellenőrzési idő:** 2026. november 5., körülbelül 12:43 CET; az időt a gyűjtés végén ellenőriztem. Az egyes nézetekhez külön időbélyeg nem áll rendelkezésre. A forrás az adott sorban hivatkozott EcoSim-nézet. **VERIFIED** = a pillanatképen olvasható; **DERIVED** = abból számított; **UNKNOWN** = nem hozzáférhető vagy nem bizonyítható. A P2 mezők **PLAN**, a P1 oszlop **FACT**; a P2 terv mentettsége **UNKNOWN**.

## Azonosítás és lefedettség

| Követelmény | Eredmény | Minősítés |
|---|---|---|
| X-Challenge 2026 Selejtező; Jutalom a nap végén; I. piac; 2/5 periódus | Egyezik | VERIFIED · [Összefoglalás](https://edu.ecosim.hu/simulation/summary) |
| P1 tény és P2 terv | A felület külön oszlopként jelöli | VERIFIED |
| SmartCity-index, 6 kategória, 29 tényező | A táblázat olvasható | VERIFIED · [Összefoglalás](https://edu.ecosim.hu/simulation/summary) |
| 35 projekt státusza | Mind a 35 neve és P1/P2 státusza látható | VERIFIED · [Összefoglalás](https://edu.ecosim.hu/simulation/summary) |
| Mind a 35 projekt költsége és indítási feltétele | Az alapértelmezett gazdaságfejlesztési alnézetben 14 projekt részlete látható; a többi kategória külön gombos | PARTIAL · [Projektek](https://edu.ecosim.hu/simulation/projects) |
| Nyitó pénz, bevételek, kiadások, tartalék | Cash flow olvasható; a kiadások főösszege az alábbiakban számított | VERIFIED / DERIVED · [Pénzügyek](https://edu.ecosim.hu/simulation/finance) |
| Hitelállomány és feltételek | Hosszú lejáratú hitel látható; rövid lejárat részletei külön alnézetben | PARTIAL · [Hitelek](https://edu.ecosim.hu/simulation/loans) |
| Intézmények, dolgozók, bérek, képzés | Az oktatási alnézet látható; öt további intézményi alnézet hiányzik | PARTIAL · [Intézmények](https://edu.ecosim.hu/simulation/institutions) |
| Közlekedési járművek és személyzet | A belsőégésű buszok és infrastruktúra látható; elektromos busz és személyzet külön alnézet | PARTIAL · [Közlekedés](https://edu.ecosim.hu/simulation/transport) |
| Adók, díjak, támogatások | Díjak és pénzügyi bevételi sorok láthatók; adókulcsok és állami törvények alnézete hiányzik | PARTIAL · [Bevételek](https://edu.ecosim.hu/simulation/income), [Pénzügyek](https://edu.ecosim.hu/simulation/finance) |
| Minden döntési mező; egyszeri és ismétlődő műveletek | Csak a megnyitott alapnézetekben látható mezők | PARTIAL |
| Lakosság, vállalkozások, elemzés | A főoldalak megnyíltak; további alnézetek, illetve grafikonok részletei nem teljesek | PARTIAL · [Lakosság](https://edu.ecosim.hu/simulation/population), [Vállalkozások](https://edu.ecosim.hu/simulation/corporations), [Elemzés](https://edu.ecosim.hu/simulation/analysis) |
| Mentett kontra pusztán tervezett állapot | A felület P2-tervet mutat, de mentési bizonyíték nincs | UNKNOWN |

## SmartCity: hitelesített P1 és P2 értékek

Forrás: [Összefoglalás – SmartCity-index táblázat](https://edu.ecosim.hu/simulation/summary). **P1 FACT / P2 PLAN · VERIFIED.** Az értékek a felület szerinti indexértékek; ahol a sor százalékot vagy fajlagos mértéket nevez meg, azt külön jelzem.

| Kategória / tényező | P1 | P2 |
|---|---:|---:|
| **Gazdaság** | **69,65** | **74,36** |
| Fizetőképes piac | 74,12 | 81,4 |
| Vállalkozások száma | 50,51 | 59,85 |
| Vállalkozóbarátság | 56,17 | 56,17 |
| Foglalkoztatottság | 97,79 | 100 |
| **Környezet** | **51,2** | **49,89** |
| Fenntarthatóság | 54,43 | 51,33 |
| Vízgazdálkodás | 53 | 53 |
| Levegőminőség | 59,72 | 58,64 |
| Zöld területek aránya | 31,14 | 30,05 |
| Hulladékgazdálkodási helyzet | 57,71 | 56,44 |
| **Kormányzás** | **86,2** | **86,11** |
| Adminisztráció | 60,56 | 62,84 |
| Adósság / vagyon | 100 | 100 |
| Lakásgazdálkodás | 37,5 | 37,82 |
| Digitalizáció | 85,53 | 82,67 |
| **Életkörülmények** | **54,63** | **56,08** |
| Közbiztonság | 36,42 | 33,59 |
| Oktatási intézmények | 64,82 | 73,06 |
| Egészségügy | 48,04 | 46,76 |
| Szociális | 65,7 | 69,41 |
| Sport | 46,02 | 50,58 |
| Művelődés | 46,07 | 50,08 |
| Rossz szociális helyzetben lévők aránya | 20,67 | 25,72 |
| Átlagos lakásérték | 50,59 | 50,88 |
| **Mobilitás** | **54,83** | **58,39** |
| Településfejlettség | 57,12 | 64,87 |
| Közlekedési minőség | 72,5 | 78,38 |
| Tömegközlekedők aránya, % | 70,14 | 68,4 |
| Autók száma / 100 fő | 47,03 | 48,66 |
| **Emberek** | **30,72** | **31,91** |
| Lakossági viszonyok / elégedettség | 20,02 | 19,71 |
| Munkakörülmények | 49,53 | 49,73 |
| Lakosság képzettsége | 24,27 | 26,3 |
| Munkanélküli arány | 2,21 | 0 |
| **Okosváros-index** | **58,87** | **60,52** |

Az index súlyai: gazdaság **25%**, környezet **20%**, kormányzás **15%**, életkörülmények **15%**, mobilitás **10%**, emberek **15%**. A korábban megadott P1- és P2-index tehát egyezik a most látható értékkel. A P2–P1 különbség **+1,65 indexpont** — **DERIVED**, nem megvalósult eredmény.

## Projektek

Forrás: [Összefoglalás – projekt táblázat](https://edu.ecosim.hu/simulation/summary). **P1 FACT / P2 PLAN · VERIFIED.** A táblázat minden projektnél ugyanazt a státuszt mutatja P1-re és P2-re.

**Futó, 10 db:** Lakás- és helyiséggazdálkodás; Informatikai fejlesztés; Új ügyfélközpont; Operaház próbacentrum és műhelyház; Kosárlabdacsarnok; Velodrom; Vasútfejlesztés; Megújuló energia park; Robert Bosch campus bővítés; Richter Központ – Új vállalati székház.

**Nem futó, 25 db:** Szomszédsági Gazdaság Modell; Kereskedelmi és Kulturális Központ; Helyi élelmiszerellátás; Körforgásos gazdaság mintaprojekt; Vállalati Társadalmi Felelősség Platform; Gazdasági és Foglalkoztatási Együttműködés; HGF Innovációs Tudásközpont; Okos Gazdaság Alkalmazások; Közösségi Finanszírozási Rendszer; Innovációs Alap; Helyi Krízisalap; Pincerendszer hasznosítása; Nyitott Alkotó és Innovációs Terek; Pályaorientáció és Tehetséggondozás; Műemléki Dreher-villa új funkcióval; Multifunkcionális Sportcentrum; Képzési együttműködések koordinációja; Közlekedési Múzeum; Bosch Önvezető Jármű Tesztközpont; Reptér elérhetőség javítása; Új trolibuszútvonal; Bicikliútfejlesztés; Közösségi kerékpár szolgáltatás bővítés (Bubi); P+R parkolók a vasút mellett; A Népliget megújítása.

A [Projektek – gazdaságfejlesztés](https://edu.ecosim.hu/simulation/projects) nézetben az első 11 nem futó projektnél **Start** gomb látható; a 12–14. projektnél **Fut** szerepel. A gombok láthatósága önmagában nem bizonyítja az összes előfeltétel teljesülését. Az alábbi számok a felület pénzügyi sorai; a képernyőn a sorok mellett pénznem nem szerepelt, ezért itt az ECU **ASSUMPTION** a szimuláció pénzügyi kontextusa alapján.

| Projekt | Indítás | Fenntartás | Beruházás | Partnertámogatás |
|---|---:|---:|---:|---:|
| Szomszédsági Gazdaság Modell | 6 000 | 2 400 | 18 000 | 3 000 |
| Kereskedelmi és Kulturális Központ | 28 000 | 8 000 | 120 000 | 25 000 |
| Helyi élelmiszerellátás | 7 000 | 1 500 | 25 000 | 3 000 |
| Körforgásos gazdaság mintaprojekt | 8 000 | 2 000 | 33 000 | 14 000 |
| Vállalati Társadalmi Felelősség Platform | 3 000 | 2 000 | 2 000 | 15 000 |
| Gazdasági és Foglalkoztatási Együttműködés | 5 000 | 8 000 | 3 000 | 2 000 |
| HGF Innovációs Tudásközpont | 6 000 | 12 000 | 15 000 | 8 000 |
| Okos Gazdaság Alkalmazások | 4 000 | 3 000 | 22 000 | 3 500 |
| Közösségi Finanszírozási Rendszer | 2 500 | 1 500 | 6 500 | 12 000 |
| Innovációs Alap | 3 500 | 14 000 | 12 000 | 10 000 |
| Helyi Krízisalap | 3 000 | 5 000 | 18 000 | 8 000 |
| Lakás- és helyiséggazdálkodás | 8 000 | −12 000 | 75 000 | 5 000 |
| Informatikai fejlesztés | 12 000 | −8 800 | 43 000 | 0 |
| Új ügyfélközpont | 0 | 0 | 0 | 0 |

A fennmaradó **21 projekt költsége és indítási feltétele UNKNOWN**: másik projektkategória gombját kellett volna megnyitni. A negatív fenntartási sorokat a felület szerinti előjellel közlöm; azok pénzáramlásbeli elszámolása külön ellenőrzést igényel.

## Pénzügyek és hitel

Forrás: [Pénzügyek – Cash flow](https://edu.ecosim.hu/simulation/finance). **P1 FACT / P2 PLAN · VERIFIED**, ECU; a felület egészre kerekített számokat mutat.

| Tétel | P1 | P2 |
|---|---:|---:|
| Előző év végi pénzállomány | 184 600 | 309 280 |
| Bevételek összesen | 5 475 892 | 5 693 381 |
| Bérek közterhekkel | 2 078 659 | 2 157 225 |
| Dologi összesen | 2 421 952 | 2 390 014 |
| Egyéb működési kiadások | 666 000 | 278 000 |
| Kamat és hitel-visszafizetés | 0 | 0 |
| Tartalékképzésre | 309 280 | 868 143 |

A P2 felsorolt kiadási főcsoportjai **4 825 239 ECU**-t tesznek ki. **DERIVED:** 2 157 225 + 2 390 014 + 278 000 = 4 825 239; ez és a **868 143 ECU** tartalék együtt **5 693 382 ECU**, ami a megjelenített bevételt **1 ECU-val** meghaladja. Ez a kerekített sorokból eredhet — **ASSUMPTION**, a pontos háttérszámok nélkül nem bizonyítható. A korábban megadott P1 **309 280,31 ECU** értéket a mostani egészre kerekített **309 280 ECU** nem cáfolja, de a fillérpontosságot nem igazolja.

P2-ben a főbb bevételek: normatív állami hozzájárulás **1 711 013 ECU**, szolgáltatási díjak összesen **2 191 708 ECU**, adók **1 032 465 ECU**, fejlesztési célú állami támogatás **130 000 ECU**, vállalati fejlesztési támogatás **62 028 ECU**, járműeladás **26 739 ECU**. Ezek PLAN / VERIFIED értékek; a bevételi főösszeg tartalmazza a **309 280 ECU** előző év végi pénzállományt is.

A [Hitelek – hosszú távú](https://edu.ecosim.hu/simulation/loans) nézet szerint a P2 nyitó és záró hosszú távú hitelállomány **0 ECU**, a felvétel/visszafizetés döntési mező **0 ECU**, a kamat **7,5%**, a fizetendő kamat **0 ECU** — **PLAN / VERIFIED**. A leírás szerint egy periódusban vagy felvétel, vagy visszafizetés lehetséges; a túlzott eladósodást bünteti a rendszer. A rövid lejárat részletes feltételei **UNKNOWN**, bár a cash flow P2-ben rövid lejáratú hitelfelvételre és kamatra **0 ECU**-t mutat.

## Látható döntések és veszélyes áthozott mezők

Az alábbiak **P2 PLAN / VERIFIED** értékek; az egyes mezők mértékegységét csak ott nevezem meg, ahol a nézet azt megadja vagy a pénzügyi kontextus egyértelmű.

- **Iskolanyitás:** a középiskola „Nyitás / Zárás” mezője P1-ben **+1**, P2-ben ismét **+1**. A tervben az intézményszám **8-ról 9-re**, a dolgozók száma **552-ről 621 főre** változik. Ez újabb egyszeri nyitás lehet, nem pusztán a már megtörtént P1-nyitás emléke — **DERIVED** a megjelenített terv alapján. Forrás: [Intézmények – oktatás](https://edu.ecosim.hu/simulation/institutions).
- **Buszeladás:** a belsőégésű buszok beszerzés/eladás mezője P1-ben **−8**, P2-ben ismét **−8 db**. A terv **62-ről 54 db-ra** csökkenti az állományt, a kihasználtság **93,69%-ról 106,46%-ra** nő; az eladás értéke **26 739**. Ez ismétlődő egyszeri eladási kockázat — **DERIVED**. Forrás: [Közlekedés – belsőégésű buszok](https://edu.ecosim.hu/simulation/transport).
- **Oktatás további mezői:** bér **550**, képzés **14 400**, fejlesztés **60 000**; általános iskola, óvoda és bölcsőde nyitás/zárás egyaránt **0**. A mezők pénzneme és időegysége a pillanatképen nem volt külön feltüntetve. Forrás: [Intézmények – oktatás](https://edu.ecosim.hu/simulation/institutions).
- **Közlekedési ismétlődő mezők:** buszkarbantartás **192 500**, infrastruktúra-karbantartás **165 000**, kommunikáció **33 600**; a beszerzett buszok életkora **0 év**. A 500 km-es járathálózat tervezett infrastruktúra-minősége **72,5%**. A költségmezők mértékegysége a pillanatképen nem volt külön feltüntetve. Forrás: [Közlekedés](https://edu.ecosim.hu/simulation/transport).
- **Szolgáltatási díjak:** tömegközlekedés/fő **10,5**, temetkezés/fő **20**, éves parkolás/hely **10**, kommunális/fő **5**, víz–csatorna–távhő/fő **50**, bérlakás/fő **30**. Mind a hat P1-értékkel egyezik. Pénznemük a pillanatképen nem szerepelt. Forrás: [Bevételek – szolgáltatások díjai](https://edu.ecosim.hu/simulation/income).

A további intézményi, közlekedési személyzeti, adó- és egyéb alnézeti mezők, valamint a mentett állapot **UNKNOWN**. Így a fenti két kockázatos áthozott mező sem tekinthető a teljes lista bizonyítékának.

## Három következő ROI-lehetőség

Az összevetés **előzetes**, mert a projektköltség-sorok elszámolása, a támogatás feltétele, a mentett állapot és a teljes projektkészlet nem ismert. A hatások a felület által megadott százalékos változások; belőlük tényleges indexpont-hozam nem számítható megbízhatóan. Forrás: [Projektek – gazdaságfejlesztés](https://edu.ecosim.hu/simulation/projects).

| Lehetőség | Látható költség / támogatás | Látható hatás és korlát |
|---|---|---|
| **Vállalati Társadalmi Felelősség Platform** | Indítás 3 000; fenntartás 2 000; beruházás 2 000; támogatás 15 000 | Többek között adminisztráció +0,5%, oktatás +0,3%, képzettség +0,3%. A magas névleges támogatás kedvezőnek tűnik, de a nettósítás szabálya UNKNOWN. |
| **Közösségi Finanszírozási Rendszer** | Indítás 2 500; fenntartás 1 500; beruházás 6 500; támogatás 12 000 | Elégedettség +0,6%, digitalizáció +0,5%, szociális +0,3%. Alacsonyabb látható fenntartás; tényleges megtérülés UNKNOWN. |
| **Körforgásos gazdaság mintaprojekt** | Indítás 8 000; fenntartás 2 000; beruházás 33 000; támogatás 14 000 | Hulladékgazdálkodás +3%, fenntarthatóság +1,5%, levegőminőség +0,3%. A romló P2 környezeti tényezőket célozza, de nagyobb beruházást jelez. |

**Egyetlen legjobban indokolt következő lépés:** a P2 terv végrehajtása előtt ellenőrizni és tudatosan felülvizsgálni a **−8 buszeladás** és **+1 középiskola-nyitás** mezőt. Mindkettő megismétli a P1 egyszeri műveletét; a buszoknál a terv már **106,46% kihasználtságot** jelez. A gyűjtés során egyik mezőt sem módosítottam, projektet nem indítottam, és mentést nem végeztem.
