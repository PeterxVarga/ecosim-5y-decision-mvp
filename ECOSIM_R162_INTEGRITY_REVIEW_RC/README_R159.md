# EcoSim R159 – bizonyítható hibák javítása, pénzügyi stressz falszifikáció

**Státusz:** offline működő belső döntési MVP; `gameplay_gate = STOP`.

## Előzetes terv → tényleges implementáció

Az R158 meglévő keresőjének és pénzügyi összesítésének célzott kódauditja után két beavatkozást hajtottunk végre **ugyanabban a rendszerben**, második optimalizáló nélkül.

1. **Pénzáram időzítési hiba javítása (érdemi pénzügyi modellhiba).** Az R158 a díjbevétel-változást előbb nettósította az intézményi bér- és anyagköltséggel, és csak ezt a nettó értéket késleltette. Ha egy évben a díjbevétel-változás +100 ECU és a munkabér-költségváltozás +100 ECU, a korábbi nettó nulla miatt a késleltetett pénzügyi stressz elmulasztotta az azonnali 100 ECU költség elismerését. Másik ellenpélda: egy adócsatorna +120, egy másik −120 ECU, tehát a nettó változás nulla, mégis a pozitív adó később jelenik meg a stresszhipotézisben, mint a negatív.
2. **Defenzív jelölthalmaz-normalizálás.** A `found_by_search_in` most egy adott keretet csak egyszer rögzít. Ez keményítés a későbbi további keresési ágakhoz, **nem** bizonyított, hogy az R158 meglévő futásában valóban előfordult volna ilyen duplikáció: az R157 már a legtöbb ismétlődést kizárja.

## Mit javít az R159?

- `tools/operating_cash_r155.py`: az eddigi hat szolgáltatási díj közvetlen különbségét csatornánként is átadja. A forrásalapú részszámításból nem találunk ki további változót.
- `tools/temporal_cash_r158.py`: az egyes **négy adó + hat díj** pozitív bevételi változását a stresszmodell hipotetikusan a következő évre helyezi, a negatív bevételi változást azonnal elszámolja. Az intézményi bér-/anyagköltség változása az adott évben jelenik meg, így a költségcsökkenésből származó megtakarítást sem téveszti késleltetett bevétellel. A csatornákhoz hiányzó vagy hibás bontást nem pótolja becsléssel: *fail closed*.
- `tools/decision_desk_r149.py`: változatlan stratégiai kereső, defenzív deduplikáció és a javított időzítési kimenet a már meglévő munkafolyamatban.
- `tools/decision_view_r149.py`: az offline HTML és a Markdown-jelentés R159 címkével, a pontosított stresszhipotézissel magyarázza a kimenetet.
- `tools/qualify_r159.py`: egyetlen integrált falszifikációs tesztkör, ellenpéldák és a valódi R157 történeti döntési futás közös ellenőrzése.

## A tényleges futás eredménye

- **51/51 új, ebben a körben ténylegesen lefuttatott ellenőrzés PASS.** A korábbi R158 `58/58` jelentést változatlanul megőriztük; nem számoljuk most újra lefuttatott tesztként.
- Az R158 történeti döntési futásában **78** feltételes terv–adó-/intézményi pálya kombináció volt. A javított időzítés **26** kombináció csúcshiány-értékét módosította; legfeljebb **+5 763 ECU** különbséggel. Ez **nem** aktuális játékbeli pénzügyi érték.
- A 26 modellkorrekciót a `results/R159_HISTORICAL_FALSIFICATION_DEMO/R158_TO_R159_CORRECTION_AUDIT.json` rögzíti a régi és új értékekkel. A korábbi történeti jelöltlista változatlan.
- Az offline HTML: `results/R159_HISTORICAL_FALSIFICATION_DEMO/DECISION_DESK.html`; gépi JSON és Markdown mellett.
- Az éves újratervezésnél (pl. a 3. évtől) a **korábbi évek esetleges késleltetett bevétele nem ismert**. A modell jelzi, ha a nulla áthozott bevétel csak feltételezés.

## Mi NEM igazolt továbbra sem?

Az egyéves bevételkésleltetés szándékos **hipotézis**, nem a szerver tényleges kifizetési időpontja. Az R159 immár a hipotézist aritmetikailag helyesen bontja csatornákra, **de nem bizonyítja annak valósághűségét**. A tényleges nyitó treasury, hitel-, támogatás-, kötelezettség- és migrációs feltételek továbbra sem ismertek. A pénzügyi különbségek nem felhasználható projektkeretek, és nem jelentenek megerősített finanszírozhatóságot. Nem létezik tényleges éles EcoSim-predikciós pontossági mérés. Éles game action: 0. Játékkapu: **STOP**.

## Offline használat később (most nem szükséges)

```bash
./qualify_once.sh
./run_r159_offline.sh
sha256sum -c SHA256SUMS
```

A `tools/decision_desk_r149.py` és `tools/strategy_5y.py` továbbra is az eredeti, egyetlen fő keresőt használja. Az eredeti R94 történeti inputokat nem írtuk át.
