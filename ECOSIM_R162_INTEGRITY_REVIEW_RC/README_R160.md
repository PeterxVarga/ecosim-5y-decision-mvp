# EcoSim R160 — független konzisztencia- és feltételvizsgálat

**Hatókör:** az R159 változatlan ötéves beam keresője, R154–R159 adó-/díj-/intézményi részmodellje és offline döntési dossziéja. Egyetlen új, kicsi és önálló **auditáló komponens** készült; nem jött létre második optimalizáló. Sem EcoSim-böngésző, sem Codex, sem felhasználói terminál nem kellett hozzá.

## Mi volt a falszifikációs cél?

A korábbi rendszer a *részmodell* Pareto-összehasonlításában a nem modellezett projekthatások **darabszámát kisebb-jobb célfüggvényként** kezelte. A darabszám nem azonos az elmaradó tényleges indexhatás nagyságával vagy előjelével. Ezért egy terv pusztán az ismeretlen hatások alacsonyabb száma miatt is részmodell-dominánsnak tűnhetett. Az R160 ezt megszünteti; a hiányos bizonyíték külön figyelmeztetés, a **számszerű részmodell-Pareto** pedig a számszerűsíthető index- és éves kártyateher dimenzióira korlátozódik. Ez sem a valós EcoSim-eredmény Pareto-dominanciája.

A másik probléma, hogy a keresőben szereplő éves előfeltétel, költség és projektlimit ellenőrzésének nem volt **független, saját kimenetet újraszámoló auditja**. Az új `tools/independent_audit_r160.py` a tárolt, 35 kártyás **történeti exportból** minden jelöltre külön újraszámolja:

- Nem ismétlődő projektek, már futó és az aktuális időszakban kiválasztott azonosítók.
- Éves indítási cap és az előző periódus `project1` bónusza; ismeretlen bónusznál szigorú bizonytalansági jelzés.
- Megjelenített `Fut` projektelőfeltételek és azonos évi co-start külön **nem szerverhitelesített** feltételként.
- Indítás + beruházás + évente pozitív fenntartási kártyateher; ellentmondó kereső-kimenet **hibával megáll**.
- Opcionális hipotetikus költségkeret, csak aritmetikai illeszkedés, **nem likviditási vagy hiteljóváhagyás**.

Az R160 audit a `strategy_5y.search` végén és a döntési jelöltek összehasonlításakor is kötelező. Az eredmény JSON-ban és a statikus HTML-jelentésben látható.

## Eredmények és evidenciakapu

A 2026-10-30-i tesztfordulós, **nem éles** példán az R157 két keresési célfüggvénye és az R159 működési pénzügyi modellje együtt futott. A döntési folyamat 26 egyedi mintajelöltet állított elő; mind a 26 külön auditot kapott, **0 belső szabály-/költségellentmondás** mellett. Mind a 26 szerverelfogadása **feltételes vagy ismeretlen**; a játékbeli kapu `STOP`.

A különböző hibás bemenetekre, függőségekre, dupla indításokra, projektlimit-bónuszra, hirdetett és újraszámolt költségek eltérésére, negatív feltételekre és részmodell-dominanciára épülő **63 R160 ellenőrzés sikeres**. Az R159 51 korábbi PASS-ja *megőrzött bizonyíték*, nem újrafuttatott jelen teszt.

- `results/R160_QUALIFICATION.json` — végső offline ellenőrzési bizonyíték.
- `results/R160_HISTORICAL_CONSISTENCY_DEMO/DECISION_DESK.json` — teljes döntési és auditadat.
- `results/R160_HISTORICAL_CONSISTENCY_DEMO/DECISION_DESK.html` — offline statikus döntési felület.
- `./qualify_once.sh` — új R160 egyszeri kvalifikáció; `./run_r160_offline.sh` azonos.

## Mit NEM igazol?

- A teljes éles EcoSim `market/team` állapotot, aktuális finanszírozhatóságot és valódi hitelkeretet.
- A szerveroldali előfeltételek elfogadási sorrendjét vagy a későbbi projektek eredeti teljes adatainak azonosságát.
- Az adó-/díj-/intézményi döntések visszacsatolását, migrációt, vállalat- vagy népességváltozást.
- A kereső globális optimumát, ötödik évi tényleges pontszámát vagy nyerési esélyét.

**A helyes használati státusz:** offline ellenőrzött, részmodell-alapú forgatókönyv-összehasonlítás, `STOP` a játékbeli döntésre. Hiteles `market/team` állapot és előre rögzített előrejelzés–tény adatpár nélkül ezeket a korlátokat nem lehet újabb offline kódtesztekkel megszüntetni.
