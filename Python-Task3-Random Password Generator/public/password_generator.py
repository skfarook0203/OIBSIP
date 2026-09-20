#!/usr/bin/env python3
"""
=============================================================================
OASIS INFOBYTE Python Programming Internship
Task 3: Random Password Generator (Advanced Version)
=============================================================================
Author: OASIS Infobyte Intern
Language: Python 3
GUI Framework: Tkinter / ttk
Key Modules: secrets, string, pyperclip
=============================================================================
Features:
1. Customizable Password Length (Minimum 8 characters)
2. Character Selection: Uppercase, Lowercase, Digits, Symbols
3. Ambiguous Character Exclusion (0, O, l, I, 1, |)
4. Strict Validation: Requires at least 2 character types
5. Cryptographically Secure Generation using Python's 'secrets' module
6. Guaranteed Representation of all selected character classes
7. Secure Fisher-Yates array shuffle with secrets.randbelow
8. Dynamic Password Strength Evaluation (Weak, Medium, Strong, Very Strong)
9. One-click Clipboard Copy using pyperclip
10. Session-Only History (Last 5 generated passwords)
11. Comprehensive Error Handling & Input Sanitization
=============================================================================
"""

import sys
import string
import secrets
from collections import deque

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False


# =============================================================================
# Core Cryptographic Password Generation Engine
# =============================================================================

def generate_secure_password(
    length: int,
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_ambiguous: bool = False
) -> str:
    """
    Generates a cryptographically secure password using Python's `secrets` module.
    
    Guarantees that every selected character type is represented at least once
    in the resulting password.
    
    Args:
        length: Desired length of the password (minimum 8).
        use_upper: Include uppercase letters (A-Z).
        use_lower: Include lowercase letters (a-z).
        use_digits: Include digits (0-9).
        use_symbols: Include special symbols.
        exclude_ambiguous: Filter out visually confusing characters (0, O, l, I, 1, |).
        
    Returns:
        A securely randomized password string.
        
    Raises:
        ValueError: If input parameters violate security constraints.
    """
    if not isinstance(length, int) or length < 8:
        raise ValueError("Password length must be an integer of at least 8 characters.")

    # Visually ambiguous characters
    ambiguous_chars = set("0OlI1|")

    selected_pools = []

    if use_upper:
        pool = string.ascii_uppercase
        if exclude_ambiguous:
            pool = "".join(ch for ch in pool if ch not in ambiguous_chars)
        if pool:
            selected_pools.append(pool)

    if use_lower:
        pool = string.ascii_lowercase
        if exclude_ambiguous:
            pool = "".join(ch for ch in pool if ch not in ambiguous_chars)
        if pool:
            selected_pools.append(pool)

    if use_digits:
        pool = string.digits
        if exclude_ambiguous:
            pool = "".join(ch for ch in pool if ch not in ambiguous_chars)
        if pool:
            selected_pools.append(pool)

    if use_symbols:
        # Standard keyboard symbol set
        pool = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if exclude_ambiguous:
            pool = "".join(ch for ch in pool if ch not in ambiguous_chars)
        if pool:
            selected_pools.append(pool)

    # Validation: at least 2 character categories must be selected
    if len(selected_pools) < 2:
        raise ValueError("Please select at least two (2) character types for a secure password.")

    if length < len(selected_pools):
        raise ValueError(
            f"Requested length ({length}) is too short to guarantee all {len(selected_pools)} selected character types."
        )

    # 1. Guarantee representation: select 1 random character from each chosen pool
    password_chars = [secrets.choice(pool) for pool in selected_pools]

    # 2. Fill the remainder using the combined chosen pool
    combined_pool = "".join(selected_pools)
    remaining_length = length - len(password_chars)
    for _ in range(remaining_length):
        password_chars.append(secrets.choice(combined_pool))

    # 3. Cryptographically secure Fisher-Yates shuffle
    # Using secrets.randbelow to ensure zero modulo bias
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


def evaluate_password_strength(password: str):
    """
    Evaluates password strength based on length, character diversity, and entropy.
    
    Returns:
        tuple: (score: int 0-4, label: str, hex_color: str, percentage: int)
    """
    if not password:
        return 0, "No Password", "#94a3b8", 0

    length = len(password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    categories_count = sum([has_upper, has_lower, has_digit, has_symbol])

    # Base strength evaluation
    if length < 8 or categories_count < 2:
        return 1, "Weak", "#ef4444", 25

    if length < 12:
        if categories_count >= 3:
            return 2, "Medium", "#f59e0b", 50
        return 1, "Weak", "#ef4444", 30

    if length < 16:
        if categories_count >= 3:
            return 3, "Strong", "#10b981", 75
        return 2, "Medium", "#f59e0b", 55

    # Length >= 16
    if categories_count >= 4:
        return 4, "Very Strong", "#059669", 100
    elif categories_count >= 3:
        return 4, "Very Strong" if length >= 20 else "Strong", "#059669" if length >= 20 else "#10b981", 90 if length >= 20 else 80

    return 2, "Medium", "#f59e0b", 60


# =============================================================================
# Tkinter Desktop GUI Application
# =============================================================================

class PasswordGeneratorApp:
    """
    Advanced Tkinter GUI for the OASIS Infobyte Password Generator.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Oasis Infobyte — Task 3: Random Password Generator")
        self.root.geometry("640x760")
        self.root.minsize(560, 680)

        # Session-only password history (Max 5 items, disappears on app exit)
        self.history = deque(maxlen=5)

        # Tkinter reactive variables
        self.length_var = tk.StringVar(value="16")
        self.use_upper_var = tk.BooleanVar(value=True)
        self.use_lower_var = tk.BooleanVar(value=True)
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_symbols_var = tk.BooleanVar(value=True)
        self.exclude_ambiguous_var = tk.BooleanVar(value=False)

        self.generated_password_var = tk.StringVar(value="")
        self.status_msg_var = tk.StringVar(value="Ready. Click 'Generate Password' to create a secure key.")
        self.status_type = "info"  # "info", "success", "error"

        # Setup colors and styling
        self._configure_styles()

        # Build UI layout
        self._create_widgets()

        # Bind shortcut keys
        self.root.bind("<Return>", lambda event: self.handle_generate())

        # Generate initial password
        self.handle_generate()

    def _configure_styles(self):
        """Sets up ttk styles and modern color scheme."""
        self.bg_main = "#0f172a"        # Deep slate background
        self.bg_card = "#1e293b"        # Card background
        self.bg_input = "#334155"       # Input field background
        self.text_primary = "#f8fafc"   # White text
        self.text_secondary = "#94a3b8" # Light slate text
        self.accent_green = "#10b981"   # Emerald accent
        self.accent_hover = "#059669"
        self.border_color = "#475569"

        self.root.configure(bg=self.bg_main)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure generic frame styles
        self.style.configure("Main.TFrame", background=self.bg_main)
        self.style.configure("Card.TFrame", background=self.bg_card, relief="flat")
        self.style.configure("Inner.TFrame", background=self.bg_card)

        # Checkbutton styles
        self.style.configure(
            "Custom.TCheckbutton",
            background=self.bg_card,
            foreground=self.text_primary,
            font=("Segoe UI", 10, "normal")
        )
        self.style.map(
            "Custom.TCheckbutton",
            background=[("active", self.bg_card)],
            foreground=[("active", self.accent_green)]
        )

        # Progressbar
        self.style.configure(
            "Strength.Horizontal.TProgressbar",
            troughcolor="#334155",
            bordercolor=self.bg_card,
            lightcolor=self.accent_green,
            darkcolor=self.accent_green,
            background=self.accent_green
        )

    def _create_widgets(self):
        """Constructs all UI components."""
        # Top Header Banner
        header_frame = tk.Frame(self.root, bg=self.bg_main, padx=20, pady=16)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="OASIS INFOBYTE INTERNSHIP",
            font=("Segoe UI", 9, "bold"),
            fg=self.accent_green,
            bg=self.bg_main
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Task 3: Random Password Generator",
            font=("Segoe UI", 18, "bold"),
            fg=self.text_primary,
            bg=self.bg_main
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        desc_label = tk.Label(
            header_frame,
            text="Cryptographically secure password engine powered by Python's 'secrets' module.",
            font=("Segoe UI", 9),
            fg=self.text_secondary,
            bg=self.bg_main
        )
        desc_label.pack(anchor="w", pady=(2, 0))

        # Main Scrollable / Padded Container
        container = tk.Frame(self.root, bg=self.bg_main, padx=20, pady=0)
        container.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 1. Output Display Card
        # -------------------------------------------------------------
        output_card = tk.LabelFrame(
            container,
            text=" Generated Secure Password ",
            font=("Segoe UI", 10, "bold"),
            fg=self.accent_green,
            bg=self.bg_card,
            padx=14,
            pady=12,
            relief="solid",
            bd=1
        )
        output_card.pack(fill="x", pady=(0, 14))

        # Password Entry / Display
        display_frame = tk.Frame(output_card, bg=self.bg_card)
        display_frame.pack(fill="x", pady=(4, 8))

        self.password_entry = tk.Entry(
            display_frame,
            textvariable=self.generated_password_var,
            font=("Consolas", 14, "bold"),
            bg="#090d16",
            fg="#38bdf8",
            insertbackground="white",
            relief="flat",
            readonlybackground="#090d16",
            state="readonly",
            justify="center"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        self.copy_btn = tk.Button(
            display_frame,
            text="📋 Copy",
            command=self.handle_copy,
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            padx=16,
            cursor="hand2"
        )
        self.copy_btn.pack(side="right", ipady=5)

        # Strength Meter Frame
        strength_frame = tk.Frame(output_card, bg=self.bg_card)
        strength_frame.pack(fill="x", pady=(4, 0))

        self.strength_lbl_title = tk.Label(
            strength_frame,
            text="Security Strength:",
            font=("Segoe UI", 9),
            fg=self.text_secondary,
            bg=self.bg_card
        )
        self.strength_lbl_title.pack(side="left")

        self.strength_badge = tk.Label(
            strength_frame,
            text="None",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg=self.bg_card,
            padx=6
        )
        self.strength_badge.pack(side="left")

        self.strength_bar = ttk.Progressbar(
            strength_frame,
            style="Strength.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100
        )
        self.strength_bar.pack(side="right", fill="x", expand=True, padx=(12, 0))

        # -------------------------------------------------------------
        # 2. Configuration & Parameter Controls Card
        # -------------------------------------------------------------
        config_card = tk.LabelFrame(
            container,
            text=" Security & Character Configuration ",
            font=("Segoe UI", 10, "bold"),
            fg=self.accent_green,
            bg=self.bg_card,
            padx=14,
            pady=12,
            relief="solid",
            bd=1
        )
        config_card.pack(fill="x", pady=(0, 14))

        # Row 1: Length Setting
        length_frame = tk.Frame(config_card, bg=self.bg_card)
        length_frame.pack(fill="x", pady=(0, 10))

        length_label = tk.Label(
            length_frame,
            text="Password Length (Min 8):",
            font=("Segoe UI", 10, "bold"),
            fg=self.text_primary,
            bg=self.bg_card
        )
        length_label.pack(side="left")

        self.length_spinbox = tk.Spinbox(
            length_frame,
            from_=8,
            to=128,
            textvariable=self.length_var,
            font=("Segoe UI", 11, "bold"),
            width=6,
            justify="center",
            bg="#090d16",
            fg=self.accent_green,
            insertbackground="white",
            relief="flat"
        )
        self.length_spinbox.pack(side="right")

        # Quick preset buttons for convenience
        preset_frame = tk.Frame(config_card, bg=self.bg_card)
        preset_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            preset_frame,
            text="Quick Presets:",
            font=("Segoe UI", 9),
            fg=self.text_secondary,
            bg=self.bg_card
        ).pack(side="left")

        for p_len in [12, 16, 24, 32]:
            btn = tk.Button(
                preset_frame,
                text=f"{p_len} Chars",
                command=lambda l=p_len: self.set_length_preset(l),
                font=("Segoe UI", 8),
                bg="#334155",
                fg=self.text_primary,
                activebackground="#475569",
                relief="flat",
                padx=8,
                pady=1,
                cursor="hand2"
            )
            btn.pack(side="left", padx=(6, 0))

        # Divider
        tk.Frame(config_card, height=1, bg="#334155").pack(fill="x", pady=(2, 10))

        # Checkbox Grid for Character Types
        check_grid = tk.Frame(config_card, bg=self.bg_card)
        check_grid.pack(fill="x")

        # Uppercase
        chk_upper = tk.Checkbutton(
            check_grid,
            text="Uppercase Letters (A-Z)",
            variable=self.use_upper_var,
            font=("Segoe UI", 10),
            fg=self.text_primary,
            bg=self.bg_card,
            activebackground=self.bg_card,
            activeforeground=self.accent_green,
            selectcolor="#090d16"
        )
        chk_upper.grid(row=0, column=0, sticky="w", pady=4, padx=(0, 16))

        # Lowercase
        chk_lower = tk.Checkbutton(
            check_grid,
            text="Lowercase Letters (a-z)",
            variable=self.use_lower_var,
            font=("Segoe UI", 10),
            fg=self.text_primary,
            bg=self.bg_card,
            activebackground=self.bg_card,
            activeforeground=self.accent_green,
            selectcolor="#090d16"
        )
        chk_lower.grid(row=0, column=1, sticky="w", pady=4)

        # Numbers
        chk_digits = tk.Checkbutton(
            check_grid,
            text="Numbers / Digits (0-9)",
            variable=self.use_digits_var,
            font=("Segoe UI", 10),
            fg=self.text_primary,
            bg=self.bg_card,
            activebackground=self.bg_card,
            activeforeground=self.accent_green,
            selectcolor="#090d16"
        )
        chk_digits.grid(row=1, column=0, sticky="w", pady=4, padx=(0, 16))

        # Symbols
        chk_symbols = tk.Checkbutton(
            check_grid,
            text="Special Symbols (!@#$%^&*)",
            variable=self.use_symbols_var,
            font=("Segoe UI", 10),
            fg=self.text_primary,
            bg=self.bg_card,
            activebackground=self.bg_card,
            activeforeground=self.accent_green,
            selectcolor="#090d16"
        )
        chk_symbols.grid(row=1, column=1, sticky="w", pady=4)

        # Divider
        tk.Frame(config_card, height=1, bg="#334155").pack(fill="x", pady=(8, 8))

        # Ambiguous character exclusion toggle
        chk_ambiguous = tk.Checkbutton(
            config_card,
            text="Exclude Ambiguous Characters (0, O, l, I, 1, |)",
            variable=self.exclude_ambiguous_var,
            font=("Segoe UI", 9, "italic"),
            fg="#cbd5e1",
            bg=self.bg_card,
            activebackground=self.bg_card,
            activeforeground=self.accent_green,
            selectcolor="#090d16"
        )
        chk_ambiguous.pack(anchor="w")

        # -------------------------------------------------------------
        # 3. Action Button: Generate Password
        # -------------------------------------------------------------
        self.generate_btn = tk.Button(
            container,
            text="⚡ GENERATE PASSWORD",
            command=self.handle_generate,
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_green,
            fg="#042f2e",
            activebackground=self.accent_hover,
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=10
        )
        self.generate_btn.pack(fill="x", pady=(0, 14))

        # -------------------------------------------------------------
        # 4. Status Notification Banner
        # -------------------------------------------------------------
        self.status_banner = tk.Label(
            container,
            textvariable=self.status_msg_var,
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#0c4a6e",
            padx=10,
            pady=6,
            relief="flat"
        )
        self.status_banner.pack(fill="x", pady=(0, 14))

        # -------------------------------------------------------------
        # 5. Session History (Last 5 Passwords)
        # -------------------------------------------------------------
        history_card = tk.LabelFrame(
            container,
            text=" Session History — Last 5 Generated Passwords (In-Memory Only) ",
            font=("Segoe UI", 10, "bold"),
            fg=self.accent_green,
            bg=self.bg_card,
            padx=14,
            pady=10,
            relief="solid",
            bd=1
        )
        history_card.pack(fill="both", expand=True, pady=(0, 10))

        tk.Label(
            history_card,
            text="Passwords below are stored in RAM during this session only. Click any item to copy.",
            font=("Segoe UI", 8),
            fg=self.text_secondary,
            bg=self.bg_card
        ).pack(anchor="w", pady=(0, 6))

        self.history_listbox = tk.Listbox(
            history_card,
            font=("Consolas", 10),
            bg="#090d16",
            fg="#e2e8f0",
            selectbackground="#0284c7",
            selectforeground="#ffffff",
            relief="flat",
            height=5,
            activestyle="none"
        )
        self.history_listbox.pack(fill="both", expand=True)
        self.history_listbox.bind("<Double-Button-1>", self.copy_selected_history)

        hist_btn_frame = tk.Frame(history_card, bg=self.bg_card)
        hist_btn_frame.pack(fill="x", pady=(6, 0))

        self.copy_hist_btn = tk.Button(
            hist_btn_frame,
            text="Copy Selected From History",
            command=self.copy_selected_history,
            font=("Segoe UI", 9),
            bg="#334155",
            fg=self.text_primary,
            activebackground="#475569",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2"
        )
        self.copy_hist_btn.pack(side="left")

        # Footer Notice
        footer_label = tk.Label(
            self.root,
            text="Oasis Infobyte Internship Task 3 • No passwords are saved to disk or network.",
            font=("Segoe UI", 8),
            fg=self.text_secondary,
            bg=self.bg_main,
            pady=6
        )
        footer_label.pack(side="bottom")

    def set_length_preset(self, length: int):
        """Sets the length to one of the quick preset options."""
        self.length_var.set(str(length))
        self.handle_generate()

    def set_status(self, message: str, status_type: str = "info"):
        """Updates the status banner with appropriate coloring."""
        self.status_msg_var.set(message)
        colors = {
            "info": ("#38bdf8", "#0c4a6e"),     # Light cyan text on dark blue
            "success": ("#4ade80", "#14532d"),  # Emerald text on dark green
            "error": ("#fca5a5", "#7f1d1d")     # Light red text on dark red
        }
        fg, bg = colors.get(status_type, ("#38bdf8", "#0c4a6e"))
        self.status_banner.configure(fg=fg, bg=bg)

    def handle_generate(self):
        """Validates inputs and generates a new secure password."""
        # 1. Parse and validate length
        raw_length = self.length_var.get().strip()
        if not raw_length:
            self.set_status("Error: Password length cannot be empty.", "error")
            messagebox.showerror("Validation Error", "Please enter a valid password length.")
            return

        try:
            length = int(raw_length)
        except ValueError:
            self.set_status("Error: Password length must be a numeric integer.", "error")
            messagebox.showerror("Validation Error", "Password length must be a valid number (e.g., 16).")
            return

        if length < 8:
            self.set_status("Error: Minimum password length is 8 characters.", "error")
            messagebox.showerror("Validation Error", "Password length must be at least 8 characters.")
            return

        if length > 256:
            self.set_status("Error: Maximum password length is 256 characters.", "error")
            messagebox.showerror("Validation Error", "Password length cannot exceed 256 characters.")
            return

        # 2. Check character types
        use_upper = self.use_upper_var.get()
        use_lower = self.use_lower_var.get()
        use_digits = self.use_digits_var.get()
        use_symbols = self.use_symbols_var.get()
        exclude_ambiguous = self.exclude_ambiguous_var.get()

        selected_count = sum([use_upper, use_lower, use_digits, use_symbols])
        if selected_count < 2:
            self.set_status("Error: Please select at least two (2) character types.", "error")
            messagebox.showerror(
                "Validation Error",
                "Security Policy Requirement:\nPlease select at least 2 character types (Uppercase, Lowercase, Numbers, or Symbols)."
            )
            return

        # 3. Generate password using cryptographically secure engine
        try:
            password = generate_secure_password(
                length=length,
                use_upper=use_upper,
                use_lower=use_lower,
                use_digits=use_digits,
                use_symbols=use_symbols,
                exclude_ambiguous=exclude_ambiguous
            )
        except Exception as err:
            self.set_status(f"Generation Error: {str(err)}", "error")
            messagebox.showerror("Generation Error", str(err))
            return

        # 4. Update display
        self.generated_password_var.set(password)

        # 5. Evaluate and update strength indicator
        score, label, hex_color, percent = evaluate_password_strength(password)
        self.strength_badge.configure(text=label, fg=hex_color)
        self.strength_bar["value"] = percent

        # 6. Add to session history
        self.history.appendleft(password)
        self._refresh_history_listbox()

        self.set_status(f"✓ New {length}-character password generated successfully ({label}).", "success")

    def _refresh_history_listbox(self):
        """Refreshes the session history listbox with the last 5 generated passwords."""
        self.history_listbox.delete(0, tk.END)
        for idx, pwd in enumerate(self.history, start=1):
            masked = pwd[:4] + "••••••••" + pwd[-4:] if len(pwd) > 16 else pwd
            self.history_listbox.insert(tk.END, f" #{idx}  [{len(pwd)} chars]  {pwd}")

    def handle_copy(self):
        """Copies the currently displayed password to the system clipboard."""
        password = self.generated_password_var.get()
        if not password:
            self.set_status("Warning: No password to copy. Click 'Generate Password' first.", "error")
            return

        copied = False

        # Attempt pyperclip first as required
        if PYPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(password)
                copied = True
            except Exception:
                copied = False

        # Fallback to Tkinter native clipboard if pyperclip has OS environment issues
        if not copied:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(password)
                self.root.update()  # Required on certain X11 systems
                copied = True
            except Exception as err:
                self.set_status(f"Clipboard Error: {str(err)}", "error")
                messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {err}")
                return

        self.set_status("✓ Password copied to clipboard successfully!", "success")

    def copy_selected_history(self, event=None):
        """Copies the selected password from the session history listbox."""
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            self.set_status("Select a password from the history list to copy.", "info")
            return

        index = selected_indices[0]
        if index < len(self.history):
            password = self.history[index]
            copied = False
            if PYPERCLIP_AVAILABLE:
                try:
                    pyperclip.copy(password)
                    copied = True
                except Exception:
                    copied = False

            if not copied:
                try:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(password)
                    self.root.update()
                    copied = True
                except Exception:
                    pass

            self.set_status(f"✓ Copied password #{index+1} from session history!", "success")


# =============================================================================
# CLI & Standalone Test Runner
# =============================================================================

def run_cli_mode():
    """
    Interactive and automated command-line interface for headless environments or terminal use.
    Supports both command line flags and interactive prompts.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="OASIS INFOBYTE Task 3 — Cryptographically Secure Random Password Generator",
        add_help=False
    )
    parser.add_argument("--cli", "-c", action="store_true", help="Run in CLI mode")
    parser.add_argument("--length", "-l", type=int, default=None, help="Password length (min 8)")
    parser.add_argument("--no-upper", action="store_true", help="Exclude uppercase letters")
    parser.add_argument("--no-lower", action="store_true", help="Exclude lowercase letters")
    parser.add_argument("--no-digits", action="store_true", help="Exclude numbers / digits")
    parser.add_argument("--no-symbols", action="store_true", help="Exclude special symbols")
    parser.add_argument("--exclude-ambiguous", "--no-ambiguous", action="store_true", help="Exclude ambiguous characters (0, O, l, I, 1, |)")
    parser.add_argument("--help", "-h", action="store_true", help="Show help message")

    args, unknown = parser.parse_known_args()

    if args.help:
        parser.print_help()
        return

    # If length is specified or non-interactive environment, use flags directly
    if args.length is not None or not sys.stdin.isatty():
        length = args.length if args.length is not None else 16
        use_upper = not args.no_upper
        use_lower = not args.no_lower
        use_digits = not args.no_digits
        use_symbols = not args.no_symbols
        exclude_ambiguous = args.exclude_ambiguous
    else:
        print("=" * 60)
        print("OASIS INFOBYTE — Task 3: Random Password Generator (CLI Mode)")
        print("=" * 60)

        try:
            raw_len = input("Enter desired password length (min 8) [Default: 16]: ").strip()
            length = int(raw_len) if raw_len else 16
        except ValueError:
            print("Invalid length. Defaulting to 16.")
            length = 16

        use_upper = input("Include Uppercase letters (A-Z)? [Y/n]: ").strip().lower() != 'n'
        use_lower = input("Include Lowercase letters (a-z)? [Y/n]: ").strip().lower() != 'n'
        use_digits = input("Include Numbers (0-9)? [Y/n]: ").strip().lower() != 'n'
        use_symbols = input("Include Special Symbols? [Y/n]: ").strip().lower() != 'n'
        exclude_ambiguous = input("Exclude Ambiguous Characters (0, O, l, I, 1)? [y/N]: ").strip().lower() == 'y'

    try:
        pwd = generate_secure_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)
        score, label, _, _ = evaluate_password_strength(pwd)
        print("\n" + "=" * 60)
        print("OASIS INFOBYTE — GENERATED PASSWORD")
        print("=" * 60)
        print(f"Password:        {pwd}")
        print(f"Security Rating: {label}")
        print(f"Length:          {len(pwd)} characters")
        print("=" * 60)

        if PYPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(pwd)
                print("✓ Copied to system clipboard via pyperclip.")
            except Exception:
                pass
    except Exception as err:
        print(f"\nError: {err}")


def main():
    """
    Main application entry point.
    Initializes Tkinter GUI when display is available; falls back to CLI otherwise.
    """
    if "--cli" in sys.argv or "-c" in sys.argv:
        run_cli_mode()
        return

    if not TKINTER_AVAILABLE:
        print("Notice: Tkinter GUI module not found. Launching CLI mode...")
        run_cli_mode()
        return

    try:
        root = tk.Tk()
        app = PasswordGeneratorApp(root)
        root.mainloop()
    except tk.TclError as err:
        # Fallback when running in headless environments with no DISPLAY set
        print(f"Notice: Graphical display not detected ({err}). Launching CLI mode...\n")
        run_cli_mode()


if __name__ == "__main__":
    main()
