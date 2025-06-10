import pygame
import sys
import json
import random
from datetime import datetime, timedelta

# Inicjalizacja Pygame
pygame.init()
pygame.font.init()

# Stałe
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
GRID_SIZE = 9
CELL_SIZE = 50
GRID_PADDING = 50
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50
FONT_SIZE = 36
SMALL_FONT_SIZE = 24

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (70, 130, 180)
RED = (255, 99, 71)
GREEN = (60, 179, 113)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)
CONFLICT_COLOR = (255, 100, 100)
PAUSE_OVERLAY = (0, 0, 0, 150)


class SudokuGenerator:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.solution = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.generate_complete_board()
        self.remove_numbers()

    def generate_complete_board(self):
        # Wypełnij przekątną 3x3
        self.fill_diagonal()

        # Rozwiąż resztę planszy
        self.solve_sudoku()
        self.solution = [row[:] for row in self.board]

    def fill_diagonal(self):
        for i in range(0, GRID_SIZE, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for r in range(3):
                for c in range(3):
                    self.board[i + r][i + c] = nums.pop()

    def is_valid(self, row, col, num):
        # Sprawdź wiersz
        if num in self.board[row]:
            return False

        # Sprawdź kolumnę
        for r in range(GRID_SIZE):
            if self.board[r][col] == num:
                return False

        # Sprawdź kwadrat 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(3):
            for c in range(3):
                if self.board[start_row + r][start_col + c] == num:
                    return False

        return True

    def solve_sudoku(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(row, col, num):
                            self.board[row][col] = num
                            if self.solve_sudoku():
                                return True
                            self.board[row][col] = 0
                    return False
        return True

    def remove_numbers(self):
        if self.difficulty == "łatwy":
            to_remove = 30
        else:  # trudny
            to_remove = 50

        cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        random.shuffle(cells)

        for i in range(to_remove):
            row, col = cells[i]
            self.board[row][col] = 0


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont(None, SMALL_FONT_SIZE)

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Sudoku")
        self.clock = pygame.time.Clock()
        self.state = "start"
        self.player_name = ""
        self.difficulty = "łatwy"
        self.selected_cell = None
        self.start_time = None
        self.elapsed_time = 0
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.small_font = pygame.font.SysFont(None, SMALL_FONT_SIZE)
        self.hint_count = 3  # Liczba dostępnych wskazówek

        # Pause tracking
        self.is_paused = False
        self.pause_start_time = None
        self.pause_duration = 0

        # Przyciski
        button_y = SCREEN_HEIGHT // 2
        self.start_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT,
                                   "Nowa Gra", GREEN, (144, 238, 144))
        self.easy_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH - 10, button_y + 70, BUTTON_WIDTH, BUTTON_HEIGHT,
                                  "Łatwy", LIGHT_BLUE, (135, 206, 250))
        self.hard_button = Button(SCREEN_WIDTH // 2 + 10, button_y + 70, BUTTON_WIDTH, BUTTON_HEIGHT,
                                  "Trudny", RED, (255, 160, 122))
        self.back_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH - 10, SCREEN_HEIGHT - 70, BUTTON_WIDTH,
                                  BUTTON_HEIGHT,
                                  "Powrót", GRAY, (220, 220, 220))
        self.save_button = Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT,
                                  "Zapisz", YELLOW, (255, 255, 153))
        self.load_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, BUTTON_WIDTH,
                                  BUTTON_HEIGHT,
                                  "Kontynuuj", PURPLE, (216, 191, 216))
        self.pause_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH - 10, SCREEN_HEIGHT - 70, BUTTON_WIDTH,
                                   BUTTON_HEIGHT,
                                   "Pauza", GRAY, (220, 220, 220))
        self.hint_button = Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT,
                                  f"Wskazówka ({self.hint_count})", YELLOW, (255, 255, 153))
        self.return_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, BUTTON_WIDTH,
                                    BUTTON_HEIGHT,
                                    "Powrót", GREEN, (144, 238, 144))
        self.save_pause_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, BUTTON_WIDTH,
                                        BUTTON_HEIGHT,
                                        "Zapisz", YELLOW, (255, 255, 153))
        self.menu_button = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2 + 90, BUTTON_WIDTH,
                                  BUTTON_HEIGHT,
                                  "Menu", RED, (255, 160, 122))

        # Generowanie planszy
        self.new_game()

    def new_game(self):
        self.generator = SudokuGenerator(self.difficulty)
        self.board = [row[:] for row in self.generator.board]
        self.solution = [row[:] for row in self.generator.solution]
        self.start_time = datetime.now()
        self.elapsed_time = 0
        self.selected_cell = None
        self.hint_count = 3
        self.hint_button.text = f"Wskazówka ({self.hint_count})"
        self.is_paused = False
        self.pause_duration = 0
        self.pause_start_time = None

    def has_conflict(self, row, col, num):
        # Check row
        for c in range(GRID_SIZE):
            if c != col and self.board[row][c] == num:
                return True

        # Check column
        for r in range(GRID_SIZE):
            if r != row and self.board[r][col] == num:
                return True

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(3):
            for c in range(3):
                box_row = start_row + r
                box_col = start_col + c
                if (box_row != row or box_col != col) and self.board[box_row][box_col] == num:
                    return True

        return False

    def draw_grid(self, start_x, start_y):
        grid_width = GRID_SIZE * CELL_SIZE
        start_x = (self.screen.get_width() - grid_width) // 2
        start_y = (self.screen.get_height() - grid_width) // 2 - 30

        # Rysowanie komórek
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell_rect = pygame.Rect(
                    start_x + col * CELL_SIZE,
                    start_y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                # Kolorowanie zaznaczonej komórki
                if self.selected_cell == (row, col):
                    pygame.draw.rect(self.screen, LIGHT_BLUE, cell_rect)
                elif (row // 3 + col // 3) % 2 == 0:
                    pygame.draw.rect(self.screen, (240, 240, 240), cell_rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, cell_rect)

                pygame.draw.rect(self.screen, GRAY, cell_rect, 1)

                # Rysowanie liczb
                if self.board[row][col] != 0:
                    # Original numbers are black
                    if self.generator.board[row][col] != 0:
                        text_color = BLACK
                    else:
                        if self.has_conflict(row, col, self.board[row][col]):
                            text_color = CONFLICT_COLOR
                        else:
                            text_color = DARK_BLUE

                    num = self.board[row][col]
                    text_surf = self.font.render(str(num), True, text_color)
                    text_rect = text_surf.get_rect(center=cell_rect.center)
                    self.screen.blit(text_surf, text_rect)

        for i in range(0, GRID_SIZE + 1):
            if i % 3 == 0:
                pygame.draw.line(
                    self.screen,
                    BLACK,
                    (start_x, start_y + i * CELL_SIZE),
                    (start_x + grid_width, start_y + i * CELL_SIZE),
                    3
                )
                pygame.draw.line(
                    self.screen,
                    BLACK,
                    (start_x + i * CELL_SIZE, start_y),
                    (start_x + i * CELL_SIZE, start_y + grid_width),
                    3
                )

    def draw_start_screen(self):
        self.screen.fill(LIGHT_BLUE)
        center_x = self.screen.get_width() // 2
        vertical_spacing = 60  # Space between elements

        # Title
        title_font = pygame.font.SysFont(None, FONT_SIZE + 20)
        title = title_font.render("SUDOKU", True, DARK_BLUE)
        title_rect = title.get_rect(center=(center_x, self.screen.get_height() // 4))
        self.screen.blit(title, title_rect)

        # Starting Y position for buttons
        current_y = self.screen.get_height() // 2 - 80

        # Player name field
        name_text = self.small_font.render("Nazwa gracza:", True, BLACK)
        name_rect = name_text.get_rect(center=(center_x, current_y))
        self.screen.blit(name_text, name_rect)
        current_y += vertical_spacing

        # Player name input box
        pygame.draw.rect(self.screen, WHITE, (center_x - 150, current_y - 20, 300, 40))
        pygame.draw.rect(self.screen, BLACK, (center_x - 150, current_y - 20, 300, 40), 2)
        player_surf = self.font.render(self.player_name, True, BLACK)
        self.screen.blit(player_surf, (center_x - 140, current_y - 15))
        current_y += vertical_spacing

        # Start and Load buttons (stacked vertically)
        self.start_button.rect.center = (center_x, current_y)
        self.start_button.draw(self.screen)
        current_y += vertical_spacing

        self.load_button.rect.center = (center_x, current_y)
        self.load_button.draw(self.screen)
        current_y += vertical_spacing

        # Difficulty selection
        level_text = self.small_font.render("Wybierz poziom trudności:", True, BLACK)
        level_rect = level_text.get_rect(center=(center_x, current_y))
        self.screen.blit(level_text, level_rect)
        current_y += vertical_spacing

        # Difficulty buttons (stacked vertically)
        self.easy_button.rect.center = (center_x, current_y)
        self.easy_button.draw(self.screen)
        current_y += vertical_spacing

        self.hard_button.rect.center = (center_x, current_y)
        self.hard_button.draw(self.screen)
        current_y += vertical_spacing

        # Current difficulty display
        diff_text = self.small_font.render(f"Aktualny: {self.difficulty.capitalize()}", True, BLACK)
        diff_rect = diff_text.get_rect(center=(center_x, current_y))
        self.screen.blit(diff_text, diff_rect)

    def draw_game_screen(self):
        self.screen.fill(WHITE)

        if self.start_time and not self.is_paused:
            base_time = datetime.now() - timedelta(seconds=self.pause_duration)
            self.elapsed_time = (base_time - self.start_time).seconds

        # Czas gry
        time_text = self.small_font.render(f"Czas: {self.elapsed_time // 60}:{self.elapsed_time % 60:02d}", True, BLACK)
        self.screen.blit(time_text, (20, 20))

        # Nazwa gracza i poziom
        info_text = self.small_font.render(f"Gracz: {self.player_name} | Poziom: {self.difficulty}", True, BLACK)
        self.screen.blit(info_text, (self.screen.get_width() - info_text.get_width() - 20, 20))

        grid_width = GRID_SIZE * CELL_SIZE
        grid_height = GRID_SIZE * CELL_SIZE
        start_x = (self.screen.get_width() - grid_width) // 2
        start_y = (self.screen.get_height() - grid_height - 100) // 2

        self.draw_grid(start_x, start_y)

        button_y = start_y + grid_height + 60
        center_x = self.screen.get_width() // 2

        self.pause_button.rect.center = (center_x - BUTTON_WIDTH // 2 - 10, button_y)
        self.hint_button.rect.center = (center_x + BUTTON_WIDTH // 2 + 10, button_y)

        self.pause_button.draw(self.screen)
        self.hint_button.draw(self.screen)

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Menu pauzy
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        # Tło menu
        menu_rect = pygame.Rect(center_x - 150, center_y - 150, 300, 300)
        pygame.draw.rect(self.screen, WHITE, menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 2, border_radius=15)

        # Tytuł
        title = self.font.render("PAUZA", True, DARK_BLUE)
        title_rect = title.get_rect(center=(center_x, center_y - 100))
        self.screen.blit(title, title_rect)

        # Przyciski
        self.return_button.rect.center = (center_x, center_y - 30)
        self.save_pause_button.rect.center = (center_x, center_y + 30)
        self.menu_button.rect.center = (center_x, center_y + 90)

        self.return_button.draw(self.screen)
        self.save_pause_button.draw(self.screen)
        self.menu_button.draw(self.screen)

    def draw_end_screen(self):
        self.screen.fill(GREEN)
        congrats = self.font.render("Gratulacje!", True, WHITE)
        congrats_rect = congrats.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3))
        self.screen.blit(congrats, congrats_rect)

        time_text = self.font.render(f"Czas: {self.elapsed_time // 60}:{self.elapsed_time % 60:02d}", True, WHITE)
        time_rect = time_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(time_text, time_rect)

        self.back_button.rect.center = (self.screen.get_width() // 2, self.screen.get_height() * 2 // 3)
        self.back_button.draw(self.screen)

    def save_game(self):
        if not self.player_name:
            return

        try:
            with open("sudoku_saves.json", "r") as f:
                saves = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            saves = {}

        save_data = {
            "board": self.board,
            "solution": self.solution,
            "difficulty": self.difficulty,
            "player": self.player_name,
            "elapsed_time": self.elapsed_time,
            "timestamp": datetime.now().isoformat(),
            "hint_count": self.hint_count
        }

        if self.player_name not in saves:
            saves[self.player_name] = []

        saves[self.player_name].append(save_data)

        with open("sudoku_saves.json", "w") as f:
            json.dump(saves, f, indent=2)

    def load_game(self):
        if not self.player_name:
            return False

        try:
            with open("sudoku_saves.json", "r") as f:
                saves = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        if self.player_name in saves and saves[self.player_name]:
            # Wybierz najnowszy zapis
            save_data = saves[self.player_name][-1]
            self.board = save_data["board"]
            self.solution = save_data["solution"]
            self.difficulty = save_data["difficulty"]
            self.elapsed_time = save_data["elapsed_time"]
            self.hint_count = save_data.get("hint_count", 3)  # Domyślnie 3 jeśli brak
            self.start_time = datetime.now() - timedelta(seconds=self.elapsed_time)
            self.hint_button.text = f"Wskazówka ({self.hint_count})"  # Aktualizacja tekstu przycisku
            self.is_paused = False
            self.pause_duration = 0
            return True

        return False

    def check_win(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] != self.solution[row][col]:
                    return False
        return True

    def use_hint(self):
        if self.hint_count <= 0:
            return

        # Znajdź wszystkie puste komórki
        empty_cells = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    empty_cells.append((row, col))

        # Jeśli nie ma pustych komórek, zakończ
        if not empty_cells:
            return

        # Przygotuj struktury do zliczania pustych komórek
        row_empty = [0] * GRID_SIZE  # Liczba pustych w każdym wierszu
        col_empty = [0] * GRID_SIZE  # Liczba pustych w każdej kolumnie
        box_empty = [[0] * 3 for _ in range(3)]  # Liczba pustych w każdym kwadracie 3x3

        # Wypełnij struktury danymi
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    row_empty[row] += 1
                    col_empty[col] += 1
                    box_empty[row // 3][col // 3] += 1

        # Znajdź komórkę z największą liczbą pustych sąsiadów
        best_cell = None
        max_empty = -1

        for (row, col) in empty_cells:
            # Suma pustych komórek w wierszu, kolumnie i kwadracie komórki
            total_empty = row_empty[row] + col_empty[col] + box_empty[row // 3][col // 3]

            if total_empty > max_empty:
                max_empty = total_empty
                best_cell = (row, col)

        # Jeśli znaleziono komórkę, wypełnij ją poprawną wartością
        if best_cell:
            row, col = best_cell
            self.board[row][col] = self.solution[row][col]
            self.hint_count -= 1
            self.hint_button.text = f"Wskazówka ({self.hint_count})"  # Aktualizacja tekstu przycisku

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Zmiana rozmiaru okna
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Obsługa klawiatury
            if event.type == pygame.KEYDOWN:
                if self.state == "start":
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.unicode.isalnum() and len(self.player_name) < 15:
                        self.player_name += event.unicode

                elif self.state == "game" and self.selected_cell:
                    row, col = self.selected_cell
                    if event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
                        self.board[row][col] = int(event.unicode)
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        self.board[row][col] = 0

            # Obsługa myszy
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "start":
                    if self.start_button.is_clicked(mouse_pos, event):
                        if self.player_name:
                            self.new_game()
                            self.state = "game"
                            self.start_time = datetime.now()

                    elif self.easy_button.is_clicked(mouse_pos, event):
                        self.difficulty = "łatwy"

                    elif self.hard_button.is_clicked(mouse_pos, event):
                        self.difficulty = "trudny"

                    elif self.load_button.is_clicked(mouse_pos, event):
                        if self.load_game():
                            self.state = "game"

                elif self.state == "game":
                    if self.pause_button.is_clicked(mouse_pos, event):
                        if not self.is_paused:  # Pausing the game
                            self.is_paused = True
                            self.pause_start_time = datetime.now()
                            self.state = "pause"
                        else:
                            self.is_paused = False
                            self.pause_duration += (datetime.now() - self.pause_start_time).seconds
                            self.state = "game"

                    elif self.hint_button.is_clicked(mouse_pos, event):
                        self.use_hint()

                    else:
                        # Wybór komórki
                        grid_width = GRID_SIZE * CELL_SIZE
                        start_x = (self.screen.get_width() - grid_width) // 2
                        start_y = (self.screen.get_height() - grid_width) // 2 - 30

                        if (start_x <= mouse_pos[0] <= start_x + grid_width and
                                start_y <= mouse_pos[1] <= start_y + grid_width):

                            col = (mouse_pos[0] - start_x) // CELL_SIZE
                            row = (mouse_pos[1] - start_y) // CELL_SIZE

                            # Sprawdź czy komórka nie jest stała
                            if self.generator.board[row][col] == 0:
                                self.selected_cell = (row, col)

                elif self.state == "pause":
                    if self.return_button.is_clicked(mouse_pos, event):
                        self.is_paused = False
                        self.pause_duration += (datetime.now() - self.pause_start_time).seconds
                        self.state = "game"
                    elif self.save_pause_button.is_clicked(mouse_pos, event):
                        self.save_game()
                    elif self.menu_button.is_clicked(mouse_pos, event):
                        self.state = "start"

                elif self.state == "end":
                    if self.back_button.is_clicked(mouse_pos, event):
                        self.state = "start"

        # Aktualizacja przycisków (hover)
        if self.state == "start":
            self.start_button.check_hover(mouse_pos)
            self.easy_button.check_hover(mouse_pos)
            self.hard_button.check_hover(mouse_pos)
            self.load_button.check_hover(mouse_pos)
        elif self.state == "game":
            self.pause_button.check_hover(mouse_pos)
            self.hint_button.check_hover(mouse_pos)
        elif self.state == "pause":
            self.return_button.check_hover(mouse_pos)
            self.save_pause_button.check_hover(mouse_pos)
            self.menu_button.check_hover(mouse_pos)
        elif self.state == "end":
            self.back_button.check_hover(mouse_pos)

    def run(self):
        while True:
            self.handle_events()

            # Rysowanie odpowiedniego ekranu
            if self.state == "start":
                self.draw_start_screen()
            elif self.state == "game":
                self.draw_game_screen()
                if self.check_win():
                    self.state = "end"
            elif self.state == "pause":
                self.draw_game_screen() 
                self.draw_pause_menu()
            elif self.state == "end":
                self.draw_end_screen()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()