# R152 — Integrált, bizonyítékhoz kötött döntési MVP

**Implementáció:** elkészült. **Codex és játékbeli művelet:** 0. **Egyetlen heurisztikus ötéves mintafuttatás:** 1. **Eredmény:** 15 történeti, feltételes stratégia. **Tényleges, hitelesített éles nyerő stratégia:** nincs.

### Elfogadási feltétel

A korábbi R151 meglévő keresője egy jogszerűen offline mentett, táblás adatcsomagból előállított normalizált állapotot és forráshash-nyugtát kapjon; az eredményben legyen összehasonlítható ötéves döntési dosszié, kifejezett bizonyítékhiányok és `gameplay_gate=STOP`. A nem igazolható aktuális állapot esetén ne keletkezzék aktuálisnak feltüntetett jelölt.

### Ellenőrzött jelenlegi teljesítés

- 2026-10-30-i R94 historikus faktor-, projekt- és pénzügyi export összekapcsolva.
- 52,48 vs 52,483733; 113 pénzügyi sor, p1 nettó 865 588 ECU (nem költhető keret), 6 korábban futó projekt.
- 15 **feltételes** ötéves terv a meglévő motorral.
- **44 új PASS**, előző **377 PASS megőrizve**; a 421 összesített ellenőrzés **nem** 421 újrafuttatott teszt.
- Szándékosan hibás, 35 projektnél hiányos, NaN, duplikált, történeti/aktuális adatkeverés, eltérő súly, symlink és könyvtárból kilépő bemenet elutasítva.
- Nem történt független EcoSim-szerverhitelesítés, UI-interakció, Codex vagy külső hívás.

**Következő legnagyobb külső bizonyíték:** engedélyezett, aktuális market/team információ, projektállapot, azonos periódusú faktor- és pénzügyi terv, előre rögzített becslés majd későbbi ténysor; nem újabb általános keresőfunkció.
