# EcoSim R158 — Éves pénzügyi időzítési híd, R157 újrahasznosításával

**Állapot:** működő, feltételes offline döntéstámogatás, `gameplay_gate = STOP`.

## Research → Falsify → Reuse → Build

Az R154 négyadó-komponense és az R155 hat szolgáltatási bevétel/lefödött intézményi részkiadás hídja az ötéves összesített bevételi eltéréseket már összevetette az R157 projektek ötéves kártya-terhével. Ebből azonban nem derült ki, hogy egy később jelentkező részbevétel mellett a projektindítás az első évben mennyire terhelné a város likviditását. Az ötéves részleges nettó összeg **nem** jelenti, hogy ugyanannyi készpénz időben rendelkezésre áll. Az R158 célzottan ezt az idődimenziós hibát kezeli.

**Bizonyítható falszifikáció:** azonos 100 ECU projektkártya az első évben, és azonos 100 ECU adókülönbség öt év alatt. Ha a feltételezett adótöbblet az első évben érkezik, az azonos éven belüli elszámolás mellett a hipotetikus nulla-nyitó kumulált negatívum 0. Ha csak a második évben, a maximális előző évi negatívum 100 ECU. Az ötéves nettó mindkét esetben 0. A fizetési időpont éven belül **egyik modellben sem bizonyított**.

## Megvalósítás, új optimalizáló nélkül

- `tools/temporal_cash_r158.py`: szigorú éves összerendelés a **meglévő** `tax_revenue_r154`, `operating_cash_r155` és `strategy_5y` projekttervezője által előállított adatokból. Két időzítési feltételezés, évenkénti pozitív és negatív részösszegek, projektkártya-terhek, nulla-nyitó feltételes kumulált sorok, első negatív év és legnagyobb negatív kumulált érték.
- `tools/decision_desk_r149.py`: ugyanabba az operátori jelentésbe bekötött R158 rész. A keresési költségkereteket NEM tágítja ki feltételezett többletadóval vagy díjbevétellel. Hiányzó R154/R155 adatoknál blokkolt állapot jelenik meg.
- `tools/decision_view_r149.py`: a korábbi **statikus, külső függőség nélküli** HTML-ben éves pénzügyi napló és összefoglaló.
- A három dimenziós, pályánként szűrt **mintabeli** időzítési Pareto-összevetés egyszerű leíró értékelés: ismert részleges index, részleges ötéves cash az új projektek költségével csökkentve, illetve a pozitív részbevétel +1 év késleltetése mellett feltételezett negatív kumulált egyenleg. Ez nem új kereső és nem hiteles finanszírozhatósági rangsor.

A két időzítési profil kifejezetten **hipotézis**:

1. `IMMEDIATE_YEAR_END`: a pozitív és negatív közvetlen részeltérést a projektkártya-teher évében könyveljük. A sorrend nem ismert.
2. `POSITIVE_COMPONENTS_ONE_YEAR_LATE`: a két pozitív részbevétel-eltérést következő évben engedjük be, a negatív különbségeket és a projektköltséget azonnal elszámoljuk. Ez konzervatív stressz, de **nem** bizonyított szerveroldali kifizetési idő.

Mindkét sor **nulláról induló, nem teljes, aritmetikai** pénzáram. Nincs megadott tényleges pénzállomány; az ismeretlen alapbevétel, egyéb kiadás, hitel, támogatás, tartalék és gazdasági feedback nem nulla, hanem nem modellezett. Az eredmények nem valós *financing gap*, nem hiteljogosultság, nem valódi elkölthető keret.

## Eredmény és teszt

- R94 történeti **tesztfordulós** faktor- és projektadatok + R154/R155 **szintetikus** pénzügyi pályák.
- 26 egyedi heurisztikusan mintavételezett projektterv × 3 hipotetikus adó-/díj/intézményi pálya = **78 évenként bontott pénzügyi kombináció**. A terminális részleges Pareto-összevetés pályánként 8 nem dominált mintabeli jelöltet tartalmaz (a különböző pályákat nem keveri egy „valódi Pareto-frontba”).
- R158 új kvalifikáció **58/58 PASS**, benne hibás és kevert forrás, kihagyott év, duplikált pálya, NaN/Inf, projektköltség-eltérés, harmadik évre történő újratervezés, valamint tényleges R157 operátori döntési futás.
- R156 (68) és R157 (66) korábbi kvalifikációs bizonyíték megőrzött, **ebben a körben nem újrafuttatva**. Az R157 teljes lánca túl költségesnek bizonyult és ezért a végső kvalifikáció a változott funkciók és egy teljes R158 E2E futás kombinációja.
- Bejelentkezett EcoSim-adat: **nincs**, valós előrejelzési pontosság: **ismeretlen**, játékbeli művelet: **0**, döntési kapu: **STOP**.

## Futtatási útvonal — nem szükséges most

```bash
./run_r158_offline.sh   # történeti illusztráció és statikus HTML/JSON/Markdown
./qualify_once.sh       # a végső R158 célzott + teljes munkafolyamatos kvalifikáció
sha256sum -c SHA256SUMS
```

Az R158-tól nem várható önmagában pontosabb szerverindex-előrejelzés. A legnagyobb hátralévő bizonyíték az éles `market/team` állapot, valódi projektkeret, szerverelszámolás, valamint ugyanazon periódus korábbi terv–későbbi tény adatpárja. További funkcióépítés előtt ezeket szükséges prioritásként kezelni, amikor ismét elérhető lesz az EcoSim.
