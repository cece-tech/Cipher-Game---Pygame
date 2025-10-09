import pygame
import sys
import os
import json
import math
from datetime import datetime
from button import Button, get_font, load_image
from game import CipherGame


pygame.init()
pygame.mixer.init()

# Get native display info for fullscreen
info = pygame.display.Info()
SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 720

# Load and play background music
try:
    back_music = pygame.mixer.Sound("assets/lalala.mp3")
    back_music.play(-1)  # Play indefinitely (-1 means loop forever)
    back_music.set_volume(0.5)  # Set volume to 50%
except pygame.error:
    print("Background music file not found or could not be loaded")
    back_music = None

# Load click sound effect
try:
    click_sound = pygame.mixer.Sound("assets/nintendo-game-boy-startup.mp3")
    click_sound.set_volume(0.7)  # Set click volume to 70%
except pygame.error:
    print("Click sound file not found, trying alternative formats")
    try:
        # Try alternative sound file names/formats
        click_sound = pygame.mixer.Sound("assets/click.mp3")
        click_sound.set_volume(0.7)
    except:
        try:
            click_sound = pygame.mixer.Sound("assets/click.ogg")
            click_sound.set_volume(0.7)
        except:
            click_sound = None
            print("No click sound available - continuing without sound effects")

def play_click_sound():
    """Play button click sound effect"""
    if click_sound:
        try:
            click_sound.play()
        except:
            pass  # Silently fail if sound can't play

# Global list to store cipher history
cipher_history = []

# Initialize screen in fullscreen mode
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Alphanumeric Cipher System - Fullscreen")

# Create a simple background color instead of loading image
BG_COLOR = (50, 50, 100)  # Dark blue background

def draw_gradient_background(surface, color1, color2):
    """Draw a gradient background"""
    width = surface.get_width()
    height = surface.get_height()
    
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

def draw_glowing_rect(surface, rect, color, glow_color, border_width=3):
    """Draw a rectangle with glowing border effect"""
    # Draw multiple layers for glow effect
    for i in range(5, 0, -1):
        alpha = 50 - i * 8
        glow_surf = pygame.Surface((rect.width + i*4, rect.height + i*4), pygame.SRCALPHA)
        glow_rect = pygame.Rect(0, 0, rect.width + i*4, rect.height + i*4)
        pygame.draw.rect(glow_surf, (*glow_color, alpha), glow_rect, border_radius=8)
        surface.blit(glow_surf, (rect.x - i*2, rect.y - i*2))
    
    # Draw main rectangle
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, glow_color, rect, border_width, border_radius=8)

def draw_animated_background(surface, time_offset=0):
    """Draw animated background with diagonal lines"""
    width = surface.get_width()
    height = surface.get_height()
    
    # Base gradient
    draw_gradient_background(surface, (26, 11, 61), (45, 27, 105))
    
    # Animated diagonal lines
    line_color = (58, 30, 120, 30)
    line_spacing = 150
    line_thickness = 2
    
    for i in range(-height, width + height, line_spacing):
        start_x = i + int(time_offset * 0.5) % line_spacing
        start_y = 0
        end_x = start_x + height
        end_y = height
        
        line_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.line(line_surf, line_color, (start_x, start_y), (end_x, end_y), line_thickness)
        surface.blit(line_surf, (0, 0))

# Save/Load functions for cipher history
def save_cipher_result(cipher_type, cipher_class, operation, plaintext, key, result):
    """Save cipher result to history"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_entry = {
        "timestamp": timestamp,
        "cipher_type": cipher_type,
        "cipher_class": cipher_class,
        "operation": operation,
        "plaintext": plaintext,
        "key": str(key),
        "result": result
    }
    cipher_history.append(history_entry)
    
    # Also save to file
    try:
        with open("cipher_history.json", "w") as f:
            json.dump(cipher_history, f, indent=2)
    except:
        pass  # Ignore file save errors

def load_cipher_history():
    """Load cipher history from file"""
    global cipher_history
    try:
        if os.path.exists("cipher_history.json"):
            with open("cipher_history.json", "r") as f:
                cipher_history = json.load(f)
    except:
        cipher_history = []

def show_save_option_with_automation(result, result_type, cipher_type, cipher_class, operation, plaintext, key, cipher_name):
    """Enhanced save option with automation buttons for quick operations"""
    clock = pygame.time.Clock()
    while True:
        MOUSE_POS = pygame.mouse.get_pos()
        
        SCREEN.fill("black")
        
        # Display the result first
        title_text = get_font(25).render(f"{result_type}:", True, "Green")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        SCREEN.blit(title_text, title_rect)
        
        # Split long results into multiple lines
        max_chars = 60
        result_lines = []
        if len(result) > max_chars:
            for i in range(0, len(result), max_chars):
                result_lines.append(result[i:i+max_chars])
        else:
            result_lines = [result]
        
        # Display result lines
        for i, line in enumerate(result_lines):
            line_surface = get_font(20).render(line, True, "White")
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH//2, 140 + i * 30))
            SCREEN.blit(line_surface, line_rect)
        
        # Display original text and key info
        info_y = 140 + len(result_lines) * 30 + 30
        info_text = get_font(16).render(f"Original: {plaintext[:50]}{'...' if len(plaintext) > 50 else ''}", True, "Cyan")
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH//2, info_y))
        SCREEN.blit(info_text, info_rect)
        
        key_text = get_font(16).render(f"Key: {str(key)}", True, "Cyan")
        key_rect = key_text.get_rect(center=(SCREEN_WIDTH//2, info_y + 25))
        SCREEN.blit(key_text, key_rect)
        
        # Save option question
        save_question = get_font(20).render("Save this result?", True, "Yellow")
        save_rect = save_question.get_rect(center=(SCREEN_WIDTH//2, info_y + 70))
        SCREEN.blit(save_question, save_rect)
        
        # Save and Continue buttons (top row)
        button_y1 = info_y + 110
        SAVE_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2 - 100, button_y1), 
                            text_input="SAVE", font=get_font(25), base_color="Green", hovering_color="White")
        CONTINUE_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2 + 100, button_y1), 
                                text_input="CONTINUE", font=get_font(25), base_color="White", hovering_color="Red")
        
        # Automation buttons section
        automation_label = get_font(18).render("Quick Actions:", True, "Orange")
        automation_rect = automation_label.get_rect(center=(SCREEN_WIDTH//2, button_y1 + 60))
        SCREEN.blit(automation_label, automation_rect)
        
        button_y2 = button_y1 + 90
        button_y3 = button_y1 + 130
        
        # Automation buttons (second and third rows)
        SOLUTION_ENCRYPT_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, button_y2), 
                                        text_input="ENCRYPT STEPS", font=get_font(20), base_color="Blue", hovering_color="White")
        SOLUTION_DECRYPT_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2 + 300, button_y2), 
                                        text_input="DECRYPT STEPS", font=get_font(20), base_color="Purple", hovering_color="White")
        
        # Back to menu button
        BACK_MENU_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, button_y3), 
                                 text_input="BACK TO MENU", font=get_font(20), base_color="Gray", hovering_color="White")
        
        buttons = [SAVE_BUTTON, CONTINUE_BUTTON, SOLUTION_ENCRYPT_BUTTON, 
                  SOLUTION_DECRYPT_BUTTON, BACK_MENU_BUTTON]
        
        for button in buttons:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC to go back to menu
                    return "BACK"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if SAVE_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    save_cipher_result(cipher_type, cipher_class, operation, plaintext, key, result)
                    show_save_confirmation()
                    return "CONTINUE"
                elif CONTINUE_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return "CONTINUE"
                elif SOLUTION_ENCRYPT_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    action = show_solution_automation(cipher_name, plaintext, key, "ENCRYPT")
                    if action == "RETURN_TO_SAVE":
                        continue
                    else:
                        return action
                elif SOLUTION_DECRYPT_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    action = show_solution_automation(cipher_name, result, key, "DECRYPT")
                    if action == "RETURN_TO_SAVE":
                        continue
                    else:
                        return action
                elif BACK_MENU_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return "BACK"
        
        pygame.display.update()
        clock.tick(60)

def show_solution_automation(cipher_name, text, key, operation):
    """Show step-by-step solution for the specified operation with return option"""
    if cipher_name == "ADDITIVE CIPHER":
        mode = 'e' if operation == "ENCRYPT" else 'd'
        result, steps = additive_encrypt_decrypt_with_solution(text, mode, key)
    elif cipher_name == "AUTO-KEY CIPHER":
        if operation == "ENCRYPT":
            result, steps = autokey_encrypt_with_solution(text, key)
        else:
            result, steps = autokey_decrypt_with_solution(text, key)
    elif cipher_name == "VIGENÈRE CIPHER":
        if operation == "ENCRYPT":
            result, steps = vigenere_encrypt_with_solution(text, key)
        else:
            result, steps = vigenere_decrypt_with_solution(text, key)
    
    return show_result_with_solution_and_return(result, operation, text, key, steps)

def show_result_with_solution_and_return(result, operation, text, key, steps):
    """Display solution with option to return to save screen"""
    clock = pygame.time.Clock()
    scroll_offset = 0
    max_scroll = 0
    
    while True:
        MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("black")
        
        # Title
        title_text = get_font(25).render(f"{operation} SOLUTION", True, "Green")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        SCREEN.blit(title_text, title_rect)
        
        # Input information
        input_info = f"Input: {text[:50]}{'...' if len(text) > 50 else ''}"
        key_info = f"Key: {str(key)}"
        result_info = f"Result: {result[:50]}{'...' if len(result) > 50 else ''}"
        
        info_y = 70
        for info in [input_info, key_info, result_info]:
            info_surface = get_font(14).render(info, True, "Cyan")
            info_rect = info_surface.get_rect(center=(SCREEN_WIDTH//2, info_y))
            SCREEN.blit(info_surface, info_rect)
            info_y += 20
        
        # Steps section
        steps_title = get_font(20).render("Step-by-Step Solution:", True, "Yellow")
        steps_rect = steps_title.get_rect(center=(SCREEN_WIDTH//2, info_y + 20))
        SCREEN.blit(steps_title, steps_rect)
        
        # Calculate scrolling
        start_y = info_y + 50
        line_height = 20
        total_height = len(steps) * line_height
        screen_height = SCREEN_HEIGHT - start_y - 100
        max_scroll = max(0, total_height - screen_height)
        
        # Display steps with scrolling
        current_y = start_y - scroll_offset
        for i, step in enumerate(steps):
            if current_y > SCREEN_HEIGHT - 100:
                break
            if current_y >= start_y - 30:
                step_surface = get_font(12).render(f"{i+1}. {step}", True, "White")
                step_rect = step_surface.get_rect(center=(SCREEN_WIDTH//2, current_y))
                SCREEN.blit(step_surface, step_rect)
            current_y += line_height
        
        # Navigation buttons
        button_y = SCREEN_HEIGHT - 80
        
        # Return to Save Options button (left)
        RETURN_SAVE_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2 - 150, button_y), 
                                   text_input="RETURN TO SAVE", font=get_font(18), 
                                   base_color="Orange", hovering_color="White")
        
        # Back to Menu button (right)
        CONTINUE_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2 + 150, button_y), 
                                 text_input="CONTINUE", font=get_font(18), 
                                 base_color="Green", hovering_color="White")
        
        buttons = [RETURN_SAVE_BUTTON, CONTINUE_BUTTON]
        
        for button in buttons:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)
        
        # Instructions
        if max_scroll > 0:
            nav_text = get_font(12).render("UP/DOWN: scroll | ESC: back to menu", True, "Orange")
        else:
            nav_text = get_font(12).render("ESC: back to menu", True, "Orange")
        nav_rect = nav_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        SCREEN.blit(nav_text, nav_rect)
        
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "BACK"
                elif event.key == pygame.K_UP and max_scroll > 0:
                    scroll_offset = max(0, scroll_offset - 20)
                elif event.key == pygame.K_DOWN and max_scroll > 0:
                    scroll_offset = min(max_scroll, scroll_offset + 20)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if RETURN_SAVE_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return "RETURN_TO_SAVE"
                elif CONTINUE_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return "CONTINUE"

def show_save_confirmation():
    """Show confirmation that result was saved"""
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    while pygame.time.get_ticks() - start_time < 2000:  # Show for 2 seconds
        SCREEN.fill("black")
        
        confirmation_text = get_font(25).render("Result saved successfully!", True, "Green")
        confirmation_rect = confirmation_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        SCREEN.blit(confirmation_text, confirmation_rect)
        
        pygame.display.update()
        clock.tick(60)
        
        # Allow early exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

def show_result(result, result_type):
    """Display result with basic formatting (fallback)"""
    clock = pygame.time.Clock()
    while True:
        SCREEN.fill("black")
        
        # Split long results into multiple lines
        max_chars = 50
        result_lines = []
        if len(result) > max_chars:
            for i in range(0, len(result), max_chars):
                result_lines.append(result[i:i+max_chars])
        else:
            result_lines = [result]
        
        # Display title
        title_text = get_font(25).render(f"{result_type}:", True, "Green")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        SCREEN.blit(title_text, title_rect)
        
        # Display result lines
        for i, line in enumerate(result_lines):
            line_surface = get_font(20).render(line, True, "White")
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH//2, 250 + i * 30))
            SCREEN.blit(line_surface, line_rect)
        
        continue_text = get_font(20).render("Press any key to continue", True, "Yellow")
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, 450))
        SCREEN.blit(continue_text, continue_rect)
        
        pygame.display.update()
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                return

def enhanced_cipher_operation_menu(cipher_name, encrypt_func, decrypt_func, encrypt_solution_func, decrypt_solution_func, screen, screen_width, screen_height, get_font_func, Button, get_text_input_func):
    """Fully functional enhanced cipher operation menu with input fields and operations"""
    clock = pygame.time.Clock()
    time_counter = 0
    
    # Input states
    plaintext_input = ""
    key_input = ""
    result_output = ""
    solutions_output = []
    current_operation = "ENCRYPTION"
    
    # Input field states
    active_field = None
    
    while True:
        time_counter += 1
        MOUSE_POS = pygame.mouse.get_pos()
        
        # Draw animated background
        draw_animated_background(screen, time_counter)
        
        # Title box with glow
        title_box = pygame.Rect(screen_width//2 - 300, 60, 600, 60)
        draw_glowing_rect(screen, title_box, (0, 0, 0, 180), (0, 255, 136), 2)
        
        TITLE_TEXT = get_font_func(28).render(cipher_name.upper(), True, (255, 255, 255))
        TITLE_RECT = TITLE_TEXT.get_rect(center=(screen_width//2, 90))
        screen.blit(TITLE_TEXT, TITLE_RECT)
        
        # Main input section box
        input_box_main = pygame.Rect(screen_width//2 - 440, 150, 880, 60)
        draw_glowing_rect(screen, input_box_main, (26, 11, 61, 200), (0, 255, 136), 3)
        
        # Input field headers
        header_y = 165
        
        # Plaintext header and input
        plaintext_header_rect = pygame.Rect(screen_width//2 - 420, header_y, 260, 30)
        if plaintext_header_rect.collidepoint(MOUSE_POS) or active_field == "plaintext":
            if active_field == "plaintext":
                draw_glowing_rect(screen, plaintext_header_rect, (0, 0, 0, 150), (255, 255, 0), 2)
            else:
                draw_glowing_rect(screen, plaintext_header_rect, (0, 0, 0, 150), (255, 200, 0), 2)
        else:
            draw_glowing_rect(screen, plaintext_header_rect, (0, 0, 0, 150), (0, 255, 136), 2)
        plaintext_text = get_font_func(14).render("PLAINTEXT:", True, (255, 255, 255))
        screen.blit(plaintext_text, (screen_width//2 - 410, header_y + 7))
        
        # Key header and input
        key_header_rect = pygame.Rect(screen_width//2 - 130, header_y, 220, 30)
        if key_header_rect.collidepoint(MOUSE_POS) or active_field == "key":
            if active_field == "key":
                draw_glowing_rect(screen, key_header_rect, (0, 0, 0, 150), (255, 255, 0), 2)
            else:
                draw_glowing_rect(screen, key_header_rect, (0, 0, 0, 150), (255, 200, 0), 2)
        else:
            draw_glowing_rect(screen, key_header_rect, (0, 0, 0, 150), (0, 255, 136), 2)
        key_text = get_font_func(14).render("KEY VALUE:", True, (255, 255, 255))
        screen.blit(key_text, (screen_width//2 - 120, header_y + 7))
        
        # Operation toggle button
        operation_rect = pygame.Rect(screen_width//2 + 103, header_y, 220, 30)
        if current_operation == "ENCRYPTION":
            draw_glowing_rect(screen, operation_rect, (39, 174, 96, 200), (46, 213, 115), 2)
        else:
            draw_glowing_rect(screen, operation_rect, (192, 57, 43, 200), (231, 76, 60), 2)
        
        operation_text = get_font_func(14).render(current_operation, True, (255, 255, 255))
        operation_text_rect = operation_text.get_rect(center=operation_rect.center)
        screen.blit(operation_text, operation_text_rect)
        
        # Submit button (top right)
        submit_rect = pygame.Rect(screen_width//2 + 330, header_y, 100, 35)
        if submit_rect.collidepoint(MOUSE_POS):
            draw_glowing_rect(screen, submit_rect, (46, 213, 115), (100, 255, 150), 3)
        else:
            draw_glowing_rect(screen, submit_rect, (39, 174, 96), (46, 213, 115), 2)
        
        submit_text = get_font_func(14).render("SUBMIT", True, (255, 255, 255))
        submit_text_rect = submit_text.get_rect(center=submit_rect.center)
        screen.blit(submit_text, submit_text_rect)
        
        # Display/Result box
        display_box = pygame.Rect(screen_width//2 - 440, 240, 880, 200)
        draw_glowing_rect(screen, display_box, (26, 11, 61, 200), (0, 255, 136), 3)
        
        # Display results inside the box
        display_y = 270
        
        # Plaintext display
        plaintext_label = get_font_func(18).render("Plaintext:", True, (255, 200, 0))
        screen.blit(plaintext_label, (screen_width//2 - 420, display_y))
        plaintext_value = get_font_func(16).render(plaintext_input[:40] + ("..." if len(plaintext_input) > 40 else ""), True, (255, 255, 255))
        screen.blit(plaintext_value, (screen_width//2 - 230, display_y + 2))
        
        # Key display
        key_label = get_font_func(18).render("Key:", True, (255, 200, 0))
        screen.blit(key_label, (screen_width//2 - 420, display_y + 50))
        key_value = get_font_func(16).render(str(key_input), True, (255, 255, 255))
        screen.blit(key_value, (screen_width//2 - 230, display_y + 52))
        
        # Result display
        result_label = get_font_func(18).render("Result:", True, (100, 255, 200))
        screen.blit(result_label, (screen_width//2 - 420, display_y + 100))
        result_value = get_font_func(16).render(result_output[:40] + ("..." if len(result_output) > 40 else ""), True, (255, 255, 255))
        screen.blit(result_value, (screen_width//2 - 230, display_y + 102))
        
        # Action buttons
        button_y = 470
        
        # Save Result button
        save_rect = pygame.Rect(screen_width//2 - 400, button_y, 180, 45)
        if save_rect.collidepoint(MOUSE_POS):
            draw_glowing_rect(screen, save_rect, (255, 255, 255), (200, 200, 200), 3)
        else:
            draw_glowing_rect(screen, save_rect, (240, 240, 240 ), (255, 255, 255), 2)
        save_text = get_font_func(14).render("SAVE RESULT", True, (0, 0, 0 ))
        screen.blit(save_text, (screen_width//2 - 385, button_y + 15))
        
        # Continue button
        continue_rect = pygame.Rect(screen_width//2 - 200, button_y, 160, 45)
        if continue_rect.collidepoint(MOUSE_POS):
            draw_glowing_rect(screen, continue_rect, (231, 76, 60), (255, 120, 120), 3)
        else:
            draw_glowing_rect(screen, continue_rect, (192, 57, 43), (231, 76, 60), 2)
        continue_text = get_font_func(14).render("CLEAR", True, (255, 255, 255))
        screen.blit(continue_text, (screen_width//2 - 155, button_y + 15))
        
        # Encrypt Steps button (blue)
        enc_steps_rect = pygame.Rect(screen_width//2 - 20, button_y, 180, 45)
        if enc_steps_rect.collidepoint(MOUSE_POS):
            draw_glowing_rect(screen, enc_steps_rect, (52, 152, 219), (100, 180, 255), 3)
        else:
            draw_glowing_rect(screen, enc_steps_rect, (41, 128, 185), (52, 152, 219), 2)
        enc_steps_text = get_font_func(12).render("ENCRYPT STEPS", True, (255, 255, 255))
        screen.blit(enc_steps_text, (screen_width//2 - 5, button_y + 15))
        
        # Decrypt Steps button (purple)
        dec_steps_rect = pygame.Rect(screen_width//2 + 180, button_y, 180, 45)
        if dec_steps_rect.collidepoint(MOUSE_POS):
            draw_glowing_rect(screen, dec_steps_rect, (155, 89, 182), (200, 150, 255), 3)
        else:
            draw_glowing_rect(screen, dec_steps_rect, (142, 68, 173), (155, 89, 182), 2)
        dec_steps_text = get_font_func(12).render("DECRYPT STEPS", True, (255, 255, 255))
        screen.blit(dec_steps_text, (screen_width//2 + 195, button_y + 15))
        
        # Back button
        back_rect = pygame.Rect(screen_width//2 - 100, button_y + 70, 200, 45)
        if back_rect.collidepoint(MOUSE_POS):
            draw_glowing_rect(screen, back_rect, (200, 200, 200), (255, 100, 100), 3)
        else:
            draw_glowing_rect(screen, back_rect, (100, 100, 100), (150, 150, 150), 2)
        back_text = get_font_func(20).render("BACK", True, (255, 120, 120))
        back_text_rect = back_text.get_rect(center=back_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Instructions at bottom
        instruction_text = get_font_func(12).render("Click on PLAINTEXT or KEY fields above to type. Press ESC to go back.", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(screen_width//2, screen_height - 30))
        screen.blit(instruction_text, instruction_rect)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                    
                # Handle text input for active field
                if active_field == "plaintext":
                    if event.key == pygame.K_BACKSPACE:
                        plaintext_input = plaintext_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_field = None
                    else:
                        plaintext_input += event.unicode
                        
                elif active_field == "key":
                    if event.key == pygame.K_BACKSPACE:
                        key_input = key_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_field = None
                    else:
                        key_input += event.unicode
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check input field clicks
                plaintext_click_area = pygame.Rect(screen_width//2 - 420, header_y, 260, 30)
                key_click_area = pygame.Rect(screen_width//2 - 130, header_y, 220, 30)
                
                if plaintext_click_area.collidepoint(MOUSE_POS):
                    play_click_sound()
                    active_field = "plaintext"
                elif key_click_area.collidepoint(MOUSE_POS):
                    play_click_sound()
                    active_field = "key"
                elif not (submit_rect.collidepoint(MOUSE_POS) or operation_rect.collidepoint(MOUSE_POS) or 
                         save_rect.collidepoint(MOUSE_POS) or continue_rect.collidepoint(MOUSE_POS) or
                         enc_steps_rect.collidepoint(MOUSE_POS) or dec_steps_rect.collidepoint(MOUSE_POS) or
                         back_rect.collidepoint(MOUSE_POS)):
                    active_field = None
                
                # Operation toggle
                if operation_rect.collidepoint(MOUSE_POS):
                    play_click_sound()
                    current_operation = "DECRYPTION" if current_operation == "ENCRYPTION" else "ENCRYPTION"
                
                # Submit button - perform encryption/decryption
                if submit_rect.collidepoint(MOUSE_POS):
                    play_click_sound()
                    if plaintext_input and key_input:
                        try:
                            if current_operation == "ENCRYPTION":
                                result_output = encrypt_func(plaintext_input, key_input)
                                _, solutions_output = encrypt_solution_func(plaintext_input, key_input)
                            else:
                                result_output = decrypt_func(plaintext_input, key_input)
                                _, solutions_output = decrypt_solution_func(plaintext_input, key_input)
                        except Exception as e:
                            result_output = f"Error: {str(e)}"
                            solutions_output = []
                
                # Encrypt Steps button
                if enc_steps_rect.collidepoint(MOUSE_POS):
                    play_click_sound()
                    if plaintext_input and key_input:
                        try:
                            action = show_solution_automation(cipher_name, plaintext_input, key_input, "ENCRYPT")
                            if action == "BACK":
                                return
                            elif action == "RETURN_TO_SAVE":
                                continue
                        except Exception as e:
                            print(f"Error showing encrypt steps: {e}")
                
                # Decrypt Steps button
                if dec_steps_rect.collidepoint(MOUSE_POS):
                    play_click_sound()
                    if result_output and key_input:
                        try:
                            action = show_solution_automation(cipher_name, result_output, key_input, "DECRYPT")
                            if action == "BACK":
                                return
                            elif action == "RETURN_TO_SAVE":
                                continue
                        except Exception as e:
                            print(f"Error showing decrypt steps: {e}")
                
                # Save button
                if save_rect.collidepoint(MOUSE_POS):
                    play_click_sound()
                    if result_output and plaintext_input and key_input:
                        try:
                            cipher_type = cipher_name.replace(" CIPHER", "").title() + " Cipher"
                            cipher_class = "Monoalphabetic" if cipher_name == "ADDITIVE CIPHER" else "Polyalphabetic"
                            save_cipher_result(cipher_type, cipher_class, current_operation, plaintext_input, key_input, result_output)
                            show_save_confirmation()
                        except:
                            pass
                
                # Continue button - clear fields
                if continue_rect.collidepoint(MOUSE_POS):
                    play_click_sound()
                    plaintext_input = ""
                    key_input = ""
                    result_output = ""
                    solutions_output = []
                
                # Back button
                if back_rect.collidepoint(MOUSE_POS):
                    play_click_sound()
                    return
        
        pygame.display.update()
        clock.tick(60)


def show_operation_selection():
    """Show encrypt/decrypt selection for show solution"""
    clock = pygame.time.Clock()
    while True:
        MOUSE_POS = pygame.mouse.get_pos()
        
        SCREEN.fill("black")
        
        TITLE_TEXT = get_font(30).render("SELECT OPERATION", True, "White")
        TITLE_RECT = TITLE_TEXT.get_rect(center=(SCREEN_WIDTH//2, 200))
        SCREEN.blit(TITLE_TEXT, TITLE_RECT)
        
        ENCRYPT_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 300), 
                               text_input="ENCRYPT", font=get_font(40), base_color="Green", hovering_color="White")
        DECRYPT_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 380), 
                               text_input="DECRYPT", font=get_font(40), base_color="Red", hovering_color="White")
        BACK_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 500), 
                            text_input="BACK", font=get_font(40), base_color="Gray", hovering_color="White")
        
        for button in [ENCRYPT_BUTTON, DECRYPT_BUTTON, BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ENCRYPT_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return "ENCRYPT"
                elif DECRYPT_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return "DECRYPT"
                elif BACK_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return "BACK"
        
        pygame.display.update()
        clock.tick(60)

def additive_cipher_screen():
    enhanced_cipher_operation_menu(
        "ADDITIVE CIPHER", 
        lambda text, key: additive_encrypt_decrypt(text, 'e', key),
        lambda text, key: additive_encrypt_decrypt(text, 'd', key),
        lambda text, key: additive_encrypt_decrypt_with_solution(text, 'e', key),
        lambda text, key: additive_encrypt_decrypt_with_solution(text, 'd', key),
        SCREEN,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        get_font,
        Button,
        None
    )

def autokey_cipher_screen():
    enhanced_cipher_operation_menu(
        "AUTO-KEY CIPHER",
        autokey_encrypt,
        autokey_decrypt,
        autokey_encrypt_with_solution,
        autokey_decrypt_with_solution,
        SCREEN,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        get_font,
        Button,
        None
    )

def vigenere_cipher_screen():
    enhanced_cipher_operation_menu(
        "VIGENÈRE CIPHER",
        vigenere_encrypt,
        vigenere_decrypt,
        vigenere_encrypt_with_solution,
        vigenere_decrypt_with_solution,
        SCREEN,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        get_font,
        Button,
        None
    )

def cipher_game_screen():
    """Launch the Cipher Game"""
    game = CipherGame(main_screen=SCREEN)
    game.run()

def about_screen():
    """Information about the cipher methods"""
    clock = pygame.time.Clock()
    while True:
        MOUSE_POS = pygame.mouse.get_pos()
        
        SCREEN.fill("black")
        
        TITLE_TEXT = get_font(35).render("ABOUT CIPHERS", True, "White")
        TITLE_RECT = TITLE_TEXT.get_rect(center=(SCREEN_WIDTH//2, 80))
        SCREEN.blit(TITLE_TEXT, TITLE_RECT)
        
        info_lines = [
            "ADDITIVE CIPHER: Shifts each letter by a fixed number (Monoalphabetic)",
            "AUTO-KEY CIPHER: Uses the message itself as part of the key (Polyalphabetic)",
            "VIGENÈRE CIPHER: Uses a repeating keyword to encrypt (Polyalphabetic)",
            "",
            "All ciphers work with alphabetic characters only.",
            "Numbers and symbols are preserved unchanged.",
            "",
            "FEATURES:",
            "• Use 'SHOW SOLUTION' to see step-by-step process!",
            "• Save your cipher results for future reference!",
            "• View all saved results in CIPHER HISTORY!",
            "• Play the interactive CIPHER GAME!",
            "• Quick automation buttons for seamless operations!"
        ]
        
        for i, line in enumerate(info_lines):
            if "FEATURES:" in line:
                color = "Orange"
            elif line.startswith("•"):
                color = "Cyan"
            elif "Monoalphabetic" in line or "Polyalphabetic" in line:
                color = "Yellow"
            else:
                color = "White"
            
            text_surface = get_font(18).render(line, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 140 + i * 25))
            SCREEN.blit(text_surface, text_rect)
        
        BACK_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 500), 
                            text_input="BACK", font=get_font(50), base_color="White", hovering_color="Red")
        
        BACK_BUTTON.changeColor(MOUSE_POS)
        BACK_BUTTON.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    play_click_sound()
                    return
        
        pygame.display.update()
        clock.tick(60)

def options():
    clock = pygame.time.Clock()
    
    # Load and scale the background image
    try:
        background_image = pygame.image.load("assets/cipher_bg.jpg")
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        background_image = None
        print("Options background image not found, using fallback color")
    
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        # Use background image instead of white fill
        if background_image:
            SCREEN.blit(background_image, (0, 0))
        else:
            SCREEN.fill("white")

        OPTIONS_TEXT = get_font(30).render("SELECT A CIPHER TYPE", True, "Blue")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(SCREEN_WIDTH//2, 100))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        # Centered buttons with proper spacing
        ADDITIVE_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 180), 
                        text_input="ADDITIVE CIPHER (MONOALPHABETIC)", font=get_font(30), base_color="White", hovering_color="Blue")
        AUTOKEY_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 240), 
                                text_input="AUTO-KEY CIPHER (POLYALPHABETIC)", font=get_font(30), base_color="White", hovering_color="Blue")
        VIGENERE_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 300), 
                                text_input="VIGENÈRE CIPHER (POLYALPHABETIC)", font=get_font(30), base_color="White", hovering_color="Blue")
        ABOUT_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 380), 
                                text_input="ABOUT CIPHER", font=get_font(35), base_color="Yellow", hovering_color="Orange")
        HISTORY_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 450), 
                                text_input="CIPHER HISTORY", font=get_font(35), base_color="Yellow", hovering_color="Orange")
        BACK_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 520), 
                                text_input="BACK", font=get_font(50), base_color="White", hovering_color="Red")
        
        buttons = [ADDITIVE_BUTTON, AUTOKEY_BUTTON, VIGENERE_BUTTON, ABOUT_BUTTON, HISTORY_BUTTON, BACK_BUTTON]
        
        for button in buttons:
            button.changeColor(OPTIONS_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ADDITIVE_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    play_click_sound()
                    additive_cipher_screen()
                elif AUTOKEY_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    play_click_sound()
                    autokey_cipher_screen()
                elif VIGENERE_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    play_click_sound()
                    vigenere_cipher_screen()
                elif ABOUT_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    play_click_sound()
                    about_screen()
                elif HISTORY_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    play_click_sound()
                    show_cipher_history()
                elif BACK_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    play_click_sound()
                    return

        pygame.display.update()
        clock.tick(60)

def main_menu():
    clock = pygame.time.Clock()
    
    # Load and scale the background image
    try:
        background_image = pygame.image.load("assets/main_bg.jpg")
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        background_image = None
        print("Background image not found, using fallback color")
    
    while True:
        # Use background image instead of fill color
        if background_image:
            SCREEN.blit(background_image, (0, 0))
        else:
            SCREEN.fill(BG_COLOR)

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(50).render("WELCOME TO", True, "#b68f40")
        MENU_TEXT2 = get_font(50).render("CIPHER WORLD", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH//2, 150))
        MENU_RECT2 = MENU_TEXT2.get_rect(center=(SCREEN_WIDTH//2, 200))

        # Centered buttons with proper spacing
        CIPHERS_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 300), 
                            text_input="CIPHER GAME", font=get_font(60), base_color="#ffee00ff", hovering_color="White")
        ABOUT_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 400), 
                            text_input="LEARN CIPHER", font=get_font(60), base_color="#ffee00ff", hovering_color="White")
        QUIT_BUTTON = Button(image=None, pos=(SCREEN_WIDTH//2, 500), 
                            text_input="QUIT", font=get_font(60), base_color="#ffee00ff", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)
        SCREEN.blit(MENU_TEXT2, MENU_RECT2)

        for button in [CIPHERS_BUTTON, ABOUT_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CIPHERS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_click_sound()
                    cipher_game_screen()
                if ABOUT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_click_sound()
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_click_sound()
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)

def filter_history(search_term, operation_filter):
    """Filter cipher history based on search term and operation"""
    filtered_history = []
    for entry in cipher_history:
        # Text search
        if search_term.lower() in entry['plaintext'].lower() or \
           search_term.lower() in entry['cipher_type'].lower() or \
           search_term.lower() in entry['result'].lower() or \
           search_term == "":
            # Operation filter
            if operation_filter == "ALL" or entry['operation'] == operation_filter:
                filtered_history.append(entry)
    return filtered_history

def delete_entry_confirmation(entry_index, entry_data):
    """Show confirmation dialog for deleting an entry"""
    clock = pygame.time.Clock()
    
    while True:
        SCREEN.fill("black")
        
        # Confirmation title
        title_text = get_font(24).render("CONFIRM DELETE", True, "Red")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        SCREEN.blit(title_text, title_rect)
        
        # Entry preview
        preview_text = [
            f"Entry #{entry_index + 1}",
            f"Date: {entry_data['timestamp']}",
            f"Cipher: {entry_data['cipher_type']}",
            f"Operation: {entry_data['operation']}",
            f"Text: {entry_data['plaintext'][:40]}{'...' if len(entry_data['plaintext']) > 40 else ''}"
        ]
        
        y_pos = 200
        for text in preview_text:
            surface = get_font(14).render(text, True, "Yellow")
            rect = surface.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            SCREEN.blit(surface, rect)
            y_pos += 25
        
        warning_text = get_font(16).render("This action cannot be undone!", True, "Red")
        warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, y_pos + 20))
        SCREEN.blit(warning_text, warning_rect)
        
        # Buttons
        confirm_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, y_pos + 60, 120, 40)
        cancel_btn = pygame.Rect(SCREEN_WIDTH//2 + 30, y_pos + 60, 120, 40)
        
        pygame.draw.rect(SCREEN, "DarkRed", confirm_btn)
        pygame.draw.rect(SCREEN, "DarkGreen", cancel_btn)
        pygame.draw.rect(SCREEN, "Red", confirm_btn, 2)
        pygame.draw.rect(SCREEN, "Green", cancel_btn, 2)
        
        confirm_text = get_font(16).render("DELETE", True, "White")
        cancel_text = get_font(16).render("CANCEL", True, "White")
        
        confirm_rect = confirm_text.get_rect(center=confirm_btn.center)
        cancel_rect = cancel_text.get_rect(center=cancel_btn.center)
        
        SCREEN.blit(confirm_text, confirm_rect)
        SCREEN.blit(cancel_text, cancel_rect)
        
        # Instructions
        inst_text = get_font(14).render("Click DELETE to confirm, CANCEL to abort, or ESC to cancel", True, "Orange")
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        SCREEN.blit(inst_text, inst_rect)
        
        pygame.display.update()
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if confirm_btn.collidepoint(event.pos):
                    play_click_sound()
                    return True
                elif cancel_btn.collidepoint(event.pos):
                    play_click_sound()
                    return False

def show_cipher_history():
    """Display all saved cipher results with search and filter capabilities"""
    if not cipher_history:
        show_no_history()
        return
    
    clock = pygame.time.Clock()
    scroll_offset = 0
    max_scroll = 0
    search_text = ""
    search_active = False
    operation_filter = "ALL"
    delete_mode = False
    
    while True:
        SCREEN.fill("black")
        
        # Filter history based on search and operation
        filtered_history = filter_history(search_text, operation_filter)
        
        # Title with delete mode indicator
        title_color = "Red" if delete_mode else "Green"
        title_prefix = "DELETE MODE - " if delete_mode else ""
        title_text = get_font(30).render(f"{title_prefix}CIPHER HISTORY", True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        SCREEN.blit(title_text, title_rect)
        
        # Search bar (only show if more than 10 entries)
        if len(cipher_history) >= 10:
            search_label = get_font(16).render("Search:", True, "Yellow")
            SCREEN.blit(search_label, (50, 70))
            
            # Search input box
            search_box = pygame.Rect(120, 70, 300, 25)
            search_color = "Yellow" if search_active else "White"
            pygame.draw.rect(SCREEN, "Black", search_box)
            pygame.draw.rect(SCREEN, search_color, search_box, 2)
            
            search_surface = get_font(16).render(search_text + ("_" if search_active else ""), True, "White")
            SCREEN.blit(search_surface, (search_box.x + 5, search_box.y + 3))
            
            # Filter buttons
            filter_label = get_font(16).render("Filter:", True, "Yellow")
            SCREEN.blit(filter_label, (450, 70))
            
            # Filter operation buttons
            all_btn = pygame.Rect(510, 70, 60, 25)
            enc_btn = pygame.Rect(580, 70, 80, 25)
            dec_btn = pygame.Rect(670, 70, 80, 25)
            
            all_color = "Green" if operation_filter == "ALL" else "Gray"
            enc_color = "Green" if operation_filter == "Encryption" else "Gray"
            dec_color = "Green" if operation_filter == "Decryption" else "Gray"
            
            pygame.draw.rect(SCREEN, all_color, all_btn)
            pygame.draw.rect(SCREEN, enc_color, enc_btn)
            pygame.draw.rect(SCREEN, dec_color, dec_btn)
            
            all_text = get_font(12).render("ALL", True, "White")
            enc_text = get_font(12).render("ENCRYPT", True, "White")
            dec_text = get_font(12).render("DECRYPT", True, "White")
            
            SCREEN.blit(all_text, (all_btn.x + 18, all_btn.y + 6))
            SCREEN.blit(enc_text, (enc_btn.x + 15, enc_btn.y + 6))
            SCREEN.blit(dec_text, (dec_btn.x + 15, dec_btn.y + 6))
            
            start_y = 120
        else:
            start_y = 80
        
        # Results count and delete mode toggle
        count_text = get_font(16).render(f"Results: {len(filtered_history)}/{len(cipher_history)}", True, "Cyan")
        count_rect = count_text.get_rect(center=(SCREEN_WIDTH//2 - 100, start_y))
        SCREEN.blit(count_text, count_rect)
        
        # Delete mode toggle button
        delete_btn = pygame.Rect(SCREEN_WIDTH//2 + 50, start_y - 10, 150, 20)
        delete_btn_color = "Red" if delete_mode else "Orange"
        delete_btn_text = "EXIT DELETE" if delete_mode else "DELETE MODE"
        
        pygame.draw.rect(SCREEN, delete_btn_color, delete_btn)
        pygame.draw.rect(SCREEN, "White", delete_btn, 1)
        
        delete_text = get_font(12).render(delete_btn_text, True, "White")
        delete_text_rect = delete_text.get_rect(center=delete_btn.center)
        SCREEN.blit(delete_text, delete_text_rect)
        
        # Calculate scrolling for filtered results
        line_height = 25
        entries_per_item = 8
        total_lines = len(filtered_history) * entries_per_item
        total_height = total_lines * line_height
        screen_height = SCREEN_HEIGHT - start_y - 100
        max_scroll = max(0, total_height - screen_height)
        
        current_y = start_y + 40 - scroll_offset
        entry_buttons = []
        
        # Display each history entry
        for i, entry in enumerate(filtered_history):
            if current_y > SCREEN_HEIGHT:
                break
            if current_y < start_y - 200:
                current_y += entries_per_item * line_height
                continue
            
            original_index = cipher_history.index(entry)
            
            # Entry separator with operation color coding
            operation_color = "Green" if entry['operation'] == "Encryption" else "Orange"
            separator_text = f"--- Entry {original_index + 1} ({entry['operation']}) ---"
            
            # Add delete button in delete mode
            if delete_mode:
                delete_entry_btn = pygame.Rect(50, current_y - 10, 60, 20)
                pygame.draw.rect(SCREEN, "DarkRed", delete_entry_btn)
                pygame.draw.rect(SCREEN, "Red", delete_entry_btn, 1)
                
                del_text = get_font(10).render("DELETE", True, "White")
                del_text_rect = del_text.get_rect(center=delete_entry_btn.center)
                SCREEN.blit(del_text, del_text_rect)
                
                entry_buttons.append((delete_entry_btn, original_index, entry))
            
            separator = get_font(16).render(separator_text, True, operation_color)
            separator_rect = separator.get_rect(center=(SCREEN_WIDTH//2, current_y))
            SCREEN.blit(separator, separator_rect)
            current_y += line_height
            
            # Entry details
            details = [
                f"Date: {entry['timestamp']}",
                f"Cipher: {entry['cipher_type']} ({entry['cipher_class']})",
                f"Plaintext: {entry['plaintext'][:60]}{'...' if len(entry['plaintext']) > 60 else ''}",
                f"Key: {entry['key']}",
                f"Result: {entry['result'][:60]}{'...' if len(entry['result']) > 60 else ''}",
                ""  # Empty line between entries
            ]
            
            for detail in details:
                if detail and current_y < SCREEN_HEIGHT and current_y > start_y - 50:
                    color = "Orange" if detail.startswith(("Date:", "Cipher:")) else "White"
                    detail_surface = get_font(12).render(detail, True, color)
                    detail_rect = detail_surface.get_rect(center=(SCREEN_WIDTH//2, current_y))
                    SCREEN.blit(detail_surface, detail_rect)
                current_y += line_height
        
        # Scrolling instructions and back button
        if len(cipher_history) >= 10:
            if max_scroll > 0:
                if delete_mode:
                    nav_text = get_font(14).render("UP/DOWN: scroll | Click DELETE buttons to remove entries | ESC: back", True, "Orange")
                else:
                    nav_text = get_font(14).render("UP/DOWN: scroll | Click search box to search | D: delete mode | ESC: back", True, "Orange")
            else:
                if delete_mode:
                    nav_text = get_font(14).render("Click DELETE buttons to remove entries | ESC: back", True, "Orange")
                else:
                    nav_text = get_font(14).render("Click search box to search | D: delete mode | ESC: back", True, "Orange")
        else:
            if delete_mode:
                nav_text = get_font(14).render("Click DELETE buttons to remove entries | D: exit delete mode | ESC: back", True, "Orange")
            else:
                nav_text = get_font(14).render("D: delete mode | ESC: back to main menu", True, "Orange")
        
        nav_rect = nav_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        SCREEN.blit(nav_text, nav_rect)
        
        pygame.display.update()
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_UP and max_scroll > 0:
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.key == pygame.K_DOWN and max_scroll > 0:
                    scroll_offset = min(max_scroll, scroll_offset + 30)
                elif event.key == pygame.K_d:  # Toggle delete mode
                    delete_mode = not delete_mode
                    search_active = False  # Deactivate search when toggling
                elif search_active:
                    if event.key == pygame.K_BACKSPACE:
                        search_text = search_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        search_active = False
                    else:
                        search_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if len(cipher_history) >= 10:
                    # Check if clicked on search box (only if not in delete mode)
                    if not delete_mode and search_box.collidepoint(event.pos):
                        play_click_sound()
                        search_active = True
                    else:
                        search_active = False
                    
                    # Check filter buttons
                    if all_btn.collidepoint(event.pos):
                        play_click_sound()
                        operation_filter = "ALL"
                    elif enc_btn.collidepoint(event.pos):
                        play_click_sound()
                        operation_filter = "Encryption"
                    elif dec_btn.collidepoint(event.pos):
                        play_click_sound()
                        operation_filter = "Decryption"
                
                # Check delete mode toggle button
                if delete_btn.collidepoint(event.pos):
                    play_click_sound()
                    delete_mode = not delete_mode
                    search_active = False
                
                # Check delete entry buttons
                if delete_mode:
                    for btn_rect, entry_index, entry_data in entry_buttons:
                        if btn_rect.collidepoint(event.pos):
                            if delete_entry_confirmation(entry_index, entry_data):
                                cipher_history.pop(entry_index)
                                # Save updated history to file
                                try:
                                    with open("cipher_history.json", "w") as f:
                                        json.dump(cipher_history, f, indent=2)
                                except:
                                    pass
                                # Reset scroll if needed
                                if not cipher_history:
                                    return
                                # Adjust scroll offset if necessary
                                new_max_scroll = max(0, (len(filter_history(search_text, operation_filter)) * entries_per_item * line_height) - screen_height)
                                scroll_offset = min(scroll_offset, new_max_scroll)
                            break

def show_no_history():
    """Display message when no history is available"""
    clock = pygame.time.Clock()
    while True:
        SCREEN.fill("black")
        
        no_history_text = get_font(25).render("No cipher history found!", True, "Red")
        no_history_rect = no_history_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        SCREEN.blit(no_history_text, no_history_rect)
        
        instruction_text = get_font(20).render("Use ciphers and save results to build history", True, "Yellow")
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        SCREEN.blit(instruction_text, instruction_rect)
        
        continue_text = get_font(20).render("Press any key to go back", True, "White")
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        SCREEN.blit(continue_text, continue_rect)
        
        pygame.display.update()
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

# Enhanced Additive Cipher Functions with solution tracking
def additive_encrypt_decrypt_with_solution(text, mode, key):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    result = ''
    solution_steps = []
    
    # Convert key to number if it's a letter
    if isinstance(key, str) and len(key) == 1 and key.isalpha():
        key = letters.find(key.lower())
        if key == -1:  # Letter not found
            key = 0
    else:
        key = int(key)  # Ensure key is an integer
    
    solution_steps.append(f"Key: {key}")
    solution_steps.append(f"Mode: {'Encryption' if mode == 'e' else 'Decryption'}")
    solution_steps.append(f"{'Encryption' if mode == 'e' else 'Decryption'} Process:")
    
    actual_key = key if mode == 'e' else -key
    
    for i, letter in enumerate(text):
        original_letter = letter
        letter = letter.lower()
        
        if letter in letters:
            index = letters.find(letter)
            new_index_raw = index + actual_key
            new_index = new_index_raw % len(letters)
            new_letter = letters[new_index]
            result += new_letter
            
            # Create step explanation
            if mode == 'e':
                if new_index_raw >= 26:
                    step = f"{original_letter.upper()} ({index}) + {key} = {new_index_raw} = ({new_index_raw}-26) = {new_index} -> {new_letter.upper()}"
                else:
                    step = f"{original_letter.upper()} ({index}) + {key} = {new_index} -> {new_letter.upper()}"
            else:
                if new_index_raw < 0:
                    step = f"{original_letter.upper()} ({index}) - {key} = {new_index_raw} = ({new_index_raw}+26) = {new_index} -> {new_letter.upper()}"
                else:
                    step = f"{original_letter.upper()} ({index}) - {key} = {new_index} -> {new_letter.upper()}"
            
            solution_steps.append(step)
        else:
            result += letter
            solution_steps.append(f"{original_letter} (non-alphabetic) -> {original_letter}")
    
    return result, solution_steps

def additive_encrypt_decrypt(text, mode, key):
    result, _ = additive_encrypt_decrypt_with_solution(text, mode, key)
    return result

# Enhanced Auto-Key Cipher Functions with solution tracking
def generate_autokey(plaintext, key):
    """Generate autokey by prepending the numeric key and using plaintext values"""
    # Convert key to numeric if it's a string
    if isinstance(key, str):
        try:
            key_val = int(key)
        except ValueError:
            key_val = ord(key.upper()) - ord('A')
    else:
        key_val = key
    
    # Start with the initial key value
    extended_key = [key_val]
    
    # Add plaintext character values (excluding the last one)
    plaintext = plaintext.upper().replace(' ', '')
    for i in range(len(plaintext) - 1):
        if plaintext[i].isalpha():
            extended_key.append(ord(plaintext[i]) - ord('A'))
    
    return extended_key

def autokey_encrypt_with_solution(plaintext, key):
    plaintext = plaintext.upper().replace(' ', '')
    extended_key = generate_autokey(plaintext, key)
    ciphertext = ''
    solution_steps = []
    
    solution_steps.append(f"Original Key: {key}")
    solution_steps.append(f"Plaintext Values: {[ord(c) - ord('A') for c in plaintext if c.isalpha()]}")
    solution_steps.append(f"Extended Key: {extended_key}")
    solution_steps.append("Encryption Process:")
    
    for i, p in enumerate(plaintext):
        if p.isalpha():
            p_val = ord(p) - ord('A')
            k_val = extended_key[i]
            c_val = (p_val + k_val) % 26
            c = chr(c_val + ord('A'))
            ciphertext += c
            
            step = f"{p} ({p_val}) + {k_val} = {c_val} -> {c}"
            solution_steps.append(step)
        else:
            ciphertext += p
            solution_steps.append(f"{p} (non-alphabetic) -> {p}")
    
    return ciphertext, solution_steps

def autokey_decrypt_with_solution(ciphertext, key):
    ciphertext = ciphertext.upper().replace(' ', '')
    
    # Convert key to numeric if it's a string
    if isinstance(key, str):
        try:
            key_val = int(key)
        except ValueError:
            key_val = ord(key.upper()) - ord('A')
    else:
        key_val = key
    
    plaintext = ''
    solution_steps = []
    
    solution_steps.append(f"Original Key: {key}")
    solution_steps.append("Decryption Process:")
    
    for i, c in enumerate(ciphertext):
        if c.isalpha():
            c_val = ord(c) - ord('A')
            
            # First character uses the initial key
            if i == 0:
                k_val = key_val
            else:
                # Use the previous plaintext character
                k_val = ord(plaintext[i-1]) - ord('A')
            
            p_val = (c_val - k_val) % 26
            p = chr(p_val + ord('A'))
            plaintext += p
            
            step = f"{c} ({c_val}) - {k_val} = {p_val} -> {p}"
            solution_steps.append(step)
        else:
            plaintext += c
            solution_steps.append(f"{c} (non-alphabetic) -> {c}")
    
    return plaintext, solution_steps

def autokey_encrypt(plaintext, key):
    result, _ = autokey_encrypt_with_solution(plaintext, key)
    return result

def autokey_decrypt(ciphertext, key):
    result, _ = autokey_decrypt_with_solution(ciphertext, key)
    return result

# Enhanced Vigenere Cipher Functions with solution tracking
def vigenere_encrypt_with_solution(message, key):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    letter_to_index = dict(zip(letters, range(len(letters))))
    index_to_letter = dict(zip(range(len(letters)), letters))
    
    encrypted = ''
    message = message.lower()
    solution_steps = []
    
    # Parse key - handle both numeric and letter keys
    if isinstance(key, str) and ',' in key:
        try:
            key_values = [int(k.strip()) for k in key.split(',') if k.strip() != '']
        except ValueError:
            return "Error: Invalid numeric key format", ["Error: Key must contain valid numbers separated by commas"]
    elif isinstance(key, list):
        key_values = key
    else:
        key = key.lower()
        key_values = [letter_to_index[k] for k in key if k in letters]
    
    # Validate key
    if not key_values or len(key_values) == 0:
        return "Error: Empty or invalid key", ["Error: Please provide a valid key (either letters or numbers like '0, 5, 8')"]
    
    # Create extended key
    extended_key = []
    key_index = 0
    for letter in message:
        if letter in letters:
            extended_key.append(key_values[key_index % len(key_values)])
            key_index += 1
        else:
            extended_key.append(None)
    
    solution_steps.append(f"Original Key: {key_values}")
    solution_steps.append(f"Extended Key: {[k if k is not None else '_' for k in extended_key]}")
    solution_steps.append("Encryption Process:")
    
    key_index = 0
    for i, letter in enumerate(message):
        if letter in letters:
            key_val = key_values[key_index % len(key_values)]
            letter_val = letter_to_index[letter]
            encrypted_val = (letter_val + key_val) % len(letters)
            encrypted_letter = index_to_letter[encrypted_val]
            encrypted += encrypted_letter
            
            step = f"{letter.upper()} ({letter_val}) + {key_val} = {encrypted_val} -> {encrypted_letter.upper()}"
            solution_steps.append(step)
            key_index += 1
        else:
            encrypted += letter
            solution_steps.append(f"{letter} (non-alphabetic) -> {letter}")
    
    return encrypted, solution_steps

def vigenere_decrypt_with_solution(cipher, key):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    letter_to_index = dict(zip(letters, range(len(letters))))
    index_to_letter = dict(zip(range(len(letters)), letters))
    
    decrypted = ''
    cipher = cipher.lower()
    solution_steps = []
    
    # Parse key - handle both numeric and letter keys
    if isinstance(key, str) and ',' in key:
        try:
            key_values = [int(k.strip()) for k in key.split(',') if k.strip() != '']
        except ValueError:
            return "Error: Invalid numeric key format", ["Error: Key must contain valid numbers separated by commas"]
    elif isinstance(key, list):
        key_values = key
    else:
        key = key.lower()
        key_values = [letter_to_index[k] for k in key if k in letters]
    
    # Validate key
    if not key_values or len(key_values) == 0:
        return "Error: Empty or invalid key", ["Error: Please provide a valid key (either letters or numbers like '0, 5, 8')"]
    
    # Create extended key
    extended_key = []
    key_index = 0
    for letter in cipher:
        if letter in letters:
            extended_key.append(key_values[key_index % len(key_values)])
            key_index += 1
        else:
            extended_key.append(None)
    
    solution_steps.append(f"Original Key: {key_values}")
    solution_steps.append(f"Extended Key: {[k if k is not None else '_' for k in extended_key]}")
    solution_steps.append("Decryption Process:")
    
    key_index = 0
    for letter in cipher:
        if letter in letters:
            key_val = key_values[key_index % len(key_values)]
            cipher_val = letter_to_index[letter]
            decrypted_val = (cipher_val - key_val) % len(letters)
            decrypted_letter = index_to_letter[decrypted_val]
            decrypted += decrypted_letter
            
            step = f"{letter.upper()} ({cipher_val}) - {key_val} = {decrypted_val} -> {decrypted_letter.upper()}"
            solution_steps.append(step)
            key_index += 1
        else:
            decrypted += letter
            solution_steps.append(f"{letter} (non-alphabetic) -> {letter}")
    
    return decrypted, solution_steps

def vigenere_encrypt(message, key):
    result, _ = vigenere_encrypt_with_solution(message, key)
    return result

def vigenere_decrypt(cipher, key):
    result, _ = vigenere_decrypt_with_solution(cipher, key)
    return result


if __name__ == "__main__":
    # Load existing cipher history on startup
    load_cipher_history()
    main_menu()