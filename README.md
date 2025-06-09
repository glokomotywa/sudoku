### Jakub Woś 288581 Informatyka Ogólnoakademicka
# Dokumentacja: Gra Sudoku
## Opis ogólny

Gra Sudoku to implementacja popularnej łamigłówki liczbowej napisana w Pythonie z wykorzystaniem biblioteki Pygame. Program oferuje pełną funkcjonalność gry, w tym generowanie plansz o różnych poziomach trudności, zapisywanie i wczytywanie postępu, system wskazówek oraz mechanizm śledzenia czasu gry.
### Funkcjonalności

- Generowanie plansz Sudoku o dwóch poziomach trudności: łatwym i trudnym

-  Interfejs graficzny z możliwością wpisywania liczb

-   System zapisywania i wczytywania stanu gry

-   Mechanizm wskazówek (3 dostępne na grę)

-   Śledzenie czasu gry z uwzględnieniem pauz

-   Sprawdzanie konfliktów w czasie rzeczywistym

-   System pauzowania gry

-   Ekran końcowy z podsumowaniem wyniku

### Struktura kodu
#### Klasy główne
##### SudokuGenerator

Generuje planszę Sudoku i jej rozwiązanie.

Metody:

-  generate_complete_board(): Tworzy pełną planszę Sudoku

- fill_diagonal(): Wypełnia przekątne kwadraty 3x3

- is_valid(row, col, num): Sprawdza poprawność liczby w komórce

- solve_sudoku(): Rozwiązuje planszę metodą backtrackingu

- remove_numbers(): Usuwa liczby zgodnie z poziomem trudności

##### Button

Reprezentuje interaktywny przycisk w interfejsie.

Metody:

- draw(screen): Rysuje przycisk na ekranie

-   check_hover(pos): Obsługuje efekt najechania myszą

-  is_clicked(pos, event): Sprawdza kliknięcie

##### Game

Główna klasa zarządzająca logiką gry.

Metody:

-    new_game(): Inicjalizuje nową grę

 -   draw_grid(): Rysuje planszę Sudoku

  -  draw_start_screen(): Rysuje ekran startowy

   - draw_game_screen(): Rysuje główny ekran gry

-    draw_pause_menu(): Rysuje menu pauzy

 -   draw_end_screen(): Rysuje ekran końcowy

  -  save_game(): Zapisuje stan gry do pliku

   - load_game(): Wczytuje zapisany stan gry

   - check_win(): Sprawdza, czy gracz wygrał

-    use_hint(): Używa wskazówki

 -   run(): Główna pętla gry

### Mechanizmy gry
#### Generowanie planszy

Plansza jest generowana w trzech krokach:

1. Wypełnienie przekątnych kwadratów 3x3

2. Rozwiązanie całej planszy metodą backtrackingu

3. Usunięcie liczb w zależności od poziomu trudności:

        Łatwy: 30 pustych komórek

        Trudny: 50 pustych komórek

#### System wskazówek

Gracz ma do dyspozycji 3 wskazówki na grę. Każda wskazówka:

1. Wybiera komórkę z największą liczbą pustych sąsiadów

2. Wypełnia ją poprawną liczbą

3. Zmniejsza licznik dostępnych wskazówek

#### Zarządzanie czasem

Czas gry jest mierzony z uwzględnieniem pauz:

- Czas pauzy jest odejmowany od całkowitego czasu gry

- Czas jest wyświetlany w formacie MM:SS

#### Zapisywanie gry

Stan gry jest zapisywany w formacie JSON z następującymi danymi:

- Aktualna plansza

 -  Rozwiązanie

   - Poziom trudności

-    Nazwa gracza

 -   Upłynięty czas

  -  Liczba pozostałych wskazówek

### Uruchomienie gry

Zainstaluj wymagane zależności:
```bash
pip install pygame
```
Uruchom plik główny:
```bash
python sudoku.py
```
### Sterowanie

- Mysz: Wybór komórek i przycisków

- Klawiatura (cyfry 1-9): Wpisywanie liczb

- Backspace/Delete: Usuwanie liczby z komórki

### Struktura plików

- sudoku_saves.json: Plik z zapisanymi stanami gier

- Plik główny: sudoku.py
