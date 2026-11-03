# EcoSim R227 – teljes Excel → aktuális UI forráslefedettségi keresztwalk

**Forrásadat:** `X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx`  
**Excel SHA-256:** `a130d6606c4488112c8825d79d5fb6aaa65a65f4dca7d1e1f9e4029cdafe53f4` (helyben függetlenül újraellenőrizve)  
**A források státusza:** felhasználói XLSX-export és bejelentkezett, csak olvasható böngészős megfigyelések; egyik sem szerver által hitelesített döntésengedély.

## Bizonyított tények

- **374/374** eredeti, sorszámhoz kötött Excel-adatsor átvéve, **7 csapattal**.
- Ezekből a saját csapat **324 numerikus** és **50 nem numerikus/fejléc** sort tartalmaz.
- A korábban rögzített R226 **19** szerkesztőmezője mellett a most látható **Adók** nézet **4** adókulcsmezője ellenőrizve; összesen **23** megfigyelt UI-szerkesztőmező.
- **19/23** a megfelelő Excel-sorral **azonos terület/címke/p0 érték** szerint egyezik.
- **4/23** esetében NINCS egyértelmű egyedi Excel-sor: **Oktatás/Bérek, Oktatás/Képzés, Oktatás/Fejlesztés, Hosszú távú hitelek/Felvétel-Visszafizetés**.
- Az Excelben **355** további sor nincs egyetlen megfigyelt UI-szerkesztőmezőhöz rendelve; ez **nem** azt jelenti, hogy nincs megfelelő mező a játék másik, még meg nem figyelt alnézetében.
- A tíz főmenü elérhető; 27 látható nézetválasztó címke nem egyenlő 27 teljesen beolvasott alnézettel.

## Biztonsági határ és nyitott kapuk

Az XLSX egy P0 kiinduló állapotot biztosít, nem engedélyezett P1 döntéseket.
Az inputmezők megjelenése nem bizonyítja a mentett P1 értéküket.
A **23 bemeneti tartomány**, **23 okozati faktor/pénzügyi hatás**, az I. piaci projektlimit és a valóban elkölthető összeg továbbra is **UNKNOWN**.

**R191 HOLD, R192 időablak HOLD, R214 éles tanácsadási kapu HOLD; játékírás 0.**  
A nyerő ötéves stratégia még nincs validálva.

## Fájlok

- `ecosim_R227_forraslefedettseg.xlsx` — 7 lap: áttekintés, 374 Excel-sor, 23 UI-mező, Excel-szekciók, 10 főmenü, hiányzó bizonyítékok, források.
- `ecosim_R227_forraslefedettseg.json` — teljes forrásazonosított, géppel feldolgozható megfeleltetési eredmény.
- `ecosim_R227_dontesi_crosswalk.csv` — a 23 döntési mező emberileg ellenőrizhető kivonata.

## Következő legnagyobb ROI

Ne ismételjük meg a korábban beolvasott 374 Excel-sort. A döntéshez először a **szerkeszthető mezők tényleges jogszerű korlátait**, a P1 választott értékeket, illetve az eredeti R153/R154/R145 hatásfüggvényeinek hiteles bemeneteit kell megvizsgálni. A projektindítási limit és a finanszírozás külön, kötelező kapu marad.

**Eredmény:** COMPLETED (R227 forráskeresztwalk); teljes EcoSim: PARTIAL.