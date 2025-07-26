import streamlit as st
import pandas as pd
from datetime import datetime, date
from google.oauth2.service_account import Credentials
import gspread

# ---------- Авторизация ----------
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1OX_vT9Qcb51niAQ8ACcB5xTs9LuqNWrQOwAxZpJNLyw/edit").sheet1
except Exception as e:
    st.error(f"שגיאה בחיבור ל-Google Sheets: {e}")
    st.stop()

# ---------- UI ----------
st.title("🍟 מערכת הזמנות למטבח")

MEALS = [
    "חזה עוף על הגריל",
    "צ'יפס גדול",
    "שניצל עם צ'יפס",
    "סלט טונה",
    "פלטת גבינות",
    "פלטת ירקות",
    "חמין עם עוף",
    "סלט טונה - שבת",
    "ארוחה קלה בחדר אוכל"
]

selected_meal = st.selectbox("בחר מנה", MEALS)
quantity = st.number_input("כמות", min_value=1, value=1, step=1)

if st.button("להזמין"):
    now = datetime.now()
    row = [now.strftime("%Y-%m-%d %H:%M:%S"), now.date().isoformat(), selected_meal, quantity]
    try:
        sheet.append_row(row)
        st.success("הוזמן בהצלחה!")
    except Exception as e:
        st.error(f"שגיאה בשליחה: {e}")

# ---------- Чтение данных ----------
try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.warning(f"שגיאה בקריאת הנתונים: {e}")
    df = pd.DataFrame(columns=["timestamp", "date", "meal_name", "quantity"])

# ---------- Заказы за сегодня ----------
st.subheader("📅 הזמנות להיום")
today = date.today().isoformat()
df_today = df[df["date"] == today]

if df_today.empty:
    st.info("אין הזמנות להיום")
else:
    for _, row in df_today.iterrows():
        st.write(f"{row['meal_name']} x{row['quantity']} — {row['timestamp'][11:16]}")
    st.markdown("---")
    summary = df_today.groupby("meal_name")["quantity"].sum().reset_index()
    summary.columns = ["מנה", "סה\"כ"]
    st.subheader("📊 סיכום להיום")
    st.dataframe(summary, use_container_width=True)

# ---------- История по дате ----------
st.subheader("📆 היסטוריה לפי תאריך")
selected_date = st.date_input("בחר תאריך")
df_sel = df[df["date"] == selected_date.isoformat()]

if df_sel.empty:
    st.info("אין הזמנות בתאריך זה.")
else:
    hist = df_sel.groupby("meal_name")["quantity"].sum().reset_index()
    hist.columns = ["מנה", "סה\"כ"]
    st.dataframe(hist, use_container_width=True)
