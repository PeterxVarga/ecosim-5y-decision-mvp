# EcoSim R155 – forrásalapú szolgáltatási bevételek és intézményi részkiadások

## Cél és változás az R154-hez képest

Az R154 meglévő **egyetlen** R149→R152 döntési motorja és R153/R154 adómoduljai megmaradnak. Az R155 az eredeti, 2026-10-30 körül rögzített `840.41fdc8e1.chunk.js` kliensbeli Webpack 5168 modul **21 külön képletrészletét** integrálja a meglévő döntési munkafolyamatba. Nem készül új optimalizáló, nem történik szerveres EcoSim-kérés.

**Hat szolgáltatási bevételi csatorna:** temetkezési szolgáltatás (`Xi`), parkolás (`eo`), kommunális szolgáltatási díj (`to`), közüzemi/szolgáltatási díj (`ao`), bérlakásdíj (`no`), tömegközlekedési díj (`io`). A parkolási formula explicit, éves parkolási referenciaárat, árrugalmasságot, arányt és csillapítót használ. A bérlakás-képletben az eredeti `min(..., .99)` korlát megmarad.

**Intézményi részkiadások:** nyolc bérkomponens (`Vn`, `Wn`, `Hn`, `On`, `Bn`, `_n`, `Un`, `Yn`) és hét anyagköltség-komponens (`Zn`, `qn`, `Gn`, `$n`, `Kn`, `Jn`, `Xn`). A kultúra bértényezőjének forrás szerinti **sport** paraméterét szándékosan nem javítjuk át más képletté. A közlekedési bérek száma külön, explicit exogén bemenet; a képzés, tömegközlekedési anyag, hitelkamat, egyéb működési kiadás és fejlesztési költség **nem** része a mostani intézményi részösszegnek.

## End-to-end működés

`inputs/mvp_run.r155_synthetic.json` az R154 futás bővítése egy új, opcionális `operating_scenarios_path` mezővel. A `tools/operating_cash_r155.py` forráshoz kötött számításait **a meglévő** `decision_desk_r149.py` hívja. A történeti R94 csomagból készült 15 feltételes ötéves projektjelölt továbbra is ugyanabból a heurisztikus keresőből jön. Az R155 három, az R153 és R154 adópályáihoz kifejezetten azonosított szintetikus díj/staff pályát értékel. Az összesített **háromtengelyes, csak a mintában értelmezhető Pareto**: (i) részleges terminális indexproxy, (ii) négyadó-változás + hatdíj-változás − lefedett bér és anyag változása, (iii) konzervatív projektkártya-teher. A részleges nettó változás **nem szerepel** engedélyezett projektkeretként a keresőben, és nem alkot teljes városi cash flow-t.

A szintetikus példa ötéves eredménye (külső állapot minden pálya között azonos, **nem** EcoSim-előrejelzés):

| Adó- és működési pálya | Hat díjbevétel Δ ECU | Lefedett intézményi részkiadás Δ ECU | Részleges nettó működési Δ ECU |
|---|---:|---:|---:|
| Változatlan | 0 | 0 | 0 |
| Alacsonyabb adó/díj, több oktatási dolgozó | −102 234,71 | +16 800 | −119 034,71 |
| Magasabb adó/díj, több egészségügyi dolgozó | +100 813,61 | +28 815 | +71 998,61 |

Az utolsó táblázat **csak** a hatdíj–intézményi részágat mutatja. A négyadó-bevétel eltéréseit az egyesített Pareto külön hozzáadja; nem szabad a fentieket teljes költségvetésként értelmezni.

## Forrásbizonyíték és falszifikáció

`evidence/R155_OPERATING_FORMULA_ANCHORS.json`: minden képlethez forrásfájl SHA-256, UTF-8 bájttartomány, képletrészlet SHA-256 és Webpack modul ID. A jelenlegi build-környezetben a 21 részlet **mindegyike** byte-szinten egyezett a korábban archivált eredeti JS-sel. Az eredeti, teljes JavaScript fájlt ez a ZIP nem tartalmazza. Az R155 teszt, amennyiben a fenti korábbi JS nincs helyben, a 21 eredeti forráshash újramérését nem tudja megismételni; ilyenkor egyértelműen jelzi a helyi hiányt.

A vállalkozásszám kliensoldali rekurzióját az eredeti kódban azonosítottuk, de **nem integráltuk**: több piac- és csapatszintű lag, versenytárscsapat, a képlet időzítése és az éles `market/team` konfiguráció hiányzik. Nem állítunk mesterségesen zérus migrációt, keresletet vagy intézményi visszacsatolást. Az R94 tesztfordulós p0 tény és p1 terv nem megfigyelt évek közötti tényváltozás.

### Biztonsági kapuk

- Csak `SYNTHETIC_TEST_ONLY` vagy `OPERATOR_DECLARED_READONLY_HYPOTHESIS` forrásosztály engedélyezett; mindkettő **nem hitelesített**.
- Aktuális játékfelülvizsgálatban a szintetikus működési paraméter tiltott.
- Évenként kötelező, teljesen explicit külső városállapot, intézményi munkaerő, bértényező, anyagköltség-paraméter és parkolási árszenzitivitás; ezekből nem találunk ki éles értéket.
- Az R153 adópálya, R154 négyadó és R155 működési pálya azonosítói és forrásosztályai egyezzenek, vagy a folyamat álljon le.
- A projektkereső **nem** emeli meg a pénzügyi keretet a részleges adó- vagy szolgáltatási bevételből.
- Játékbeli művelet: **0**, tényleges ötéves predikció: **nem kalibrált**, végső döntési kapu: **STOP**.

## Használat később Fedora gépen (most nem szükséges)

```bash
cd ECOSIM_R155_SOURCE_OPERATING_CASH_MVP
./run_r155_offline.sh
./qualify_once.sh
sha256sum -c SHA256SUMS
```

Mintakimenetek: `results/R155_EVIDENCE_TO_OPERATING_DECISION/DECISION_DESK.html`, `DECISION_DESK.json`, `R155_SOURCE_OPERATING_COUNTERFACTUAL.json`, `R155_THREE_AXIS_OPERATING_PARETO.json`. A HTML hálózat és JavaScript nélkül megnyitható.

**Következő kritikus függőség:** a legfrissebb és tényleges `market/team` állapot, szolgáltatási és intézményi adatok, jogszerűen beszerzett modell-előnézeti vagy későbbi lezárt tények. Ezek nélkül a jelenlegi működési képletek feltételes, statikus részkomponensek, nem ötéves győzelmi prediktor.
