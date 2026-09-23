# Procedura bezpiecznego użycia

1. Zapisz własne kopie firmware CD, ED, bootloadera i EEPROM.
2. Zweryfikuj, że kopie można odczytać i przechować poza komputerem używanym do
   flashowania.
3. Pobierz własny plik `CS7T-14C026-CD.vbf` z firmware M0RTAR/Motral. Może to
   być wariant czteropozycyjny albo wariant z wcześniej dodanym `Gauge sweep`.
4. Uruchom patcher z katalogu projektu:

   ```bash
   python tools/patch_vbf_menu_pl.py CS7T-14C026-CD.vbf CS7T-14C026-CD_MENU_PL.vbf
   ```

5. Sprawdź komunikat `OK` oraz checksumy pliku wyjściowego.
6. Do wgrania użyj wyłącznie zaakceptowanego pliku CD. Ten patch nie wymaga
   ponownego wgrywania ED ani bootloadera. Jeżeli narzędzie rozpozna wariant
   pięciopozycyjny, w raporcie pojawi się `5-item Gauge Sweep`. Jeżeli pojawi
   się nowa pozycja, zostanie wypisana jako `UNTRANSLATED` i pozostanie bez
   zmian.

Jeżeli pojawi się `REFUSED`, zatrzymaj się. Oznacza to niezgodną wersję, błąd
checksumy albo brak oczekiwanej struktury moda. Nie obchodź kontroli.

## Ważne

Patcher nie komunikuje się z licznikiem i nie wykonuje flashowania. Odpowiedzialność
za narzędzie programujące, zasilanie i procedurę recovery pozostaje po stronie
użytkownika. VBF i EEPROM mogą zawierać VIN — nie wysyłaj ich do GitHuba ani do
issue.
