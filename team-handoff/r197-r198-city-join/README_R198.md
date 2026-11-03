# EcoSim R197–R198: közös állapot, szigorú projekt–adó–működés párosítás

**Nem új optimalizáló. Nem éles játékutasítás.** Az R196 tízfüles lefedettségi rétegét megtartva az R197 a **meglévő** R149–R159 offline fiskális számítási láncot az R195 azonos bemeneti állapotához köti. Az R198 pedig csak akkor mutat konkrét, előre kiszámolt részleges fiskális pályaeredményt az R195 két tervéhez, ha a teljes, öt évre kiterjedő projektsorozat **és minden éves konzervatív kártyateher egyezik** a független R149 jelölttel és az R159 pályával.

## Miért szükséges az egyezés?

Az R195 két 100/90 ezer ECU-s történeti keret melletti tervét külön heurisztikus keresőfuttatás számítja. Az eredeti R149 a historikus bemeneten 50/100/150 ezer ECU-s feltételezett keretek mellett hozhat más ötéves projektjelölteket. Még azonos elsőéves projektek mellett sem következik azonos ötéves cash-flow vagy indexérték! Az R198 **nem** rendeli rá önkényesen egy másik projektjelölt fiskális eredményét az R195-re; az egyezés hiányát `HOLD_NO_EXACT_PROJECT_SCHEDULE_MATCH`-ként rögzíti.

## Újrahasznált, valós (nem stub) komponensek

- R195 teljes megőrzött történeti kétterves eredménye, SHA-256-tal azonosított bemeneti állapottal.
- R149/153: adóérzékenységi pályák, projektfüggő részleges index.
- R154: négyadó-bevételek kizárólag megadott adóalap-hipotézisekkel.
- R155: hat díjbevétel és intézményi bér-/anyagköltség-részösszeg.
- R158/159: helyesbített, csatornánként időzített pénzáram-stressz azonos R149 jelölten és adó-/működési pályán.
- R196: a tíz EcoSim-fül hiányzó bizonyítékának nyilvántartása.

**Nem rendelkezünk szerverhitelesített teljes cash flow-val**, naprakész hitel- és támogatási feltételekkel, vagy a lakosság/vállalkozások visszacsatolásának validált modelljével. A részleges pénzügyi eredmények nem növelik az R195 projektkeretét, és nem adhatók hozzá a projektmodell pontszámához. Játékkapu: `STOP`.

## Egyszeri Fedora natív történeti kereszt-E2E

Az R195 már PASS történeti `TRADEOFF.json` fájljával, repo gyökérből:

```bash
bash team-handoff/r197-r198-city-join/run_joint_historical.sh \
  --tradeoff /tmp/ecosim-r195-tradeoff-2qiKmOEe/TRADEOFF.json
```

A runner a saját repositoryjában található eredeti R162/R149 szoftvert **egy alkalommal** újrafuttatja, ezt hozzákapcsolja az R196, R197 és R198 ellenőrzésekhez, és külön SHA-256 manifesttel ellátott `/tmp/ecosim-r198-native-*` dossziét állít elő. Játékhoz nem csatlakozik. Az adó- és működési pályák itt **szintetikusak**, kizárólag a pontos E2E szerkezeti ellenőrzésére szolgálnak.

Tesztek:

```bash
python3 -m unittest discover -s team-handoff/r197-r198-city-join/tests -v
python3 -m unittest discover -s team-handoff/r196-city-review/tests -v
```

## Bizonyíték és integrálási kapu

Native PASS csak akkor állítható, ha a Fedora valóban lefuttatta a R149→R196→R197→R198 láncot **és** az eredmények visszaolvashatók. Azonos projektjelölt hiánya nem code-fail, hanem bizonyított modellezési gap, amelyet a jelentés HOLD-dal mutat. Később azonos projekt és policy pályák közös keresési kiértékelését kell hozzáadni a már meglévő motorhoz — nem egy második optimizerrel.
