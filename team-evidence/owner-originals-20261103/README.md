# EcoSim – eredeti állományok és R257/R258 történeti megfigyelések

Ez a könyvtár a tulajdonos kifejezett kérésére publikált további EcoSim-versenyadatokat tartalmaz egy **PUBLIC** GitHub-repositoryban.

- `original-source-inventory.json` — a ChatGPT Library-ben elérhető öt eredeti XLSX/ZIP fájl neve, mérete, SHA-256 hash-e. **Ez a leltár, nem az eredeti bináris fájlok.**
- `R238_RECEIPT_RECONSTRUCTED_FROM_ARCHIVE.json` — a felhasználó által szolgáltatott R238 ZIP-ben talált JSON-nyugta mezőinek visszaállított változata. Az eredeti ZIP még nincs GitHubra feltöltve; a ZIP-ben lévő nyugta eredeti SHA-256 értéke: `d5497d8e5d0a12c4cf48f61d633de2d639d4d2ce1cf253f8fed099dc5fc5a464`. A visszaállított JSON bájtszintű egyezése nem igazolt.
- `R257_R258_HISTORICAL_AB_REPORT_HU.md` — a korábbi élő UI A/B-próbáról készült történeti összefoglaló, pontosan megjelölt korlátokkal. **Nem** az eredeti R257/R258 nyugta.

A korábbi, forrásazonosított szoftverfejlesztések és a Library-importált adatok a `main` ágon már a `team-handoff/` és `team-evidence/library-20261103/` helyeken találhatók.

**Nincs még ezen a `main` ágon:** az öt eredeti ZIP/XLSX bájtsora, a Fedora gépen maradt eredeti R257/R258 könyvtárak, valamint az ezekhez tartozó teljes tulajdonosi helyi R239–R256 fájlok. A tartalmi kivonat nem azonos a forrásfájl feltöltésével. A GitHub-nyugta nélküli fájlok státusza `NOT_UPLOADED`.

**Adatvédelmi megjegyzés:** a repó nyilvános, a versenyhez kötött csapat- és stratégiai adatok bárki számára hozzáférhetők. Bejelentkezési cookie, API-token, jelszó és titkos kulcs nem kerülhet ide.

**Műveleti kapu:** `GAME_ACTION_GATE=STOP`, `NO_START`, `NO_SAVE`, `NO_NEXT_PERIOD`. A játék szerveroldali mentett állapota UNKNOWN.
