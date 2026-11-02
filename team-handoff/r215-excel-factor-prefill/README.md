# R215 – forrásellenőrzött Excel-faktor-előkitöltés

## Felhasználói képesség
Az R213 eredeti beolvasóját újrahasználva a következő, azonos 374 soros szerkezetű városi exportból egyetlen paranccsal előállítható az R156 29 mutatót és indexet tartalmazó faktor-CSV. Ez 30 mező kézi beírását válthatja ki. A régi R213 működés változatlan; az új opció más ötcsapatos oszlopneveket is megenged.

## Használat aktuális, ténylegesen exportált Excelből
bash team-handoff/r215-excel-factor-prefill/run_private.sh --new-workbook /private/current_city.xlsx --team 'A SAJÁT AKTUÁLIS CSAPAT' --source-id 'CURRENT_OPERATOR_OBSERVED_CITY_EXPORT' --out-dir /private/new_r215_report

Az eredmény a privát R215_FACTORS_FOR_REVIEW.csv és R215_RECEIPT.json. A CSV-t az eredeti R156 offline űrlap factors_csv mezőjébe lehet másolni. A rekordok forrásazonosítóval és SHA-val rendelkeznek.

## A kulcsfontosságú tiltások
Az Excelben látott érték lehet kiinduló FACT, nem feltétlenül a tényleges PLAN oszlop. Az így készített CSV csak ellenőrzésre szánt előkitöltés, nem hoz létre automatikusan CURRENT_READONLY PLAN adatcsomagot. R156/R191/R192/R214 csak az adott időszak ténylegesen megfigyelt tervével futhat. A csapatnevet nem találgatjuk; a csapatok azonosságát az eredeti tesztfordulóval nem állítjuk.
Az eredeti történeti XLSX SHA kötelező. Az azonos cellatartalmú, eltérő bináris másolatot nem fogadjuk új adatsorként. Pontosan 374 címkézett sor, az eredetivel azonos sorrend és 29/29 numerikus faktor + index szükséges. Eltérő játékformátum HOLD.
A 35 projektstátuszt, 35 kártyát, hat súlyt, kapot, pénzügyi keretet, hiteleket és a piac azonosítóját a program nem találja ki. Az éles forrás hitelességét sem igazolja. Játékművelet: STOP, 0 írás.

## Natív teszt
bash team-handoff/r215-excel-factor-prefill/qualify_private.sh
Az eredeti két privát workbookot, ideiglenesen módosított egycellás tesztfájlt, a téves csapatot, hamis forrásazonosítót, hiányos faktort és sorszerkezet-eltérést teszteli; újraellenőrzi az R213 forrásillesztését is.
