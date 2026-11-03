# EcoSim EDU — csapatos, adaptív P1–P5 döntési munkamenet

**Kiadási cél:** a `main` ágon meglévő R162/R189–R195 *offline*, forrásazonosított döntéstámogatás használható, átlátható csapatmunkafolyamata. Ez nem új optimalizáló, nem élő játékvezérlés, és **nem igazolt ötödik évi győzelmi előrejelzés**.

**Állapot:** `GAME_ACTION_GATE=STOP` · `READ_ONLY_DECISION_SUPPORT` · `FUTURE_FACT_TO_FACT_EVIDENCE=UNKNOWN`.

## 1. Kezdés csapattagként

A repó gyökeréből a **main** ágon (Python 3 és Git szükséges):

```bash
git rev-parse HEAD
bash team-handoff/r191-live-admission/run_team.sh historical
bash team-handoff/r191-live-admission/run_tradeoff.sh historical
```

Az első futás meglévő, rögzített R162→R194 történeti ellenőrzés; a második két *hipotetikus*, azonos bemeneten számolt ötéves projekttervet hasonlít össze az R195 motorral. A jelentés és a nyugták a szkript által kiírt ideiglenes könyvtárban keletkeznek, **nem** a játékban. A historikus mód nem a saját csapat aktuális állapotát mutatja. PASS ≠ élő döntésre alkalmas rendszer.

Forrás és használati szerződés: [R194](r191-live-admission/README_R194.md), [R195](r191-live-admission/README_R195.md). A történeti modell feltételezéseit és függőségeit az eredeti [R162](../ECOSIM_R162_INTEGRITY_REVIEW_RC/README_R162.md) dokumentálja. A frissebb R196+ kísérleti modulok külön draft PR-ben maradnak; ne feltételezd, hogy `main`-en elérhetők.

## 2. Privát döntési dosszié — ne commitold

A repository **PUBLIC**. Csapatnévhez kötött élő játékképernyőt, belépési munkamenetet, teljes R156 exportot, aktuális pénzügyeket, versenytárs-adatot és bizalmas A/B-próbajegyzőkönyvet **ne pusholj ebbe a repóba**.

Az aktuális döntési dossziét tartsd külön, hozzáférés-szabályozott csapatmappában, vagy helyben a gitignore-olt `private-evidence/` alatt. Ez utóbbi *nem* biztonságos megosztási csatorna; csak a véletlen Git-commit ellen véd. Ne tegyél jelszót, tokent vagy session cookie-t semmilyen dossziéba.

Egy időponthoz, piachoz és periódushoz tartozó, egymással összefüggő bizonyítékcsomag szükséges:
- időbélyeg, forrás, piac, csapat, periódus, a mentés állapota;
- P0 **FACT** és P1 **PLAN** külön, teljes SmartCity-faktorok és hat súly;
- 35 aktuális projektkártya: státusz, költség, hatások, feltételek; az eredetileg futó és az ebben a periódusban újonnan indított projektek külön;
- megfigyelt projektszámlimit és kötelező függőségek; hiányzó adat **UNKNOWN**, nem nulla;
- finanszírozható források, lekötött tételek, kölcsönök és támogatások időzítése, külön a csak tervezett perióduseredménytől;
- a döntési állapot előtti és utáni képernyő/nyugta, majd ha jogosultan mentették: a mentés szerveres visszaigazolása.

**A mostani elsőéves csapatpróba** eredményeit külön, privát R257/R258 dosszié őrzi. Az ott szereplő A/B csomagok egyike csak *feltételesen kiválasztott*; a korábbi próba minden ideiglenes indítást visszavont, és nem mentette a játékot. A csapattársak ne tekintsék a privát eredményeket automatikusan végrehajtott döntésnek.

## 3. Első év / P1 — időkritikus döntési kapu

1. **Friss állapot:** ellenőrizd a bejelentkezett játékon, hogy a csapat/piac/periódus nem változott és nincs korábbról véletlenül bent maradt új projekt.
2. **Két legitim cél:** magasabb azonnali SmartCity-index, illetve magasabb pénzügyi mozgástér a következő évekre. Az egyikben jobb csomag nem automatikusan az öt évben is jobb.
3. **Választás:** összehasonlítható A/B-mérésből válassz feltételes P1-tervet; a munkatársak száma, az adók, hitelek és más politikák maradjanak rögzítve az összevetésnél.
4. **Külön engedély:** a projektindítás, Save és periódusléptetés *három eltérő műveleti kapu*. A terv kiválasztása önmagában egyiket sem engedélyezi. Save előtt mutasd meg a friss indexet, költséget, perióduseredményt, kölcsönöket és a négy érintett projektet.
5. **Visszaellenőrzés:** valódi mentés után független szerveroldali visszaolvasás; a csapat számára a mentett állapot jelenti a P2 induló inputját, nem az előzetes PLAN.

## 4. P2–P5 — évente újraoptimalizálás, nem vak öt éves lista

| Periódus | Kötelező új megfigyelés | Adaptív döntés |
|---|---|---|
| **P2** | P1 tényleges záró FACT, P1 tervezett értékekkel eltérés, új költség és cash, aktuális 35 kártya | Áttervezés csak az új FACT-ból; az előző előrejelzési hibát dokumentáld, ne nevezz PLAN-t FACT-nak |
| **P3** | P2 lezárt FACT, új piaci/népességi és intézményi viselkedés, tényleges finanszírozás | Tarts meg több pénzügyi és index-orientált jelöltet; a projektfüggőségeket és fenntartási költséget ellenőrizd |
| **P4** | P3 lezárt FACT, fennmaradó projektek és évközi commitments | A megmaradt időhorizont szerint új rangsor, nem historikus fix évenkénti költségből |
| **P5** | P4 lezárt FACT, aktuális korlátok és ellenőrzött források | A záró SmartCity-indexre optimalizált döntési összevetés, bizonytalan jövőbeli megtérülés külön jelölve |

Minden periódusban:
- Ha van teljes, egységes és forrásazonosított aktuális dosszié, futtasd újra a *meglévő* auditált keresőt; nem kell saját indexképletet vagy új keresőt írni.
- Összehasonlítható, azonos kiinduló állapotú szcenáriókat értékelj: index-előny; finanszírozási mozgástér; stresszes, **hipotetikus** bevételi/kiadási eset. A stresszváltozat nem szerver-előrejelzés.
- Számolj fenntartással, támogatások bizonytalan időzítésével, kamattal, előfeltételekkel és már futó projektekkel. Ne keverd össze a perióduseredményt az elkölthető készpénzzel.
- Ha a következő zárt FACT hiányzik, az évhatás, projektlimit vagy a piaci szabály nem bizonyított, a helyes állapot **HOLD / UNKNOWN**. A játékbeli művelet ettől még külön jóváhagyást igényel.
- A többi város várható döntése és a teljes szerveres hatásmodell nem ismert; ezért ötödik évi győzelem nem garantálható.

**Jelenlegi fő korlát:** a `run_tradeoff.sh current` elsőéves pénzügyi és R156/R192 bemeneti kapura épül. **P2–P5 aktuális játékállapotra való használata külön forrás-/periódus-adapter kvalifikációt igényel.** Ne címkézz történeti vagy P1-es futást friss P2–P5 validált eredménynek.

## 5. Csak olvasható aktuális R195 futás — ha minden adat megvan

Az itt felsorolt fájlokat az operátor privát, ellenőrzött adatgyűjtéssel készíti elő; a parancs maga nem lép be a játékba.

```bash
bash team-handoff/r191-live-admission/run_tradeoff.sh current \
  --state "/abs/path/current_state.json" \
  --r156-bundle "/abs/path/r156_immutable_bundle" \
  --year1-finance "/abs/path/observed_year1_finance.json" \
  --current-card-catalog "/abs/path/observed_35_cards.json" \
  --base-budget "$SCENARIO_HIGH_ECU" \
  --reserve-budget "$SCENARIO_RESERVE_ECU" \
  --cap "$OBSERVED_PROJECT_CAP"
```

A három környezeti változót külön, ellenőrzött forrásból töltsd fel. A két pénzügyi keret szcenáriófeltétel; az első periódusban nem lépheti túl a külön igazolt, ténylegesen hozzáférhető keretet. A `HOLD` eredmény nem hiba, amelyet ki kell kerülni, hanem bizonyítékhiány.

## 6. Csapatos döntési és ellenőrzési protokoll

Minden **privát** évzáró döntési feljegyzés tartalmazza: `FACT_PERIOD`, `PLAN_PERIOD`, `MARKET`, `TEAM`, `CAPTURED_AT`, `SOURCE_HASHES`, `RUNNER_COMMIT`, `PROJECT_START_IDS`, `INDEX_PLAN`, `FINANCE_PLAN`, `CASH_AUTHORITY`, `LOANS`, `UNKNOWN_GATES`, `A_VS_B_TRADEOFF`, `OWNER_APPROVAL`, `SAVE_RECEIPT`. Mentés előtt `SAVE_RECEIPT=ABSENT`, nem kitalált `PASS`.

A csapattárs a `main` kódot reprodukálhatja; az azonos **privát bemenet** és forrás-pin szükséges ugyanahhoz a konkrét döntéshez. A történeti R195 kimenet, a jelenlegi saját csapat R258 UI-mérése és az éles szerver által ténylegesen mentett állapot három külön bizonyítékszint.

**Csapatátadás elfogadása:** a fenti két `historical` parancs sikeresen lefut a csapattag gépén, a jelentés megnyitható, minden kétes élő állítás HOLD marad, és nem történt játékbeli módosítás. A repository publikálása önmagában nem igazolja ezt az egyéni gépes futást.

**Tiltások:** `NO_GAME_WRITE` · `NO_START` · `NO_SAVE` · `NO_NEXT_PERIOD` · `NO_CREDENTIAL_UPLOAD`. A bizonyított jövőbeli cél a legnagyobb P5 SmartCity-index, nem a legnagyobb önmagában vett P1-score.
