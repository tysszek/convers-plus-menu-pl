# Pełna procedura zmian menu Convers+ — V5.2 → V5.3.4

Ten dokument opisuje dokładnie nasz pełny wariant zmian widocznych na liczniku. Bazą jest działający CD V5.2 z wcześniejszym modem Bluetooth Audio. Dokument rozdziela ten wariant od osobnego patcha dodatkowego menu Advanced dla M0RTAR/Motral.

## Dwie różne ścieżki w tym repozytorium

| Ścieżka | Do czego służy | Główny skrypt |
|---|---|---|
| Pełny patch V5.2 → V5.3.4 | Napisy widocznych menu konfiguracji, motywów oraz komunikat telefonu | `build_menu_labels_v531_physical_fix.py`, `apply_theme_labels_v533.py`, `apply_theme_labels_v534.py`, `apply_ed_phone_fix_v53.py` |
| M0RTAR/Motral Advanced | Dodatkowe, relokowane menu Advanced i jego wewnętrzne pozycje | `patch_vbf_menu_pl.py` / `localize_advanced_pl.py` |

Nie należy mieszać tych dwóch procedur na podstawie samej nazwy pliku. Mają inne struktury menu i inne kontrolowane bazy wejściowe. Tytuł README pozostaje historyczny, ale pełny zakres naszego softu opisuje właśnie niniejszy dokument.

## Co zostało zmienione

### Menu główne — zmiana polski → polski

| Było | Jest |
|---|---|
| `Zmieniacz płyt CD` | `Płyta CD` |
| `wejście Auxiliary` | `Multimedia USB/BT` |

Te dwie nazwy są już częścią wejściowej bazy CD V5.2 użytej w dalszym łańcuchu. Nie wykonuje się ich ponownie skryptem V5.3.

### Menu konfiguracji — angielski → polski

| Było | Jest |
|---|---|
| `Forward Alert` | `Ostrz. kolizji` |
| `Driver Alert` | `Czujność` |
| `Colour themes` | `Kolory` |
| `Advanced` | `Zaawansowane` |
| `Cruise Control` | `Tempomat` |

Skrypt zmienia także bezpośrednie wskaźniki nagłówków używane przy wejściu do poszczególnych podmenu. Dlatego sama zmiana wpisu w tabeli językowej nie wystarczała — etap V5.3.2 poprawia również nagłówki widoczne po wejściu do menu.

`Forward Alert` jest nazwą funkcji ostrzegania przed kolizją/ruchem. W analizowanej gałęzi nie ma osobnego aktywnego napisu `Traffic`, który należałoby dodatkowo tłumaczyć.

### Menu motywów „Kolory” — angielski → polski

| Było | Jest |
|---|---|
| `Dark` | `Ciemny` |
| `Blue` | `Niebieski` |
| `Grey` | `Szary` |
| `Red` | `Czerwony` |
| `Green` | `Zielony` |
| `Lunar Sky` | `Nocne niebo` |

`Green` i `Lunar Sky` są aktywnymi pozycjami widocznymi na fizycznym liczniku. Nie zostały pominięte jako „nieużywane”; etap V5.3.4 tłumaczy je w istniejących rekordach, zachowując wskaźniki i flagi motywów.

### Komunikat telefonu — polski → polski

| Było | Jest |
|---|---|
| `Dokladnie` | `przychodzi` |

W zasobie ED `przychodzi` zajmuje o jeden bajt więcej niż `Dokladnie`. Aby nie przesuwać kolejnych rekordów, w tym samym pakiecie skrócono technicznie sąsiedni przycisk `Akcept.` → `Akcept`. To nie jest osobna zmiana funkcjonalna ani zmiana działania przycisku — jest to zachowanie stałego rozmiaru zasobu.

### Dodatkowe menu Advanced M0RTAR/Motral

To osobny wariant, ale jego widoczne wewnętrzne pozycje są opisane w tym samym repozytorium:

| Było | Jest |
|---|---|
| `Advanced` | `Zaawansowane` |
| `Digital speed` | `Predkosc cyfrowa` |
| `Gauge sweep` | `Test wskazowek` |
| `Engine temp & Voltage` | `Temp. silnika i napiecie` |
| `on main` | `Na ekranie glownym` |
| `in standby` | `W trybie czuwania` |

Ten patch działa na rozpoznanej strukturze M0RTAR, obsługuje wariant cztero- i pięciopozycyjny, tłumaczy tylko rozpoznane aktywne etykiety i raportuje nieznane wpisy jako `UNTRANSLATED`. Nie dodaje funkcji ani pozycji menu.

## Który skrypt robi którą zmianę

### 1. CD V5.2 → V5.3.2

`build_menu_labels_v531_physical_fix.py` uruchamia wewnętrznie bazowy etap `apply_menu_labels_v53.py`, który:

- kieruje polskie wpisy `Forward Alert`, `Driver Alert`, `Colour themes` i `Advanced` do nowych polskich napisów;
- zmienia cztery pola `Cruise Control` na `Tempomat`;
- poprawia wskaźniki bezpośrednich nagłówków, dzięki czemu napisy są polskie także po wejściu do podmenu;
- nie zmienia kopii innych języków ani ukrytych wpisów tabel systemowych;
- przelicza CRC16 payloadu i `file_checksum` VBF.

Nie uruchamiaj `apply_menu_labels_v53.py` drugi raz na tej samej bazie — etap jest już zawarty w skrypcie budującym V5.3.2.

### 2. CD V5.3.2 → V5.3.3

`apply_theme_labels_v533.py` dodaje do aktywnego menu „Kolory” pierwsze cztery nazwy: `Ciemny`, `Niebieski`, `Szary` i `Czerwony`. Zmienia także wspólny nagłówek motywów na `Kolory` tam, gdzie wymaga tego deskryptor.

### 3. CD V5.3.3 → V5.3.4

`apply_theme_labels_v534.py` zmienia aktywne rekordy `Green` i `Lunar Sky` na `Zielony` i `Nocne niebo` w miejscu. Skrypt sprawdza typ rekordu, wskaźnik tekstu i flagę motywu przed zapisem oraz po zapisie.

### 4. ED — komunikat telefonu

`apply_ed_phone_fix_v53.py` zmienia `Dokladnie` na `przychodzi`, skracając sąsiednie `Akcept.` do `Akcept`, aby zachować dokładny rozmiar bloku ED i wszystkie dalsze offsety.

AA pozostaje niezmieniony.

## Odtworzenie pełnego patcha

Pracuj w katalogu głównym repozytorium i używaj własnych, zachowanych plików wejściowych. Nazwy poniżej są przykładowe — ważne jest, aby zawartość odpowiadała właściwym bazom.

### CD — trzy kolejne etapy

~~~bash
python tools/build_menu_labels_v531_physical_fix.py CS7T-14C026-CD_V5_2.vbf CS7T-14C026-CD_V5_3_2.vbf
python tools/apply_theme_labels_v533.py CS7T-14C026-CD_V5_3_2.vbf CS7T-14C026-CD_V5_3_3.vbf
python tools/apply_theme_labels_v534.py CS7T-14C026-CD_V5_3_3.vbf CS7T-14C026-CD_V5_3_4.vbf
~~~

### ED — jeden etap

~~~bash
python tools/apply_ed_phone_fix_v53.py CS7T-14C026-ED_BAZA.vbf CS7T-14C026-ED_V5_3.vbf
~~~

Nie trzeba uruchamiać żadnego skryptu dla AA.

## Kontrola baz i wyników

Skrypty celowo odmawiają pracy, jeśli SHA-256, adres lub rozmiar bloku nie pasują do analizowanej wersji. Najważniejsze oczekiwane wyniki tej ścieżki są następujące:

| Etap | Plik wynikowy | SHA-256 | CRC16 | `file_checksum` |
|---|---|---|---:|---:|
| V5.3.2 | CD | `687a85f70138d247db171b01c0262a4cb3a544313d77680e51dbab4bdd20e45a` | `13C3` | `1430D9EE` |
| V5.3.3 | CD | `212ef4f577a5acdce4ab276b9daff3f057647dc7b5317f437d09586ef4584756` | `DA3C` | `449BB259` |
| V5.3.4 | CD | `dde96153e4ad9948596fb0f4d93e723949bd351625bd99f599d0ce0ab12d8f03` | `13CC` | `37D37491` |
| ED V5.3 | ED | `c283d7ae243bbbaba4f27ed163c70b8bd9e29888f878507dadebddf1336f2568` | `9A13` | `980FC989` |

Bazowy CD V5.2 ma SHA-256 `21058ce5f64949e7926e2225eda00c06b43e5308ecd77a651f5ca0f96a631d49`. Bazowy ED dla poprawki telefonu ma SHA-256 `6b8a0a3d72338014570e4493ffb4749299c0f18dcc40a6754f229ec92c7ccab2`.

Po każdym etapie można wykonać walidację:

~~~bash
python tools/vbf_tool.py verify CS7T-14C026-CD_V5_3_4.vbf
python tools/vbf_tool.py verify CS7T-14C026-ED_V5_3.vbf
python -m unittest discover -s tests -v
~~~

Do flashowania używa się wyłącznie wyników po pozytywnej walidacji. Repozytorium nie zawiera binarnego firmware Forda.

## Ważne rozgraniczenie zakresu

Ta ścieżka zmienia teksty i wskaźniki istniejących elementów. Nie dodaje komunikatu `Niski poziom płynu chłodniczego`, nie dodaje obsługi zdarzenia CAN/PCM i nie dodaje `Ostrzeżenie DPF`. Są to osobne zmiany funkcjonalne wymagające analizy i obsługi sygnałów, a nie samego tłumaczenia.

Przed flashowaniem zachowaj oryginalne CD, ED, AA/SBL i EEPROM, sprawdź sumy oraz zapewnij stabilne zasilanie. Nie obchodź odmowy skryptu dla nieznanej wersji.