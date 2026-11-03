# R199 – Az R195 teljes ötéves projekttervei az eredeti városi részmodellekben

**Research → Reuse → Build.** Az R198 0 teljesen azonos projektütemezést talált az R195 két terve és az R149 15 jelöltje között. Ezért nem lehetett a régi pénzügyi eredményeket átcímkézni. Az R199 változtatás nélkül újrafelhasználja az R153 adóhatás-, R154 négyadó-bevétel-, R155 hat szolgáltatási díj és intézményi részkiadás-, valamint R159 komponensenként időzített cash-flow függvényeket.

## Mit ellenőriz?

1. R195 mindkét eredeti R191 nyugtájának és R160-auditjának újraellenőrzése az eredeti R195 komparátorral.
2. R197 azonos kiinduló csapatállapot SHA-256 egyezés; az R149 döntési dosszié és minden R153–R155 input SHA egyezése.
3. Az eredeti R149 15 jelöltjének projektproxyja és az R153, R154, R155 kimenetek független modell-visszajátszása. A változás HOLD.
4. Pontosan az R195 mindkét ötéves projektütemezése kerül az eredeti R153 és R159 modulokba. Az eredmény 2 x 3 = 6 projekt-adó-működési párosítás.
5. Évenkénti projektlista/költség- és finanszírozási STOP ellenőrzés.

Ez **nem** új optimalizáló. A projektindex változása és az R195 abszolút robusztus modellértékei nem adhatók össze, mert különféle definíciók. A pozitív adó- és díjpénzáram csak részleges, szintetikus ellenpélda, nem használható el költségkeretként.

## Korlátok

Az R199 kizárólag történeti/szintetikus bemenetet enged. A current mód HOLD. A valódi hitel-, támogatás-, lakossági-, vállalkozási és nem lefedett intézményi hatások, az éves állapotátmenet és a szerver szerinti pénzügyi időzítés továbbra sem bizonyított. A három bemutatott adó-/intézményi pálya előre megadott, nem teljes döntéstérre végzett keresés.

## Reprodukció Fedora gépen

Az R195 eredeti futásának nyugtái és az azonos kiinduló állapotú R149 döntési dosszié szükségesek; ezek nem tartalmaznak belépési adatokat.

    ROOT="$HOME/Downloads/ecosim-r199-native-20261102/repo"
    TR="/tmp/ecosim-r195-tradeoff-2qiKmOEe"
    POLICY="$HOME/Downloads/ecosim-r197-research-L62ruUfD/policy/DECISION_DESK.json"

    python3 -I -B "$ROOT/team-handoff/r197-r198-city-join/tools/exact_policy_replay_r199.py" \
      --tradeoff "$TR/TRADEOFF.json" \
      --max-receipt "$TR/max_receipt.json" \
      --reserve-receipt "$TR/reserve_receipt.json" \
      --decision-desk "$POLICY" \
      --out-dir "$HOME/Downloads/ecosim-r199-native-20261102/native-output"

    python3 -I -B -m unittest discover \
      -s "$ROOT/team-handoff/r197-r198-city-join/tests" \
      -p "test_exact_policy_replay_r199.py" -v

A kimenet R199.json és R199_HU.md. Az output könyvtár már meglévő állapotában a futás STOP-pal leáll, nem írja felül a bizonyítékokat.

**Játékbeli művelet: 0. GAME_ACTION_GATE=STOP. PR draft marad a független kontroll után is, éles használathoz aktuális ellenőrzött EcoSim-state szükséges.**
