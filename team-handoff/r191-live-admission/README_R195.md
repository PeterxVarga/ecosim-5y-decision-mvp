# EcoSim R195 — két keret, egy natív döntési motor

**Cél:** az R194 főági, már történeti natív E2E-n átment rendszer újrafelhasználása két külön éves projektkerethez, majd magyar, ellenőrzött kompromisszum-jelentés. Nincs új optimalizáló, Python/JS indexátirat, hálózati kérés, játékbeli módosítás vagy AI-szövegalkotó.

**A számítási út ugyanaz:** R162 `search(..., objective='scenario_min')` → eredeti R160 audit → R189 ütemezésjavítás → R191/R192 adatkapu → R193 magyar javaslat → **R195 ugyanazon forrásból származó két nyugta összevetése**.

## Történeti natív, egyparancsos teszt

Frissítsd a fejlesztési ágat a saját, GitHub-hozzáféréssel rendelkező Fedora gépeden, majd a repo gyökeréből:

```bash
bash team-handoff/r191-live-admission/run_tradeoff.sh historical
```

Alapértelmezett hipotetikus korlátok: **100 000 ECU/év** (magasabb keretes modelljelölt) és **90 000 ECU/év** (tartalékos jelölt). Ezek nem igazoltan elkölthető források. A `--base-budget` és `--reserve-budget` opciókkal a két összeg módosítható; a tartalékos összegnek szigorúan kisebbnek kell lennie.

A szkript maga létrehozza a befagyasztott R162 forrás új, tiszta Git-worktree-jét, ellenőrzi az R189 közös forrás SHA-ját, az R162 release-integritást, az összes helyi regressziós tesztet, **kétszer ténylegesen futtatja az R162→R193 teljes Python-láncot**, végül a régi R162 natív kvalifikációját. Mindkét megoldásnak külön `PASS` R160 audit szükséges. A kimenetek a terminálon kijelzett `/tmp/ecosim-r195-tradeoff-*` mappában: `max_hungarian_hu.md`, `reserve_hungarian_hu.md`, `TRADEOFF_HU.md`, `TRADEOFF.json`, a két teljes R191 nyugta és ellenőrzési napló. A fordulóhoz nem csatlakozik, és semmilyen projektet nem indít.

## Aktuális, csak olvasó összehasonlítás

A valódi aktuális fordulós adatokat nem használhatjuk automatikusan a történeti tesztállományból. Ha rendelkezésre áll az R156 immutábilis export, a tényleges elsőéves pénzügyi megfigyelés és a 35 aktuális projektkártya, akkor:

```bash
bash team-handoff/r191-live-admission/run_tradeoff.sh current \
  --state /path/to/current_state.json \
  --r156-bundle /path/to/r156_immutable_bundle \
  --year1-finance /path/to/observed_finance.json \
  --current-card-catalog /path/to/observed_35_cards.json \
  --base-budget 100000 --reserve-budget 90000 --cap 4
```

Az itt szereplő összegek és a `4` **csak szintaktikai példák**; éles futtatáskor a felületen megfigyelt és ellenőrzött értékeket kell megadni. A jövőbeni 2–5. éves pénzügyi keretek *feltételezések*. A jelenlegi R191 időbélyeg-, finanszírozási, projektkártya-, R156- és forrásintegritás-kapuk változatlanok. Ismeretlen forrás, hiányzó feltétel, azonosíthatatlan költség vagy kedvezőtlen audit esetén `HOLD`.

## A jelentés értelmezése

- Két **külön korlátos keresés** eredményét hasonlítjuk össze. Nincs állítás globális optimumról, de a pontértékeket ugyanaz a modell és ugyanaz a kiinduló állapot állítja elő.
- A `TRADEOFF_HU.md` mind az öt évre (vagy aktuális periódustól a végéig) megadja a konkrét projekteket névvel, éves konzervatív költséget és a közös, magasabb kerethez viszonyított szabad mozgásteret.
- A magasabb keretes terv akár alacsonyabb modellszámot is adhat a korlátos keresés miatt. A jelentés a **tényleges** előjel alapján javasol, nem tulajdonít nem bizonyított előnyt.
- A támogatások nincsenek levonva; a jövőbeni városi visszacsatolás nincs empirikusan kalibrálva. A játék felülete és a valós finanszírozás külön ellenőrzést igényel.
- `GAME_ACTION_GATE=STOP` minden esetben. Az R195 önmagában nem live-ready igazolás.

## Kvalifikáció

- Helyi R194 + R195 tesztek: **112/112 PASS** (88 korábbi és 24 új R195).
- `bash -n run_tradeoff.sh`: PASS; a fordított két keret és a hiányos aktuális adatcsomag helyes `HOLD` ágon áll meg.
- **R195 új natív kétfuttatásos E2E: még nem történt meg** a Fedora gépen. Ez külön gate, nem örököljük automatikusan az R194 egyszeri natív PASS eredményét.
- R194 teljes eredeti natív történeti E2E: operator Fedora **PASS 2026-11-01**, dokumentált korábbi PR #2.

Ez az R195 fejlesztési csomag elkülönített PR-ban marad a natív kétfuttatásos bizonyítékig.
