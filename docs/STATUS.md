# Status projektu

Repozytorium zawiera dwa jasno rozdzielone warianty patcha dla Convers+ 1412-FL.

## Pełny wariant menu V5.2 → V5.3.4

To jest aktualna ścieżka naszego softu. Obejmuje:

- zmiany menu głównego `Zmieniacz płyt CD` → `Płyta CD` oraz `wejście Auxiliary` → `Multimedia USB/BT`;
- nagłówki `Forward Alert` → `Ostrz. kolizji`, `Driver Alert` → `Czujność`, `Colour themes` → `Kolory`, `Advanced` → `Zaawansowane`;
- `Cruise Control` → `Tempomat`, także w bezpośrednich nagłówkach widocznych po wejściu do podmenu;
- sześć aktywnych motywów: `Ciemny`, `Niebieski`, `Szary`, `Czerwony`, `Zielony`, `Nocne niebo`;
- komunikat telefonu `Dokladnie` → `przychodzi`, z technicznym skróceniem sąsiedniego `Akcept.` → `Akcept` dla zachowania rozmiaru ED.

Pełna kolejność skryptów i oczekiwane sumy są w [procedurze V5.2–V5.3.4](odtworzenie-pelnego-patcha-v5-3-4.md).

V5.3.4 jest zweryfikowany strukturalnie i checksumami VBF. Skrypty sprawdzają wersję wejściową, adres, długość i oczekiwane dane przed zapisem. Fizyczne wgranie należy potwierdzić na konkretnym egzemplarzu licznika po zachowaniu kopii recovery.

## Wariant M0RTAR/Motral

Osobny patch `patch_vbf_menu_pl.py` tłumaczy dodatkowe, relokowane menu Advanced, w tym jego wewnętrzne pozycje. Obsługuje rozpoznane warianty cztero- i pięciopozycyjne, nie dodaje funkcji i nie zmienia logiki pomiarów. Ten wariant nie jest automatycznie kolejnym krokiem pełnego łańcucha V5.2 → V5.3.4.

## Poza zakresem

Nie dodano komunikatu `Niski poziom płynu chłodniczego` ani `Ostrzeżenie DPF`. To osobne zmiany funkcjonalne wymagające potwierdzenia i obsługi zdarzeń CAN/PCM. Nie należy omijać kontroli struktury VBF ani publikować firmware i EEPROM.