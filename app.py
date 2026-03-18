import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Google Sheet CSV Export Links
SHEET_ID = "160Ezos965ohyCWGrefj9wxPnCK-tu0O8BcB2nVQhW68"
SALES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sales"
INV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Inventory"

st.set_page_config(page_title="WMT Mobile POS Pro", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #28a745; color: white; height: 3em; }
    .main { background-color: #f4f7f6; }
    </style>
    """, unsafe_allow_html=True)

# --- Login Logic ---
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

# --- Navigation ---
st.sidebar.title("WMT Mobile POS")
menu = ["🏠 Dashboard", "🛒 အရောင်းနှင့် ဝန်ဆောင်မှု", "📦 ပစ္စည်းစာရင်း"]
choice = st.sidebar.radio("Menu", menu)

# --- 1. Dashboard ---
if choice == "🏠 Dashboard":
    st.title("ယနေ့ လုပ်ငန်းအခြေအနေ")
    try:
        df_sales = pd.read_csv(SALES_URL)
        if not df_sales.empty:
            today = datetime.now().strftime("%Y-%m-%d")
            today_df = df_sales[df_sales['date'] == today]
            c1, c2, c3 = st.columns(3)
            c1.metric("ယနေ့ရောင်းရငွေ", f"{today_df['total_amount'].sum():,.0f} MMK")
            c2.metric("ယနေ့အမြတ်", f"{today_df['profit'].sum():,.0f} MMK")
            st.write("### လတ်တလော အရောင်းမှတ်တမ်း")
            st.dataframe(df_sales.tail(10))
    except:
        st.info("Google Sheet ထဲမှာ data မရှိသေးပါ သို့မဟုတ် Column နာမည်များ မှားနေပါသည်။")

# --- 2. Sales & Service ---
elif choice == "🛒 အရောင်းနှင့် ဝန်ဆောင်မှု":
    st.title("အရောင်းနှင့် ဝန်ဆောင်မှု")
    # ဤနေရာတွင် Google Sheets သို့ Data ပို့ရန် gspread သို့မဟုတ် Forms လိုအပ်ပါသည်
    st.warning("Google Sheet သို့ တိုက်ရိုက်စာရေးရန်အတွက် Google Service Account ထည့်သွင်းရန် လိုအပ်ပါသည်။")
    st.info("လတ်တလောတွင် စာရင်းများကို သင်၏ Google Sheet ထဲတွင် ကိုယ်တိုင် အလွယ်တကူ ဖြည့်သွင်းနိုင်ပြီး Dashboard တွင် အလိုအလျောက် ပေါ်လာမည်ဖြစ်သည်။")

# --- 3. Inventory ---
elif choice == "📦 ပစ္စည်းစာရင်း":
    st.title("လက်ကျန်ပစ္စည်းများ")
    try:
        df_inv = pd.read_csv(INV_URL)
        st.dataframe(df_inv)
    except:
        st.error("Inventory Sheet ကို မဖတ်နိုင်ပါ။")

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()
