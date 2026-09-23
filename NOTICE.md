# Notice

To jest nieoficjalna modyfikacja firmware Ford Convers+. Nie jest związana z
Ford Motor Company.

Patch jest przeznaczony dla rozpoznanej struktury menu M0RTAR/Motral w payloadzie
programu:

- partycja: `CS7T-14C026-CD`,
- adres: `0x5000`,
- długość: `0xFB000`,
- znany wariant M0RTAR 1412-FL, 4 pozycje, SHA-256:
  `9c4b3b051a9dd1705d2acd27658d25fb71a52f5c2a20f5595f4885016a3661a1`,
- znany wariant M0RTAR + Gauge Sweep, 5 pozycji, SHA-256:
  `0c91f7e940b4e48c729a5f8b0a788c2296fb51c645c1a18db60e76c3497dd034`.

Narzędzie domyślnie rozpoznaje strukturę, a nie tylko sumę pliku. Dzięki temu
może obsłużyć zgodny wariant z dodatkowym patchem Bluetooth lub nową pozycją
menu. Nieznane etykiety pozostawia bez zmian i zgłasza w raporcie. Opcja
`--strict-hash` ogranicza pracę do dwóch powyższych wariantów referencyjnych.
Bluetooth nie jest osobną pozycją menu i nie wymaga dodatkowej gałęzi
tłumaczenia.
