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
    import traceback
    st.error("שגיאה בחיבור ל-Google Sheets")
    st.text(traceback.format_exc())
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
    if data:
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(columns=["timestamp", "date", "meal_name", "quantity"])
except Exception as e:
    st.warning(f"שגיאה בקריאת הנתונים: {e}")
    df = pd.DataFrame(columns=["timestamp", "date", "meal_name", "quantity"])

# ---------- Заказы за сегодня ----------
st.subheader("📅 הזמנות להיום")
today = date.today().isoformat()
if "date" in df.columns:
    df_today = df[df["date"] == today]
else:
    df_today = pd.DataFrame(columns=["timestamp", "date", "meal_name", "quantity"])
    st.warning("לא נמצאו עמודות בטבלה. בדוק את הגיליון Google Sheets.")

if df_today.empty:
    st.info("אין הזמנות להיום")
else:
    st.write("### מחיקת הזמנה מהיום")
for idx, row in df_today.iterrows():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"{row['meal_name']} x{row['quantity']} — {row['timestamp'][11:16]}")
    with col2:
        if st.button("❌ מחק", key=f"del_{idx}"):
            # Найдём строку по timestamp
            all_data = sheet.get_all_values()
            for i, r in enumerate(all_data):
                if r[0] == row["timestamp"]:  # timestamp
                    sheet.delete_rows(i + 1)  # строки в gspread с 1, не с 0
                    st.success("הוזמנה נמחקה")
                    st.success("הוזמנה נמחקה! אנא רענן את הדף.")
                    st.stop()


    st.markdown("---")
    summary = df_today.groupby("meal_name")["quantity"].sum().reset_index()
    summary.columns = ["מנה", "סה\"כ"]
    st.subheader("📊 סיכום להיום")
    st.dataframe(summary, use_container_width=True)

# ---------- История по дате ----------
st.subheader("📆 היסטוריה לפי תאריך")
selected_date = st.date_input("בחר תאריך")

if "date" in df.columns:
    df_sel = df[df["date"] == selected_date.isoformat()]
    if df_sel.empty:
        st.info("אין הזמנות בתאריך זה.")
    else:
        hist = df_sel.groupby("meal_name")["quantity"].sum().reset_index()
        hist.columns = ["מנה", "סה\"כ"]
        st.dataframe(hist, use_container_width=True)
else:
    st.warning("הטבלה אינה מכילה עמודת 'date'. נא לבדוק את הגיליון.")
