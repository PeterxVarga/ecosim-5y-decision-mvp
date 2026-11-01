# R193 – Magyarul megfogalmazott EcoSim-döntési javaslat

**Feladat:** a meglévő R162 → R189 → R191/R192 modellező és szabályellenőrző lánc kimenetéhez közvetlenül kapcsolni egy ember számára olvasható magyar döntési magyarázatot. Ne külön AI-alkalmazást vagy új keresőt építsünk.

## Az eredmény mit mond a csapatnak?

- **Most, az aktuális évben mely projekteket érdemes együttesen megfontolni?** Teljes projektnév és projektazonosító; a már kiválasztott projektek egyértelmű megkülönböztetése.
- **Miért kerültek bele?** A projektkártyák kedvezőként modellezett, számszerű hatásai, emellett a kedvezőtlen hatások; a közvetlen indexmodellből kimaradó hatások külön jelölése. Nem állítjuk, hogy ez az egyedi projekt okozta a teljes célfüggvénybeli nyereséget.
- **Mennyibe kerül?** Indítás + beruházás és a már futó/új projektek pozitív éves fenntartási költsége, az éves vizsgálati kerethez viszonyítva. A partnertámogatások NINCSENEK levonva a finanszírozási igényből.
- **Mi legyen a következő években?** Évenként teljes névvel felsorolt javasolt projektek, tömör hatásmagyarázat, költségigény, függőségek és releváns negatív hatások.
- **Mihez képest jobb?** Az R189 által kapott eredmény kiinduló ötéves tervhez képest mért minmax proxy-index különbsége, **nem** valós SmartCity-index-előrejelzés, és nem egyetlen projekt hozzájárulása.
- **Mikor lehet kattintani?** A szöveg nem ad automatikus vagy felhatalmazó játékműveletet. Az azonos évre javasolt projektek nem jelentenek igazolt kattintási sorrendet. `GAME_ACTION_GATE=STOP`.

## Kapcsolódás: automatikusan az R191 kimenetében

A `tools/run_r191_shadow.py` teljes siker után, de a kimenet kiírása előtt a `human_explanation_hu` kulcsba illeszti az `ECOSIM_R193_HUMAN_DECISION_EXPLANATION_V1` JSON-objektumot; ennek `markdown` mezője a teljes magyar jelentés. A futtató a kész jelentést **a terminálra is kiírja**, tehát a csapatnak nem kell külön generálót futtatnia. A géppel olvasható R191 JSON változatlan többi mezővel rendelkezik.

A modul tisztán lokális Python, nem hív EcoSimet vagy távoli AI-szolgáltatást, nem módosítja a játékot és nem változtatja meg a keresési algoritmust. **Ha az R160 audit, az R191/R192 aktuális adatkapu, a projektfüggőség, az éves keret vagy a `STOP` jelzés nem megfelelő, a magyar javaslatot NEM állítja elő.**

```bash
python3 -B -m unittest discover -s tests -v
```

A `tests/test_r193.py` 25 új, adatvezérelt tesztet tartalmaz; a R191/R192 örökölt 48 szerződéstesztet szintén futtatjuk (helyettesítő modulokkal). Ez **nem natív R162/R160 Git-checkoutos E2E**: a teljes éles javaslathoz továbbra szükség van tiszta forrásfuttatásra és az aktuális versenyadatokra.

## A külön mellékelt példa

`examples/R190_historical_50k_minta.md` az R190 korábbi **történeti** tervének, az eredeti kártyákon látható adatoknak az emberi nyelvű bemutatása. A példa manuális szemléltetés: nem natív R191 által kiadott auditnyugta, nem jogosít játékbeli kattintásra.

**Státusz:** `PASS_LOCAL_REGRESSIONS; NATIVE_R162_R160_E2E_HOLD; GAME_ACTION_GATE_STOP`.
