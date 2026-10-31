# EcoSim — R143 Integrated Engine, szállítási összefoglaló

**2026-10-31. Cél: az R143 V2.1 meglévő munkájából egységes, offline, ötéves projektstratégiai motort készíteni.**

## Elkészült funkciók

1. A meglévő 35 kártyás tesztfordulós projektadatok újrahasználata; a projektlimit, költségek, támogatáscímkék és projektfüggőségek egy állapotgépben.
2. Ötéves projektindítási sorozatok keresése (korlátos beam search; nem bizonyított globális optimum); 4 projekt/év szóbeli feltételezés, `project1` előző évi feltételes extra lehetőséggel.
3. Éves konzervatív kártyaköltség, folyamatos pozitív fenntartás és külön jelzett nem garantált negatív fenntartás/támogatás. Pénzügyi és hiteljóváhagyás **nem** állítható elő.
4. R142 ismert SmartCity-hatás-proxy többéves, hipotetikus projekthatás-fennmaradással, 50%-os projekt-hatás és 85%-os éves fennmaradás érzékenységgel. A nem leképezett hatásokat tételesen felsorolja.
5. 50k/100k/200k ECU **feltételezett éves keretek** összevetése; nem igazolt pénzügyi keret.
6. Állapotból való újratervezés 2–5. évre, amikor új, igazolt kiinduló metrikák és futó projektek rendelkezésre állnak.
7. Liga-pontszám-pillanatképek csak olvasási kiértékelése, hiányos lista vagy holtverseny esetén nincs hitelesített helyezési állítás; korábban jóváhagyott és visszaállított megfigyelésekhez leíró előrejelzési hiba.
8. Egyetlen összevont kvalifikációs futtató, megismételhető JSON/Markdown eredmény, auditálható eredet és STOP státusz.

## Kritikus elhatárolás

**Nem készült valódi ötéves, teljes EcoSim-városszimulátor**, mert nincs hozzá elég bizonyított paraméter és állapotátmenet. A motor jelenleg **projektstratégiai alternatívákat** számol. Az adó-, díj-, kapacitás-, bér-, hitel- és migrációs döntések nem szerepelnek a számszerű jóslatban; a versenytársak döntéseiből fakadó eltérések sem. Az ötödik évre kiírt indexérték egy *változatlan bázisra épített kártyahatás-proxy*, nem játékbeli terv vagy tény.

A projekt-előfeltétel azonos éves teljesítésének kliensoldali lehetősége nem bizonyít szerveroldali elfogadást. A 2026. október 29-i megnyitón elhangzó 4/év és 12% csak szóbeli példa; a konkrét éles `market` értékei ismeretlenek. A tesztfordulós hat futó projektet tilos éles kezdőállapotnak tekinteni.

## Egyszeri használat

```bash
cd ECOSIM_R143_5Y_ENGINE
./run_offline_strategy.sh --budget-per-year 100000 --out results/own_hypothetical_run.json
```

A teljes leírás a `README.md` fájlban; az összevont teszt `./qualify_once.sh`. Semmilyen böngésző, Codex, API vagy hálózati kapcsolat nem kell. Az oldalon semmit nem indít vagy ment.

## Következő külső bizonyíték-kapuk

- **P0:** éles hivatalos konfiguráció és induló adatok, projektlimit, hitel és valóban költhető egyenleg.
- **P0:** teljes index- és pénzügyi állapotátmenet dokumentálása vagy biztonságos előnézeti kalibrálás, külön jóváhagyással.
- **P1:** gazdaságpolitikai, intézményi és demográfiai döntések kvantitatív leképezése, versenytársi bizonytalanság.
- **P1:** tényleges 5 éves többdöntéses optimalizálás és valós fordulós hibamérés.

A fejlesztési chunk **kész**; a tényleges nyerő stratégia **nem bizonyított**. Játékbeli GO: **STOP**.
