import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

# သင်၏ Google Sheet ID
SHEET_ID = "160Ezos965ohyCWGrefj9wxPnCK-tu0O8BcB2nVQhW68"
# ပိုမိုစိတ်ချရသော CSV Export Link
SALES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="WMT Mobile POS", layout="wide")

# UI အလှဆင်ခြင်း
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Login စနစ်
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 WMT POS Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pw == "admin123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.sidebar.title("WMT Mobile")
choice = st.sidebar.radio("Menu", ["🏠 Dashboard", "📦 Inventory"])

if choice == "🏠 Dashboard":
    st.header("ယနေ့ လုပ်ငန်းအခြေအနေ")
    
    try:
        # Link ကို အရင် စစ်ဆေးခြင်း
        response = requests.get(SALES_URL)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            
            if not df.empty:
                # Column နာမည်များတွင် Space ပါနေပါက ဖယ်ရှားခြင်း
                df.columns = df.columns.str.strip()
                
                if 'total_amount' in df.columns:
                    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
                    
                    c1, c2 = st.columns(2)
                    c1.metric("စုစုပေါင်း ရောင်းရငွေ", f"{df['total_amount'].sum():,.0f} MMK")
                    c2.metric("မှတ်တမ်းအရေအတွက်", f"{len(df)} ခု")
                    
                    st.subheader("လတ်တလော စာရင်း")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Sheet ထဲတွင် 'total_amount' ဟူသော column နာမည်ကို ရှာမတွေ့ပါ။ Row 1 ကို ပြန်စစ်ပေးပါ။")
            else:
                st.info("Sheet ထဲတွင် ဒေတာများ မတွေ့ရသေးပါ။")
        else:
            st.error("Google Sheet ထံမှ ဒေတာရယူ၍ မရပါ။ Link Permission ကို ပြန်စစ်ပေးပါ။")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()
