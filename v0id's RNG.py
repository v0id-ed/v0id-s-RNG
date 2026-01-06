import pygame
import sys
import random
import time
import cv2
import numpy as np

# ---------------- INITIALIZE ----------------
pygame.init()

# ---------------- CONSTANTS ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
GREEN = (0, 150, 0)
YELLOW = (255, 251, 0)
RED = (200, 0, 0)
PURPLE = (237, 0, 255)
GOLD = (255, 215, 0)
DARK_PURPLE = (100, 0, 150)

# ---------------- SCREEN & FONTS ----------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("v0id's RNG")
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

# ---------------- VIDEO BACKGROUND ----------------
video_path = "v0id girl background animation.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video file.")
    pygame.quit()
    sys.exit()

# Video properties
vid_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
vid_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Scale factor to cover screen without stretching
scale_w = SCREEN_WIDTH / vid_width
scale_h = SCREEN_HEIGHT / vid_height
scale_factor = max(scale_w, scale_h)
new_width = int(vid_width * scale_factor)
new_height = int(vid_height * scale_factor)

def get_background_frame():
    """Return the next video frame as a Pygame surface, cropped to screen size."""
    global cap
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    # Convert BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Resize to cover screen
    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    # Crop center
    x_offset = (new_width - SCREEN_WIDTH) // 2
    y_offset = (new_height - SCREEN_HEIGHT) // 2
    frame = frame[y_offset:y_offset+SCREEN_HEIGHT, x_offset:x_offset+SCREEN_WIDTH]
    # Convert to Pygame surface
    return pygame.surfarray.make_surface(frame.swapaxes(0,1))

# ---------------- GAME STATE ----------------
class GameState:
    def __init__(self):
        self.numbers = [1, 2, 3, 4, 5]
        self.player1_score = 3
        self.player2_score = 3
        self.current_player = 1
        self.player1_guess = None
        self.player2_guess = None
        self.game_message = "Player 1: Choose your number (1-5)"
        self.round_complete = False
        self.random_number = None

        # Username system
        self.game_phase = "username_entry"
        self.username_phase = 1
        self.player1_name = ""
        self.player2_name = ""
        self.current_input = ""
        self.input_active = True

        # Flash timers
        self.flash_start = None
        self.flash_duration = 0.2
        self.win_flash_start = None
        self.win_flash_duration = 0.5
        self.correct_guess_player = None

    def handle_username_input(self, text):
        if text == "ENTER":
            if len(self.current_input.strip()) > 0:
                if self.username_phase == 1:
                    self.player1_name = self.current_input.strip()
                    self.username_phase = 2
                    self.current_input = ""
                else:
                    self.player2_name = self.current_input.strip()
                    self.game_phase = "playing"
                    self.game_message = f"{self.player1_name}: Choose your number (1-5)"
        elif text == "BACKSPACE":
            self.current_input = self.current_input[:-1]
        else:
            if len(self.current_input) < 15:
                self.current_input += text

    def make_guess(self, number):
        if self.current_player == 1:
            self.player1_guess = number
            self.current_player = 2
            self.game_message = f"{self.player2_name}: Choose your number (1-5)"
        else:
            self.player2_guess = number
            self.evaluate_round()

    def evaluate_round(self):
        self.random_number = random.choice(self.numbers)
        self.correct_guess_player = None

        if self.player1_guess == self.random_number and self.player2_guess == self.random_number:
            winner = "Both guessed right!"
            self.correct_guess_player = "both"
        elif self.player1_guess == self.random_number:
            self.player1_score += 1
            self.player2_score -= 1
            winner = self.player1_name
            self.correct_guess_player = 1
        elif self.player2_guess == self.random_number:
            self.player2_score += 1
            self.player1_score -= 1
            winner = self.player2_name
            self.correct_guess_player = 2
        else:
            winner = "Nobody"

        self.game_message = f"Random number: {self.random_number} | Winner: {winner}"
        self.round_complete = True
        if self.correct_guess_player:
            self.win_flash_start = time.time()

    def new_round(self):
        self.current_player = 1
        self.player1_guess = None
        self.player2_guess = None
        self.round_complete = False
        self.random_number = None
        self.game_message = f"{self.player1_name}: Choose your number (1-5)"
        self.correct_guess_player = None

    def new_game(self):
        self.player1_score = 3
        self.player2_score = 3
        self.new_round()
        self.correct_guess_player = None
        self.win_flash_start = None

# ---------------- UI HELPERS ----------------
def draw_text_with_outline(screen, text, font, color, center_x, y, outline_color=DARK_PURPLE, outline_width=2):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(center_x, y))
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx == 0 and dy == 0:
                continue
            outline_surf = font.render(text, True, outline_color)
            outline_rect = outline_surf.get_rect(center=(center_x + dx, y + dy))
            screen.blit(outline_surf, outline_rect.topleft)
    screen.blit(text_surf, text_rect.topleft)

def draw_button(screen, text, x, y, width, height, color, text_color, flash=False):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, DARK_PURPLE, rect.inflate(4, 4))
    pygame.draw.rect(screen, color, rect)
    outline_color = WHITE if flash else BLACK
    pygame.draw.rect(screen, outline_color, rect, 2)
    draw_text_with_outline(screen, text, font, text_color, x + width//2, y + height//2)
    return rect

def draw_text_input(screen, text, x, y, width, height, active, flash=False):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, DARK_PURPLE, rect.inflate(4, 4))
    pygame.draw.rect(screen, WHITE, rect)
    outline_color = WHITE if flash else BLUE if active else (200, 200, 200)
    pygame.draw.rect(screen, outline_color, rect, 3)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surf, text_rect.topleft)
    return rect

# ---------------- MAIN LOOP ----------------
def main():
    clock = pygame.time.Clock()
    game = GameState()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # ----- EVENTS -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Username input flash
            if game.game_phase == "username_entry" and event.type == pygame.KEYDOWN:
                flash_triggered = False
                if event.key == pygame.K_RETURN:
                    game.handle_username_input("ENTER")
                    flash_triggered = True
                elif event.key == pygame.K_BACKSPACE:
                    game.handle_username_input("BACKSPACE")
                    flash_triggered = True
                elif event.unicode.isalnum() or event.unicode == " ":
                    game.handle_username_input(event.unicode)
                    flash_triggered = True
                if flash_triggered:
                    game.flash_start = time.time()

            # Playing phase
            elif game.game_phase == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
                # Number buttons
                if not game.round_complete:
                    for i, number in enumerate(game.numbers):
                        button_rect = pygame.Rect(150 + i*100, 300, 80, 60)
                        if button_rect.collidepoint(mouse_pos):
                            game.make_guess(number)
                            game.flash_start = time.time()
                            break

                # Next Round button
                if game.round_complete and game.player1_score > 0 and game.player2_score > 0:
                    next_rect = pygame.Rect(300, 500, 200, 50)
                    if next_rect.collidepoint(mouse_pos):
                        game.new_round()
                        game.flash_start = time.time()

                # New Game button
                if game.player1_score == 0 or game.player2_score == 0:
                    new_game_rect = pygame.Rect(300, 500, 200, 50)
                    if new_game_rect.collidepoint(mouse_pos):
                        game.new_game()
                        game.flash_start = time.time()

        # ---------------- DRAW ----------------
        screen.blit(get_background_frame(), (0, 0))

        flash_active = game.flash_start and (time.time() - game.flash_start < game.flash_duration)
        win_flash_active = game.win_flash_start and (time.time() - game.win_flash_start < game.win_flash_duration)
        if game.flash_start and not flash_active:
            game.flash_start = None
        if game.win_flash_start and not win_flash_active:
            game.win_flash_start = None

        # ---------------- UI DRAW ----------------
        if game.game_phase == "username_entry":
            draw_text_with_outline(screen, "Enter Player Names", large_font, PURPLE, SCREEN_WIDTH//2, 150)
            if game.username_phase == 1:
                draw_text_with_outline(screen, "Player 1, enter your username:", font, BLUE, SCREEN_WIDTH//2, 250)
            else:
                draw_text_with_outline(screen, "Player 2, enter your username:", font, RED, SCREEN_WIDTH//2, 250)
                draw_text_with_outline(screen, f"Player 1: {game.player1_name}", font, BLUE, SCREEN_WIDTH//2, 200)
            draw_text_input(screen, game.current_input, 250, 300, 300, 40, game.input_active, flash=flash_active)
            draw_text_with_outline(screen, "Press ENTER to confirm", font, (100,100,100), SCREEN_WIDTH//2, 370)

        else:
            draw_text_with_outline(screen, "v0id's RNG", large_font, PURPLE, SCREEN_WIDTH//2, 50)
            draw_text_with_outline(screen, f"{game.player1_name}: {game.player1_score}", font, BLUE, SCREEN_WIDTH//2 - 150, 120)
            draw_text_with_outline(screen, f"{game.player2_name}: {game.player2_score}", font, RED, SCREEN_WIDTH//2 + 150, 120)

            if game.player1_guess is not None:
                color = BLUE
                if win_flash_active and game.correct_guess_player in [1, "both"]:
                    color = GOLD
                draw_text_with_outline(screen, f"{game.player1_name} guess: {game.player1_guess}", font, color, SCREEN_WIDTH//2, 180)

            if game.player2_guess is not None:
                color = RED
                if win_flash_active and game.correct_guess_player in [2, "both"]:
                    color = GOLD
                draw_text_with_outline(screen, f"{game.player2_name} guess: {game.player2_guess}", font, color, SCREEN_WIDTH//2, 220)

            draw_text_with_outline(screen, game.game_message, font, PURPLE, SCREEN_WIDTH//2, 260)

            # --- Buttons ---
            if game.round_complete and game.player1_score > 0 and game.player2_score > 0:
                draw_button(screen, "Next Round", 300, 500, 200, 50, GREEN, WHITE, flash=flash_active)
            elif not game.round_complete and game.player1_score > 0 and game.player2_score > 0:
                for i, number in enumerate(game.numbers):
                    color = BLUE if game.current_player == 1 else RED
                    draw_button(screen, str(number), 150 + i*100, 300, 80, 60, color, WHITE, flash=flash_active)

            # Game over
            if game.player1_score == 0 or game.player2_score == 0:
                winner_name = game.player2_name if game.player1_score == 0 else game.player1_name
                win_flash = GOLD if win_flash_active else YELLOW
                draw_text_with_outline(screen, f"{winner_name} Wins!", large_font, win_flash, SCREEN_WIDTH//2, 400)
                draw_button(screen, "New Game", 300, 500, 200, 50, PURPLE, WHITE, flash=flash_active)

        pygame.display.flip()
        clock.tick(20)
        

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
