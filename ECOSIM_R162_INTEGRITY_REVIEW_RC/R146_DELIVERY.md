# EcoSim R146 — összevont ötéves döntési motor: feltételes policy-aware keresés, stresszteszt, passzív kalibráció

**2026. október 31. | R145 → R146 ugyanabban a kódbázisban**

## Mi készült el ténylegesen?

1. **Valódi, működési forgatókönyvre kondicionált projektkeresés.** Az R145 először projektterveket keresett a projekt-only faktorokkal, és csak utána adta hozzá a policy-hatásokat. Az R146 most a keresési heurisztikát és a beam-rangsorolást is a *kifejezetten megadott* működési hatásokra kondicionálja, minden forgatókönyvnél külön. A projekt-only eredmény és a policy mellett becsült marginális projekt-hatás külön mezőt kapott.
2. **Négy deklarált stresszprofil.** Változó projektintenzitás, hatásfennmaradás, policy-intenzitás és feltételezett költségkeret-szűkítés. Az egyes tervekről a legrosszabb/legjobb **ismert faktorokra korlátozott** proxykimenetet szolgáltatja. Ezek NEM konfidenciaintervallumok, nem valószínűségek és nem a teljes EcoSim-kimenet garantált határai. A végső rangsorban a kimondott feltételezések alatti minimum szerepel, nem hamis várható érték.
3. **Finanszírozási UNKNOWN-kapu.** Ha akár egy aktív működési döntésnek hiányzik az éves pénzhatása, az éves projektkeretet nem igazoltnak jelöljük. Nincs ismeretlen adó vagy intézményi többlet **0 ECU-ként** történő jóváírása. A szintetikus pozitív bevétel nem emelheti a megengedhető projektkeretet. Minden keret továbbra is csak feltételes szcenárió.
4. **Passzív, forrásazonosítós ellenőrzés.** A 2026. október 30-i történeti p0 **tény** és p1 **terv** két külön rekordja alapján újraszámolja a kijelzett indexet és a pénzügyi számtani különbségeket. Ha később ugyanazon évre terv- és tényrekord kerül be, a különbséget leírja, de nem teszi oksági bizonyítékká.
5. **Egyetlen helyi indítópont.** `tools/run_r146_offline.py` a passzív egyeztetést és az öt évre szóló projektek/működési döntések együttes forgatókönyveit ugyanabban a rendszerben készíti el. A példaeredmények már a ZIP-ben vannak, futtatni jelenleg nem szükséges.

## Technikai kvalifikáció

- **131/131 összevont offline ellenőrzés PASS** (85 örökölt + 46 új).
- A teljes R146 futtató is sikeresen előállította a JSON, Markdown és státusz kimeneteket.
- **0 bejelentkezés, 0 játékbeli mentés/módosítás, 0 webhívás, 0 Codex CLI, 0 felhasználói terminál-futtatás.**
- A korábbi R139–R145 bizonyítékok, projektkatalógus, történeti pénzügyi CSV és mintaeredmények továbbra is a csomag részei.
- Standard library Python, nincs új függőség.

## Konkrét, kizárólag szemléltető eredmény

Az évi **100 000 ECU** külsőleg feltételezett projektkeret és a korábbi 2026. október 30-i tesztadatok mellett:

| Forgatókönyv | Év 5 ismert faktorokra számított kombinált proxy Δ | Deklarált stresszprofilok szerinti minimum Δ | Finanszírozási státusz |
|---|---:|---:|---|
| Új policy nélkül | +1,3410 | +0,6596 | Feltételes hipotetikus |
| Szintetikus képzési kapacitás, +2% faktor és −5000 ECU/év | +1,3216 | +0,6447 | Feltételes hipotetikus |
| Ismeretlen pénz-/indexhatású adódöntés | +1,3410 ismert komponens | +0,6596 ismert komponens | **UNKNOWN** |

**Sem a szintetikus hatás, sem a 100 000 ECU/év nem az EcoSim igazolt beállítása.** Az ismeretlen adóhatást nem nulla modellértékként számítja: a fenti ismert komponens mellé kifejezett hiányjelölést ad. A modell nem igazol végleges nyerő stratégiát.

## Mi hiányzik a tényleges ötödik évi nyerő stratégia bizonyításához?

1. Éles, hitelesített **market/setup/team** paraméterek, projektlimit-korrekciók és pénzügyi kötelezettségek.
2. Adók, díjak, intézmények, kapacitások és bérek **valós, nemlineáris éves hatásfüggvényei**; az R146 ezeket csak megadott forgatókönyvek esetén tudja kezelni.
3. A kliensoldali pontozásból nem visszafejtett tényezők, rejtett aliasok, projektkésések, ismételhetőség.
4. A szerveroldali hitel-, támogatás- és elszámolási korlátok.
5. Versenytársak, lakossági és vállalati migráció; terv–tény eltérések.
6. Hiteles, passzívan megfigyelt **terv–tény adatsorok** az éves állapotmodell validálására. További játékbeli kísérlet csak előzetesen igazolt visszaállítás és külön felhasználói jóváhagyás mellett.

**Döntési kapu: STOP.** Nincs bizonyítottan finanszírozható, szerveroldalon elfogadott vagy matematikailag globális optimumként bizonyított stratégia.

## Fájlok

- `tools/strategy_5y.py` — új, policy-conditional projektkeresés az eredeti motorban
- `tools/joint_5y.py` — integrált politika/projekt search + robusztus rerank + ismeretlen pénzhatás kapu
- `tools/robust_r146.py` — négy deklarált stresszprofil
- `tools/passive_r146.py` — biztonságos tény/terv egyeztetés
- `tools/run_r146_offline.py` — egyetlen újrafuttatható, helyi workflow
- `tools/qualify_r146.py` — összevont regressziós kvalifikáció
- `results/R146_SYNTHETIC_100K_*.json`, `.md` — előállított példák
- `results/R146_PASSIVE_HISTORICAL_RECONCILIATION.json` — történeti tény/terv ellenőrzés
- `results/R146_INTEGRATED_QUALIFICATION.json` — kvalifikációs jegyzőkönyv

**Felhasználói művelet most: nincs.**
