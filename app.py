import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="WMT Mobile POS", layout="wide")

# ဒေတာသိမ်းမည့်ဖိုင်အမည်
DB_FILE = "sales_data.csv"

# ဖိုင်မရှိလျှင် အသစ်ဆောက်ရန်
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=['type', 'customer', 'detail', 'total_amount', 'date'])
    df.to_csv(DB_FILE, index=False)

def load_data():
    return pd.read_csv(DB_FILE)

def save_data(new_row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# Login စနစ်
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 WMT POS - ဆိုင်ဝင်ရန်")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pw == "admin123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ပင်မ Menu
st.sidebar.title("WMT Mobile")
menu = ["🏠 Dashboard", "📝 စာရင်းသွင်းရန်", "📊 မှတ်တမ်းထုတ်ရန်"]
choice = st.sidebar.radio("Menu", menu)

if choice == "🏠 Dashboard":
    st.header("ယနေ့ လုပ်ငန်းအခြေအနေ")
    df = load_data()
    if not df.empty:
        df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
        c1, c2 = st.columns(2)
        c1.metric("စုစုပေါင်း ရောင်းရငွေ", f"{df['total_amount'].sum():,.0f} MMK")
        c2.metric("အရောင်းအရေအတွက်", f"{len(df)} ခု")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("စာရင်းများ မသွင်းရသေးပါ။")

elif choice == "📝 စာရင်းသွင်းရန်":
    st.header("အရောင်းစာရင်းသွင်းရန်")
    with st.form("entry_form"):
        type = st.selectbox("အမျိုးအစား", ["Handset", "Accessory", "Service", "Other"])
        customer = st.text_input("ဝယ်သူအမည်")
        detail = st.text_area("အကြောင်းအရာ (ဥပမာ- Redmi Note 13)")
        amount = st.number_input("ရောင်းစျေး (MMK)", min_value=0)
        date = st.date_input("ရက်စွဲ", datetime.now())
        
        if st.form_submit_button("စာရင်းသိမ်းမည်"):
            new_data = {
                'type': type,
                'customer': customer,
                'detail': detail,
                'total_amount': amount,
                'date': date.strftime("%Y-%m-%d")
            }
            save_data(new_data)
            st.success("စာရင်းသိမ်းဆည်းပြီးပါပြီ!")
            st.rerun()

elif choice == "📊 မှတ်တမ်းထုတ်ရန်":
    st.header("Excel ဖိုင်အဖြစ် ထုတ်ယူရန်")
    df = load_data()
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download Sales Excel (CSV)",
        data=csv,
        file_name=f'wmt_sales_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )
