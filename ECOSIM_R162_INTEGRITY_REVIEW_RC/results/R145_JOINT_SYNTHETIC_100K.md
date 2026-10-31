# R146 — Ötéves integrált, stresszelt projekt + várospolitika (feltételes)

**Játékbeli módosítás: 0. Eredmények: nem validált forgatókönyvek, nem döntési ajánlások.**

| Szcenárió | Forrás | Elsőéves projektindítás | 5. évi kombinált proxy Δ | Finanszírozási kapu |
|---|---|---|---:|---|
| test_no_new_policy | SYNTHETIC_TEST_ONLY | 13,17,20,27 | +1.3444 | STOP |
| synthetic_training_capacity | SYNTHETIC_TEST_ONLY | 9,13,17,27 | +1.3254 | STOP |
| synthetic_unknown_tax | SYNTHETIC_TEST_ONLY | 13,17,20,27 | +1.3444 | STOP |

## Értelmezési korlátok

- A felsorolt szintetikus hatások **nem EcoSim-szabályok**; csak a program tesztjére valók.
- A játék valós adó-, díj- és intézményi hatásfüggvénye **ismeretlen**. A modellezett nulladik pálya nem jelenti, hogy a valós hatás nulla.
- A modell nem igazolja a hitelfelvételi jogosultságot, a szabadon elkölthető keretet vagy a projektindítás szerveroldali elfogadását.
- A keresés korlátos beam heurisztika. Az előre rögzített működési forgatókönyvek között hasonlít, nem keresi meg az összes lehetséges adó- és intézményi döntést.
- A tesztfordulós történeti állapot nem éles, hitelesített kezdőállapot.

## Mi kell a következő kalibrációhoz?

Hivatalos, verziózott piac- és csapatállapot; a működési döntésmezők dokumentált tartományai; ellenőrizhető tervoszlop-változások; hitelek, projekttámogatások és migráció érvényes szabályai. A jóváhagyás és visszaállíthatóság tisztázása előtt nincs játékbeli A/B próba.
