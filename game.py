import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Get native display info for fullscreen
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Fonts
title_font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 32)
text_font = pygame.font.Font(None, 24)
hint_font = pygame.font.Font(None, 28)
blank_font = pygame.font.Font(None, 32)

class CipherGame:
    def __init__(self, main_screen=None):
        # Use existing screen if provided (from main.py), otherwise create new fullscreen
        if main_screen:
            self.screen = main_screen
            self.external_screen = True  # Flag to know we're using external screen
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            pygame.display.set_caption("Cipher Challenge Game - Fill in the Blanks")
            self.external_screen = False
        
        self.clock = pygame.time.Clock()
        self.game_should_exit = False  # Flag for returning to main menu
        
        # Game state
        self.current_screen = "menu"  # menu, game, result
        self.game_mode = None  # "encrypt" or "decrypt"
        self.cipher_key = 0
        self.original_text = ""
        self.cipher_text = ""
        self.display_text = ""  # Text with blanks
        self.blank_positions = []  # Positions of blanked letters
        self.user_inputs = {}  # Dictionary to store user inputs for each blank
        self.active_blank = None  # Currently active input blank
        self.score = 0
        self.level = 1
        self.streak = 0  # Consecutive correct answers
        self.hints_used = 0  # Track hints used
        
        # Blank input boxes
        self.blank_boxes = {}
        
        # Enhanced buttons - adjusted for fullscreen
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        self.encrypt_button = pygame.Rect(center_x - 200, center_y - 2, 200, 60)
        self.decrypt_button = pygame.Rect(center_x + 40, center_y - 2, 200, 60)
        self.submit_button = pygame.Rect(center_x - 50, center_y + 200, 100, 40)
        self.next_button = pygame.Rect(center_x - 50, center_y + 250, 100, 40)
        self.menu_button = pygame.Rect(50, 50, 100, 40)
        self.hint_button = pygame.Rect(center_x + 200, center_y - 40, 80, 30)
        
        # Enhanced sample texts with varying difficulties
        self.sample_texts = {
            1: ["HELLO WORLD", "PYGAME IS FUN", "CIPHER GAME"],
            2: ["DECODE THIS MESSAGE", "CRYPTOGRAPHY ROCKS", "SECRET MESSAGE HIDDEN"],
            3: ["BREAK THE CODE NOW", "ENCRYPTION GAME RULES", "SOLVING PUZZLES DAILY"],
            4: ["MASTER THE CIPHER TECHNIQUES", "ADVANCED CRYPTOGRAPHIC METHODS", "COMPLEX CIPHER CHALLENGES"],
            5: ["PROFESSIONAL ENCRYPTION ALGORITHMS", "SOPHISTICATED DECRYPTION PROCEDURES", "ULTIMATE CRYPTANALYSIS EXPERTISE"]
        }
    
    def caesar_cipher(self, text, shift, decrypt=False):
        """Apply Caesar cipher to text"""
        if decrypt:
            shift = -shift
        
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - ascii_offset + shift) % 26
                result += chr(shifted + ascii_offset)
            else:
                result += char
        return result
    
    def create_blanks(self, text):
        """Create blanks in the text and return positions"""
        # Get only alphabetic characters and their positions
        letter_positions = [(i, char) for i, char in enumerate(text) if char.isalpha()]
        
        if len(letter_positions) < 3:
            # If text is too short, blank all letters
            blank_count = len(letter_positions)
        else:
            # Determine number of blanks based on level (3-7 blanks)
            min_blanks = min(3, len(letter_positions))
            max_blanks = min(3 + self.level, len(letter_positions))
            blank_count = random.randint(min_blanks, max_blanks)
        
        # Randomly select positions to blank
        selected_positions = random.sample(letter_positions, blank_count)
        self.blank_positions = [pos for pos, char in selected_positions]
        
        # Create display text with blanks
        display_chars = list(text)
        for pos in self.blank_positions:
            display_chars[pos] = "_"
        
        return "".join(display_chars)
    
    def generate_challenge(self):
        """Generate a new cipher challenge with blanks"""
        self.cipher_key = random.randint(1, 25)
        
        # Select text based on level
        level_key = min(self.level, 5)  # Cap at level 5 for text selection
        self.original_text = random.choice(self.sample_texts[level_key])
        
        if self.game_mode == "encrypt":
            # Show original text, user fills blanks in cipher
            self.cipher_text = self.caesar_cipher(self.original_text, self.cipher_key)
            self.display_text = self.create_blanks(self.cipher_text)
            self.target_text = self.cipher_text
        else:  # decrypt mode
            # Show cipher text, user fills blanks in original
            self.cipher_text = self.caesar_cipher(self.original_text, self.cipher_key)
            self.display_text = self.create_blanks(self.original_text)
            self.target_text = self.original_text
        
        # Reset user inputs and hints
        self.user_inputs = {pos: "" for pos in self.blank_positions}
        self.active_blank = None
        self.hints_used = 0
    
    def create_blank_input_boxes(self, text_start_pos):
        """Create input boxes aligned with blank positions in text"""
        self.blank_boxes = {}
        char_width = 20  # Character width for monospace-like spacing
        
        start_x, start_y = text_start_pos
        
        for pos in self.blank_positions:
            # Calculate exact position based on character position in text
            box_x = start_x + (pos * char_width)
            box_y = start_y - 5  # Slightly above the text baseline
            
            self.blank_boxes[pos] = pygame.Rect(box_x, box_y, 25, 30)
    
    def give_hint(self):
        """Provide a hint by revealing one random blank"""
        if self.hints_used >= 2:  # Limit hints per challenge
            return False
        
        # Find unfilled blanks
        unfilled_blanks = [pos for pos in self.blank_positions if not self.user_inputs[pos].strip()]
        
        if unfilled_blanks:
            hint_pos = random.choice(unfilled_blanks)
            correct_char = self.target_text[hint_pos] if hint_pos < len(self.target_text) else ""
            self.user_inputs[hint_pos] = correct_char
            self.hints_used += 1
            return True
        return False

    def draw_button(self, button_rect, text, color):
        """Draw a button with text and handle hover effects"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is hovering over button
        if button_rect.collidepoint(mouse_pos):
            # Lighter color when hovering
            hover_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(self.screen, hover_color, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 3)  # White border
        else:
            # Normal color
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)  # Black border
        
        # Draw button text
        text_surface = text_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_menu(self):
        """Draw the main menu screen"""
        # Load and scale the background image if not already loaded
        if not hasattr(self, 'menu_background'):
            try:
                self.menu_background = pygame.image.load("assets/cipher_bg.jpg")
                self.menu_background = pygame.transform.scale(self.menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except pygame.error:
                self.menu_background = None
                print("Menu background image not found, using fallback color")
        
        # Use background image instead of white fill
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill(WHITE)
        
        # Title with enhanced styling - centered for fullscreen
        title_text = title_font.render("Cipher Challenge Game", True, WHITE)
        title_shadow = title_font.render("Cipher Challenge Game", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 2, SCREEN_HEIGHT//4 + 2))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = text_font.render("Fill in the Blanks Edition", True, CYAN)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 40))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Enhanced instructions - centered for fullscreen
        instructions = [
            "Choose your challenge:",
            "ENCRYPT: Fill missing letters in cipher text",
            "DECRYPT: Fill missing letters in plain text",
            f"Level {self.level}: {3 + self.level} blanks to fill!",
            "Use hints wisely - only 2 per challenge!",
            "Build streaks for bonus points!"
        ]
        
        start_y = SCREEN_HEIGHT//4 + 80
        for i, instruction in enumerate(instructions):
            text_surface = text_font.render(instruction, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, start_y + i * 25))
            self.screen.blit(text_surface, text_rect)
        
        # Buttons
        self.draw_button(self.encrypt_button, "ENCRYPT", GREEN)
        self.draw_button(self.decrypt_button, "DECRYPT", RED)
        
        # Enhanced score display - bottom of screen
        score_text = text_font.render(f"Score: {self.score} | Level: {self.level} | Streak: {self.streak}", True, WHITE)
        self.screen.blit(score_text, (50, SCREEN_HEIGHT - 50))
        
        # Go to main.py instruction
        exit_text = text_font.render("Press ESC to return to main menu", True, WHITE)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(exit_text, exit_rect)
    
    def draw_text_with_aligned_blanks(self, text, start_pos):
        """Draw text with blank input boxes aligned to missing letters"""
        x, y = start_pos
        char_width = 21
        
        # Create input boxes aligned with text positions
        self.create_blank_input_boxes(start_pos)
        
        # Draw each character or blank
        for i, char in enumerate(text):
            char_x = x + (i * char_width)
            
            if i in self.blank_positions:
                # Draw the input box for this blank position
                box = self.blank_boxes[i]
                
                # Enhanced box colors
                if self.active_blank == i:
                    color = YELLOW
                elif self.user_inputs[i].strip():
                    color = GREEN
                else:
                    color = LIGHT_GRAY
                
                pygame.draw.rect(self.screen, WHITE, box)
                pygame.draw.rect(self.screen, color, box, 3)
                
                # Draw user input in box
                if i in self.user_inputs and self.user_inputs[i]:
                    input_surface = blank_font.render(self.user_inputs[i], True, BLACK)
                    input_rect = input_surface.get_rect(center=box.center)
                    self.screen.blit(input_surface, input_rect)
                else:
                    # Draw underscore placeholder in the box
                    placeholder_surface = blank_font.render("_", True, GRAY)
                    placeholder_rect = placeholder_surface.get_rect(center=box.center)
                    self.screen.blit(placeholder_surface, placeholder_rect)
            else:
                # Draw normal character with enhanced visibility
                char_surface = button_font.render(char, True, YELLOW)
                self.screen.blit(char_surface, (char_x, y))
    
    def draw_game(self):
        """Draw the game screen"""
        # Load and scale the background image if not already loaded
        if not hasattr(self, 'game_background'):
            try:
                self.game_background = pygame.image.load("assets/game_bg.jpg")
                self.game_background = pygame.transform.scale(self.game_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except pygame.error:
                self.game_background = None
                print("Game background image not found, using fallback color")
        
        # Use background image instead of white fill
        if self.game_background:
            self.screen.blit(self.game_background, (0, 0))
        else:
            self.screen.fill(WHITE)
        
        # Menu button
        self.draw_button(self.menu_button, "MENU", GRAY)
        
        # Title with enhanced styling - adjusted for fullscreen
        mode_text = "ENCRYPTION" if self.game_mode == "encrypt" else "DECRYPTION"
        title_text = title_font.render(f"{mode_text} Challenge", True, WHITE)
        title_shadow = title_font.render(f"{mode_text} Challenge", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 2, 82))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Enhanced level and score display
        level_text = text_font.render(f"Level: {self.level} | Score: {self.score} | Streak: {self.streak}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, 120))
        self.screen.blit(level_text, level_rect)
        
        # Key hint with enhanced styling
        hint_text = hint_font.render(f"Key Hint: {self.cipher_key}", True, CYAN)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(hint_text, hint_rect)
        
        # Challenge text - centered for fullscreen
        if self.game_mode == "encrypt":
            challenge_label = "Original Text:"
            given_text = self.original_text
            fill_label = "Fill the missing letters in the cipher text:"
        else:
            challenge_label = "Cipher Text:"
            given_text = self.cipher_text
            fill_label = "Fill the missing letters in the plain text:"
        
        # Display given text with enhanced visibility - centered
        label_surface = text_font.render(challenge_label, True, WHITE)
        label_rect = label_surface.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(label_surface, label_rect)
        
        given_surface = button_font.render(given_text, True, YELLOW)
        given_rect = given_surface.get_rect(center=(SCREEN_WIDTH//2, 230))
        self.screen.blit(given_surface, given_rect)
        
        # Display text with blanks to fill - centered
        fill_surface = text_font.render(fill_label, True, WHITE)
        fill_rect = fill_surface.get_rect(center=(SCREEN_WIDTH//2, 280))
        self.screen.blit(fill_surface, fill_rect)
        
        text_width = len(self.display_text) * 25
        text_pos = ((SCREEN_WIDTH - text_width) // 2, 330)
        self.draw_text_with_aligned_blanks(self.display_text, text_pos)
        
        # Hint button
        hint_color = ORANGE if self.hints_used < 2 else GRAY
        self.draw_button(self.hint_button, "HINT", hint_color)
        
        # Hint counter
        hint_text = pygame.font.Font(None, 18).render(f"Hints: {2 - self.hints_used}/2", True, WHITE)
        self.screen.blit(hint_text, (self.hint_button.x, self.hint_button.y + 35))
        
        # Enhanced instructions - centered for fullscreen
        instructions = [
            "Click on boxes to fill in missing letters",
            "Use Caesar cipher key and context clues",
            f"Blanks to fill: {len([pos for pos in self.blank_positions if not self.user_inputs[pos].strip()])}/{len(self.blank_positions)}",
            "Press ENTER to move to next blank"
        ]
        
        start_y = SCREEN_HEIGHT//2 + 100
        for i, instruction in enumerate(instructions):
            text_surface = pygame.font.Font(None, 20).render(instruction, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, start_y + i * 25))
            self.screen.blit(text_surface, text_rect)
        
        # Submit button with enhanced feedback
        all_filled = all(self.user_inputs[pos].strip() for pos in self.blank_positions)
        button_color = GREEN if all_filled else GRAY
        self.draw_button(self.submit_button, "SUBMIT", button_color)
        
        if not all_filled:
            status_text = text_font.render("Fill all blanks to submit", True, RED)
            status_rect = status_text.get_rect(center=(SCREEN_WIDTH//2, self.submit_button.y + 45))
            self.screen.blit(status_text, status_rect)
        else:
            ready_text = text_font.render("Ready to submit!", True, GREEN)
            ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH//2, self.submit_button.y + 45))
            self.screen.blit(ready_text, ready_rect)
    
    def draw_result(self):
        """Draw the result screen with enhanced feedback"""
        # Reconstruct user's answer
        user_answer = list(self.display_text)
        for pos in self.blank_positions:
            if pos < len(user_answer):
                user_answer[pos] = self.user_inputs[pos].upper()
        user_answer_str = "".join(user_answer)
        
        # Check if answer is correct
        is_correct = user_answer_str.upper() == self.target_text.upper()
        
        # Load background for result screen
        if not hasattr(self, 'result_background') or (hasattr(self, 'last_result_correct') and self.last_result_correct != is_correct):
            try:
                bg_path = "assets/correct.png" if is_correct else "assets/challenge_bg.jpg"
                self.result_background = pygame.image.load(bg_path)
                self.result_background = pygame.transform.scale(self.result_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.last_result_correct = is_correct
            except pygame.error:
                self.result_background = None
        
        if self.result_background:
            self.screen.blit(self.result_background, (0, 0))
        else:
            self.screen.fill(WHITE)
        
        # Menu button
        self.draw_button(self.menu_button, "MENU", GRAY)
        
        # Enhanced result title - centered for fullscreen
        if is_correct:
            result_title = "EXCELLENT!" if self.streak >= 3 else "CORRECT!"
            title_color = CYAN if self.streak >= 3 else GREEN
        else:
            result_title = "INCORRECT!"
            title_color = RED
            
        title_text = title_font.render(result_title, True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title_text, title_rect)
        
        # Show the correct answer - centered
        answer_text = text_font.render(f"Correct answer: {self.target_text}", True, WHITE)
        answer_rect = answer_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 70))
        self.screen.blit(answer_text, answer_rect)
        
        # Show user's answer - centered
        user_text = text_font.render(f"Your answer: {user_answer_str}", True, WHITE)
        user_rect = user_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 110))
        self.screen.blit(user_text, user_rect)
        
        # Enhanced blank results - centered
        blank_results = []
        for pos in self.blank_positions:
            correct_char = self.target_text[pos] if pos < len(self.target_text) else ""
            user_char = self.user_inputs[pos].upper()
            status = "✓" if user_char == correct_char else "✗"
            blank_results.append(f"Position {pos+1}: {user_char} {status}")
        
        results_text = text_font.render("Blank Results:", True, WHITE)
        results_rect = results_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 150))
        self.screen.blit(results_text, results_rect)
        
        start_y = SCREEN_HEIGHT//4 + 180
        for i, result in enumerate(blank_results):
            color = GREEN if "✓" in result else RED
            result_surface = pygame.font.Font(None, 20).render(result, True, color)
            result_rect = result_surface.get_rect(center=(SCREEN_WIDTH//2, start_y + i * 25))
            self.screen.blit(result_surface, result_rect)
        
        # Enhanced scoring with streak bonuses - centered (preview, actual update in handle_result_events)
        base_points = 15 * self.level
        if is_correct:
            streak_bonus = self.streak * 5 if self.streak > 1 else 0
            hint_penalty = self.hints_used * 5
            total_points = max(base_points + streak_bonus - hint_penalty, 5)
            score_text = text_font.render(f"+{total_points} points! (Base: {base_points}, Streak: +{streak_bonus}, Hints: -{hint_penalty})", True, GREEN)
        else:
            # Partial credit
            correct_blanks = sum(1 for pos in self.blank_positions 
                               if pos < len(self.target_text) and 
                               self.user_inputs[pos].upper() == self.target_text[pos])
            if correct_blanks > 0:
                partial_points = (correct_blanks * 5 * self.level) // len(self.blank_positions)
                score_text = text_font.render(f"+{partial_points} points (partial credit)", True, BLUE)
            else:
                score_text = text_font.render("No points this time", True, RED)
        
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        self.screen.blit(score_text, score_rect)
        
        # Current score - centered
        current_score_text = text_font.render(f"Total Score: {self.score}", True, WHITE)
        current_score_rect = current_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
        self.screen.blit(current_score_text, current_score_rect)
        
        # Next button
        self.draw_button(self.next_button, "NEXT", BLUE)
    
    def handle_menu_events(self, event):
        """Handle events on the menu screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.encrypt_button.collidepoint(event.pos):
                self.game_mode = "encrypt"
                self.generate_challenge()
                self.current_screen = "game"
            elif self.decrypt_button.collidepoint(event.pos):
                self.game_mode = "decrypt"
                self.generate_challenge()
                self.current_screen = "game"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_should_exit = True # Return to main.py option 
    
    def handle_game_events(self, event):
        """Handle events on the game screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on blank boxes
            clicked_blank = None
            for pos, box in self.blank_boxes.items():
                if box.collidepoint(event.pos):
                    clicked_blank = pos
                    break
            
            self.active_blank = clicked_blank
            
            # Check hint button
            if self.hint_button.collidepoint(event.pos):
                self.give_hint()
            
            # Check submit button
            all_filled = all(self.user_inputs[pos].strip() for pos in self.blank_positions)
            if self.submit_button.collidepoint(event.pos) and all_filled:
                self.current_screen = "result"
            elif self.menu_button.collidepoint(event.pos):
                self.current_screen = "menu"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_should_exit = True
            elif self.active_blank is not None:
                if event.key == pygame.K_RETURN:
                    # Move to next blank or submit if all filled
                    current_index = self.blank_positions.index(self.active_blank)
                    if current_index < len(self.blank_positions) - 1:
                        self.active_blank = self.blank_positions[current_index + 1]
                    else:
                        all_filled = all(self.user_inputs[pos].strip() for pos in self.blank_positions)
                        if all_filled:
                            self.current_screen = "result"
                elif event.key == pygame.K_BACKSPACE:
                    self.user_inputs[self.active_blank] = ""
                elif event.unicode.isalpha() and len(event.unicode) == 1:
                    # Only accept single letters
                    self.user_inputs[self.active_blank] = event.unicode.upper()
    
    def handle_result_events(self, event):
        """Handle events on the result screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_button.collidepoint(event.pos):
                # Reconstruct user's answer for scoring
                user_answer = list(self.display_text)
                for pos in self.blank_positions:
                    if pos < len(user_answer):
                        user_answer[pos] = self.user_inputs[pos].upper()
                user_answer_str = "".join(user_answer)
                
                # Update score and streak
                is_correct = user_answer_str.upper() == self.target_text.upper()
                if is_correct:
                    self.streak += 1
                    base_points = 15 * self.level
                    streak_bonus = self.streak * 5 if self.streak > 1 else 0
                    hint_penalty = self.hints_used * 5
                    total_points = max(base_points + streak_bonus - hint_penalty, 5)
                    self.score += total_points
                else:
                    self.streak = 0
                    # Partial credit
                    correct_blanks = sum(1 for pos in self.blank_positions 
                                       if pos < len(self.target_text) and 
                                       self.user_inputs[pos].upper() == self.target_text[pos])
                    if correct_blanks > 0:
                        partial_points = (correct_blanks * 5 * self.level) // len(self.blank_positions)
                        self.score += partial_points
                
                # Level up check (every 100 points)
                if self.score > 0 and self.score % 100 == 0 and self.score // 100 > self.level - 1:
                    self.level += 1
                
                self.generate_challenge()
                self.current_screen = "game"
            elif self.menu_button.collidepoint(event.pos):
                self.current_screen = "menu"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_should_exit = True
    
    def run(self):
        """Main game loop"""
        running = True
        while running and not self.game_should_exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    if not self.external_screen:
                        pygame.quit()
                        sys.exit()
                
                if self.current_screen == "menu":
                    self.handle_menu_events(event)
                elif self.current_screen == "game":
                    self.handle_game_events(event)
                elif self.current_screen == "result":
                    self.handle_result_events(event)
            
            # Draw current screen
            if self.current_screen == "menu":
                self.draw_menu()
            elif self.current_screen == "game":
                self.draw_game()
            elif self.current_screen == "result":
                self.draw_result()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        if not self.external_screen:
            pygame.quit()
            import main
            main.main_menu()
        # If external screen (from main.py), just return without quitting

def cipher_game_screen(screen=None):
    """Function to run the cipher game screen, callable from main.py"""
    game = CipherGame(main_screen=screen)
    game.run()

if __name__ == "__main__":
    game = CipherGame()
    game.run()