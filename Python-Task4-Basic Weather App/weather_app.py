"""
OASIS Infobyte Python Programming Internship — Task 4: Weather App (Advanced Tier)
Main Desktop GUI Application built with Python 3, Tkinter, and Pillow.

Features:
- Dual-mode Search: City name or ZIP / postal code
- Real-time Current Weather with high-res OpenWeatherMap icons (PIL)
- 6-to-12-Hour Timeline Forecast
- 5-Day Daily Outlook with min/max temperatures
- Dynamic Celsius (°C) / Fahrenheit (°F) unit toggling without reload
- Optional IP-based Geolocation ("Use My Location") via ipinfo.io
- Dedicated in-GUI status, error, and loading state indicators
- Multi-threaded network calls to ensure zero GUI stutter or freeze
"""

from __future__ import annotations

import os
import queue
import sys
import threading

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    tk = None
    messagebox = None
    ttk = None

# Local modular services
import config
from config import THEME, validate_api_key
from forecast_service import get_forecast_data
from icon_manager import get_weather_photo_image
from location_service import get_approximate_location
from weather_service import WeatherServiceError, get_current_weather


class WeatherDashboardApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(config.APP_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.root.configure(bg=THEME["bg_dark"])

        # State Variables
        self.current_unit = tk.StringVar(value="C")  # "C" or "F"
        self.search_query = tk.StringVar()
        self.is_fetching = False
        self.weather_cache: dict | None = None
        self.forecast_cache: dict | None = None
        self.event_queue = queue.Queue()

        # Build UI
        self._configure_styles()
        self._create_header()
        self._create_search_panel()
        self._create_status_banner()
        self._create_scrollable_content()
        self._create_footer()

        # Keyboard bindings
        self.root.bind("<Return>", lambda event: self.start_weather_fetch())
        self.root.bind("<Escape>", lambda event: self.clear_search())

        # Start thread-safe event queue polling
        self._schedule_queue_check()

        # Check API key presence at startup
        valid, msg = validate_api_key()
        if not valid:
            self.set_status(
                "Notice: API key is not configured in .env. Configure your API key to fetch live data.",
                status_type="warning",
            )
        else:
            self.set_status("Ready. Enter a city name (e.g. 'Hyderabad' or 'London, UK') or ZIP code.", "info")

    def _configure_styles(self):
        """Initializes modern ttk styles matching the dark desktop theme."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Card & Panel Frames
        self.style.configure(
            "Card.TFrame",
            background=THEME["bg_card"],
            relief="solid",
            borderwidth=1,
        )
        self.style.configure(
            "InnerCard.TFrame",
            background=THEME["bg_card_inner"],
            relief="flat",
        )
        self.style.configure(
            "Dark.TFrame",
            background=THEME["bg_dark"],
        )

        # Radio buttons for Unit Toggle
        self.style.configure(
            "Unit.TRadiobutton",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 10, "bold"),
            indicatorcolor=THEME["accent_blue"],
        )
        self.style.map(
            "Unit.TRadiobutton",
            background=[("active", THEME["bg_card"])],
            foreground=[("active", THEME["accent_blue"])],
        )

    def _create_header(self):
        """Creates the application header bar."""
        header_frame = tk.Frame(self.root, bg=THEME["bg_card"], padx=20, pady=14, relief="ridge", bd=1)
        header_frame.pack(fill="x", side="top")

        title_box = tk.Frame(header_frame, bg=THEME["bg_card"])
        title_box.pack(side="left")

        title_lbl = tk.Label(
            title_box,
            text="🌦 Weather Dashboard",
            font=("Segoe UI", 17, "bold"),
            fg=THEME["text_primary"],
            bg=THEME["bg_card"],
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            title_box,
            text="Real-time Weather Observations & Multi-day Forecast",
            font=("Segoe UI", 9),
            fg=THEME["accent_blue"],
            bg=THEME["bg_card"],
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Temperature Unit Toggle Frame on the Right
        unit_frame = tk.Frame(header_frame, bg=THEME["bg_card"])
        unit_frame.pack(side="right", fill="y")

        unit_label = tk.Label(
            unit_frame,
            text="Unit:",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["text_secondary"],
            bg=THEME["bg_card"],
        )
        unit_label.pack(side="left", padx=(0, 6))

        # Celsius / Fahrenheit Switch Button
        self.btn_unit_switch = tk.Button(
            unit_frame,
            text="⇄ Switch to °F",
            command=self.toggle_unit,
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card_inner"],
            fg=THEME["accent_blue"],
            activebackground=THEME["bg_hover"],
            activeforeground=THEME["text_primary"],
            relief="solid",
            bd=1,
            padx=10,
            pady=3,
            cursor="hand2",
        )
        self.btn_unit_switch.pack(side="left", padx=(0, 8))

        rb_c = ttk.Radiobutton(
            unit_frame,
            text="°C",
            variable=self.current_unit,
            value="C",
            command=self.on_unit_change,
            style="Unit.TRadiobutton",
        )
        rb_c.pack(side="left", padx=2)

        rb_f = ttk.Radiobutton(
            unit_frame,
            text="°F",
            variable=self.current_unit,
            value="F",
            command=self.on_unit_change,
            style="Unit.TRadiobutton",
        )
        rb_f.pack(side="left", padx=2)

    def _create_search_panel(self):
        """Creates the search bar with action buttons."""
        search_box = tk.Frame(self.root, bg=THEME["bg_dark"], padx=20, pady=12)
        search_box.pack(fill="x")

        # Inner container
        entry_wrap = tk.Frame(search_box, bg=THEME["bg_card"], padx=6, pady=6, bd=1, relief="solid")
        entry_wrap.pack(fill="x")

        loc_icon = tk.Label(entry_wrap, text="🔍", font=("Segoe UI", 11), bg=THEME["bg_card"], fg=THEME["text_muted"])
        loc_icon.pack(side="left", padx=(6, 4))

        self.entry_input = tk.Entry(
            entry_wrap,
            textvariable=self.search_query,
            font=("Segoe UI", 12),
            bg=THEME["bg_card_inner"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent_blue"],
            relief="flat",
            bd=5,
        )
        self.entry_input.pack(side="left", fill="x", expand=True, padx=4)
        self.entry_input.focus_set()

        # Clear button
        clear_btn = tk.Button(
            entry_wrap,
            text="✕",
            command=self.clear_search,
            font=("Segoe UI", 10, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            activebackground=THEME["bg_hover"],
            activeforeground=THEME["text_primary"],
            bd=0,
            padx=8,
            cursor="hand2",
        )
        clear_btn.pack(side="left")

        # Action Buttons container
        btns_frame = tk.Frame(search_box, bg=THEME["bg_dark"], pady=8)
        btns_frame.pack(fill="x")

        self.btn_search = tk.Button(
            btns_frame,
            text="Get Weather",
            command=self.start_weather_fetch,
            font=("Segoe UI", 10, "bold"),
            bg=THEME["accent_blue"],
            fg="#003640",
            activebackground=THEME["accent_blue_hover"],
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.btn_search.pack(side="left", padx=(0, 8))

        self.btn_location = tk.Button(
            btns_frame,
            text="📍 Auto-Detect Location (ipinfo.io)",
            command=self.start_location_detect,
            font=("Segoe UI", 10, "bold"),
            bg="#0f766e",
            fg="#ffffff",
            activebackground="#115e59",
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        )
        self.btn_location.pack(side="left", padx=(0, 8))

        # Quick preset buttons for instant exploration
        presets_label = tk.Label(
            btns_frame,
            text="Presets:",
            font=("Segoe UI", 9),
            bg=THEME["bg_dark"],
            fg=THEME["text_muted"],
        )
        presets_label.pack(side="left", padx=(12, 4))

        for city in ["Hyderabad", "Tokyo", "London", "New York"]:
            btn = tk.Button(
                btns_frame,
                text=city,
                command=lambda c=city: self.quick_search(c),
                font=("Segoe UI", 8),
                bg=THEME["bg_card"],
                fg=THEME["text_secondary"],
                activebackground=THEME["bg_hover"],
                activeforeground=THEME["text_primary"],
                relief="flat",
                padx=8,
                pady=4,
                cursor="hand2",
            )
            btn.pack(side="left", padx=3)

    def _create_status_banner(self):
        """Dedicated error/loading/notification banner visible on the GUI."""
        self.status_frame = tk.Frame(self.root, bg=THEME["bg_card"], padx=20, pady=8, bd=1, relief="solid")
        self.status_frame.pack(fill="x", padx=20, pady=(0, 8))

        self.status_icon_lbl = tk.Label(
            self.status_frame,
            text="ℹ",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["accent_blue"],
        )
        self.status_icon_lbl.pack(side="left", padx=(0, 8))

        self.status_msg_lbl = tk.Label(
            self.status_frame,
            text="Ready.",
            font=("Segoe UI", 9),
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            wraplength=640,
            justify="left",
        )
        self.status_msg_lbl.pack(side="left", fill="x", expand=True)

    def _create_scrollable_content(self):
        """Creates a scrollable canvas for the weather and forecast cards."""
        container = tk.Frame(self.root, bg=THEME["bg_dark"])
        container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.canvas = tk.Canvas(container, bg=THEME["bg_dark"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas, bg=THEME["bg_dark"])

        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=self.scrollbar.set)

        # Responsive width adjustment
        def on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling across platforms
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        # Build Card Sections
        self._create_current_weather_card()
        self._create_hourly_forecast_card()
        self._create_daily_forecast_card()

    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _create_current_weather_card(self):
        """Builds the hero Current Weather panel."""
        self.current_card = tk.Frame(
            self.scroll_content,
            bg=THEME["bg_card"],
            padx=20,
            pady=18,
            bd=1,
            relief="solid",
        )
        self.current_card.pack(fill="x", pady=(0, 12))

        # Top line: Location & Time
        top_box = tk.Frame(self.current_card, bg=THEME["bg_card"])
        top_box.pack(fill="x")

        self.lbl_location = tk.Label(
            top_box,
            text="No Location Loaded",
            font=("Segoe UI", 16, "bold"),
            fg=THEME["text_primary"],
            bg=THEME["bg_card"],
        )
        self.lbl_location.pack(side="left")

        self.lbl_time = tk.Label(
            top_box,
            text="—",
            font=("Segoe UI", 9),
            fg=THEME["text_muted"],
            bg=THEME["bg_card"],
        )
        self.lbl_time.pack(side="right")

        # Hero temperature and icon center area
        hero_box = tk.Frame(self.current_card, bg=THEME["bg_card"], pady=12)
        hero_box.pack(fill="x")

        self.lbl_weather_icon = tk.Label(hero_box, bg=THEME["bg_card"])
        self.lbl_weather_icon.pack(side="left", padx=(0, 16))

        temp_col = tk.Frame(hero_box, bg=THEME["bg_card"])
        temp_col.pack(side="left")

        self.lbl_temperature = tk.Label(
            temp_col,
            text="--°",
            font=("Segoe UI", 42, "bold"),
            fg=THEME["text_primary"],
            bg=THEME["bg_card"],
        )
        self.lbl_temperature.pack(anchor="w")

        self.lbl_condition_desc = tk.Label(
            temp_col,
            text="Enter location to load weather telemetry",
            font=("Segoe UI", 11, "bold"),
            fg=THEME["accent_blue"],
            bg=THEME["bg_card"],
        )
        self.lbl_condition_desc.pack(anchor="w")

        # Secondary feels-like & range badge
        self.lbl_feels_range = tk.Label(
            hero_box,
            text="",
            font=("Segoe UI", 10),
            fg=THEME["text_secondary"],
            bg=THEME["bg_card"],
        )
        self.lbl_feels_range.pack(side="right", anchor="e")

        # Divider
        divider = tk.Frame(self.current_card, bg=THEME["border"], height=1)
        divider.pack(fill="x", pady=10)

        # 4-Column Metrics Grid (Feels Like, Humidity, Wind, Visibility)
        metrics_frame = tk.Frame(self.current_card, bg=THEME["bg_card"])
        metrics_frame.pack(fill="x")
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.metric_widgets = {}
        metrics_meta = [
            ("feels_like", "🌡 FEELS LIKE", "--", 0),
            ("humidity", "💧 HUMIDITY", "--", 1),
            ("wind", "💨 WIND SPEED", "--", 2),
            ("visibility", "👁 VISIBILITY", "--", 3),
        ]

        for key, title, default_val, col in metrics_meta:
            m_box = tk.Frame(metrics_frame, bg=THEME["bg_card_inner"], padx=10, pady=8, bd=1, relief="solid")
            m_box.grid(row=0, column=col, padx=4, sticky="nsew")

            t_lbl = tk.Label(m_box, text=title, font=("Segoe UI", 8, "bold"), fg=THEME["text_muted"], bg=THEME["bg_card_inner"])
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(m_box, text=default_val, font=("Segoe UI", 12, "bold"), fg=THEME["text_primary"], bg=THEME["bg_card_inner"])
            v_lbl.pack(anchor="w", pady=(2, 0))

            self.metric_widgets[key] = v_lbl

    def _create_hourly_forecast_card(self):
        """Builds the 6-Hour upcoming forecast timeline panel."""
        self.hourly_card = tk.Frame(
            self.scroll_content,
            bg=THEME["bg_card"],
            padx=16,
            pady=14,
            bd=1,
            relief="solid",
        )
        self.hourly_card.pack(fill="x", pady=(0, 12))

        header_lbl = tk.Label(
            self.hourly_card,
            text="⏱ HOURLY FORECAST (NEXT 6 HOURS)",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["accent_blue"],
            bg=THEME["bg_card"],
        )
        header_lbl.pack(anchor="w", pady=(0, 10))

        # Container for horizontal hourly slots
        self.hourly_slots_frame = tk.Frame(self.hourly_card, bg=THEME["bg_card"])
        self.hourly_slots_frame.pack(fill="x")
        self.hourly_slots_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.hourly_slot_widgets = []
        for i in range(5):
            slot = tk.Frame(self.hourly_slots_frame, bg=THEME["bg_card_inner"], padx=8, pady=8, bd=1, relief="solid")
            slot.grid(row=0, column=i, padx=3, sticky="nsew")

            lbl_time = tk.Label(slot, text="--", font=("Segoe UI", 9, "bold"), fg=THEME["text_secondary"], bg=THEME["bg_card_inner"])
            lbl_time.pack()

            lbl_icon = tk.Label(slot, bg=THEME["bg_card_inner"])
            lbl_icon.pack(pady=3)

            lbl_temp = tk.Label(slot, text="--°", font=("Segoe UI", 12, "bold"), fg=THEME["text_primary"], bg=THEME["bg_card_inner"])
            lbl_temp.pack()

            lbl_cond = tk.Label(slot, text="--", font=("Segoe UI", 8), fg=THEME["text_muted"], bg=THEME["bg_card_inner"])
            lbl_cond.pack()

            self.hourly_slot_widgets.append({
                "time": lbl_time,
                "icon": lbl_icon,
                "temp": lbl_temp,
                "cond": lbl_cond,
            })

    def _create_daily_forecast_card(self):
        """Builds the 5-Day Daily Outlook panel."""
        self.daily_card = tk.Frame(
            self.scroll_content,
            bg=THEME["bg_card"],
            padx=16,
            pady=14,
            bd=1,
            relief="solid",
        )
        self.daily_card.pack(fill="x", pady=(0, 8))

        header_lbl = tk.Label(
            self.daily_card,
            text="📅 DAILY FORECAST (NEXT 5 DAYS)",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["accent_blue"],
            bg=THEME["bg_card"],
        )
        header_lbl.pack(anchor="w", pady=(0, 8))

        self.daily_rows_frame = tk.Frame(self.daily_card, bg=THEME["bg_card"])
        self.daily_rows_frame.pack(fill="x")

        self.daily_row_widgets = []
        for i in range(5):
            row = tk.Frame(self.daily_rows_frame, bg=THEME["bg_card_inner"], padx=12, pady=8, bd=1, relief="solid")
            row.pack(fill="x", pady=2)

            lbl_day = tk.Label(
                row,
                text="Day",
                font=("Segoe UI", 10, "bold"),
                fg=THEME["text_primary"],
                bg=THEME["bg_card_inner"],
                width=14,
                anchor="w",
            )
            lbl_day.pack(side="left")

            lbl_icon = tk.Label(row, bg=THEME["bg_card_inner"])
            lbl_icon.pack(side="left", padx=8)

            lbl_cond = tk.Label(
                row,
                text="Condition",
                font=("Segoe UI", 9),
                fg=THEME["text_secondary"],
                bg=THEME["bg_card_inner"],
                width=18,
                anchor="w",
            )
            lbl_cond.pack(side="left")

            lbl_temp_range = tk.Label(
                row,
                text="--° / --°",
                font=("Segoe UI", 10, "bold"),
                fg=THEME["accent_emerald"],
                bg=THEME["bg_card_inner"],
            )
            lbl_temp_range.pack(side="right")

            self.daily_row_widgets.append({
                "day": lbl_day,
                "icon": lbl_icon,
                "cond": lbl_cond,
                "temp": lbl_temp_range,
            })

    def _create_footer(self):
        """Creates the bottom credit bar."""
        footer_frame = tk.Frame(self.root, bg=THEME["bg_dark"], padx=20, pady=6)
        footer_frame.pack(fill="x", side="bottom")

        cred_lbl = tk.Label(
            footer_frame,
            text="Accurate Live Meteorological Observations & Multi-Day Forecasts",
            font=("Segoe UI", 8),
            fg=THEME["text_muted"],
            bg=THEME["bg_dark"],
        )
        cred_lbl.pack(side="left")

        ver_lbl = tk.Label(
            footer_frame,
            text=f"v{config.APP_VERSION}",
            font=("Segoe UI", 8),
            fg=THEME["text_muted"],
            bg=THEME["bg_dark"],
        )
        ver_lbl.pack(side="right")

    # =========================================================================
    # User Interaction & Controller Logic
    # =========================================================================

    def clear_search(self):
        """Clears the search input field."""
        self.search_query.set("")
        self.entry_input.focus_set()

    def quick_search(self, city_name: str):
        """Populates search input with a preset city and initiates fetch."""
        self.search_query.set(city_name)
        self.start_weather_fetch()

    def set_status(self, message: str, status_type: str = "info"):
        """Updates the status banner with appropriate colors and icons."""
        colors = {
            "info": (THEME["status_info_bg"], THEME["status_info_fg"], "ℹ"),
            "warning": ("#78350f", "#fde68a", "⚠"),
            "error": (THEME["status_error_bg"], THEME["status_error_fg"], "⚠"),
            "success": (THEME["status_success_bg"], THEME["status_success_fg"], "✓"),
            "loading": ("#1e3a8a", THEME["accent_amber"], "⏳"),
        }
        bg, fg, icon = colors.get(status_type, colors["info"])

        self.status_frame.configure(bg=bg)
        self.status_icon_lbl.configure(bg=bg, fg=fg, text=icon)
        self.status_msg_lbl.configure(bg=bg, fg=fg, text=message)

    def set_loading_state(self, loading: bool):
        """Toggles loading state and disables/enables action controls."""
        self.is_fetching = loading
        state = "disabled" if loading else "normal"
        self.btn_search.configure(state=state)
        self.btn_location.configure(state=state)

    def toggle_unit(self):
        """Toggles between Celsius and Fahrenheit via the unit switch button."""
        new_unit = "F" if self.current_unit.get() == "C" else "C"
        self.current_unit.set(new_unit)
        self.on_unit_change()

    def on_unit_change(self):
        """Triggers dynamic re-rendering of all temperature displays upon toggle."""
        unit = self.current_unit.get()
        if hasattr(self, "btn_unit_switch"):
            self.btn_unit_switch.configure(
                text="⇄ Switch to °C" if unit == "F" else "⇄ Switch to °F"
            )
        if self.weather_cache:
            self._render_current_weather(self.weather_cache)
        if self.forecast_cache:
            self._render_forecast(self.forecast_cache)

    def start_weather_fetch(self):
        """Validates input and launches the background worker thread."""
        if self.is_fetching:
            return

        query = self.search_query.get().strip()
        if not query:
            self.set_status("Please enter a city name or ZIP/postal code.", "error")
            self.entry_input.focus_set()
            return

        self.set_loading_state(True)
        self.set_status(f"Fetching live weather telemetry for '{query}'...", "loading")

        # Run in daemon thread to guarantee zero GUI freezing
        worker = threading.Thread(target=self._fetch_weather_thread, args=(query,), daemon=True)
        worker.start()

    def _schedule_queue_check(self):
        """Polls the thread-safe event queue and re-schedules itself."""
        self._process_queue()
        try:
            self.root.after(50, self._schedule_queue_check)
        except Exception:
            pass

    def _process_queue(self):
        """Dispatches all pending background events on the main Tkinter thread."""
        while not self.event_queue.empty():
            try:
                fn, args = self.event_queue.get_nowait()
                fn(*args)
            except queue.Empty:
                break
            except Exception:
                pass

    def _fetch_weather_thread(self, query: str):
        """Worker thread executing both weather and forecast network requests."""
        try:
            weather_data = get_current_weather(query)
            forecast_data = None
            forecast_error_msg = None

            try:
                forecast_data = get_forecast_data(query)
            except WeatherServiceError as f_err:
                forecast_error_msg = str(f_err)

            # Safely put callback into main-thread event queue
            self.event_queue.put((self._on_fetch_success, (weather_data, forecast_data, forecast_error_msg)))

        except WeatherServiceError as err:
            self.event_queue.put((self._on_fetch_error, (str(err),)))
        except Exception as exc:
            self.event_queue.put((self._on_fetch_error, (f"Unexpected error occurred: {str(exc)}",)))

    def _on_fetch_success(self, weather_data: dict, forecast_data: dict | None, forecast_error: str | None):
        """Main-thread callback after successful weather retrieval."""
        self.weather_cache = weather_data
        self.forecast_cache = forecast_data
        self.set_loading_state(False)

        self._render_current_weather(weather_data)

        if forecast_data:
            self._render_forecast(forecast_data)
            self.set_status(f"Weather & Forecast successfully loaded for {weather_data['location_display']}.", "success")
        else:
            self.set_status(
                f"Loaded current weather for {weather_data['location_display']}. (Forecast note: {forecast_error})",
                "warning",
            )

    def _on_fetch_error(self, error_message: str):
        """Main-thread callback when an error occurs during weather retrieval."""
        self.set_loading_state(False)
        self.set_status(error_message, "error")

    def start_location_detect(self):
        """Initiates background IP-based location detection via ipinfo.io."""
        if self.is_fetching:
            return

        self.set_loading_state(True)
        self.set_status("Detecting approximate location via ipinfo.io...", "loading")

        worker = threading.Thread(target=self._location_detect_thread, daemon=True)
        worker.start()

    def _location_detect_thread(self):
        loc_query, msg = get_approximate_location()
        self.event_queue.put((self._on_location_detected, (loc_query, msg)))

    def _on_location_detected(self, loc_query: str | None, message: str):
        self.set_loading_state(False)
        if loc_query:
            self.search_query.set(loc_query)
            self.set_status(message, "info")
            # Automatically fetch weather for detected location
            self.start_weather_fetch()
        else:
            self.set_status(message, "warning")

    # =========================================================================
    # Rendering & Presentation Layer
    # =========================================================================

    def _render_current_weather(self, data: dict):
        """Updates the Hero Current Weather card with current unit values."""
        unit = self.current_unit.get()
        temp_val = data["temp_c"] if unit == "C" else data["temp_f"]
        feels_val = data["feels_like_c"] if unit == "C" else data["feels_like_f"]
        min_val = data["temp_min_c"] if unit == "C" else data["temp_min_f"]
        max_val = data["temp_max_c"] if unit == "C" else data["temp_max_f"]
        unit_sym = f"°{unit}"

        # Location and local time
        self.lbl_location.configure(text=data["location_display"])
        self.lbl_time.configure(text=data["time_str"])

        # Weather icon via PIL
        icon_code = data["icon_code"]
        photo = get_weather_photo_image(icon_code, size=(80, 80))
        self.lbl_weather_icon.configure(image=photo)
        self.lbl_weather_icon.image = photo  # Keep reference

        # Temperatures & Condition
        self.lbl_temperature.configure(text=f"{int(round(temp_val))}{unit_sym}")
        self.lbl_condition_desc.configure(text=f"{data['condition']} • {data['description']}")
        self.lbl_feels_range.configure(
            text=f"Feels like: {feels_val:.1f}{unit_sym}\nLow: {min_val:.1f}{unit_sym} | High: {max_val:.1f}{unit_sym}"
        )

        # 4 Metric Cards
        self.metric_widgets["feels_like"].configure(text=f"{feels_val:.1f}{unit_sym}")
        self.metric_widgets["humidity"].configure(text=f"{data['humidity']}%")

        if unit == "C":
            wind_text = f"{data['wind_speed_ms']} m/s {data['wind_dir']}"
            vis_text = f"{data['visibility_km']} km"
        else:
            wind_text = f"{data['wind_speed_mph']} mph {data['wind_dir']}"
            vis_text = f"{data['visibility_mi']} mi"

        self.metric_widgets["wind"].configure(text=wind_text)
        self.metric_widgets["visibility"].configure(text=vis_text)

    def _render_forecast(self, data: dict):
        """Updates both the 6-to-12-Hour timeline and 5-Day Outlook panels."""
        unit = self.current_unit.get()
        unit_sym = f"°{unit}"

        # 1. Render Hourly Timeline
        hourly_items = data.get("hourly", [])
        for i, widget_group in enumerate(self.hourly_slot_widgets):
            if i < len(hourly_items):
                item = hourly_items[i]
                temp_val = item["temp_c"] if unit == "C" else item["temp_f"]

                widget_group["time"].configure(text=item["time"])
                widget_group["temp"].configure(text=f"{int(round(temp_val))}{unit_sym}")
                widget_group["cond"].configure(text=item["condition"])

                # Icon
                photo = get_weather_photo_image(item["icon_code"], size=(36, 36))
                widget_group["icon"].configure(image=photo)
                widget_group["icon"].image = photo
            else:
                widget_group["time"].configure(text="--")
                widget_group["temp"].configure(text="--°")
                widget_group["cond"].configure(text="--")

        # 2. Render 5-Day Outlook
        daily_items = data.get("daily", [])
        for i, row_group in enumerate(self.daily_row_widgets):
            if i < len(daily_items):
                d = daily_items[i]
                min_val = d["temp_min_c"] if unit == "C" else d["temp_min_f"]
                max_val = d["temp_max_c"] if unit == "C" else d["temp_max_f"]

                row_group["day"].configure(text=d["display_date"])
                row_group["cond"].configure(text=f"{d['condition']} — {d['description']}")
                row_group["temp"].configure(
                    text=f"Low: {int(round(min_val))}{unit_sym}   High: {int(round(max_val))}{unit_sym}"
                )

                # Icon
                photo = get_weather_photo_image(d["icon_code"], size=(32, 32))
                row_group["icon"].configure(image=photo)
                row_group["icon"].image = photo
            else:
                row_group["day"].configure(text="--")
                row_group["cond"].configure(text="--")
                row_group["temp"].configure(text="--° / --°")


def main():
    """Application entry point: launches GUI by default, or CLI if --cli is passed or Tkinter is absent."""
    if "--cli" in sys.argv or "-c" in sys.argv:
        from weather_cli import main as cli_main
        cli_main()
        return

    if not HAS_TKINTER:
        print("\n" + "=" * 64)
        print("  [Notice] Tkinter graphical library is not installed.")
        print("=" * 64)
        print("  The desktop GUI requires Tkinter. To install it on your system:")
        print("    • Ubuntu / Debian : sudo apt-get install python3-tk python3-pil.imagetk")
        print("    • Fedora / RHEL   : sudo dnf install python3-tkinter")
        print("    • macOS / Windows : Reinstall Python with Tcl/Tk enabled.")
        print("\n  Available alternatives in this codebase:")
        print("    1. Terminal CLI   : python3 weather_cli.py [city_name]")
        print("    2. Web Dashboard  : python3 web_preview.py (http://localhost:3000)")
        print("=" * 64 + "\n")
        
        # If running interactively, offer to launch CLI
        if sys.stdin.isatty():
            choice = input("Would you like to run the Weather CLI now? [Y/n]: ").strip().lower()
            if choice in ("", "y", "yes"):
                from weather_cli import main as cli_main
                cli_main()
                return
        sys.exit(1)

    root = tk.Tk()
    app = WeatherDashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
