# EcoSim R153 – Forrásképlettel integrált adó-/díjérzékenység

## Végcél és eredmény

A meglévő R152/R151 **egyetlen** ötéves döntési motorja most már a SmartCity kliensének eredeti `Re(e,t)` vállalkozóbarátság-képletét használhatja **feltételes, bemeneti paraméterekkel**. A forrásképlet a szolgáltatási döntés, a vállalkozási adó, a jármű- és építményadó, a piaci súlyok és indexosztók, valamint az aktív projektek szorzóhatása alapján számol. Ez az első, konkrét adózási számítási komponens, nem szintetikus +x% policy-hatás.

**Nem** rekonstrukciója az adóbevételnek, a pénznek, a migrációnak, a GDP-nek, az éves állapotátmenetnek vagy az egész ötödik évi indexnek. A piaci paramétereket NEM tudtuk hitelesíteni, ezért a demonstráció szintetikus; játékbeli döntési kapu STOP.

## Egyetlen meglévő integrációs út

- `tools/tax_response_r153.py` — a dokumentált `Re` képlet, az adó-/díjinput szigorú ellenőrzése, előjeles hatások, projektek által változó szorzó és felső korlát.
- `tools/decision_desk_r149.py` — meglévő R149 döntési jelentés és kereső. Az opcionális `tax_scenarios_path` mellett összeveti az ötéves projektjelöltek minden évét a megadott adó-/díjpályákkal; **nem indít második optimalizálót**.
- `tools/run_evidence_pipeline_r152.py` — az R152 eredeti történeti vagy hivatalos read-only bemenetét, az új adózási modul kimenetét és a meglévő döntési dossziét egyetlen adatfolyamban kapcsolja össze.
- `tools/decision_view_r149.py` — a forrásképletes összevetés hozzákerült a meglévő, offline, JavaScript nélküli HTML-jelentéshez. Korábbi duplikált pénzügyi kerettáblázatot javítja.

## Egyetlen, már végrehajtott történeti mintafolyamat

Az `inputs/tax_counterfactual_r153.synthetic.json` adatai **mesterségesek**, kizárólag a feltételes számítás tesztelésére szolgálnak. A `market.base_multiplier` kifejezetten úgy lett kiválasztva, hogy ugyanúgy 28,33 legyen a **történeti** vállalkozóbarátság, és ez semmilyen értelemben NEM igazolja a piac valós adóparamétereit.

A `results/R153_EVIDENCE_TO_TAX_AND_DECISION/` egy már elkészült 15 projektjelölt × 3 adó-/díjpálya (mindegyik 5 év) összekötött bemutató. Egyéni évi számszaki eredmény csak az adott, mesterséges piaci paraméterek feltételezése alatt érvényes. A kimenetben **nincs** hiteles adóbevétel, elkölthető keret, valós teljes index vagy győzelmi valószínűség.

A futás később, ha szeretnéd (MOST NEM SZÜKSÉGES):

```bash
cd R153_ECOSIM_DECISION_MVP
./run_r153_offline.sh
```

A jelenlegi bemeneti fájlt az `inputs/mvp_run.r153_synthetic.json` konfigurálja. Tényleges, szabályosan rögzített market/team adatoknál a kontextus, az indexsúlyok, a döntés és a forrásosztály egyezése kötelező, a szintetikus tax-fájl a CURRENT módban tiltott. A forrás- és csapatadatok felhasználói megadása nem független hitelesítés.

## Bizonyíték és falszifikáció

- A felhasználó által mentett `840.41fdc8e1.chunk.js` Webpack-modul 5168 `Re(e,t)` képletének pontos bájttartománya és SHA-256-ja: `evidence/R153_TAX_FORMULA_SOURCE_ANCHOR.json`. A teljes kliensprogramot nem másoljuk ide.
- Képletbeli `Math.min(1,...)` felső korlát igen; bizonyítatlan `Math.max(0,...)` alsó korlát **nem**.
- Adó- és díjnövelés a többi paraméter rögzítése mellett közvetlenül nem növelheti a vállalkozóbarátságot az adott képletben. Ez nem jelenti, hogy az összindex, az adóbevétel, a cégek száma vagy az ötéves eredmény monoton lenne.
- A projekt-szorzók a **tesztfordulós** 35 projekthez tartoznak; jövőbeli start/aktív projektmechanizmus szerveroldalon továbbra sem igazolt.
- Ha az explicit képletbemenetből visszaszámolt kiinduló vállalkozóbarátság 0,04 pontnál jobban eltér a megfigyelttől, az adatút STOP. Az eltérő current factor és szintetikus market-minta is STOP.
- Az elmúlt R152 eredmények 421 ellenőrzését a kvalifikáció dokumentáltan **megörökli, nem futtatja újra**. Az R153-ban 46 új célzott ellenőrzés PASS; a teljes, működő E2E mintát külön egy alkalommal végigfuttattuk.

## Következő blokkoló

A tényleges piaci tax-weights/divisors, az intézményi és vállalati átmenet, az operátori szabályok és a valós, időrendileg helyes terv–tény kalibráció továbbra is hiányzik. Az R153 a bizonyított részmodellt integrálja, nem ígér nyerő stratégiát.

Minden játékbeli írás, mentés, véglegesítés, jogosultságkerülés és élő API-hívás tiltott ebben a csomagban.
