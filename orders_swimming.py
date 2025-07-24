import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ---------- Настройки ----------
FILENAME = "orders.csv"
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

# ---------- Загрузка/создание CSV ----------
if not os.path.exists(FILENAME):
    df = pd.DataFrame(columns=["timestamp", "date", "meal_name", "quantity"])
    df.to_csv(FILENAME, index=False)

# ---------- Заголовок ----------
st.title(":shallow_pan_of_food: מערכת הזמנות למטבח")

# ---------- Выбор блюда ----------
selected_meal = st.selectbox("בחר מנה", MEALS)
quantity = st.number_input("כמות", min_value=1, value=1, step=1)

if st.button("להזמין"):
    now = datetime.now()
    new_order = pd.DataFrame({
        "timestamp": [now.strftime("%Y-%m-%d %H:%M:%S")],
        "date": [now.date().isoformat()],
        "meal_name": [selected_meal],
        "quantity": [quantity]
    })
    new_order.to_csv(FILENAME, mode='a', header=False, index=False)
    st.success("הוזמן בהצלחה!")

# ---------- Показать заказы за сегодня ----------
st.subheader(":calendar: הזמנות להיום")
df = pd.read_csv(FILENAME)
today = date.today().isoformat()
df_today = df[df['date'] == today]

# Кнопки удаления по индексу
to_delete = None
for i, row in df_today.iterrows():
    col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 4, 2])
    with col1: st.write(row['meal_name'])
    with col2: st.write(f"x{row['quantity']}")
    with col3: st.write(row['timestamp'][11:16])
    with col4: st.write("")
    with col5:
        if st.button("בטל", key=f"del_{i}"):
            to_delete = i

# Удаление записи
if to_delete is not None:
    df.drop(index=to_delete, inplace=True)
    df.to_csv(FILENAME, index=False)
    st.experimental_rerun()

# ---------- Сводка по сегодняшним заказам ----------
st.subheader(":bar_chart: סיכום להיום")
summary = df_today.groupby('meal_name')['quantity'].sum().reset_index()
summary.columns = ['מנה', 'סה"כ']
st.dataframe(summary, use_container_width=True)

# ---------- История по дате ----------
st.subheader(":date: היסטוריה לפי תאריך")
selected_date = st.date_input("בחר תאריך")
df_selected = df[df['date'] == selected_date.isoformat()]
if not df_selected.empty:
    st.write(f"סה\"כ הזמנות ליום {selected_date.isoformat()}:")
    hist_summary = df_selected.groupby('meal_name')['quantity'].sum().reset_index()
    hist_summary.columns = ['מנה', 'סה"כ']
    st.dataframe(hist_summary, use_container_width=True)
else:
    st.info("אין הזמנות בתאריך זה.")

