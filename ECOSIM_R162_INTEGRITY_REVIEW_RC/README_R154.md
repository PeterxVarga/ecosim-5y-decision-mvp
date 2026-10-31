# EcoSim R154 – Forrásalapú négyadó-bevétel és feltételes pénz–index Pareto

## Cél, bizonyíték, falszifikáció

Az R153 belső ötéves döntési MVP egyetlen motorját bővíti. **Nincs új optimalizáló.** Az R153 már ismerte a vállalkozóbarátság közvetlen kliensoldali adó/díj képletét, de nem tudta az adóbevételi oldal négy közvetlen részét számszerűen visszaszámolni. Az R154 a régi `decision_desk_r149.py` → `run_evidence_pipeline_r152.py` → `decision_view_r149.py` adatútba kötött, szigorú feltételes bevételszámítóval és új háromtengelyes, mintabeli Pareto-jelentéssel egészíti ki.

**Elsődleges helyi forrás:** a már korábban archivált `840.41fdc8e1.chunk.js` Webpack-modul 5168; `Bi`, `_i`, `Ui`, `Yi` kliensoldali függvények. A forrásfájl SHA-256-ja és mind a négy függvény pontos UTF-8 bájttartománya/hash-e az `evidence/R154_TAX_REVENUE_FORMULA_ANCHORS.json` fájlban szerepel. A nagy, eredeti JS-bundle-t nem másoljuk ebbe a kiadásba.

### Integrált, forrásalapú képletek

- Iparűzési adó = üzleti adóalap × adókulcs százalékban / 100.
- Gépjárműadó = járműszám-index × gépjárműadó összeg × `max(0, 1 − adó×érzékenység/indexosztó)` × lakosság / 1000.
- Kommunális adó = kommunális adóösszeg × lakóegységek × `max(0, 1 − adó×érzékenység/indexosztó)`.
- Építményadó = építményadó-összeg × lakóegységek × `max(0, 1 − adó×érzékenység/indexosztó)`.

Minden évhez kötelező külön megadni a vállalati adóalapot, járműindexet, népességet, lakóegységeket és kommunális adóösszeget, továbbá mindhárom szükséges piaci bevételérzékenységet és osztót. **Ezeket nem találjuk ki, és a képlet nem tudja előrejelezni, hogyan változnak az adódöntések hatására.** A példában expliciten SZINTETIKUSAK. Ha hiányoznak, a bevétel nem számítható. A számítás négy adócsatornára terjed ki, nem az összes városi bevételre.

### Működő, ugyanazon döntési adatút

`inputs/mvp_run.r154_synthetic.json` ugyanazt az R149/R153 konfigurációt használja, egyetlen új opcionális `tax_revenue_scenarios_path` mezővel. Az `inputs/tax_revenue_r154.synthetic.json` részletes öt évre vonatkozó, **nem hivatalos** adóalap-forgatókönyv. A rendszer minden R153 adópályához kiszámolja mind a négy adót külön és együtt, éves és ötéves különbséggel, majd **a már megtalált 15 projektterv × 3 adópálya** 45 összevetéséből háromdimenziós, mintabeli Pareto-frontot állít elő: közvetlen részleges SmartCity-indexproxy (nő), négyadó-bevétel-változás (nő), öt év konzervatív projektteher (csökken). Ez a keresés eredményeit *utólag* értékeli, nem módosítja a kereső heurisztikáját.

A demonstrációs eredmények: elsőéves négyadó-alap **454 368,608 ECU**; 5 év alatt a változatlan adópálya különbsége **0**, a vállalkozási adó csökkentése **−920 000 ECU**, emelése **+920 000 ECU** közvetlen négyadó-bevételi delta; **45 összehasonlított kombináció, 21 mintabeli nem dominált**. Ezen számok egyike sem valós EcoSim-pénzügyi előrejelzés vagy azonnal elkölthető összeg. A mintából nem következik, hogy egy magasabb adókulcs valóban magasabb ötéves költségvetést vagy indexet eredményez, mert a vállalkozási alap és a migráció megváltozhat.

### Egyetlen parancs a későbbi Fedora-ellenőrzéshez – jelenleg nem szükséges

```bash
cd ECOSIM_R154_SOURCE_TAX_REVENUE_MVP
./run_r154_offline.sh
./qualify_once.sh
sha256sum -c SHA256SUMS
```

A teljes történeti mintakimenet már megvan a `results/R154_EVIDENCE_TO_FOUR_TAX_DECISION/` mappában; `DECISION_DESK.html` internet nélkül nyitható. A `R154_SOURCE_TAX_REVENUE_COUNTERFACTUAL.json` és `R154_THREE_AXIS_CONDITIONAL_PARETO.json` szintén ott található. Nincs böngésző-/EcoSim-művelet. Minden játékbeli kapu **STOP**.

### Kockázati és elfogadási határ

- Éles futásban a szintetikus bevételi adóalap megtagadva; `CURRENT_SNAPSHOT_REVIEW` esetében csak explicit `OPERATOR_DECLARED_READONLY_HYPOTHESIS` forrásosztály engedhető meg, és az sem független hitelesítés.
- A bevételi forgatókönyv nem pótolja a projektkiadási keretet, nem növeli a kereső által feltételezett finanszírozást, és nem keveredik a teljes cash flow-ba. Anti-duplikációs deklaráció szükséges.
- Adószabályok kliensoldali képleteit sikerült reprodukálni; szerveroldali elszámolás, valós évközi adóalap-változás, hitel, intézmények és migráció **NINCS VALIDÁLVA**.
- A korábbi 421 ellenőrzés dokumentált, de nem fut újra; az R153 46 régi regressziós ellenőrzése újra lefutott és PASS; az R154 69 új ellenőrzése PASS. A megelőző 421 nem válik új tesztté, és az összes 536 ellenőrzés nem bizonyítja az ötéves játékpontosságot.

**Következő kritikus lépés:** aktuális market/team adatok és valóban egymáshoz illő, megfigyelt döntés–előnézet vagy terv–tény párok a szerver által számolt adóalap, vállalkozásszám, intézményi állapot és cash flow kalibrálásához. A tesztforduló p0 tény és p1 terv nem valid, tényleges éves állapotátmenet.
