# EcoSim R162 — Friss szemléletű kódaudit és integritási hibajavítás

## Miért ez a chunk?

Az R161 release candidate után a felhasználónak továbbra sincs hozzáférése a bejelentkezett EcoSimhez, Codexhez vagy saját terminálhoz. Újabb, bizonyítatlan nyerőstratégia-keresés helyett az elérhető R161 kódon **két reprodukálható hibát** javítottunk.

## Bizonyított hibák, ellenpéldák és javítás

1. **Hibás JSON-számelfogadás (HIGH).** Az R161 `strategy_5y.read_json` elutasította a literális `NaN` és `Infinity` tokeneket, de a szabványosnak látszó `1e999` számból a Python `json.loads` `float('inf')` értéket készített. **Ellenpélda:** `{"tax_rate":1e999}` az R161-en elfogadott. **R162:** közös `tools/json_integrity_r162.py` JSON parser kifejezetten ellenőrzi a `parse_float` véges eredményét, elutasítja a duplikált mezőket és nem szabványos konstansokat; a már meglévő 10 MB-os alap méretkorlátot is megtartja. A stratégia, politika, adó, bizonyíték, kalibrációs és CLI-adatút belépési pontjai azonos szigorú feldolgozót használnak. Nem jelent szerverhitelesítést.
2. **Szigorú tagadó projektfeltétel hibája (MEDIUM).** Az R161 `permitted()` a tagadó előfeltételek együttindítási konfliktusát csak `allow_same_year=True` mellett látta. **Ellenpélda:** projekt A feltétele `not B`, és A+B ugyanabban az évben indul, `allow_same_year=False` esetén az R161 `(True,False)` értékkel engedte. **R162:** a tagadó feltételek mindig vizsgálják a korábbi aktív és az azonos évben induló projekteket; csak a *pozitív* előfeltételeknél működik a feltételes együttindítás. A historikus 35 kártya két ismert, *pozitív* függősége (#30→#29, #31→#27) nem változott. Ez jövőbeli katalógusok és hibás bemeneti esetek ellenőrzését erősíti, **nem állítja, hogy a mai 35 kártyában van tagadó feltétel**.

## Egyetlen célzott kvalifikáció

`results/R162_QUALIFICATION.json` — **44/44 új ellenőrzés sikeres**. A tényleges eredeti R160-as döntésfolyamaton végzett **1 teljes történeti E2E futás** 20 azonos jelöltet adott. Ezt nem keverjük össze az R161 korábbi, most nem újrafuttatott 62 ellenőrzésével. Ellenőrzött állapot: `PASS_OFFLINE_ONLY`, `STOP`.

## Reprodukálás (későbbre, nem szükséges most)

```bash
./verify_release_r162.sh      # csak olvassa és ellenőrzi az R162 fájlokat
./qualify_r162_once.sh       # egy történeti E2E + célzott ellenpéldák
```

A múltbeli `verify_release_r161.sh` és R161 manifest **történeti verziók**. A módosított R162 fát az új R162 ellenőrzővel szabad minősíteni; az R161 fájl-ellenőrző az előző kiadás változatlan fájljait várja.

## Nyitott, nem kódolással feloldható bizonyítékhiányok

- Nincs hiteles, jelenlegi `market/team` konfiguráció és éles költségkeret.
- Nincs szerveroldalilag igazolt teljes éves városállapotmodell (vándorlás, intézmények, versenytársak).
- Nincs előre rögzített modellbecslés és későbbi hiteles FACT pár; valós előrejelzési hiba ismeretlen.
- Az R162 fájlintegritási ellenőrzése nem harmadik féltől származó, aláírt buildhitelesítés; független emberi review nem történt.
- Semmilyen in-game műveletre nem ad engedélyt; a játékbeli döntési kapu `STOP`.

**Döntés:** a jelenlegi hozzáférési feltételek mellett a további szintetikus funkciófejlesztést nem indokolja bizonyíték. Az első valódi folytatás: jóváhagyott, csak olvasható aktuális állapot-export, amelyet a meglévő R156/R152 adatút ellenőrizhet.
