# Polskie menu Advanced dla moda M0RTAR/Motral

To repozytorium opisuje dwa odrębne warianty zmian napisów w Ford Convers+ 1412-FL.
Nie należy ich łączyć na podstawie samej nazwy pliku — każdy wariant ma własną
strukturę wejściową i własny, kontrolowany zestaw skryptów.

## Wariant 1 — pełny patch V5.2 → V5.3.4

To jest pełny łańcuch naszego softu: `Płyta CD`, `Multimedia USB/BT`, nagłówki
konfiguracji, `Tempomat`, wszystkie aktywne motywy oraz poprawka komunikatu
telefonu `Dokladnie` → `przychodzi`. Kompletna procedura odtworzenia znajduje
się w [pełnej instrukcji V5.2–V5.3.4](docs/odtworzenie-pelnego-patcha-v5-3-4.md).

## Wariant 2 — M0RTAR/Motral, dodatkowe menu Advanced

Mały, bezpieczny patch językowy dla dodatkowego menu Advanced. Nie dodaje nowej
funkcji i nie zmienia sposobu obliczania ani wyświetlania wartości.

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
## Pełny wykaz widocznych zmian menu — V5.3.4

To repozytorium zawiera kompletny opis zmian napisów, które zostały wykonane w widocznych menu i komunikatach naszego Convers+ 1412-FL. Poniższa lista obejmuje cały łańcuch zmian V5.2 → V5.3.4, a nie tylko dwa ostatnie napisy motywów. Procedura technicznego odtworzenia jest opisana w [pełnej instrukcji V5.2–V5.3.4](docs/odtworzenie-pelnego-patcha-v5-3-4.md).

### Menu główne

| Oryginał | Nazwa po polsku |
|---|---|
| `Zmieniacz płyt CD` | `Płyta CD` |
| `wejście Auxiliary` | `Multimedia USB/BT` |

### Menu konfiguracji

| Oryginał | Nazwa po polsku |
|---|---|
| `Forward Alert` | `Ostrz. kolizji` |
| `Driver Alert` | `Czujność` |
| `Colour themes` | `Kolory` |
| `Advanced` | `Zaawansowane` |
| `Cruise Control` | `Tempomat` |

`Forward Alert` to pozycja związana z ostrzeganiem przed kolizją/ruchem. W tej gałęzi firmware nie ma osobnego, niezależnego napisu `Traffic` — został on rozpoznany w rozmowie jako opis tej funkcji.

### Wewnętrzne menu „Advanced”

Wariant M0RTAR/Motral dodatkowego menu Advanced ma również poniższe widoczne pozycje. Odtwarza je osobny patcher `patch_vbf_menu_pl.py`; nie są one dodatkowym krokiem pełnego łańcucha V5.2 → V5.3.4 bez ponownej analizy zgodności:

| Oryginał | Nazwa po polsku |
|---|---|
| `Digital speed` | `Predkosc cyfrowa` |
| `Gauge sweep` | `Test wskazowek` |
| `Engine temp & Voltage` | `Temp. silnika i napiecie` |
| `on main` | `Na ekranie glownym` |
| `in standby` | `W trybie czuwania` |

W tych zasobach zachowano zapis bez polskich znaków tam, gdzie wymaga tego potwierdzona mapa glifów firmware.

### Menu motywów „Kolory”

| Oryginał | Nazwa po polsku |
|---|---|
| `Dark` | `Ciemny` |
| `Blue` | `Niebieski` |
| `Grey` | `Szary` |
| `Red` | `Czerwony` |
| `Green` | `Zielony` |
| `Lunar Sky` | `Nocne niebo` |

`Green` i `Lunar Sky` są aktywnymi pozycjami widocznymi na fizycznym liczniku i zostały dodane do finalnego zakresu V5.3.4.

### Komunikat telefonu

| Oryginał | Nazwa po polsku |
|---|---|
| `Dokladnie` | `przychodzi` |

Aby zachować rozmiar zasobu ED, sąsiedni przycisk został technicznie skrócony z `Akcept.` do `Akcept`. Nie zmienia to jego funkcji.

### Zakres techniczny

Zmiany dotyczą wyłącznie tekstów używanych przez widoczne menu i komunikaty. Nie tłumaczyliśmy ukrytych kopii innych języków ani nieużywanych wpisów tabel systemowych. Nie dodano w tej wersji komunikatu o niskim poziomie płynu chłodniczego ani funkcji `Ostrzeżenie DPF` — są to osobne prace funkcjonalne V9.

Dokumentacja wersji i skrypty odtworzeniowe znajdują się w:

- [V5.3.4 — aktualny stan](docs/menu-label-patch-v5-3-4.md)
- [V5.3.3 — wcześniejszy audyt](docs/menu-label-patch-v5-3-3.md)
- [V5.3 — pierwsza pełna gałąź napisów](docs/menu-label-patch-v5-3-v1.md)
- [V5.2 — menu główne](docs/menu-label-patch-v5-2-v1.md)
