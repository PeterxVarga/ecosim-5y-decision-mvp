# R167 – Rövidlejáratú hitelek, csak olvasó megfigyelés

**Forrás:** [EcoSim Loans](https://edu.ecosim.hu/simulation/loans) → Rövidlejáratú hitelek, bejelentkezett böngészőben kiolvasott, nem csonkolt látható DOM; megfigyelés: `2026-10-31T19:16:42.237Z`.

**Állapot:** X-Challenge 2026 **Tesztforduló**, Z piac, „Jutalom a nap végén”, 1/1 periódus. A p0 tény és a p1 terv; nem két egymást követő lezárt periódus. Nem bizonyítja az éles verseny paramétereit.

## Megfigyelt szöveg

> Automatikus kerül felvételre, amennyiben a város pénzügyi helyzete negatív. A rövidlejáratú hitelek kamata magasabb, mint a hosszúlejáratúaké.

## Látható adatok

| Típus | p0 tény | p1 terv |
|---|---:|---:|
| Rövidlejáratú hitel | 0 ECU | 0 ECU |
| Rövidlejáratú kamat, % | 12 | 12 |

A korábbi, külön R164-es megfigyelés szerint a **hosszú lejáratú hitel kamata 7,5%** volt (p0 és p1). Így a két képernyőn megjelenített kamatláb különbsége **4,5 százalékpont**. A hosszú lejáratú nézetet ebben az R167 olvasásban nem nyitottuk újra.

A pénzügyi R165-pillantkép mindkét rövidlejáratú hitelsorában 0 szerepel (kamat és visszafizetés), ami összhangban van a nulla megjelenített hitelállománnyal. Ez **nem** bizonyítja, hogy egy negatív jövőbeli egyenleg nem vált ki automatikus hitelt.

## Amit még nem tudunk

- Az „a város pénzügyi helyzete negatív” feltétel pontos képlete, ellenőrzési időpontja és a tartalékkezelés kapcsolata.
- Hitelfelvételi korlát, tényleges futamidő és visszafizetési/újrafinanszírozási szabály.
- A hosszú hitelhez viszonyított választási jogosultság és az éves kamat számítási időzítése a rövid lejáratú hitelnél.
- Az aktuális, éles ötéves verseny paraméterei és a p1 tartalék felhasználhatósága.

**Következtetés:** a szimuláció a negatív pénzügyi állapothoz automatikus, 12%-os kamatot mutató rövid hitel felvételét kapcsolja. A modellnek ezt **finanszírozási kockázatként** kell megjelenítenie, nem biztosan elérhető, korlátlan forrásként. A cash-stressz eredmény változatlanul hipotetikus, amíg az aktiválási szabály nem hitelesített. **Game action gate: STOP.**

Az R162 motor és a GitHub `main` ág változatlan. Adatfájl: [`R167_SHORT_TERM_LOANS_READONLY.json`](./R167_SHORT_TERM_LOANS_READONLY.json).
