import streamlit as st
import pandas as pd
from datetime import datetime

# Google Sheet Link (WMT POS Data)
SHEET_ID = "160Ezos965ohyCWGrefj9wxPnCK-tu0O8BcB2nVQhW68"
# Sales sheet ကို ဖတ်ရန် link
SALES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sales"

st.set_page_config(page_title="WMT Mobile POS Pro", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-top: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Login Logic ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 WMT POS - ဆိုင်သုံးစနစ်")
    user = st.text_input("အသုံးပြုသူအမည်")
    pw = st.text_input("လျှို့ဝှက်နံပါတ်", type="password")
    if st.button("စနစ်ထဲသို့ဝင်မည်"):
        if user == "admin" and pw == "admin123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("အမည် သို့မဟုတ် လျှို့ဝှက်နံပါတ် မှားယွင်းနေပါသည်။")
    st.stop()

# --- Main App ---
st.sidebar.title("WMT Mobile")
menu = ["🏠 ပင်မစာမျက်နှာ", "🛒 အရောင်းဖွင့်ရန်", "📦 ပစ္စည်းစာရင်း"]
choice = st.sidebar.radio("သွားရောက်လိုသည့်နေရာ", menu)

if choice == "🏠 ပင်မစာမျက်နှာ":
    st.header("ယနေ့ လုပ်ငန်းဆောင်ရွက်မှု")
    
    try:
        # Google Sheet မှ ဒေတာကို ဖတ်ခြင်း
        df = pd.read_csv(SALES_URL)
        
        # ဒေတာရှိမရှိ စစ်ဆေးခြင်း
        if not df.empty and 'total_amount' in df.columns:
            today = datetime.now().strftime("%Y-%m-%d")
            # ယနေ့ရောင်းရငွေ တွက်ချက်ခြင်း
            today_sales = df[df['date'] == today]['total_amount'].sum() if 'date' in df.columns else 0
            
            c1, c2 = st.columns(2)
            c1.metric("ယနေ့ရောင်းရငွေ", f"{today_sales:,.0f} MMK")
            c2.metric("စုစုပေါင်း အရောင်းမှတ်တမ်း", f"{len(df)} ခု")
            
            st.subheader("လတ်တလော အရောင်းမှတ်တမ်း (Google Sheet မှ)")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("Google Sheet ထဲတွင် ဒေတာအသစ်များ မရှိသေးပါ။")
            
    except Exception as e:
        st.warning("Google Sheet နှင့် ချိတ်ဆက်ရန် ပြင်ဆင်နေဆဲဖြစ်သည်။ (Sheet ထဲတွင် Row 1 ကို အရင်ဖြည့်ပေးပါ)")
        st.info("Sheet နာမည်ကို 'Sales' ဟု ပေးထားရန် လိုအပ်ပါသည်။")

elif choice == "🛒 အရောင်းဖွင့်ရန်":
    st.subheader("အရောင်းဘောင်ချာအသစ်")
    st.info("အရောင်းမှတ်တမ်းများကို သင်၏ Google Sheet ထဲတွင် တိုက်ရိုက်ရိုက်ထည့်နိုင်ပါသည်။")
    st.write(f"👉 [Google Sheet သို့သွားရန်](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")

elif choice == "📦 ပစ္စည်းစာရင်း":
    st.subheader("လက်ကျန်ဖုန်းစာရင်း")
    st.write("ပစ္စည်းစာရင်းများကို 'Inventory' Sheet ထဲတွင် စီမံနိုင်ပါသည်။")

if st.sidebar.button("Log out"):
    st.session_state.auth = False
    st.rerun()
