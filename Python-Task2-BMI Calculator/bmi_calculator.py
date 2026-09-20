"""
OASIS INFOBYTE Python Programming Internship
Task 2: BMI Calculator (Advanced Version)
Main Script: bmi_calculator.py

Features:
- Tkinter Desktop Graphical User Interface (GUI)
- Standard Quetelet BMI Formula: BMI = weight (kg) / height (m)^2
- Official WHO Categorization (Underweight, Normal weight, Overweight, Obesity)
- Named User Profiles with instant history recall
- Local SQLite Database Storage (auto-created via database.py)
- Historical Measurements Log (filterable, sortable, with deletion & CSV export)
- Embedded Matplotlib BMI Longitudinal Trend Graph with WHO Benchmark Bands
- Rigorous Input Validation & SQLite Error Handling
- Terminal CLI Fallback for headless environments
- Medical Disclaimer Notice
"""

import os
import sys
import csv
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

# Local SQLite Database Manager
from database import DatabaseManager


# ==============================================================================
# 1. CORE CALCULATION & CLASSIFICATION LOGIC
# ==============================================================================

def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculates Body Mass Index (BMI).
    Formula: weight (kg) / (height (m) ^ 2)
    Returns: Rounded to 2 decimal places.
    """
    if height_m <= 0:
        raise ValueError("Height must be strictly positive.")
    if weight_kg <= 0:
        raise ValueError("Weight must be strictly positive.")
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def classify_bmi(bmi: float) -> str:
    """
    Classifies a BMI value according to standard World Health Organization criteria:
    - Underweight: BMI < 18.5
    - Normal weight: 18.5 <= BMI <= 24.9
    - Overweight: 25.0 <= BMI <= 29.9
    - Obesity: BMI >= 30.0
    """
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi <= 24.9:
        return "Normal weight"
    elif 25.0 <= bmi <= 29.9:
        return "Overweight"
    else:
        return "Obesity"


def get_category_color(category: str) -> str:
    """Returns color hex codes corresponding to clinical categories."""
    colors = {
        "Underweight": "#1976D2",    # Calming Blue
        "Normal weight": "#2E7D32",  # Healthy Green
        "Overweight": "#ED6C02",     # Caution Orange
        "Obesity": "#D32F2F",        # Alert Red
    }
    return colors.get(category, "#45464D")


def calculate_healthy_weight_range(height_m: float) -> Tuple[float, float]:
    """
    Calculates the healthy weight range (BMI 18.5 to 24.9) for a given height in meters.
    Returns: (min_weight_kg, max_weight_kg)
    """
    min_weight = round(18.5 * (height_m ** 2), 1)
    max_weight = round(24.9 * (height_m ** 2), 1)
    return min_weight, max_weight


def validate_user_inputs(name: str, weight_str: str, height_str: str) -> Tuple[bool, Optional[Tuple[str, float, float]], Optional[str]]:
    """
    Validates user input fields.
    Returns: (is_valid, (name, weight, height), error_message)
    """
    clean_name = name.strip()
    if not clean_name:
        return False, None, "Please enter or select a user name."

    clean_weight = weight_str.strip()
    if not clean_weight:
        return False, None, "Please enter weight in kilograms (kg)."

    clean_height = height_str.strip()
    if not clean_height:
        return False, None, "Please enter height in meters (m)."

    try:
        weight = float(clean_weight)
    except ValueError:
        return False, None, "Weight must be a valid numeric number (e.g., 70.5)."

    try:
        height = float(clean_height)
    except ValueError:
        return False, None, "Height must be a valid numeric number (e.g., 1.75)."

    if weight <= 0:
        return False, None, "Weight must be strictly greater than zero."

    if height <= 0:
        return False, None, "Height must be strictly greater than zero."

    # Helpful bounds checking
    if height > 3.0:
        return False, None, (
            f"Height entered is {height}. Height must be in meters (e.g., 1.75 for 175 cm).\n"
            "Realistic adult height is between 0.50 m and 2.80 m."
        )

    if height < 0.50:
        return False, None, "Height entered is too low. Please enter a height between 0.50 m and 2.80 m."

    if weight < 10.0 or weight > 500.0:
        return False, None, "Weight must be between 10 kg and 500 kg for a realistic assessment."

    return True, (clean_name, weight, height), None


# ==============================================================================
# 2. TKINTER GUI APPLICATION
# ==============================================================================

def run_gui():
    """Launches the Tkinter GUI Desktop Application."""
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog

    # Matplotlib integration
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates

    class BMICalculatorGUI:
        def __init__(self, root: tk.Tk):
            self.root = root
            self.root.title("OASIS INFOBYTE — Task 2: Advanced BMI Calculator")
            self.root.geometry("1100 biographicalx720".replace("biographical", ""))
            self.root.geometry("1080x720")
            self.root.minsize(980, 640)

            # Initialize Database
            self.db = DatabaseManager("bmi_calculator.db")
            self.db.seed_demo_data()

            # State
            self.current_user_name = tk.StringVar(value="")
            self.weight_var = tk.StringVar(value="")
            self.height_var = tk.StringVar(value="")
            self.selected_filter_user = tk.StringVar(value="All Users")

            # Configure Theme & Styling
            self._setup_styles()

            # Build UI Layout
            self._create_header()
            self._create_main_content()
            self._create_footer_status()

            # Populate initial data
            self.refresh_user_dropdowns()
            self.load_history_table()
            self.update_trend_chart()

        def _setup_styles(self):
            """Sets up ttk styles with a clean, professional aesthetic."""
            self.style = ttk.Style()
            try:
                self.style.theme_use("clam")
            except Exception:
                pass

            self.root.configure(bg="#F4F6F9")

            # Custom colors
            self.style.configure(".", background="#F4F6F9", foreground="#1A1C1E")
            self.style.configure("TLabel", background="#F4F6F9", font=("Helvetica", 10))
            self.style.configure("TFrame", background="#F4F6F9")
            self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
            
            # Header
            self.style.configure("Header.TFrame", background="#0B1C30")
            self.style.configure("HeaderTitle.TLabel", background="#0B1C30", foreground="#FFFFFF", font=("Helvetica", 16, "bold"))
            self.style.configure("HeaderSubtitle.TLabel", background="#0B1C30", foreground="#86F2E4", font=("Helvetica", 9))

            # Buttons
            self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"), background="#006A61", foreground="#FFFFFF")
            self.style.map("Accent.TButton", background=[("active", "#00534C"), ("pressed", "#003E39")])

            self.style.configure("Secondary.TButton", font=("Helvetica", 10), background="#E0E2EC", foreground="#1A1C1E")
            self.style.map("Secondary.TButton", background=[("active", "#D0D3DE")])

            self.style.configure("Danger.TButton", font=("Helvetica", 9), background="#FFDAD6", foreground="#BA1A1A")

            # Treeview Styling
            self.style.configure(
                "Treeview",
                background="#FFFFFF",
                foreground="#1A1C1E",
                rowheight=26,
                fieldbackground="#FFFFFF",
                font=("Helvetica", 9),
            )
            self.style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"), background="#E7ECF3", foreground="#0B1C30")
            self.style.map("Treeview", background=[("selected", "#006A61")], foreground=[("selected", "#FFFFFF")])

        def _create_header(self):
            """Creates the top application banner."""
            header = ttk.Frame(self.root, style="Header.TFrame", padding=(20, 12))
            header.pack(fill=tk.X, side=tk.TOP)

            title_box = ttk.Frame(header, style="Header.TFrame")
            title_box.pack(side=tk.LEFT)

            ttk.Label(title_box, text="OASIS INFOBYTE — Task 2: BMI Calculator (Advanced)", style="HeaderTitle.TLabel").pack(anchor="w")
            ttk.Label(title_box, text="Python Desktop Application • Multi-User SQLite Storage • Matplotlib Trend Analysis", style="HeaderSubtitle.TLabel").pack(anchor="w")

            badge = tk.Label(header, text="Python 3.10+ & Tkinter", bg="#006A61", fg="#FFFFFF", font=("Helvetica", 9, "bold"), padx=10, pady=4)
            badge.pack(side=tk.RIGHT)

        def _create_main_content(self):
            """Creates the split main content layout (Left: Input & Result; Right: History & Charts)."""
            main_container = ttk.Frame(self.root, padding=16)
            main_container.pack(fill=tk.BOTH, expand=True)

            # Left Panel: Input Form & Results (Width ~ 380px)
            left_panel = tk.Frame(main_container, bg="#FFFFFF", bd=1, relief="solid", highlightbackground="#DCE2EA", padx=18, pady=16)
            left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))

            self._build_input_section(left_panel)
            self._build_result_section(left_panel)

            # Right Panel: Tabs for History and Trends
            right_panel = ttk.Frame(main_container)
            right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            self.notebook = ttk.Notebook(right_panel)
            self.notebook.pack(fill=tk.BOTH, expand=True)

            # Tab 1: History Log Table
            self.history_tab = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(self.history_tab, text="  BMI Measurement History  ")
            self._build_history_tab()

            # Tab 2: Matplotlib Trend Chart
            self.trend_tab = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(self.trend_tab, text="  BMI Longitudinal Trend Chart  ")
            self._build_trend_tab()

        def _build_input_section(self, parent: tk.Widget):
            """Builds the input fields for name, weight, and height."""
            title_label = tk.Label(parent, text="User & Measurements", bg="#FFFFFF", fg="#0B1C30", font=("Helvetica", 12, "bold"))
            title_label.pack(anchor="w", pady=(0, 12))

            # User Name Field
            tk.Label(parent, text="User Name:", bg="#FFFFFF", fg="#45464D", font=("Helvetica", 9, "bold")).pack(anchor="w")
            self.user_combo = ttk.Combobox(parent, textvariable=self.current_user_name, font=("Helvetica", 10))
            self.user_combo.pack(fill=tk.X, pady=(2, 10))
            self.user_combo.bind("<<ComboboxSelected>>", self._on_user_selected)

            # Weight Field
            tk.Label(parent, text="Weight in Kilograms (kg):", bg="#FFFFFF", fg="#45464D", font=("Helvetica", 9, "bold")).pack(anchor="w")
            weight_entry = ttk.Entry(parent, textvariable=self.weight_var, font=("Helvetica", 10))
            weight_entry.pack(fill=tk.X, pady=(2, 10))

            # Height Field
            tk.Label(parent, text="Height in Meters (m):", bg="#FFFFFF", fg="#45464D", font=("Helvetica", 9, "bold")).pack(anchor="w")
            height_entry = ttk.Entry(parent, textvariable=self.height_var, font=("Helvetica", 10))
            height_entry.pack(fill=tk.X, pady=(2, 4))

            hint = tk.Label(parent, text="e.g., 70.5 kg and 1.75 m (175 cm = 1.75 m)", bg="#FFFFFF", fg="#76777D", font=("Helvetica", 8, "italic"))
            hint.pack(anchor="w", pady=(0, 14))

            # Action Buttons
            btn_frame = ttk.Frame(parent)
            btn_frame.pack(fill=tk.X, pady=(0, 16))

            calc_btn = ttk.Button(btn_frame, text="Calculate BMI", style="Accent.TButton", command=self.on_calculate)
            calc_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

            clear_btn = ttk.Button(btn_frame, text="Clear", style="Secondary.TButton", command=self.on_clear)
            clear_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        def _build_result_section(self, parent: tk.Widget):
            """Builds the display area for BMI results, category, and disclaimer."""
            result_frame = tk.LabelFrame(parent, text="  BMI Assessment Result  ", bg="#F8F9FB", fg="#0B1C30", font=("Helvetica", 10, "bold"), padx=12, pady=12)
            result_frame.pack(fill=tk.X, pady=(0, 12))

            # Big BMI Display
            self.bmi_display_label = tk.Label(result_frame, text="BMI: --.--", bg="#F8F9FB", fg="#0B1C30", font=("Helvetica", 20, "bold"))
            self.bmi_display_label.pack(anchor="center", pady=(4, 4))

            # Category Display Badge
            self.category_badge = tk.Label(result_frame, text="Category: Awaiting calculation", bg="#E0E2EC", fg="#1A1C1E", font=("Helvetica", 10, "bold"), padx=10, pady=4)
            self.category_badge.pack(anchor="center", pady=(2, 6))

            # Healthy Weight Range
            self.range_info_label = tk.Label(result_frame, text="Healthy weight range for height: --", bg="#F8F9FB", fg="#45464D", font=("Helvetica", 8))
            self.range_info_label.pack(anchor="center", pady=(2, 4))

            # Reference Table
            ref_box = tk.LabelFrame(parent, text="  WHO BMI Reference  ", bg="#FFFFFF", fg="#45464D", font=("Helvetica", 8, "bold"), padx=8, pady=6)
            ref_box.pack(fill=tk.X, pady=(0, 12))

            ref_text = (
                "• Underweight:   < 18.5\n"
                "• Normal weight: 18.5 – 24.9\n"
                "• Overweight:    25.0 – 29.9\n"
                "• Obesity:       ≥ 30.0"
            )
            tk.Label(ref_box, text=ref_text, bg="#FFFFFF", fg="#45464D", font=("Courier", 8), justify=tk.LEFT).pack(anchor="w")

            # Medical Disclaimer
            disclaimer = tk.Label(
                parent,
                text="Medical Disclaimer:\nBMI is a general screening indicator and does not replace medical diagnosis, clinical evaluation, or professional healthcare advice.",
                bg="#FFFFFF",
                fg="#76777D",
                font=("Helvetica", 7, "italic"),
                justify=tk.LEFT,
                wraplength=280,
            )
            disclaimer.pack(anchor="w", side=tk.BOTTOM)

        def _build_history_tab(self):
            """Builds the table view for previous measurements."""
            controls_frame = ttk.Frame(self.history_tab)
            controls_frame.pack(fill=tk.X, pady=(0, 8))

            ttk.Label(controls_frame, text="Filter by User:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
            self.filter_combo = ttk.Combobox(controls_frame, textvariable=self.selected_filter_user, state="readonly", width=18)
            self.filter_combo.pack(side=tk.LEFT, padx=(0, 10))
            self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_history_table())

            refresh_btn = ttk.Button(controls_frame, text="Refresh", command=self.load_history_table)
            refresh_btn.pack(side=tk.LEFT, padx=(0, 6))

            export_btn = ttk.Button(controls_frame, text="Export CSV", command=self.export_csv)
            export_btn.pack(side=tk.LEFT, padx=(0, 6))

            delete_btn = ttk.Button(controls_frame, text="Delete Selected", style="Danger.TButton", command=self.delete_selected_record)
            delete_btn.pack(side=tk.RIGHT, padx=(6, 0))

            clear_user_btn = ttk.Button(controls_frame, text="Clear User History", command=self.clear_user_history)
            clear_user_btn.pack(side=tk.RIGHT)

            # Treeview Table
            table_frame = ttk.Frame(self.history_tab)
            table_frame.pack(fill=tk.BOTH, expand=True)

            columns = ("id", "date_time", "user_name", "weight", "height", "bmi", "category")
            self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

            self.tree.heading("id", text="# ID")
            self.tree.heading("date_time", text="Date / Time")
            self.tree.heading("user_name", text="User Name")
            self.tree.heading("weight", text="Weight (kg)")
            self.tree.heading("height", text="Height (m)")
            self.tree.heading("bmi", text="BMI Value")
            self.tree.heading("category", text="Category")

            self.tree.column("id", width=45, anchor="center")
            self.tree.column("date_time", width=140, anchor="center")
            self.tree.column("user_name", width=110, anchor="w")
            self.tree.column("weight", width=85, anchor="center")
            self.tree.column("height", width=85, anchor="center")
            self.tree.column("bmi", width=85, anchor="center")
            self.tree.column("category", width=120, anchor="center")

            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
            self.tree.configure(yscroll=scrollbar.set)

            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _build_trend_tab(self):
            """Builds the embedded Matplotlib figure canvas for trend tracking."""
            top_bar = ttk.Frame(self.trend_tab)
            top_bar.pack(fill=tk.X, pady=(0, 6))

            ttk.Label(top_bar, text="Viewing Longitudinal Trend for:", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
            self.chart_user_label = ttk.Label(top_bar, text="(Select a user to view trend)", font=("Helvetica", 9, "italic"), foreground="#006A61")
            self.chart_user_label.pack(side=tk.LEFT)

            refresh_chart_btn = ttk.Button(top_bar, text="Update Chart", command=self.update_trend_chart)
            refresh_chart_btn.pack(side=tk.RIGHT)

            # Matplotlib Figure
            self.figure = Figure(figsize=(6.5, 4.2), dpi=100)
            self.figure.patch.set_facecolor("#FFFFFF")
            self.ax = self.figure.add_subplot(111)

            self.canvas = FigureCanvasTkAgg(self.figure, master=self.trend_tab)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        def _create_footer_status(self):
            """Creates the bottom status bar."""
            self.status_bar = tk.Label(
                self.root,
                text="Connected to local SQLite database (bmi_calculator.db) • Ready",
                bg="#E0E2EC",
                fg="#45464D",
                font=("Helvetica", 8),
                anchor="w",
                padx=12,
                pady=4,
            )
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # ----------------------------------------------------------------------
        # Event Handlers & Actions
        # ----------------------------------------------------------------------

        def on_calculate(self):
            """Validates inputs, calculates BMI, stores in SQLite, updates table & graph."""
            name = self.current_user_name.get()
            weight_str = self.weight_var.get()
            height_str = self.height_var.get()

            is_valid, data, error_msg = validate_user_inputs(name, weight_str, height_str)
            if not is_valid:
                messagebox.showerror("Input Validation Error", error_msg)
                return

            clean_name, weight, height = data
            bmi = calculate_bmi(weight, height)
            category = classify_bmi(bmi)

            # Save to SQLite
            try:
                record_id = self.db.insert_record(clean_name, weight, height, bmi, category)
                self.status_bar.config(text=f"Record #{record_id} successfully saved for {clean_name} at {datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save record to SQLite database:\n{e}")
                return

            # Update Result Display
            self.bmi_display_label.config(text=f"BMI: {bmi:.2f}")
            color = get_category_color(category)
            self.category_badge.config(text=f"Category: {category}", bg=color, fg="#FFFFFF")

            min_w, max_w = calculate_healthy_weight_range(height)
            self.range_info_label.config(text=f"Healthy weight range for {height:.2f} m: {min_w} kg – {max_w} kg")

            # Refresh UI elements
            self.refresh_user_dropdowns(keep_user=clean_name)
            self.load_history_table()
            self.update_trend_chart(user_name=clean_name)

            messagebox.showinfo(
                "Calculation Complete",
                f"User: {clean_name}\n"
                f"Weight: {weight:.1f} kg | Height: {height:.2f} m\n\n"
                f"BMI: {bmi:.2f}\n"
                f"Category: {category}\n\n"
                f"Record #{record_id} saved to database."
            )

        def on_clear(self):
            """Resets input fields and result labels."""
            self.weight_var.set("")
            self.height_var.set("")
            self.bmi_display_label.config(text="BMI: --.--")
            self.category_badge.config(text="Category: Awaiting calculation", bg="#E0E2EC", fg="#1A1C1E")
            self.range_info_label.config(text="Healthy weight range for height: --")
            self.status_bar.config(text="Input fields cleared.")

        def _on_user_selected(self, event=None):
            """Triggered when a user is selected from the combobox."""
            selected = self.current_user_name.get().strip()
            if selected:
                self.selected_filter_user.set(selected)
                self.load_history_table()
                self.update_trend_chart(user_name=selected)

        def refresh_user_dropdowns(self, keep_user: Optional[str] = None):
            """Refreshes the user lists in comboboxes from the database."""
            users = self.db.get_all_users()
            self.user_combo["values"] = users
            self.filter_combo["values"] = ["All Users"] + users

            if keep_user and keep_user in users:
                self.current_user_name.set(keep_user)
                self.selected_filter_user.set(keep_user)
            elif users and not self.current_user_name.get():
                self.current_user_name.set(users[0])
                self.selected_filter_user.set("All Users")

        def load_history_table(self):
            """Loads and displays records in the Treeview table based on the selected user filter."""
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            filter_user = self.selected_filter_user.get()
            if filter_user == "All Users" or not filter_user:
                records = self.db.get_all_records()
            else:
                records = self.db.get_user_records(filter_user)
                # Reverse to show newest first in table
                records = list(reversed(records))

            for r in records:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        r["id"],
                        r["date_time"],
                        r["user_name"],
                        f"{r['weight']:.1f}",
                        f"{r['height']:.2f}",
                        f"{r['bmi']:.2f}",
                        r["category"],
                    ),
                )

            count = len(records)
            self.status_bar.config(text=f"Displaying {count} record(s) for filter: '{filter_user}'.")

        def update_trend_chart(self, user_name: Optional[str] = None):
            """Renders the BMI trajectory graph for the selected user using Matplotlib."""
            target_user = user_name or self.current_user_name.get().strip()
            if not target_user:
                users = self.db.get_all_users()
                if users:
                    target_user = users[0]
                    self.current_user_name.set(target_user)

            self.ax.clear()
            self.ax.set_facecolor("#FFFFFF")

            if not target_user:
                self.chart_user_label.config(text="No users available")
                self.ax.text(0.5, 0.5, "No BMI history records found in database.\nCalculate a measurement to view trends.", ha="center", va="center", color="#76777D", fontsize=11, transform=self.ax.transAxes)
                self.canvas.draw()
                return

            self.chart_user_label.config(text=f"User: {target_user}")
            records = self.db.get_user_records(target_user)

            # Threshold bands
            self.ax.axhspan(10, 18.5, color="#E3F2FD", alpha=0.6, label="Underweight (< 18.5)")
            self.ax.axhspan(18.5, 24.9, color="#E8F5E9", alpha=0.6, label="Normal weight (18.5–24.9)")
            self.ax.axhspan(25.0, 29.9, color="#FFF3E0", alpha=0.6, label="Overweight (25.0–29.9)")
            self.ax.axhspan(30.0, 45.0, color="#FFEBEE", alpha=0.6, label="Obesity (≥ 30.0)")

            if len(records) < 2:
                # Handle case with not enough history
                if len(records) == 1:
                    r = records[0]
                    try:
                        dt = datetime.strptime(r["date_time"], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        dt = datetime.now()
                    self.ax.plot([dt], [r["bmi"]], marker="o", color="#006A61", markersize=8, label="Initial Measurement")
                    self.ax.text(0.5, 0.85, f"1 record for {target_user} (BMI: {r['bmi']:.2f})\nAdd at least 2 measurements to plot a continuous trajectory.", ha="center", va="center", color="#0B1C30", fontsize=10, transform=self.ax.transAxes, bbox=dict(boxstyle="round,pad=0.5", facecolor="#EFF4FF", edgecolor="#006A61"))
                else:
                    self.ax.text(0.5, 0.5, f"No previous records found for '{target_user}'.\nCalculate a BMI measurement above to start tracking.", ha="center", va="center", color="#76777D", fontsize=11, transform=self.ax.transAxes)

                self.ax.set_ylim(14, 38)
                self.ax.set_ylabel("BMI Value", fontsize=10, fontweight="bold", color="#0B1C30")
                self.ax.set_title(f"BMI History for {target_user}", fontsize=11, fontweight="bold", color="#0B1C30")
                self.ax.grid(True, linestyle="--", alpha=0.4)
                self.canvas.draw()
                return

            # Parse dates and BMIs
            dates = []
            bmis = []
            weights = []
            for r in records:
                try:
                    d = datetime.strptime(r["date_time"], "%Y-%m-%d %H:%M:%S")
                except Exception:
                    d = datetime.now()
                dates.append(d)
                bmis.append(r["bmi"])
                weights.append(r["weight"])

            # Plot continuous line with markers
            self.ax.plot(dates, bmis, marker="o", markersize=6, color="#006A61", linewidth=2.2, label=f"BMI ({target_user})")

            # Point value labels
            for d, b, w in zip(dates, bmis, weights):
                self.ax.annotate(
                    f"{b:.1f}\n({w:.0f}kg)",
                    xy=(d, b),
                    xytext=(0, 9),
                    textcoords="offset points",
                    ha="center",
                    fontsize=7.5,
                    fontweight="bold",
                    color="#0B1C30",
                )

            # Formatting
            self.ax.set_title(f"Longitudinal BMI Trend — {target_user} ({len(records)} measurements)", fontsize=11, fontweight="bold", color="#0B1C30")
            self.ax.set_xlabel("Date of Measurement", fontsize=9, fontweight="bold", color="#0B1C30")
            self.ax.set_ylabel("Body Mass Index (BMI)", fontsize=9, fontweight="bold", color="#0B1C30")
            
            # Format X Axis Dates
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%Y"))
            self.figure.autofmt_xdate(rotation=0, ha="center")

            # Dynamic Y limits with buffer
            min_y = max(12, min(bmis) - 3)
            max_y = min(46, max(bmis) + 4)
            self.ax.set_ylim(min_y, max_y)

            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.ax.legend(loc="upper left", fontsize=7.5, framealpha=0.8)
            self.figure.tight_layout()
            self.canvas.draw()

        def delete_selected_record(self):
            """Deletes the highlighted record from SQLite and refreshes."""
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please select a record from the table to delete.")
                return

            item_values = self.tree.item(selected[0], "values")
            record_id = int(item_values[0])
            user = item_values[2]
            date_time = item_values[1]

            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to permanently delete record #{record_id} for '{user}' taken on {date_time}?",
            )
            if confirm:
                if self.db.delete_record(record_id):
                    self.load_history_table()
                    self.update_trend_chart()
                    self.status_bar.config(text=f"Record #{record_id} deleted successfully.")
                else:
                    messagebox.showerror("Error", "Could not delete record from database.")

        def clear_user_history(self):
            """Clears all records for the currently filtered user."""
            user = self.selected_filter_user.get()
            if user == "All Users" or not user:
                messagebox.showwarning("Warning", "Please select a specific user from the 'Filter by User' dropdown to clear their history.")
                return

            confirm = messagebox.askyesno(
                "Clear History",
                f"Are you sure you want to delete ALL historical records for user '{user}'?\nThis action cannot be undone.",
            )
            if confirm:
                if self.db.clear_user_history(user):
                    self.refresh_user_dropdowns()
                    self.load_history_table()
                    self.update_trend_chart()
                    messagebox.showinfo("Success", f"All records for '{user}' have been cleared.")
                else:
                    messagebox.showerror("Error", f"Failed to clear history for '{user}'.")

        def export_csv(self):
            """Exports current filtered records to a standard CSV file."""
            filter_user = self.selected_filter_user.get()
            if filter_user == "All Users" or not filter_user:
                records = self.db.get_all_records()
                filename = "bmi_records_all.csv"
            else:
                records = self.db.get_user_records(filter_user)
                filename = f"bmi_records_{filter_user.lower()}.csv"

            if not records:
                messagebox.showinfo("Export Empty", "No records found to export.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=filename,
                filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")],
            )
            if not file_path:
                return

            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "User Name", "Weight (kg)", "Height (m)", "BMI", "Category", "Date Time"])
                    for r in records:
                        writer.writerow([r["id"], r["user_name"], r["weight"], r["height"], r["bmi"], r["category"], r["date_time"]])
                messagebox.showinfo("Export Successful", f"Exported {len(records)} records to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to write CSV file:\n{e}")

    # Launch GUI
    root = tk.Tk()
    app = BMICalculatorGUI(root)
    root.mainloop()


# ==============================================================================
# 3. INTERACTIVE TERMINAL CLI FALLBACK
# ==============================================================================

def run_cli():
    """Runs an interactive command-line interface when GUI display is unavailable."""
    print("=" * 65)
    print("  OASIS INFOBYTE — Task 2: Advanced BMI Calculator")
    print("  Terminal CLI Mode")
    print("=" * 65)

    db = DatabaseManager("bmi_calculator.db")
    db.seed_demo_data()

    while True:
        print("\n[Menu Options]")
        print("  1. Calculate & Save New BMI Record")
        print("  2. View User BMI History")
        print("  3. View All BMI Records")
        print("  4. List All Registered Users")
        print("  5. Exit")

        choice = input("\nSelect an option (1-5): ").strip()

        if choice == "1":
            print("\n--- Calculate New BMI ---")
            name = input("Enter User Name: ").strip()
            weight_str = input("Enter Weight in kg (e.g., 70.5): ").strip()
            height_str = input("Enter Height in meters (e.g., 1.75): ").strip()

            is_valid, data, err = validate_user_inputs(name, weight_str, height_str)
            if not is_valid:
                print(f"[Error] {err}")
                continue

            clean_name, weight, height = data
            bmi = calculate_bmi(weight, height)
            category = classify_bmi(bmi)

            try:
                rec_id = db.insert_record(clean_name, weight, height, bmi, category)
                min_w, max_w = calculate_healthy_weight_range(height)
                print("\n" + "=" * 45)
                print(f"  Result for:     {clean_name}")
                print(f"  Weight & Height: {weight:.1f} kg | {height:.2f} m")
                print(f"  BMI Value:      {bmi:.2f}")
                print(f"  WHO Category:   {category}")
                print(f"  Healthy Range:  {min_w} kg – {max_w} kg")
                print(f"  Database ID:    #{rec_id} (Saved to SQLite)")
                print("=" * 45)
            except Exception as e:
                print(f"[Database Error] {e}")

        elif choice == "2":
            users = db.get_all_users()
            if not users:
                print("\nNo records found in database.")
                continue
            print("\nAvailable Users:", ", ".join(users))
            target_user = input("Enter user name to view history: ").strip()
            records = db.get_user_records(target_user)
            if not records:
                print(f"No records found for '{target_user}'.")
            else:
                print(f"\n--- History for {target_user} ({len(records)} entries) ---")
                print(f"{'ID':<4} | {'Date / Time':<19} | {'Weight':<7} | {'Height':<7} | {'BMI':<6} | {'Category'}")
                print("-" * 65)
                for r in records:
                    print(f"{r['id']:<4} | {r['date_time']:<19} | {r['weight']:<7.1f} | {r['height']:<7.2f} | {r['bmi']:<6.2f} | {r['category']}")

        elif choice == "3":
            records = db.get_all_records()
            if not records:
                print("\nNo records in database.")
            else:
                print(f"\n--- All Database Records ({len(records)} total) ---")
                print(f"{'ID':<4} | {'Date / Time':<19} | {'User Name':<12} | {'Weight':<7} | {'Height':<7} | {'BMI':<6} | {'Category'}")
                print("-" * 75)
                for r in records:
                    print(f"{r['id']:<4} | {r['date_time']:<19} | {r['user_name']:<12} | {r['weight']:<7.1f} | {r['height']:<7.2f} | {r['bmi']:<6.2f} | {r['category']}")

        elif choice == "4":
            users = db.get_all_users()
            print("\nRegistered Users in SQLite:", users if users else "None")

        elif choice == "5":
            print("\nExiting BMI Calculator. Stay healthy!")
            break
        else:
            print("[Invalid Option] Please choose 1, 2, 3, 4, or 5.")


# ==============================================================================
# 4. ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Check if CLI mode explicitly requested via argument
    if "--cli" in sys.argv or "-c" in sys.argv:
        run_cli()
    else:
        try:
            # Check for graphical display availability
            run_gui()
        except Exception as e:
            err_str = str(e).lower()
            if "no display name" in err_str or "$display" in err_str or "couldn't connect to display" in err_str:
                print("[Notice] No graphical desktop display detected ($DISPLAY environment variable is unset).")
                print("Switching automatically to interactive Terminal CLI mode...\n")
                run_cli()
            else:
                raise e
