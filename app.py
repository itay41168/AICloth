import os
import pandas as pd
import streamlit as st
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")

# --- CSS לעיצוב עברית ו-RTL ורקע מרשים ---
st.markdown("""
<style>
html, body, [class*="css"]  {
    direction: rtl;
    text-align: right;
    font-family: 'Alef', sans-serif;
    background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
    color: #333;
    min-height: 100vh;
    padding: 20px;
}
.stButton>button {
    background-color: #4a90e2;
    color: white;
    font-weight: bold;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Alef&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- פונקציה לשליפת נתוני מזג אוויר ---
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&lang=he&appid={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    weather_api_to_label = {
        "Clear": "sunny",
        "Clouds": "cloudy",
        "Rain": "rainy",
        "Snow": "snowy",
        "Wind": "windy",
        "Drizzle": "rainy",
        "Thunderstorm": "rainy",
        "Mist": "cloudy",
        "Fog": "cloudy"
    }
    weather_main = data['weather'][0]['main']
    weather_label = weather_api_to_label.get(weather_main, "sunny")  # ברירת מחדל sunny
    
    return {
        'temp': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'weather': weather_label
    }

# --- מילון תרגום outfit מאנגלית לעברית ---
translation_dict = {
    'long shirt': 'חולצה ארוכה',
    'tank top': 'גופייה',
    'short shirt': 'חולצה קצרה',
    'sweater': 'סוודר',
    'thermal shirt': 'חולצה תרמית',
    'jeans': 'ג\'ינס',
    'long pants': 'מכנס ארוך',
    'short pants': 'מכנס קצר',
    'shorts': 'מכנסיים קצרים',
    'thermal pants': 'מכנס תרמי',
    'light jacket': 'מעיל קל',
    'raincoat': 'מעיל גשם',
    'boots': 'מגפיים',
    'regular shoes': 'נעליים רגילות',
    'waterproof shoes': 'נעליים עמידות למים',
    'sandals': 'סנדלים'
}

def translate_outfit_en_to_he(outfit_en):
    parts = [part.strip() for part in outfit_en.split(',')]
    translated_parts = [translation_dict.get(p, p) for p in parts]
    return ', '.join(translated_parts)

# --- טען את הנתונים ---
df = pd.read_csv('weather_outfits_en.csv')  # וודא שהקובץ נמצא בספרייה

# --- קידוד קטגוריות ---
label_encoders = {}
for col in ['weather', 'season', 'outfit']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

X = df[['temp', 'humidity', 'wind_speed', 'weather', 'season']]
y = df['outfit']

# --- אימון המודל ---
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
model.fit(X, y)

# --- כותרת ---
st.title("מה ללבוש היום?")

# --- פונקציה לקבלת עונה לפי תאריך היום ---
import datetime
def get_season_by_date():
    month = datetime.datetime.now().month
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3,4,5]:
        return 'spring'
    elif month in [6,7,8]:
        return 'summer'
    else:
        return 'autumn'

season_today = get_season_by_date()

# --- בחירת מצב הזנת נתונים ---
mode = st.radio("כיצד תרצה להזין את הנתונים?", ("שליפה אוטומטית לפי עיר", "הזנה ידנית"))

if mode == "שליפה אוטומטית לפי עיר":
    city = st.text_input("הכנס שם עיר:")
    if st.button("בדוק מזג אוויר"):
        if not api_key:
            st.error("מפתח ה-API לא נמצא. ודא שקובץ .env קיים עם מפתח תקין.")
        else:
            weather_data = get_weather(city, api_key)
            if weather_data:
                st.success(f"מזג האוויר ב-{city}:")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**מזג אוויר:**")
                    st.markdown(f"<div style='font-size:20px; color:blue;'>{weather_data['weather']}</div>", unsafe_allow_html=True)
                    st.markdown("**טמפרטורה:**")
                    st.markdown(f"<div style='font-size:20px;'>{weather_data['temp']}°C</div>", unsafe_allow_html=True)
                    st.markdown("**עונה:**")
                    st.markdown(f"<div style='font-size:20px;'>{season_today}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("**לחות:**")
                    st.markdown(f"<div style='font-size:20px;'>{weather_data['humidity']}%</div>", unsafe_allow_html=True)
                    st.markdown("**מהירות רוח:**")
                    st.markdown(f"<div style='font-size:20px;'>{weather_data['wind_speed']} קמ\"ש</div>", unsafe_allow_html=True)

                weather_enc = label_encoders['weather'].transform([weather_data['weather']])[0]
                season_enc = label_encoders['season'].transform([season_today])[0]
                input_df = pd.DataFrame([[weather_data['temp'], weather_data['humidity'], weather_data['wind_speed'], weather_enc, season_enc]],
                                        columns=['temp', 'humidity', 'wind_speed', 'weather', 'season'])
                pred = model.predict(input_df)[0]
                outfit_en = label_encoders['outfit'].inverse_transform([pred])[0]
                st.success(f"ההמלצה שלך: {translate_outfit_en_to_he(outfit_en)}")
            else:
                st.error("לא הצלחנו להביא את מזג האוויר. בדוק את שם העיר או את המפתח.")
else:
    temp = st.number_input("טמפרטורה (°C)", -10, 45, 20)
    humidity = st.number_input("לחות (%)", 0, 100, 50)
    wind_speed = st.number_input("מהירות רוח (קמ\"ש)", 0, 100, 10)
    weather = st.radio("מזג אוויר", label_encoders['weather'].classes_)
    season = st.radio("עונה", label_encoders['season'].classes_)

    if st.button("קבל המלצה"):
        weather_enc = label_encoders['weather'].transform([weather])[0]
        season_enc = label_encoders['season'].transform([season])[0]
        input_data = pd.DataFrame([[temp, humidity, wind_speed, weather_enc, season_enc]],
                                  columns=['temp', 'humidity', 'wind_speed', 'weather', 'season'])
        pred = model.predict(input_data)[0]
        outfit_en = label_encoders['outfit'].inverse_transform([pred])[0]
        st.success(f"ההמלצה שלך: {translate_outfit_en_to_he(outfit_en)}")
