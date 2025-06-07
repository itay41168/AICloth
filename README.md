# 👚 AICloth – מה ללבוש היום?

**AICloth** is a smart weather-based outfit recommender built with Python and Streamlit. It uses real-time weather data from the [OpenWeather API](https://openweathermap.org/) and a machine learning model (Random Forest Classifier) trained on historical outfit-weather data to recommend what to wear — in Hebrew!

---

## 🌟 Features

- 🌍 Get weather by IP geolocation or by city name
- 📦 Supports manual weather input
- 🌦 Uses live weather from OpenWeather API
- 🧠 Predicts outfits using a trained Random Forest model
- 🧥 Translates outfit recommendations to Hebrew
- 💅 Beautiful RTL-friendly Hebrew UI with custom CSS
- 📱 Mobile-responsive layout

---

## 🧠 How It Works

1. The user selects how to input weather data (location, city name, or manual).
2. If using geolocation, it attempts to detect your city via IP using `geocoder` and OpenWeather's reverse geocoding API.
3. Weather data (temperature, humidity, wind, and weather type) is collected.
4. The trained ML model predicts the best outfit.
5. The recommendation is translated from English to Hebrew and displayed in a stylish UI.

---

## 🛠️ Tech Stack

- **Python 3**
- **Streamlit** – for interactive UI
- **Pandas, scikit-learn** – for ML pipeline
- **OpenWeatherMap API** – live weather data
- **geocoder** – for IP-based location detection
- **dotenv** – for API key management

---

## 📁 Project Structure

```bash
├── weather_outfits_en.csv         # Training dataset for outfit recommendations
├── main.py                        # Main Streamlit app
├── .env                           # Your API key (not pushed to GitHub)
├── requirements.txt               # List of dependencies
└── README.md                      # This file
