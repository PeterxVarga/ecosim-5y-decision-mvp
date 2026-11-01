# EcoSim R189/R190 — csapatos átadás (offline, csak olvasás)

**Állapot:** R189 árnyékkereső / R190 történeti 35-kártyás összehasonlítás. Nem merge-elt, nem élesben validált; GAME_ACTION_GATE=STOP.

## Mire jó?

- Meglévő R162 ötéves tervben **a már kiválasztott projektek indítási évét** rendezi át korlátozott számú lépésben.
- Végig az eredeti R162/R157 modell szerinti pontozást és az eredeti R160 független auditot hívja.
- Ismeretlen szabálynál, feltételes projektjogosultságnál, rossz Git PIN-nél és felülírási veszélynél leáll.
- Nem indít projektet, nem lép be az EcoSimbe, nem ír a forrásmunkafába. A hipotetikus költségkeret **nem** elkölthető pénz.

## Teszt és futtatás

1. A csapattag klónozza ezt a **privát** repositoryt, és váltson a `work/ecosim-r190-team-handoff-20261101` ágra. GitHub olvasási jog szükséges.
2. A projekt gyökerében hozzon létre külön tiszta, **detach** worktree-t a kanonikus R162 PIN-en:

```bash
git worktree add --detach ../ecosim-r162-pinned 9d2d17d822bb97a210151e269454a0432a1952ae
python3 -B -m unittest discover -s team-handoff/r189-r190/tests -v
```

3. Futtassa az **offline, történeti, feltételezett** 100 000 ECU-s példát (a kimeneti útvonal ne létezzen előre):

```bash
python3 -B team-handoff/r189-r190/tools/run_r162_shadow.py \
  --repo-root ../ecosim-r162-pinned/ECOSIM_R162_INTEGRITY_REVIEW_RC \
  --state team-handoff/r189-r190/examples/historical_test_state.json \
  --annual-budget 100000 --cap 4 \
  --out /tmp/ecosim-r189-shadow-100k.json
```

Futtatás előtt ellenőrizze, hogy a megadott kimeneti fájl még nem létezik. Ha a natív R162/R160 első futtatásán HOLD jelentkezik, az auditálás helyes működését jelzi; ne írja felül kézzel.

## Bizonyíték és korlátok

- Az R189 19/19 eredeti strukturális tesztje és az R190 6/6 kiegészítő ellenőrzése helyben PASS (2026-11-01). A fenti 19 unittest bekerült a commitba.
- R190: 35 valódi **tesztfordulós** projektkártyán, 20 korábbi R157 mintatervből választva, 50k/100k/150k hipotetikus éves keretnél +0,026934 / +0,012159 / +0,037022 feltételes modell-indexpontot mértünk a kétprojekt-es átrendezés független JS újrajátszásával.
- A teljes **natív R162 Python + R160 Python E2E nem volt futtatható** az eredeti projekt tiszta checkoutja nélkül. Ne kezeljétek ezt az ágat igazolt éles optimalizálóként.
- Nincs bizonyított ötödik évi EcoSim-pontszám, globális optimum, éles projektlimit, támogatási időzítés vagy elkölthető keret.
- A tesztfordulós baseline-t az éles kvalifikációhoz tilos automatikusan újrahasznosítani.

## Forrásrögzítés

`PeterxVarga/ecosim-5y-decision-mvp` @ `9d2d17d822bb97a210151e269454a0432a1952ae`. Az R189 két Python modult az R190 csomagból emeltük át. A `main` R162 motor változatlan.

**Döntési kapu:** csak operátor által áttekintett javaslat, semmilyen játékbeli mentés vagy véglegesítés nem engedélyezett.
