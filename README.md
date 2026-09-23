# Polskie menu Advanced dla moda M0RTAR/Motral

Mały, bezpieczny patch językowy dla popularnego moda Ford Convers+ 1412-FL.
Tłumaczy istniejące dodatkowe menu Advanced, które w bazowym modzie pozostaje
po angielsku. Nie dodaje nowej funkcji i nie zmienia sposobu obliczania ani
wyświetlania wartości.

## Rozpoznawane warianty

Patcher nie zgaduje wersji po nazwie pliku. Przed zmianą sprawdza długość,
strukturę VBF, aktywny wskaźnik ekranu, nagłówek menu, liczbę rekordów i typy
pozycji. Poniższe sumy są znanymi wariantami referencyjnymi:

| Wariant wejściowy | Liczba pozycji | SHA-256 payloadu |
|---|---:|---|
| M0RTAR/Motral, bez Testu wskazówek | 4 | `9c4b3b051a9dd1705d2acd27658d25fb71a52f5c2a20f5595f4885016a3661a1` |
| M0RTAR/Motral + Gauge Sweep | 5 | `0c91f7e940b4e48c729a5f8b0a788c2296fb51c645c1a18db60e76c3497dd034` |

Wariant pięciopozycyjny musi już zawierać pozycję `Gauge sweep`. Ten patch nie
dodaje testu wskazówek — tylko zmienia jego etykietę na `Test wskazowek`.

Domyślnie patch działa na zgodnych strukturalnie wariantach tego moda, więc
dodatkowy patch Bluetooth nie powoduje odrzucenia pliku. Opcjonalny przełącznik
`--strict-hash` ogranicza pracę wyłącznie do dwóch powyższych sum referencyjnych.

## Tłumaczone pozycje

| Oryginał | Wersja PL bez znaków diakrytycznych |
|---|---|
| Advanced | Zaawansowane |
| Digital speed | Predkosc cyfrowa |
| Gauge sweep | Test wskazowek |
| Engine temp & Voltage | Temp. silnika i napiecie |
| on main | Na ekranie glownym |
| in standby | W trybie czuwania |

Użyto ASCII, ponieważ mapa polskich glifów w relokowanym menu M0RTAR nie jest
potwierdzona. Dzięki temu nie pojawiają się przypadkowe znaki zamiast `ą`, `ę`,
`ł` itd.

## Co patch robi

Patch:

1. sprawdza dokładny wariant programu i checksumy VBF,
2. rozpoznaje relokowany deskryptor Advanced M0RTAR,
3. dla wariantu czteropozycyjnego klonuje go do pustego obszaru `0xEF`,
4. dla wariantu pięciopozycyjnego korzysta z istniejącego klonu z Gauge Sweep,
5. podmienia wszystkie wskaźniki językowe tytułu i pozycji,
6. przekierowuje wskaźniki ekranowe tylko tam, gdzie wymaga tego wariant,
7. ponownie liczy CRC16 payloadu i checksum pliku VBF.

Przed zapisem patch odczytuje aktualne etykiety. Znane tłumaczy, a nieznane
pozostawia bez zmian. W raporcie pojawi się wtedy np.:

```text
UNTRANSLATED item_5: New future option
```

Nieznana pozycja nie jest usuwana, przesuwana ani zastępowana przypadkowym
tekstem.

Nie zmienia ED, bootloadera, formatterów pomiarów ani pamięci EEPROM.

## Czy Bluetooth dodaje pozycję do menu?

Nie. Publiczny patch Bluetooth służy do odebrania metadanych utworu z CAN i
przekazania ich do istniejącego toru mediów. Nie dodaje pozycji do menu
Advanced. Pozycję `Gauge sweep` dodaje osobny patch testu wskazówek, dlatego
patch językowy rozpoznaje oba warianty: 4- i 5-pozycyjny.

Patch Bluetooth i jego autorstwo są opisane w osobnym projekcie:
<https://github.com/tysszek/convers-plus-bt-audio-v5-2>.

## Użycie na własnym VBF

Wymagany jest własny, zweryfikowany plik `CS7T-14C026-CD.vbf` z modem
M0RTAR/Motral. Uruchom:

```bash
python tools/patch_vbf_menu_pl.py \
  CS7T-14C026-CD.vbf \
  CS7T-14C026-CD_MENU_PL.vbf
```

W razie potrzeby można wymusić kontrolę dwóch znanych sum:

```bash
python tools/patch_vbf_menu_pl.py \
  CS7T-14C026-CD.vbf \
  CS7T-14C026-CD_MENU_PL.vbf \
  --strict-hash
```

Skrypt utworzy nowy plik wyjściowy i odmówi działania, jeżeli nie rozpozna
bezpiecznej struktury menu lub VBF. Jeżeli wejściowy VBF ma wyłącznie nieaktualny
`file_checksum` w nagłówku, narzędzie przeliczy go w pliku wyjściowym; błędny
payload, CRC16 albo struktura nadal powodują odmowę. Do flashowania używa się
wyłącznie pliku wyjściowego po pozytywnej walidacji.

## Bezpieczeństwo

Przed jakąkolwiek operacją wykonaj i sprawdź kopię własnego firmware oraz
EEPROM. Nie publikuj VBF, zrzutów pamięci ani danych auta — mogą zawierać VIN.
Nie flashuj obrazu, którego narzędzie nie zaakceptowało. Reflash licznika może
go unieruchomić i wymagać sprzętowego recovery.

## Testy

Testy struktury patcha uruchomisz bez firmware:

```bash
python -m unittest discover -s tests -v
```

Projekt nie zawiera żadnego firmware. Licencje i autorstwo opisano w
`CREDITS.md`, `NOTICE.md` oraz `LICENSE_UPSTREAM_MIT`.
