# EcoSim X-Challenge 2026 – P1, a maradék információk célzott auditja

**Vizsgálat dátuma:** 2026. november 3.  
**Csapat:** Jutalom a nap végén · **Piac:** I · **Időszak:** 1/5.  
**Mód:** kizárólag meglévő, korábban engedélyezett R238–R245 felvételek, hivatalos versenyoldal, játékkézikönyv és archivált kliensforrás ellenőrzése. **Nem történt játékírás.**

## 1. Biztosan rendelkezésre áll

| Terület | Bizonyított információ | Korlát |
|---|---|---|
| Projektek | 35 aktuális kártya, 140/140 pénzügyi adat egyezik | Projektindexre gyakorolt pontos, teljes hatás nincs kalibrálva |
| Indítás | 4 új projekt/virtuális év a hivatalos videóban | A korábbi kliens esetleges projekt1-es kivételére nem építünk |
| Projektállapot | 6 fut; 27 aktív Start; 30. Bubi és 31. P+R előfeltétel miatt tiltott | Mentett P1-indítás nincs külön bizonyítva; az ellenőrzött felületen 0 új P1-start látszott |
| Döntési tér | 57 látható szerkeszthető mező 14 alnézeten | Nem azonos a teljes, esetleg rejtett szerveroldali döntéssémával |
| Pontozás | 26 versenyszempont / 6 kategória; a játékban 29 tényezősor | Részmutatók súlya, a sport–művelődés összevonásának képlete nem ismert |
| Kategóriasúlyok | Gazdaság 25%, környezet 20%, kormányzás 15%, életkörülmények 15%, mobilitás 10%, emberek 15% | Kategórián belüli súlyozás nem következik ezekből |
| Aktuális index | P0 51,96 → P1-terv 52,48; hat súlyozott kategória hozzájárulása +0,5175 | Nem azonos egy kiválasztott adó-, bér- vagy projektváltoztatás okozati hatásával |
| Pénzügyek | P1-terv bevétel 5 562 335, hitel-/tartalékmozgás nélküli kiadás 4 511 224, tervezett pénzegyenleg 1 051 111 ECU | A pénzegyenleg nem bizonyított szabad projektkeret |
| Hitelek | Rövid 12%; hosszú 7,5%; automatikus rövidhitel, ha a város pénzügyi helyzete negatív | Az automatikus hitel maximuma és teljes ponthatása nem ismert |
| Eladósodás | A hosszúhitel-képernyő szerint a túlzott eladósodást a rendszer bünteti; kamat év végi hitelállomány után; egy periódusban felvétel VAGY törlesztés | Büntetési képlet és adósságküszöb nem ismert |
| Mentés | Külön mentési művelet; az utolsó sikeresen mentett döntés számít | Nincs független mentési nyugta vagy mentett döntés-visszaolvasás; státusz UNKNOWN |
| Versenystratégia | R242/R244: 8 korábbi, feltételes ötéves projektútvonal | Nem igazolt globális optimum, győzelmi valószínűség vagy riválisreakció |

## 2. Újonnan feltárt, részlegesen számszerűsíthető korlátok

A korábban archivált és SHA-256-tal rögzített **`840.41fdc8e1.chunk.js`** klienskódban az intézményi nyitási/zárási mezőkhöz az `1 − előző időszaki intézményszám`, a közlekedési felvételi mezőkhöz a `− előző időszak végi létszám` alsó korlátképlete szerepel. A mostani P1 nézetek értékeivel behelyettesítve:

| Döntés | Megfigyelt P0 bázis | Régi kliensképletből adódó alsó változás |
|---|---:|---:|
| Középiskolák nyitás/zárás | 7 | −6 |
| Általános iskolák nyitás/zárás | 13 | −12 |
| Óvodák nyitás/zárás | 16 | −15 |
| Bölcsődék nyitás/zárás | 10 | −9 |
| Sportlétesítmények nyitás/zárás | 7 | −6 |
| Kulturális intézmények nyitás/zárás | 5 | −4 |
| Orvosi rendelők nyitás/zárás | 18 | −17 |
| Szociális otthonok nyitás/zárás | 8 | −7 |
| Buszvezetők felvétele/elbocsátása | 255 | −255 |
| Szerelők felvétele/elbocsátása | 24 | −24 |
| Közlekedési irodai dolgozók felvétele/elbocsátása | 391 | −391 |

**Bizonyítékszint:** archivált kliensképlet + aktuális P1 felületen megfigyelt bázis; **nem** teljes, érvényes szerveroldali min–max pár. Egyik sorhoz sem igazolt felső korlát, és a jelenlegi szerver-elfogadás sem lett próbával vizsgálva. Az R235-ben az első négy korlát már korábban szerepelt; a következő hét a mostani célzott összevetésből került elő.

Az állami törvény P1-ben a **közalkalmazotti minimálbért 350 ECU-ban** mutatja. A régi kliens intézményi bérek minimumát állami törvényi függvényből veszi, de a jelenlegi szerver elfogadási tartománya ettől nem bizonyított teljesen. A képzési, fejlesztési, környezeti és támogatási mezőknél több helyen előző évi érték × piacfüggő minimum-/maximum-szorzó képlet látható, azonban a konkrét **piaci szorzók továbbra is hiányoznak**.

## 3. Valóban egyeztethető részmodellek – nem csak korrelációk

**Lakossági létszámegyenlet:**

- P0: 75 028 + 875 születés − 1 024 halálozás + 420 migráció = **75 299 lakos**.
- P1-terv: 75 299 + 875 születés − 1 044 halálozás + 420 migráció = **75 550 lakos**.

**Állami népességalapú támogatás:** az előző időszaki lakosságszám alapján egyezik a kijelzett összeggel.

- P0: 75 028 × 8 = **600 224 ECU**.
- P1-terv: 75 299 × 9 = **677 691 ECU**.

**A változatlan mező is lehet nem nulla akció:** a közlekedési irodai dolgozóknál a felvételi érték P0-ban és P1-ben egyaránt **+1**; emiatt a létszám 391-ről 392-re, a bértömeg 172 040-ről 172 480 ECU-ra és a képzési összeg 9 775-ről 9 800 ECU-ra változik. Ez **+465 ECU** egyéves megfigyelt bér- és képzésiköltség-különbség. Nem bizonyítja, hogy a mentett P1-akció ugyanilyen, és nem bizonyít indexhatást.

**Célzott források a Fedora-gépen:**

`~/Downloads/ecosim-r241-altviews-private-20261103/R241_14_institutions_default_or_refresh.txt`, `R241_15_institutions_culture_and_sports.txt`, `R241_16_institutions_healthcare.txt`, `R241_19_institutions_social_institutions.txt`, `R241_21_transport_transport_staff.txt`, `R241_32_transport_mechanics.txt`, `R241_33_transport_office_workers.txt`, `R241_24_population_default_or_refresh.txt`, `R241_08_income_state_laws.txt`, `R241_04_loans_default_or_refresh.txt`.

### A jelenleg látható négy helyi adó és hat szolgáltatási díj

Az **R241 bevételi alnézeteinek** ténylegesen kijelzett P0- és P1-beviteli értékei – nem külön mentett határozatok:

| Mező | P0 és látható P1-célérték |
|---|---:|
| Iparűzési / vállalkozási adó | 2% |
| Gépjárműadó | 1,9% |
| Kommunális adó | 1,1% |
| Építményadó | 0,5% |
| Tömegközlekedési díj / fő | 12,4 ECU |
| Temetkezési díj / fő | 32,2 ECU |
| Parkolási éves díj / hely | 3,8 ECU |
| Kommunális szolgáltatási díj / fő | 8,5 ECU |
| Víz-, csatorna- és távhődíj / fő | 33,2 ECU |
| Önkormányzati bérlakás díja / fő | 45 ECU |

A képernyő szerint az adók a lakossági és vállalkozási vonzerőt is befolyásolják, a szolgáltatási díjak pedig bevételt adnak, de terhet rónak a lakosokra és vállalkozásokra. **A pontos érzékenységi együtthatók és a szerveres adómaximumok továbbra is ismeretlenek.** Az, hogy a P0- és P1-ráták egyeznek, nem jelenti azt, hogy a későbbi adóbevétel azonos: a vállalkozási adó kijelzett bevétele 401 330-ról 402 640 ECU-ra, a gépjárműadóé 57 803-ról 59 087 ECU-ra változik.

## 4. Még hiányzó, valóban nem megszerezhető tények

| Adat | Miért hiányzik? | Teendő |
|---|---|---|
| Aktuális, teljes szerveroldali min–max határ mind az 57 mezőre | Az aktuális konfiguráció nem érhető el a korábbi R156-forrásban, nem látható az A11y pillanatképekben; a régi JS csak képleteket tartalmaz | Jogosult, olvasható konfiguráció vagy kifejezett admin/szervezői szabályigazolás |
| Utolsó sikeresen mentett P1-döntéscsomag | Öt friss R245 oldalmegnyitásban sem szerepelt mentési nyugta; a Save gomb megléte nem bizonyít mentést | Sikeres mentési nyugta vagy jogosult mentettállapot-visszaolvasás |
| 57 periodikus változtatás hatása a 26 versenyszempontokra | Nincs kontrollált beavatkozás és ellenőrzött eredmény, a P0/P1 egyezésből nem becsülhető | Elkülönített, engedélyezett próbakör vagy hiteles képletek/szerverhatásadatok |
| A 26 részmutató belső súlyai és a kategórián belüli képlet | A hivatalos weboldal csak szempontcímeket és kategóriákat közöl | Hivatalos modell vagy megfelelő szerverkonfiguráció |
| Túlzott adósság büntetési küszöbe, automatikus hitel felső határa | A játék csak általános büntetést és hitelkamatot mutat | Adminisztrátori szabályigazolás; nem érdemes végtelen hitellel modellezni |
| Más csapatok P2–P5 döntése és költözési válasza | Jövőbeli, még meg nem történt események | Robust forgatókönyv + újratervezés minden év lezárulta után |
| Bizonyítottan legjobb P1 kombinált projekt + periodikus döntés | A korábbi nyolc terv projekt-only mintavétel; hiányos teljes városi hatásmodell | Óvatos, feltételes P1 terv és külön jóváhagyott Save-visszaellenőrzés |

## 5. Időkritikus döntési keret

A hivatalos versenyoldal az éles szakaszt **2026. november 2–12.** közé, az egyes időszakokat két naposra jelöli. Az R241 felvételének visszaszámlálása alapján az első időszak vége **várhatóan 2026. november 3. 23:59 körül** van, de ez számított, nem külön hiteles szerverhatáridő.

**Biztonságos sorrend:** minden hozzáférhető, változtatás nélküli tényt összerakni → a már elfogadott **4 új projekt/év** korláttal feltételes P1 ajánlást választani → ellenőrizni az összes periodikus bevitelt, különösen a **nem nulla ismétlődő akciókat** → csak a tulajdonos külön jóváhagyása után menteni → a Save sikerét és a tényleges P1 döntésállapotot bizonyítani.

A teljes, bizonyított nyerő ötéves modell **nem kész**. A jelenlegi döntési állapot **UNKNOWN**. A jelentés elkészítése nem jelenti azt, hogy az élő játékban mentés vagy projektindítás történt.

**Forráshivatkozás:** EcoSim belső R241/R245 felvételei és korábban archivált JS; hivatalos versenyoldal: https://www.xchallenge.hu/ ; hivatalos SmartCity tájékoztató: https://edu.ecosim.hu/smartcity .