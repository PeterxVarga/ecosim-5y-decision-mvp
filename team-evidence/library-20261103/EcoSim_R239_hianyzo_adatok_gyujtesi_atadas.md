# EcoSim – célzott R239 adatgyűjtési átadás

**Állapot:** a R238 SHA-256 egyezése igazolt; nem teljes adatfelvétel. **Nincs éles játékírás vagy optimalizálás.**

A jelenlegi ChatGPT böngészőkapcsolatból olvasható a nyitott *Szolgáltatások díjai* alnézet. A három táblázat és a hat input megfelel az R238 korábbi felvételének; az új, privát megfigyelés a Fedora-gépen maradt.

## Azonnali adatgyűjtési prioritások

| Prioritás | Nézet / adat | Teendő |
|---|---|---|
| P0 | **Pénzügyek → Vagyoni kimutatás**, Cash flow ellenőrzése | Lekötések, elkölthető források és tartalékok ellenőrzése |
| P0 | **Hitelek → Rövidlejáratú hitelek** | Hitelfeltételek és felvételi korlátok |
| P0 | **Bevételek → Állami törvények**, Adók frissítése | Jogszabályi és adókorlátok; P1 aktuális értékek |
| P0 | **Projektek → 4 kategória** | Friss 35 kártya, feltételek, állapotok lehetőleg egy összehangolt felvételben |
| P1 | **Városi intézmények → további alnézetek** | Oktatási szorzók, intézményi döntések, személyzet, fenntartás |
| P1 | **Közösségi közlekedés → elektromos buszok és személyzet** | Hiányzó költségek és döntési mezők |
| P2 | **Lakosság / Vállalkozások → második/harmadik alnézetek** | Független indikátor- és pénzügyi ellenőrzés |

## Megfigyelhető nézetválasztók – az R238 eredeti forrásából

- **projects**: Gazdaságfejlesztés, Sport és Kultúra, Közlekedés, Környezet
- **institutions**: Oktatás, Művelődés és sport, Egészségügy, Szolgáltató, Városi hivatal, Szociális intézmények
- **transport**: Járművek, Közlekedési személyzet, Belsőégésű motoros buszok, Elektromos buszok
- **income**: Szolgáltatások díjai, Adók, Állami törvények
- **population**: Lakosság száma, Foglalkozás, kereset, Egyéb adatok
- **corporations**: Kisvállalkozások, Közepes méretű vállalkozások, Nagyvállalkozások
- **loans**: Hosszú távú hitelek, Rövidlejáratú hitelek
- **finance**: Cash flow, Vagyoni kimutatás

## Biztonsági és bizonyítékhatárok

- **Csak kifejezetten engedélyezett böngészős olvasás.** Ha a hitelesített browser-origin engedélyt elutasítja a rendszer, nincs CDP-/cookie-/session-megkerülés.
- Tilos a **Mentés**, **Start**, hitelfelvétel, adóérték módosítása vagy egyéb játékbeli állapotírás.
- Minden nézet rögzítendő: időpont (UTC), csapat, piac, periódus, URL, alnézet, eredeti tartalom, SHA-256; a P0 és P1 külön szerepel.
- A régi **2026-10-30-i Tesztforduló, Z piac, 1/1** exportjai csak struktúramintának jók, nem a Selejtező I piacának tényadatai.
- A P1 alatti P2–P5 tényállapot nem gyűjthető be. A R238 eredeti privát JSON változatlan marad; az új forrásokat mellékletként kell hozzákapcsolni.

## Javasolt Work-munkakérés

> Használd a feltöltött R238 ZIP-et kanonikus forrásnak, és az R239 manifest alapján gyűjtsd be az EcoSim aktuális Selejtező, I. piac, 1/5. periódus hiányzó alnézeteit egy bejelentkezett, engedélyezett böngészőben. Csak megfigyelés; semmit ne állíts át, ne kattints Mentésre vagy Start gombra. Minden nézethez eredeti adat, időpont, SHA és hiánylistás visszaellenőrzés kell. Ne futtass optimalizálót, amíg a döntéshez szükséges adatok nem igazoltak.

**Ellenőrzött R238 SHA-256:** `078882198dfa74f2d33453daba272c255d652a5021953022cb68dfc69778dce2`