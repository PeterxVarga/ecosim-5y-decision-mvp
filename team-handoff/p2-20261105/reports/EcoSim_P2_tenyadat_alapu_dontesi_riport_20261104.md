# EcoSim P2–P5 – P1 FACT-ra alapozott, feltételes döntés-előkészítés

**2026-11-04 · Selejtező I piac · Jutalom a nap végén · READ-ONLY / NO_GAME_ACTIONS**

## Eredmény és kritikus bizonyíték

- Az első kör tényleges SmartCity-indexe **58,87**, 2/7 hely; a vezetőé **58,94** (hátrány: 0,07).
- A lezárt P1 Excel **29/29** részletes tényezője illeszthető az eredeti R162 modellhez. A visszaszámított index **58,865979** (kerekítve 58,87).
- Az Excel P1 nettó eredménye **309 280,31 ECU**, de ez **nem igazolja a P2 elkölthető pénzét**.
- A P1-ben futó 6 és újonnan indított 4 projektet (12,13,14,22,23,24,27,32,34,35) **feltételezett** P2-aktívként kezelem; a P2 projektek aktuális állapota nem olvasható ki a P1 exportból.
- A keresés az eredeti R162 stratégiamotort használja az R232 **abszolút négy indítás/év** kapuval. 8 feltételes futás (4 keret × 2 célfüggvény), R160 kemény szabálysértés 0.

## Első P2-jelöltek – hipotetikus keretek

| Feltételezett éves ECU | Célfüggvény | P2-indítások | P2 konzervatív kártyateher ECU | Szcenárióban maradó ECU | P5 leképezett proxy Δ* |
|---:|---|---|---:|---:|---:|
| 75 000 | nominal | #8  #17  #26  #28 | 72 500 | 2 500 | +0.9650 |
| 75 000 | scenario_min | #8  #21  #28 | 69 000 | 6 000 | +0.9574 |
| 150 000 | nominal | #4  #16  #21  #26 | 149 000 | 1 000 | +1.3589 |
| 150 000 | scenario_min | #4  #16  #21  #26 | 149 000 | 1 000 | +1.3589 |
| 300 000 | nominal | #8  #21  #26  #33 | 293 000 | 7 000 | +1.5847 |
| 300 000 | scenario_min | #1  #8  #26  #33 | 284 400 | 15 600 | +1.5847 |
| 450 000 | nominal | #4  #8  #16  #33 | 316 000 | 134 000 | +1.6222 |
| 450 000 | scenario_min | #4  #16  #31  #33 | 359 000 | 91 000 | +1.6222 |

\* A proxy Δ nem az eredményül kapott SmartCity-index és nem tényelőrejelzés; a köztes szakpolitikák, versenytársak és modellezetlen hatások hiányoznak.

## ROI Challenger – három lényegileg különböző út

1. **Az eddigi R258-as, P1 PLAN terv folytatása:** elvetve, mert van új P1 FACT; rossz kiindulópont.
2. **Új vagy második optimalizáló fejlesztése:** elvetve, mert az R162/R232 újrafelhasználható és a valódi blokkoló az aktuális P2 forrás, nem a hiányzó új algoritmus.
3. **P1 FACT → meglévő R162/R232 → P2 szcenáriók → élő P2 keret/projektállapot-hitelesítés:** kiválasztva; ez ad értékes, de nem önhatalmú döntés-előkészítést.

## Döntési értelmezés

- **Óvatos feltételes jelölt, 150k/év:** #4 Körforgásos gazdaság mintaprojekt, #16 Nyitott Alkotó és Innovációs Terek, #21 Közlekedési Múzeum, #26 Reptér elérhetőség javítása; P2 kártyateher 149 000 ECU. A két célfüggvény azonos P2 csomagot adott.
- **Középső, 300k/év:** a nominális terv #8/#21/#26/#33 (293 000 ECU), a scenario_min #1/#8/#26/#33 (284 400 ECU). A csomag ezért érzékeny a célfüggvényre.
- **Magasabb, 450k/év:** a nominális P2 #4/#8/#16/#33 (316 000 ECU), scenario_min #4/#16/#31/#33 (359 000 ECU). Nem indokolható magasabb kiadás csak a P1 nettó eredményéből.
- **75k/év visszafogott alternatíva:** a két célfüggvény eltér; nincs stabil egyetlen P2-javaslat.

## Kötelező élő kapuk P2 előtt

1. P2 **Pénzügyek**: ténylegesen elkölthető pénz és kötelezettségek, hitelek, valamint az új projektek P2 várható költsége.
2. P2 **Projektek**: a 10 feltételezett aktív projekt valódi státusza, új projektindítások száma, az új kártyák költségei/előfeltételei.
3. P2 **Összefoglalás**: P2 PLAN index és FACT megkülönböztetése; szakpolitikai, intézményi, közlekedési döntések és készpénzhatások külön vizsgálata.

**STOP:** ez a riport sem projektindítást, sem Save-t, sem Next Period műveletet nem engedélyez.

## Reprodukálhatóság és bizonyítékszint

- Forrás Excel SHA256: `23a76fd044fe698e66a18577642825eca1f058d5715cd8f85b05d0a3b9fd38ab`
- Forrás kör ZIP SHA256: `6cb7279bb199a05b7bd484cd660b693ca4a4d681c75246964d4ee271a8cdbeb4`
- Pontosan 29 első körös ténytényező; 8 R232 abszolút-4 feltételes modellfutás. R160 kemény auditjelzés: 0. Mindegyik futás offline; nincs jogosultság- vagy szerveroldali ellenőrzés.
- Az azonosított P2-források hiánya: éles projektstátusz, spendable cash, hitel-/piaci szabályok, intézmény-/adó-politika és versenytársak jövőbeli válasza UNKNOWN.
- Funkcionális készültség, integrált E2E és éles készültség: UNKNOWN (nincs teljesprojekt-nevező); P2 mentés és P2 projektindítás: 0 végrehajtva ebben a körben.
