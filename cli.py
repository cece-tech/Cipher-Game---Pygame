import sys
import os
import json
from datetime import datetime

# Global list to store cipher history
cipher_history = []

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"{title:^60}")
    print("=" * 60)

def print_divider():
    """Print a divider line"""
    print("-" * 60)

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
        print("✓ Result saved successfully!")
    except Exception as e:
        print(f"✗ Error saving: {e}")

def load_cipher_history():
    """Load cipher history from file"""
    global cipher_history
    try:
        if os.path.exists("cipher_history.json"):
            with open("cipher_history.json", "r") as f:
                cipher_history = json.load(f)
                print(f"✓ Loaded {len(cipher_history)} entries from history.")
    except Exception as e:
        print(f"⚠ Could not load history: {e}")
        cipher_history = []

# Enhanced Additive Cipher Functions with solution tracking
def additive_encrypt_decrypt_with_solution(text, mode, key):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    result = ''
    solution_steps = []
    
    # Convert key to number if it's a letter
    if isinstance(key, str) and len(key) == 1 and key.isalpha():
        key = letters.find(key.lower())
        if key == -1:
            key = 0
    else:
        key = int(key)
    
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
    if isinstance(key, str):
        try:
            key_val = int(key)
        except ValueError:
            key_val = ord(key.upper()) - ord('A')
    else:
        key_val = key
    
    extended_key = [key_val]
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
            
            if i == 0:
                k_val = key_val
            else:
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
    
    # Parse key
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
    
    if not key_values or len(key_values) == 0:
        return "Error: Empty or invalid key", ["Error: Please provide a valid key"]
    
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
    
    # Parse key
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
    
    if not key_values or len(key_values) == 0:
        return "Error: Empty or invalid key", ["Error: Please provide a valid key"]
    
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

# CLI Command Handler
def handle_command(command):
    """Process user commands"""
    parts = command.strip().split(maxsplit=1)
    if not parts:
        return
    
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Help command
    if cmd in ['help', 'h', '?']:
        print_header("AVAILABLE COMMANDS")
        print("\nCIPHER OPERATIONS:")
        print("  additive encrypt <text> --key <key>     - Encrypt using Additive cipher")
        print("  additive decrypt <text> --key <key>     - Decrypt using Additive cipher")
        print("  autokey encrypt <text> --key <key>      - Encrypt using Auto-Key cipher")
        print("  autokey decrypt <text> --key <key>      - Decrypt using Auto-Key cipher")
        print("  vigenere encrypt <text> --key <key>     - Encrypt using Vigenère cipher")
        print("  vigenere decrypt <text> --key <key>     - Decrypt using Vigenère cipher")
        print("\nWITH SOLUTION STEPS:")
        print("  additive encrypt <text> --key <key> --steps")
        print("\nHISTORY:")
        print("  history                  - View all saved results")
        print("  save                     - Save the last result")
        print("\nGENERAL:")
        print("  help, h, ?               - Show this help")
        print("  exit, quit, q            - Exit program")
        print_divider()
    
    # Exit
    elif cmd in ['exit', 'quit', 'q']:
        print("\n✓ Thank you for using Cipher World CLI!")
        print("Goodbye!\n")
        sys.exit(0)
    
    # History commands
    elif cmd == 'history':
        if not cipher_history:
            print("\n⚠ No cipher history found!")
        else:
            print_header(f"CIPHER HISTORY ({len(cipher_history)} entries)")
            for i, entry in enumerate(cipher_history, 1):
                print(f"\n[{i}] {entry['timestamp']}")
                print(f"    Cipher: {entry['cipher_type']} ({entry['cipher_class']})")
                print(f"    Operation: {entry['operation']}")
                print(f"    Plaintext: {entry['plaintext'][:40]}{'...' if len(entry['plaintext']) > 40 else ''}")
                print(f"    Key: {entry['key']}")
                print(f"    Result: {entry['result'][:40]}{'...' if len(entry['result']) > 40 else ''}")
            print_divider()
    
    # Cipher operations
    elif cmd in ['additive', 'autokey', 'vigenere']:
        if not args:
            print(f"✗ Usage: {cmd} encrypt/decrypt <text> --key <key> [--steps]")
            return
        
        # Parse operation and arguments
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print(f"✗ Usage: {cmd} encrypt/decrypt <text> --key <key> [--steps]")
            return
        
        operation = parts[0].lower()
        rest = parts[1]
        
        # Check for --steps flag
        show_steps = '--steps' in rest
        rest = rest.replace('--steps', '')
        
        # Parse text and key
        if '--key' not in rest:
            print("✗ Missing --key parameter")
            return
        
        text_and_key = rest.split('--key')
        text = text_and_key[0].strip()
        key = text_and_key[1].strip() if len(text_and_key) > 1 else ""
        
        if not text or not key:
            print("✗ Both text and key are required")
            return
        
        try:
            # Store last operation for save command
            global last_result
            
            if cmd == 'additive':
                if operation == 'encrypt':
                    if show_steps:
                        result, steps = additive_encrypt_decrypt_with_solution(text, 'e', key)
                        print(f"\n✓ Encrypted: {result}")
                        print_header("STEP-BY-STEP SOLUTION")
                        for i, step in enumerate(steps, 1):
                            print(f"{i}. {step}")
                        print_divider()
                    else:
                        result = additive_encrypt_decrypt(text, 'e', key)
                        print(f"\n✓ Encrypted: {result}")
                    last_result = ('Additive Cipher', 'Monoalphabetic', 'Encryption', text, key, result)
                elif operation == 'decrypt':
                    if show_steps:
                        result, steps = additive_encrypt_decrypt_with_solution(text, 'd', key)
                        print(f"\n✓ Decrypted: {result}")
                        print_header("STEP-BY-STEP SOLUTION")
                        for i, step in enumerate(steps, 1):
                            print(f"{i}. {step}")
                        print_divider()
                    else:
                        result = additive_encrypt_decrypt(text, 'd', key)
                        print(f"\n✓ Decrypted: {result}")
                    last_result = ('Additive Cipher', 'Monoalphabetic', 'Decryption', text, key, result)
                else:
                    print("✗ Operation must be 'encrypt' or 'decrypt'")
                    return
            
            elif cmd == 'autokey':
                if operation == 'encrypt':
                    if show_steps:
                        result, steps = autokey_encrypt_with_solution(text, key)
                        print(f"\n✓ Encrypted: {result}")
                        print_header("STEP-BY-STEP SOLUTION")
                        for i, step in enumerate(steps, 1):
                            print(f"{i}. {step}")
                        print_divider()
                    else:
                        result = autokey_encrypt(text, key)
                        print(f"\n✓ Encrypted: {result}")
                    last_result = ('Auto-Key Cipher', 'Polyalphabetic', 'Encryption', text, key, result)
                elif operation == 'decrypt':
                    if show_steps:
                        result, steps = autokey_decrypt_with_solution(text, key)
                        print(f"\n✓ Decrypted: {result}")
                        print_header("STEP-BY-STEP SOLUTION")
                        for i, step in enumerate(steps, 1):
                            print(f"{i}. {step}")
                        print_divider()
                    else:
                        result = autokey_decrypt(text, key)
                        print(f"\n✓ Decrypted: {result}")
                    last_result = ('Auto-Key Cipher', 'Polyalphabetic', 'Decryption', text, key, result)
                else:
                    print("✗ Operation must be 'encrypt' or 'decrypt'")
                    return
            
            elif cmd == 'vigenere':
                if operation == 'encrypt':
                    if show_steps:
                        result, steps = vigenere_encrypt_with_solution(text, key)
                        print(f"\n✓ Encrypted: {result}")
                        print_header("STEP-BY-STEP SOLUTION")
                        for i, step in enumerate(steps, 1):
                            print(f"{i}. {step}")
                        print_divider()
                    else:
                        result = vigenere_encrypt(text, key)
                        print(f"\n✓ Encrypted: {result}")
                    last_result = ('Vigenère Cipher', 'Polyalphabetic', 'Encryption', text, key, result)
                elif operation == 'decrypt':
                    if show_steps:
                        result, steps = vigenere_decrypt_with_solution(text, key)
                        print(f"\n✓ Decrypted: {result}")
                        print_header("STEP-BY-STEP SOLUTION")
                        for i, step in enumerate(steps, 1):
                            print(f"{i}. {step}")
                        print_divider()
                    else:
                        result = vigenere_decrypt(text, key)
                        print(f"\n✓ Decrypted: {result}")
                    last_result = ('Vigenère Cipher', 'Polyalphabetic', 'Decryption', text, key, result)
                else:
                    print("✗ Operation must be 'encrypt' or 'decrypt'")
                    return
            
            print("(Type 'save' to save this result to history)")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Save last result
    elif cmd == 'save':
        try:
            if 'last_result' in globals():
                cipher_type, cipher_class, operation, plaintext, key, result = last_result
                save_cipher_result(cipher_type, cipher_class, operation, plaintext, key, result)
            else:
                print("⚠ No result to save. Perform a cipher operation first.")
        except Exception as e:
            print(f"✗ Error saving: {e}")
    
    else:
        print(f"✗ Unknown command: '{cmd}'. Type 'help' for available commands.")

# Main program
def main():
    """Main CLI loop"""
    print_header("CIPHER WORLD CLI")
    print("Welcome to Cipher World - Command Line Interface")
    print("Type 'help' for available commands")
    print_divider()
    
    # Load history
    load_cipher_history()
    
    # Main command loop
    while True:
        try:
            command = input("\ncipher> ").strip()
            if command:
                handle_command(command)
        except KeyboardInterrupt:
            print("\n\n✓ Use 'exit' or 'quit' to close the program")
        except EOFError:
            print("\n\n✓ Goodbye!")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    # Initialize global variables
    last_result = None
    main()