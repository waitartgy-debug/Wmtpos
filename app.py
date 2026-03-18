import streamlit as st
import pandas as pd
from datetime import datetime

# Google Sheet ID နှင့် တိုက်ရိုက် Link
SHEET_ID = "160Ezos965ohyCWGrefj9wxPnCK-tu0O8BcB2nVQhW68"
# Export format ကိုသုံးပြီး Publish လုပ်စရာမလိုဘဲ ဖတ်ခြင်း
SALES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.set_page_config(page_title="WMT Mobile POS", layout="wide")

# UI အလှဆင်ခြင်း
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-top: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

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

st.sidebar.title("WMT Mobile")
menu = ["🏠 ပင်မစာမျက်နှာ", "📊 အရောင်းမှတ်တမ်းကြည့်ရန်"]
choice = st.sidebar.radio("Menu", menu)

if choice == "🏠 ပင်မစာမျက်နှာ":
    st.header("ယနေ့ လုပ်ငန်းအခြေအနေ")
    try:
        # ဒေတာဖတ်ရန် ကြိုးစားခြင်း
        df = pd.read_csv(SALES_URL)
        if not df.empty:
            # total_amount ကို ဂဏန်းအဖြစ်ပြောင်းခြင်း
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
            today = datetime.now().strftime("%Y-%m-%d")
            
            # ဒေတာရှိလျှင် Metric များပြသခြင်း
            c1, c2 = st.columns(2)
            c1.metric("ယနေ့ရောင်းရငွေ", f"{df['total_amount'].sum():,.0f} MMK")
            c2.metric("စုစုပေါင်းမှတ်တမ်း", f"{len(df)} ခု")
            
            st.subheader("လတ်တလော စာရင်းများ")
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.info("Google Sheet ထဲတွင် ဒေတာအသစ်များကို စောင့်ဆိုင်းနေပါသည်။")

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()
