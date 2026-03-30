📌 Project Overview

This project is a desktop weather application built using Python and Tkinter. It provides real-time weather data along with a 5-day forecast for any city using the OpenWeatherMap API. The application focuses on delivering a clean, interactive, and maintaining smooth performance through multithreading.


⚙️ Features

🌍 Search weather by city name

🌡 Real-time temperature, “feels like,” and weather conditions

📅 5-day forecast with daily summaries

⏰ Hourly forecast for the next 24 hours

💨 Additional metrics: humidity, wind speed & direction, pressure, cloudiness, visibility

🔁 Unit conversion support (Celsius, Fahrenheit, Kelvin)

🕘 Live system clock display

📜 Search history with quick access

⚡ Multithreaded API calls for a responsive UI


🧠 How It Works

The application interacts with the OpenWeatherMap API to fetch both current weather and forecast data. When a user searches for a city, API requests are executed in a separate thread to prevent the UI from freezing. The retrieved JSON data is parsed and displayed using structured UI components such as cards, scrollable sections, and icons.

🖥️ Tech Stack

Python (Core language)

Tkinter (GUI framework)

Requests (API handling)

Pillow (PIL) (Image processing for weather icons)

Threading (Non-blocking UI updates