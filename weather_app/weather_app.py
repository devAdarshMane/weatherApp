# ============================================================
# BLOCK 1 — IMPORTS & CONFIGURATION
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import threading
from PIL import Image, ImageTk
import io
import urllib.request

# --- API CONFIGURATION ---
API_KEY  = "4780165e19fc8f6720e66f953c6746a8"
BASE_URL = "https://api.openweathermap.org/data/2.5"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"

# ============================================================
# BLOCK 2 — COLOR THEME & FONTS
# ============================================================

COLORS = {
    "bg_dark"     : "#2f6a6e",
    "bg_medium"   : "#16213e",
    "bg_card"     : "#000000",
    "accent"      : "#dfb913",
    "accent_light": "#ff6b6b",
    "text_white"  : "#ffffff",
    "text_gray"   : "#a8b2d8",
    "text_light"  : "#ccd6f6",
    "success"     : "#64ffda",
    "warning"     : "#ffd700",
    "card_border" : "#1e4080",
}

FONTS = {
    "title"   : ("Helvetica", 28, "bold"),
    "subtitle": ("Helvetica", 14),
    "heading" : ("Helvetica", 16, "bold"),
    "body"    : ("Helvetica", 12),
    "small"   : ("Helvetica", 10),
    "temp"    : ("Helvetica", 48, "bold"),
    "large"   : ("Helvetica", 20, "bold"),
}

# ============================================================
# BLOCK 3 — API FUNCTIONS
# ============================================================

def get_current_weather(city, units="metric"):
    try:
        url = f"{BASE_URL}/weather"
        params = {
            "q"    : city,
            "appid": API_KEY,
            "units": units
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            raise ValueError(f"City '{city}' not found.")
        elif response.status_code == 401:
            raise ValueError("Invalid API Key. Please check your key.")
        else:
            raise ValueError(f"HTTP Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise ValueError("No internet connection. Please check network.")
    except requests.exceptions.Timeout:
        raise ValueError("Request timed out. Please try again.")


def get_forecast(city, units="metric"):
    try:
        url = f"{BASE_URL}/forecast"
        params = {
            "q"    : city,
            "appid": API_KEY,
            "units": units
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            raise ValueError(f"City '{city}' not found.")
        elif response.status_code == 401:
            raise ValueError("Invalid API Key.")
        else:
            raise ValueError(f"HTTP Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise ValueError("No internet connection. Please check network.")
    except requests.exceptions.Timeout:
        raise ValueError("Request timed out. Please try again.")


def load_weather_icon(icon_code, size=(60, 60)):
    try:
        url = ICON_URL.format(icon_code)
        with urllib.request.urlopen(url, timeout=5) as response:
            image_data = response.read()
        image = Image.open(io.BytesIO(image_data))
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception:
        return None

# ============================================================
# BLOCK 4 — HELPER FUNCTIONS
# ============================================================

def get_unit_symbol(units):
    if units == "metric":
        return "°C"
    elif units == "imperial":
        return "°F"
    else:
        return "K"


def get_wind_unit(units):
    return "m/s" if units == "metric" else "mph"


def format_time(timestamp, fmt="%H:%M"):
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def format_date(timestamp, fmt="%A, %d %B %Y"):
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def get_day_name(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%a")


def get_weather_bg_color(weather_main):
    conditions = {
        "Clear"       : "#1a3a5c",
        "Clouds"      : "#2d3748",
        "Rain"        : "#1a2a3a",
        "Drizzle"     : "#1a2535",
        "Thunderstorm": "#1a1a2e",
        "Snow"        : "#2d3a4a",
        "Mist"        : "#2a3040",
        "Fog"         : "#2a3040",
        "Haze"        : "#2a3040",
    }
    return conditions.get(weather_main, "#1a1a2e")


def get_wind_direction(degrees):
    directions = [
        "N",  "NNE", "NE",  "ENE",
        "E",  "ESE", "SE",  "SSE",
        "S",  "SSW", "SW",  "WSW",
        "W",  "WNW", "NW",  "NNW"
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]

# ============================================================
# BLOCK 5 — MAIN APP CLASS
# ============================================================

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤 Weather Forecast App")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)
        self.root.configure(bg=COLORS["bg_dark"])

        self.units           = tk.StringVar(value="metric")
        self.city_var        = tk.StringVar()
        self.is_loading      = False
        self.icon_references = []
        self.search_history  = []

        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        width  = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth()  // 2) - (width  // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        self._build_header()
        self._build_search_bar()
        self._build_content_area()
        self._build_status_bar()

    # ============================================================
    # BLOCK 6 — HEADER & SEARCH BAR
    # ============================================================

    def _build_header(self):
        header_frame = tk.Frame(self.main_frame, bg=COLORS["bg_dark"])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text = "🌤 Weather Forecast",
            font = FONTS["title"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["text_white"]
        ).pack(side=tk.LEFT)

        unit_frame = tk.Frame(header_frame, bg=COLORS["bg_dark"])
        unit_frame.pack(side=tk.RIGHT)

        tk.Label(
            unit_frame,
            text = "Units:",
            font = FONTS["body"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["text_gray"]
        ).pack(side=tk.LEFT, padx=(0, 5))

        for text, value in [("°C", "metric"), ("°F", "imperial"), ("K", "standard")]:
            tk.Radiobutton(
                unit_frame,
                text             = text,
                variable         = self.units,
                value            = value,
                font             = FONTS["small"],
                bg               = COLORS["bg_dark"],
                fg               = COLORS["text_light"],
                selectcolor      = COLORS["bg_card"],
                activebackground = COLORS["bg_dark"],
                activeforeground = COLORS["accent"],
                cursor           = "hand2",
                command          = self._on_unit_change
            ).pack(side=tk.LEFT, padx=3)

    def _build_search_bar(self):
        search_frame = tk.Frame(
            self.main_frame,
            bg                  = COLORS["bg_medium"],
            highlightbackground = COLORS["card_border"],
            highlightthickness  = 1
        )
        search_frame.pack(fill=tk.X, pady=(0, 15), ipady=8)

        inner = tk.Frame(search_frame, bg=COLORS["bg_medium"])
        inner.pack(fill=tk.X, padx=10)

        tk.Label(
            inner,
            text = "🔍",
            font = FONTS["body"],
            bg   = COLORS["bg_medium"],
            fg   = COLORS["text_gray"]
        ).pack(side=tk.LEFT, padx=(5, 5))

        self.city_entry = tk.Entry(
            inner,
            textvariable     = self.city_var,
            font             = FONTS["body"],
            bg               = COLORS["bg_medium"],
            fg               = COLORS["text_white"],
            insertbackground = COLORS["text_white"],
            relief           = tk.FLAT,
            width            = 35
        )
        self.city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.city_entry.bind("<Return>", lambda e: self._search_weather())
        self.city_entry.focus()

        tk.Button(
            inner,
            text    = "📋 History",
            font    = FONTS["small"],
            bg      = COLORS["bg_card"],
            fg      = COLORS["text_light"],
            relief  = tk.FLAT,
            padx    = 10,
            pady    = 5,
            cursor  = "hand2",
            command = self._show_history
        ).pack(side=tk.RIGHT, padx=5)

        self.search_btn = tk.Button(
            inner,
            text             = "Search",
            font             = FONTS["body"],
            bg               = COLORS["accent"],
            fg               = COLORS["text_white"],
            relief           = tk.FLAT,
            padx             = 20,
            pady             = 5,
            cursor           = "hand2",
            activebackground = COLORS["accent_light"],
            command          = self._search_weather
        )
        self.search_btn.pack(side=tk.RIGHT, padx=5)

    # ============================================================
    # BLOCK 7 — CONTENT AREA & WELCOME SCREEN
    # ============================================================

    def _build_content_area(self):
        canvas_frame = tk.Frame(self.main_frame, bg=COLORS["bg_dark"])
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg                = COLORS["bg_dark"],
            highlightthickness= 0
        )

        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient  = tk.VERTICAL,
            command = self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.content_frame = tk.Frame(self.canvas, bg=COLORS["bg_dark"])
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window = self.content_frame,
            anchor = "nw"
        )

        self.content_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>",        self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>",        self._on_mousewheel)
        self.canvas.bind("<Button-4>",          self._on_mousewheel)
        self.canvas.bind("<Button-5>",          self._on_mousewheel)

        self._show_welcome()

    def _build_status_bar(self):
        status_frame = tk.Frame(self.main_frame, bg=COLORS["bg_medium"])
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = tk.Label(
            status_frame,
            text   = "Enter a city name to get weather information.",
            font   = FONTS["small"],
            bg     = COLORS["bg_medium"],
            fg     = COLORS["text_gray"],
            anchor = tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.time_label = tk.Label(
            status_frame,
            text = "",
            font = FONTS["small"],
            bg   = COLORS["bg_medium"],
            fg   = COLORS["text_gray"]
        )
        self.time_label.pack(side=tk.RIGHT, padx=10, pady=5)
        self._update_time()

    def _update_time(self):
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.time_label.config(text=f"🕐 {now}")
        self.root.after(1000, self._update_time)

    def _show_welcome(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        welcome_frame = tk.Frame(self.content_frame, bg=COLORS["bg_dark"])
        welcome_frame.pack(fill=tk.BOTH, expand=True, pady=40)

        tk.Label(
            welcome_frame,
            text = "🌍",
            font = ("Helvetica", 60),
            bg   = COLORS["bg_dark"]
        ).pack()

        tk.Label(
            welcome_frame,
            text = "Welcome to Weather Forecast",
            font = FONTS["large"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["text_white"]
        ).pack(pady=(10, 5))

        tk.Label(
            welcome_frame,
            text = "Search for any city to get current weather and 5-day forecast",
            font = FONTS["body"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["text_gray"]
        ).pack(pady=(0, 30))

        tk.Label(
            welcome_frame,
            text = "Popular Cities:",
            font = FONTS["subtitle"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["text_light"]
        ).pack(pady=(0, 10))

        cities_frame = tk.Frame(welcome_frame, bg=COLORS["bg_dark"])
        cities_frame.pack()

        popular_cities = [
            "London",  "New York", "Tokyo",  "Paris",
            "Dubai",   "Sydney",   "Mumbai", "Berlin"
        ]

        for i, city in enumerate(popular_cities):
            row = i // 4
            col = i %  4
            tk.Button(
                cities_frame,
                text             = city,
                font             = FONTS["small"],
                bg               = COLORS["bg_card"],
                fg               = COLORS["text_light"],
                relief           = tk.FLAT,
                padx             = 12,
                pady             = 6,
                cursor           = "hand2",
                activebackground = COLORS["accent"],
                activeforeground = COLORS["text_white"],
                command          = lambda c=city: self._quick_search(c)
            ).grid(row=row, column=col, padx=5, pady=5)
        # ============================================================
    # BLOCK 9 — DISPLAY CURRENT WEATHER
    # ============================================================

    def _display_weather(self, current, forecast):
        """Master display function — clears screen and shows all weather data."""
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.icon_references.clear()

        # Get values needed for display
        weather_main = current["weather"][0]["main"]
        bg_color     = get_weather_bg_color(weather_main)
        units        = self.units.get()
        unit         = get_unit_symbol(units)
        wind_unit    = get_wind_unit(units)

        # Build each section
        self._build_current_weather_card(current, unit, wind_unit, bg_color)
        self._build_info_cards(current, wind_unit)
        self._build_hourly_forecast(forecast, unit)
        self._build_daily_forecast(forecast, unit)

        # Update status bar
        city_name    = current["name"]
        country      = current["sys"]["country"]
        last_updated = format_time(current["dt"])
        self._set_status(
            f"✅ Showing weather for {city_name}, {country}  |  "
            f"Last updated: {last_updated}"
        )

        # Scroll back to top
        self.canvas.yview_moveto(0)


    def _build_current_weather_card(self, data, unit, wind_unit, bg_color):
        """Builds the main large weather card."""
        card = tk.Frame(
            self.content_frame,
            bg                  = bg_color,
            highlightbackground = COLORS["card_border"],
            highlightthickness  = 1
        )
        card.pack(fill=tk.X, padx=5, pady=5)

        # --- TOP ROW: City name + Date ---
        top_row = tk.Frame(card, bg=bg_color)
        top_row.pack(fill=tk.X, padx=20, pady=(15, 0))

        city_name = data["name"]
        country   = data["sys"]["country"]

        tk.Label(
            top_row,
            text = f"📍 {city_name}, {country}",
            font = FONTS["heading"],
            bg   = bg_color,
            fg   = COLORS["text_white"]
        ).pack(side=tk.LEFT)

        tk.Label(
            top_row,
            text = format_date(data["dt"]),
            font = FONTS["small"],
            bg   = bg_color,
            fg   = COLORS["text_gray"]
        ).pack(side=tk.RIGHT)

        # --- MIDDLE ROW: Temperature (left) + Icon (right) ---
        mid_row = tk.Frame(card, bg=bg_color)
        mid_row.pack(fill=tk.X, padx=20, pady=10)

        # Temperature section
        temp_frame = tk.Frame(mid_row, bg=bg_color)
        temp_frame.pack(side=tk.LEFT)

        temp       = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        desc       = data["weather"][0]["description"].title()

        tk.Label(
            temp_frame,
            text = f"{temp}{unit}",
            font = FONTS["temp"],
            bg   = bg_color,
            fg   = COLORS["text_white"]
        ).pack(anchor=tk.W)

        tk.Label(
            temp_frame,
            text = f"Feels like {feels_like}{unit}",
            font = FONTS["small"],
            bg   = bg_color,
            fg   = COLORS["text_gray"]
        ).pack(anchor=tk.W)

        tk.Label(
            temp_frame,
            text = desc,
            font = FONTS["subtitle"],
            bg   = bg_color,
            fg   = COLORS["success"]
        ).pack(anchor=tk.W, pady=(5, 0))

        # Icon + Min/Max section
        icon_frame = tk.Frame(mid_row, bg=bg_color)
        icon_frame.pack(side=tk.RIGHT, padx=20)

        icon_code = data["weather"][0]["icon"]
        icon      = load_weather_icon(icon_code, size=(90, 90))
        if icon:
            self.icon_references.append(icon)
            tk.Label(
                icon_frame,
                image = icon,
                bg    = bg_color
            ).pack()

        temp_min = round(data["main"]["temp_min"])
        temp_max = round(data["main"]["temp_max"])

        tk.Label(
            icon_frame,
            text = f"↑{temp_max}{unit}   ↓{temp_min}{unit}",
            font = FONTS["small"],
            bg   = bg_color,
            fg   = COLORS["text_light"]
        ).pack()

        # --- BOTTOM ROW: Sunrise + Sunset + Visibility ---
        bottom_row = tk.Frame(card, bg=bg_color)
        bottom_row.pack(fill=tk.X, padx=20, pady=(0, 15))

        sunrise    = format_time(data["sys"]["sunrise"])
        sunset     = format_time(data["sys"]["sunset"])
        visibility = data.get("visibility", 0) / 1000

        tk.Label(
            bottom_row,
            text = f"🌅 Sunrise: {sunrise}",
            font = FONTS["small"],
            bg   = bg_color,
            fg   = COLORS["warning"]
        ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            bottom_row,
            text = f"🌇 Sunset: {sunset}",
            font = FONTS["small"],
            bg   = bg_color,
            fg   = COLORS["warning"]
        ).pack(side=tk.LEFT)

        tk.Label(
            bottom_row,
            text = f"👁 Visibility: {visibility:.1f} km",
            font = FONTS["small"],
            bg   = bg_color,
            fg   = COLORS["text_gray"]
        ).pack(side=tk.RIGHT)


    def _build_info_cards(self, data, wind_unit):
        """Builds row of 4 info cards below main weather card."""
        info_frame = tk.Frame(self.content_frame, bg=COLORS["bg_dark"])
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        for i in range(4):
            info_frame.columnconfigure(i, weight=1)

        humidity   = data["main"]["humidity"]
        pressure   = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        wind_deg   = data["wind"].get("deg", 0)
        cloudiness = data["clouds"]["all"]
        wind_dir   = get_wind_direction(wind_deg)

        info_items = [
            ("💧", "Humidity",   f"{humidity}%"),
            ("🌬", "Wind",       f"{wind_speed} {wind_unit} {wind_dir}"),
            ("🔵", "Pressure",   f"{pressure} hPa"),
            ("☁",  "Cloudiness", f"{cloudiness}%"),
        ]

        for col, (icon, label, value) in enumerate(info_items):
            self._create_info_card(info_frame, icon, label, value, col)


    def _create_info_card(self, parent, icon, label, value, col):
        """Creates a single small info card."""
        card = tk.Frame(
            parent,
            bg                  = COLORS["bg_card"],
            highlightbackground = COLORS["card_border"],
            highlightthickness  = 1
        )
        card.grid(row=0, column=col, padx=4, pady=4, sticky="ew")

        tk.Label(
            card,
            text = icon,
            font = ("Helvetica", 22),
            bg   = COLORS["bg_card"]
        ).pack(pady=(12, 0))

        tk.Label(
            card,
            text = label,
            font = FONTS["small"],
            bg   = COLORS["bg_card"],
            fg   = COLORS["text_gray"]
        ).pack()

        tk.Label(
            card,
            text = value,
            font = FONTS["body"],
            bg   = COLORS["bg_card"],
            fg   = COLORS["text_white"]
        ).pack(pady=(2, 12))
        # ============================================================
    # BLOCK 10 — HOURLY & DAILY FORECAST
    # ============================================================

    def _build_hourly_forecast(self, forecast, unit):
        """Builds horizontally scrollable 24-hour forecast strip."""
        # Section heading
        tk.Label(
            self.content_frame,
            text   = "⏰ Hourly Forecast (Next 24 Hours)",
            font   = FONTS["heading"],
            bg     = COLORS["bg_dark"],
            fg     = COLORS["text_white"],
            anchor = tk.W
        ).pack(fill=tk.X, padx=10, pady=(15, 5))

        # Outer container
        outer = tk.Frame(
            self.content_frame,
            bg                  = COLORS["bg_medium"],
            highlightbackground = COLORS["card_border"],
            highlightthickness  = 1
        )
        outer.pack(fill=tk.X, padx=5, pady=5)

        # Horizontal canvas + scrollbar
        h_canvas = tk.Canvas(
            outer,
            bg                = COLORS["bg_medium"],
            height            = 140,
            highlightthickness= 0
        )
        h_scroll = ttk.Scrollbar(
            outer,
            orient  = tk.HORIZONTAL,
            command = h_canvas.xview
        )
        h_canvas.configure(xscrollcommand=h_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        h_canvas.pack(fill=tk.BOTH, expand=True)

        # Frame inside horizontal canvas
        hourly_frame = tk.Frame(h_canvas, bg=COLORS["bg_medium"])
        h_canvas.create_window((0, 0), window=hourly_frame, anchor="nw")

        # API gives data every 3 hours — 8 slots = 24 hours
        items = forecast["list"][:8]

        for item in items:
            time_str  = format_time(item["dt"])
            temp      = round(item["main"]["temp"])
            icon_code = item["weather"][0]["icon"]
            desc      = item["weather"][0]["main"]

            # Each hour slot card
            slot = tk.Frame(
                hourly_frame,
                bg                  = COLORS["bg_card"],
                highlightbackground = COLORS["card_border"],
                highlightthickness  = 1
            )
            slot.pack(side=tk.LEFT, padx=4, pady=8, ipadx=10, ipady=5)

            tk.Label(
                slot,
                text = time_str,
                font = FONTS["small"],
                bg   = COLORS["bg_card"],
                fg   = COLORS["text_gray"]
            ).pack()

            icon = load_weather_icon(icon_code, size=(40, 40))
            if icon:
                self.icon_references.append(icon)
                tk.Label(
                    slot,
                    image = icon,
                    bg    = COLORS["bg_card"]
                ).pack()

            tk.Label(
                slot,
                text = f"{temp}{unit}",
                font = ("Helvetica", 13, "bold"),
                bg   = COLORS["bg_card"],
                fg   = COLORS["text_white"]
            ).pack()

            tk.Label(
                slot,
                text = desc,
                font = FONTS["small"],
                bg   = COLORS["bg_card"],
                fg   = COLORS["text_gray"]
            ).pack()

        # Update scroll region after adding all items
        hourly_frame.update_idletasks()
        h_canvas.configure(scrollregion=h_canvas.bbox("all"))

        # Horizontal mouse scroll
        h_canvas.bind(
            "<MouseWheel>",
            lambda e: h_canvas.xview_scroll(
                -1 if e.delta > 0 else 1, "units"
            )
        )


    def _build_daily_forecast(self, forecast, unit):
        """Builds 5-day forecast section with one card per day."""
        tk.Label(
            self.content_frame,
            text   = "📅 5-Day Forecast",
            font   = FONTS["heading"],
            bg     = COLORS["bg_dark"],
            fg     = COLORS["text_white"],
            anchor = tk.W
        ).pack(fill=tk.X, padx=10, pady=(15, 5))

        forecast_frame = tk.Frame(self.content_frame, bg=COLORS["bg_dark"])
        forecast_frame.pack(fill=tk.X, padx=5, pady=5)

        # 5 equal columns
        for i in range(5):
            forecast_frame.columnconfigure(i, weight=1)

        # Get one entry per day
        daily_data = self._get_daily_data(forecast["list"])

        for col, day in enumerate(daily_data[:5]):
            self._create_daily_card(forecast_frame, day, unit, col)

        # Bottom spacing
        tk.Frame(
            self.content_frame,
            bg     = COLORS["bg_dark"],
            height = 20
        ).pack()


    def _create_daily_card(self, parent, day_data, unit, col):
        """Builds one day forecast card."""
        card = tk.Frame(
            parent,
            bg                  = COLORS["bg_card"],
            highlightbackground = COLORS["card_border"],
            highlightthickness  = 1
        )
        card.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        # Extract data
        day_name  = get_day_name(day_data["dt"])
        date_str  = datetime.fromtimestamp(day_data["dt"]).strftime("%d %b")
        temp_max  = round(day_data["main"]["temp_max"])
        temp_min  = round(day_data["main"]["temp_min"])
        icon_code = day_data["weather"][0]["icon"]
        desc      = day_data["weather"][0]["description"].title()
        humidity  = day_data["main"]["humidity"]

        tk.Label(
            card,
            text = day_name,
            font = FONTS["body"],
            bg   = COLORS["bg_card"],
            fg   = COLORS["text_white"]
        ).pack(pady=(12, 0))

        tk.Label(
            card,
            text = date_str,
            font = FONTS["small"],
            bg   = COLORS["bg_card"],
            fg   = COLORS["text_gray"]
        ).pack()

        icon = load_weather_icon(icon_code, size=(55, 55))
        if icon:
            self.icon_references.append(icon)
            tk.Label(
                card,
                image = icon,
                bg    = COLORS["bg_card"]
            ).pack(pady=5)

        tk.Label(
            card,
            text       = desc,
            font       = FONTS["small"],
            bg         = COLORS["bg_card"],
            fg         = COLORS["success"],
            wraplength = 100
        ).pack()

        tk.Label(
            card,
            text = f"↑ {temp_max}{unit}",
            font = ("Helvetica", 13, "bold"),
            bg   = COLORS["bg_card"],
            fg   = COLORS["text_white"]
        ).pack()

        tk.Label(
            card,
            text = f"↓ {temp_min}{unit}",
            font = FONTS["small"],
            bg   = COLORS["bg_card"],
            fg   = COLORS["text_gray"]
        ).pack()

        tk.Label(
            card,
            text = f"💧 {humidity}%",
            font = FONTS["small"],
            bg   = COLORS["bg_card"],
            fg   = COLORS["text_gray"]
        ).pack(pady=(2, 12))


    def _get_daily_data(self, forecast_list):
        """
        Picks one forecast entry per day.
        API returns data every 3 hours.
        We take first entry of each day.
        """
        seen_days = set()
        daily     = []

        for item in forecast_list:
            # Get just the date part
            day = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")

            if day not in seen_days:
                seen_days.add(day)
                daily.append(item)

        return daily

    # ============================================================
    # BLOCK 8 — TEMPORARY METHODS (will replace later)
    # ============================================================

    def _on_unit_change(self):
        city = self.city_var.get().strip()
        if city:
            self._fetch_weather(city)

    def _search_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return
        if self.is_loading:
            return
        self._fetch_weather(city)

    def _quick_search(self, city):
        self.city_var.set(city)
        self._fetch_weather(city)

    def _fetch_weather(self, city):
        
        self.is_loading = True
        self.search_btn.config(state=tk.DISABLED, text="Loading...")
        self._set_status(f"Fetching weather for '{city}'...")
        self._show_loading()

        def worker():
            try:
                units    = self.units.get()
                current  = get_current_weather(city, units)
                forecast = get_forecast(city, units)
                self.root.after(0, lambda: self._display_weather(current, forecast))

                if city not in self.search_history:
                    self.search_history.insert(0, city)
                    if len(self.search_history) > 10:
                        self.search_history.pop()

            except ValueError as e:
                self.root.after(0, lambda: self._show_error(str(e)))
            finally:
                self.root.after(0, self._reset_search_btn)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _reset_search_btn(self):
        """Re-enables search button after loading."""
        self.is_loading = False
        self.search_btn.config(state=tk.NORMAL, text="Search")

    def _show_loading(self):
        """Shows animated loading screen."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        loading_frame = tk.Frame(self.content_frame, bg=COLORS["bg_dark"])
        loading_frame.pack(fill=tk.BOTH, expand=True, pady=100)

        tk.Label(
            loading_frame,
            text = "⏳",
            font = ("Helvetica", 50),
            bg   = COLORS["bg_dark"]
        ).pack()

        tk.Label(
            loading_frame,
            text = "Fetching weather data...",
            font = FONTS["subtitle"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["text_gray"]
        ).pack(pady=10)

        self.progress = ttk.Progressbar(
            loading_frame,
            mode   = "indeterminate",
            length = 300
        )
        self.progress.pack(pady=10)
        self.progress.start(10)

    def _show_error(self, message):

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        error_frame = tk.Frame(self.content_frame, bg=COLORS["bg_dark"])
        error_frame.pack(fill=tk.BOTH, expand=True, pady=60)

        tk.Label(
            error_frame,
            text = "❌",
            font = ("Helvetica", 50),
            bg   = COLORS["bg_dark"]
        ).pack()

        tk.Label(
            error_frame,
            text = "Something went wrong",
            font = FONTS["large"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["accent"]
        ).pack(pady=(10, 5))

        tk.Label(
            error_frame,
            text       = message,
            font       = FONTS["body"],
            bg         = COLORS["bg_dark"],
            fg         = COLORS["text_gray"],
            wraplength = 500
        ).pack(pady=(0, 20))

        tk.Button(
            error_frame,
            text    = "Go Back",
            font    = FONTS["body"],
            bg      = COLORS["accent"],
            fg      = COLORS["text_white"],
            relief  = tk.FLAT,
            padx    = 20,
            pady    = 8,
            cursor  = "hand2",
            command = self._show_welcome
        ).pack()

        self._set_status(f"Error: {message}")

    def _show_history(self):
        """Shows popup window with past city searches."""
        if not self.search_history:
            messagebox.showinfo("Search History", "No search history yet.")
            return

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Search History")
        popup.geometry("300x350")
        popup.configure(bg=COLORS["bg_dark"])
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(
            popup,
            text = "📋 Recent Searches",
            font = FONTS["heading"],
            bg   = COLORS["bg_dark"],
            fg   = COLORS["text_white"]
        ).pack(pady=15)

        list_frame = tk.Frame(popup, bg=COLORS["bg_dark"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        for city in self.search_history:
            tk.Button(
                list_frame,
                text    = f"🏙 {city}",
                font    = FONTS["body"],
                bg      = COLORS["bg_card"],
                fg      = COLORS["text_white"],
                relief  = tk.FLAT,
                anchor  = tk.W,
                padx    = 10,
                pady    = 6,
                cursor  = "hand2",
                command = lambda c=city: [
                    popup.destroy(),
                    self._quick_search(c)
                ]
            ).pack(fill=tk.X, pady=2)

        tk.Button(
            list_frame,
            text    = "🗑 Clear History",
            font    = FONTS["small"],
            bg      = COLORS["accent"],
            fg      = COLORS["text_white"],
            relief  = tk.FLAT,
            padx    = 10,
            pady    = 5,
            cursor  = "hand2",
            command = lambda: [
                self.search_history.clear(),
                popup.destroy()
            ]
        ).pack(pady=15)
    def _set_status(self, message):
        self.status_label.config(text=message)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")


    # ============================================================
# BLOCK 11 — ENTRY POINT (OUTSIDE CLASS)
# ============================================================

def main():
    """Creates root window, applies styles and starts the app."""
    root = tk.Tk()

    # Style ttk widgets to match our dark theme
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Vertical.TScrollbar",
        background  = COLORS["bg_card"],
        troughcolor = COLORS["bg_medium"],
        arrowcolor  = COLORS["text_gray"]
    )

    style.configure(
        "Horizontal.TScrollbar",
        background  = COLORS["bg_card"],
        troughcolor = COLORS["bg_medium"],
        arrowcolor  = COLORS["text_gray"]
    )

    style.configure(
        "TProgressbar",
        troughcolor = COLORS["bg_medium"],
        background  = COLORS["accent"]
    )

    # Create and start the app
    app = WeatherApp(root)
    root.mainloop()


# Run only if this file is executed directly
if __name__ == "__main__":
    main()