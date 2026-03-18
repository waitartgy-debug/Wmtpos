import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page Config ---
st.set_page_config(page_title="WMT Mobile POS Pro", layout="wide", page_icon="📱")

# --- Database Setup (Internal CSV) ---
DATA_FILE = "wmt_pos_v4.csv"
if not os.path.exists(DATA_FILE):
    # Customer Name ကို Column အသစ်အနေနဲ့ ထည့်ထားပါတယ်
    cols = ['id', 'customer', 'item_name', 'barcode', 'qty', 'cost', 'sell', 'total', 'profit', 'date', 'time', 'staff', 'payment']
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(rows):
    df = load_data()
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- Styling ---
st.markdown("""
    <style>
    .stTextInput>div>div>input { background-color: #f0f2f6; border-radius: 10px; }
    .stButton>button { border-radius: 10px; background-image: linear-gradient(to right, #1e3c72, #2a5298); color: white; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- Login & Authentication ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'role': None, 'user': None, 'cart': []})

LOGO_URL = "https://drive.google.com/thumbnail?id=1S-ga29FKEi5ekqDAeJ2F1dDENWUTxUvP&sz=w500"

if not st.session_state.auth:
    st.image(LOGO_URL, width=120)
    st.title("WMT Mobile POS")
    with st.form("login_gate"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("ဝင်မည်"):
            if u == "admin" and p == "wmtadmin123":
                st.session_state.update({'auth': True, 'role': 'admin', 'user': 'Wai Min Tar'})
                st.rerun()
            elif u == "staff1" and p == "wmtstaff456":
                st.session_state.update({'auth': True, 'role': 'staff', 'user': 'Staff-01'})
                st.rerun()
            else: st.error("❌ မှားယွင်းနေပါသည်။")
    st.stop()

# --- Sidebar ---
st.sidebar.image(LOGO_URL, width=80)
st.sidebar.markdown(f"**အသုံးပြုသူ:** {st.session_state.user}")
menu = st.sidebar.radio("သွားရောက်လိုသည့်နေရာ", ["📊 Dashboard", "🛒 အရောင်းဖွင့်ရန်", "📋 မှတ်တမ်း"])

# --- 1. Dashboard ---
if menu == "📊 Dashboard":
    st.header("📊 ယနေ့ လုပ်ငန်းအခြေအနေ")
    df = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    tdf = df[df['date'] == today]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 ယနေ့ရောင်းရငွေ", f"{tdf['total'].sum():,.0f} MMK")
    if st.session_state.role == 'admin':
        c2.metric("📈 ယနေ့အမြတ်", f"{tdf['profit'].sum():,.0f} MMK")
    c3.metric("📦 ရောင်းချမှုပေါင်း", f"{len(tdf)} ခု")
    
    st.subheader("🕒 လတ်တလော အရောင်းမှတ်တမ်း")
    st.dataframe(df.tail(15), use_container_width=True)

# --- 2. POS System ---
elif menu == "🛒 အရောင်းဖွင့်ရန်":
    st.header("🛒 အရောင်းဘောင်ချာအသစ်")
    
    # Customer အချက်အလက်
    with st.expander("👤 ဝယ်သူအချက်အလက် (မထည့်လည်းရသည်)", expanded=True):
        cus_name = st.text_input("ဝယ်သူအမည်", placeholder="ဥပမာ - ကိုမောင်မောင်")
    
    # ပစ္စည်းအချက်အလက်
    with st.container():
        c1, c2 = st.columns([2, 2])
        item_name = c1.text_input("📦 ပစ္စည်းအမည်", placeholder="ဥပမာ - Redmi Note 13")
        barcode_no = c2.text_input("🔍 Barcode Scan", placeholder="Barcode ဖတ်ရန် ဤနေရာကိုနှိပ်ပါ")
        
        c3, c4, c5 = st.columns(3)
        qty = c3.number_input("အရေအတွက်", min_value=1, value=1)
        sell = c4.number_input("ရောင်းစျေး (ကျပ်)", min_value=0)
        cost = 0
        if st.session_state.role == 'admin':
            cost = c5.number_input("အရင်းစျေး (ကျပ်)", min_value=0)
            
        pay = st.selectbox("ငွေပေးချေမှု", ["Cash", "KPay", "Wave", "AYA Pay"])

        if st.button("➕ ခြင်းတောင်းထဲထည့်မည်"):
            if (item_name or barcode_no) and sell > 0:
                st.session_state.cart.append({
                    'customer': cus_name if cus_name else "Guest",
                    'item_name': item_name if item_name else "Unknown Item",
                    'barcode': barcode_no if barcode_no else "-",
                    'qty': qty, 'cost': cost, 'sell': sell, 'payment': pay
                })
                st.rerun()

    # Cart Table
    if st.session_state.cart:
        st.write("---")
        st.subheader("🛒 လက်ရှိရောင်းချမည့်စာရင်း")
        cart_df = pd.DataFrame(st.session_state.cart)
        st.table(cart_df[['customer', 'item_name', 'barcode', 'qty', 'sell', 'payment']])
        
        g_total = (cart_df['sell'] * cart_df['qty']).sum()
        st.markdown(f"### 💵 စုစုပေါင်းကျသင့်ငွေ: **{g_total:,.0f} MMK**")
        
        if st.button("✅ စာရင်းသိမ်းမည်"):
            tid = f"WMT{datetime.now().strftime('%y%m%d%H%M%S')}"
            dt, tm = datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%I:%M %p")
            
            final_rows = []
            for r in st.session_state.cart:
                final_rows.append({
                    'id': tid, 'customer': r['customer'], 'item_name': r['item_name'], 
                    'barcode': r['barcode'], 'qty': r['qty'], 'cost': r['cost'], 
                    'sell': r['sell'], 'total': r['sell'] * r['qty'],
                    'profit': (r['sell'] - r['cost']) * r['qty'],
                    'date': dt, 'time': tm, 'staff': st.session_state.user, 'payment': r['payment']
                })
            save_data(final_rows)
            st.session_state.cart = []
            st.success("✅ စာရင်းသိမ်းပြီးပါပြီ")
            st.rerun()

# --- 3. Full Logs ---
elif menu == "📋 မှတ်တမ်း":
    st.header("📋 စုစုပေါင်း အရောင်းမှတ်တမ်း")
    df = load_data()
    # ရှာဖွေနိုင်သည့်စနစ်
    search = st.text_input("🔍 ဝယ်သူအမည် သို့မဟုတ် Barcode ဖြင့်ရှာရန်")
    if search:
        df = df[df['customer'].str.contains(search, case=False) | df['barcode'].str.contains(search, case=False)]
    
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Excel ထုတ်ယူရန်", df.to_csv(index=False).encode('utf-8-sig'), "WMT_Sales_Export.csv", "text/csv")

if st.sidebar.button("🚪 Logout"):
    st.session_state.auth = False
    st.rerun()
