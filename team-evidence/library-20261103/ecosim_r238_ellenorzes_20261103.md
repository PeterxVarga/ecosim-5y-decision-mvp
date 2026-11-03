# EcoSim R238 – feltöltött adatcsomag ellenőrzése

**Állapot: PARTIAL – az adatcsomag integritása megfelelő, a teljes P1 adatlefedettség nem igazolt.**

- ZIP-ellenőrzés: PASS; fő JSON SHA-256 = `078882198dfa74f2d33453daba272c255d652a5021953022cb68dfc69778dce2`.
- A nyugtában szereplő SHA-256 egyezik a ZIP-ben található JSON-nal. Az eredeti 14 forrásfájl nincs csatolva, ezért az adatok eredeti forrásazonossága külön nem ellenőrizhető.
- Forrásazonosító: I. piac, 1/5. periódus, X-Challenge 2026 selejtező.

## Ellenőrzött struktúra

| Adatkör | Eredmény |
|---|---:|
| Excel címkézett sorok | 374 |
| Saját csapat numerikus P0 Excel-sorai | 324 |
| Csapatok | 7 |
| Projektkártyák | 35 |
| Korábban futó projekt státusz | 6 |
| P0 tény / P1 terv városi faktorok | 29 |
| Megváltozott faktorok | 24 |
| Főmenük rögzített aktív nézetei | 10 |
| Azonosított alnézetválasztó címkék | 27 (nem mind rögzített) |
| Döntési mezők | 23 |
| Egyértelmű Excel–UI P0 párosítások | 19 |
| Hitelesített teljes min–max pár | 0 |
| Hitelesített mentett P1 döntés | 0 |
| Kalibrált szakpolitikai hatás | 0 |

## Hiányzó adatok / döntési kapuk

- Missing contents of alternate subviews; 27 selector labels do not equal 27 captured pages.
- Coherent current project catalog in the same time window as current P1 state.
- Server-verified project admission cap and spendable cash, including loan and grant constraints.
- Current legal and dynamic min/max for 23 decision controls and proof of saved P1 actions.
- Current market institution multiplier configuration and other hidden model parameters.
- Policy causal impacts on cash/city factors (P1 plan is not P1 fact).
- P2-P5 actual outcomes can only be observed in later periods.

## Lefedettség menüpontonként

| Menü | Megfigyelt nézet | További felismert választók |
|---|---|---|
| summary | Csak az aktív/alapnézet | – |
| projects | Csak az aktív/alapnézet | Gazdaságfejlesztés, Sport és Kultúra, Közlekedés, Környezet |
| institutions | Csak az aktív/alapnézet | Oktatás, Művelődés és sport, Egészségügy, Szolgáltató, Városi hivatal, Szociális intézmények |
| transport | Csak az aktív/alapnézet | Járművek, Közlekedési személyzet, Belsőégésű motoros buszok, Elektromos buszok |
| income | Csak az aktív/alapnézet | Szolgáltatások díjai, Adók, Állami törvények |
| population | Csak az aktív/alapnézet | Lakosság száma, Foglalkozás, kereset, Egyéb adatok |
| corporations | Csak az aktív/alapnézet | Kisvállalkozások, Közepes méretű vállalkozások, Nagyvállalkozások |
| loans | Csak az aktív/alapnézet | Hosszú távú hitelek, Rövidlejáratú hitelek |
| finance | Csak az aktív/alapnézet | Cash flow, Vagyoni kimutatás |
| analysis | Csak az aktív/alapnézet | – |

## Eredmény és következő lépés

Az adatcsomag használható a korábbi források deduplikált elemzéséhez és a hiányzó oldalak azonosításához, **de nem bizonyít teljes ötéves optimalizálási vagy játékbeli döntési készültséget**.
A ZIP-ben található Codex-diagnosztika szerint a böngésző host akkor nem volt elérhető. Ez múltbeli diagnosztika; a jelenlegi host-állapotot ebből nem lehet megállapítani.

Nincs új játékírás, merge vagy deployment. A csomag tartalmát nem továbbítjuk GitHubra.