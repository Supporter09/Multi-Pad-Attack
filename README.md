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

- After research for idea like `guessing` and `score`, i have prepare a prompt explain the general idea and approach for Google AI Studio to help me build the base code. After that, i add interactive mode to correct wrong char after automated process. (Prompt in `prompt.txt`)

