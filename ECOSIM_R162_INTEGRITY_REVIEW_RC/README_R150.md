# EcoSim R150 — mintán belüli döntésminőség és offline újratervezési összehasonlítás

## Cél

Az R149 döntési MVP továbbfejlesztése az **évenkénti döntési felülvizsgálat** felé. Az R143–R149 meglévő `strategy_5y.py` marad az egyetlen optimalizáló; sem új modell, sem párhuzamos kereső nincs.

## Új képességek

1. **Mintán belüli feltételes Pareto-szűrés:** a kereső teljes, korlátos jelölt-uniójából számolja a nem dominált terveket minden hipotetikus költségkeretre, nem csak a korábbi maximum húsz megjelenített találatból. Több cél: éves projektköltségek, ismert részleges indexproxy, szélső *illusztratív* proxy, nem leképezett hatások száma és azonos évben bizonyítatlan feltétel. Az ismeretlen hatások száma nem előjel vagy bizonyított kockázati mérték. A front nem nyerőstratégia-bizonyíték.
2. **Mintán belüli részleges alternatívaköltség:** minden, egy keretbe beleférő tervnél mutatja az eltérést a *vizsgált mintában* legjobb ismert proxyhoz és illusztratív stresszelt proxyhoz képest. Ez nem valós játékbeli regret, valószínűség vagy konfidenciaintervallum.
3. **Kezdőév-csoportok:** az azonos első lépéssel induló ötéves jelöltek külön családba kerülnek; az előfordulás nem esély, az indexsáv nem előrejelzési intervallum.
4. **Offline két jelentés összehasonlítása:** `tools/compare_runs_r150.py` megkülönbözteti az azonos periódusú csak terv-összevetést, az egymást követő évek pusztán leíró újratervezését, a történeti demót és az összemérhetetlen csapatokat. Egyik esetben sem állít oksági hatást vagy éves előrejelzési pontosságot.
5. **Kezdőévi címkejavítás:** az R149 statikus döntési HTML immár `start_year` szerint címkézi az éveket (nem mindent É1-ként), és az R150 Pareto-táblát is megmutatja.

## Bemenet és kimenet

A korábbi R149 JSON- és konfigurációs séma változatlan. `results/R150_MVP_DEMO/DECISION_DESK.json` új mezői:
- `r150_sampled_quality` — frontok, feltételes relatív veszteség, elsőéves jelöltcsaládok.
- `source_context` — csapat, piac, periódus, terv/tény eredet, csak a bemeneti deklaráció, független hitelesítés nincs.
- `start_year` — nem kell az évszámot a listapozícióból kitalálni.

A helyi összehasonlítás opcionális formája:

```bash
python3 -I -B tools/compare_runs_r150.py \
  --before results/R149_MVP_DEMO/DECISION_DESK.json \
  --after results/R150_MVP_DEMO/DECISION_DESK.json \
  --out results/offline_comparison.json
```

Mindkét jelentés inputként különálló, *már elkészült* offline fájl. Két jelenlegi/historikus példától nem lesz valós tény-visszamérés.

## Kemény megállási feltételek

- A bemeneti költségkeretek hipotézisek, és nem szerver által jóváhagyott költségvetés.
- A keresés **korlátos heurisztika**, ezért még a mintán belüli Pareto-front sem globális front.
- A projektindex csak bizonyítottan leképezhető részhatás; hiányzik a teljes vállalati, intézményi, adó- és migrációs dinamika.
- A paired-PLAN egyeztetés nem megfigyelt éves tényváltozás.
- Az aktuális konfigurációból hiányzó információt nem helyettesíti a 2026-10-30-i tesztforduló.
- A forrásra hivatkozó felhasználói állítás nem önmagában hitelesített szerverforrás.
- **`gameplay_gate=STOP`**, nincs EcoSim-írás, nincs automatikus projektindítás.

## Utolsó következő blokk

A helyes következő eredmény már nem újabb offline rangsorszámítás, hanem egy hiteles, engedélyezett **aktuális market/team/period** bemenet és egy szabályos, párba illesztett EcoSim tervelőnézet. Ez az R150 architektúrájával új kód nélkül is feldolgozható, de külső bizonyíték nélkül nem állítunk ötéves predikciós pontosságot.
