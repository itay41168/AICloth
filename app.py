import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- CSS לעיצוב ו-RTL עם התאמות לרדיואים ---
st.markdown(
    """
    <style>
    /* כיוון RTL ויישור טקסט */
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        unicode-bidi: bidi-override;
        background: #f0f4f8;
        font-family: 'Alef', Arial, sans-serif;
        color: #222222;
    }

    /* הגדלת שדות הקלט מספריים */
    input[type=number] {
        font-size: 1.3rem !important;
        padding: 8px !important;
        border-radius: 10px !important;
        border: 1.5px solid #0a9396 !important;
        width: 100% !important;
        box-sizing: border-box;
        text-align: right !important;
        background-color: white !important;
        color: #222222 !important;
    }

    /* עיצוב תוויות רדיו */
    div.row-widget.stRadio > div {
        font-size: 1.3rem !important;
        color: #222222 !important;
        text-align: right !important;
        direction: rtl !important;
        margin-bottom: 10px;
    }

    /* עיצוב אפשרויות רדיו */
    div.row-widget.stRadio > div label {
        font-size: 1.2rem !important;
        padding: 5px 12px;
        cursor: pointer;
    }

    /* כפתור */
    div.stButton > button {
        background-color: #0a9396;
        color: white;
        border-radius: 12px;
        padding: 12px 30px;
        font-size: 1.2rem;
        font-weight: 700;
        cursor: pointer;
        transition: background-color 0.3s ease;
        margin-top: 1.2rem;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #94d2bd;
        color: #004e4e;
    }

    /* הודעת הצלחה */
    .stSuccess {
        background-color: #94d2bd !important;
        color: #003333 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        margin-top: 1rem !important;
        text-align: right !important;
    }
    </style>

    <!-- גופן Alef מגוגל -->
    <link href="https://fonts.googleapis.com/css2?family=Alef&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

# --- טען את הנתונים ---
df = pd.read_csv('weather_outfits_en.csv')  # תעדכן את הנתיב במחשב שלך

# --- קידוד עמודות קטגוריאליות ---
label_encoders = {}
for col in ['weather', 'season', 'outfit']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

X = df[['temp', 'humidity', 'wind_speed', 'weather', 'season']]
y = df['outfit']

# --- בניית המודל ---
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
model.fit(X, y)

# --- מילון תרגום לעברית ---
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

# --- ממשק המשתמש ---
st.title("ממליץ לך מה ללבוש")

temp = st.number_input("טמפרטורה (°C)", min_value=-10, max_value=45, value=20, step=1)
humidity = st.number_input("לחות (%)", min_value=0, max_value=100, value=50, step=1)
wind_speed = st.number_input("מהירות רוח (קמ\"ש)", min_value=0, max_value=100, value=10, step=1)

weather = st.radio("מזג אוויר", list(label_encoders['weather'].classes_))
season = st.radio("עונה", list(label_encoders['season'].classes_))

if st.button("קבל המלצה"):
    weather_enc = label_encoders['weather'].transform([weather])[0]
    season_enc = label_encoders['season'].transform([season])[0]
    input_data = pd.DataFrame([[temp, humidity, wind_speed, weather_enc, season_enc]],
                              columns=['temp', 'humidity', 'wind_speed', 'weather', 'season'])
    pred = model.predict(input_data)[0]
    outfit_en = label_encoders['outfit'].inverse_transform([pred])[0]
    outfit_he = translate_outfit(outfit_en)
    st.success(f"ההמלצה שלך: {outfit_he}")
