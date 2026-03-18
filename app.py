import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# --- Page Configuration ---
st.set_page_config(page_title="WMT Mobile POS Pro", layout="wide", page_icon="📱")

# --- Database Setup ---
DATA_FILE = "wmt_pos_pro_v3.csv"
if not os.path.exists(DATA_FILE):
    cols = ['id', 'category', 'item_name', 'qty', 'cost', 'sell', 'total', 'profit', 'date', 'time', 'staff', 'payment']
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(new_rows):
    df = load_data()
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- WMT Style & Branding ---
LOGO_URL = "https://drive.google.com/thumbnail?id=1S-ga29FKEi5ekqDAeJ2F1dDENWUTxUvP&sz=w500"

st.markdown(f"""
    <style>
    .main {{ background-color: #f0f4f7; }}
    .stMetric {{ background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #007bff; }}
    .stButton>button {{ width: 100%; border-radius: 8px; font-weight: bold; height: 3em; background-image: linear-gradient(to right, #1e3c72, #2a5298); color: white; border: none; }}
    .sidebar-content {{ background-color: #1e3c72; }}
    </style>
    """, unsafe_allow_html=True)

# --- Session State ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'role': None, 'user': None, 'cart': [], 'last_receipt': None})

# --- Login System ---
if not st.session_state.auth:
    st.image(LOGO_URL, width=150)
    st.title("📱 WMT Mobile - ဆိုင်ဝင်ရန်")
    role = st.selectbox("အသုံးပြုသူအဆင့်", ["Admin (ဆိုင်ရှင်)", "Staff (ဝန်ထမ်း)"])
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("ဝင်မည်"):
        if role == "Admin (ဆိုင်ရှင်)" and u == "admin" and p == "wmtadmin123":
            st.session_state.update({'auth': True, 'role': 'admin', 'user': 'Wai Min Tar'})
            st.rerun()
        elif role == "Staff (ဝန်ထမ်း)" and u == "staff1" and p == "wmtstaff456":
            st.session_state.update({'auth': True, 'role': 'staff', 'user': 'Staff-01'})
            st.rerun()
        else: st.error("❌ မှားယွင်းနေပါသည်။")
    st.stop()

# --- Navigation ---
st.sidebar.image(LOGO_URL, width=100)
st.sidebar.markdown(f"**User:** {st.session_state.user} ({st.session_state.role})")
menu = ["📊 Dashboard", "🛒 အရောင်းဖွင့်ရန်", "📋 မှတ်တမ်း"]
if st.session_state.role != 'admin': menu.remove("📋 မှတ်တမ်း")
choice = st.sidebar.radio("သွားရောက်လိုသည့်နေရာ", menu)

# --- 1. Dashboard ---
if choice == "📊 Dashboard":
    st.header("📊 ယနေ့ လုပ်ငန်းအကျဉ်း")
    df = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    tdf = df[df['date'] == today]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 ယနေ့ရောင်းရငွေ", f"{tdf['total'].sum():,.0f} MMK")
    if st.session_state.role == 'admin':
        c2.metric("📈 ယနေ့အမြတ်", f"{tdf['profit'].sum():,.0f} MMK", delta=f"{tdf['profit'].sum():,.0f}")
    c3.metric("📦 ရောင်းချမှုပေါင်း", f"{len(tdf)} ခု")
    
    st.subheader("🕒 နောက်ဆုံးရောင်းချမှု ၁၀ ခု")
    st.dataframe(df.tail(10), use_container_width=True)

# --- 2. Sales System ---
elif choice == "🛒 အရောင်းဖွင့်ရန်":
    st.header("🛒 အရောင်းဘောင်ချာအသစ်")
    
    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        barcode = c1.text_input("🔍 ပစ္စည်းအမည် / Barcode Scan", placeholder="ပစ္စည်းအမည် ရိုက်ပါ")
        qty = c2.number_input("အရေအတွက်", min_value=1, value=1)
        cat = c3.selectbox("အမျိုးအစား", ["Handset", "Accessory", "Service", "Software", "Other"])
        
        c4, c5, c6 = st.columns(3)
        sell = c4.number_input("ရောင်းစျေး (ကျပ်)", min_value=0)
        cost = c5.number_input("အရင်းစျေး (ကျပ်)", min_value=0) if st.session_state.role == 'admin' else 0
        pay = c6.selectbox("ငွေပေးချေမှု", ["Cash", "KPay", "Wave", "AYA"])
        
        if st.button("➕ ခြင်းတောင်းထဲထည့်မည်"):
            if barcode and sell > 0:
                st.session_state.cart.append({'name': barcode, 'qty': qty, 'cat': cat, 'sell': sell, 'cost': cost, 'pay': pay})
                st.rerun()

    if st.session_state.cart:
        st.write("---")
        st.subheader("🛒 ခြင်းတောင်းထဲရှိစာရင်း")
        temp_df = pd.DataFrame(st.session_state.cart)
        st.table(temp_df[['name', 'qty', 'sell', 'pay']])
        
        g_total = (temp_df['sell'] * temp_df['qty']).sum()
        st.markdown(f"### 💵 စုစုပေါင်း: **{g_total:,.0f} MMK**")
        
        if st.button("✅ အရောင်းအတည်ပြုပြီး Voucher ထုတ်မည်"):
            tid = f"WMT{datetime.now().strftime('%y%m%d%H%M%S')}"
            dt, tm = datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%I:%M %p")
            
            final_data = []
            for r in st.session_state.cart:
                final_data.append({
                    'id': tid, 'category': r['cat'], 'item_name': r['name'], 'qty': r['qty'],
                    'cost': r['cost'], 'sell': r['sell'], 'total': r['sell'] * r['qty'],
                    'profit': (r['sell'] - r['cost']) * r['qty'], 'date': dt, 'time': tm,
                    'staff': st.session_state.user, 'payment': r['pay']
                })
            save_data(final_data)
            
            # --- Voucher Layout ---
            v = f"        WMT MOBILE\n"
            v += f"     Phone & Service\n"
            v += f"   ------------------\n"
            v += f"  ID: {tid}\n  Date: {dt} {tm}\n"
            v += f"  Staff: {st.session_state.user}\n"
            v += f"   ------------------\n"
            for r in st.session_state.cart:
                v += f" {r['name'][:15]:<15} {r['qty']:>2} x {r['sell']:>8,.0f}\n"
            v += f"   ------------------\n"
            v += f"  TOTAL: {g_total:>12,.0f} MMK\n"
            v += f"   ------------------\n"
            v += f"   ကျေးဇူးတင်ပါသည် (WMT)\n"
            
            st.session_state.last_receipt = v
            st.session_state.cart = []
            st.rerun()

    if st.session_state.last_receipt:
        st.markdown("### 🧾 ဘောင်ချာ (Voucher)")
        st.text_area("", st.session_state.last_receipt, height=300)
        st.download_button("📥 Voucher သိမ်းမည်", st.session_state.last_receipt, file_name=f"WMT_Voucher.txt")
        if st.button("🔄 ဘောင်ချာအသစ်ဖွင့်ရန်"):
            st.session_state.last_receipt = None
            st.rerun()

# --- 3. Logs (Admin) ---
elif choice == "📋 မှတ်တမ်း":
    st.header("📋 အရောင်းမှတ်တမ်းအပြည့်အစုံ")
    df = load_data()
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Excel ထုတ်ရန်", df.to_csv(index=False).encode('utf-8-sig'), "WMT_Sales.csv", "text/csv")

if st.sidebar.button("🚪 Logout"):
    st.session_state.update({'auth': False, 'role': None, 'user': None, 'cart': [], 'last_receipt': None})
    st.rerun()
