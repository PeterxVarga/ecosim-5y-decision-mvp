# EcoSim R148 — bizonyítékhatáros ötéves, évek között állapotot hordozó motor

**Kiadás:** 2026-10-31. **Játékbeli módosítás:** nincs. **Codex / felhasználói terminál:** nem szükséges a kapott eredmények megtekintéséhez.

## Az R147-hez képest ténylegesen hozzáadott képességek

1. **Egységes projekt + működési hatásréteg** (`tools/annual_transition_r148.py`): a relatív projekt-szorzók és a külön *felhasználó által megadott hipotetikus* működési szorzók egy faktorban összeszorzódnak, majd **egyetlen** forrásban igazolt felső/alsó korlátozás történik. Az R147 eltérő műveleti sorrendjét javítja. Nem állítja, hogy a működési szorzók tényleges EcoSim-szabályok.
2. **Rejtett telítettség láthatóvá tétele:** a korlátértéken kijelzett, de ismeretlen belső értéket az új motor külön jelzi; csak egy **feltételes telítettségi részintervallumot** számol. A teljes index bizonytalansága **nem korlátos**, mert maradnak ismeretlen közvetett hatások.
3. **Éves projektállapot-átvezetés:** az éveken át tovább futó projektek, az első évi beruházás és az éves (aláírt) kliensoldali fenntartási sor eltérő időzítésben szerepel. A konzervatív pénzigény a negatív fenntartást nem számítja szabad pénznek, és a partnertámogatást nem tekinti garantált készpénznek.
4. **Évek között hordozott hitelkomponensek:** a hosszú hitel ügyféloldali nyitó/felvétel/törlesztési korlát/záró/kamat számai, a rövid hitel következő évi visszafizetése és kamatterhe. Hitelplafont, jogosultságot és szerverelszámolást **nem** állítunk. Finanszírozási útvonal csak külön, teljes, kifejezetten hipotetikus pénzáram és átfedésmentességi nyilatkozat mellett számolható.
5. **Közös ötéves kereső:** a korábbi `strategy_5y.py` maradt a tulajdonos; az új bizonyítékhatáros éves naplót a jelölttervekhez kapcsolja. Az `R145–R147` operating-policy forgatókönyv keresőjében is az új, egységes faktor-számítás szerepel.
6. **Hivatalos adatok célzott kapuja:** `tools/readiness_r148.py` külön jelöli a tényleges jelenlegi projektlimit, korábbi projektállapot, faktorok/súlyok, kamatok, keretek és előnézet hiányát. A 2026. október 30-i **tesztfordulós** állapotot nem minősíti éles konfigurációnak.

## Meglévő, már előállított eredmények

- `results/R148_QUALIFICATION.json` — 173 örökölt + 58 új offline ellenőrzés = **231/231 PASS** az elkészítés idején.
- `results/R148_SOURCE_BOUNDED_100K_ILLUSTRATIVE.json` — hipotetikus 100 000 ECU/év keret, ötéves projektválasztás, részleges index- és pénzügyi komponensek, explicit STOP.
- `results/R148_OFFICIAL_INPUT_GATE.json` — konkrétan hiányzó bemenetek listája.
- `evidence/R148_FINANCE_SOURCE_ANCHORS.json` — 9 eredeti kliensoldali JS-hash + hely, a teljes programkód mellékelése nélkül. Ezek a **forrásbizonyítékok**, nem mérések egy futó játékról.

## Opcionális, későbbi offline újrafuttatás

```bash
cd ECOSIM_R148_5Y_ENGINE
./qualify_once.sh
python3 -I -B tools/readiness_r148.py --state inputs/official_state.template.json --out results/input_gate.json
python3 -I -B tools/strategy_5y.py --budget-per-year 100000 --out results/my_illustrative_strategy.json
```

Nincs internet, bejelentkezés, böngészővezérlés, DevTools, belső API vagy játékbeli írás. Az eredeti JS nem része a csomagnak, így a forráshash újraellenőrzése csak az eredeti fájlokhoz jogosult helyi olvasás mellett lehetséges. A `qualify_once.sh` emiatt ilyen környezetben a **helyben elérhető** forrásokat ellenőrzi, a hiányzót nem pótolja feltételezéssel.

## Továbbra is szükséges

- Tényleges piaci és csapatkonfiguráció hiteles, engedélyezett forrásból.
- Működési döntések (adó, díj, intézmény, kapacitás) valós oksági hatásfüggvényei.
- Vállalkozásszám és migráció részleges/közvetett hatásai.
- Hitelszerződési feltételek és kifizetés/finanszírozás szerveroldali szabályai.
- Összehasonlítható, **azonos periódusú és azonos feltételekkel rögzített** EcoSim előnézeti pár, ha a szervezők és a felhasználó ezt engedélyezik és a visszaállítás biztonságos.

**Nem eredmény:** igazolt ötödik évi SmartCity index, garantáltan nyerő stratégia, pénzügyileg jóváhagyott projektindítás. **Státusz: STOP a játékbeli véglegesítésre.**
