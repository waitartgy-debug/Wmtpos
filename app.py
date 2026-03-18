import streamlit as st
import pandas as pd
from datetime import datetime

# သင်၏ Google Sheet ID
SHEET_ID = "160Ezos965ohyCWGrefj9wxPnCK-tu0O8BcB2nVQhW68"

# Google Sheet ၏ ပထမဆုံး Tab (Sales) ကို CSV အဖြစ် ဖတ်ရန် Link
# gid=0 သည် ပထမဆုံး sheet ကို ဆိုလိုသည်
SALES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

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

# ပင်မ Menu
st.sidebar.title("WMT Mobile")
menu = ["🏠 Dashboard", "📦 Inventory"]
choice = st.sidebar.radio("Menu", menu)

if choice == "🏠 Dashboard":
    st.header("ယနေ့ လုပ်ငန်းအခြေအနေ")
    
    try:
        # ဒေတာဖတ်ခြင်း
        df = pd.read_csv(SALES_URL)
        
        if not df.empty:
            # အရောင်းပမာဏကို ဂဏန်းအဖြစ်ပြောင်းလဲခြင်း
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
            
            c1, c2 = st.columns(2)
            c1.metric("စုစုပေါင်း ရောင်းရငွေ", f"{df['total_amount'].sum():,.0f} MMK")
            c2.metric("အရောင်းမှတ်တမ်းအရေအတွက်", f"{len(df)} ခု")
            
            st.subheader("လတ်တလော စာရင်းမှတ်တမ်း")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Sheet ထဲတွင် ဒေတာများ မတွေ့ရသေးပါ။")
            
    except Exception as e:
        st.error(f"ချိတ်ဆက်မှု အဆင်မပြေပါ - Sheet Link ကို ထပ်မံစစ်ဆေးပေးပါ")
        st.info("Google Sheet တွင် 'Anyone with the link' (Viewer/Editor) ပေးထားရန် လိုအပ်ပါသည်။")

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()
