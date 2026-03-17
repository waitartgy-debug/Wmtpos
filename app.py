import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# စာမျက်နှာ အပြင်အဆင် (Loyverse Style)
st.set_page_config(page_title="WMT Mobile POS", layout="wide", initial_sidebar_state="expanded")

# --- UI ကို ပိုလှအောင် ပြင်ဆင်ခြင်း ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; }
    .main { background-color: #f8f9fa; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Database တည်ဆောက်ခြင်း ---
def init_db():
    conn = sqlite3.connect('wmt_mobile_v2.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, brand TEXT, model TEXT, imei TEXT UNIQUE, buy_price REAL, sell_price REAL, status TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, type TEXT, customer TEXT, detail TEXT, 
                  total_amount REAL, cost_price REAL, profit REAL, date TEXT, staff TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- Login စနစ် ---
if 'auth' not in st.session_state:
    st.session_state.auth, st.session_state.role = False, None

if not st.session_state.auth:
    st.title("🔐 ဆိုင်သုံးစနစ်သို့ ဝင်ရောက်ရန်")
    user = st.text_input("အသုံးပြုသူအမည် (Username)")
    pw = st.text_input("လျှို့ဝှက်နံပါတ် (Password)", type="password")
    if st.button("အကောင့်ဝင်မည်"):
        if user == "admin" and pw == "admin123":
            st.session_state.auth, st.session_state.role = True, "Owner"
            st.rerun()
        elif user == "staff" and pw == "staff123":
            st.session_state.auth, st.session_state.role = True, "Staff"
            st.rerun()
    st.stop()

# --- Sidebar Menu ---
st.sidebar.title("WMT Mobile")
st.sidebar.subheader(f"အဆင့်: {st.session_state.role}")

menu = ["🏠 ပင်မစာမျက်နှာ", "🧾 အရောင်းနှင့် ပြုပြင်ရေး", "📦 ပစ္စည်းစာရင်း (Stock)"]
if st.session_state.role == "Owner":
    menu.append("📊 စာရင်းချုပ်ကြည့်ရန်")

choice = st.sidebar.radio("သွားရောက်လိုသည့်နေရာ", menu)

if st.sidebar.button("စနစ်မှ ထွက်မည် (Logout)"):
    st.session_state.auth = False
    st.rerun()

conn = sqlite3.connect('wmt_mobile_v2.db')

# --- 1. Dashboard (ပင်မစာမျက်နှာ) ---
if choice == "🏠 ပင်မစာမျက်နှာ":
    st.title("ယနေ့ လုပ်ငန်းဆောင်ရွက်မှု")
    df = pd.read_sql("SELECT * FROM transactions WHERE date=?", (datetime.now().strftime("%Y-%m-%d"),), conn)
    
    col1, col2, col3 = st.columns(3)
    if not df.empty:
        col1.metric("ယနေ့ရောင်းရငွေ", f"{df[df['type']=='အရောင်း']['total_amount'].sum():,.0f} MMK")
        col2.metric("ယနေ့ Service ရငွေ", f"{df[df['type']=='ပြုပြင်ရေး']['total_amount'].sum():,.0f} MMK")
        if st.session_state.role == "Owner":
            col3.metric("ယနေ့စုစုပေါင်းအမြတ်", f"{df['profit'].sum():,.0f} MMK")
    else:
        col1.metric("ယနေ့ရောင်းရငွေ", "0 MMK")
        col2.metric("ယနေ့ Service ရငွေ", "0 MMK")
        col3.metric("ယနေ့အမြတ်", "0 MMK")

# --- 2. Sales & Service (အရောင်းနှင့် ပြုပြင်ရေး) ---
elif choice == "🧾 အရောင်းနှင့် ပြုပြင်ရေး":
    st.title("အရောင်းနှင့် ပြုပြင်ရေး")
    tab1, tab2 = st.tabs(["🛒 ဖုန်းအသစ်ရောင်းရန်", "🔧 ဖုန်းပြုပြင်ရေး (Service)"])
    
    with tab1:
        imei_scan = st.text_input("IMEI / Barcode ကို Scan ဖတ်ပါ")
        if imei_scan:
            phone = pd.read_sql(f"SELECT * FROM inventory WHERE imei='{imei_scan}' AND status='အဆင်သင့်ရှိ'", conn)
            if not phone.empty:
                st.info(f"ဖုန်းအမျိုးအစား: {phone['brand'].iloc[0]} {phone['model'].iloc[0]}")
                cust = st.text_input("ဝယ်ယူသူအမည် (အရောင်း)")
                final_p = st.number_input("ရောင်းစျေး သတ်မှတ်ပါ", value=float(phone['sell_price'].iloc[0]))
                if st.button("အရောင်းသိမ်းဆည်းမည်"):
                    profit = final_p - phone['buy_price'].iloc[0]
                    c = conn.cursor()
                    c.execute("INSERT INTO transactions (type, customer, detail, total_amount, cost_price, profit, date, staff) VALUES (?,?,?,?,?,?,?,?)",
                              ("အရောင်း", cust, f"{phone['model'].iloc[0]} ({imei_scan})", final_p, phone['buy_price'].iloc[0], profit, datetime.now().strftime("%Y-%m-%d"), "Staff"))
                    c.execute("UPDATE inventory SET status='ရောင်းပြီး' WHERE imei=?", (imei_scan,))
                    conn.commit()
                    st.success("အရောင်းစာရင်း သိမ်းဆည်းပြီးပါပြီ။")
                    st.balloons()
            else: st.warning("ဤ IMEI ဖြင့် ပစ္စည်းမရှိပါ သို့မဟုတ် ရောင်းပြီးသားဖြစ်နေပါသည်။")

    with tab2:
        cust_s = st.text_input("ဝယ်ယူသူအမည် (Service)")
        s_type = st.selectbox("ပြုပြင်သည့်အမျိုးအစား", [
            "Touch + LCD လဲလှယ်ခြင်း", 
            "အသံချို့ယွင်းမှုပြုပြင်ခြင်း", 
            "ဖုန်း အင်တာနာ ပြုပြင်ခြင်း", 
            "အားသွင်းပေါက်ပြုပြင်ခြင်း", 
            "အခြား ပြုပြင်မှု"
        ])
        c_col1, c_col2 = st.columns(2)
        s_cost = c_col1.number_input("အပိုပစ္စည်း အရင်းနှီးစရိတ်", min_value=0.0)
        s_total = c_col2.number_input("စုစုပေါင်း ကျသင့်ငွေ", min_value=0.0)
        
        if st.button("ပြုပြင်ရေးမှတ်တမ်း သိမ်းမည်"):
            c = conn.cursor()
            c.execute("INSERT INTO transactions (type, customer, detail, total_amount, cost_price, profit, date, staff) VALUES (?,?,?,?,?,?,?,?)",
                      ("ပြုပြင်ရေး", cust_s, s_type, s_total, s_cost, s_total - s_cost, datetime.now().strftime("%Y-%m-%d"), "Staff"))
            conn.commit()
            st.success("ပြုပြင်ရေးမှတ်တမ်း သိမ်းဆည်းပြီးပါပြီ။")

# --- 3. Inventory (ပစ္စည်းစာရင်း) ---
elif choice == "📦 ပစ္စည်းစာရင်း (Stock)":
    st.title("ပစ္စည်းစာရင်း စီမံခန့်ခွဲမှု")
    if st.session_state.role == "Owner":
        with st.expander("➕ ဖုန်းအသစ် ထည့်သွင်းရန်"):
            col1, col2 = st.columns(2)
            brand = col1.text_input("တံဆိပ် (Brand)")
            model = col2.text_input("မော်ဒယ် (Model)")
            imei = col1.text_input("IMEI နံပါတ်")
            bp = col2.number_input("ဝယ်စျေး (အရင်း)", min_value=0.0)
            sp = col1.number_input("ရောင်းစျေး", min_value=0.0)
            if st.button("Stock ထဲသို့ ထည့်မည်"):
                c = conn.cursor()
                c.execute("INSERT INTO inventory (brand, model, imei, buy_price, sell_price, status) VALUES (?,?,?,?,?,'အဆင်သင့်ရှိ')", (brand, model, imei, bp, sp))
                conn.commit()
                st.success("Stock စာရင်းထဲသို့ ထည့်သွင်းပြီးပါပြီ။")
    
    # ပစ္စည်းစာရင်းပြဇယား
    query = "SELECT brand as တံဆိပ်, model as မော်ဒယ်, imei as IMEI, sell_price as ရောင်းစျေး, status as အခြေအနေ FROM inventory"
    df_inv = pd.read_sql(query, conn)
    st.dataframe(df_inv, use_container_width=True)

# --- 4. Reports (စာရင်းချုပ်) ---
elif choice == "📊 စာရင်းချုပ်ကြည့်ရန်":
    st.title("အမြတ်အစွန်းနှင့် စာရင်းချုပ်")
    df_res = pd.read_sql("SELECT * FROM transactions", conn)
    
    if not df_res.empty:
        # အရောင်းပြဇယား
        fig = px.bar(df_res, x='date', y='total_amount', color='type', title="ရက်အလိုက် ဝင်ငွေပြဇယား")
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### အသေးစိတ် အရောင်းမှတ်တမ်း")
        st.dataframe(df_res, use_container_width=True)
    else:
        st.info("စာရင်းမှတ်တမ်းများ မရှိသေးပါ။")

conn.close()
