# Status projektu

Wersja publiczna jest przygotowana jako patch językowy dla struktury menu
M0RTAR 1412-FL. Patcher przechodzi testy strukturalne i waliduje VBF przed oraz
po modyfikacji.

Zakres obejmuje menu bazowe oraz menu rozszerzone o `Gauge sweep` lub kolejną
pozycję. Znane etykiety są tłumaczone, a nowe pozycje pozostają niezmienione i
pojawiają się w raporcie jako nieprzetłumaczone. Patch nie dodaje testu
wskazówek ani patcha Bluetooth — te funkcje są utrzymywane osobno. Bluetooth
nie zmienia struktury menu Advanced.

Jeżeli narzędzie odmówi pracy, nie należy omijać kontroli struktury VBF/menu.
Opcjonalna kontrola SHA-256 jest dostępna przez `--strict-hash`. Do zgłoszenia
problemu wystarczy komunikat z narzędzia i suma pliku; nie należy publikować
firmware ani zrzutu EEPROM.
