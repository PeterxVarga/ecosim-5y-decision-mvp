# EcoSim R156 — Read-Only Market/Team Acquisition Bridge

**Döntés: az R155 belső, ötéves offline MVP folytatása; nem második optimalizáló.**

## Kiinduló megállapítás

- A 2026. október 30-i R94 **tesztforduló** adatai megvannak: 29 kijelzett faktor, kijelzett index, 35 projektstátusz, R94 pénzügyi sorok, történeti súlyok.
- A jelenlegi EcoSim **bejelentkezett** `market/team` állapotához ebből a ChatGPT-beszélgetésből nem volt hozzáférés. A Browser kapcsolat nem tudott az eredeti bejelentkezett böngészőablakhoz kapcsolódni; a külön böngészős profilban nincs rögzített EcoSim-bejelentkezés.
- Az **éles** projektlimit, indexsúlyok, városállapot, valóban szabad pénzügyi keret, kamatok, feloldási szabályok, szabályosan megfigyelt EcoSim-előnézet és későbbi FACT nincs megszerezve. Az R156 **nem állítja, hogy megszerezte** ezeket.
- Az X-Challenge nyilvános oldala tájékoztat a döntési típusokról, de nem tartalmazza a csapatspecifikus `market/team` állapotot.

## Új R156 funkciók

1. **`capture/R156_OFFLINE_CAPTURE.html`** — telefonon/laptopon is megnyitható, internetkapcsolatot nem használó **helyi, csak olvasó** adatbeviteli oldal; nincs fetch, külső szkript, cookie-/session-hozzáférés, EcoSim-művelet. Üres faktor- és projektstátusz-sablonokból JSON exportot készít. **Nem böngészi automatikusan az EcoSimet.**
2. **`tools/readonly_intake_r156.py`** — az explicit, felhasználó által rögzített JSON-ból előállítja az **eredeti R152** `manifest.json`, `factors.csv`, `projects.csv`, `parameters.json` fájlokat. Az eredeti R152 normalizáló és R149 állapotellenőrző minden lényeges szabálya továbbra is fut. A csomag egyszer írható, SHA-256 nyugtázott, és semmit nem ír vissza a játékba.
3. **Forrás-, jogosultsági és adatbiztonsági elhatárolás** — hiányzó szerverbizonyítékból nem lesz fiktív projektlimit/keret; `CURRENT_READONLY` esetén forrásazonosító szükséges a faktor- és projektstátuszhoz, a megadott cap/weights értékhez. Tiltottak a session/token/cookie-szerű bemenetek és az ismeretlen paraméterkulcsok. A jövő évi `confirmed_spendable_cash` nem állítható hitelesen egy aktuális UI-megfigyelésből.
4. **Egyetlen meglévő R152→R155 döntési folyamat** — ha egy későbbi aktuális export **és külön, megfelelő R149 konfiguráció** elérhető, a CLI a korábbi `run_evidence_pipeline_r152.execute()` függvényen keresztül indítja a keresőt. Az aktuális futásból kizárja a történeti/szintetikus R153–R155 policy-, tax- és operating fájlokat. A játékbeli kapu mindig `STOP`.
5. **`tools/qualify_r156.py`** — 68 új pozitív, negatív és integrációs check, benne egy valódi (historikus) 15-jelöltes R155 végponttól végpontig futás. A korábbi R155 99 és R153–R154 115 checks megőrzött kvalifikációja nem lett ismételten futtatva.

## Terminál nélküli használat (később, ha hozzáférsz az EcoSimhez)

A `capture/R156_OFFLINE_CAPTURE.html` fájlt nyisd meg a böngésződben. Írd be/copy-paste-eld az **azonos periódusú és ugyanabból a PLAN vagy FACT oszlopból származó, hivatalosan megjelenített** 29 faktort és az indexet, a 35 projekt státuszát, valamint az igazolható market/team paramétereket és a forrásnézetek azonosítóit. A letöltött `ecosim-r156-readonly-capture.json` fájlt csatolhatod később ehhez a chathez. **Sem terminál, sem Codex nem kell a helyi JSON elkészítéséhez.**

Fontos: a legbiztonságosabb következő lépés egy **felhasználó által engedélyezett, bejelentkezett, csak olvasó böngészőkapcsolat**. Ehhez a felhasználó egyszeri, külön hozzájárulása és a belépés szükséges. A HTML nem jelenti azt, hogy az aktuális adatok automatikusan rendelkezésre állnak.

**Ne adj meg** login-azonosítót, jelszót, tokent, cookie-t, HAR-t, teljes hálózati választ vagy privát személyes adatokat. A forrásadatot lehetőség szerint hivatalos exportból/megtekintett UI-ból másold, és őrizd meg a képernyőnézet nevét és az időpontot. Projektkártya megnyitása **akár állapotváltozással járhat**, ezért a működés nem automatizál nem biztonságosan visszafordítható UI-interakciót.

## Fejlesztői offline használat (most már lefuttatott történeti demo)

```bash
./run_r156_historical_offline.sh
./qualify_once.sh
sha256sum -c SHA256SUMS
```

A `results/R156_HISTORICAL_FULL_DEMO/` tartalmazza a kész történeti E2E döntési fájlokat. Az aktuális JSON-t a fenti Python module `--export ... --out-dir ...` kapcsolókkal lehet majd átalakítani és ellenőrizni. `--decision-config ...` esetén a meglévő R149/R155 motor fut, **nem** egy új kereső. Az éles konfiguráció hiányzó projektlimitje és indexsúlya nem pótolható R94-csel.

## Érvényességi határ

- A JSON a felhasználó által másolt offline bemenet, **nem hitelesített szerverállapot**.
- `CURRENT_READONLY` sem jelenti, hogy a szerver ellenőrzött; csak a capture szándékát rögzíti.
- A másolt 29 faktor alapján történő indexegyezés aritmetikai konzisztencia, nem előrejelzési pontosság.
- R94 p0 FACT és p1 PLAN **nem** lezárt évek közötti visszamérés.
- Ötéves stratégiai helyezést és biztos finanszírozhatóságot ebből nem lehet igazolni.
- Ez a teljes chunk offline, **0 EcoSim-írás**. **Játékbeli döntési kapu: STOP.**
