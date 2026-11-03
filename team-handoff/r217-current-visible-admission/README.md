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

## R220: all four category views genuinely observed (2026-11-02)

In the SAME logged-in Selejtező, Market I, P1 UI, the user switched four
Project categories. The authorized read-only browser connector returned each
active category's visible HTML/text, saved PRIVATE on Fedora as
`projects_economy.txt`, `projects_sport.txt`, `projects_transport.txt`,
`projects_environment.txt` with visible source URL, source class, identity,
and a view label. Existing R217 summary and immutable R156 state retained.

`qualify_all_views_r220.py` reuses the original R217 card parser and
the original pinned R162 35-project dataset. It requires, in each of four views,
exact sequential project IDs (1–14; 15–24; 25–31; 32–35), same named cards,
exact displayed four financial values, same visible effect metric/% pairs,
and current UI Start/Fut state equal to the current Summary's p0/p1 state.
It also rechecks SHA hashes of all five R217 previously acquired page inputs.

The private result `~/Downloads/ecosim-r220-all-35-current-source-20261102/R220_RECEIPT.json`
proves **35/35 current visible card financial + displayed effect parity** and
six running projects 14,22,23,24,34,35. Original two card reports are still
not substitutes for current source. The existing R217 captured 14/35; R220
uses the four private pages to prove complete *visible-field coverage*.

**Critical HOLD remains unchanged:** The UI does not evidence the full R192
project_conditions arrays or a formally verified market project start cap.
The finance page's p1 reserve/earnings are NOT admitted as spendable funds.
R192's full current card definition admission, R191 project-cap admission,
and R214 finance/decision issuance are all **HOLD**; no automatic gameplay.
No browser page bodies, account data, cookies, or R220 receipts enter Git.

Reproduce with private sources already on Fedora:

```bash
env R220_PRIVATE_PAGES="$HOME/Downloads/ecosim-r217-live-readonly-20261102" \
    R220_R217_DIR="$HOME/Downloads/ecosim-r217-current-admission-20261102" \
    python3 -I -B team-handoff/r217-current-visible-admission/test_all_views_r220.py
```

The eight R220 tests include byte-determinism, fake status, altered name,
wrong active category, missing category, and output-overwrite refusal.

## R222 forráshelyességi pontosítás (2026-11-02)

Az R217 és R220 korábbi leírásában a projektfeltételek **nem megfigyeltként** szerepeltek, mert az eredeti, költségekre és hatásokra szűkített kártyaparser **nem olvasta ki** a látható `Projekt feltételek` szakaszt. Az eredeti négy, változatlan böngészős forrás újbóli elemzése megmutatta, hogy a 30. és 31. projektnél a feltételek **valóban meg vannak jelenítve**: Bubi ← Bicikliútfejlesztés fut; P+R ← Vasútfejlesztés fut. A másik 33 kártyán nem jelenik meg külön feltételblokk.

A konkrét forrásazonosítók és az eredeti R192 `_card` ellenőrzése a `team-handoff/r222-visible-conditions/` láncban találhatók. A négy megfigyelés viszont 103,55 percen át történt, ezért az R192 **egyórás** aktuális felvételi időkapuja továbbra is **HOLD**. A jelenlegi Market I projektlimit és elkölthető cash továbbra is UNKNOWN; nem indítottunk játékműveletet.
