from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'P2_indirect_business_sensitivity.json').read_text())
projects={p['id']:p for p in json.loads((ROOT/'P2_joined_input.json').read_text())['projects']}

def ids(v):return ', '.join(f'#{i}' for i in v)
def f(x,n=6):return f'{x:.{n}f}'.replace('.',',')

def row_for_budget(b):
 r=D['rankings_by_budget'][str(b)];d=r['direct_only_leader'];m=r['reference_equal_weight_1x'];flip=r['first_leader_flip_equal_firm_weight_grid']
 return f'| {b:,} | {r["feasible_combinations"]:,} | {ids(d["ids"])} | {ids(m["ids"])} | {str(flip).replace(".",",") if flip is not None else "nincs a rácson"}× |'

p=D['focused_pair_comparisons'][0]
report=f"""# EcoSim P2 — A 30 közvetett vállalkozásszám-hatás falszifikációja (2026-11-05)

**Státusz: COMPLETED — feltételes offline érzékenységi kör.** Teljes P2–P5 stratégiára **PARTIAL**. A játékállapothoz nem történt hozzáférés vagy módosítás ebben a körben. A számítás a korábbi `P2_joined_input.json` és a 2026-10-30-i tesztfordulós hatáskatalógus alapján reprodukálható. **NEM EcoSim által számított előrejelzés.**

## 1. Pontosan milyen adatokat vizsgáltunk?

- Teljes történeti hatásleltár: **272 rekord / 35 projekt**; ebből **30 közvetett**: **22** „Kisvállalkozások száma”, **8** „Középvállalkozások száma”. A 30 rekord **23 projektnél** jelenik meg (köztük már futó projektek is). Nincs kihagyott vagy zéróként kezelt rekord.
- A második évben kiértékelhető új jelöltek közül 25 még nem fut; a korábbi szigorú függőségi szűrővel és a legfeljebb négy projekt / év feltétellel, legfeljebb 450 000 ECU újkiadási küszöb mellett **12 386** kombináció került a fő számításba. A 4 × hipotetikus költségkeret **nem** a játék által engedélyezett szabad pénz.
- P2 tényező: „Vállalkozások száma” **59,85** (P1 tény: **50,51**); súlya a megjelenített teljes indexben **0,0625** indexpont per tényezőpont a rekonstruált képletben (Gazdaság 25% × almutató 1/4).
- Külön beolvasott vállalkozásdarabszámok: kisvállalat **4 765 → 5 226**; közepes **92 → 108**; nagy **25 → 28**. Együttes változás **+480 db**, de **nem bizonyított, hogy ettől és csak ettől** mozdult a tényező **+9,34 pontot**.

## 2. Falszifikációs modell — nem oksági kalibráció

A 9,34 / 480 = **{f(D['observation']['observational_secant_factor_points_per_added_firm'],8)} tényezőpont/vállalkozás** egy *megfigyelt szelőmeredekség*. Ha ezt kizárólag érzékenységi referenciaértékként megszorozzuk a 0,0625 indexsúllyal, **{f(D['observation']['observational_reference_index_points_per_added_firm'],9)} indexpont / új vállalkozás** adódik. **Ez NEM igazolt oksági meredekség, nem jóslat és nem statisztikai konfidenciaintervallum**; a P1–P2 eltérésben piaci változások, adó- és bérdöntések, más projektek, nagyvállalkozások és nemlineáris faktorleképezések keverednek.

A hipotézis a projektkártyák százalékait a P2 jelenleg megfigyelt kis- és középvállalkozásszámához alkalmazza (például 0,03% × 5 226 = 1,5678 **hipotetikus** új kisvállalkozás). A több projekt százalékos szorzói összeszorzódnak. Ennek valós képlete **nem bizonyított**. A referencia meredekséget **0; 0,05; 0,1; 0,25; 0,5; 1; 2; 5; 10; 20×** változattal, a középvállalatok relatív súlyát **0,25; 1; 5; 20×** értékkel ellenőriztük. Ezek szándékosan tág *stresszforgatókönyvek*, nem valószínűségek.

A pénzügyi oldal változatlanul konzervatív: új projekt indítás + beruházás + pozitív P2 fenntartás; partneri támogatás és negatív fenntartás **nem** növeli a készpénzkeretet. A meglévő futó projektek –65 800 ECU fenntartási sora már szerepel a kiinduló P2-ben.

## 3. Változik-e a legjobb projektcsomag?

| Feltételezett költségkeret (ECU) | Megengedett kombinációk | Korábbi direkt rangelső | 1× referencia + közvetett hatás rangelső | Első rangsorfordulás, azonos cégsúllyal (vizsgált rácson) |
|---:|---:|---|---|---|
"""+'\n'.join(row_for_budget(b) for b in (75000,150000,300000,450000))+f"""

**Kritikus 450 ezres keret:** a korábbi **{ids(p['a_ids'])}** és **{ids(p['b_ids'])}** jelöltek között a közvetlen hatás alapján az előbbi csak **+{f(p['direct_A_minus_B'],9)} indexponttal** vezet. A második csomag a #16 projekt miatt **{f(-p['small_firm_difference_A_minus_B'],4)} vállalkozással nagyobb hipotetikus kisvállalkozás-hatást** kap. A referencia közvetett átváltás mellett ez **{f(-p['reference_1x_indirect_A_minus_B'],9)} indexpont** különbséget jelent az utóbbi javára, az eredeti direkt előnyt meghaladva. A matematikai fordulási küszöb **{f(p['equal_weight_crossing_secant_multiple'],4)}×** referencia — ez *nem* érvényes valódi kritikus paraméter, hanem a hipotézis saját küszöbe.

**További falszifikáció:** a középvállalkozások húszszoros relatív súlyát feltételezve már az 1× referencia mellett a 150k és 300k keret korábbi győztese is lecserélődhet. Ez bizonyítja, hogy a rangsor részben az **ismeretlen kis-/középvállalati faktorleképezéstől** függ, nem csak a kártyahatások mértékétől. Az egyes konfigurációk nem rendelkeznek ismert valószínűséggel, és *nem* szabad belőlük várható pontszámot átlagolni.

## 4. Mit dönthetünk el most?

**Bizonyított, offline:** a 30 hatás tételesen megőrzött és közvetettként osztályozott; az érzékenységi modellt a korábbi P2 direkt-hatás + pénzügyi szűrőhöz illesztettük; a 450k közeli csomagok sorrendje a hiányzó kapcsolat miatt nem robusztus. A 17 célzott teszt sikeres (8 korábbi integrációs és 9 új fókuszált teszt).

**Nem bizonyított:** a 30 hatás tényleges EcoSim-vállalkozásszámváltozása, ennek megjelenített „Vállalkozások száma” tényezőre gyakorolt oksági hatása, P2-ben a valódi index- és készpénzváltozás, a partneri támogatás időzítése, P3–P5 vállalkozásdinamika, a mentett P2 állapot. Emiatt továbbra sincs döntésre alkalmas „globális legjobb négyes”.

## 5. ROI Challenger — következő legjobb munka

1. **Újabb széles adatgyűjtés**: alacsony marginális ROI, mert a 35 projekt státusz/költség és 272 történeti hatás már megvan. Nem ezt választanánk.
2. **Még több szintetikus szorzóvariáns**: a mostani 40 konfiguráció után alacsonyabb ROI; nem oldja fel az azonosíthatatlan oksági együtthatót. Nem ezt választanánk.
3. **A vállalkozásszám → SmartCity-faktor tényleges forrásképletének célzott azonosítása** a meglévő, jóváhagyott kliensoldali forrásbizonyítékból, vagy korábbi *egy változós* mentett P1-trialekből, amennyiben tényleg van kontrollált összehasonlítás. **Ez a legjobb következő offline ROI**, ha a forrás hozzáférhető. Ha nincs bizonyíték, STOP: ne találjunk ki új együtthatót.
4. **Élő, kontrollált, visszaállítható preview**: végül ez a legerősebb kalibrációs bizonyíték lehet, de csak külön jóváhagyással, garantált mentés nélküli visszaállítással és változtatási joggal. Most nem engedélyezett.

## Státusz és elfogadási bizonyíték

**COMPLETED – ez az offline elemzési kör:** 30/30 indirekt rekord és 35/35 projektleltár; négy keret, 12 386 egyedi megengedett, 450k keret alatt vizsgált kombináció; 40 ellenőrzési feltétel mindegyik keretre; 17/17 célzott offline teszt; játékbeli írás 0. A teljes *feltételezett* keresési tér vizsgálata nem jelent globális optimumot.

**PARTIAL – teljes EcoSim P2–P5 stratégia:** a valódi oksági leképezés és P3–P5 átmenet továbbra is UNKNOWN. **Funkcionális készültség** UNKNOWN (nincs minden képességre mérési nevező); **integrált E2E** UNKNOWN (nincs tényleges, kalibrált P2 döntési preview); **éles használat** UNKNOWN (mentettség/végrehajtás nem igazolt); **változás (Δ)** UNKNOWN (nincs reprodukálható előző teljes százalékos mérés).

## Források

- 2026-11-05 P2 élő, csak olvasott, Brave–Codex: `Pasted text(20261105-122441).txt` és `EcoSim_P2_Brave_Codex_elo_ellenorzes_20261105.md`.
- Korábbi integrált bemenet és szűrő: `P2_joined_input.json`, `p2_joint_screen.py`, `effect_replay_r147.py`, `r142_proxy_reference.py`.
- Történeti projektkártyák: `ecosim_projects_20261030.json` (TEST Z, 2026-10-30), nem hitelesített P2 projektindex-következmény.
- `P2_indirect_business_sensitivity.json`: az összes 30 indirekt rekord és a rangsorfordulási érzékenységi mátrix; `indirect_business_sensitivity.py`: a reprodukáló szkript.
"""
Path('/mnt/data/EcoSim_P2_30_kozvetett_hatas_erzekenyseg_20261105.md').write_text(report,encoding='utf-8')
print('REPORT',len(report),len(report.splitlines()))
