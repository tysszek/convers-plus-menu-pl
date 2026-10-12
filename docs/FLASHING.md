# Procedura bezpiecznego użycia

Repozytorium zawiera dwie niezależne procedury. Pełny łańcuch zmian naszego menu V5.2 → V5.3.4 opisuje [odrębna instrukcja](odtworzenie-pelnego-patcha-v5-3-4.md). Ten plik zawiera skrót tej procedury oraz osobny wariant M0RTAR/Motral.

## Wspólne przygotowanie

1. Zapisz własne kopie firmware CD, ED, AA/SBL, bootloadera i EEPROM.
2. Zweryfikuj, że kopie można odczytać i przechować poza komputerem używanym do flashowania.
3. Nie publikuj VBF, EEPROM ani zrzutów pamięci — mogą zawierać VIN.
4. Użyj stabilnego zasilania i nie przerywaj programowania.

## Wariant A — pełny patch V5.2 → V5.3.4

Ten wariant zaczyna się od zweryfikowanego CD V5.2 z wcześniejszym modem Bluetooth Audio. Kolejne etapy muszą być wykonane w tej kolejności:

~~~bash
python tools/build_menu_labels_v531_physical_fix.py CS7T-14C026-CD_V5_2.vbf CS7T-14C026-CD_V5_3_2.vbf
python tools/apply_theme_labels_v533.py CS7T-14C026-CD_V5_3_2.vbf CS7T-14C026-CD_V5_3_3.vbf
python tools/apply_theme_labels_v534.py CS7T-14C026-CD_V5_3_3.vbf CS7T-14C026-CD_V5_3_4.vbf
python tools/apply_ed_phone_fix_v53.py CS7T-14C026-ED_BAZA.vbf CS7T-14C026-ED_V5_3.vbf
~~~

`build_menu_labels_v531_physical_fix.py` zawiera bazowy etap `apply_menu_labels_v53.py`, dlatego nie uruchamiaj go dodatkowo na tej samej bazie.

Zmiany obejmują `Płyta CD`, `Multimedia USB/BT`, `Ostrz. kolizji`, `Czujność`, `Kolory`, `Zaawansowane`, `Tempomat`, sześć aktywnych nazw motywów oraz `Dokladnie` → `przychodzi`. Techniczne `Akcept.` → `Akcept` zachowuje rozmiar zasobu ED.

Po każdym etapie sprawdź wynik, a przed wgraniem wykonaj końcową walidację:

~~~bash
python tools/vbf_tool.py verify CS7T-14C026-CD_V5_3_4.vbf
python tools/vbf_tool.py verify CS7T-14C026-ED_V5_3.vbf
python -m unittest discover -s tests -v
~~~

Nie trzeba zmieniać AA.

## Wariant B — M0RTAR/Motral, dodatkowe menu Advanced

Ten wariant stosuje się do rozpoznanego M0RTAR CD VBF, a nie jako kolejny etap powyższego łańcucha:

~~~bash
python tools/patch_vbf_menu_pl.py CS7T-14C026-CD.vbf CS7T-14C026-CD_MENU_PL.vbf
~~~

Opcjonalnie można dodać `--strict-hash`. Patcher rozpoznaje strukturę cztero- lub pięciopozycyjnego menu, tłumaczy znane wewnętrzne pozycje Advanced i raportuje nieznane jako `UNTRANSLATED`. Nie dodaje funkcji ani pozycji.

Jeżeli narzędzie zwróci `REFUSED`, zatrzymaj się. Oznacza to niezgodną wersję, błąd checksumy albo brak oczekiwanej struktury. Nie obchodź kontroli.

## Ważne

Patcher nie komunikuje się z licznikiem i nie wykonuje flashowania. Odpowiedzialność za narzędzie programujące, zasilanie i procedurę recovery pozostaje po stronie użytkownika. Nie dodano tymi patchami komunikatu `Niski poziom płynu chłodniczego` ani `Ostrzeżenie DPF` — wymagają one osobnej obsługi funkcjonalnej CAN/PCM.