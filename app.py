import pandas as pd
import streamlit as st
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- CSS לעיצוב עברית ו-RTL ---
st.markdown("""
<style>
html, body, [class*="css"]  {
    direction: rtl;
    text-align: right;
    font-family: 'Alef', sans-serif;
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
    # מיפוי ערכי API לערכי הקטגוריות שלך
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

# --- מילון תרגום ---
translation_items = {
    'short shirt': 'חולצה קצרה',
    'long shirt': 'חולצה ארוכה',
    'short pants': 'מכנס קצר',
    'long pants': 'מכנס ארוך',
    'sandals': 'סנדלים',
    'regular shoes': 'נעליים רגילות',
    'waterproof shoes': 'נעליים עמידות למים',
    'boots': 'מגפיים',
    'thick coat': 'מעיל עבה',
    'raincoat': 'מעיל גשם',
    'light jacket': 'מעיל קל'
}

def translate_outfit(outfit_en):
    parts = [p.strip() for p in outfit_en.split(',')]
    return ', '.join([translation_items.get(p, p) for p in parts])

# --- כותרת ---
st.title("מה ללבוש היום?")

# --- בחירת מצב הזנת נתונים ---
mode = st.radio("כיצד תרצה להזין את הנתונים?", ("שליפה אוטומטית לפי עיר", "הזנה ידנית"))

api_key = "451b85a381534122b31a96473ce02388"  # המפתח שסיפקת

if mode == "שליפה אוטומטית לפי עיר":
    city = st.text_input("הכנס שם עיר:")
    if st.button("בדוק מזג אוויר"):
        weather_data = get_weather(city, api_key)
        if weather_data:
            st.success(f"מזג האוויר ב-{city}:")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**מזג אוויר:**")
                st.markdown(f"<div style='font-size:20px; color:blue;'>{weather_data['weather']}</div>", unsafe_allow_html=True)
                st.markdown("**טמפרטורה:**")
                st.markdown(f"<div style='font-size:20px;'>{weather_data['temp']}°C</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("**לחות:**")
                st.markdown(f"<div style='font-size:20px;'>{weather_data['humidity']}%</div>", unsafe_allow_html=True)
                st.markdown("**מהירות רוח:**")
                st.markdown(f"<div style='font-size:20px;'>{weather_data['wind_speed']} קמ\"ש</div>", unsafe_allow_html=True)

            season = st.radio("בחר עונה", label_encoders['season'].classes_)
            weather_enc = label_encoders['weather'].transform([weather_data['weather']])[0]
            season_enc = label_encoders['season'].transform([season])[0]
            input_df = pd.DataFrame([[weather_data['temp'], weather_data['humidity'], weather_data['wind_speed'], weather_enc, season_enc]],
                                    columns=['temp', 'humidity', 'wind_speed', 'weather', 'season'])
            pred = model.predict(input_df)[0]
            outfit = label_encoders['outfit'].inverse_transform([pred])[0]
            st.success(f"ההמלצה שלך: {translate_outfit(outfit)}")
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
        st.success(f"ההמלצה שלך: {translate_outfit(outfit_en)}")
