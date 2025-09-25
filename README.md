## Many-Time Pad Attack Solver

### I. How to Use

- **Prepare Ciphertexts**
  - Create a folder (e.g., `ciphers/`).
  - Place each ciphertext in its own file: `c0.txt`, `c1.txt`, …
  - Each file must contain a hex string, e.g., `1a2b3c4d...`.

- **Run the Script**
  - Point to the directory and target index ( if c10.txt is target cipher then index is 10 ):

    ```bash
    python solve.py --directory ciphers/ --target 10
    ```

  - Or with short flags:

    ```bash
    python solve.py -d ciphers/ -t 10
    ```

- **Fix Mistakes (Interactive Mode)**
![Interactive Mode](./assets/interactive_mode.png)

### II. Core Logic

- **Scoring**
  - The `score_text` function evaluates characters with a `SCORING_TABLE`.
  - Spaces and common English letters score high; non-printables score low.

- **Key Guessing**
  - For each byte position, try all 256 possible key values.
  - Decrypt that column across all ciphertexts.
  - Score the results, pick the best key byte.
  - Repeat until the full key of target cipher is derived.

### III. How I Build This Attack

- **Concept**: XOR of two ciphertexts reveals XOR of plaintexts. If you can guess part of one, the other is exposed.
- **Automation**: Instead of manual guessing, i try to guess all characters for each position with code and scores them.
- **Improvement**: UsingiInteractive mode to fix any wrong characters to ensure a perfect key and accurate decryption.
