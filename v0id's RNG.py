import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
GREEN = (0, 150, 0)
YELLOW = (255, 251, 0)
RED = (200, 0, 0)
PURPLE = (237, 0, 255)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("v0id's RNG")
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

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
        self.game_phase = "username_entry"  # "username_entry" or "playing"
        self.username_phase = 1  # 1 for player1, 2 for player2
        self.player1_name = ""
        self.player2_name = ""
        self.current_input = ""
        self.input_active = True

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

        if self.player1_guess == self.random_number and self.player2_guess == self.random_number:
            # If both picked the same correct number, count it as a tie — no score change
            winner = "Both guessed right!"
        elif self.player1_guess == self.random_number:
            self.player1_score += 1
            self.player2_score -= 1
            winner = self.player1_name
        elif self.player2_guess == self.random_number:
            self.player2_score += 1
            self.player1_score -= 1
            winner = self.player2_name
        else:
            winner = "Nobody"

        self.game_message = f"Random number: {self.random_number} | Winner: {winner}"
        self.round_complete = True

    def new_round(self):
        self.current_player = 1
        self.player1_guess = None
        self.player2_guess = None
        self.round_complete = False
        self.random_number = None
        self.game_message = f"{self.player1_name}: Choose your number (1-5)"

    def new_game(self):
        self.player1_score = 3
        self.player2_score = 3
        self.new_round()

def draw_button(screen, text, x, y, width, height, color, text_color):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def draw_text_input(screen, text, x, y, width, height, active):
    color = BLUE if active else (200, 200, 200)
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, color, rect, 3)
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (x + 10, y + 10))
    return rect

def main():
    clock = pygame.time.Clock()
    game = GameState()
    running = True

    while running:
        # ----- EVENTS -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

             # Username phase
            if game.game_phase == "username_entry":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game.handle_username_input("ENTER")
                    elif event.key == pygame.K_BACKSPACE:
                        game.handle_username_input("BACKSPACE")
                    else:
                        if event.unicode.isalnum() or event.unicode == " ":
                            game.handle_username_input(event.unicode)

            # Playing phase
            elif game.game_phase == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # If game over, only "New Game" is clickable
                    if game.player1_score == 0 or game.player2_score == 0:
                        new_game_rect = pygame.Rect(300, 500, 200, 50)
                        if new_game_rect.collidepoint(mouse_pos):
                            game.new_game()
                        # Skip other clicks while game over
                        continue

                    # Number buttons (only when round not complete)
                    if not game.round_complete:
                        for i, number in enumerate(game.numbers):
                            button_x = 150 + i * 100
                            button_y = 300
                            button_rect = pygame.Rect(button_x, button_y, 80, 60)
                            if button_rect.collidepoint(mouse_pos):
                                game.make_guess(number)
                                break

                    # Next Round button
                    if game.round_complete:
                        next_rect = pygame.Rect(300, 500, 200, 50)
                        if next_rect.collidepoint(mouse_pos):
                            game.new_round()

        # ----- DRAW -----
        screen.fill(BLACK)

        if game.game_phase == "username_entry":
            title = large_font.render("Enter Player Names", True, PURPLE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))

            if game.username_phase == 1:
                prompt = font.render("Player 1, enter your username:", True, BLUE)
                screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 250))
            else:
                prompt = font.render("Player 2, enter your username:", True, RED)
                screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 250))
                p1_display = font.render(f"Player 1: {game.player1_name}", True, BLUE)
                screen.blit(p1_display, (SCREEN_WIDTH//2 - p1_display.get_width()//2, 200))

            draw_text_input(screen, game.current_input, 250, 300, 300, 40, game.input_active)
            instruction = font.render("Press ENTER to confirm", True, (100, 100, 100))
            screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 370))

        else:
            # Title
            title = large_font.render("v0id's RNG", True, PURPLE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

            # Scores
            score_text1 = font.render(
                f"{game.player1_name}: {game.player1_score}",
                True, BLUE
            )
            score_text2 = font.render(
            f"{game.player2_name}: {game.player2_score}",
            True, RED
            )

            screen.blit(score_text1, (200, 120))
            screen.blit(score_text2, (500, 120))

            # Guesses
            if game.player1_guess is not None:
                p1_guess_text = font.render(f"{game.player1_name} guess: {game.player1_guess}", True, BLUE)
                screen.blit(p1_guess_text, (150, 180))
            if game.player2_guess is not None:
                p2_guess_text = font.render(f"{game.player2_name} guess: {game.player2_guess}", True, RED)
                screen.blit(p2_guess_text, (450, 180))

            # Message
            message = font.render(game.game_message, True, PURPLE)
            screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, 220))

            # Buttons for normal play
            if (game.player1_score > 0 and game.player2_score > 0):
                if not game.round_complete:
                    for i, number in enumerate(game.numbers):
                        button_x = 150 + i * 100
                        button_y = 300
                        color = BLUE if game.current_player == 1 else RED
                        draw_button(screen, str(number), button_x, button_y, 80, 60, color, WHITE)
                else:
                    draw_button(screen, "Next Round", 300, 500, 200, 50, GREEN, WHITE)

            # Game over UI
            if game.player1_score == 0 or game.player2_score == 0:
                winner_name = game.player2_name if game.player1_score == 0 else game.player1_name
                win_surf = large_font.render(f"{winner_name} Wins!", True, YELLOW)
                screen.blit(win_surf, (SCREEN_WIDTH//2 - win_surf.get_width()//2, 400))
                draw_button(screen, "New Game", 300, 500, 200, 50, PURPLE, WHITE)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
