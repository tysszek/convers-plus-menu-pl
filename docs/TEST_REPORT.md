# Raport testów wersji publicznej

Testy wykonano lokalnie na znanym payloadzie M0RTAR 1412-FL. Firmware nie jest
częścią repozytorium.

## Wyniki wariantu czteropozycyjnego

- testy jednostkowe patchera: `5 passed`,
- wejściowy payload: SHA-256
  `9c4b3b051a9dd1705d2acd27658d25fb71a52f5c2a20f5595f4885016a3661a1`,
- długość payloadu: `0xFB000`, adres bazowy: `0x5000`,
- rozpoznano nagłówek M0RTAR `0x006B0007`,
- zachowano liczbę pozycji `4/4`,
- oryginalny deskryptor przy `0xDD200` pozostał niezmieniony,
- zmieniono 646 bajtów: klon deskryptora, etykiety oraz dwa wskaźniki tabel,
- sprawdzono odczyt etykiet i raportowanie nieznanej dodatkowej pozycji,
- output VBF przeszedł kontrolę CRC16 i `file_checksum`,
- output payload po teście: SHA-256
  `33c8bac781f1f78556901a554e1cc76424e31585aebe963e85abc6474654f087`.

## Wyniki wariantu pięciopozycyjnego

- wejściowy payload: SHA-256
  `0c91f7e940b4e48c729a5f8b0a788c2296fb51c645c1a18db60e76c3497dd034`,
- rozpoznano istniejący klon menu `5/5` z pozycją `Gauge sweep`,
- pozycję przetłumaczono na `Test wskazowek`, bez dodawania nowego rekordu,
- output VBF przeszedł kontrolę CRC16 i `file_checksum`,
- output payload po teście: SHA-256
  `6b7a8f74b10d942325ab025262bff5b105fd6fa69a7cba26604d55579692e7de`.

Patch Bluetooth został przeanalizowany osobno. Nie dodaje wpisu do menu
Advanced; zatem lokalizacja menu ma tylko dwie gałęzie: 4 pozycje oraz 5
pozycji po użyciu patcha Gauge Sweep.

## Zakres wyniku

To jest walidacja statyczna i kontrola struktury VBF. Nie zastępuje testu na
każdym wariancie licznika ani prawdziwej procedury recovery. Do zgłoszeń nie
załączaj firmware, EEPROM-u ani zrzutów pamięci.
