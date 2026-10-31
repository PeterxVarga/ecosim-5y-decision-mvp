# EcoSim X-Challenge 2026 — R143 videóbizonyíték és feladatfrissítés

Állapot: 2026-10-31. Kiegészítés, **nem új fejlesztési ág**. Forrás: [EcoSim — X-Challenge 2026 megnyitó](https://www.youtube.com/watch?v=3GNCkvECOdk), publikálva 2026-10-29; a 44:42 hosszú videó magyar automatikus feliratának célzott átnézése. A felirat hibái miatt a kritikus számokat az eredeti videón is ajánlott ellenőrizni. Nem történt játékbeli művelet.

## R143 előtti fontos, új bizonyítékok

| Idő | Elhangzott | Következmény | Erősség / még hiányzik |
|---|---|---|---|
| [21:08](https://www.youtube.com/watch?v=3GNCkvECOdk&t=1268s) | 4 projekt indítható virtuális évenként; 5 év alatt 20 | Alapfeltételezés a forgatókönyvkerethez: K_base=4 | Hivatalos szóbeli közlés; az éles `market.maxProjectPerTurn` és a `project1` +1 kivétel egyeztetendő |
| [21:57](https://www.youtube.com/watch?v=3GNCkvECOdk&t=1317s) | 12%-os kamat példaként a hitel kapcsán | Szenzitivitási vizsgálat és adósságkockázat | A pontos hitelfajta, tényleges ráták és plafonok ismeretlenek |
| [18:41](https://www.youtube.com/watch?v=3GNCkvECOdk&t=1121s) | Terv nem garantált tény; lakosok/cégek vándorolhatnak a régióban | Terv–tény eltérés modellezése; robusztus, ligaviszonyokra reagáló politika | A migráció mechanikája/paraméterei továbbra is ismeretlenek |
| [22:14](https://www.youtube.com/watch?v=3GNCkvECOdk&t=1334s) | Ligán belüli mutatók, projektek és döntések láthatók | Fordulónkénti versenytárs-megfigyelés és újratervezés (csak hivatalos UI/export) | Az éles hozzáférés/mezők később ellenőrizendők |
| [38:23](https://www.youtube.com/watch?v=3GNCkvECOdk&t=2303s) | A liga első két csapata továbbjut a középdöntőbe; harmadikoknál másodikhoz viszonyított relatív távolság számíthat | Cél: az ötödik év végén erős ligabeli helyezés és relatív rés, nem csak maximális nominális index | Pontos, végleges kvalifikációs szabályt hétfőre ígérték |
| [39:49](https://www.youtube.com/watch?v=3GNCkvECOdk&t=2389s) | Az ötödik év végén számít a helyezés; az első évek rangja nem dönt | Véghorizont-célfüggvény + gördülő éves újratervezés | Nincs hiteles ötéves ténygenerátor |
| [13:27](https://www.youtube.com/watch?v=3GNCkvECOdk&t=807s) | A sok nevező miatt középdöntős szakasz is lesz | A top 2 ligahelyezés nem azonos az élő döntőbe jutással | Középdöntő pontos lebonyolítása nyitott |
| [35:25](https://www.youtube.com/watch?v=3GNCkvECOdk&t=2125s) | Tét nélküli tesztben projekt-, adó- és kapacitásdöntésekkel javasolt kísérletezni | Kontrollált A/B kalibráció potenciálisan magas értékű | A felületi automatikus reset/mentés előbb tisztázandó; csak jóváhagyással |

## Jelenlegi R143 állapot (a 2026-10-31-én ellenőrzött helyi csomag)

- Elkészült az `ECOSIM_R143_5Y_CODEX.zip` bemeneti csomag és a projektköltségek demonstrációs ötéves naptára.
- **Nem érkezett vissza `ECOSIM_R143_5Y_REVIEW.zip`**; így a Codex általi teljes ötéves átmeneti/tényezőmodell nincs igazolva.
- 18/18 ismert JS, 35 projekt és a SmartCity-kézikönyv korábbi auditja rendelkezésre áll.
- Projektkártya-költségnaptár van; hiteles versenymodell nincs. P1 tesztadatokat nem szabad automatikusan éles adatoknak tekinteni.

## Mi kell még feltétlenül

1. **Éles `market/setup`**: az induló állapot, a tényleges cap, periódus, játék/ligaszabályok, hitelkamatok, kamatplafonok, támogatások folyósítása.
2. **Hiteles döntés-visszajelzés**: legalább néhány jól dokumentált tesztfordulós, egyváltozós A/B terv–index–cash-flow megfigyelés, kizárólag megengedett és igazoltan visszaállítható módon.
3. **Ötéves dinamikus modell**: projektütemezés + adók/díjak/intézménykapacitások/bérek/hitelek + perzisztencia, projektkésleltetés, pénzügyi korlátok; szerveroldali és versenytárs-hatások UNKNOWN maradnak, ahol nincsenek bizonyítékok.
4. **Liga döntéstámogatás**: az ötödik év végi várható index, a második helyhez mért rés, adósságkockázat, forgatókönyvek, évente frissíthető paraméterek. Ne állítsunk pontos kvalifikációs valószínűséget megalapozatlanul.
5. **Középdöntő/fair-play**: pontos és végleges kvalifikáció, a külső eszközök használatára vonatkozó versenyszabályzat külön tisztázása.

## Frissítés a Codex R143 feladatához

- Olvasd ezt a mellékletet a `CODEX_TASK.md` mellett; **ne kezelj szóbeli szabályt hardcoded szerverigazságként**.
- A 4/év és 12% legyen igazolásra váró input/scenario, ne kitöltött `actual_market` mező.
- A célfüggvényt egészítsd ki végső évre, ligabeli relatív helyezésre érzékeny értékelési felülettel, nem valószínűségi csodamodellel.
- Építs be terv–tény eltérés és migrációs kitettség nyilvántartási helyeket, és egy minimalista kísérleti/calibration log sémát.
- A `R142A STOP` marad: játékmódosítás/véglegesítés nélkül dolgozz; a per-year cost tool nem hiteles ötéves cash-flow- és indexszimulátor.
