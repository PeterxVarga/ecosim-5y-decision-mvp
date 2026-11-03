# EcoSim R196 – teljes városi bizonyítéklefedettség (R195 fölötti, csak olvasó ellenőrzés)

**Nem új optimalizáló.** Az R162–R195 eredeti stratégiai motor változatlan. Az R196 kis, önálló döntésellenőrzője a kétterves `TRADEOFF.json` mellé tesz egy géppel ellenőrizhető, tíz EcoSim-fülre kiterjedő fedezettségi jelentést.

## Pontosan mit nyújt?

- Összefoglalás, Projektek, Városi intézmények, Közösségi közlekedés, Bevételek, Lakossági adatok, Vállalkozások, Hitelek, Pénzügyek, Elemzés: mind külön sor és rögzített szükséges megfigyelési témák.
- Az operátor által rögzített aktuális megfigyelés csak ugyanolyan módra, forrásállapot-hashre, projektkatalógus-hashre és **az adott R195 eredmény konkrét SHA-256 hashére** köthető.
- Aktuális megfigyeléseknél legfeljebb 48 órás, időzónás időbélyeg; ismeretlen és hiányos mezőknél `HOLD`. Nincs bejelentkezés, scraping, hálózat, szimulációs írás.
- **Teljes operátori adatfedettség esetén sem ad éles végrehajtási engedélyt.** A projekt-, adó-, díj-, intézmény-, lakossági-, vállalkozási-, hitel- és közlekedési döntések szerver által igazolt, közös jövőbeli állapotváltozás-modellje hiányzik.

## Hol tartunk a részmodellekkel?

Az eredeti R162 már tartalmaz R145 `joint_5y` policy-track újrarendezést, R153–R154 négy adó részmodellt, R155 hat díj és részleges intézményi bér-/anyagköltség modellt, valamint R158–R159 időzítés-stresszmodelleket. Ezek csak **megadott, explicit, gyakran szintetikus feltételezéseken** működnek, nem bizonyítják a teljes pénzügyi cash flow-t. Az R195 `run_tradeoff.sh` **ezeket a részmodelleket nem futtatja**, így a 0,451337/0,432832 értékek projektmodell-pontok, nem teljes városstratégiai pontok.

## Használat a mostani, már sikeres Fedora R195 futásoddal

A `team-handoff/r196-city-review/tools/city_review_r196.py` fájlt a legújabb fejlesztési munkafából hívd a meglévő történeti nyugtán:

```bash
python3 team-handoff/r196-city-review/tools/city_review_r196.py \
  --tradeoff /tmp/ecosim-r195-tradeoff-2qiKmOEe/TRADEOFF.json \
  --out-json /tmp/ecosim-r196-city-review.json \
  --out-md /tmp/ecosim-r196-city-review.md
```

Ez a történeti példában **`HISTORICAL_PROJECT_MODEL_ONLY`** státuszt ad és 10 fül ellenőrzési listáját, nem hamis „live kész” jelzést.

Az éles operátori bizonyítékfájl **opcionális** `--city-evidence FILE.json`, ahol a `schema` `ECOSIM_R196_OPERATOR_CITY_VIEWS_V1`. A gépi ellenőrzés megköveteli mind a 10 kulcsot, `status=MISSING` vagy `status=OPERATOR_OBSERVED` státuszt, az utóbbinál `source_view`, `source_evidence_id`, időbélyeg és az adott fül `observed_topics` listáját. A szükséges témakulcsokat a `REQUIRED_TOPICS` konstans dokumentálja. A fájl összes identitás-hashét a konkrét `TRADEOFF.json` és a futási állapot azonosítóira kell állítani, nem szabad fiktíven kitölteni.

Következő *nagy ROI-jú* lépés: friss, ténylegesen megfigyelt füladatok és a hitel/folyósítás/fiskális szabályok után az eredeti R149–R159 policy-track számítások bekötése ugyanabba a csapat- és időszak-azonosított döntési dossziéba. Enélkül egy önmagában sikeres R195 **nem** elegendő városgazdálkodási döntési jóváhagyásra.

**Korlát:** az R196 nem olvassa ki az EcoSim-et, nem számít új döntést, nem alakítja át az R195 pontértékeit. `GAME_ACTION_GATE=STOP`.

## Kvalifikáció

`python3 -m unittest discover -s team-handoff/r196-city-review/tests -v` – 26 szigorú, offline ellenőrzés. Az eredeti teljes R162–R195 natív teszt külön kvalifikációt kapott; az R196 egyelőre PR-ban ellenőrzendő, nem élesített változtatás.
