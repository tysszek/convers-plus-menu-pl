# Credits i autorstwo

## Oryginalny mod Advanced

Patch jest przeznaczony dla firmware zmodyfikowanego przez autora moda
M0RTAR/Motral. Ten projekt nie przypisuje sobie autorstwa dodania menu
Advanced, Digital speed, Engine temp & Voltage ani logiki pomiarowej.

## Format menu i narzędzia referencyjne

Struktura relokowanego menu oraz sposób bezpiecznego klonowania deskryptora
zostały opracowane na podstawie publicznego projektu:

<https://github.com/andrzejogh/convers-gauge-sweep>

Autor projektu referencyjnego: GitHub `andrzejogh`. Odpowiednia kopia licencji
MIT znajduje się w `LICENSE_UPSTREAM_MIT`.

## Nasz dodatek

Ten projekt dodaje wyłącznie polskie etykiety ASCII do istniejącego menu
M0RTAR. Obsługuje bazowe menu czteropozycyjne oraz istniejące relokowane menu
rozszerzone o `Gauge sweep` lub inne rekordy. Nie zmienia formatterów
temperatury, napięcia, prędkości, stanu paliwa ani logiki zapisu ustawień.

Pozycja `Gauge sweep` pochodzi z osobnego projektu autora moda i nie jest
autorskim dodatkiem tego repozytorium; tutaj jest tylko lokalizowana.

## Oddzielny patch Bluetooth

Patch Bluetooth jest utrzymywany osobno w:

<https://github.com/tysszek/convers-plus-bt-audio-v5-2>

Odbiór metadanych Bluetooth w tamtym projekcie opiera się na:

<https://github.com/andrzejogh/convers-bt-audio>
