EcoSim P2 R3 – vállalkozásszám-faktor empirikus hipotézis
2026-11-05 | Csak offline elemzés | Nincs játékbeli írás

Bizonyíték: 7 csapat P1 tényexportja, 2 teszt Z snapshot,
1 visszaállított R258 négyprojektes P1 UI-próba, 1 P2 élő terv.

Futtatás a ZIP kibontott mappájából:
  python3 EcoSim_P2_vallalkozasszam_R3_empirikus_kalibracio.py \
    --input EcoSim_P2_vallalkozasszam_forrasmegfigyelesek_20261105.json \
    --output EcoSim_P2_vallalkozasszam_empirikus_R3_20261105.json
  python3 -m unittest -q test_EcoSim_P2_vallalkozasszam_R3.py

A modell keresési tér 12 386 potenciális, feltételesen jogosult projektcsomag.
A számok nem EcoSim API-számításból és nem szerverforrásból származnak.

Forrásellenőrzés: a forrásmegfigyelések JSON-ban eredeti fájlnév
és SHA-256 szerepel. A ZIP nem tartalmazza az eredeti teljes P1 xlsx-et,
P1 history ZIP-eket vagy R258 privát receipteket; azok a tulajdonos
feltöltött történeti forrásai. A reprodukció a minimálisan kivont
megfigyeléseken történik.

A munkafüzet R3 új munkalapjai:
- R3 képlet
- R3 P1 bizonyíték
- R3 rangsor
A korábbi R2 munkalapok megmaradtak; a R2 szelő nem azonos
az új R3 éves növekedési hipotézissel.

Játékbeli STOP: Start/Save/Next Period/API write nem része a körnek.
