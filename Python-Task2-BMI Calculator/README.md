# OASIS INFOBYTE Python Programming Internship
## Task 2: Advanced BMI Calculator (Python Desktop Application)

An advanced, clinical-grade **Body Mass Index (BMI) Calculator** built using **Python 3**, **Tkinter**, **SQLite3**, and **Matplotlib**. 

This application fulfills all the core and advanced requirements of **Task 2 (BMI Calculator)** for the **OASIS INFOBYTE Python Programming Internship**, providing a clean graphical user interface, named user profiles, persistent SQLite database storage, chronological history management, and longitudinal trend visualizations.

---

## 📌 Project Overview

- **Internship Domain**: Python Programming Internship
- **Organization**: OASIS INFOBYTE
- **Task Number**: Task 2 — Advanced Version
- **Application Type**: Native Python Desktop Graphical User Interface (GUI)
- **Primary Script**: `bmi_calculator.py`
- **Database Engine**: `database.py` (Local SQLite3)

---

## 🌟 Key Features

1. **Precision BMI Assessment**:
   - Calculates Body Mass Index using the standard Quetelet formula ($BMI = \text{weight (kg)} / \text{height (m)}^2$).
   - Automatically rounds calculated BMI to **2 decimal places**.
   - Classifies scores into official **World Health Organization (WHO)** categories with distinct color-coded visual badges.
   - Calculates the **Healthy Weight Range** for the user's specific height.

2. **Named User Management**:
   - Users can type a new name or select existing profiles from a dropdown combobox.
   - Every measurement is linked to the user's name in SQLite.
   - Filtering and instant history recall for any selected user.

3. **Persistent Local SQLite Storage**:
   - Automatically initializes a local database (`bmi_calculator.db`) on startup.
   - Stores user name, weight (kg), height (m), BMI value, category, and timestamps (`YYYY-MM-DD HH:MM:SS`).
   - Uses parameterized queries (`?`) to prevent SQL injection and ensure ACID compliance via Write-Ahead Logging (WAL).

4. **Chronological Measurement History**:
   - Clean `ttk.Treeview` table displaying historical records.
   - Filter records by specific user or view all database entries.
   - Ability to select and delete individual records.
   - Option to clear all records for a selected user with confirmation dialogs.
   - **CSV Export**: Export filtered or complete health records to standard `.csv` spreadsheets.

5. **Embedded Matplotlib Trend Chart**:
   - Native interactive trend graph embedded directly into Tkinter via `FigureCanvasTkAgg`.
   - Displays historical BMI trajectory with date on the X-axis and BMI on the Y-axis.
   - Shaded WHO benchmark zones:
     - **Blue**: Underweight ($< 18.5$)
     - **Green**: Normal weight ($18.5 – 24.9$)
     - **Orange**: Overweight ($25.0 – 29.9$)
     - **Red**: Obesity ($\ge 30.0$)
   - Displays data point annotations showing exact BMI and weight.
   - Gracefully handles users with fewer than 2 measurements with clear guidance.

6. **Robust Input Validation & Error Handling**:
   - Checks for empty name, weight, and height fields.
   - Validates that weight and height are positive, non-zero numeric values.
   - Realistic bounds checking:
     - Detects when height is mistakenly entered in centimeters (e.g., $175$ instead of $1.75$).
     - Enforces adult realistic limits ($10 - 500\text{ kg}$, $0.50 - 2.80\text{ m}$).
   - Displays clear `tkinter.messagebox` alerts without crashing.
   - Wraps database connections in `try...except sqlite3.Error` blocks.

7. **Dual Mode Execution**:
   - Default: Native Tkinter Graphical Desktop Application.
   - Headless / Terminal Fallback: Automatically launches in interactive CLI mode if running in a headless Linux environment where `$DISPLAY` is unset, or when run with `--cli`.

---

## 🛠️ Technologies Used

| Technology | Role & Category | Standard Library / External |
| :--- | :--- | :--- |
| **Python 3.10+** | Core Programming Language | Standard |
| **Tkinter (`tkinter`, `ttk`)** | Graphical User Interface (GUI) | Python Standard Library |
| **SQLite3 (`sqlite3`)** | Persistent Relational Database | Python Standard Library |
| **Matplotlib** | Longitudinal Data Visualization & Plotting | External (`requirements.txt`) |
| **Unittest (`unittest`)** | Automated Unit Testing Framework | Python Standard Library |

---

## 📐 BMI Formula & Calculation

The Body Mass Index is calculated using the international standard formula:

$$\text{BMI} = \frac{\text{Weight (kg)}}{[\text{Height (m)}]^2}$$

### Calculation Example:
- **User**: John
- **Weight**: $70.0\text{ kg}$
- **Height**: $1.75\text{ m}$
- **Calculation**: $\frac{70.0}{1.75^2} = \frac{70.0}{3.0625} \approx 22.8571$
- **Displayed Result**: **`BMI: 22.86`** (Rounded to 2 decimal places)

---

## 📊 Standard BMI Categories

The application classifies BMI using official World Health Organization (WHO) benchmarks:

| Category | BMI Range ($kg/m^2$) | Visual Color Code | Health Implication |
| :--- | :--- | :--- | :--- |
| **Underweight** | $< 18.5$ | Blue (`#1976D2`) | Below healthy weight baseline |
| **Normal weight** | $18.5 – 24.9$ | Green (`#2E7D32`) | Optimal healthy weight range |
| **Overweight** | $25.0 – 29.9$ | Orange (`#ED6C02`) | Above optimal range |
| **Obesity** | $\ge 30.0$ | Red (`#D32F2F`) | Elevated health risk |

---

## 📥 Installation & Setup Instructions

### Prerequisites
- Ensure **Python 3.10** or higher is installed on your computer.
- You can verify your Python version by running:
  ```bash
  python --version
  # or
  python3 --version
  ```

### Step 1: Clone or Download the Repository
```bash
git clone https://github.com/<your-username>/Python-Task2-BMICalculator.git
cd Python-Task2-BMICalculator
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the single external dependency (`matplotlib`):
```bash
python -m pip install -r requirements.txt
```
*(Note: `tkinter`, `sqlite3`, and `unittest` are built into Python's standard library.)*

---

## 🚀 How to Run the Application

### 1. Run the Desktop GUI Application
```bash
python bmi_calculator.py
# or on macOS/Linux:
python3 bmi_calculator.py
```

### 2. Run in Terminal CLI Mode (Headless / Optional)
To run the interactive command-line interface directly in your terminal:
```bash
python bmi_calculator.py --cli
```

### 3. Run Web / Cloud Sandbox Preview
To launch the interactive Python HTTP server (configured for cloud sandbox and browser previews):
```bash
python server.py
# Server listens on port 3000 (http://localhost:3000)
```

### 4. Run Automated Unit Tests
To verify all formulas, boundary categories, input validators, and SQLite CRUD operations:
```bash
python -m unittest test_bmi.py
```

---

## 🗄️ Database Architecture

The application uses an embedded SQLite database named **`bmi_calculator.db`**, managed through `database.py`.

### Schema (`records` table):
```sql
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    weight REAL NOT NULL,
    height REAL NOT NULL,
    bmi REAL NOT NULL,
    category TEXT NOT NULL,
    date_time TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_user_name ON records(user_name);
CREATE INDEX IF NOT EXISTS idx_date_time ON records(date_time);
```

- **Local & Private**: No cloud credentials, tokens, or external servers are involved.
- **Safety**: Uses parameterized SQL statements (`?`) to prevent syntax errors and injection vulnerabilities.
- **Auto-Initialization**: The database and demonstration records are created automatically on the very first run.

---

## 📈 BMI Trend Chart Information

- Embedded directly into the Tkinter window using `FigureCanvasTkAgg`.
- Dynamic shaded horizontal bands identify **Underweight**, **Normal weight**, **Overweight**, and **Obesity** zones.
- Points are plotted with chronological timestamps, formatted date markers, and exact BMI values.
- Automatically refreshes whenever a new calculation is saved or when switching between users.
- If fewer than 2 records are present for a user, a helpful message guides the user to record additional measurements.

---

## 🛡️ Input Validation & Error Handling

| Scenario | Handled Condition | User Feedback |
| :--- | :--- | :--- |
| **Empty Name** | User leaves name blank | Warning Dialog: *"Please enter or select a user name."* |
| **Empty Weight** | User leaves weight blank | Warning Dialog: *"Please enter weight in kilograms (kg)."* |
| **Empty Height** | User leaves height blank | Warning Dialog: *"Please enter height in meters (m)."* |
| **Non-Numeric Input** | Text entered in weight/height | Error Dialog: *"Weight/Height must be a valid numeric number."* |
| **Zero or Negative** | Value $\le 0$ | Error Dialog: *"Value must be strictly greater than zero."* |
| **Height in Centimeters** | Value $> 3.0$ (e.g., $175$) | Warning Dialog explaining height must be in meters ($1.75\text{ m}$). |
| **Unrealistic Values** | Outside $10-500\text{ kg}$ or $0.5-2.8\text{ m}$ | Warning Dialog for realistic physiological bounds. |
| **Database Failure** | I/O lock or missing table | Error Dialog with exact diagnostic without crashing the GUI. |

---

## ⚠️ Medical Disclaimer

> **Disclaimer**: The Body Mass Index (BMI) calculation and classification provided by this software are intended strictly as a **general screening indicator** and educational tool. BMI does not directly measure body fat percentage, muscle mass, bone density, or metabolic health. It does not replace professional medical advice, clinical diagnosis, or personalized treatment by a physician or registered dietitian.

---

## 📸 Screenshots & User Interface Layout

```text
+---------------------------------------------------------------------------------------------+
|  OASIS INFOBYTE — Task 2: BMI Calculator (Advanced)                    Python 3 & Tkinter   |
|  Python Desktop Application • Multi-User SQLite Storage • Matplotlib Trend Analysis         |
+---------------------------------------------------------------------------------------------+
| [ Left Panel: Form & Results ]              | [ Right Panel: History Log & Trend Graph ]    |
|                                             |                                               |
| User Name: [ John                     |v]   |  [ BMI Measurement History ] [ Trend Chart ]  |
|                                             |  -------------------------------------------  |
| Weight (kg): [ 70.0                     ]   |  Filter by User: [ All Users         |v]      |
| Height (m):  [ 1.75                     ]   |  [ Refresh ] [ Export CSV ] [ Delete Record ] |
|                                             |                                               |
| [ Calculate BMI ]    [ Clear / Reset ]      |  ID  | Date / Time         | Weight | BMI   | |
|                                             |  #1  | 2026-08-30 09:10:00 | 72.0kg | 23.51 | |
| ------------------------------------------- |  #2  | 2026-07-25 08:45:00 | 73.8kg | 24.10 | |
| Assessment Result:                          |  #3  | 2026-06-20 08:15:00 | 75.2kg | 24.56 | |
|                                             |                                               |
|               BMI: 22.86                    |  [ Embedded Matplotlib Trend Canvas ]         |
|         Category: Normal weight             |   BMI ^                                       |
|                                             |    30 | - - - - - - - - - - (Obesity Zone)    |
| Healthy weight range for 1.75m:             |    25 | - - - - - - - - - - (Overweight Zone) |
| 56.7 kg – 76.3 kg                           |    20 |     *-------*                         |
|                                             |       +----------------------------> Date     |
+---------------------------------------------------------------------------------------------+
| Connected to local SQLite database (bmi_calculator.db) • Ready                              |
+---------------------------------------------------------------------------------------------+
```

---

## 📁 Repository Structure

```text
Python-Task2-BMICalculator/
│
├── bmi_calculator.py    # Main Tkinter Desktop Application & CLI Fallback
├── database.py          # SQLite database connection, table schemas & CRUD methods
├── server.py            # Python HTTP server for cloud sandbox & interactive preview
├── test_bmi.py          # Automated unit test suite (13 test cases)
├── requirements.txt     # External dependencies (matplotlib)
├── README.md            # Comprehensive project documentation
└── bmi_calculator.db    # Local SQLite database file (created automatically)
```

---

## 📜 License

This project is developed for the **OASIS INFOBYTE Internship** and is distributed under the **MIT License**.
