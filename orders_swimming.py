import streamlit as st
import pandas as pd
from datetime import datetime, date
from google.oauth2.service_account import Credentials
import gspread

st.write("Содержимое secrets.toml:", st.secrets)

# ---------- Подключение к Google Sheets ----------
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
client = gspread.authorize(creds)

# Попытка открыть таблицу
try:
    sheet = client.open("kitchen-orders").sheet1
    data = sheet.get_all_records()
except Exception as e:
    st.error(f"שגיאה בחיבור ל-Google Sheets: {e}")
    st.stop()

# ---------- Интерфейс ----------
st.title("🍟 מערכת הזמנות למטבח")

# ---------- Меню ----------
MEALS = [
    "שניצל עם צ'יפס",
    "צ'יפס גדול",
    "חמין עם עוף",
    "סלט טונה",
    "פלטת גבינות",
    "פלטת ירקות",
    "חזה עוף על הגריל",
    "סלט טונה - שבת",
    "ארוחה קלה בחדר אוכל"
]

selected_meal = st.selectbox("בחר מנה", MEALS)
quantity = st.number_input("כמות", min_value=1, value=1, step=1)

if st.button("להזמין"):
    with st.spinner("שולח הזמנה..."):
        now = datetime.now()
        new_row = [now.strftime("%Y-%m-%d %H:%M:%S"), now.date().isoformat(), selected_meal, quantity]
        try:
            sheet.append_row(new_row)
            st.success("הוזמן בהצלחה!")
        except Exception as e:
            st.error(f"שגיאה בשליחה: {e}")

# ---------- Загрузка данных в DataFrame ----------
if data:
    df = pd.DataFrame(data)
    if not all(col in df.columns for col in ["timestamp", "date", "meal_name", "quantity"]):
        st.error("הטבלה חסרה עמודות נדרשות.")
        st.stop()
else:
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
    summary_today = df_today.groupby("meal_name")["quantity"].sum().reset_index()
    summary_today.columns = ["מנה", "סה\"כ"]
    st.subheader("📊 סיכום להיום")
    st.dataframe(summary_today, use_container_width=True)

# ---------- История по дате ----------
st.subheader("📅 היסטוריה לפי תאריך")
selected_date = st.date_input("בחר תאריך")
df_sel = df[df["date"] == selected_date.isoformat()]

if df_sel.empty:
    st.info("אין הזמנות בתאריך זה.")
else:
    summary_hist = df_sel.groupby("meal_name")["quantity"].sum().reset_index()
    summary_hist.columns = ["מנה", "סה\"כ"]
    st.dataframe(summary_hist, use_container_width=True)

