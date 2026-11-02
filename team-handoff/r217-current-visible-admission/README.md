# R217 – Selejtező I: élő, csak olvasható részleges R156 befogadás

## Elért képesség
Az engedélyezett Browser csatlakozón keresztül a bejelentkezett EcoSim UI öt látható oldalának szövegét külön, PRIVÁT Fedora-könyvtárban, URL- és SHA-azonosítókkal tároltuk. Semmit nem mentettünk vissza a játékba; nem nyertünk ki tokent, cookie-t vagy HAR-t.

- Az aktuális Összefoglaló oldal: p0 index 51,96, p1 PLAN index 52,48, a 29 p1 tényező, hat súly és mind a 35 projekt p0/p1 futási státusza.
- A hat futó projekt: 14, 22, 23, 24, 34, 35. Újonnan elindított projekt nincs.
- Projektek: a Gazdaságfejlesztés kategória 14/14 kártyájának megfigyelt pénzügyi és hatásadata egyezik a történeti definícióval. Projektfeltételeik és a további 21 kártya NEM hitelesített.
- Pénzügyek: p0/p1 nettó eredmény 962 785 / 1 051 111 ECU; nyitó pénzállomány 184 600 ECU. A p1 tartalék nem igazolt szabad keret.
- Hitelek: hosszú lejáratú kamat 7,5%, nulla állomány; hitelplafon és rövid lejáratú szabályok ismeretlenek.

Az eredeti R156 létrehozó és R152 normalizáló valóban lefutott: az aktuálisan megfigyelt 35 státusz és 29 tényező R156-kompatibilis, forráshash-elt, változtathatatlan privát adatcsomagban van. Az R191 CAP_UNKNOWN_OR_ASSUMED hibával helyesen blokkol. A projektindítási limitet nem vettük át a történeti tesztből.

## Privát futtatás
bash team-handoff/r217-current-visible-admission/qualify_private.sh

Önálló újrafuttatás csak új kimeneti könyvtárba: python3 -I -B team-handoff/r217-current-visible-admission/prepare_visible_r217.py --browser-text-dir "$HOME/Downloads/ecosim-r217-live-readonly-20261102" --out-dir "$HOME/Downloads/ecosim-r217-fresh-output"

Az R217 R156 adatcsomag, pénzügyi résznyugta, 35 projektstátusz és forráshash-ek a Fedora privát mappáiban maradnak. A GitHub csak generikus forráskódot, célzott tesztet és ezt a dokumentációt kapja.

## Következő kritikus hiány
Mind a 35 jelenlegi projektkártya (feltételekkel), a tényleges maxProjectPerTurn forrása, valamint a jelenleg elkölthető összeg és kötelezettségek külön megfigyelése. E nélkül az R214-hez nincs teljes engedélyezett bemenet. No game writes, no merge or deploy. GAME_ACTION_GATE=STOP.
