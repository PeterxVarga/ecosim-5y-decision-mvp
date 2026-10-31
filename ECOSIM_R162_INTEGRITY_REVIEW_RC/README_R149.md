# EcoSim R149 — Offline Decision Desk MVP (integrált az R148-ba)

**Cél:** egy teljes, belső, csak olvasó döntéselőkészítési ciklus egyetlen paranccsal: forrásbemenet → kapuk → 1–5. év projektkeresése több deklarált ECU-keretre → alternatívák összevetése → szintetikus/hipotetikus operating-policy szcenáriók → passzív történeti egyeztetés → jelentés és konkrét következő bizonyítéklista.

## Mi működik már?

- A korábbi `tools/strategy_5y.py`, `joint_5y.py`, `annual_transition_r148.py` és kapcsolódó modulok maradnak az **egyetlen** projektkereső és faktor-számítási tulajdonosok. Az R149 nem épít párhuzamos optimalizálót.
- `tools/decision_desk_r149.py`: több, külön megjelölt hipotetikus pénzügyi keretet ellenőriz; ismételt jelölteket deduplikál; *minden megtalált* jelölt ötéves kiadását összeveti minden kerettel; külön jelzi a szcenárióként megadott működési hatásokat, a mérés nélküli részleges indexet és a hiányzó pénzügyi bizonyítékot.
- `tools/intake_r149.py`: felhasználó által rendelkezésre bocsátott, **engedélyezett read-only** faktor-pillanatkép adatát beolvassa; képes a kijelzett indexet visszaszámolni, de **nem** igazolja, hogy a megadott pillanatkép tényleg élő szerveradat. A hiányzó limitet, kamatot, pénzt és projektállapotot nem tölti ki becsléssel.
- `HISTORICAL_ILLUSTRATION`: az R94 tesztfordulós adatokból demonstrál. `CURRENT_SNAPSHOT_REVIEW`: jelenlegi forrásbizonyíték hiányakor **meg sem indítja a keresést**, a döntés STOP. A megfelelő formájú, még nem hitelesített bemenet mellett is csak feltételes jelöltet ad, nem server által igazolt megoldást.
- Opcionálisan a meglévő `paired_calibration_r147.py` és `readiness.py` modulokkal azonos periódusú PLAN-párokat és csak olvasott liga-pillanatképeket is fogad. Ezeket nem állítja be ötéves előrejelzési pontosságnak vagy bizonyított továbbjutásnak.
- Kimenet: `DECISION_DESK.json` (géppel feldolgozható), `DECISION_DESK.md` (magyar döntési jelentés), `INPUT_HASHES.json` (helyi bemenetek SHA-256 jegyzéke).

## Előkészített eredmények (nem kell most futtatni)

A `results/R149_MVP_DEMO` mappa már tartalmazza a 3 hipotetikus éves kerettel és az R94 történeti p1 tervvel készített mintakimenetet. **Nem éles eredmény, nem valós keret, nem teljes EcoSim-pontszám.**

## Opcionális későbbi helyi futtatás

```bash
cd ECOSIM_R149_OFFLINE_DECISION_MVP
./run_mvp.sh --config inputs/mvp_run.illustrative.json --out-dir results/own_exploration
./qualify_once.sh
```

Egy új, megengedett **aktuális** pillanatkép használatakor:

1. Másold a `inputs/capture_current.template.json` mintát, cseréld a történeti számokat az aktuális, engedélyezett olvasási adatokra; add hozzá a valódi forrásbizonyítékot, az aktuális csapat/piac/periódus mezőket és az elérhető `market`/`team` mezőket. Ne használj session cookie-t, tokent, személyes azonosítót.
2. `python3 -I -B tools/intake_r149.py --capture ... --out-state inputs/your_state.json --out-check results/your_intake_check.json`
3. Készíts saját másolatot a `inputs/mvp_run.current.template.json` fájlból. A `state_path` a létrehozott state-re mutasson, az `annual_envelopes` *kifejezetten hipotetikus, megindokolt* kereteket tartalmazzon. `./run_mvp.sh --config ... --out-dir ...`

Ha az aktuális adatokból nem ismerjük a projektlimit és a projektállapot mezőket, a current-mode **nem keres**. Sem hitelkeretet, sem játékon belüli GO-t nem következtet a p1 nettó eredményből. Az azonos periódusú, engedélyezett előnézeti összehasonlítás később külön, tulajdonosi engedélyezés és visszaállíthatóság mellett vizsgálható. Az R149 önmaga nem végez ilyen beavatkozást.

## Pontosság és korlátok

Az offline ellenőrzés csak a kód konzisztenciáját ellenőrzi. A modellből **hiányzik a hiteles szerveroldali éves állapotváltozás, az adó/díj/intézményi hatásfüggvények egy része, a vállalati és migrációs dinamika, a versenytársak döntései és a validált pénzügyi hitelkeret**. A heurisztikus kereső nem garantál globális optimumot. Az érzékenységi szélsőértékek **nem** probabilisztikus megbízhatósági intervallumok. A `SOURCE`/`USER` eredetjelzés csak *átadott* bizonyíték, nem független hitelesítési mechanizmus.

**Biztonsági állapot:** offline, nincs böngésző, hálózat, Codex, jogosultságkezelés és EcoSim-írás. Minden kimenet `gameplay_gate: STOP`.
