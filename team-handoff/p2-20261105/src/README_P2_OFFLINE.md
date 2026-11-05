# EcoSim P2 – közös, csak olvasó projekt- és pénzügyi modell

**Forrásidőpont:** 2026-11-05. **Játékbeli műveletek: 0.**

Ez a csomag a P2-ben megfigyelt SmartCity tényezőket, pénzügyi baseline-t, projektstátuszokat és mind a 35 projekt kártyaköltségét kapcsolja a 2026-10-30-i **TEST Z** hatáskatalógushoz. A projekt-hatásbecslés **nem** hitelesített P2-faktorváltozás és **nem** élő játék-előrejelzés.

## Újrafuttatás

Python 3.11+ szükséges, csak standard library:

```bash
python3 -m unittest -v test_joint_model.py
python3 p2_joint_screen.py
```

A második parancs a helyi `P2_joint_scenarios.json` fájlt írja újra, **nem kommunikál a játékkal**. Más hipotetikus projektkeretek:

```bash
python3 p2_joint_screen.py --budgets 50000,100000,200000,350000
```

A tesztek 35 projektkártya-költséget, 272 történeti hatást, a 29 faktor képleti újraszámítását, a -65 800 ECU fenntartási egyezést, a 1 ECU cash kerekítési eltérést, projektfüggőségeket és a feltételes portfóliókereteket ellenőrzik.

## Fájlok

- `P2_joined_input.json` – ellenőrzött P2 faktor/költség/status/pénzügyi baseline + historikus TEST Z hatásadat + kilenc ismételt művelet, forrás-SHA-k.
- `P2_joint_scenarios.json` – négy feltételes keret, nominális és ½–1½ hatásamplitúdóra érzékenységi rangsor, nem bizonyított előrejelzés.
- `p2_joint_screen.py` – offline közös cash/score forgatókönyv-kereső, max. négy új indítással.
- `r142_proxy_reference.py`, `effect_replay_r147.py` – a meglévő, felhasználói repo-ból újrahasznált történeti modellkód.
- `test_joint_model.py` – 8 célzott ellenőrzés.
- `EcoSim_P2_projekt_penzugyi_osszekapcsolas_20261105.md` – döntési eredmények és korlátok.
- `EcoSim_P2_kozos_projekt_penzugyi_modell_20261105.xlsx` – 6 lapos, képletekkel összekötött áttekintő munkafüzet.

**Hard STOP:** nincs live projektindítás, mentés, hitelfelvétel vagy P2–P5 forecast a feltételes indexproxyból. A pénzügyi szcenáriók nem igazolják a szabadon elkölthető összeget; a partneri támogatás időzítése és a 30 közvetett hatás UNKNOWN.
