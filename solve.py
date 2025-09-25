import os
import argparse
import sys

# --- Configuration ---
SCORING_TABLE = {
    b' ': 10, b'e': 9, b't': 8, b'a': 7, b'o': 7, b'i': 7, b'n': 7,
    b's': 6, b'h': 6, b'r': 6, b'd': 5, b'l': 5, b'u': 5,
}
for i in range(32, 127):
    char = bytes([i])
    if char.isalpha() and char.lower() not in SCORING_TABLE:
        SCORING_TABLE[char.lower()] = 3
    elif char.isdigit():
        SCORING_TABLE[char] = 2
    elif char in b'.,!?;:\'"()[]{}':
        SCORING_TABLE[char] = 1

# --- Core Attack Logic ---

def score_text(byte_string):
    """Scores a byte string based on character frequency."""
    score = 0
    for byte in byte_string:
        char = bytes([byte])
        score += SCORING_TABLE.get(char.lower(), -5)
        if not (32 <= byte <= 126):
            score -= 10
    return score

def solve_many_time_pad(ciphertexts, target_index):
    """
    Automates the initial pass of the attack, continuing as long as
    at least two ciphertexts are available.
    """
    if not ciphertexts or not (0 <= target_index < len(ciphertexts)):
        raise ValueError("Invalid target index or empty ciphertext list.")

    ### <<< CHANGE START: The logic now handles variable lengths >>>
    target_ciphertext = ciphertexts[target_index]
    target_len = len(target_ciphertext)
    key = bytearray(target_len)
    
    print(f"\n[*] Starting automated attack. Analyzing up to {target_len} bytes...")

    # Iterate up to the full length of the target ciphertext
    for i in range(target_len):
        # Dynamically create a list of ciphertexts that are long enough for this position
        ciphertexts_at_pos_i = [c for c in ciphertexts if i < len(c)]
        
        # We need at least 2 ciphertexts (e.g., target + another) to run the attack
        if len(ciphertexts_at_pos_i) < 2:
            print(f"\n[*] Automated guessing stopped at position {i} due to insufficient overlapping ciphertexts.")
            # Fill the rest of the key with zeros (or a placeholder)
            for j in range(i, target_len):
                key[j] = 0 # This part will require manual user correction
            break

        best_guess_for_key_byte = 0
        highest_score = -float('inf')

        for key_byte_guess in range(256):
            decrypted_column = bytearray(c[i] ^ key_byte_guess for c in ciphertexts_at_pos_i)
            current_score = score_text(decrypted_column)
            
            if current_score > highest_score:
                highest_score = current_score
                best_guess_for_key_byte = key_byte_guess
        
        key[i] = best_guess_for_key_byte

        if (i + 1) % 10 == 0 or i == target_len - 1:
            print(f"\r[*] Progress: {i + 1}/{target_len} bytes recovered...", end="")
            sys.stdout.flush()

    print("\n[+] Automated attack complete!")

    # Decrypt each ciphertext up to its own length or the key's length
    plaintexts = []
    for c in ciphertexts:
        max_decrypt_len = min(len(c), len(key))
        plaintexts.append(bytearray(c[j] ^ key[j] for j in range(max_decrypt_len)))

    return key, plaintexts
    ### <<< CHANGE END >>>

# --- Interactive UI and Refinement ---

def display_state(plaintexts, target_index):
    """Displays the current state of the decrypted plaintexts."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 80)
    print("INTERACTIVE REFINEMENT MODE")
    print("=" * 80)
    print("Enter 'msg_idx,char_pos,new_char' to make a correction.")
    print("Example: '3,15,e' means plaintext 3, position 15, should be 'e'.")
    print("Enter 'quit' or 'exit' to finish.")
    print("-" * 80)

    max_len = len(plaintexts[target_index])
    
    # Header with character indices
    tens = " " * 12
    units = " " * 12
    for i in range(max_len):
        tens += str(i // 10) if i % 10 == 0 else " "
        units += str(i % 10)
    print(tens)
    print(units)
    print("-" * (max_len + 12))

    for i, p in enumerate(plaintexts):
        prefix = ">> TARGET" if i == target_index else f"   P {i}"
        decoded_p = p.decode('utf-8', 'replace').replace('\n', ' ')
        print(f"{prefix:10}: {decoded_p}")
    print("-" * 80)

def interactive_refinement_loop(key, plaintexts, ciphertexts, target_index):
    """Handles the user-in-the-loop correction process."""
    ### <<< CHANGE START: Max length is now based on target text >>>
    target_len = len(ciphertexts[target_index])
    ### <<< CHANGE END >>>

    while True:
        display_state(plaintexts, target_index)
        
        try:
            user_input = input("Enter correction (or 'quit'): ").strip().lower()
            if user_input in ['quit', 'exit']:
                break
            
            parts = user_input.split(',')
            if len(parts) != 3:
                print("[!] Invalid format. Please use 'msg_idx,char_pos,new_char'.")
                input("Press Enter to continue...")
                continue
            
            msg_idx, char_pos, new_char = int(parts[0]), int(parts[1]), parts[2]

            if not (0 <= msg_idx < len(plaintexts)):
                print(f"[!] Message index must be between 0 and {len(plaintexts)-1}.")
                input("Press Enter to continue...")
                continue
            ### <<< CHANGE START: Validate against appropriate lengths >>>
            if not (0 <= char_pos < target_len):
                print(f"[!] Character position must be between 0 and {target_len-1}.")
                input("Press Enter to continue...")
                continue
            if not (char_pos < len(ciphertexts[msg_idx])):
                 print(f"[!] Position {char_pos} is out of bounds for message {msg_idx} (length {len(ciphertexts[msg_idx])}).")
                 input("Press Enter to continue...")
                 continue
            ### <<< CHANGE END >>>
            if len(new_char) != 1:
                print("[!] Please provide a single character.")
                input("Press Enter to continue...")
                continue

            new_char_byte = ord(new_char)
            c_user = ciphertexts[msg_idx]
            new_key_byte = c_user[char_pos] ^ new_char_byte
            key[char_pos] = new_key_byte
            
            # Propagate the change to all other plaintexts that are long enough
            for i in range(len(plaintexts)):
                if char_pos < len(ciphertexts[i]):
                    plaintexts[i][char_pos] = ciphertexts[i][char_pos] ^ new_key_byte

        except (ValueError, IndexError) as e:
            print(f"[!] Invalid input: {e}. Please follow the format.")
            input("Press Enter to continue...")

    return key, plaintexts

# --- Main Application ---
def main():
    parser = argparse.ArgumentParser(
        description="Advanced Interactive Many-Time Pad Attack Solver.",
        epilog="Example: python advanced_interactive_solver.py -d ciphers/ -t 0"
    )
    parser.add_argument("-d", "--directory", required=True, help="Directory containing ciphertext files (hex format).")
    parser.add_argument("-t", "--target", required=True, type=int, help="Index of the target ciphertext file.")

    args = parser.parse_args()

    try:
        files = sorted([os.path.join(args.directory, f) for f in os.listdir(args.directory)])
        ciphertexts = [bytes.fromhex(open(f, 'r').read().strip()) for f in files]
        print(f"[+] Loaded {len(ciphertexts)} ciphertexts.")
    except Exception as e:
        print(f"[!] Error loading ciphertexts: {e}")
        return

    try:
        if not (0 <= args.target < len(ciphertexts)):
            print(f"[!] Error: Target index {args.target} is out of bounds.")
            return
        initial_key, initial_plaintexts = solve_many_time_pad(ciphertexts, args.target)
    except Exception as e:
        print(f"[!] An error occurred during the automated attack: {e}")
        return

    final_key, final_plaintexts = interactive_refinement_loop(
        initial_key, initial_plaintexts, ciphertexts, args.target
    )

    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"\n[+] Final Recovered Key (hex):\n{final_key.hex()}")
    print("\n[+] Final Decrypted Plaintexts:")
    for i, p in enumerate(final_plaintexts):
        prefix = ">> TARGET" if i == args.target else f"   P {i}"
        print(f"{prefix}: {p.decode('utf-8', 'replace')}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()