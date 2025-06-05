import os
import pandas as pd
import streamlit as st
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
import datetime

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")

# --- CSS לעיצוב עברית, RTL, רקע ורוד, טקסט מוגדל, והסרת רווחים מיותרים ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Alef&display=swap');

html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
    font-family: 'Alef', sans-serif;
    background: linear-gradient(135deg, #f78ca0 0%, #f9748f 50%, #fd868c 100%);
    color: #ffffff;
    min-height: 100vh;
    margin: 0;
    padding: 30px 40px;
    font-size: 20px;  /* טקסט מוגדל לכל העמוד */
}

h1 {
    font-weight: 900;
    font-size: 48px;
    margin-bottom: 20px;
    letter-spacing: 2px;
    color: #fff3f5;
    text-shadow: 1px 1px 5px rgba(0,0,0,0.2);
}

.stButton>button {
    background-color: #d6336c;
    color: white;
    font-weight: 700;
    font-size: 22px;
    border-radius: 10px;
    padding: 14px 28px;
    border: none;
    transition: background-color 0.3s ease;
    cursor: pointer;
    width: 100%;
    max-width: 320px;
    margin-bottom: 0;  /* הסרת מרווח תחתון כדי למנוע רווח לבן מתחת */
}
.stButton>button:hover {
    background-color: #e85c8a;
}

.stTextInput>div>input {
    font-size: 20px;
    padding: 14px 16px;
    border-radius: 10px;
    border: none;
    width: 100%;
    max-width: 380px;
    box-shadow: 0 0 8px rgba(0,0,0,0.15);
    margin-bottom: 15px;
}

.stRadio>div {
    font-size: 20px;
    margin-top: 10px;
    margin-bottom: 20px;
}

.weather-box {
    background-color: rgba(255, 255, 255, 0.2);
    padding: 25px 30px;
    border-radius: 18px;
    margin-bottom: 30px;
    box-shadow: 0 0 16px rgba(0,0,0,0.25);
    max-width: 650px;
}

.outfit-box {
    background-color: #d6336c;
    padding: 25px 30px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.4);
    font-size: 26px;
    font-weight: 900;
    max-width: 650px;
    margin-top: 40px;
    color: white;
    text-align: center;
    letter-spacing: 1.2px;
}

@media (max-width: 768px) {
    html, body, [class*="css"] {
        padding: 20px 15px;
        font-size: 18px;
    }
    h1 {
        font-size: 38px;
    }
    .stButton>button, .stTextInput>div>input {
        max-width: 100%;
    }
    .weather-box, .outfit-box {
        max-width: 100%;
    }
}
</style>
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

# --- פונקציה לקבלת עונה לפי תאריך היום ---
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

# --- כותרת ---
st.title("AICloth - מה ללבוש היום?")

# --- שליפת מיקום GPS באמצעות JS ---
def get_location():
    # קוד JS שפותח בקונסולה של הדפדפן ומחזיר קואורדינטות
    location_js = """
    <script>
    const sendLocationToStreamlit = () => {
        navigator.geolocation.getCurrentPosition(
            position => {
                const coords = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                };
                // שליחת הקואורדינטות ל-Streamlit
                window.parent.postMessage({ type: 'coords', data: coords }, '*');
            },
            error => {
                window.parent.postMessage({ type: 'coords', data: null }, '*');
            }
        );
    };
    sendLocationToStreamlit();
    </script>
    """
    st.components.v1.html(location_js, height=0, width=0)

# --- קבלת הודעות מ-JS ---

# בממשק הפשוט של Streamlit אין API ישיר לקבלת אירועים JS (חוץ מה-SessionState)
# לכן נעשה פתרון פשוט עם st.experimental_get_query_params
# אבל מכיוון שזה מתבטל, אפשר להשתמש ב-`st.experimental_get_query_params` או עם אוסף params ידני.

# כאן אציע פתרון חלופי עם input נסתר שנעדכן ע"י JS (צריך לבנות אינטגרציה מורכבת יותר ב-frontend).

# במקום זאת, נשתמש ב-Streamlit forms או נבקש מהמשתמש להזין ידנית, או נבחר את האופציות הידניות והעיר.

# לכן, נשמור על 3 אופציות קלט פשוטות:

mode = st.radio("כיצד תרצה להזין את הנתונים?", (
    "שליפה אוטומטית לפי GPS (מצריך הרשאה בדפדפן)",
    "שליפה אוטומטית לפי עיר",
    "הזנה ידנית"
))

weather_data = None
city = None

if mode == "שליפה אוטומטית לפי GPS (מצריך הרשאה בדפדפן)":
    st.markdown("לחץ על הכפתור כדי לאפשר קבלת מיקום ולהביא את מזג האוויר בהתאם:")
    if st.button("קבל מיקום ומזג אוויר"):
        # כאן, בגלל מגבלות Streamlit, לא נוכל לקבל מיקום ישירות בלי JS מורכב.
        # אבל יש פתרונות חיצוניים או הרצת קוד JS כמו בפתרון הבא:
        st.info("עדכון מיקום מתבצע כרגע. אם זה לא עובד, נסה להזין עיר ידנית.")
        # פתרון פשוט יותר: בקש מהמשתמש להזין מיקום ידנית, או השתמש בספריית צד ג׳.

        # אלטרנטיבה: השתמש ב-API להמרת כתובת IP למיקום (אם מותר לך)
        # כאן נשתמש ב-api חינמי להדגמה:
        try:
            ip_response = requests.get('https://ipinfo.io/json')
            ip_data = ip_response.json()
            loc = ip_data.get('loc', None)  # "lat,lon"
            if loc:
                lat, lon = loc.split(',')
                # המרת קואורדינטות לשם עיר:
                geo_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
                geo_resp = requests.get(geo_url)
                city_data = geo_resp.json()
                if city_data:
                    city = city_data[0]['name']
                    st.success(f"זוהתה העיר שלך: {city}")
                    weather_data = get_weather(city, api_key)
                else:
                    st.error("לא הצלחנו לקבל את שם העיר מהמיקום.")
            else:
                st.error("לא הצלחנו לקבל מיקום מה-IP.")
        except Exception as e:
            st.error(f"שגיאה בקבלת המיקום: {e}")

elif mode == "שליפה אוטומטית לפי עיר":
    city = st.text_input("הכנס שם עיר:")
    if st.button("בדוק מזג אוויר"):
        if not api_key:
            st.error("מפתח ה-API לא נמצא. ודא שקובץ .env קיים עם מפתח תקין.")
        else:
            weather_data = get_weather(city, api_key)
            if not weather_data:
                st.error("לא הצלחנו להביא את מזג האוויר. בדוק את שם העיר או את המפתח.")

else:  # הזנה ידנית
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
        st.markdown(f'<div class="outfit-box">ההמלצה שלך: {translate_outfit_en_to_he(outfit_en)}</div>', unsafe_allow_html=True)

# אם קיבלנו נתוני מזג אוויר אוטומטית, נציג ונחשב המלצה
if weather_data:
    st.markdown('<div class="weather-box">', unsafe_allow_html=True)
    st.markdown(f"**מזג אוויר ב-{city}:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**מצב מזג האוויר:** <span style='color:#ffde59;'>{weather_data['weather']}</span>", unsafe_allow_html=True)
        st.markdown(f"**טמפרטורה:** {weather_data['temp']}°C")
        st.markdown(f"**עונה:** <span style='color:#a1e44d;'>{season_today}</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"**לחות:** {weather_data['humidity']}%")
        st.markdown(f"**מהירות רוח:** {weather_data['wind_speed']} קמ\"ש")
    st.markdown('</div>', unsafe_allow_html=True)

    weather_enc = label_encoders['weather'].transform([weather_data['weather']])[0]
    season_enc = label_encoders['season'].transform([season_today])[0]
    input_df = pd.DataFrame([[weather_data['temp'], weather_data['humidity'], weather_data['wind_speed'], weather_enc, season_enc]],
                            columns=['temp', 'humidity', 'wind_speed', 'weather', 'season'])
    pred = model.predict(input_df)[0]
    outfit_en = label_encoders['outfit'].inverse_transform([pred])[0]

    st.markdown(f'<div class="outfit-box">ההמלצה שלך: {translate_outfit_en_to_he(outfit_en)}</div>', unsafe_allow_html=True)
