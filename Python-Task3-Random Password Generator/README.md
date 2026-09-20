# OASIS INFOBYTE Python Programming Internship
## Task 3: Random Password Generator (Advanced Version)

An advanced, cryptographically secure desktop password generator built in Python using **Tkinter**, the standard **secrets** module, and **pyperclip**.

---

## 1. Project Title
**OASIS INFOBYTE Internship — Task 3: Advanced Random Password Generator**

- **Domain:** Python Programming
- **Task Number:** Task 3
- **Internship Host:** OASIS INFOBYTE
- **Author:** Internship Participant
- **Application Type:** Desktop GUI Application (Tkinter)

---

## 2. Project Description
This project delivers the **Advanced Version** of the Random Password Generator for the OASIS INFOBYTE Python Programming Internship. 

Unlike standard password generators that rely on the pseudo-random `random` module or simple concatenation, this application employs Python's cryptographically secure `secrets` module (based on OS-level entropy from `/dev/urandom` or `CryptGenRandom`). It enforces strict security policies, guarantees representation from every selected character category, provides dynamic password strength evaluation, supports ambiguous-character exclusion, and maintains an in-memory session history of the last 5 generated passwords.

---

## 3. Key Features

1. **Customizable Password Length**:
   - Allows users to specify any desired length (minimum 8 characters, maximum 128+).
   - Includes quick-preset buttons (`12`, `16`, `24`, `32` characters).
   - Full input sanitization rejecting negative, empty, non-numeric, or <8 values.

2. **Character Category Selection**:
   - Toggle Uppercase Letters (`A-Z`)
   - Toggle Lowercase Letters (`a-z`)
   - Toggle Numeric Digits (`0-9`)
   - Toggle Special Symbols (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

3. **Mandatory Security Validation**:
   - Requires a minimum of at least two (2) character categories to guarantee complexity.
   - Prevents generation if fewer than 2 types are chosen, displaying clear GUI error dialogs.
   - Validates that length is greater than or equal to the number of chosen types.

4. **Cryptographically Secure Generation**:
   - Powered by Python's `secrets` module (CSPRNG).
   - **Guaranteed Category Representation**: Selects at least one character from every active category so no category is omitted.
   - Secure Fisher-Yates shuffle using `secrets.randbelow` to eliminate modulo bias.

5. **Ambiguous Character Filtering**:
   - Optional exclusion of visually confusing characters (`0`, `O`, `l`, `I`, `1`, `|`).
   - Prevents transcription errors on handwritten or print credentials.

6. **Password Strength Evaluation**:
   - Real-time visual progress meter and status badge:
     - **Weak** (Orange/Red)
     - **Medium** (Yellow)
     - **Strong** (Green)
     - **Very Strong** (Emerald)
   - Evaluates length, character category variety, and entropy.

7. **One-Click Clipboard Copying**:
   - Dedicated "Copy Password" button using `pyperclip`.
   - Native Tkinter clipboard fallback for maximum cross-platform compatibility.
   - Visual success banner confirmation.

8. **Session-Only History (Last 5 Passwords)**:
   - Stores the last 5 generated passwords in volatile memory (RAM) only.
   - Double-click or select any historic password to copy it.
   - **Zero Persistence**: Absolutely no passwords are written to disk, files, or network databases. When the app is closed, all history is destroyed.

9. **Robust Error Handling**:
   - The application never crashes from user input errors, non-numeric strings, clipboard errors, or edge cases.

---

## 4. Technologies Used

| Technology / Library | Purpose | Source |
| :--- | :--- | :--- |
| **Python 3.8+** | Core Programming Language | Standard |
| **tkinter / ttk** | Native Desktop Graphical User Interface | Standard Library |
| **secrets** | Cryptographically Secure Pseudo-Random Number Generator (CSPRNG) | Standard Library |
| **string** | Standard character constants (`ascii_uppercase`, `digits`, etc.) | Standard Library |
| **collections.deque** | Fixed-size bounded queue for session-only history (maxlen=5) | Standard Library |
| **pyperclip** | Cross-platform clipboard read/write engine | External Dependency (`requirements.txt`) |

---

## 5. Python Version Requirements
- **Python 3.8, 3.9, 3.10, 3.11, or 3.12+**
- Tkinter included with standard Python installations on Windows and macOS.
- On Linux/Debian: `sudo apt-get install python3-tk`

---

## 6. Installation & Setup Instructions

### Step 1: Clone or Download the Project
Navigate to your cloned repository folder:
```bash
git clone <your-github-repository-url>
cd <repository-folder>
```

### Step 2: Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the single external dependency (`pyperclip`):
```bash
python -m pip install -r requirements.txt
```

---

## 7. How to Run the Application

### Running the Desktop GUI (Default):
Execute the main script:
```bash
python password_generator.py
```
*(On Linux/macOS, use `python3 password_generator.py`)*

### Running in Headless / Terminal CLI Mode:
If you are operating on a headless remote server or without a desktop display:
```bash
python password_generator.py --cli
```

### Running the Automated Unit Tests:
Run the test suite validating the cryptographic constraints:
```bash
python -m unittest test_generator.py
```

---

## 8. How the Password Generation Works

The generation follows a 4-step security pipeline:

1. **Pool Compilation & Sanitization**:
   Based on user checkboxes, individual pools (`uppercase`, `lowercase`, `digits`, `symbols`) are created. If "Exclude ambiguous characters" is enabled, characters in `set("0OlI1|")` are removed.

2. **Guaranteed Class Representation**:
   To satisfy security compliance (NIST / CIS benchmarks), one character is drawn from *each* selected pool using `secrets.choice()`. This guarantees that if symbols are selected, the password is mathematical guaranteed to have at least one symbol.

3. **Remainder Filling**:
   The remaining characters needed to reach the desired length are sampled from the combined pool using `secrets.choice()`.

4. **Zero-Bias Cryptographic Fisher-Yates Shuffle**:
   To prevent predictable placement of the guaranteed characters, the character array is shuffled using:
   ```python
   for i in range(len(password_chars) - 1, 0, -1):
       j = secrets.randbelow(i + 1)
       password_chars[i], password_chars[j] = password_chars[j], password_chars[i]
   ```
   This produces a uniformly random permutation.

---

## 9. Security & Privacy Considerations

- **CSPRNG vs PRNG**: Standard `random.choice()` uses the Mersenne Twister (MT19937), which is completely predictable after observing 624 outputs. This application strictly uses `secrets` backed by the operating system's cryptographic entropy source.
- **Local Generation**: Passwords are generated 100% offline on the local CPU.
- **No Disk Storage**: Passwords are never logged to `.txt`, `.csv`, `.json`, or SQLite databases.
- **Session-Only Memory**: The last 5 generated passwords reside in an in-memory `collections.deque(maxlen=5)`. Once the Tkinter window closes, the memory is purged by the operating system.

---

## 10. Validation & Error Handling Matrix

| User Input / Action | Handling Strategy | User Feedback |
| :--- | :--- | :--- |
| Empty length field | Handled via `try/except ValueError` | GUI Error Dialog + Red Status Banner |
| Non-numeric input (e.g., `"abc"`) | Rejects non-integer string | "Password length must be a numeric integer" |
| Length < 8 | Enforces minimum security threshold | "Password length must be at least 8 characters" |
| Fewer than 2 categories selected | Enforces diversity requirement | "Please select at least two (2) character types" |
| Clipboard unavailable | Catches OS exception with Tk fallback | Graceful error notification without crashing |

---

## 11. Project File Structure

```text
├── password_generator.py       # Main Python Tkinter GUI & CLI Application
├── requirements.txt           # External dependencies (pyperclip)
├── test_generator.py          # Cryptographic validation unit tests
├── README.md                  # Complete internship documentation
├── screenshots/               # Directory for execution screenshots
│   └── README.md              # Screenshot capture guidelines
├── .gitignore                 # Configured for Python & Node environments
├── package.json               # Web simulator manifest
└── src/                       # Interactive web preview interface
```

---

## 12. How to Push to GitHub

```bash
# 1. Initialize git repository (if not already initialized)
git init

# 2. Stage all project files
git add .

# 3. Create your initial commit
git commit -m "Task 3: Random Password Generator - OASIS INFOBYTE"

# 4. Set main branch and link your remote repository
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repository-name>.git

# 5. Push to GitHub
git push -u origin main
```

---

## 13. Screenshots Section Placeholder

Capture and place your execution screenshots in the `screenshots/` directory:

| Screenshot | Description | File Path |
| :--- | :--- | :--- |
| **Main GUI** | Application window with default 16-character settings | `screenshots/gui_main.png` |
| **Generated Password** | Output with "Very Strong" indicator | `screenshots/gui_generated.png` |
| **Session History** | In-memory list showing last 5 generated passwords | `screenshots/gui_history.png` |
| **Validation Error** | Alert dialog when fewer than 2 types are checked | `screenshots/gui_validation.png` |

---

## 14. Internship Submission Checklist

- [x] Python used as primary language
- [x] Tkinter used for the desktop GUI
- [x] Python `secrets` module used for cryptographically secure random generation
- [x] Python `string` module used for character sets
- [x] `pyperclip` used for clipboard copying
- [x] Minimum password length validation (>= 8 characters)
- [x] Input validation for empty, negative, or invalid length
- [x] Checkboxes for Uppercase, Lowercase, Numbers, and Symbols
- [x] Minimum 2 character types validation
- [x] Guaranteed representation of all selected character classes
- [x] Secure Fisher-Yates array shuffling
- [x] Password strength indicator (Weak, Medium, Strong, Very Strong)
- [x] Copy Password button with confirmation feedback
- [x] Generate / Regenerate password button
- [x] Session-only history of the last 5 generated passwords
- [x] In-memory storage only (no persistent files or databases)
- [x] Ambiguous character exclusion option (0, O, l, I, 1, |)
- [x] Professional, user-friendly desktop GUI layout
- [x] Comprehensive error handling preventing application crashes
- [x] Clean, well-documented code with comments and functions
- [x] `requirements.txt` containing only external dependencies
- [x] Complete, professional `README.md`
