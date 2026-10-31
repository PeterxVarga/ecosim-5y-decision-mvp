# R155 — Source-Anchored Operating-Cash MVP (2026-10-31)

## Kész, integrált szoftver

R154-ből továbbépített egyetlen offline döntési dosszié. 6 forrásbeli szolgáltatásidíj-bevétel, 8 bérkomponens és 7 intézményi anyagköltség-komponens; öt éves explicit exogén városállapot és működési pálya; 21 forrásrészlet SHA-256; kapcsolás az R154 négyadó-pénzügyéhez, R153 részindexhez és az R149 projektkereséshez. A projektkeresés változatlan; új, mintabeli háromtengelyes operating Pareto. JSON + offline HTML + Markdown.

## Bizonyítható, de korlátozott eredmény

- Az új R155 kvalifikáció a csomag elkészítésekor a korábbi eredeti JS-t tartalmazó, lezárt helyi bizonyítékból mind a 21 képletrészletet újrahitelesítette; eredmény a `results/R155_QUALIFICATION.json` fájlban.
- A korábbi R153/R154 regressziós modulok is a végső összevont kiadási teszt részét képezik (`qualify_once.sh`). A régebbi 421 ellenőrzés nem tekintendő most újra lefuttatottnak.
- Valós 5. évi pontosság: `UNKNOWN`, tényleges rendelkezésre álló pénz: `UNKNOWN`, aktuális versenypiaci paraméterek: `UNVERIFIED`. A régi R94-adat nem éles állapot.
- Az EcoSim szerveren **0 művelet**, nincs engedélyezett játékbeli intézkedés.

## Következő nagy, értékes lépés

Nem további általános keresőfejlesztés. Valódi, azonos eredetű market/team/financial/institution pillanatkép és későbbi ugyanazon periódusú terv–tény pár; ehhez a már létező intake/kalibrációs kapukat használnánk. A klienskód szerinti vállalkozásszám-átmenet csak hiánytalan lagelt piac/verseny mezőkkel valósítható meg bizonyító erejűen.
